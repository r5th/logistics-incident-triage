import json
from pathlib import Path

import pytest

from triage.policy import Policy, cost, load_policy, predicted_urgency, routing_mode
from triage.schema import Category, Destination, Label

from .test_schema import _prediction

D = Destination
C = Category


def _policy(**threshold_overrides):
    thresholds = {"urgent_threshold": 0.5, "review_band": [0.3, 0.7], "min_category_prob": 0.6,
                      "min_destination_prob": 0.6}
    thresholds.update(threshold_overrides)
    return Policy(
        version="t",
        costs={"missed_urgent": 20, "wrong_destination": 5, "false_alarm": 2,
                   "wrong_category_same_destination": 1, "review": 1},
        thresholds=thresholds,
        forcing_triggers=["conflicting_statements"],
    )


def _confident(**overrides):
    """A prediction that auto-routes under _policy(): damage, routine, claims, no triggers."""
    fields = {"category": C.SHIPMENT_DAMAGE, "category_probs": {"shipment_damage": 0.9},
                  "urgent_prob": 0.05, "destination": D.CLAIMS, "destination_probs": {"claims": 0.9},
                  "triggers": []}
    fields.update(overrides)
    return _prediction(**fields)


def test_shipped_policies_differ_only_in_missed_urgent_cost():
    v1, v2 = load_policy("policies/v1.json"), load_policy("policies/v2.json")
    assert (v1.version, v2.version) == ("v1", "v2")
    assert v2.costs["missed_urgent"] > v1.costs["missed_urgent"]
    assert ({k: v for k, v in v1.costs.items() if k != "missed_urgent"}
            == {k: v for k, v in v2.costs.items() if k != "missed_urgent"})
    assert v1.thresholds == v2.thresholds and v1.forcing_triggers == v2.forcing_triggers


def test_load_policy_reads_frozen_flag(tmp_path):
    raw = json.loads(Path("policies/v1.json").read_text(encoding="utf-8"))
    raw["frozen"] = True
    path = tmp_path / "p.json"
    path.write_text(json.dumps(raw), encoding="utf-8")
    assert load_policy(path).frozen is True
    assert load_policy("policies/v1.json").frozen is False


@pytest.mark.parametrize("p, expected", [(0.49, "routine"), (0.5, "urgent"), (0.95, "urgent")])
def test_predicted_urgency_uses_urgent_threshold(p, expected):
    assert predicted_urgency(_confident(urgent_prob=p), _policy()) == expected


def test_confident_prediction_auto_routes_with_no_reasons():
    assert routing_mode(_confident(), _policy()) == ("auto", [])


@pytest.mark.parametrize("p, mode", [(0.29, "auto"), (0.3, "review"), (0.5, "review"),
                                     (0.7, "review"), (0.71, "auto")])
def test_review_band_edges_are_inclusive(p, mode):
    got, reasons = routing_mode(_confident(urgent_prob=p), _policy())
    assert got == mode
    assert reasons == (["Urgency uncertain"] if mode == "review" else [])


def test_forcing_trigger_sends_to_review_but_other_triggers_do_not():
    pred = _confident(triggers=["conflicting_statements", "location_missing"])
    assert routing_mode(pred, _policy()) == ("review", ["Conflicting statements"])
    assert routing_mode(_confident(triggers=["location_missing"]), _policy()) == ("auto", [])


def test_low_top_probabilities_send_to_review_with_named_reasons():
    pred = _confident(category_probs={"shipment_damage": 0.55, "missing_shipment": 0.45},
                      destination_probs={"claims": 0.5, "security_investigations": 0.5})
    assert routing_mode(pred, _policy()) == (
        "review", ["Low category probability", "Low destination probability"])


def test_error_always_sends_to_review():
    mode, reasons = routing_mode(_confident(error="timeout"), _policy())
    assert (mode, reasons) == ("review", ["Prediction error"])


DAMAGE_ROUTINE_CLAIMS = Label(C.SHIPMENT_DAMAGE, "routine", D.CLAIMS)


@pytest.mark.parametrize("pred_overrides, label, expected", [
    ({}, DAMAGE_ROUTINE_CLAIMS, 0),
    ({}, Label(C.SHIPMENT_DAMAGE, "urgent", D.CLAIMS), 20),  # missed urgent
    ({"urgent_prob": 0.9, "category_probs": {"shipment_damage": 0.9}},
     DAMAGE_ROUTINE_CLAIMS, 2),  # false alarm
    ({}, Label(C.SHIPMENT_DAMAGE, "routine", D.SECURITY_INVESTIGATIONS), 5),  # wrong dest
    ({}, Label(C.VEHICLE_BREAKDOWN, "routine", D.CLAIMS), 1),  # wrong cat, right dest
    ({}, Label(C.MISSING_SHIPMENT, "urgent", D.SECURITY_INVESTIGATIONS), 25),  # both, no cat
])
def test_auto_route_cost_sums_applicable_terms(pred_overrides, label, expected):
    pred = _confident(**pred_overrides)
    assert routing_mode(pred, _policy())[0] == "auto"
    assert cost(pred, label, _policy()) == expected


def test_review_costs_only_the_review_cost_even_when_everything_is_wrong():
    pred = _confident(triggers=["conflicting_statements"])
    label = Label(C.MISSING_SHIPMENT, "urgent", D.SECURITY_INVESTIGATIONS)
    assert cost(pred, label, _policy()) == 1


def test_v2_costs_charge_more_for_the_same_missed_urgent():
    pred = _confident()
    label = Label(C.SHIPMENT_DAMAGE, "urgent", D.CLAIMS)
    base = _policy()
    v2 = load_policy("policies/v2.json")
    with_v2_costs = Policy(version="v2", costs=v2.costs, thresholds=base.thresholds,
                           forcing_triggers=base.forcing_triggers)
    assert (cost(pred, label, base), cost(pred, label, with_v2_costs)) == (20, 100)
