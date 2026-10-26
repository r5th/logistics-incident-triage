"""Data types shared by every approach: Incident Reports, Scenarios, Labels and Predictions.

Field names follow the Data contract in docs/build-plan.md; vocabulary follows GLOSSARY.md.
"""

from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass, field
from enum import StrEnum
from pathlib import Path


class Category(StrEnum):
    VEHICLE_BREAKDOWN = "vehicle_breakdown"
    DELIVERY_DELAY = "delivery_delay"
    SHIPMENT_DAMAGE = "shipment_damage"
    MISSING_SHIPMENT = "missing_shipment"
    DOCUMENTATION_ISSUE = "documentation_issue"
    SAFETY_INCIDENT = "safety_incident"


class Destination(StrEnum):
    FLEET_SUPPORT = "fleet_support"
    CUSTOMER_DESK = "customer_desk"
    CLAIMS = "claims"
    SECURITY_INVESTIGATIONS = "security_investigations"
    COMPLIANCE = "compliance"
    SAFETY_DESK = "safety_desk"


# Label guide D0: the Destination each Category goes to when no exception applies.
DEFAULT_DESTINATION: dict[Category, Destination] = {
    Category.VEHICLE_BREAKDOWN: Destination.FLEET_SUPPORT,
    Category.DELIVERY_DELAY: Destination.CUSTOMER_DESK,
    Category.SHIPMENT_DAMAGE: Destination.CLAIMS,
    Category.MISSING_SHIPMENT: Destination.SECURITY_INVESTIGATIONS,
    Category.DOCUMENTATION_ISSUE: Destination.COMPLIANCE,
    Category.SAFETY_INCIDENT: Destination.SAFETY_DESK,
}

URGENT = "urgent"
ROUTINE = "routine"


@dataclass(frozen=True)
class Report:
    """An Incident Report. Approaches read only `text`; the rest is provenance."""

    report_id: str
    scenario_id: str
    text: str
    author_role: str
    channel: str


@dataclass(frozen=True)
class Label:
    """The reference answer for an Incident Report."""

    category: Category
    urgency: str  # URGENT | ROUTINE
    destination: Destination


@dataclass(frozen=True)
class Scenario:
    scenario_id: str
    split: str
    category: Category
    urgency: str
    destination: Destination
    destination_is_exception: bool
    tags: list[str] = field(default_factory=list)
    facts: list[str] = field(default_factory=list)
    label_reason: str = ""

    @property
    def label(self) -> Label:
        """The Seeded Label."""
        return Label(self.category, self.urgency, self.destination)


@dataclass(frozen=True)
class Prediction:
    """One approach's triage decisions for one Incident Report, with raw probabilities.

    Policies turn these into a Routing Mode after the fact, so nothing here is thresholded
    except the top `category` / `destination` and the approach's own `triggers`.
    """

    report_id: str
    approach: str  # "A" | "B" | "C"
    category: Category
    category_probs: dict[str, float]
    urgent_prob: float
    destination: Destination
    destination_probs: dict[str, float]
    evidence: list[str]  # verbatim sentences from the report
    triggers: list[str]  # Review Trigger codes raised by the approach itself
    latency_ms: float
    input_tokens: int
    output_tokens: int
    attempts: int
    error: str | None
    model: str | None
    version: str  # rule-set or question-set version that produced it
    source: str | None = None  # cascade only: "A" or "B", whose prediction was used

    def to_json(self) -> str:
        return json.dumps(asdict(self), ensure_ascii=False)

    @classmethod
    def from_json(cls, line: str) -> Prediction:
        data = json.loads(line)
        data["category"] = Category(data["category"])
        data["destination"] = Destination(data["destination"])
        return cls(**data)


def _jsonl(path: str | Path) -> list[dict]:
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def load_reports(path: str | Path) -> list[Report]:
    """Read data/reports.jsonl; fields outside Report (generator, synthetic) are ignored."""
    return [
        Report(
            report_id=d["report_id"],
            scenario_id=d["scenario_id"],
            text=d["text"],
            author_role=d["author_role"],
            channel=d["channel"],
        )
        for d in _jsonl(path)
    ]


def load_scenarios(path: str | Path) -> list[Scenario]:
    return [
        Scenario(
            scenario_id=d["scenario_id"],
            split=d["split"],
            category=Category(d["category"]),
            urgency=d["urgency"],
            destination=Destination(d["destination"]),
            destination_is_exception=d["destination_is_exception"],
            tags=d.get("tags", []),
            facts=d.get("facts", []),
            label_reason=d.get("label_reason", ""),
        )
        for d in _jsonl(path)
    ]


def load_predictions(path: str | Path) -> list[Prediction]:
    with open(path, encoding="utf-8") as f:
        return [Prediction.from_json(line) for line in f if line.strip()]


def write_predictions(path: str | Path, predictions: list[Prediction]) -> None:
    """Write sorted by report_id, one JSON object per line, LF endings."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.writelines(p.to_json() + "\n" for p in sorted(predictions, key=lambda p: p.report_id))


# --- Sentence splitting (Evidence candidates for A and B) -----------------------------------

# Words that end with a full stop but do not end a sentence (lower-cased, without the stop).
_ABBREVIATIONS = {"approx", "st", "no", "nos", "mr", "mrs", "ms", "dr", "e.g", "i.e", "eg", "ie",
                  "vs", "ref", "tel", "nr", "rd", "ave", "est", "dept", "co", "ltd", "inc"}
# End punctuation, any closing quotes or brackets, then whitespace.
_BOUNDARY = re.compile(r"[.!?]+[\"')\]]*(?=\s)")
_SENTENCE_START = re.compile(r"\s+[\"'(\[]?[A-Z0-9]")
_LAST_WORD = re.compile(r"([A-Za-z.]+)\.$")


def split_sentences(text: str) -> list[str]:
    """Split a report into sentences, deterministically, each a verbatim substring of `text`.

    Every line break splits. Within a line, a sentence ends at . ! or ? (plus closing quotes)
    when the next word starts with a capital letter, digit or opening quote, unless the word
    before the stop is a known abbreviation ("approx.", "St.").
    """
    sentences: list[str] = []
    for line in text.splitlines():
        start = 0
        for m in _BOUNDARY.finditer(line):
            if not _SENTENCE_START.match(line, m.end()):
                continue
            word = _LAST_WORD.search(line[start : m.start() + 1])
            if m.group().startswith(".") and word and word.group(1).lower() in _ABBREVIATIONS:
                continue
            sentences.append(line[start : m.end()].strip())
            start = m.end()
        sentences.append(line[start:].strip())
    return [s for s in sentences if s]
