Implementation job.

# J2: evaluation harness, threshold tuning, agreement, and tests

## Goal

Turn cached Predictions into the evidence the submission rests on: per-approach, per-Policy
metrics with scenario-level bootstrap intervals, threshold tuning on validation only, the
operating-point curve, Missed Urgent case lists, latency and cost, and κ agreement for the
human labels. Every output is deterministic so CI can reproduce `results/` byte-for-byte.

## Base SHA

Given in the task message.

## Read first

`docs/build-plan.md` (source of truth), `GLOSSARY.md` (use its terms in names, output keys and
report prose), `src/triage/schema.py`, `src/triage/policy.py`, `policies/v1.json`, `tests/` (for
style), and `~/.claude/skills/behavior-tests/SKILL.md` in full: every test you write must be
able to go red.

## In scope

- `src/triage/policy.py` and `policies/v1.json`, `policies/v2.json` (only the change in step 1)
- `eval/evaluate.py`, `eval/tune.py`, `eval/agreement.py`, `eval/metrics.py` (new)
- `tests/test_metrics.py`, `tests/test_evaluate.py`, `tests/test_tune.py`,
  `tests/test_agreement.py`, `tests/test_policy.py` (edit only for step 1), `tests/fixtures/eval/`
- `results/.gitkeep`

Everything else is read-only. Standard library only (no numpy/pandas/sklearn).

## Steps

1. **Per-approach thresholds.** A's `urgent_prob` takes only values 0.05 / 0.5 / 0.95, so one
   threshold set cannot fit all approaches. Change the Policy JSON `thresholds` to
   `{"A": {...}, "B": {...}, "C": {...}}` (same four keys each) and make
   `predicted_urgency` / `routing_mode` pick `thresholds[pred.approach]`. Keep costs and
   `forcing_triggers` Policy-wide. Update the existing policy tests minimally to match.
2. **`eval/metrics.py`**: pure functions. Accuracy; per-class precision, recall, F1;
   macro-F1; confusion matrix (dict of dict, fixed label order from the schema enums);
   Cohen's κ; percentiles by nearest-rank (state this in the docstring); scenario-cluster
   bootstrap: resample Scenarios with replacement (all reports of a drawn Scenario come along),
   1,000 resamples, `random.Random(20261027)`, 2.5/97.5 percentiles.
3. **Labels.** `load_labels(split, source)`: `seeded` = the Scenario's Label via the report's
   `scenario_id`; `final` (test only) = `data/labels/adjudicated_test.json` when present, else
   `data/labels/blind_test.json` pass 1, else error. Label-file formats:
   `blind_test.json` = list of `{report_id, category, urgency, destination, pass (1|2), labelled_at}`;
   `adjudicated_test.json` = list of `{report_id, category, urgency, destination, seeded: {...},
   blind: {...}, ruling_note}`.
4. **`eval/evaluate.py --split <s> --labels seeded|final`**. For each approach whose file
   `results/predictions/<approach>_<split>.jsonl` exists, and each Policy (v1, v2), compute:
   - Category: accuracy, macro-F1, per-class P/R/F1, confusion matrix. Same for Destination.
   - Urgency (threshold applied, ignoring Routing Mode): recall, precision, counts.
   - Routing: review rate, Auto-route coverage, auto-routed error rate (auto-routed reports
     with any of the three decisions wrong), Missed Urgent count, and the Missed Urgent list
     (`report_id`, `scenario_id`, first 160 characters of text, `urgent_prob`, triggers).
   - Cost: total and per 100 reports under that Policy, split by cost term.
   - Reliability: error count, `invalid_output` count, mean attempts.
   - Latency: p50, p95, max, n (from `latency_ms`). Tokens: mean input/output per report.
     API cost per 1,000 reports at the price constant already in `src/triage/typesafe_ai.py`
     (import it; do not duplicate the number).
   - Bootstrap 95% CI for urgent recall, review rate, auto-routed error rate, cost per 100.
   Write `results/metrics_<split>_<labels>.json` (sorted keys, 2-space indent, floats rounded
   to 4 places, no timestamps, no absolute paths) and `results/report_<split>_<labels>.md`
   (markdown tables: an approaches × Policies summary first, then per-class tables, confusion
   matrices, the Missed Urgent lists, latency and cost; a short "How to read this" paragraph
   using glossary terms). Running it twice must give byte-identical files.
5. **`eval/tune.py --policy v1|v2`** (validation only; refuses any other split): for each
   approach, grid-search `urgent_threshold` ∈ {0.05..0.95 step 0.05}, `review_band` lo/hi
   from the same grid with lo ≤ urgent_threshold ≤ hi (include the empty band lo == hi),
   `min_category_prob` and `min_destination_prob` ∈ {0, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8}; pick
   minimum total cost on validation with seeded labels; tie-break by lower review rate, then
   by the lexicographically smallest threshold tuple. Write the thresholds into the Policy file
   with `"frozen": false`. `--freeze` sets `"frozen": true` and records
   `"frozen_on": {"split": "validation", "predictions_sha256": {<file>: <hash>}}`.
   Also write `results/curve_<split>.json` for a given split (`eval/tune.py --curve <split>`,
   allowed for validation, and for test only when both Policies are frozen): per approach, the
   points obtained by sweeping `urgent_threshold` and a symmetric `review_band` width with the
   other thresholds fixed at that Policy's values: `{review_rate, missed_urgent, cost_v1,
   cost_v2, urgent_threshold, band}`, plus the chosen v1 and v2 points marked.
6. **`eval/agreement.py`**: κ (and raw agreement, n) per decision for seeded vs blind pass 1
   over test; blind pass 1 vs pass 2 over the reports that have both. Writes
   `results/agreement.json` and a markdown section `results/agreement.md` that states plainly
   these are not inter-rater agreement between two people.
7. **Tests**, hand-computed on tiny fixtures in `tests/fixtures/eval/`: κ on a known 2×2 example
   (value written in the test with the arithmetic in a comment); nearest-rank p95; bootstrap
   determinism and that it resamples Scenarios, not reports; each cost term; tune's tie-break;
   tune refusing test; curve refusing test before freeze; evaluate byte-identical on two runs;
   label loading precedence. No network.

## Check

```
python -m uv run ruff check
python -m uv run pytest -q
python -m uv run python eval/evaluate.py --help
python -m uv run python eval/tune.py --help
```

Passing: ruff prints `All checks passed!`; pytest ends with `N passed` and no failures
(the 1 deselected live test is expected); both `--help` commands exit 0.

## Done when

All steps are implemented, the Check passes, and everything is committed on your branch in
one or more commits whose messages end with
`Co-Authored-By: GPT-6.1 Sol (Codex) <noreply@openai.com>`.

## Report

Max 200 words: worktree path, branch, base SHA, changed and added files, Check output tail,
any spec point you could not meet and why.
