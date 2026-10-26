"""Build the demo's JSON from committed data, predictions, Policies and results.

    python -m uv run python eval/export_web.py [--split test|validation|build] [--out web/static/data]

Writes incidents.json, results.json, curve.json and labelling.json; the shapes are described in
web/src/lib/data/types.ts. Missing inputs give empty arrays or nulls, never an error, so the
demo builds before any prediction exists. Output is deterministic: no timestamps, no absolute
paths, sorted where order is not meaningful.

labelling.json feeds the blind-labelling screen, so it carries report ids and text only: no
Label, no Scenario, no prediction (tests/test_export_web.py guards this).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import random
from pathlib import Path

from triage.policy import (
    LOW_CATEGORY,
    LOW_DESTINATION,
    PREDICTION_ERROR,
    REVIEW,
    TRIGGER_NAMES,
    UNCERTAIN_URGENCY,
    Policy,
    load_policy,
    predicted_urgency,
    routing_mode,
)
from triage.schema import Prediction, load_predictions, split_sentences

APPROACHES = ("A", "B", "C")
POLICIES = ("v1", "v2")
SPLITS = ("test", "validation", "build")
SEED = 20261027
PASS2_SAMPLE = 25
# The demo's clock: every report "arrives" during the night shift before this time.
DEMO_CLOCK_MIN = 8 * 60

# Plain-words detail for the Review Triggers an approach raises itself.
TRIGGER_DETAIL = {
    "no_rule_matched": "No rule matched the report text, so the rules cannot decide.",
    "conflicting_categories": "Two Categories are almost equally likely.",
    "conflicting_statements": "The report contradicts itself on a fact that decides the Label.",
    "multiple_issues": "The report describes more than one issue.",
    "location_missing": "The report does not say where the vehicle is.",
    "cargo_missing": "The report does not say what the load is.",
    "invalid_output": "The model's answer could not be read, so nothing was decided.",
}


def _jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def _json(path: Path):
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else None


def _write(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    path.write_text(text + "\n", encoding="utf-8", newline="\n")


def _r(x: float) -> float:
    return round(float(x), 4)


def thresholds_for(policy: Policy, approach: str) -> dict:
    """A Policy's thresholds for one approach; works for flat and per-approach Policy files."""
    t = policy.thresholds
    return t.get(approach, t)


def _hash(text: str) -> int:
    return int(hashlib.sha256(text.encode("utf-8")).hexdigest()[:8], 16)


def received_minutes(report_ids: list[str]) -> dict[str, int]:
    """Minutes before the demo clock each report arrived: about 4 minutes apart, in a fixed
    order that does not follow report ids."""
    order = sorted(report_ids, key=lambda rid: (_hash(rid), rid))
    return {rid: i * 4 + _hash(rid + "w") % 3 + 1 for i, rid in enumerate(order)}


def _clock(minutes_before: int) -> str:
    m = (DEMO_CLOCK_MIN - minutes_before) % (24 * 60)
    return f"{m // 60:02d}:{m % 60:02d}"


def _triggers(pred: Prediction, policy: Policy, reasons: list[str]) -> list[dict]:
    t = thresholds_for(policy, pred.approach)
    code_of = {TRIGGER_NAMES.get(c, c): c for c in pred.triggers}
    out = []
    for name in reasons:
        if name == UNCERTAIN_URGENCY:
            lo, hi = t["review_band"]
            detail = (f"Urgent probability {pred.urgent_prob:.2f} is inside the Review band "
                      f"{lo:.2f} to {hi:.2f}.")
            source = f"Policy {policy.version}"
        elif name == LOW_CATEGORY:
            top = max(pred.category_probs.values(), default=0.0)
            detail = (f"Top Category probability {top:.2f} is below the minimum "
                      f"{t['min_category_prob']:.2f}.")
            source = f"Policy {policy.version}"
        elif name == LOW_DESTINATION:
            top = max(pred.destination_probs.values(), default=0.0)
            detail = (f"Top Destination probability {top:.2f} is below the minimum "
                      f"{t['min_destination_prob']:.2f}.")
            source = f"Policy {policy.version}"
        elif name == PREDICTION_ERROR:
            detail = f"The approach returned an error: {pred.error}."
            source = f"Approach {pred.approach}"
        else:
            detail = TRIGGER_DETAIL.get(code_of.get(name, ""), "")
            source = f"Approach {pred.approach}"
        out.append({"name": name, "detail": detail, "source": source})
    return out


