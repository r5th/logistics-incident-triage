import json

import pytest
from typesafe_sdk import Choice, Noul, SystemOneResponse, TypeSafeAPITimeoutError

from triage.schema import Category, Destination, Report
from triage.typesafe_ai import (
    MAX_EVIDENCE_SENTENCES,
    MODEL,
    QUESTIONS_VERSION,
    SpendCapExceeded,
    SpendGuard,
    TypeSafeTriager,
    build_questions,
    load_api_key,
)

TEXT = ("Blow-out on the M1 near J23. Pulled onto the hard shoulder. "
        "Seal on the trailer is broken and two cartons of laptops are smashed.")
REPORT = Report("R-0042", "S-X", TEXT, "driver", "app")


def _answers(**overrides):
    answers = {
        "category": {"type": "choice", "choice": "shipment_damage", "confidence": 0.8,
                     "probabilities": {"vehicle_breakdown": 0.2, "delivery_delay": 0.0,
                                       "shipment_damage": 0.7, "missing_shipment": 0.1,
                                       "documentation_issue": 0.0, "safety_incident": 0.0}},
        "urgent": {"type": "noul", "noul": 0.91},
        "destination": {"type": "choice", "choice": "security_investigations",
                        "confidence": 0.6,
                        "probabilities": {"fleet_support": 0.1, "customer_desk": 0.0,
                                          "claims": 0.3, "security_investigations": 0.6,
                                          "compliance": 0.0, "safety_desk": 0.0}},
        "location_stated": {"type": "noul", "noul": 0.2},
        "cargo_identified": {"type": "noul", "noul": 0.9},
        "conflicting_statements": {"type": "noul", "noul": 0.8},
        "multiple_issues": {"type": "noul", "noul": 0.4},
        "evidence_category": {"type": "choice", "choice": "s3", "confidence": 0.9,
                              "probabilities": {"s1": 0.05, "s2": 0.05, "s3": 0.9}},
        "evidence_urgency": {"type": "choice", "choice": "s3", "confidence": 0.5,
                             "probabilities": {"s1": 0.25, "s2": 0.15, "s3": 0.6}},
    }
    answers.update(overrides)
    return answers


class FakeClient:
    """Stands in for TypeSafeClient: records each request, returns a canned response."""

    def __init__(self, answers=None, error=None, input_tokens=1200):
        self.answers, self.error, self.input_tokens = answers, error, input_tokens
        self.calls = []

    def system_one(self, state, questions, **kwargs):
        self.calls.append({"state": state, "questions": questions, **kwargs})
        if self.error:
            raise self.error
        return SystemOneResponse.model_validate({
            "model": "jev-1.14.0",
            "usage": {"input_tokens": self.input_tokens, "output_tokens": 30},
            "answers": self.answers,
        })


def _triager(tmp_path, client, cap_usd=5.0):
    return TypeSafeTriager(client=client,
                           spend_guard=SpendGuard(tmp_path / "spend.json", cap_usd=cap_usd))


def test_question_set_has_every_decision_and_evidence_over_the_reports_sentences():
    qs = build_questions(["Tyre gone.", "Seal broken."])
    assert sorted(qs) == sorted(["category", "urgent", "destination", "location_stated",
                                 "cargo_identified", "conflicting_statements",
                                 "multiple_issues", "evidence_category", "evidence_urgency"])
    assert isinstance(qs["urgent"], Noul) and isinstance(qs["category"], Choice)
    assert set(qs["category"].criteria) == {c.value for c in Category}
    assert set(qs["destination"].criteria) == {d.value for d in Destination}
    assert qs["evidence_category"].criteria == {"s1": "Tyre gone.", "s2": "Seal broken."}


def test_evidence_options_are_capped():
    sentences = [f"Sentence {i}." for i in range(30)]
    qs = build_questions(sentences)
    assert len(qs["evidence_urgency"].criteria) == MAX_EVIDENCE_SENTENCES == 24
    assert qs["evidence_urgency"].criteria["s24"] == "Sentence 23."


