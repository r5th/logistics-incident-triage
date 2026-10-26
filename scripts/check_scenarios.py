"""Validate data/scenarios.jsonl against the Data contract in docs/build-plan.md.

Checks schema and enums, counts, split balance, urgent and tag rates, and destination
exceptions, then prints a summary table. Exits 1 on any failure.

With --reports PATH it also validates data/reports.jsonl (the J1 output) against the
scenarios: 400 lines, 4 per Scenario, schema fields and enums, unique ids, 30-180 words.

Run: python scripts/check_scenarios.py [--scenarios PATH] [--reports PATH]
Standard library only.
"""

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path

CATEGORIES = ["vehicle_breakdown", "delivery_delay", "shipment_damage",
              "missing_shipment", "documentation_issue", "safety_incident"]
DEFAULT_DEST = dict(zip(CATEGORIES, ["fleet_support", "customer_desk", "claims",
                                     "security_investigations", "compliance", "safety_desk"]))
DESTINATIONS = set(DEFAULT_DEST.values())
URGENCY = {"urgent", "routine"}
SPLITS = {"build": 50, "validation": 20, "test": 30}
TAGS = {"multi_issue", "incomplete", "contradictory", "hazmat", "temperature_controlled",
        "time_critical", "night", "third_party"}
FIELDS = ["scenario_id", "split", "category", "urgency", "destination",
          "destination_is_exception", "tags", "facts", "label_reason"]
# (target, allowed half-width) as fractions of all Scenarios
TAG_TARGETS = {"multi_issue": (0.20, 0.05), "incomplete": (0.15, 0.05),
               "contradictory": (0.05, 0.02)}
URGENT_TARGET, URGENT_TOL = 0.30, 0.05
EXCEPTION_TARGET, EXCEPTION_TOL = 0.20, 0.05

REPORT_FIELDS = ["report_id", "scenario_id", "author_role", "channel", "text", "generator",
                 "synthetic"]
ROLES = {"driver", "depot", "customer", "subcontractor"}
CHANNELS = {"app", "email", "phone_transcript"}


class Checker:
    def __init__(self):
        self.errors = []

    def check(self, ok, msg):
        if not ok:
            self.errors.append(msg)
        return ok


def load(path):
    rows = []
    for n, line in enumerate(Path(path).read_text(encoding="utf-8").splitlines(), 1):
        if line.strip():
            rows.append((n, json.loads(line)))
    return rows


def pct(n, d):
    return f"{100 * n / d:5.1f}%" if d else "  n/a"


def check_scenarios(rows, c):
    ids = [s.get("scenario_id") for _, s in rows]
    c.check(len(rows) == 100, f"expected 100 scenarios, got {len(rows)}")
    c.check(ids == [f"S-{i:03d}" for i in range(1, len(rows) + 1)],
            "scenario_ids must be S-001.. in order with no gaps")
    for n, s in rows:
        where = f"line {n} ({s.get('scenario_id')})"
        if not c.check(list(s) == FIELDS, f"{where}: fields {list(s)} != {FIELDS}"):
            continue
        c.check(s["split"] in SPLITS, f"{where}: bad split {s['split']!r}")
        c.check(s["category"] in CATEGORIES, f"{where}: bad category {s['category']!r}")
        c.check(s["urgency"] in URGENCY, f"{where}: bad urgency {s['urgency']!r}")
        c.check(s["destination"] in DESTINATIONS, f"{where}: bad destination {s['destination']!r}")
        c.check(isinstance(s["destination_is_exception"], bool),
                f"{where}: destination_is_exception must be bool")
        if s["category"] in DEFAULT_DEST:
            is_exc = s["destination"] != DEFAULT_DEST[s["category"]]
            c.check(is_exc == s["destination_is_exception"],
                    f"{where}: destination_is_exception disagrees with the category default")
        c.check(s["category"] != "safety_incident" or not s["destination_is_exception"],
                f"{where}: safety_incident has no destination exceptions")
        c.check(isinstance(s["tags"], list) and set(s["tags"]) <= TAGS
                and len(set(s["tags"])) == len(s["tags"]), f"{where}: bad tags {s['tags']}")
        c.check(isinstance(s["facts"], list) and len(s["facts"]) >= 2
                and all(isinstance(f, str) and f.strip() for f in s["facts"]),
                f"{where}: facts must be a list of at least 2 non-empty strings")
        reason = s["label_reason"]
        c.check(isinstance(reason, str) and reason.strip() and "\n" not in reason,
                f"{where}: label_reason must be one non-empty line")
        c.check(bool(re.search(r"\bU[0-6]\b", reason)) and bool(re.search(r"\b(D0|X[1-6])\b", reason)),
                f"{where}: label_reason must cite an Urgency rule (U0-U6) and D0 or X1-X6")
        if s["destination_is_exception"]:
            c.check(bool(re.search(r"\bX[1-6]\b", reason)), f"{where}: exception without an X rule")
    good = [s for _, s in rows if list(s) == FIELDS]
    total = len(good)
    by_split = {k: [s for s in good if s["split"] == k] for k in SPLITS}

    # counts
    for k, want in SPLITS.items():
        c.check(len(by_split[k]) == want, f"split {k}: {len(by_split[k])} scenarios, want {want}")
    cat_counts = Counter(s["category"] for s in good)
    for cat in CATEGORIES:
        c.check(14 <= cat_counts[cat] <= 20, f"category {cat}: {cat_counts[cat]}, want 14-20")
    # rates
    for name, group in [("all", good)] + list(by_split.items()):
        if not group:
            continue
        u = sum(s["urgency"] == "urgent" for s in group) / len(group)
        c.check(abs(u - URGENT_TARGET) <= URGENT_TOL + 1e-9,
                f"urgent rate in {name} is {u:.0%}, want {URGENT_TARGET:.0%} +/- {URGENT_TOL:.0%}")
        e = sum(s["destination_is_exception"] for s in group)
        c.check(e > 0, f"no destination exceptions in {name}")
    e = sum(s["destination_is_exception"] for s in good) / max(total, 1)
    c.check(abs(e - EXCEPTION_TARGET) <= EXCEPTION_TOL + 1e-9,
            f"exception rate {e:.0%}, want {EXCEPTION_TARGET:.0%} +/- {EXCEPTION_TOL:.0%}")
    tag_counts = Counter(t for s in good for t in s["tags"])
    for tag, (target, tol) in TAG_TARGETS.items():
        r = tag_counts[tag] / max(total, 1)
        c.check(abs(r - target) <= tol + 1e-9, f"tag {tag} rate {r:.0%}, want {target:.0%} +/- {tol:.0%}")

    # summary
    print("Scenarios by split")
    print(f"{'split':<12}{'n':>4}{'urgent':>9}{'except.':>9}{'multi':>8}{'incompl':>9}{'contra':>8}")
    for name, group in list(by_split.items()) + [("all", good)]:
        n = len(group)
        tc = Counter(t for s in group for t in s["tags"])
        print(f"{name:<12}{n:>4}"
              f"{pct(sum(s['urgency'] == 'urgent' for s in group), n):>9}"
              f"{pct(sum(s['destination_is_exception'] for s in group), n):>9}"
              f"{pct(tc['multi_issue'], n):>8}{pct(tc['incomplete'], n):>9}"
              f"{pct(tc['contradictory'], n):>8}")
    print()
    print("Category x split (urgent/total)")
    print(f"{'category':<22}" + "".join(f"{k:>12}" for k in SPLITS) + f"{'all':>10}")
    missing_urgent = []
    for cat in CATEGORIES:
        cells = []
        for k in SPLITS:
            g = [s for s in by_split[k] if s["category"] == cat]
            u = sum(s["urgency"] == "urgent" for s in g)
            cells.append(f"{u}/{len(g)}")
            if u == 0:
                missing_urgent.append(f"{cat} in {k}")
        g = [s for s in good if s["category"] == cat]
        allc = f"{sum(s['urgency'] == 'urgent' for s in g)}/{len(g)}"
        print(f"{cat:<22}" + "".join(f"{x:>12}" for x in cells) + f"{allc:>10}")
    print()
    print("Destinations (all):", dict(sorted(Counter(s["destination"] for s in good).items())))
    print("Tags (all):", dict(sorted(tag_counts.items())))
    if missing_urgent:
        print("note: no urgent example for", "; ".join(missing_urgent))
    return {s["scenario_id"]: s for s in good}


