import pytest

from triage.baseline import RULES_VERSION, predict
from triage.schema import Category, Destination, Report

FIXTURE_IDS = [f"F{i:02d}" for i in range(1, 22)]


def _report(text, report_id="R-T001"):
    return Report(report_id=report_id, scenario_id="S-T", text=text, author_role="driver",
                  channel="app")


@pytest.mark.parametrize("fid", FIXTURE_IDS)
def test_fixture_category_matches_seeded_label(fid, fixture_reports, fixture_labels):
    assert predict(fixture_reports[fid]).category == fixture_labels[fid].category


@pytest.mark.parametrize("fid", FIXTURE_IDS)
def test_fixture_urgency_comes_from_a_hard_rule(fid, fixture_reports, fixture_labels):
    expected = 0.95 if fixture_labels[fid].urgency == "urgent" else 0.05
    assert predict(fixture_reports[fid]).urgent_prob == expected


@pytest.mark.parametrize("fid", FIXTURE_IDS)
def test_fixture_destination_matches_seeded_label(fid, fixture_reports, fixture_labels):
    assert predict(fixture_reports[fid]).destination == fixture_labels[fid].destination


def test_prediction_metadata_for_rules():
    pred = predict(_report("Puncture on the A30 near Bodmin, in a lay-by. Dialysis fluids on board."))
    assert (pred.approach, pred.version, pred.input_tokens, pred.output_tokens) == (
        "A", RULES_VERSION, 0, 0)
    assert (pred.attempts, pred.error, pred.model, pred.report_id) == (1, None, None, "R-T001")
    assert pred.latency_ms >= 0
    assert pytest.approx(sum(pred.category_probs.values())) == 1.0
    assert pytest.approx(sum(pred.destination_probs.values())) == 1.0


def test_evidence_is_the_verbatim_sentences_that_fired(fixture_reports):
    pred = predict(fixture_reports["F16"])
    assert pred.evidence == [
        "Reversing onto the bay at Greystone in Wolverhampton, the trailer clipped their banksman.",
        "He has a graze and bruising on his forearm, first aid given.",
    ]


def test_thin_report_raises_location_and_cargo_triggers(fixture_reports):
    assert predict(fixture_reports["F20"]).triggers == ["location_missing", "cargo_missing"]
    assert predict(fixture_reports["F01"]).triggers == []


def test_no_rule_matched_gives_uniform_probabilities():
    pred = predict(_report("Please call me back when you get this, at the Leeds depot, pallets."))
    assert pred.triggers == ["no_rule_matched"]
    assert pred.category_probs == {c.value: pytest.approx(1 / 6) for c in Category}


def test_unrelated_issues_follow_p4_and_flag_conflicting_categories():
    pred = predict(_report("At the Derby store three pallets of tiles were short and two "
                           "pallets were crushed."))
    assert pred.category == Category.MISSING_SHIPMENT
    assert "conflicting_categories" in pred.triggers


def test_delay_caused_by_breakdown_is_the_breakdown_p2():
    pred = predict(_report("Clutch has failed at Corley services on the M6, parked in the HGV "
                           "park. Household goods for Tollbridge will be a day late."))
    assert (pred.category, pred.urgent_prob) == (Category.VEHICLE_BREAKDOWN, 0.05)


def test_damage_dangerous_goods_packaging_is_urgent_without_a_leak():
    pred = predict(_report("Two drums of class 3 paint have dented packaging and a cracked lid "
                           "at the Avonmouth depot, no leak seen."))
    assert (pred.category, pred.urgent_prob) == (Category.SHIPMENT_DAMAGE, 0.95)


@pytest.mark.parametrize("eta, expected", [("11:15", 0.95), ("09:40", 0.05)])
def test_medical_slot_compares_eta_with_slot_time(eta, expected):
    pred = predict(_report(f"Vaccines for the clinic in Leeds, slot 10:00. Stuck in traffic on "
                           f"the M62 near Huddersfield, ETA {eta}."))
    assert (pred.category, pred.urgent_prob) == (Category.DELIVERY_DELAY, expected)


def test_medical_delay_without_a_stated_miss_is_ambiguous():
    pred = predict(_report("Insulin for the hospital pharmacy in Leeds, stuck in traffic on the "
                           "M62."))
    assert pred.urgent_prob == 0.5


def test_frozen_load_back_in_refrigeration_within_the_hour_is_ambiguous():
    pred = predict(_report("Reefer unit stopped on the A1(M) about 30 minutes from the RDC with "
                           "frozen ice cream. Box at -18 C and they will tip on arrival."))
    assert (pred.category, pred.urgent_prob) == (Category.VEHICLE_BREAKDOWN, 0.5)


def test_contradictory_lane_position_is_urgent_i3():
    pred = predict(_report("Brakes locked on, stopped on the M25 near J27 on the hard shoulder. "
                           "Cars are having to swerve round the back of the trailer in lane 1."))
    assert (pred.category, pred.urgent_prob) == (Category.VEHICLE_BREAKDOWN, 0.95)


def test_paperwork_hold_is_documentation_not_authority_delay():
    pred = predict(_report("DVSA have held us at Ashby because the driver card has expired. "
                           "Ambient load, delivery will be late."))
    assert (pred.category, pred.destination) == (
        Category.DOCUMENTATION_ISSUE, Destination.COMPLIANCE)


def test_missing_with_innocent_explanation_but_breached_seal_stays_security_x1():
    pred = predict(_report("Two pallets short at the Leeds RDC, we think they were left behind "
                           "at loading. Seal number does not match the paperwork though."))
    assert (pred.category, pred.urgent_prob, pred.destination) == (
        Category.MISSING_SHIPMENT, 0.95, Destination.SECURITY_INVESTIGATIONS)


def test_rules_are_deterministic(fixture_reports):
    a, b = predict(fixture_reports["F09"]), predict(fixture_reports["F09"])
    assert (a.category_probs, a.destination_probs, a.evidence) == (
        b.category_probs, b.destination_probs, b.evidence)
