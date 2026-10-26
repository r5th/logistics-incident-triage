import pytest

from triage.cascade import cascade, cascade_all
from triage.schema import Category, Destination

from .test_schema import _prediction

CONFIDENT_A = {"approach": "A", "category": Category.VEHICLE_BREAKDOWN,
                   "category_probs": {"vehicle_breakdown": 0.8, "delivery_delay": 0.2},
                   "urgent_prob": 0.95, "destination": Destination.FLEET_SUPPORT, "triggers": [],
                   "latency_ms": 0.5, "version": "a-v1"}
B = {"approach": "B", "category": Category.SAFETY_INCIDENT,
         "category_probs": {"vehicle_breakdown": 0.3, "safety_incident": 0.7}, "urgent_prob": 0.8,
         "destination": Destination.SAFETY_DESK, "triggers": ["multiple_issues"], "latency_ms": 250.0,
         "input_tokens": 1500, "output_tokens": 40, "model": "jev-1.14.0", "version": "b-v1"}


def _a(**overrides):
    return _prediction(**{**CONFIDENT_A, **overrides})


def test_confident_a_is_used_without_calling_on_b():
    c = cascade(_a(), _prediction(**B))
    assert (c.approach, c.source, c.category, c.urgent_prob) == (
        "C", "A", Category.VEHICLE_BREAKDOWN, 0.95)
    assert (c.latency_ms, c.input_tokens, c.version) == (0.5, 0, "a-v1")


@pytest.mark.parametrize("a_overrides", [
    {"triggers": ["location_missing"]},
    {"category_probs": {"vehicle_breakdown": 0.6, "delivery_delay": 0.4}},  # margin 0.2
    {"urgent_prob": 0.5},
])
def test_doubtful_a_hands_over_to_b(a_overrides):
    c = cascade(_a(**a_overrides), _prediction(**B))
    assert (c.approach, c.source, c.category, c.triggers) == (
        "C", "B", Category.SAFETY_INCIDENT, ["multiple_issues"])
    # B only runs after A, so the cascade pays both latencies and B's tokens.
    assert (c.latency_ms, c.input_tokens, c.version) == (250.5, 1500, "b-v1")


def test_routine_hard_rule_counts_as_confident():
    assert cascade(_a(urgent_prob=0.05), _prediction(**B)).source == "A"


def test_cascade_all_joins_on_report_id_and_rejects_mismatches():
    a = [_a(report_id="R-2"), _a(report_id="R-1", triggers=["cargo_missing"])]
    b = [_prediction(**B, report_id="R-1"), _prediction(**B, report_id="R-2")]
    assert [(p.report_id, p.source) for p in cascade_all(a, b)] == [("R-1", "B"), ("R-2", "A")]
    with pytest.raises(ValueError, match="R-3"):
        cascade_all(a + [_a(report_id="R-3")], b)
