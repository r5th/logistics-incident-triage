from triage.schema import Category, Destination, Label, Prediction, load_reports, load_scenarios

from .conftest import FIXTURES


def _prediction(**overrides):
    fields = {
        "report_id": "R-0001",
        "approach": "A",
        "category": Category.SHIPMENT_DAMAGE,
        "category_probs": {"shipment_damage": 0.7, "missing_shipment": 0.3},
        "urgent_prob": 0.95,
        "destination": Destination.SECURITY_INVESTIGATIONS,
        "destination_probs": {"security_investigations": 0.6, "claims": 0.4},
        "evidence": ["Seal number on the doors does not match the CMR."],
        "triggers": ["location_missing"],
        "latency_ms": 1.25,
        "input_tokens": 0,
        "output_tokens": 0,
        "attempts": 1,
        "error": None,
        "model": None,
        "version": "a-v1",
        "source": None,
    }
    fields.update(overrides)
    return Prediction(**fields)


def test_prediction_round_trips_through_json():
    pred = _prediction(error="boom", model="jev-1.14.0", source="B")
    back = Prediction.from_json(pred.to_json())
    assert back == pred
    assert back.category is Category.SHIPMENT_DAMAGE
    assert back.destination is Destination.SECURITY_INVESTIGATIONS


def test_prediction_json_is_one_line_with_enum_values():
    line = _prediction().to_json()
    assert "\n" not in line
    assert '"category": "shipment_damage"' in line
    assert '"destination": "security_investigations"' in line


def test_load_reports_reads_contract_fields_and_ignores_extras():
    reports = load_reports(FIXTURES / "reports.jsonl")
    assert len(reports) == 21
    first = reports[0]
    assert (first.report_id, first.scenario_id, first.author_role, first.channel) == (
        "R-9001", "S-F01", "driver", "app")
    assert first.text.startswith("Gearbox has gone on the A49")


def test_load_scenarios_exposes_the_seeded_label():
    scenarios = {s.scenario_id: s for s in load_scenarios(FIXTURES / "scenarios.jsonl")}
    s = scenarios["S-F09"]
    assert s.split == "build"
    assert s.destination_is_exception is True
    assert s.label == Label(Category.SHIPMENT_DAMAGE, "urgent", Destination.SECURITY_INVESTIGATIONS)
