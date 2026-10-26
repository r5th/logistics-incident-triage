"""Policy: thresholds, Review Triggers and error costs that decide Routing Mode and score it.

A Policy is applied after the fact to cached Predictions, so changing thresholds needs no new
API calls. Cost unit is the reviewer-minute equivalent (docs/build-plan.md, Fixed decisions).
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from triage.schema import ROUTINE, URGENT, Label, Prediction

AUTO = "auto"
REVIEW = "review"

# Human-readable Review Trigger names for the trigger codes approaches raise.
TRIGGER_NAMES: dict[str, str] = {
    "no_rule_matched": "No rule matched",
    "conflicting_categories": "Conflicting categories",
    "conflicting_statements": "Conflicting statements",
    "multiple_issues": "Multiple issues",
    "location_missing": "Location missing",
    "cargo_missing": "Cargo not identified",
    "invalid_output": "Invalid model output",
}
UNCERTAIN_URGENCY = "Urgency uncertain"
LOW_CATEGORY = "Low category probability"
LOW_DESTINATION = "Low destination probability"
PREDICTION_ERROR = "Prediction error"


@dataclass(frozen=True)
class Policy:
    version: str
    costs: dict[str, float]
    thresholds: dict
    forcing_triggers: list[str]
    frozen: bool = False


def load_policy(path: str | Path) -> Policy:
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    return Policy(
        version=raw["version"],
        costs=raw["costs"],
        thresholds=raw["thresholds"],
        forcing_triggers=list(raw["forcing_triggers"]),
        frozen=bool(raw.get("frozen", False)),
    )


def predicted_urgency(pred: Prediction, policy: Policy) -> str:
    return URGENT if pred.urgent_prob >= policy.thresholds["urgent_threshold"] else ROUTINE


def routing_mode(pred: Prediction, policy: Policy) -> tuple[str, list[str]]:
    """Return ("auto" | "review", reasons). Reasons are Review Trigger names, in a fixed order."""
    t = policy.thresholds
    reasons = [TRIGGER_NAMES.get(code, code) for code in pred.triggers
               if code in policy.forcing_triggers]
    lo, hi = t["review_band"]
    if lo <= pred.urgent_prob <= hi:
        reasons.append(UNCERTAIN_URGENCY)
    if max(pred.category_probs.values(), default=0.0) < t["min_category_prob"]:
        reasons.append(LOW_CATEGORY)
    if max(pred.destination_probs.values(), default=0.0) < t["min_destination_prob"]:
        reasons.append(LOW_DESTINATION)
    if pred.error is not None:
        reasons.append(PREDICTION_ERROR)
    return (REVIEW if reasons else AUTO), reasons


def cost(pred: Prediction, label: Label, policy: Policy) -> float:
    """Cost of one Prediction under a Policy.

    Review costs only the review cost: the reviewer is assumed to fix every decision.
    Auto-route sums every error term that applies.
    """
    c = policy.costs
    if routing_mode(pred, policy)[0] == REVIEW:
        return c["review"]
    total = 0.0
    urgency = predicted_urgency(pred, policy)
    if label.urgency == URGENT and urgency == ROUTINE:
        total += c["missed_urgent"]
    if label.urgency == ROUTINE and urgency == URGENT:
        total += c["false_alarm"]
    if pred.destination != label.destination:
        total += c["wrong_destination"]
    elif pred.category != label.category:
        total += c["wrong_category_same_destination"]
    return total
