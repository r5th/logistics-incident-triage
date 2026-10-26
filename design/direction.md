# Direction: Route sign

The contract the SvelteKit build follows. Reference comps: `design/comps/d2-route-sign.html`
(Queue and Incident detail), `design/comps/d2-results.html` (Results, sketch), the token CSS in
`design/comps/shared/route-sign.css`, and the side-by-side in `design/comps/compare-01.html`.
`DESIGN.md` gets written later from the shipped build; until then this file wins over the comps
where they disagree.

HIG citations use the form *HIG › Section*, from the Apple Human Interface Guidelines digest
(`~/.claude/skills/hig`).

## Thesis

Read it like a road sign. A Destination is a white direction plate with an arrow, Review is a
yellow diversion plate, Auto-route is a green plate and Urgent is a red warning triangle with the
word. Where a report goes, and whether a human holds it first, reads at thumbnail size and in a
screen-share. Everything else is a plain, dense operations tool: a navigation rail, a table, a
two-column detail. The category default this refuses is the grey SaaS table with coloured status
pills, where every state looks like every other.

**Signature move:** the plate system. It appears in exactly three places: the Destination column,
the Routing Mode column, and the detail header's route line (Urgency, Routing Mode, arrow,
Destination). Nowhere else.

## Decisions taken on the user's behalf

The user delegated every design choice. These were answered from `docs/build-plan.md`,
`GLOSSARY.md`, ADR-0002 and `docs/research/straive-values.md`:

| Question a skill would ask | Answer | Source |
|---|---|---|
| Primary user and device | Straive assessor on a laptop (5 minutes), the author screen-sharing; phone second | build plan "Goal", "Demo" |
| Stack | SvelteKit + Svelte 5 + adapter-static, static JSON, localStorage | ADR-0002 |
| Surface mode | Operate (a working tool), not Persuade | brief |
| Light or dark | Both, following the system (`prefers-color-scheme`), no in-app toggle | build plan; *HIG › Dark Mode* "don't offer an app-specific appearance setting" |
| Build path | Code-led (Operate surfaces are code-led by rule; no image generation) | impeccable new-work |
| Direction | Route sign, over the roll-assigned Tachograph | `compare-01.html` "Why" box |
| Font | System font stack | see Type below |

## Tokens

### Colour roles

