import importlib.util
import json
import shutil
from pathlib import Path

from triage import baseline
from triage.schema import load_reports, load_scenarios, write_predictions

from .conftest import FIXTURES

_spec = importlib.util.spec_from_file_location(
    "export_web", Path(__file__).parent.parent / "eval" / "export_web.py")
export_web = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(export_web)

# Keys that would leak a Label or a prediction to the blind labeller.
FORBIDDEN = {"label", "labels", "category", "urgency", "destination", "scenario_id",
             "predictions", "urgent_prob", "evidence", "routing_mode", "review_triggers"}


def _keys(value) -> set[str]:
    if isinstance(value, dict):
        return set(value) | {k for v in value.values() for k in _keys(v)}
    if isinstance(value, list):
        return {k for v in value for k in _keys(v)}
    return set()


def _workspace(tmp_path: Path) -> Path:
    """Fixture reports with Seeded Labels, A predictions on test and Blind Labels."""
    (tmp_path / "data" / "labels").mkdir(parents=True)
    shutil.copy(FIXTURES / "reports.jsonl", tmp_path / "data" / "reports.jsonl")
    shutil.copy(FIXTURES / "scenarios.jsonl", tmp_path / "data" / "scenarios.jsonl")
    shutil.copytree("policies", tmp_path / "policies")
    split = {s.scenario_id: s for s in load_scenarios(FIXTURES / "scenarios.jsonl")}
    test = [r for r in load_reports(FIXTURES / "reports.jsonl")
            if split[r.scenario_id].split == "test"]
    write_predictions(tmp_path / "results" / "predictions" / "A_test.jsonl",
                      [baseline.predict(r) for r in test])
    blind = [{"report_id": r.report_id, "category": split[r.scenario_id].category.value,
              "urgency": split[r.scenario_id].urgency,
              "destination": split[r.scenario_id].destination.value,
              "pass": 1, "labelled_at": "2026-10-27T10:00:00Z"} for r in test]
    (tmp_path / "data" / "labels" / "blind_test.json").write_text(json.dumps(blind))
    return tmp_path


def test_labelling_json_has_test_text_but_no_label_or_prediction_keys(tmp_path):
    root = _workspace(tmp_path)
    out = root / "out"
    export_web.export(root, out, split="test")

    incidents = json.loads((out / "incidents.json").read_text(encoding="utf-8"))
    labelling = json.loads((out / "labelling.json").read_text(encoding="utf-8"))

    # The same run does export Labels and predictions for the Queue ...
    assert {"label", "predictions", "urgent_prob"} <= _keys(incidents)
    # ... and the labeller gets exactly the test reports' ids and text, nothing else.
    assert sorted(r["id"] for r in labelling["reports"]) == [
        "R-9002", "R-9005", "R-9008", "R-9011", "R-9014", "R-9017", "R-9020"]
    assert {k for r in labelling["reports"] for k in r} == {"id", "text"}
    assert _keys(labelling) & FORBIDDEN == set()
    assert "Blow-out on the nearside steer tyre" in json.dumps(labelling)


def test_export_tolerates_an_empty_repo_and_is_deterministic(tmp_path):
    export_web.export(tmp_path, tmp_path / "a")
    export_web.export(tmp_path, tmp_path / "b")
    incidents = json.loads((tmp_path / "a" / "incidents.json").read_text(encoding="utf-8"))
    assert incidents["reports"] == [] and incidents["split"] == "test"
    for name in ("incidents.json", "results.json", "curve.json", "labelling.json"):
        assert (tmp_path / "a" / name).read_bytes() == (tmp_path / "b" / name).read_bytes()


def test_build_curve_reads_tune_flat_list(tmp_path):
    (tmp_path / "results").mkdir()
    pts = [{"review_rate": 0.1, "missed_urgent": 2, "sweep_policy": "v1", "chosen": False},
           {"review_rate": 0.5, "missed_urgent": 0, "sweep_policy": "v1", "chosen": True},
           {"review_rate": 0.6, "missed_urgent": 0, "sweep_policy": "v2", "chosen": True}]
    (tmp_path / "results" / "curve_validation.json").write_text(json.dumps({"A": pts}))
    got = export_web.build_curve(tmp_path, fixture=False)
    assert got["split"] == "validation"
    assert got["approaches"]["A"] == {"points": pts[:1], "v1": pts[1], "v2": pts[2]}
