"""Write sample data for the demo until real predictions exist.

    python -m uv run python web/scripts/make_fixtures.py

Uses build-split Scenarios only (never validation or test). Each build Scenario becomes one
report whose text is its facts; approach A is the real rules baseline run on that text, B is
made up deterministically from the Seeded Label, C is the real cascade of the two. Metrics and
the curve are computed from those with the real Policies. Every file is marked
`"fixture": true`, and the app shows a "Sample data" notice. Running the real exporter
(eval/export_web.py) overwrites all of it.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
import tempfile
from dataclasses import replace
from pathlib import Path

from triage import baseline
from triage.cascade import cascade_all
from triage.policy import REVIEW, load_policy, predicted_urgency, routing_mode
from triage.schema import (
    Category,
    Destination,
    Prediction,
    Report,
    load_scenarios,
    split_sentences,
    write_predictions,
)

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "web" / "static" / "data"
ROLES = ("driver", "depot", "customer", "subcontractor")
CHANNELS = ("app", "email", "phone_transcript")

_spec = importlib.util.spec_from_file_location("export_web", ROOT / "eval" / "export_web.py")
export_web = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(export_web)


def h(text: str) -> float:
    """Deterministic number in [0, 1) from a string."""
    return int(hashlib.sha256(text.encode()).hexdigest()[:8], 16) / 0x100000000


def spread(top: str, labels: list[str], p: float) -> dict[str, float]:
    rest = [x for x in labels if x != top]
    runner = rest[int(h(top + str(p)) * len(rest))]
    probs = {x: round((1 - p) * 0.25 / (len(rest) - 1), 4) for x in rest}
    probs[runner] = round((1 - p) * 0.75, 4)
    probs[top] = round(p, 4)
    return probs


def fake_b(report: Report, a: Prediction, scenario) -> Prediction:
    rid = report.report_id
    cats, dests = [c.value for c in Category], [d.value for d in Destination]
    cat = scenario.category.value if h(rid + "c") < 0.88 else cats[int(h(rid + "c2") * 6)]
    dest = scenario.destination.value if h(rid + "d") < 0.86 else dests[int(h(rid + "d2") * 6)]
    if scenario.urgency == "urgent":
        urgent = 0.62 + 0.36 * h(rid + "u") if h(rid + "m") < 0.9 else 0.22 + 0.2 * h(rid)
    else:
        urgent = 0.02 + 0.3 * h(rid + "u") if h(rid + "m") < 0.9 else 0.45 + 0.3 * h(rid)
    sentences = split_sentences(report.text)
    evidence = sorted(set(a.evidence) | {sentences[0]}, key=sentences.index)
    return replace(
        a, approach="B", category=Category(cat),
        category_probs=spread(cat, cats, 0.5 + 0.48 * h(rid + "pc")),
        urgent_prob=round(urgent, 4), destination=Destination(dest),
        destination_probs=spread(dest, dests, 0.5 + 0.48 * h(rid + "pd")),
        evidence=evidence, triggers=[], latency_ms=round(200 + 140 * h(rid + "l"), 1),
        input_tokens=2100 + int(300 * h(rid + "t")), output_tokens=320, attempts=1,
        model="jev-1.14.0", version="b-v1")


def nearest_rank(values: list[float], pct: float) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    return ordered[max(0, -(-len(ordered) * pct // 100) - 1)]


def metrics(preds: list[Prediction], labels: dict, texts: dict, scen: dict, policy) -> dict:
    n = len(preds)
    rows = []
    for p in preds:
        lab = labels[p.report_id]
        mode, reasons = routing_mode(p, policy)
        urg = predicted_urgency(p, policy)
        auto = mode != REVIEW
        missed = auto and lab.urgency == "urgent" and urg == "routine"
        rows.append((p, lab, auto, urg, missed, reasons))
    reviewed = sum(not r[2] for r in rows)
    urgent = [r for r in rows if r[1].urgency == "urgent"]
    flagged = [r for r in rows if r[3] == "urgent"]
    costs = {k: 0.0 for k in policy.costs}
    for p, lab, auto, urg, missed, _ in rows:
        if not auto:
            costs["review"] += policy.costs["review"]
            continue
        costs["missed_urgent"] += policy.costs["missed_urgent"] * missed
        costs["false_alarm"] += policy.costs["false_alarm"] * (
            lab.urgency == "routine" and urg == "urgent")
        if p.destination != lab.destination:
            costs["wrong_destination"] += policy.costs["wrong_destination"]
        elif p.category != lab.category:
            costs["wrong_category_same_destination"] += policy.costs[
                "wrong_category_same_destination"]
    total = sum(costs.values())
    lat = [p.latency_ms for p in preds]
    mean_in = sum(p.input_tokens for p in preds) / n
    auto_err = sum(r[2] and (r[0].category != r[1].category or r[0].destination
                             != r[1].destination or r[3] != r[1].urgency) for r in rows)
    return {
        "n": n,
        "category": {"accuracy": round(sum(p.category == labels[p.report_id].category
                                           for p in preds) / n, 4)},
        "destination": {"accuracy": round(sum(p.destination == labels[p.report_id].destination
                                              for p in preds) / n, 4)},
        "urgency": {"recall": round(sum(r[3] == "urgent" for r in urgent) / max(1, len(urgent)), 4),
                    "precision": round(sum(r[1].urgency == "urgent" for r in flagged)
                                       / max(1, len(flagged)), 4)},
        "routing": {
            "review_rate": round(reviewed / n, 4),
            "auto_route_coverage": round(1 - reviewed / n, 4),
            "auto_routed_error_rate": round(auto_err / max(1, n - reviewed), 4),
            "missed_urgent_count": sum(r[4] for r in rows),
            "missed_urgent": [{"report_id": r[0].report_id, "scenario_id": scen[r[0].report_id],
                               "text": texts[r[0].report_id][:160],
                               "urgent_prob": r[0].urgent_prob, "triggers": r[5]}
                              for r in rows if r[4]],
        },
        "cost": {"total": total, "per_100": round(100 * total / n, 4),
                 "terms": {k: {"total": v, "per_100": round(100 * v / n, 4)}
                           for k, v in costs.items()}},
        "latency": {"p50": nearest_rank(lat, 50), "p95": nearest_rank(lat, 95),
                    "max": max(lat), "n": n},
        "tokens": {"mean_input": round(mean_in, 1),
                   "mean_output": round(sum(p.output_tokens for p in preds) / n, 1)},
        "api_cost_per_1000_usd": round(mean_in * 0.042 / 1000, 4),
    }


def with_thresholds(policy, approach: str, **changes):
    t = {**export_web.thresholds_for(policy, approach), **changes}
    # Flat keys for the current policy.py, per-approach keys for the J2 one.
    return replace(policy, thresholds={**t, approach: t})


def curve(preds: list[Prediction], labels: dict, ctx: tuple, policies: dict) -> dict:
    approach = preds[0].approach
    out = {"points": []}
    base = policies["v1"]
    t0 = export_web.thresholds_for(base, approach)["urgent_threshold"]
    for w in [i / 20 for i in range(10)]:
        lo, hi = round(max(0.0, t0 - w), 2), round(min(1.0, t0 + w), 2)
        pol = with_thresholds(base, approach, review_band=[lo, hi])
        m = metrics(preds, labels, *ctx, pol)
        out["points"].append({"review_rate": m["routing"]["review_rate"],
                              "missed_urgent": m["routing"]["missed_urgent_count"],
                              "urgent_threshold": t0, "band": [lo, hi]})
    for v, pol in policies.items():
        m = metrics(preds, labels, *ctx, pol)
        out[v] = {"review_rate": m["routing"]["review_rate"],
                  "missed_urgent": m["routing"]["missed_urgent_count"]}
    return out



def main() -> None:
    scenarios = [s for s in load_scenarios(ROOT / "data" / "scenarios.jsonl")
                 if s.split == "build"]
    by_id = {s.scenario_id: s for s in scenarios}
    reports = []
    for i, s in enumerate(sorted(scenarios, key=lambda s: h(s.scenario_id))):
        text = " ".join(f if f.endswith((".", "!", "?")) else f + "." for f in s.facts)
        reports.append(Report(f"R-{5001 + i}", s.scenario_id, text,
                              ROLES[int(h(s.scenario_id + "r") * 4)],
                              CHANNELS[int(h(s.scenario_id + "ch") * 3)]))
    a = [replace(baseline.predict(r), latency_ms=round(0.3 + h(r.report_id) * 0.5, 2))
         for r in reports]
    rep = {r.report_id: r for r in reports}
    b = [fake_b(rep[p.report_id], p, by_id[rep[p.report_id].scenario_id]) for p in a]
    c = cascade_all(a, b)

    labels = {r.report_id: by_id[r.scenario_id].label for r in reports}
    texts = {r.report_id: r.text for r in reports}
    scen = {r.report_id: r.scenario_id for r in reports}
    policies = {v: load_policy(ROOT / "policies" / f"{v}.json") for v in ("v1", "v2")}

    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        (root / "data").mkdir()
        (root / "results").mkdir()
        (root / "data" / "scenarios.jsonl").write_text(
            (ROOT / "data" / "scenarios.jsonl").read_text(encoding="utf-8"), encoding="utf-8")
        with open(root / "data" / "reports.jsonl", "w", encoding="utf-8", newline="\n") as f:
            f.writelines(json.dumps({"report_id": r.report_id, "scenario_id": r.scenario_id,
                                    "author_role": r.author_role, "channel": r.channel,
                                    "text": r.text, "generator": "fixture: Scenario facts",
                                    "synthetic": True}) + "\n" for r in reports)
        (root / "policies").mkdir()
        for v in ("v1", "v2"):
            (root / "policies" / f"{v}.json").write_text(
                (ROOT / "policies" / f"{v}.json").read_text(encoding="utf-8"), encoding="utf-8")
        for name, preds in (("A", a), ("B", b), ("C", c)):
            write_predictions(root / "results" / "predictions" / f"{name}_build.jsonl", preds)
        result = {name: {v: metrics(preds, labels, texts, scen, p) for v, p in policies.items()}
                  for name, preds in (("A", a), ("B", b), ("C", c))}
        (root / "results" / "metrics_build_seeded.json").write_text(json.dumps(result))
        curves = {name: curve(preds, labels, (texts, scen), policies) for name, preds in
                  (("A", a), ("B", b), ("C", c))}
        (root / "results" / "curve_validation.json").write_text(json.dumps(curves))
        export_web.export(root, OUT, split="build", labelling_split="build", fixture=True)
    print(f"wrote sample data for {len(reports)} build reports to {OUT}", file=sys.stderr)


if __name__ == "__main__":
    main()