Components use roles only, never raw hex (*HIG › Color*: "use dynamic (semantic) colors by
purpose, not appearance"). Values swap under `@media (prefers-color-scheme: dark)`. Set
`color-scheme: light dark` and `<meta name="color-scheme" content="light dark">` so native
controls and scrollbars follow (*HIG › Dark Mode* [web]).

| Role | Light | Dark | Used for |
|---|---|---|---|
| `--bg` | `#F3F5F7` | `#0D141B` | page |
| `--surface` | `#FFFFFF` | `#141D26` | panels, table |
| `--surface-2` | `#E9EDF1` | `#1B2631` | section rows, tab track, hover, bar track |
| `--sep` | `#D3DAE1` | `#2A3846` | rules and borders |
| `--text` | `#111C27` | `#E7EDF3` | primary text |
| `--text-2` | `#4A5866` | `#A3B2C1` | secondary text, column headings, meta |
| `--shell` | `#0B4A8B` | `#0A3566` | navigation rail and phone app bar (motorway blue) |
| `--shell-text` / `--shell-text-2` | `#FFFFFF` / `#C8D7EA` | `#FFFFFF` / `#B7C9DF` | rail text, current / other |
| `--accent` / `--on-accent` | `#0B57A8` / `#FFFFFF` | `#7DB3F0` / `#0D141B` | primary button, links, selection, focus ring |
| `--accent-tint` | `#E2ECF8` | `#172F4B` | selected row |
| `--urgent` | `#B3261E` | `#FF8A7D` | Urgent icon and word only |
| `--auto` / `--on-auto` | `#00703C` / `#FFFFFF` | `#12804A` / `#FFFFFF` | Auto-route plate (primary-route green) |
| `--review` / `--on-review` | `#F2C200` / `#111111` | same | Review plate, awaiting badge, below-threshold bar (diversion yellow) |
| `--plate-bg` / `--plate-ink` | `#FFFFFF` / `#111C27` | `#0D141B` / `#E7EDF3` | Destination plate (inverts in dark) |
| `--evidence` / `--evidence-line` | `#DCE8F7` / `#0B57A8` | `#1C3553` / `#7DB3F0` | Evidence highlight fill and underline |

Chart series (Results only; validated with the dataviz validator, all checks pass in both modes):
A `#7C4DBA` / `#9271D4`, B `#D06A0A` / `#CF7630`, C `#14866D` / `#22A07E`. Target status uses
`--auto` green (met) and `--urgent` red (missed), always with an icon and a word.

### Contrast (WCAG 2.x, computed)

Text pairs, both themes, all ≥ 4.5:1 (*HIG › Accessibility*: "never below 4.5:1"; *HIG › Dark
Mode*: "strive for 7:1, especially small text"):

| Pair | Light | Dark |
|---|---|---|
| text on surface / bg | 17.22 / 15.76 | 14.44 / 15.72 |
| text-2 on surface / surface-2 / bg | 7.29 / 6.20 / 6.67 | 7.86 / 7.09 / – |
| text-2 on accent-tint (selected row) | 6.11 | 6.28 |
| shell-text / shell-text-2 on shell | 8.87 / 6.07 | 12.25 / 7.25 |
| accent on surface; on-accent on accent | 7.14; 7.14 | 7.77; 8.45 |
| urgent on surface / on accent-tint | 6.54 / 5.47 | 7.45 / 5.95 |
| on-auto on auto | 6.21 | 4.99 |
| on-review on review | 11.23 | 11.23 |
| plate-ink on plate-bg | 17.22 | 15.72 |
| text on evidence | 13.88 | 10.58 |

Non-text: the Auto-route plate is 6.21 (light) and 3.41 (dark) against the surface. The Review
plate's yellow is only 1.68 against white, so the plate never relies on its edge: its 11:1 label
and diamond icon carry it (WCAG 1.4.11 is met by the label). The below-threshold probability bar
is yellow for the same reason, and its meaning is repeated in text ("threshold 0.85 (below)").
Add a `@media (prefers-contrast: more)` layer that gives the Review plate and the low bar a 1px
`--text` outline (*HIG › Color*: an increased-contrast variant per colour).

### Type

**Family:** the system stack, `system-ui, -apple-system, "Segoe UI", Roboto, "Helvetica Neue",
Arial, sans-serif`. Why: no download and no layout shift on GitHub Pages, native hinting on every
platform the assessor might use (SF on a Mac, Segoe UI on Windows), true tabular figures for ids,
times and probabilities, and *HIG › Typography* prefers the system font and few typefaces. One
family carries everything (impeccable operate: "one family is often right"). Figures in ids,
times, counts and probabilities use `font-variant-numeric: tabular-nums`. No monospace anywhere.

Scale in rem, root 16px, ratio about 1.2 (*HIG › Typography*; [web] "size it in rem, so browser
font-size settings play the role of Dynamic Type"):

| Token | rem / px | Weight | Line height | Use |
|---|---|---|---|---|
| `--t-caption` | 0.75 / 12 | 500–650 | 1.4 | column headings, meta, legends, badges |
| `--t-row` | 0.8125 / 13 | 400–650 | 1.4 | table rows and plates on desktop (dense data) |
| `--t-small` | 0.875 / 14 | 400–600 | 1.5 | nav, buttons, triggers, phone list text |
| `--t-body` | 1 / 16 | 400 | 1.65 for report text, 1.5 otherwise | body, Incident Report text |
| `--t-title-3` | 1.125 / 18 | 650 | 1.3 | large plates in the detail header |
| `--t-title` | 1.5 / 24 | 650 | 1.25 | page title (`h1`); phone app bar uses 1.0625 / 17 |

Minimums: nothing below 12px (desktop) and 11px only for phone tab-bar labels (*HIG ›
Accessibility*: iOS minimum 11 pt, macOS 10 pt). Avoid light weights (*HIG › Typography*). Report
text is capped at 68ch (*HIG › Layout* [web] readable measure). Page must work at 200% zoom:
rem sizes, `min-height` not `height` on rows (*HIG › Accessibility*, WCAG 1.4.4).

### Spacing, radii, elevation

- Spacing (4px base): `--s1` 4, `--s2` 8, `--s3` 12, `--s4` 16, `--s5` 24, `--s6` 32, `--s7` 48.
  More space above a heading than below it.
- Radii: plates 4px (6px large), controls 6px, panels 8px, badges pill.
- Elevation: borders, not shadows. Only the selected tab uses a 1px soft shadow. In dark, higher
  layers are lighter surfaces (*HIG › Dark Mode* [web]).
- Motion: 150–200ms ease-out on hover, selection and the override form opening; nothing on page
  load; under `prefers-reduced-motion` use opacity only (*HIG › Accessibility*, Motion).

## Components and states

Every interactive component has default, hover, focus-visible, active, disabled, and where it
applies loading and error. Focus is a 2px `--accent` outline at 2px offset, visible in both
themes (*HIG › Accessibility*: keyboard operable with visible focus).

| Component | Anatomy | States and rules |
|---|---|---|
| **Destination plate** | Destination name + right arrow icon, 1.5px inset `--plate-ink` border, `--plate-bg` fill | Static. Large variant (18px, 3px border) only in the detail header. Never coloured per Destination. |
| **Routing Mode plate** | Auto-route: `--auto` fill, auto icon. Review: `--review` fill, diamond icon | Static. Always icon + word. |
| **Urgency mark** | Urgent: triangle icon + "Urgent" in `--urgent`, 600. Routine: clock icon + "Routine" in `--text-2`, 500 | Never colour alone (*HIG › Accessibility*: "convey information with more than color alone"). |
| **Reviewer Action status** | icon + word: Awaiting review (clock, bold), Accepted (check), Overridden (pencil), Escalated (double chevron); "—" for auto-routed | Text, no pill. |
| **Navigation rail** (≥ 1024px) | brand, Queue (awaiting count badge in `--review`), Results, Labeller, About; Approach A/B/C and Policy v1/v2 segmented controls at the foot with a one-line explanation; "Synthetic reports" footer | Current page: `aria-current="page"`, lighter fill, 600. Segments: `aria-pressed`. |
| **Tab bar** (< 600px) | Queue, Results, Labeller, About, icon above label | Always visible, 52px items (*HIG › Tab bars*: navigation not actions, keep visible, labels). |
| **Filter tabs** | Awaiting review, All, Reviewed, Auto-routed, each with a count | `role="tablist"`; selected = surface fill. Horizontal scroll on phone, 36px tall. |
| **Selects and search** | Urgency, Destination, search report text; `/` focuses search | Native `<select>` styled minimally; search is a real `<input type="search">` with `<label>`. |
| **Queue table** | Urgency, Report (id + first line, truncated at 44ch), Category, Destination, Routing Mode, Reviewer Action, Received (sortable) | Section rows: "Awaiting review · urgent first", then "Everything else · newest first". Row 44px min, 13px text. Hover `--surface-2`; selected `--accent-tint` + 1px `--accent` outline; whole row is a link to the detail, Enter opens. Empty filter: one line saying what is filtered plus "Show all reports". |
| **Phone list row** | Urgency + id + time; two-line excerpt; plates | Whole row is one 44px+ target. |
| **Detail header** | back link "Queue", id, meta (role · channel · received · synthetic), route line (Urgency, Routing Mode plate, arrow, Destination plate) | Actions sit at the header's right on desktop. |
| **Incident Report panel** | report text, sentence numbers as superscripts, Evidence sentences highlighted with letters C / U / D for the decision they support; legend | Hovering or focusing a decision row highlights only its Evidence sentences. Highlight = fill + 2px underline, so it survives without colour. |
| **Triage decisions panel** | per decision: label, top value (Destination as a small plate, Urgent as the mark), probability to 2 decimals, bar with a threshold tick, "Next: runner-up p · threshold t · Evidence n" | Below threshold: bar in `--review`, "(below)" in text. Borrowed from Interchange: the bar may stack the runner-up segment at 45% opacity. |
| **Review Triggers panel** | diamond icon, trigger name (bold), one-line detail citing sentences, rule code chip (I3, P2, v1 …) | Shown only for reports sent to Review. A report auto-routed shows "No Review Triggers. Auto-routed by Policy v1." |
| **Reviewer Action buttons** | "Accept and route" (primary), "Override", "Escalate" | One primary per view (*HIG › Buttons*). Override opens an inline form under the header (new Category / Urgency / Destination selects + required note); Escalate opens a required note. Disabled once an action is logged; the header then shows the logged action with an "Undo" button that stays until the reviewer leaves the report (no timed toast, *HIG › Accessibility*: minimize time-boxed UI). |
| **Decision history** | time (tabular), actor (System, Approach C, Policy v1, Reviewer), event | Pending row in italics: "Awaiting a Reviewer Action". Overrides show "Customer Desk → Fleet Support" and the note. |
| **Results: approach columns** | A, B, C side by side; rows for urgent recall, Missed Urgent, review rate, Destination accuracy, p95 latency, cost per 1,000; target beside each label | Met / Missed with icon + word. Headline sentence above (*HIG › Charting data*: add descriptive text). |
| **Results: operating-point chart** | review rate (x) vs Missed Urgent (y), one line per approach, direct labels, v1 circle and v2 square on the chosen approach, dashed 25% target line | Hover tooltip per point; a table view toggle; `aria-label` summarising the chart (*HIG › Charting data*: make every chart accessible). One y-axis. |
| **Results: Missed Urgent table** | report id (link), missed by, routed as, why | Every case listed; "None" is stated if empty. |

## Layout per breakpoint

| Width | Shell | Queue | Incident detail |
|---|---|---|---|
| ≥ 1024px | 232px rail + fluid main, 24/32px padding | Toolbar row, full table | Header with actions right; grid `1fr 440px`: left Incident Report then Decision history, right Triage decisions then Review Triggers |
| 600–1023px | rail collapses to a top app bar with a menu button | Table drops Category, Received moves under Report | Single column, same order as phone, actions in the header |
| < 600px | `--shell` app bar (title, Approach · Policy chip) + bottom tab bar | List rows; filter tabs scroll | Order: route line, Incident Report, Triage decisions, Review Triggers, Decision history; action bar pinned above the tab bar (Accept, Override, Escalate, 44px) |

Breakpoints follow *HIG › Layout* [web] (compact < 600, medium 600–1024, expanded > 1024);
functionality is identical at every width, only density changes. Touch targets on phone are at
least 44×44 px (*HIG › Accessibility*, Mobility); desktop toolbar controls are 30–40px, allowed
for pointer UIs (*HIG* quick reference, macOS row). Respect `env(safe-area-inset-bottom)` under
the tab bar.

## Copy rules

- **Glossary or nothing.** Use `GLOSSARY.md` terms exactly: Incident Report, Category, Urgency,
  urgent / routine, Destination and its six team names, Evidence, Routing Mode, Auto-route,
  Review, Review Trigger, Reviewer Action, accept / override / escalate, Missed Urgent, Policy,
  Operating Point. Never: ticket, case, priority, severity, flag, abstain, approve, queue (for a
  team), owner, human-in-the-loop (*HIG › Writing*: "keep a list of common terms and reuse
  them").
- **Sentence case** for every heading, label, button and column heading. Glossary terms keep their
  capitals because they are defined names ("Routing Mode", "Review Triggers").
- **Buttons start with a verb** and name the outcome: "Accept and route", "Override", "Escalate",
  "Show all reports" (*HIG › Writing*: action-oriented; *HIG › Buttons*).
- **Errors say the fix**, next to the field: "Add a note so the override can be audited", not
  "Note required" (*HIG › Writing*: say how to fix; no "oops"; avoid "we").
- **Numbers:** probabilities and thresholds to 2 decimals (0.71, threshold 0.85); rates as whole
  percentages; latency in ms; money as "US$0.34". Times 24-hour.
- **Honesty labels:** "Synthetic reports" visible in the shell; Results shows the real numbers from
  `results/*.json` and says so; a missed target is written "Missed", never softened.
- **Concise:** labels of one to three words; meta lines joined with " · ".

## What not to do

- Do not colour Destinations differently from each other; the plate is white for all six.
- Do not use red, yellow or green for anything except Urgent, Review and Auto-route / target met.
  The accent blue is for actions and selection only, never a status.
- Do not show Urgency, Routing Mode or a target result by colour alone.
- Do not put plates anywhere else (no plate-styled buttons, headings or nav).
- No cards inside cards, no eyebrow labels above headings, no gradients, glass or glow, no
  coloured side stripes on rows or panels (selection is tint + 1px outline), no hard
  offset shadows, no monospace "technical" styling, no emoji as icons.
- No modal for Override or Escalate; open inline (*impeccable operate*: modal is rarely right).
- No timed toasts for logged actions; the decision history is the confirmation.
- No in-app light/dark switch.
- No probability without its threshold and Evidence beside it.
- Do not call the API or show a "triage a new report" box in the core demo (ADR-0002).
