"""Cache one approach's Predictions for one split.

    python -m uv run python eval/run_predictions.py --approach A|B|C --split build|validation|test

Writes results/predictions/<approach>_<split>.jsonl, sorted by report_id. A is deterministic
apart from its measured latency. B calls TypeSafe once per report (spend-guarded). C combines
the cached A and B files and makes no API calls.

Test guard: the test split runs only when policies/v1.json and v2.json are both frozen and
--i-know-this-is-the-one-test-run is passed, and B never re-runs on test once B_test exists.
"""

from __future__ import annotations

import argparse
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
    if not confirmed:
        raise SystemExit(f"refusing the test split without {TEST_FLAG}")
    b_test = root / "results" / "predictions" / "B_test.jsonl"
    if approach == "B" and b_test.exists():
        raise SystemExit(f"refusing the test split: {b_test.name} already exists (one run only)")


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
            preds = []
            for i, r in enumerate(reports, 1):
                preds.append(triager.predict(r))
                if preds[-1].error:
                    print(f"  {r.report_id}: {preds[-1].error}")
                if i % 20 == 0:
                    print(f"  {i}/{len(reports)}")

    write_predictions(out, preds)
    errors = sum(p.error is not None for p in preds)
    print(f"wrote {len(preds)} predictions to {out} ({errors} errors)")


if __name__ == "__main__":
    main()
