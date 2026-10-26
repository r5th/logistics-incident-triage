---
name: Logistics Incident Triage
description: A road-sign operations tool. Where an Incident Report goes, and whether a human holds it first, reads at thumbnail size.
colors:
  bg: "#f3f5f7"
  surface: "#ffffff"
  surface-2: "#e9edf1"
  sep: "#d3dae1"
  ctl-border: "#7a8796"
  text: "#111c27"
  text-2: "#4a5866"
  shell-motorway-blue: "#0b4a8b"
  accent: "#0b57a8"
  accent-tint: "#e2ecf8"
  urgent: "#b3261e"
  auto-green: "#00703c"
  review-yellow: "#f2c200"
  review-edge: "#111111"
  evidence: "#dce8f7"
  series-a: "#7c4dba"
  series-b: "#d06a0a"
  series-c: "#14866d"
typography:
  title:
    fontFamily: "system-ui, -apple-system, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif"
    fontSize: "1.5rem"
    fontWeight: 650
    lineHeight: 1.25
    letterSpacing: "-0.01em"
  title-3:
    fontFamily: "system-ui, -apple-system, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif"
    fontSize: "1.125rem"
    fontWeight: 650
    lineHeight: 1.3
  body:
    fontFamily: "system-ui, -apple-system, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif"
    fontSize: "1rem"
    fontWeight: 400
    lineHeight: 1.5
  small:
    fontFamily: "system-ui, -apple-system, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif"
    fontSize: "0.875rem"
    fontWeight: 600
    lineHeight: 1.5
  row:
    fontFamily: "system-ui, -apple-system, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif"
    fontSize: "0.8125rem"
    fontWeight: 400
    lineHeight: 1.4
  caption:
    fontFamily: "system-ui, -apple-system, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif"
    fontSize: "0.75rem"
    fontWeight: 600
    lineHeight: 1.4
rounded:
  plate: "4px"
  plate-lg: "6px"
  ctl: "6px"
  panel: "8px"
  pill: "999px"
spacing:
  s1: "4px"
  s2: "8px"
  s3: "12px"
  s4: "16px"
  s5: "24px"
  s6: "32px"
  s7: "48px"
components:
  plate-destination:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.text}"
    typography: "{typography.row}"
    rounded: "{rounded.plate}"
    padding: "5px 8px"
  plate-auto:
    backgroundColor: "{colors.auto-green}"
    textColor: "{colors.surface}"
    rounded: "{rounded.plate}"
    padding: "5px 8px"
  plate-review:
    backgroundColor: "{colors.review-yellow}"
    textColor: "{colors.review-edge}"
    rounded: "{rounded.plate}"
    padding: "5px 8px"
  button-primary:
    backgroundColor: "{colors.accent}"
    textColor: "{colors.surface}"
    typography: "{typography.small}"
    rounded: "{rounded.ctl}"
    height: "40px"
    padding: "0 16px"
  button-default:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.text}"
    typography: "{typography.small}"
    rounded: "{rounded.ctl}"
    height: "40px"
    padding: "0 16px"
  panel:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.text}"
    rounded: "{rounded.panel}"
    padding: "16px 24px"
  trigger-chip:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.text}"
    typography: "{typography.caption}"
    rounded: "4px"
    padding: "1px 6px"
  evidence-highlight:
    backgroundColor: "{colors.evidence}"
    textColor: "{colors.text}"
    rounded: "2px"
---

# Design System: Logistics Incident Triage

Recorded from the shipped SvelteKit build (`web/src/app.css`, the components under `web/src/lib/components`, the routes). Where this file and `design/direction.md` differ, this file describes what was built; deviations are listed at the end.

## Overview

**Creative North Star: "The Route Sign"**

Read it like a road sign. A Destination is a white direction plate with an arrow, Review is a yellow diversion plate, Auto-route is a green plate, and Urgent is a red warning triangle with the word. Where a report goes, and whether a human holds it first, reads at thumbnail size and in a screen-share. Everything else is a plain, dense operations tool: a motorway-blue navigation rail, a table, a two-column detail.

The system is flat, bordered and quiet so the plates can carry the signal. One system font, one accent blue reserved for actions and selection, and three status colours reserved for Urgent, Review and Auto-route / target met. Light and dark both ship and follow the system setting; there is no in-app switch.