def check_reports(rows, scenarios, c):
    c.check(len(rows) == 400, f"expected 400 reports, got {len(rows)}")
    ids = [r.get("report_id") for _, r in rows]
    c.check(len(set(ids)) == len(ids), "report_ids are not unique")
    c.check(sorted(ids) == [f"R-{i:04d}" for i in range(1, len(rows) + 1)],
            "report_ids must be R-0001.. with no gaps")
    per_scenario = Counter()
    roles = {}
    words = []
    for n, r in rows:
        where = f"reports line {n} ({r.get('report_id')})"
        if not c.check(list(r) == REPORT_FIELDS, f"{where}: fields {list(r)} != {REPORT_FIELDS}"):
            continue
        c.check(r["scenario_id"] in scenarios, f"{where}: unknown scenario_id {r['scenario_id']}")
        c.check(r["author_role"] in ROLES, f"{where}: bad author_role {r['author_role']!r}")
        c.check(r["channel"] in CHANNELS, f"{where}: bad channel {r['channel']!r}")
        c.check(isinstance(r["generator"], str) and r["generator"].strip(), f"{where}: empty generator")
        c.check(r["synthetic"] is True, f"{where}: synthetic must be true")
        w = len(r["text"].split()) if isinstance(r["text"], str) else 0
        words.append(w)
        c.check(30 <= w <= 180, f"{where}: {w} words, want 30-180")
        per_scenario[r["scenario_id"]] += 1
        roles.setdefault(r["scenario_id"], set()).add(r["author_role"])
    for sid in scenarios:
        c.check(per_scenario[sid] == 4, f"{sid}: {per_scenario[sid]} reports, want 4")
        c.check(len(roles.get(sid, ())) >= 2, f"{sid}: all reports share one author_role")
    in_order = [r.get("scenario_id") for _, r in sorted(rows, key=lambda x: x[1].get("report_id", ""))]
    runs = sum(a == b for a, b in zip(in_order, in_order[1:]))
    c.check(runs < 40, f"report_ids look unshuffled ({runs} adjacent same-scenario pairs)")
    print()
    print(f"Reports: {len(rows)} lines, {len(per_scenario)} scenarios, "
          f"words min/median/max {min(words, default=0)}/"
          f"{sorted(words)[len(words) // 2] if words else 0}/{max(words, default=0)}")
    print("author_role:", dict(Counter(r["author_role"] for _, r in rows)))
    print("channel:", dict(Counter(r["channel"] for _, r in rows)))
    print("generator:", dict(Counter(r["generator"] for _, r in rows)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scenarios", default="data/scenarios.jsonl")
    ap.add_argument("--reports")
    args = ap.parse_args()
    c = Checker()
    scenarios = check_scenarios(load(args.scenarios), c)
    if args.reports:
        check_reports(load(args.reports), scenarios, c)
    print()
    if c.errors:
        print(f"FAIL: {len(c.errors)} problem(s)")
        for e in c.errors[:50]:
            print(" -", e)
        sys.exit(1)
    print("PASS")


if __name__ == "__main__":
    main()
