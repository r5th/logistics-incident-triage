# Logistics Incident Triage

This reads a free-text Incident Report from a road-freight operator and makes three decisions: Category, Urgency and Destination. A Policy then sets the Routing Mode: Auto-route, or send to Review. We compare three approaches on the same input: **A**, a transparent rules baseline; **B**, TypeSafe only (Jev); and **C**, a cascade that uses A when A is confident and B otherwise. The point is the cost of the decisions, not only accuracy. The main risk is a Missed Urgent: an urgent report auto-routed as routine.

Live demo: https://r5th.github.io/logistics-incident-triage/ (live once published)

Terms are in [GLOSSARY.md](GLOSSARY.md).

## Reproduce

No API key is needed. Python 3.11 and [uv](https://docs.astral.sh/uv/).

```
uv sync
uv run pytest -q
uv run python eval/evaluate.py --split validation --labels seeded
uv run python eval/tune.py --curve validation
uv run python eval/export_web.py
git diff --exit-code results/ web/static/data/
```

This re-computes every metric from the cached Predictions in `results/predictions/`. The last line must show no change. CI does the same on each push (`.github/workflows/ci.yml`). Use `python -m uv` if `uv` is not on your PATH.

**How the Predictions were made.** `eval/run_predictions.py --approach A|B|C --split <split>` caches one approach on one split, with raw probabilities. B needs `TYPESAFE_API_KEY` in `~/.config/logistics-incident-triage/.env`, outside the repo. Policies apply thresholds afterwards, so v1, v2 and the curve cost no extra calls. Total spend is in `results/spend.json`.

**The one test run.** Thresholds were tuned on validation and frozen. The test split is run once, with `--i-know-this-is-the-one-test-run`. The script checks that the frozen thresholds match the validation Predictions, and no approach may overwrite its test output. An interrupted B run resumes without repeating paid calls.

## Repo map

- `data/`: 100 Scenarios, 400 synthetic Incident Reports (50 / 20 / 30 Scenarios in build / validation / test).
- `src/triage/`: approaches A, B, C and the Policy logic.
- `policies/`: Policy v1 and v2 with frozen thresholds.
- `eval/`: predictions, metrics, tuning, label agreement, web export.
- `results/`: cached Predictions, metrics and reports.
- `web/`: the SvelteKit demo. It reads committed JSON.
- `docs/`: label guide, build plan, ADRs, provenance, attribution.

## Results

<!-- RESULTS: filled after the one test run -->

## Label agreement caveat

Seeded Labels came from the Scenario that a model wrote the report from. Blind Labels are one person's labels of the test reports without seeing those. The agreement between Seeded and Blind Labels, and the agreement of the user's own re-label of 25 reports at least 4 hours later, are **not** inter-rater agreement. There is one labeller. The numbers show how stable the labels are, not how well independent people would agree.

## Limitations

- All data is synthetic. No real incident was used. Scale and mix are design choices, not operational estimates.
- One model wrote every report, so voice and vocabulary vary less than in real reports (see [docs/provenance-generation.md](docs/provenance-generation.md)).
- A's rules were tuned on build errors, and it does not transfer. Category accuracy is 0.96 on build but 0.69 on validation.
- The cost-optimal Policies review heavily on validation: A 100%, B 54%, C 80%. A review costs 1 and a wrong auto-route costs 5 or more, so weak auto-routing loses. The review rate target of 25% or less is met only at other points on the curve, with a higher cost.
- Evidence is one list per report, not per decision.
- The real-report stress set (PHMSA) was cut.

## Docs

[Build plan](docs/build-plan.md) · [Label guide](docs/label-guide.md) · [ADRs](docs/adr/) · [Provenance](docs/provenance-generation.md) · [Attribution](docs/attribution.md) · [Decision trail](decisions.tsv)
