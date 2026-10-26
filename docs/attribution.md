# Attribution

Who did what. The user owns every decision; the rows in `decisions.tsv` are the trail.

| Who | What | Evidence |
|---|---|---|
| Claude Opus 5.5 | Planning and orchestration. Label guide and the 100 Scenarios. Engine (rules A, TypeSafe B, cascade C, Policy). Reviews of every sub-agent and Codex diff. Tests, CI, docs. | `ada53b8`, `35bca64`, `docs/build-plan.md` |
| Claude Sonnet 5.5 | Sub-agent work. Tuned A's rules (a-v2) against build-split errors only; validation and test text were not used. Research agent for the PHMSA stress set (cut: site returned 403). | `08f6c44`; rows `tune-A`, `data` in `decisions.tsv` |
| GPT-6.1 Sol via Codex | J1: wrote the passages behind all 400 synthetic Incident Reports. J2: eval harness, tuning and agreement scripts, built to a Claude-written spec. Pre-test review of `eval/` and `src/triage/policy.py`; found 3 blockers and 1 should-fix, all fixed. | `b1bc5bd`, `f96f18e`, `a6be246`, `a288cca`; `docs/provenance-generation.md` |
| TypeSafe Jev `jev-1.14.0` | Approach B: typed questions with sentence Evidence. Called through the SDK; spend is in `results/spend.json`. | ADR-0001, `src/triage/typesafe_ai.py` |
| The user | Decision owner. Blind Labels for the 120 test reports, a re-label of 25 of them at least 4 hours later, and adjudication of disagreements (once, both labels visible). | `data/labels/` once published |

Claude wrote the Seeded Labels, so they are not independent of the label guide. The Blind Labels are the user's.