def test_one_call_maps_answers_to_a_prediction(tmp_path):
    client = FakeClient(_answers())
    pred = _triager(tmp_path, client).predict(REPORT)
    assert len(client.calls) == 1
    assert client.calls[0]["state"] == {"report": TEXT}
    assert client.calls[0]["model"] == MODEL
    assert (pred.report_id, pred.approach, pred.version, pred.model) == (
        "R-0042", "B", QUESTIONS_VERSION, "jev-1.14.0")
    assert pred.category == Category.SHIPMENT_DAMAGE
    assert pred.category_probs["vehicle_breakdown"] == 0.2
    assert pred.urgent_prob == 0.91
    assert pred.destination == Destination.SECURITY_INVESTIGATIONS
    assert pred.evidence == [
        "Seal on the trailer is broken and two cartons of laptops are smashed."]
    assert pred.triggers == ["location_missing", "conflicting_statements"]
    assert (pred.input_tokens, pred.output_tokens, pred.attempts, pred.error) == (
        1200, 30, 1, None)


def test_urgency_evidence_is_added_only_when_predicted_urgent(tmp_path):
    answers = _answers(evidence_urgency={"type": "choice", "choice": "s1", "confidence": 0.5,
                                         "probabilities": {"s1": 0.7, "s2": 0.2, "s3": 0.1}})
    urgent = _triager(tmp_path, FakeClient(answers)).predict(REPORT)
    assert urgent.evidence == ["Blow-out on the M1 near J23.",
                               ("Seal on the trailer is broken and two cartons of laptops are "
                               "smashed.")]
    answers["urgent"] = {"type": "noul", "noul": 0.1}
    routine = _triager(tmp_path, FakeClient(answers)).predict(REPORT)
    assert routine.evidence == [
        "Seal on the trailer is broken and two cartons of laptops are smashed."]


def test_api_failure_becomes_an_error_prediction_not_an_answer(tmp_path):
    client = FakeClient(error=TypeSafeAPITimeoutError(timeout=10.0))
    pred = _triager(tmp_path, client).predict(REPORT)
    assert pred.error.startswith("TypeSafeAPITimeoutError")
    assert pred.triggers == ["invalid_output"]
    assert pred.urgent_prob == 0.5
    assert pred.category_probs == {c.value: pytest.approx(1 / 6) for c in Category}
    assert pred.destination_probs == {d.value: pytest.approx(1 / 6) for d in Destination}
    assert pred.evidence == []


def test_answer_missing_a_question_is_invalid_output(tmp_path):
    answers = _answers()
    del answers["urgent"]
    pred = _triager(tmp_path, FakeClient(answers)).predict(REPORT)
    assert (pred.triggers, pred.error) == (["invalid_output"], "invalid output: missing 'urgent'")


def test_spend_guard_accumulates_tokens_across_runs(tmp_path):
    _triager(tmp_path, FakeClient(_answers())).predict(REPORT)
    _triager(tmp_path, FakeClient(_answers())).predict(REPORT)
    spend = json.loads((tmp_path / "spend.json").read_text(encoding="utf-8"))
    assert (spend["input_tokens"], spend["output_tokens"], spend["calls"]) == (2400, 60, 2)
    assert spend["usd"] == pytest.approx(2400 * 0.042 / 1e6)


def test_spend_guard_aborts_before_the_call_when_projected_cost_exceeds_cap(tmp_path):
    (tmp_path / "spend.json").write_text(json.dumps(
        {"input_tokens": 119_100_000, "output_tokens": 0, "calls": 1}), encoding="utf-8")
    client = FakeClient(_answers())
    with pytest.raises(SpendCapExceeded, match="US\\$5"):
        _triager(tmp_path, client).predict(REPORT)
    assert client.calls == []
    fresh = FakeClient(_answers())
    _triager(tmp_path / "fresh", fresh).predict(REPORT)
    assert len(fresh.calls) == 1


def test_api_key_comes_from_env_file_when_unset(tmp_path, monkeypatch):
    monkeypatch.delenv("TYPESAFE_API_KEY", raising=False)
    env = tmp_path / ".env"
    env.write_text("TYPESAFE_API_KEY=ts-from-file\n", encoding="utf-8")
    assert load_api_key(env) == "ts-from-file"
    monkeypatch.setenv("TYPESAFE_API_KEY", "ts-from-env")
    assert load_api_key(env) == "ts-from-env"


@pytest.mark.live
def test_live_smoke_one_report():
    """Calls the real API once. Run with: python -m uv run pytest -m live"""
    pred = TypeSafeTriager().predict(Report(
        "R-LIVE", "S-LIVE", "One of the drums of UN1263 paint (class 3) is leaking in the "
        "back of the trailer at the Avonmouth depot. Strong smell, we've kept people away.",
        "driver", "app"))
    assert pred.error is None
    assert (pred.category, pred.destination) == (Category.SAFETY_INCIDENT,
                                                 Destination.SAFETY_DESK)
    assert pred.urgent_prob > 0.5
