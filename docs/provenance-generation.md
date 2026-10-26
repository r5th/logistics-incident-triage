# Incident Report generation

On 27 October 2026, `gpt-6.1-sol` wrote all 400 synthetic Incident Reports in
`data/reports.jsonl`. No other model wrote reports.

The inputs were the complete `docs/label-guide.md`, `GLOSSARY.md`, the Data contract
in `docs/build-plan.md`, and all 100 Scenarios in `data/scenarios.jsonl`. Each
Scenario already had its Seeded Label before any report text was written.

The model wrote two alternative phrasings of three passages for each Scenario.
`scripts/build_reports.py` assembles four Incident Reports from different
combinations of those passages, with varied ordering and app, email or phone
transcript framing. Each Scenario uses at least two author roles. Accounts passed
on by another role are attributed to their source. The passages retain the facts
that decide the Label, including contradictions, uncertainty, refrigeration
readings, seal discrepancies and missed windows. Tone instructions affect the
voice; information marked “Not stated” stays absent. Text avoids Label names and
rule codes, uses UK English and the details supplied in the Scenarios, and adds no
new incident facts that would change the Label.

The script first builds four reports per Scenario in Scenario order, then calls
`random.Random(20261027).shuffle(reports)`. It assigns `R-0001` to `R-0400` after
shuffling and writes them in that order, as UTF-8 JSON Lines with LF endings and
`ensure_ascii=False`. The generator value on every line is `gpt-6.1-sol` and
`synthetic` is `true`.

Every Incident Report is synthetic; no real incident data was used. Companies,
operational places and plates are fictional within the Scenarios. The supplied
road, town and port names also include real UK geography; their use does not
describe an actual incident at those places.

One model wrote every report, so voice and vocabulary are less varied than real
reports. Passage reuse and channel framing further limit the independence of the
four paraphrases. The text was not checked by a human at generation time. The
supplied checker verifies the data contract, rather than semantic agreement with
the Label guide; its passing result is not a Blind Label.

Two Scenarios warrant human attention; their facts and Seeded Labels were left
unchanged:

- **S-070** (`data/scenarios.jsonl:70`): the forklift reverses into cereal pallets.
  The Seeded Label is shipment damage, but the guide's “collision of any size” and
  safety precedence could encompass that contact. The guide may need to distinguish
  goods-handling damage from a collision.
- **S-089** (`data/scenarios.jsonl:89`): the yard team only thinks the shunter moved
  the trailer. The exception for missing goods requires a stated innocent
  explanation; whether this unconfirmed explanation suffices needs clarification.
  Reports retain “think” or “believe” and the ongoing check, without inventing a
  confirmed location.

Validation: `python scripts/check_scenarios.py --reports data/reports.jsonl` ended
with `PASS`. The brief's Label-name and rule-code leak check printed nothing.

## Limitations noted at review (Claude Code, 27 October 2026)

- The four reports of a Scenario are built from two phrasings of three passages, so they share
  more wording than independent paraphrases would. Reports run 37–73 words (median 52), shorter
  than the 30–180 asked for, and customers write only 6 of 400. Real reports would be longer,
  messier and more varied, so measured accuracy here is likely optimistic.
- Splits are by Scenario, so shared wording never crosses build, validation and test.
