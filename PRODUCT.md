# Product

<!-- impeccable:product-schema 1 -->

> Written by `/impeccable init` without a live interview: the user delegated every design
> choice, and this session had no question tool. Facts come from `docs/build-plan.md`,
> `GLOSSARY.md`, `docs/adr/` and `docs/research/straive-values.md`. Lines marked
> *(inferred)* are this agent's reading of those docs, not something the user said.

## Platform

web

## Stack

SvelteKit + Svelte 5 + adapter-static on GitHub Pages, base path `/logistics-incident-triage`
(ADR-0002). Reads committed JSON; Reviewer Actions persist in `localStorage`. No server, no API
key, no live model calls in the core demo. npm, not pnpm.

## Users

- **Primary: a Straive assessor** with about five minutes, opening the public link on a laptop
  (and possibly a phone) to judge whether the author can ship a governed AI workflow. They know
  AI and operations, not this operator's rules. *(inferred: desktop first, phone second)*
- **The author, live:** walks the assessor through the demo in a screen-share, so every key
  state must be one or two clicks from the Queue and stable on reload.
- **The fictional user the screens are for:** a reviewer at a UK road-freight operator's
  triage desk, working through Incident Reports in Review and accepting, overriding or
  escalating them.

## Product Purpose

Triage Incident Reports for one road-freight operator: decide Category, Urgency and Destination
for each, and whether to Auto-route or hold for Review. Triage decides where attention goes
first; it does not decide the outcome. Success for the demo (build plan, "Goal"): the assessor
watches an urgent report auto-route, a doubtful one go to Review and an override get logged,
then trusts the numbers because they can re-run them.

Targets the Results screen reports against: urgent recall ≥ 0.98 on test, review rate ≤ 25%,
p95 latency < 1 s, API cost < US$1 per 1,000 reports. The floor is honest reporting: a missed
target is shown as missed.

## Positioning

Every routing decision carries its Evidence (verbatim sentences from the report) and its named
Review Triggers, and the operating point is a versioned Policy with stated error costs. The demo
compares a transparent rules baseline (A), TypeSafe (B) and a cascade (C) on identical inputs,
so the AI is shown earning its place against a strong baseline rather than asserted.

## Operating Context

- Screens: Queue, Incident detail, Results, Blind labelling ("Labeller" link), About.
- Data: 400 synthetic Incident Reports from 100 Scenarios (UK-style roads, depots and
  customers); predictions frozen with raw probabilities; Policies v1 and v2 differ only in the
  Missed Urgent cost (20 vs 100 reviewer-minutes).
- The walkthrough follows Straive's "Show vs Tell": normal routing, a Review, an override, the
  Policy change, then the numbers.

## Capabilities and Constraints

- Vocabulary is fixed by `GLOSSARY.md` and every UI string uses it: Incident Report, Category,
  Urgency (urgent / routine), Destination (Fleet Support, Customer Desk, Claims, Security &
  Investigations, Compliance, Safety Desk), Evidence, Routing Mode (Auto-route / Review), Review
  Trigger, Reviewer Action (accept / override / escalate), Missed Urgent, Policy, Operating
  Point. Avoided words (ticket, priority, severity, queue-as-team, flag, abstain, approve) never
  appear.
- Routing Mode is never a Destination.
- Light and dark themes are both required.
- Static only: anything "live" (triaging a new report) is a stretch goal behind a serverless
  function.

## Evidence on Hand

- `data/scenarios.jsonl` (100 Scenarios with facts and label reasons), `docs/label-guide.md`
  (rule codes U1–U6, X1–X6 that a Review Trigger or label reason can cite).
- Results JSON does not exist yet. Comps use clearly synthetic placeholder metrics; the build
  must show the real numbers from `results/*.json`, never the comp's.
- All report text is synthetic and must be labelled as such somewhere visible (About, footer).

## Product Principles

1. **Evidence on every handoff.** No decision appears without the sentences that support it.
2. **Attention, not verdicts.** The UI says where a report goes and why, and leaves the outcome
   to the receiving team.
3. **Show, then tell.** The working Queue and detail come before any chart or claim.
4. **Honest numbers.** Missed targets, Missed Urgent cases and costs are shown as plainly as
   the wins.
5. **Glossary or nothing.** One word per concept, the glossary's.

## Accessibility & Inclusion

WCAG 2.2 AA: contrast ≥ 4.5:1 in both themes, Urgency never shown by colour alone, visible
keyboard focus, 44 px touch targets on phone. *(inferred from the delegating brief)*