def _probs(probs: dict[str, float]) -> dict[str, float]:
    return {k: _r(v) for k, v in probs.items()}


def prediction_entry(pred: Prediction, sentences: list[str], policies: dict[str, Policy]) -> dict:
    evidence = set(pred.evidence)
    per_policy = {}
    for version, policy in policies.items():
        mode, reasons = routing_mode(pred, policy)
        per_policy[version] = {
            "urgency": predicted_urgency(pred, policy),
            "routing_mode": "review" if mode == REVIEW else "auto",
            "review_triggers": _triggers(pred, policy, reasons) if mode == REVIEW else [],
        }
    return {
        "category": {"top": pred.category.value, "probs": _probs(pred.category_probs)},
        "urgent_prob": _r(pred.urgent_prob),
        "destination": {"top": pred.destination.value, "probs": _probs(pred.destination_probs)},
        "evidence": [i for i, s in enumerate(sentences) if s in evidence],
        "latency_ms": round(pred.latency_ms, 1),
        "model": pred.model,
        "version": pred.version,
        "source": pred.source,
        "error": pred.error,
        "policies": per_policy,
    }


def final_test_labels(root: Path) -> dict[str, dict] | None:
    """Final test Labels: adjudicated when present, else Blind Labels pass 1, else None."""
    adjudicated = _json(root / "data" / "labels" / "adjudicated_test.json")
    if adjudicated is not None:
        rows = adjudicated
    else:
        blind = _json(root / "data" / "labels" / "blind_test.json")
        if blind is None:
            return None
        rows = [r for r in blind if r.get("pass") == 1]
    return {r["report_id"]: {k: r[k] for k in ("category", "urgency", "destination")}
            for r in rows}


def choose_split(root: Path) -> str:
    for split in SPLITS:
        if any((root / "results" / "predictions" / f"{a}_{split}.jsonl").exists()
               for a in APPROACHES):
            return split
    return "test"


def build_incidents(root: Path, split: str, fixture: bool) -> dict:
    scenarios = {s["scenario_id"]: s for s in _jsonl(root / "data" / "scenarios.jsonl")}
    raw_reports = _jsonl(root / "data" / "reports.jsonl")
    reports = sorted((r for r in raw_reports
                      if scenarios.get(r["scenario_id"], {}).get("split") == split),
                     key=lambda r: r["report_id"])
    policies = {v: load_policy(root / "policies" / f"{v}.json") for v in POLICIES
                if (root / "policies" / f"{v}.json").exists()}
    preds: dict[str, dict[str, Prediction]] = {}
    for a in APPROACHES:
        path = root / "results" / "predictions" / f"{a}_{split}.jsonl"
        if path.exists():
            preds[a] = {p.report_id: p for p in load_predictions(path)}

    if split == "test":
        labels, labels_source = final_test_labels(root), "final"
        if labels is None:
            labels_source = None  # Seeded Labels of test stay hidden until Blind Labels exist
    else:
        labels_source = "seeded"
        labels = {r["report_id"]: {k: scenarios[r["scenario_id"]][k]
                                   for k in ("category", "urgency", "destination")}
                  for r in reports}

    waited = received_minutes([r["report_id"] for r in reports])
    out_reports = []
    for r in reports:
        sentences = split_sentences(r["text"])
        entry = {
            "id": r["report_id"],
            "text": r["text"],
            "sentences": sentences,
            "author_role": r["author_role"],
            "channel": r["channel"],
            "received": _clock(waited[r["report_id"]]),
            "waiting_min": waited[r["report_id"]],
            "predictions": {a: prediction_entry(p[r["report_id"]], sentences, policies)
                            for a, p in preds.items() if r["report_id"] in p},
        }
        if labels and r["report_id"] in labels:
            entry["label"] = labels[r["report_id"]]
        out_reports.append(entry)

    return {
        "fixture": fixture,
        "split": split,
        "labels_source": labels_source,
        "demo_clock": _clock(0),
        "approaches": sorted(preds),
        "generators": sorted({r.get("generator") for r in raw_reports if r.get("generator")}),
        "models": sorted({p.model for ps in preds.values() for p in ps.values() if p.model}),
        "policies": {
            v: {"version": p.version, "frozen": p.frozen, "costs": p.costs,
                "forcing_triggers": p.forcing_triggers,
                "thresholds": {a: thresholds_for(p, a) for a in APPROACHES}}
            for v, p in policies.items()
        },
        "reports": out_reports,
    }


