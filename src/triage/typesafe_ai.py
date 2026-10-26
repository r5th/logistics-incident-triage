"""Approach B: TypeSafe only (ADR-0001). One System One call per Incident Report.

Jev makes the judgments; code turns them into a Prediction. All question wording lives in this
module (`build_questions`) and is versioned by QUESTIONS_VERSION, which every Prediction records.
State is the report text only, so A, B and C see identical inputs.

Evidence is a Choice over the report's own sentences, so a quote can never be invented.
"""

from __future__ import annotations

import json
import os
import time
from pathlib import Path

import httpx2
from typesafe_sdk import Choice, Noul, RetryPolicy, TypeSafeClient, TypeSafeError

from triage.schema import (
    Category,
    Destination,
    Prediction,
    Report,
    split_sentences,
)

QUESTIONS_VERSION = "b-v1"
# Pinned versioned model ID, not the `jev-latest` alias: thresholds are tuned against it.
MODEL = "jev-1.14.0"

# Price per million input tokens; output tokens are free. Source: https://docs.typesafe.ai/models.md
PRICE_PER_MTOK_INPUT_USD = 0.042
SPEND_CAP_USD = 5.0  # hard cap from docs/build-plan.md
SPEND_FILE = Path("results/spend.json")
ENV_FILE = Path.home() / ".config" / "logistics-incident-triage" / ".env"

MAX_EVIDENCE_SENTENCES = 24
# Bounded retries inside the SDK (429, 408, 5xx, connection errors, timeouts).
RETRY = RetryPolicy(max_retries=2, timeout=10.0)

# Noul thresholds that raise Review Triggers. 0.5 = "more likely than not"; the Policy decides
# which triggers force Review, so these only name what the model saw.
LOCATION_STATED_MIN = 0.5  # below → location_missing
CARGO_IDENTIFIED_MIN = 0.5  # below → cargo_missing
CONFLICTING_STATEMENTS_MAX = 0.5  # above → conflicting_statements
MULTIPLE_ISSUES_MAX = 0.5  # above → multiple_issues
# Extra Evidence sentences beyond the top one are kept when at least this probable.
EVIDENCE_MIN_PROB = 0.3
# Urgency Evidence is shown only when Jev leans urgent.
URGENCY_EVIDENCE_MIN = 0.5


class SpendCapExceeded(RuntimeError):
    """Raised before a call that would take cumulative spend over the cap."""


# --- Questions ---------------------------------------------------------------------------------
# Wording is condensed from docs/label-guide.md; rule codes are kept in the text so a reviewer
# can trace each clause to the guide.

CATEGORY_CRITERIA = {
    "vehicle_breakdown": "C1: the vehicle, trailer or equipment on it has a fault or is "
    "immobilised: mechanical or electrical failure, puncture or blow-out, flat battery, warning "
    "light with loss of power, failed refrigeration unit, failed tail-lift, a defect found at a "
    "roadside check, or immobilised by fuel theft or vandalism. Includes the vehicle's own fuel "
    "leak with no collision, and a breakdown in a live lane with nobody hurt.",
    "delivery_delay": "C2: the goods are intact and accounted for but late or not delivered at "
    "the booked time, because of traffic, road closures, weather, late loading, a customer site "
    "closed or refusing the slot, driver hours, or an authority hold with paperwork in order.",
    "shipment_damage": "C3: goods are physically damaged, spoiled, wet, contaminated or "
    "temperature-abused, found at any point, including a damage note on a POD or CMR. Damaged "
    "dangerous goods that are leaking are a safety incident instead.",
    "missing_shipment": "C4: goods are not where they should be: short on delivery, never "
    "loaded, delivered to the wrong address, on the wrong vehicle, lost, stolen, or a loaded "
    "vehicle or trailer whose whereabouts are unknown. Late goods whose location is known are a "
    "delay.",
    "documentation_issue": "C5: paperwork or records are missing, wrong or disputed: CMR, "
    "delivery note, POD, customs or transit declaration, health certificate, dangerous goods "
    "note, tachograph record, driver card or permit, while the goods themselves are fine.",
    "safety_incident": "C6: a person was hurt, taken ill at work, or was or could have been at "
    "risk: injury, collision of any size, fire, leak or spill of dangerous goods cargo, an "
    "unsafe or shifting load, threats or violence against staff, a near miss, or a hazard "
    "report about a site or vehicle.",
}

