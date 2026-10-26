"""Approach C: use the rules (A) when they are confident, otherwise TypeSafe (B).

Built from cached A and B Predictions, so it makes no API calls of its own. When B is used,
the cascade is charged A's latency plus B's (B would only run after A) and B's tokens.
"""

from __future__ import annotations

from dataclasses import replace

from triage.baseline import HARD_URGENT, NO_URGENCY
from triage.schema import Prediction

# A's top Category must lead the runner-up by at least this much.
MIN_CATEGORY_MARGIN = 0.3


def a_is_confident(a: Prediction) -> bool:
    top, second = (sorted(a.category_probs.values(), reverse=True) + [0.0, 0.0])[:2]
    return (not a.triggers and top - second >= MIN_CATEGORY_MARGIN
            and (a.urgent_prob >= HARD_URGENT or a.urgent_prob <= NO_URGENCY))


def cascade(a: Prediction, b: Prediction) -> Prediction:
    if a.report_id != b.report_id:
        raise ValueError(f"report_id mismatch: {a.report_id} vs {b.report_id}")
    if a_is_confident(a):
        return replace(a, approach="C", source="A")
    return replace(b, approach="C", source="B", latency_ms=a.latency_ms + b.latency_ms)


def cascade_all(a_preds: list[Prediction], b_preds: list[Prediction]) -> list[Prediction]:
    a_by_id = {p.report_id: p for p in a_preds}
    b_by_id = {p.report_id: p for p in b_preds}
    unmatched = sorted(set(a_by_id) ^ set(b_by_id))
    if unmatched:
        raise ValueError(f"A and B predictions cover different reports: {unmatched[:5]}")
    return [cascade(a_by_id[r], b_by_id[r]) for r in sorted(a_by_id)]
