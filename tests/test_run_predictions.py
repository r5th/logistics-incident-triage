import hashlib
import importlib.util
import json
import shutil
from pathlib import Path

import pytest

from triage.schema import load_predictions

from .conftest import FIXTURES

_spec = importlib.util.spec_from_file_location(
    "run_predictions", Path(__file__).parent.parent / "eval" / "run_predictions.py")
run_predictions = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(run_predictions)

FLAG = "--i-know-this-is-the-one-test-run"


@pytest.fixture
def workspace(tmp_path):
    """data/, policies/ and results/ laid out as in the repo, from the fixtures."""
    (tmp_path / "data").mkdir()
    shutil.copy(FIXTURES / "reports.jsonl", tmp_path / "data" / "reports.jsonl")
    shutil.copy(FIXTURES / "scenarios.jsonl", tmp_path / "data" / "scenarios.jsonl")
    shutil.copytree("policies", tmp_path / "policies")
    for v in ("v1", "v2"):  # the repo's Policies may be frozen; tests start unfrozen
        path = tmp_path / "policies" / f"{v}.json"
        raw = json.loads(path.read_text(encoding="utf-8"))
        raw["frozen"] = False
        raw.pop("frozen_on", None)
        path.write_text(json.dumps(raw), encoding="utf-8")
    return tmp_path


def _freeze(workspace, *versions):
    """Freeze like eval/tune.py --freeze: frozen flag plus validation-prediction hashes."""
    tuned_on = _out(workspace, "A_validation.jsonl")
    if not tuned_on.exists():
        tuned_on.parent.mkdir(parents=True, exist_ok=True)
        tuned_on.write_text("", encoding="utf-8")
    for v in versions:
        path = workspace / "policies" / f"{v}.json"
        raw = json.loads(path.read_text(encoding="utf-8"))
        raw["frozen"] = True
        raw["frozen_on"] = {"split": "validation", "predictions_sha256": {
            "results/predictions/A_validation.jsonl":
                hashlib.sha256(tuned_on.read_bytes()).hexdigest()}}
        path.write_text(json.dumps(raw), encoding="utf-8")


def _run(workspace, *args):
    return run_predictions.main([*args, "--root", str(workspace)])


def _out(workspace, name):
    return workspace / "results" / "predictions" / name


def test_a_writes_only_the_split_sorted_by_report_id(workspace):
    _run(workspace, "--approach", "A", "--split", "validation")
    preds = load_predictions(_out(workspace, "A_validation.jsonl"))
    # fixture splits cycle build/validation/test by row, so validation is rows 1, 4, 7, ...
    assert [p.report_id for p in preds] == [f"R-90{i:02d}" for i in range(1, 22, 3)]


def test_a_output_is_deterministic_apart_from_measured_latency(workspace):
    _run(workspace, "--approach", "A", "--split", "build")
    first = load_predictions(_out(workspace, "A_build.jsonl"))
    _run(workspace, "--approach", "A", "--split", "build")
    second = load_predictions(_out(workspace, "A_build.jsonl"))
    strip = [{**p.__dict__, "latency_ms": 0} for p in first]
    assert strip == [{**p.__dict__, "latency_ms": 0} for p in second]


@pytest.mark.parametrize("frozen, args", [
    ((), [FLAG]),  # flag but policies not frozen
    (("v1",), [FLAG]),  # only one frozen
    (("v1", "v2"), []),  # frozen but no flag
])
def test_test_split_is_refused_unless_both_policies_frozen_and_flag_passed(
        workspace, frozen, args):
    _freeze(workspace, *frozen)
    with pytest.raises(SystemExit, match="test split"):
        _run(workspace, "--approach", "A", "--split", "test", *args)
    assert not _out(workspace, "A_test.jsonl").exists()


def test_test_split_runs_once_both_policies_are_frozen_and_flag_passed(workspace):
    _freeze(workspace, "v1", "v2")
    _run(workspace, "--approach", "A", "--split", "test", FLAG)
    assert len(load_predictions(_out(workspace, "A_test.jsonl"))) == 7