PRIMARY_CATEGORY_RULES = [
    "P1: if any part of the report is a safety incident, the Category is safety_incident.",
    "P2: a delay caused by something in another Category takes that other Category.",
    "P3: goods damaged or missing win over the vehicle fault or paperwork that led to it.",
    ("P4: unrelated issues in one report: safety > missing > damage > breakdown > "
    "documentation > delay."),
]

URGENT_TRUE = [
    ("U1: someone is hurt (any injury, however minor) or a person is in danger now: on foot "
    "beside moving traffic, trapped, threatened, taken ill at work, or near a load that may fall."),
    ("U2: dangerous goods leaking, spilled or in damaged packaging; fuel, oil or chemical "
    "spilled onto a public road; a spill on site that is not contained."),
    "U3: the vehicle is stopped in a running lane of a public road with traffic passing.",
    ("U4: a chilled or frozen load still on our vehicle or at our depot whose refrigeration has "
    "stopped or will stop within hours, or whose temperature is already out of range; a frozen "
    "load back in working refrigeration within 1 hour is not at risk."),
    ("U5: a medical consignment, or one with a flagged deadline (penalty slot, production line "
    "waiting, ferry cut-off), that will or is likely to miss its window."),
    ("U6: theft in progress, a loaded vehicle whose location is unknown and whose driver cannot "
    "be contacted, or the load space breached: seal broken, missing or not matching, curtain "
    "slashed, doors forced."),
    ("A trigger stated as possible counts. If the report contradicts itself and either reading "
    "meets a trigger, the answer is yes."),
]

URGENT_FALSE = (
    "None of the triggers is stated or clearly implied. For example: a breakdown on the hard "
    "shoulder, in a lay-by or at services; a near miss that is over with nobody hurt; intact, "
    "correctly packed dangerous goods; a medical delivery that will still make its slot; goods "
    "short with the seal intact. Swearing, capitals or an alarmed tone do not count."
)

DESTINATION_CRITERIA = {
    "fleet_support": "Vehicle, trailer, refrigeration-unit or tail-lift faults and breakdowns "
    "not caused by crime. Also delays caused by driver availability: driving or duty-time limit "
    "reached, a required break or rest, or no driver for the shift.",
    "customer_desk": "Delivery delays from traffic, closures, weather, late loading or the "
    "customer's site. Also missing goods with an innocent explanation stated (wrong address, "
    "left behind at loading, put on the wrong vehicle) and no sign of theft. Also problems only "
    "with the consignee's delivery paperwork (POD, delivery note) with no regulatory document "
    "involved.",
    "claims": "Goods damaged, spoiled, wet or temperature-abused, with the load space not "
    "breached or tampered with.",
    "security_investigations": "Goods missing with no innocent explanation, or with any theft "
    "sign; stolen loads or vehicles. Also damaged goods where the load space was breached (seal "
    "broken or mismatched, curtain slashed, cartons opened). Also breakdowns caused deliberately: "
    "fuel siphoned, lines or cables cut, tyres slashed, vandalism.",
    "compliance": "Problems with regulatory paperwork: customs or transit declarations, CMR on "
    "an international job, health certificates, dangerous goods notes, tachograph records, "
    "driver cards or permits. Also delays where an authority (Border Force, customs, DVSA, "
    "police) holds the vehicle or load and the paperwork is not at fault.",
    "safety_desk": "Every safety incident: injury, illness at work, collision, fire, dangerous "
    "goods leak, unsafe load, threats to staff, near miss or hazard report, even when theft, "
    "hazmat or a breakdown is also involved.",
}


def _evidence_options(sentences: list[str]) -> dict[str, str]:
    return {f"s{i}": s for i, s in enumerate(sentences[:MAX_EVIDENCE_SENTENCES], start=1)}


