Implementation job.

# J1: write the 400 Incident Reports

## Goal

Write `data/reports.jsonl`: four synthetic Incident Reports for each of the 100 Scenarios in
`data/scenarios.jsonl` (400 in all). Each report must carry every fact that decides its
Scenario's Seeded Label, so a human labeller using `docs/label-guide.md` on the report text
alone would reach the same Category, Urgency and Destination. The reports are the only input
the triage approaches see, so they must read like real messages from a UK road-freight
operation, not like a restated label.

## Base SHA

`<filled in by orchestrator>`

## In scope

Create or edit only these files:

- `data/reports.jsonl`
- `scripts/build_reports.py` (only if you need a script to assemble, shuffle or number the
  reports)
- `docs/provenance-generation.md`

Do not edit `data/scenarios.jsonl`, `docs/label-guide.md`, `scripts/check_scenarios.py` or
anything else. If a Scenario looks wrong under the label guide, still write its reports, and
list the Scenario id and the problem in your Report.

## Steps

1. Read `docs/label-guide.md` in full, then `GLOSSARY.md`, then the "Data contract" section of
   `docs/build-plan.md`. Use the glossary terms in anything you write.
2. Read every line of `data/scenarios.jsonl`. For each Scenario, `category`, `urgency`,
   `destination` and `label_reason` are the Seeded Label and the rule that decides it; `facts`
   is what happened. Two kinds of fact bullet are instructions, not content:
   - `Tone: …` sets the writer's voice for all four reports (for example a routine case written
     in alarm, or an urgent case written calmly). Keep that tone.
   - `Not stated: …` lists information that must be absent from all four reports. Do not add it,
     guess it or hint at it.
3. For each Scenario write exactly 4 reports. Each report is one JSON object with these fields,
   in this order:
   - `report_id`: assigned in step 5.
   - `scenario_id`: the Scenario's id.
   - `author_role`: `driver`, `depot`, `customer` or `subcontractor`. Use at least two different
     roles per Scenario, and only roles that could plausibly know the facts (a customer cannot
     report a tachograph limit first-hand; they can report what the driver told them). Use
     `subcontractor` mainly where the facts name a subcontractor.
   - `channel`: `app`, `email` or `phone_transcript`. Vary it across the four.
   - `text`: the report, 30–180 words.
   - `generator`: your exact model id string (the same on every line).
   - `synthetic`: `true`.
4. Writing rules for `text`:
   - **Keep every label-deciding fact** in every report: whatever `label_reason` relies on
     (for example the vehicle being in lane 1, the seal number not matching, the medical cargo
     and the slot it will miss, the stated innocent explanation for missing goods, the reefer
     state and box temperature). An `incomplete` Scenario is incomplete in all four reports; a
     `contradictory` Scenario contains its contradiction in all four.
   - **Add nothing that would change the Label**: no injuries, spills, live-lane positions,
     deadlines, theft signs or explanations that are not in the facts.
   - **Vary** voice, length, order of facts, and level of detail across the four. Some short
     app messages, some fuller emails, some phone transcripts (`Caller: … / Desk: …` lines,
     fillers, interruptions).
   - **Realistic noise**: typos, abbreviations (RDC, POD, ETA, reg, J14, NB/SB, "artic",
     "trailer's"), times in mixed formats (05:40, 5.40am, "about 6"), reg plates and trailer
     numbers from the facts, the odd missing punctuation or all-caps word. Plain UK English and
     UK spelling.
   - **Do not name the label.** Do not write the Category names, Destination names or the words
     "urgent"/"routine" as labels. A writer may naturally say "it's urgent" only when the facts'
     tone supports it, and at most once across a Scenario's four reports. Never write a rule code
     (`U3`, `X1` …).
   - Use only the fictional companies, places and plates in the facts; no real people's names.
     First names for drivers or staff are fine if invented.
5. Shuffle all 400 reports with `random.Random(20261027).shuffle(reports)` (after building them
   in Scenario order, four per Scenario), then number them `R-0001` … `R-0400` in the shuffled
   order and write them to `data/reports.jsonl` sorted by `report_id`, one JSON object per line,
   UTF-8, `\n` line endings, `ensure_ascii=False`.
6. Write `docs/provenance-generation.md` (see below).
7. Run the Check and fix anything it reports.

### `docs/provenance-generation.md`

Short, plain UK English. Record: the exact model id and that it wrote all 400 reports; the date
of generation; the procedure (inputs read, four reports per Scenario, the writing rules above in
brief, the shuffle seed 20261027 and how ids were assigned, and whether a script was used); that
every report is synthetic and that companies, places and plates are fictional; and the
limitations (one model wrote every report, so voice and vocabulary are less varied than real
messages; no real incident data was used; the Seeded Label was fixed before the text was written
and the text was not checked by a human at generation time; any Scenario you flagged as doubtful).

## Check

Run from the repo root:

```
python scripts/check_scenarios.py --reports data/reports.jsonl
```

It checks the Scenarios, then the reports: 400 lines; every Scenario has exactly 4 reports;
every line has exactly the fields `report_id, scenario_id, author_role, channel, text,
generator, synthetic` in that order; enums valid; `synthetic` is `true`; `generator` non-empty;
ids unique and `R-0001`…`R-0400`; every report 30–180 words; at least two author roles per
Scenario; ids not in Scenario order.

Passing looks like: the Scenario summary table, then a line
`Reports: 400 lines, 100 scenarios, words min/median/max …`, the author_role, channel and
generator counts (one generator value), and a final line `PASS`. Any `FAIL` line lists the
problems; fix them and run it again.

Also run this leak check and confirm in your Report that it prints nothing (or explain each hit):

```
python -c "import json,re; [print(r['report_id'], m) for r in map(json.loads, open('data/reports.jsonl', encoding='utf-8')) for m in re.findall(r'(?i)\b(?:vehicle_breakdown|delivery_delay|shipment_damage|missing_shipment|documentation_issue|safety_incident|fleet_support|customer_desk|security_investigations|safety_desk|routine|[UX][0-6])\b', r['text'])]"
```

## Done when

- `python scripts/check_scenarios.py --reports data/reports.jsonl` ends with `PASS`.
- The leak check prints nothing, or each hit is justified in the Report.
- `docs/provenance-generation.md` exists with the contents above.
- Only the in-scope files changed (`git status` shows nothing else), and the work is committed
  on your branch with a clear message.

## Report

At most 200 words: worktree path, branch, base SHA, commit SHA, files changed, the last 15 lines
of the Check output, the leak-check result, and anything not done or any Scenario you think is
mislabelled under the label guide (id and one line why).
