# Build plan (agreed 2026-10-27, deadline 2026-10-27 23:59 SGT)

Source of truth for every agent working on this repo. Vocabulary: `GLOSSARY.md`. Decisions:
`docs/adr/`. Trail: `decisions.tsv` (committed). If this plan and a later row in
`decisions.tsv` disagree, the later row wins.

## Goal

An assessor opens the demo, watches an urgent report auto-route, a doubtful one go to Review and
an override get logged, then trusts the numbers because they can re-run them.
Targets (floor is honest reporting): urgent recall ≥ 0.98 on test, review rate ≤ 25%, p95
latency < 1 s, API cost < US$1 per 1,000 reports.

## Fixed decisions

- One road-freight operator (UK-style roads and depots), three decisions per report: Category,
  Urgency, Destination. Routing Mode (Auto-route vs Review) is separate from Destination.
- Categories: `vehicle_breakdown`, `delivery_delay`, `shipment_damage`, `missing_shipment`,
  `documentation_issue`, `safety_incident`.
- Urgency: `urgent` | `routine`. Urgent if any: someone hurt or at risk; hazmat or spill; vehicle
  stopped in a live lane; temperature-controlled cargo at risk within hours; time-critical
  consignment (medical, or contract-deadline flagged) that will miss its window; theft in progress
  or breached seal. Else routine.
- Primary Category: safety incident always wins; otherwise the cause the receiving team acts on
  (breakdown causing delay → vehicle_breakdown; damage found at delivery → shipment_damage).
- Destinations: `fleet_support`, `customer_desk`, `claims`, `security_investigations`,
  `compliance`, `safety_desk`. Default per Category (breakdown→fleet_support,
  delay→customer_desk, damage→claims, missing→security_investigations,
  documentation→compliance, safety→safety_desk) with documented exceptions in the label guide
  (about 20% of scenarios), so Destination is a real third decision.
- Three approaches on identical inputs (report text only): **A** transparent rules baseline
  (reasonably tuned, not weak); **B** TypeSafe only (ADR-0001); **C** cascade: A when A is
  confident, else B.
- Policies v1 and v2 (`policies/v1.json`, `policies/v2.json`), cost unit = reviewer-minute
  equivalent: Missed Urgent 20 (v2: 100); wrong Destination auto-routed 5; routine auto-routed
  as urgent 2; right Destination wrong Category 1; sent to Review 1. Thresholds per Policy chosen
  on validation to minimise that Policy's total cost, then frozen. Test is scored once per Policy.
- Predictions are cached with raw probabilities; Policies apply thresholds after the fact, so
  v1/v2 and the operating-point curve need no extra API calls.
- Agreement (labelling alone): κ Seeded Label vs Blind Label on all 120 test reports; κ of the
  user's re-label of 25 reports ≥ 4 h later. Neither is inter-rater; README says so. On test the
  Blind Label is final; disagreements adjudicated once by the user with both visible, all logged.
- Demo: SvelteKit + Svelte 5 + adapter-static on GitHub Pages, base `/logistics-incident-triage`,
  reads committed JSON, Reviewer Actions in localStorage (ADR-0002). Screens: Queue, Incident
  detail, Results, Blind labelling ("Labeller" link), About. Light + dark. Design lane:
  /impeccable init → shape → build → audit → polish, /hig for type, contrast, copy.
- TypeSafe key: `~/.config/logistics-incident-triage/.env` (`TYPESAFE_API_KEY`), never in the
  repo. Hard cap US$5. CI never calls the API.
- Git: work on a branch, merge to `main` at checkpoints, push to the **private** remote.
  Public only on the user's word.
- Cut order if late: live triage box → PHMSA stress set → interactive curve (static chart) →
  cascade C. Never cut: A, B, Blind Labels, v1/v2 on test, Queue + detail, business summary,
  provenance + attribution, reproduction check.
- Context: main Claude thread stays under 150k tokens; hand off to a fresh thread from this file
  and `decisions.tsv` when near it.

## Tooling

Python 3.11 via `python -m uv` (uv is not on PATH): `python -m uv sync`, `python -m uv run pytest`.
Web: npm (pnpm is not installed). TypeSafe SDK `typesafe-sdk` 0.7.5, model `jev-1.14.0`,
`TypeSafeClient().system_one(state=text, questions={...})`; measured ~240 ms per call.

## Data contract

100 Scenarios × 4 Incident Reports = 400. Split by Scenario: 50 build / 20 validation / 30 test
Scenarios → 200 / 80 / 120 reports. Bootstrap CIs resample Scenarios, not reports.

`data/scenarios.jsonl`, one object per line:
`scenario_id` (`S-001`…), `split` (`build|validation|test`), `category`, `urgency`,
`destination`, `destination_is_exception` (bool), `tags` (subset of `multi_issue`, `incomplete`,
`contradictory`, `hazmat`, `temperature_controlled`, `time_critical`, `night`, `third_party`),
`facts` (short bullet list of what happened: vehicle, place, cargo, time, people), `label_reason`
(one line citing the label-guide rule that decides Urgency and Destination).