def build_questions(sentences: list[str]) -> dict[str, Choice | Noul]:
    """The b-v1 question set for one report, whose sentences become the Evidence options."""
    questions: dict[str, Choice | Noul] = {
        "category": Choice(
            instructions={
                "question": "Which Category is the primary one for the incident in `report`?",
                "primary_category_rules": PRIMARY_CATEGORY_RULES,
            },
            criteria=CATEGORY_CRITERIA,
        ),
        "urgent": Noul(
            instructions="Does `report` state or clearly imply an urgency trigger?",
            criteria={"true": URGENT_TRUE, "false": URGENT_FALSE},
        ),
        "destination": Choice(
            instructions="Which team should handle the incident in `report`?",
            criteria=DESTINATION_CRITERIA,
        ),
        "location_stated": Noul(
            instructions="Does `report` say where the incident happened?",
            criteria={
                "true": "A road, junction, town, depot, customer site, port or services is "
                "named.",
                "false": "The report gives no place at all, only something like 'broken down, "
                "waiting for recovery'.",
            },
        ),
        "cargo_identified": Noul(
            instructions="Does `report` say what goods are on the vehicle or involved?",
            criteria={
                "true": "The goods are described, for example chilled yoghurt, 26 pallets of "
                "tinned soup, laptops, or an empty trailer.",
                "false": "The goods are not mentioned, or only as 'the load' or 'the delivery'.",
            },
        ),
        "conflicting_statements": Noul(
            instructions="Does `report` contradict itself about a fact that matters for "
            "handling the incident?",
            criteria={
                "true": "Two statements cannot both be true, for example 'nobody hurt' and later "
                "'he cut his hand', or 'parked safely off the road' and later 'traffic is "
                "squeezing past me'.",
                "false": "Every statement fits with the others, even if details are missing.",
            },
        ),
        "multiple_issues": Noul(
            instructions="Does `report` describe more than one distinct problem?",
            criteria={
                "true": "For example a breakdown and damaged goods, or a delay and a missing "
                "delivery note.",
                "false": "One problem, perhaps with its knock-on effect such as a late arrival.",
            },
        ),
    }
    options = _evidence_options(sentences)
    if len(options) >= 2:
        questions["evidence_category"] = Choice(
            instructions="Which sentence of `report` best shows what went wrong?",
            criteria=options,
        )
        questions["evidence_urgency"] = Choice(
            instructions="Which sentence of `report` gives the strongest reason it might need "
            "attention quickly?",
            criteria=options,
        )
    return questions


# --- Spend guard -------------------------------------------------------------------------------


class SpendGuard:
    """Accumulates tokens across runs in a JSON file and refuses calls past the cap."""

    def __init__(self, path: str | Path = SPEND_FILE, cap_usd: float = SPEND_CAP_USD):
        self.path = Path(path)
        self.cap_usd = cap_usd

    def _read(self) -> dict:
        if self.path.exists():
            return json.loads(self.path.read_text(encoding="utf-8"))
        return {"input_tokens": 0, "output_tokens": 0, "calls": 0}

    @staticmethod
    def usd(input_tokens: int) -> float:
        return input_tokens * PRICE_PER_MTOK_INPUT_USD / 1e6

    def check(self, projected_input_tokens: int) -> None:
        spent = self._read()["input_tokens"]
        projected = self.usd(spent + projected_input_tokens)
        if projected > self.cap_usd:
            raise SpendCapExceeded(
                f"projected TypeSafe spend US${projected:.2f} exceeds the US${self.cap_usd:g} "
                f"cap ({self.path})")

    def record(self, input_tokens: int, output_tokens: int) -> None:
        spend = self._read()
        spend["input_tokens"] += input_tokens
        spend["output_tokens"] += output_tokens
        spend["calls"] += 1
        spend["usd"] = self.usd(spend["input_tokens"])
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(spend, indent=2) + "\n", encoding="utf-8")


def _estimate_input_tokens(state: dict, questions: dict) -> int:
    """Over-estimate (about 3 characters per token) of what a call will be billed."""
    payload = json.dumps({"state": state,
                          "questions": {k: q.model_dump() for k, q in questions.items()}})
    return len(payload) // 3 + 1


# --- Client ------------------------------------------------------------------------------------


def load_api_key(env_file: str | Path = ENV_FILE) -> str | None:
    """TYPESAFE_API_KEY from the environment, else from the key file outside the repo."""
    from dotenv import dotenv_values

    key = os.environ.get("TYPESAFE_API_KEY")
    if key:
        return key
    if Path(env_file).exists():
        return dotenv_values(env_file).get("TYPESAFE_API_KEY")
    return None