def test_b_on_test_refuses_to_overwrite_an_existing_run(workspace):
    _freeze(workspace, "v1", "v2")
    out = _out(workspace, "B_test.jsonl")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("existing\n", encoding="utf-8")
    with pytest.raises(SystemExit, match="B_test.jsonl already exists"):
        _run(workspace, "--approach", "B", "--split", "test", FLAG)
    assert out.read_text(encoding="utf-8") == "existing\n"


def test_c_combines_cached_a_and_b_without_api_calls(workspace, monkeypatch):
    _run(workspace, "--approach", "A", "--split", "build")
    a = load_predictions(_out(workspace, "A_build.jsonl"))
    b_path = _out(workspace, "B_build.jsonl")
    b_path.write_text("".join(
        p.__class__(**{**p.__dict__, "approach": "B", "version": "b-v1"}).to_json() + "\n"
        for p in a), encoding="utf-8")
    monkeypatch.setattr(run_predictions, "TypeSafeTriager", None)  # any API use would crash
    _run(workspace, "--approach", "C", "--split", "build")
    c = load_predictions(_out(workspace, "C_build.jsonl"))
    assert [p.report_id for p in c] == [p.report_id for p in a]
    assert {p.approach for p in c} == {"C"}
    assert {p.source for p in c} <= {"A", "B"} and len(c) == 7


def test_c_needs_cached_b(workspace):
    _run(workspace, "--approach", "A", "--split", "build")
    with pytest.raises(SystemExit, match="B_build.jsonl"):
        _run(workspace, "--approach", "C", "--split", "build")


def test_test_split_is_refused_when_validation_predictions_changed_after_freeze(workspace):
    _freeze(workspace, "v1", "v2")
    _out(workspace, "A_validation.jsonl").write_text("changed\n", encoding="utf-8")
    with pytest.raises(SystemExit, match="provenance"):
        _run(workspace, "--approach", "A", "--split", "test", FLAG)
    assert not _out(workspace, "A_test.jsonl").exists()


@pytest.mark.parametrize("approach", ["A", "C"])
def test_no_approach_overwrites_its_test_run(workspace, approach):
    _freeze(workspace, "v1", "v2")
    out = _out(workspace, f"{approach}_test.jsonl")
    out.write_text("existing\n", encoding="utf-8")
    with pytest.raises(SystemExit, match=f"{approach}_test.jsonl already exists"):
        _run(workspace, "--approach", approach, "--split", "test", FLAG)
    assert out.read_text(encoding="utf-8") == "existing\n"


def test_interrupted_b_test_run_resumes_without_repeating_calls(workspace, monkeypatch):
    from triage import baseline
    _freeze(workspace, "v1", "v2")
    calls = []

    class Fake:
        def __init__(self, **_):
            pass

        def predict(self, report):
            calls.append(report.report_id)
            if len(calls) == 3:
                raise KeyboardInterrupt  # interrupted mid-run
            p = baseline.predict(report)
            return p.__class__(**{**p.__dict__, "approach": "B", "version": "b-v1"})

    monkeypatch.setattr(run_predictions, "TypeSafeTriager", Fake)
    monkeypatch.setattr(run_predictions, "SpendGuard", lambda *_: None)
    with pytest.raises(KeyboardInterrupt):
        _run(workspace, "--approach", "B", "--split", "test", FLAG)
    assert not _out(workspace, "B_test.jsonl").exists()
    _run(workspace, "--approach", "B", "--split", "test", FLAG)
    ids = [p.report_id for p in load_predictions(_out(workspace, "B_test.jsonl"))]
    assert len(ids) == 7 and len(calls) == 3 + 5  # 2 kept, the interrupted one retried
    assert len(set(calls)) == 7  # every report called, only the interrupted one twice
    assert not _out(workspace, "B_test.partial.jsonl").exists()
