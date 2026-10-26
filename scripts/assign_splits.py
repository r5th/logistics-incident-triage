"""Assign build / validation / test splits to Scenarios, reproducibly.

Procedure (seed 20261027, standard library only):

1. Read data/scenarios.jsonl (authored without `split`; an existing `split` is ignored).
2. Group Scenarios into strata by (urgency, category). Urgent strata come first, then routine;
   within each, categories in alphabetical order.
3. Inside each stratum, order Scenarios with destination exceptions first, then shuffle each of
   those two groups with one seeded random.Random(20261027), consumed in stratum order.
4. Walk the concatenated list and deal splits from a fixed 10-slot pattern
   (5 build, 2 validation, 3 test). There are exactly 30 urgent Scenarios, so the urgent block
   is three whole patterns and every split gets exactly 30% urgent; categories and exceptions are
   spread because consecutive members of a stratum land in different slots.
5. Write the file back in Data-contract field order.

Run: python scripts/assign_splits.py [path]   (default data/scenarios.jsonl)
"""

import json
import random
import sys
from pathlib import Path

SEED = 20261027
PATTERN = ["build", "test", "validation", "build", "test",
           "build", "build", "test", "validation", "build"]
FIELDS = ["scenario_id", "split", "category", "urgency", "destination",
          "destination_is_exception", "tags", "facts", "label_reason"]


def assign(scenarios):
    rng = random.Random(SEED)
    strata = {}
    for s in sorted(scenarios, key=lambda s: s["scenario_id"]):
        strata.setdefault((s["urgency"] != "urgent", s["category"]), []).append(s)
    ordered = []
    for key in sorted(strata):
        members = strata[key]
        exceptions = [s for s in members if s["destination_is_exception"]]
        defaults = [s for s in members if not s["destination_is_exception"]]
        rng.shuffle(exceptions)
        rng.shuffle(defaults)
        ordered += exceptions + defaults
    for i, s in enumerate(ordered):
        s["split"] = PATTERN[i % len(PATTERN)]
    return sorted(ordered, key=lambda s: s["scenario_id"])


def main():
    path = Path(sys.argv[1] if len(sys.argv) > 1 else "data/scenarios.jsonl")
    scenarios = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]
    out = assign(scenarios)
    with path.open("w", encoding="utf-8", newline="\n") as f:
        for s in out:
            f.write(json.dumps({k: s[k] for k in FIELDS}, ensure_ascii=False) + "\n")
    counts = {}
    for s in out:
        counts[s["split"]] = counts.get(s["split"], 0) + 1
    print("assigned:", counts)


if __name__ == "__main__":
    main()