class _CountingTransport(httpx2.HTTPTransport):
    """Counts HTTP requests so a Prediction can record attempts including SDK retries."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.requests = 0

    def handle_request(self, request):
        self.requests += 1
        return super().handle_request(request)


# --- Approach B --------------------------------------------------------------------------------


def _uniform(options) -> dict[str, float]:
    return {o.value: 1 / len(options) for o in options}


class TypeSafeTriager:
    def __init__(self, client=None, spend_guard: SpendGuard | None = None):
        self._transport: _CountingTransport | None = None
        if client is None:
            self._transport = _CountingTransport()
            client = TypeSafeClient(api_key=load_api_key(), model=MODEL, retry=RETRY,
                                    transport=self._transport)
        self.client = client
        self.spend_guard = spend_guard or SpendGuard()

    def predict(self, report: Report) -> Prediction:
        sentences = split_sentences(report.text)
        state = {"report": report.text}
        questions = build_questions(sentences)
        self.spend_guard.check(_estimate_input_tokens(state, questions))

        before = self._transport.requests if self._transport else 0
        start = time.perf_counter()
        response, error = None, None
        try:
            response = self.client.system_one(state=state, questions=questions, model=MODEL)
        except TypeSafeError as e:
            error = f"{type(e).__name__}: {e}"[:500]
        latency_ms = (time.perf_counter() - start) * 1000
        attempts = (self._transport.requests - before) if self._transport else 1

        input_tokens = output_tokens = 0
        model = None
        if response is not None:
            input_tokens, output_tokens = (response.usage.input_tokens,
                                           response.usage.output_tokens)
            model = response.model
            self.spend_guard.record(input_tokens, output_tokens)
            try:
                return self._from_answers(report, sentences, questions, response,
                                          latency_ms, attempts)
            except (KeyError, ValueError) as e:
                error = f"invalid output: {e}"

        return Prediction(
            report_id=report.report_id,
            approach="B",
            category=next(iter(Category)),
            category_probs=_uniform(Category),
            urgent_prob=0.5,
            destination=next(iter(Destination)),
            destination_probs=_uniform(Destination),
            evidence=[],
            triggers=["invalid_output"],
            latency_ms=latency_ms,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            attempts=attempts,
            error=error,
            model=model,
            version=QUESTIONS_VERSION,
        )

    @staticmethod
    def _from_answers(report, sentences, questions, response, latency_ms, attempts):
        choices, nouls = response.choices, response.nouls
        missing = [k for k in questions if k not in choices and k not in nouls]
        if missing:
            raise ValueError(f"missing {missing[0]!r}")

        def probs(key: str, options) -> dict[str, float]:
            got = choices[key].probabilities
            if set(got) != {o.value for o in options}:
                raise ValueError(f"unexpected options in {key!r}")
            return {o.value: float(got[o.value]) for o in options}

        category_probs = probs("category", Category)
        destination_probs = probs("destination", Destination)
        n = {k: float(nouls[k].noul) for k in questions if isinstance(questions[k], Noul)}
        if not all(0.0 <= v <= 1.0 for v in n.values()):
            raise ValueError("noul outside [0, 1]")
        urgent_prob = n["urgent"]

        evidence_ids: set[int] = set()
        if "evidence_category" in questions:
            keys = ["evidence_category"]
            if urgent_prob >= URGENCY_EVIDENCE_MIN:
                keys.append("evidence_urgency")
            for key in keys:
                answer = choices[key]
                evidence_ids.add(int(answer.choice[1:]) - 1)
                evidence_ids |= {int(k[1:]) - 1 for k, p in answer.probabilities.items()
                                 if p >= EVIDENCE_MIN_PROB}
        elif sentences:
            evidence_ids.add(0)  # a one-sentence report is its own Evidence

        triggers = []
        if n["location_stated"] < LOCATION_STATED_MIN:
            triggers.append("location_missing")
        if n["cargo_identified"] < CARGO_IDENTIFIED_MIN:
            triggers.append("cargo_missing")
        if n["conflicting_statements"] > CONFLICTING_STATEMENTS_MAX:
            triggers.append("conflicting_statements")
        if n["multiple_issues"] > MULTIPLE_ISSUES_MAX:
            triggers.append("multiple_issues")

        return Prediction(
            report_id=report.report_id,
            approach="B",
            category=Category(max(category_probs, key=category_probs.get)),
            category_probs=category_probs,
            urgent_prob=urgent_prob,
            destination=Destination(max(destination_probs, key=destination_probs.get)),
            destination_probs=destination_probs,
            evidence=[sentences[i] for i in sorted(evidence_ids) if i < len(sentences)],
            triggers=triggers,
            latency_ms=latency_ms,
            input_tokens=response.usage.input_tokens,
            output_tokens=response.usage.output_tokens,
            attempts=attempts,
            error=None,
            model=response.model,
            version=QUESTIONS_VERSION,
        )

