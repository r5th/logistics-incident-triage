"""Cache one approach's Predictions for one split.

    python -m uv run python eval/run_predictions.py --approach A|B|C --split build|validation|test

Writes results/predictions/<approach>_<split>.jsonl, sorted by report_id. A is deterministic
apart from its measured latency. B calls TypeSafe once per report (spend-guarded). C combines
the cached A and B files and makes no API calls.

Test guard: the test split runs only when policies/v1.json and v2.json are both frozen, their
frozen_on hashes still match the validation predictions they were tuned on, and
--i-know-this-is-the-one-test-run is passed. No approach re-runs on test once its output exists.
B on test appends each Prediction to B_test.partial.jsonl as it arrives, so an interrupted run
resumes without calling TypeSafe again for reports it already has.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from triage import baseline
from triage.cascade import cascade_all
from triage.policy import load_policy
from triage.schema import load_predictions, load_reports, load_scenarios, write_predictions
from triage.typesafe_ai import SpendGuard, TypeSafeTriager

TEST_FLAG = "--i-know-this-is-the-one-test-run"


def check_test_guard(root: Path, approach: str, split: str, confirmed: bool) -> None:
    if split != "test":
        return
    unfrozen = [v for v in ("v1", "v2")
                if not load_policy(root / "policies" / f"{v}.json").frozen]
    if unfrozen:
        raise SystemExit(f"refusing the test split: policies {unfrozen} are not frozen")
    for v in ("v1", "v2"):
        hashes = json.loads((root / "policies" / f"{v}.json").read_text(encoding="utf-8")).get(
            "frozen_on", {}).get("predictions_sha256", {})
        stale = [name for name, digest in hashes.items()
                 if hashlib.sha256((root / name).read_bytes()).hexdigest() != digest]
        if not hashes or stale:
            raise SystemExit(f"refusing the test split: {v} freeze provenance is missing or stale"
                             f" {stale}; re-run eval/tune.py --policy {v} --freeze")
    if not confirmed:
        raise SystemExit(f"refusing the test split without {TEST_FLAG}")
    out = root / "results" / "predictions" / f"{approach}_test.jsonl"
    if out.exists():
        raise SystemExit(f"refusing the test split: {out.name} already exists (one run only)")


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--approach", choices=["A", "B", "C"], required=True)
    parser.add_argument("--split", choices=["build", "validation", "test"], required=True)
    parser.add_argument(TEST_FLAG, dest="confirmed", action="store_true")
    parser.add_argument("--root", type=Path, default=Path("."), help="repo root (tests only)")
    args = parser.parse_args(argv)
    root: Path = args.root

    check_test_guard(root, args.approach, args.split, args.confirmed)
    out_dir = root / "results" / "predictions"
    out = out_dir / f"{args.approach}_{args.split}.jsonl"

    if args.approach == "C":
        cached = {a: out_dir / f"{a}_{args.split}.jsonl" for a in ("A", "B")}
        for path in cached.values():
            if not path.exists():
                raise SystemExit(f"C needs cached predictions: {path} is missing")
        preds = cascade_all(load_predictions(cached["A"]), load_predictions(cached["B"]))
    else:
        split_of = {s.scenario_id: s.split for s in load_scenarios(root / "data" / "scenarios.jsonl")}
        reports = [r for r in load_reports(root / "data" / "reports.jsonl")
                   if split_of[r.scenario_id] == args.split]
        reports.sort(key=lambda r: r.report_id)
        if args.approach == "A":
            preds = [baseline.predict(r) for r in reports]
        else:
            triager = TypeSafeTriager(spend_guard=SpendGuard(root / "results" / "spend.json"))
            partial = out.with_name(out.stem + ".partial.jsonl")
            preds = load_predictions(partial) if args.split == "test" and partial.exists() else []
            done = {p.report_id for p in preds}
            for i, r in enumerate(reports, 1):
                if r.report_id in done:
                    continue
                preds.append(triager.predict(r))
                if args.split == "test":
                    with open(partial, "a", encoding="utf-8", newline="\n") as f:
                        f.write(preds[-1].to_json() + "\n")
                if preds[-1].error:
                    print(f"  {r.report_id}: {preds[-1].error}")
                if i % 20 == 0:
                    print(f"  {i}/{len(reports)}")

    write_predictions(out, preds)
    if args.approach == "B" and args.split == "test":
        out.with_name(out.stem + ".partial.jsonl").unlink(missing_ok=True)
    errors = sum(p.error is not None for p in preds)
    print(f"wrote {len(preds)} predictions to {out} ({errors} errors)")


if __name__ == "__main__":
    main()