`data/reports.jsonl`: `report_id` (`R-0001`…, shuffled so ids do not reveal Scenario),
`scenario_id`, `author_role` (`driver|depot|customer|subcontractor`), `channel`
(`app|email|phone_transcript`), `text`, `generator` (model id), `synthetic: true`.
All four paraphrases of a Scenario keep every label-deciding fact (an `incomplete` Scenario is
incomplete in all four) and vary voice, length, order, spelling and noise.

Mix (design choice, not an operational estimate): Categories roughly balanced (14–20 Scenarios
each); ~30% urgent overall and in every split; `multi_issue` ~20%, `incomplete` ~15%,
`contradictory` ~5%; every split has urgent examples of every Category where plausible.

## Code layout

```
src/triage/schema.py      Report, Prediction (per-decision probabilities, evidence, triggers)
src/triage/baseline.py    approach A
src/triage/typesafe_ai.py approach B (Choice/Noul questions, sentence Evidence)
src/triage/cascade.py     approach C
src/triage/policy.py      Policy load, Routing Mode, cost
eval/run_predictions.py   cache predictions → results/predictions/<approach>_<split>.jsonl
eval/evaluate.py          metrics, curve, v1/v2 → results/*.json, results/report.md
eval/export_web.py        → web/static/data/*.json
tests/
web/                      SvelteKit demo
docs/label-guide.md, docs/provenance.md, docs/business-summary.md, docs/attribution.md
```

## Phases (SGT)

| By | Phase | Owner |
|---|---|---|
| 01:30 | P1 label guide + 100 Scenarios; J1 dispatched | Claude (Opus sub-agent) |
| 04:00 | P2 reports merged; A; B on build + validation; J2 dispatched | Claude + Codex |
| 10:00 | P3 Blind labelling tool live; thresholds frozen on validation | Claude |
| 10–16 | Blind-label 120 test reports; re-label 25 ≥ 4 h later | user |
| 18:00 | P4 one test run, results, demo deployed | Claude |
| ~20:00 | think-aloud on demo (author's own trial) | user |
| 21:30 | P5 business summary, README, walkthrough script | Claude |
| ~22:00 | go public, 15-min rehearsal | user |

Codex jobs (`~/.claude/routing/codex-offload.md`): **J1** paraphrases from Scenarios + label
guide; **J2** eval harness + tests to a Claude-written spec. Claude reviews both diffs.

## Status at handoff 1 (2026-10-27 ~02:00 SGT)

Done: label guide + 100 Scenarios (`ada53b8`), 400 reports from Codex J1 (`b1bc5bd`, variety
limitation in `docs/provenance-generation.md`), engine A/B/C + Policy (`35bca64`), eval harness
from Codex J2 (`f96f18e`), design direction Route sign (`design/direction.md`), SvelteKit demo on
sample data (`1e4f07c`). Predictions cached for A/B/C on build + validation; TypeSafe spend so
far US$0.028 (`results/spend.json`). Build-split, untuned thresholds: B urgent recall 0.93 with 0
Missed Urgent at 27% review; A 0.82 recall, 10 Missed Urgent (`results/report_build_seeded.md`).

Next, in order:
1. Optional, ≤45 min: tune A's rules against **build-split** errors only (never validation or
   test text), re-run A and C on build + validation (no API cost). Log it.
2. `eval/tune.py --policy v1` and `--policy v2` on validation; sanity-check; `--freeze`;
   `eval/tune.py --curve validation`.
3. Sol review (`~/.claude/routing/sol.md`) of `eval/` + `src/triage/policy.py` before any test
   run: leakage, metric definitions, cost and Missed Urgent logic.
4. `eval/export_web.py` with real data; `labelling.json` = 120 test reports, no labels. Serve
   `web` dev server so the user can blind-label at http://localhost:5173/label by **10:00 SGT**
   (if they are remote, use the `tailscale-remote-preview` skill). Tell the user.
5. User downloads labels → `data/labels/blind_test.json` (pass 1; pass 2 ≥4 h later). Then the one
   test run: `run_predictions.py --split test --i-know-this-is-the-one-test-run` for A, B, C;
   `evaluate.py --split test --labels final` and `--labels seeded`; `agreement.py`; user
   adjudicates disagreements → `data/labels/adjudicated_test.json`; `tune.py --curve test`.
6. Export real data to web; `/impeccable audit` + `polish` (bounded); `/impeccable document` →
   `DESIGN.md`; CI workflow that re-runs evaluate from cached predictions and fails on
   `git diff --exit-code results/`; README (run steps, live link), `docs/business-summary.md`
   (one page), `docs/attribution.md` (Claude Opus 5.5 / Sonnet 5.5, GPT-6.1 Sol via Codex J1/J2,
   TypeSafe Jev; user = labeller and decision owner), walkthrough script.
7. GitHub Pages needs the repo public (or a paid plan): ask the user before 22:00.
8. ~20:00 user think-aloud on the demo; log findings; fix ≤2. ~22:00 go public on the user's
   word; rehearsal.
9. Before handing back: decision-log audit + independent review + Attention section.
