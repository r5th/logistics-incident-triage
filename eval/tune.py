"""Tune per-approach Policy thresholds on validation only, or export an operating-point curve."""

import argparse
import hashlib
import json
import sys
from dataclasses import replace
from pathlib import Path

if __package__ in (None, ''):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from eval.evaluate import (
    cached_predictions,
    decision_rows,
    load_labels,
    operating_statistics,
    split_reports,
    write_json,
)
from triage.policy import load_policy

GRID = tuple(i / 20 for i in range(1, 20))
MIN_PROBS = (0, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8)


def tune_thresholds(preds, labels, policy):
    """Minimise (total cost, Review count, threshold tuple) over the complete specified grid.

    Precompute the loss of Auto-route at each urgent threshold. Review replaces that loss
    with its fixed cost; confidence and band masks can then be reused without Policy copies.
    """
    confidence = {}
    for category in MIN_PROBS:
        for destination in MIN_PROBS:
            confidence[category, destination] = sum(
                1 << i for i, p in enumerate(preds)
                if p.error is not None or any(t in policy.forcing_triggers for t in p.triggers)
                or max(p.category_probs.values(), default=0) < category
                or max(p.destination_probs.values(), default=0) < destination)
    bands = {(lo, hi): sum(1 << i for i, p in enumerate(preds)
                           if lo < hi and lo <= p.urgent_prob <= hi)
             for lo in GRID for hi in GRID if lo <= hi}
    best = None
    for threshold in GRID:
        losses = []
        for p in preds:
            label = labels[p.report_id]
            urgent = p.urgent_prob >= threshold
            losses.append(
                policy.costs['missed_urgent'] * (label.urgency == 'urgent' and not urgent)
                + policy.costs['false_alarm'] * (label.urgency == 'routine' and urgent)
                + (policy.costs['wrong_destination'] if p.destination != label.destination
                   else policy.costs['wrong_category_same_destination']
                   * (p.category != label.category)))
        totals = {}
        for lo in GRID:
            if lo > threshold:
                continue
            for hi in GRID:
                if hi < threshold:
                    continue
                for category in MIN_PROBS:
                    for destination in MIN_PROBS:
                        mask = bands[lo, hi] | confidence[category, destination]
                        if mask not in totals:
                            totals[mask] = sum(policy.costs['review'] if mask & (1 << i)
                                               else loss for i, loss in enumerate(losses))
                        candidate = (totals[mask], mask.bit_count(),
                                     (threshold, lo, hi, category, destination))
                        if best is None or candidate < best:
                            best = candidate
    threshold, lo, hi, category, destination = best[2]
    return {'urgent_threshold': threshold, 'review_band': [lo, hi],
            'min_category_prob': category, 'min_destination_prob': destination}


def point(preds, labels, reports, policies, thresholds):
    values = []
    for policy in policies:
        changed = replace(policy, thresholds={**policy.thresholds, preds[0].approach: thresholds})
        rows = decision_rows(preds, labels, reports, changed)
        values.append((operating_statistics(rows), sum(r['missed_urgent'] for r in rows),
                       sum(r['cost'] for r in rows)))
    return {'review_rate': values[0][0]['review_rate'], 'missed_urgent': values[0][1],
            'cost_v1': values[0][2], 'cost_v2': values[1][2],
            'urgent_threshold': thresholds['urgent_threshold'], 'band': thresholds['review_band']}


def curve(root, split):
    if split not in ('validation', 'test'):
        raise ValueError('curve supports validation or test only')
    policies = [load_policy(root / f'policies/{v}.json') for v in ('v1', 'v2')]
    if split == 'test' and not all(p.frozen for p in policies):
        raise ValueError('test curve requires both Policies frozen')
    reports, _ = split_reports(root, split)
    labels = load_labels(split, 'final' if split == 'test' else 'seeded', root)
    cached = cached_predictions(root, split, reports)
    output = {}
    for a, preds in cached.items():
        if not preds:
            raise ValueError('curve requires nonempty Predictions')
        points = []
        # Half-width 0..0.95 at 0.05 increments; clip symmetric bands at [0, 1].
        for policy in policies:
            for threshold in GRID:
                for width in (0, *GRID):
                    band = [round(max(0, threshold - width), 4),
                            round(min(1, threshold + width), 4)]
                    thresholds = {**policy.thresholds[a], 'urgent_threshold': threshold,
                                  'review_band': band}
                    points.append({**point(preds, labels, reports, policies, thresholds),
                                   'sweep_policy': policy.version, 'chosen': False})
            points.append({**point(preds, labels, reports, policies, policy.thresholds[a]),
                           'sweep_policy': policy.version, 'chosen': True})
        output[a] = points
    write_json(root / f'results/curve_{split}.json', output)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--policy', choices=['v1', 'v2'])
    mode.add_argument('--curve', choices=['validation', 'test'])
    parser.add_argument('--split', default='validation', help='tuning accepts validation only')
    parser.add_argument('--freeze', action='store_true')
    parser.add_argument('--root', type=Path, default=Path('.'))
    args = parser.parse_args(argv)
    if args.curve:
        if args.freeze:
            parser.error('--freeze requires --policy')
        curve(args.root, args.curve)
        return
    if args.split != 'validation':
        parser.error('tuning accepts validation only')
    path = args.root / f'policies/{args.policy}.json'
    policy = load_policy(path)
    reports, _ = split_reports(args.root, 'validation')
    cached = cached_predictions(args.root, 'validation', reports)
    if any(not preds for preds in cached.values()):
        raise ValueError('tuning requires nonempty validation Predictions')
    raw = json.loads(path.read_text(encoding='utf-8'))
    for a, preds in cached.items():
        raw['thresholds'][a] = tune_thresholds(
            preds, load_labels('validation', 'seeded', args.root), policy)
    raw['frozen'] = args.freeze
    raw.pop('frozen_on', None)
    if args.freeze:
        raw['frozen_on'] = {'split': 'validation', 'predictions_sha256': {
            f'results/predictions/{a}_validation.jsonl': hashlib.sha256(
                (args.root / f'results/predictions/{a}_validation.jsonl').read_bytes()).hexdigest()
            for a in cached}}
    write_json(path, raw)


if __name__ == '__main__':
    main()