**Key Characteristics:**
- Plates appear in exactly three places: the Destination column, the Routing Mode column, and the detail header's route line.
- Depth comes from 1px borders and tonal surfaces, not shadows.
- Status is always icon plus word, never colour alone.
- Dense desktop rows (13px), 44px touch targets on phone.

## Colors

A cool blue-grey neutral field, one motorway-blue shell and accent, and three sign colours used only for status. Components consume roles (CSS custom properties in `app.css`), never raw hex. Hex below is the light value; dark values are given beside it.

### Primary
- **Motorway Blue Shell** (#0b4a8b; dark #0a3566): navigation rail and phone app bar. Text on it is white (`--shell-text`) and pale blue (`--shell-text-2`, #c8d7ea / dark #b7c9df).
- **Signal Blue Accent** (#0b57a8; dark #7db3f0): primary button, links, selection, focus ring, caret. On-accent is white (dark: #0d141b).
- **Accent Tint** (#e2ecf8; dark #172f4b): selected row, together with a 1px accent outline.

### Secondary (status)
- **Warning Red** (#b3261e; dark #ff8a7d): Urgent icon and word, and field errors.
- **Primary-Route Green** (#00703c; dark plate #12804a, dark text #4fc98a): Auto-route plate and "Met" targets (`--met-text` is the lightened text variant in dark).
- **Diversion Yellow** (#f2c200, both modes): Review plate, awaiting-count badge, below-threshold probability bar. Label ink #111111. Yellow is only 1.68:1 on white, so every yellow element carries a #111111 edge (see Review plate).

### Neutral
- **Page Grey** (#f3f5f7; dark #0d141b): page background.
- **Surface White** (#ffffff; dark #141d26): panels, table, Destination plate (dark plate is #0d141b), inputs.
- **Surface 2** (#e9edf1; dark #1b2631): hover, bar track, skeleton, segmented tracks.
- **Hairline** (#d3dae1; dark #2a3846): borders and table rules.
- **Control Edge** (#7a8796; dark #5f7184): form control and key-cap borders, 3.7:1 on surface (WCAG 1.4.11).
- **Ink** (#111c27; dark #e7edf3): primary text.
- **Ink 2** (#4a5866; dark #a3b2c1): secondary text, column heads, meta.
- **Evidence Blue** (#dce8f7; dark #1c3553), line #0b57a8 (dark #7db3f0): Evidence highlight.

### Contrast
Contrast figures below are the computed values recorded in `design/direction.md`; the build's token values match that contract, and the row marked "built" is stated in `app.css` comments.

| Pair | Light | Dark |
|---|---|---|
| Ink on surface | 17.22 | 14.44 |
| Ink 2 on surface | 7.29 | 7.86 |
| Accent on surface | 7.14 | 7.77 |
| Warning Red on surface | 6.54 | 7.45 |
| On-auto on auto | 6.21 | 4.99 |
| Label on yellow | 11.23 | 11.23 |
| Shell text on shell | 8.87 | 12.25 |
| Control Edge on surface (built) | 3.7 | not recorded |
| Yellow on white (why the edge exists) | 1.68 | n/a |

### Chart series (Results only)
Approach A #7c4dba (dark #9271d4), B #d06a0a (dark #cf7630), C #14866d (dark #22a07e).

### Named Rules
**The Sign Colours Rule.** Red, yellow and green mean Urgent, Review and Auto-route / target met, and nothing else. Accent blue is for actions and selection, never status.
**The One Plate Colour Rule.** All six Destinations share the same white (dark: near-black) plate; Destinations are never coloured individually.

## Typography

**Font:** the system stack `system-ui, -apple-system, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif` for everything. No monospace, no webfont.

**Character:** native and utilitarian; hierarchy comes from weight (400/500/600/650) and size, with tabular figures for ids, times and probabilities.

### Hierarchy
- **Title** (650, 1.5rem, 1.25, -0.01em): page `h1`. The phone app bar title is 1.0625rem.
- **Title 3** (650, 1.125rem, 1.3): large plates and the large Urgency mark in the detail header.
- **Body** (400, 1rem, 1.5): report text, capped at 68ch. `h2` is 1rem/650; `h3` is 0.875rem/650.
- **Small** (500-600, 0.875rem): nav, buttons, inputs, meta lines.
- **Row** (400-650, 0.8125rem): table rows, plates, the Urgency mark, field labels.
- **Caption** (500-700, 0.75rem): column heads, legends, chips, badges. The phone tab-bar label is 0.6875rem (11px), the smallest size in use.

### Named Rules
**The Tabular Figures Rule.** Ids, times, counts and probabilities use `font-variant-numeric: tabular-nums`.
**The Rem Rule.** Sizes in rem and row heights as `min-height`, so 200% zoom works.

## Layout

Three widths. 1024px and up is a 232px rail plus fluid main (24px/32px padding). 600-1023px swaps the rail for a sticky 52px app bar with a menu panel. Below 600px a fixed bottom tab bar is added (4 items, 52px, safe-area aware) and main padding drops to 12px/16px. Spacing is a 4px scale: 4, 8, 12, 16, 24, 32, 48. Panels stack with 16px. Incident detail at desktop is a grid of `minmax(0,1fr) 440px` with a 24px gap; under 1024px it is one column. Functionality is identical at every width; only density changes. Notices are capped at 100ch.

## Elevation & Depth

Flat. Panels, tables and notices use a 1px Hairline border on Surface; in dark, higher layers are lighter surfaces. There are no drop shadows. The only `box-shadow` uses are inset strokes that draw an edge or underline: plate outlines, the Evidence underline (`inset 0 -2px 0`), and a 1px ring on the yellow below-threshold bar and tab-bar count dot.

### Named Rules
**The Border-Not-Shadow Rule.** Separation is a 1px border or a tonal step; never a blurred or offset shadow.

## Shapes

Small, squared-off geometry like a sign face. Plates 4px (large plates 6px), controls and segments 6px (inner segment 4px), panels and tables 8px, chips and key-caps 4px, count badges pill (999px), probability bars 3px, Evidence highlight 2px. Selection is a tint plus a 1px inset outline; there are no coloured side stripes. Motion is 180ms with `cubic-bezier(0.16, 1, 0.3, 1)` on hover and open; under `prefers-reduced-motion` only opacity transitions remain.

## Components

### Destination plate
White (dark #0d141b) plate, ink border drawn as `inset 0 0 0 1.5px`, 13px/650 name followed by an arrow icon. The large variant (18px, 10px 14px padding, 6px radius, 3px border) appears only in the detail header. Static.

### Routing Mode plate
Same geometry as the Destination plate. **Auto-route**: green fill, white label, auto icon. **Review (yellow plate)**: #f2c200 fill, #111111 label, diamond icon, and always a dark outline (`inset 0 0 0 1.5px`, 2px when large) in every mode, because the yellow is only 1.68:1 on white. Always icon plus word.

### Urgency mark
Urgent: triangle icon plus "Urgent" in Warning Red, 600. Routine: clock icon plus "Routine" in Ink 2, 500. Large (1.125rem) in the detail route line.

### Review Trigger chips
In the Review Triggers panel each row is a 20px icon column, a bold trigger name with a one-line detail citing sentences, and a rule-code chip (I3, P2, v1 and so on): 12px/650, 1px Hairline border, 4px radius, 1px 6px padding, no fill. Shown only for reports sent to Review.

### Evidence highlight
Report sentences that support a decision are `mark` elements: Evidence Blue fill, 2px Evidence-line underline (inset), 2px radius. Sentence numbers are 11px superscripts, accent-coloured when they are Evidence. Fill plus underline, so it survives without colour. A legend swatch explains it.

### Triage decision rows
A 96px label column and a value column; the value in 650, probability to 2 decimals, a 3px-radius bar on Surface 2 with a 2px threshold tick and a dashed band. Below threshold the bar is yellow with a 1px #111111 ring and the text says "(below)". The runner-up segment is drawn lighter.

### Buttons
40px min-height, 6px radius, 1px Control Edge border, 14px/600. Default is Surface fill with Surface 2 hover. **Primary** is Signal Blue fill (hover brightness 1.1), one per view ("Accept and route"). **Quiet** is transparent with accent text. Active nudges 1px down; disabled is 50% opacity. Icons 16px.

### Inputs and selects
40px min-height, 1px Control Edge border, 6px radius, 14px text, Ink 2 placeholder. Labels 13px/600. Errors in Warning Red with the fix in words. Focus: 2px accent outline at 2px offset (white on the shell).

### Navigation
Rail: brand mark, links at 40px (44px on medium), 14px/500, current page with a lighter fill (`aria-current="page"`) and 600 weight; awaiting count badge as a yellow pill; Approach A/B/C and Policy v1/v2 are `aria-pressed` segmented buttons on a dark translucent track, selected segment white on blue. Phone: app bar plus bottom tab bar, current tab in accent, yellow count dot with a dark ring.

### Queue table and filter tabs
Table in an 8px bordered wrap; 12px/600 Ink 2 column heads, 9px 12px cell padding, hairline row rules, section rows. Row hover Surface 2; selected tint plus 1px accent outline. Filter tabs are `aria-pressed` buttons (34px, 44px on phone) with counts. Phone shows list rows as single 44px+ targets.

### Operating-point chart
Inline SVG: review rate (x) against Missed Urgent (y), one 2px line per approach in the series colours with the chosen approach emphasised and the others dimmed, direct labels, Policy v1 as a filled circle and Policy v2 as a hollow square, a dashed 25% review-rate target line, Hairline gridlines, 12px tabular axis text, and an Ink tooltip on hover. It has an `aria-labelledby` text summary and a "Show as table" toggle carrying the same numbers. Targets read "Met" or "Missed" with icon and word.

### Notices and empty states
Bordered Surface notice with a 16px accent icon and 13px text. Empty states are centred Ink 2 text with a fix link. Loading uses Surface 2 skeleton bars, not spinners.

## Voice and copy

Glossary or nothing: use `GLOSSARY.md` terms exactly (Incident Report, Category, Urgency, Destination, Evidence, Routing Mode, Auto-route, Review, Review Trigger, Reviewer Action, Missed Urgent, Policy, Operating Point). Sentence case everywhere except defined names. Buttons start with a verb and name the outcome ("Accept and route", "Show all reports"). Errors say the fix. Probabilities and thresholds to 2 decimals, rates as whole percentages, latency in ms, money as "US$0.34", 24-hour times. "Synthetic reports" stays visible in the shell. A missed target is written "Missed". Meta lines are joined with " · ".

## Accessibility floor

WCAG 2.2 AA. Text contrast at least 4.5:1 in both themes; non-text edges at least 3:1 (hence Control Edge and the yellow's dark edge). Urgency, Routing Mode and target results never rely on colour alone. 2px accent focus ring on everything focusable, a skip link, `aria-current` and `aria-pressed` states, 44px phone targets, `prefers-reduced-motion` (opacity only), `prefers-contrast: more` (stronger separators, control edges and Ink 2 text, outlined low bar), `color-scheme: light dark`.

## Do's and Don'ts

### Do:
- **Do** use colour roles from `app.css`, never raw hex, so both themes swap.
- **Do** pair every status with an icon and a word (Urgent, Review, Auto-route, Met, Missed).
- **Do** give every yellow surface a #111111 edge, in light and dark.
- **Do** show every probability with its threshold and Evidence beside it.
- **Do** keep the 2px accent focus outline (white on the shell) and 44px phone targets.
- **Do** open Override and Escalate inline and confirm logged actions in the decision history, not in toasts.

### Don't:
- **Don't** put plates anywhere beyond the Destination column, Routing Mode column and detail route line.
- **Don't** colour Destinations differently from each other.
- **Don't** use red, yellow or green for decoration, or accent blue for status.
- **Don't** add drop shadows, decorative gradients, glass, glow, side stripes, monospace styling or emoji icons.
- **Don't** nest cards, use a modal for Override, or add an in-app light/dark switch.
- **Don't** use the words ticket, case, priority, severity, flag, abstain, approve, or "queue" for a team.

## Deviations from `design/direction.md`

- **Review plate edge**: the contract relied on the label and added an outline only under `prefers-contrast: more`. The build always draws the dark edge (and a ring on the yellow bar and count dot) in every mode, a contract amendment recorded in `app.css`.
- **Contrast layer**: `prefers-contrast: more` strengthens separators, control edges and Ink 2, and outlines the low bar; it does not touch the plate.
- **Filter tabs** are `aria-pressed` buttons, not `role="tablist"`.
- **Shell backdrop**: `.app` uses a hard-stop `linear-gradient` only to run the rail blue to the page bottom; it is not a decorative gradient.
- **Added tokens** not in the contract: `--met-text`, `--ctl-border`, `--shell-hover`, `--shell-active`, `--ease`, `--dur`.
- **Dark contrast** figures for the build were not re-measured here; they are the contract's computed values.