def build_results(root: Path, fixture: bool) -> dict:
    for split, labels in (("test", "final"), ("test", "seeded"), ("validation", "seeded"),
                          ("build", "seeded")):
        name = f"metrics_{split}_{labels}.json"
        metrics = _json(root / "results" / name)
        if metrics is not None:
            return {"fixture": fixture, "split": split, "labels": labels,
                    "report_path": f"results/report_{split}_{labels}.md", "metrics": metrics}
    return {"fixture": fixture, "split": None, "labels": None, "report_path": None,
            "metrics": None}


def build_curve(root: Path, fixture: bool) -> dict:
    """Normalise results/curve_<split>.json to {approach: {points, v1, v2}}."""
    for split in ("test", "validation"):
        raw = _json(root / "results" / f"curve_{split}.json")
        if raw is None:
            continue
        approaches = {}
        for a in APPROACHES:
            entry = raw.get(a)
            if entry is None:
                continue
            points = entry.get("points", entry if isinstance(entry, list) else [])
            chosen = entry.get("chosen", entry) if isinstance(entry, dict) else {}
            approaches[a] = {"points": points, "v1": chosen.get("v1"), "v2": chosen.get("v2")}
        return {"fixture": fixture, "split": split, "approaches": approaches}
    return {"fixture": fixture, "split": None, "approaches": {}}


def build_labelling(root: Path, split: str, fixture: bool) -> dict:
    scenarios = {s["scenario_id"]: s["split"] for s in _jsonl(root / "data" / "scenarios.jsonl")}
    reports = sorted(({"id": r["report_id"], "text": r["text"]}
                      for r in _jsonl(root / "data" / "reports.jsonl")
                      if scenarios.get(r["scenario_id"]) == split),
                     key=lambda r: r["id"])
    ids = [r["id"] for r in reports]
    random.Random(SEED).shuffle(reports)
    pass2 = sorted(random.Random(SEED).sample(ids, min(PASS2_SAMPLE, len(ids))))
    return {"fixture": fixture, "seed": SEED, "reports": reports, "pass2_ids": pass2}


def export(root: Path, out: Path, split: str | None = None, labelling_split: str = "test",
           fixture: bool = False) -> None:
    root, out = Path(root), Path(out)
    split = split or choose_split(root)
    _write(out / "incidents.json", build_incidents(root, split, fixture))
    _write(out / "results.json", build_results(root, fixture))
    _write(out / "curve.json", build_curve(root, fixture))
    _write(out / "labelling.json", build_labelling(root, labelling_split, fixture))


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--split", choices=SPLITS, default=None,
                        help="split shown in the Queue (default: first of test, validation, "
                             "build that has predictions)")
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--out", type=Path, default=Path("web/static/data"))
    args = parser.parse_args(argv)
    export(args.root, args.out, args.split)
    print(f"wrote {args.out}/incidents.json, results.json, curve.json, labelling.json")


if __name__ == "__main__":
    main()
