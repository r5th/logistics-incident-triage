"""Evaluate cached Predictions against Seeded Labels or final test Labels, without API calls."""

import argparse
import json
import sys
from pathlib import Path

# Support both direct script execution and namespace-package imports in tests.
if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from eval.metrics import classification, cluster_bootstrap, percentile, ratio
from triage.policy import AUTO, REVIEW, load_policy, predicted_urgency, routing_mode
from triage.schema import (
    Category,
    Destination,
    Label,
    load_predictions,
    load_reports,
    load_scenarios,
)
from triage.typesafe_ai import PRICE_PER_MTOK_INPUT_USD


def write_json(path, value):
    def rounded(obj):
        if isinstance(obj, float):
            return round(obj, 4)
        if isinstance(obj, dict):
            return {k: rounded(v) for k, v in obj.items()}
        if isinstance(obj, (list, tuple)):
            return [rounded(v) for v in obj]
        return obj
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(rounded(value), sort_keys=True, indent=2) + "\n",
                    encoding="utf-8", newline="\n")


def split_reports(root, split):
    scenarios = {s.scenario_id: s for s in load_scenarios(root / 'data/scenarios.jsonl')}
    reports = {r.report_id: r for r in load_reports(root / 'data/reports.jsonl')
               if scenarios[r.scenario_id].split == split}
    return reports, scenarios


def label_from_row(row):
    if row['urgency'] not in ('urgent', 'routine'):
        raise ValueError('invalid Urgency')
    return Label(Category(row['category']), row['urgency'], Destination(row['destination']))


def load_labels(split, source, root=Path('.')):
    root = Path(root)
    reports, scenarios = split_reports(root, split)
    if source == 'seeded':
        return {rid: scenarios[r.scenario_id].label for rid, r in reports.items()}
    if source != 'final' or split != 'test':
        raise ValueError('final Labels are test only; source must be seeded or final')
    directory = root / 'data/labels'
    adjudicated = directory / 'adjudicated_test.json'
    blind = directory / 'blind_test.json'
    if adjudicated.exists():
        rows = json.loads(adjudicated.read_text(encoding='utf-8'))
    elif blind.exists():
        rows = [r for r in json.loads(blind.read_text(encoding='utf-8')) if r['pass'] == 1]
    else:
        raise ValueError('final Labels require adjudicated_test.json or blind_test.json pass 1')
    labels = {}
    for row in rows:
        rid = row['report_id']
        if rid not in reports or rid in labels:
            raise ValueError(f'unknown or duplicate final Label: {rid}')
        labels[rid] = label_from_row(row)
    if set(labels) != set(reports):
        raise ValueError('final Labels do not cover every test Incident Report')
    return labels


def cached_predictions(root, split, reports):
    cached = {}
    for approach in 'ABC':
        path = root / f'results/predictions/{approach}_{split}.jsonl'
        if path.exists():
            preds = sorted(load_predictions(path), key=lambda p: p.report_id)
            if (len(preds) != len(reports) or {p.report_id for p in preds} != set(reports)
                    or any(p.approach != approach for p in preds)):
                raise ValueError(f'{path.name}: Predictions must cover the split exactly once')
            cached[approach] = preds
    if not cached:
        raise ValueError(f'no cached Predictions for {split}')
    return cached


def decision_rows(predictions, labels, reports, policy):
    rows = []
    for pred in predictions:
        label = labels[pred.report_id]
        mode, triggers = routing_mode(pred, policy)
        urgency = predicted_urgency(pred, policy)
        terms = dict.fromkeys(policy.costs, 0)
        missed = mode == AUTO and label.urgency == 'urgent' and urgency == 'routine'
        if mode == REVIEW:
            terms['review'] = policy.costs['review']
        else:
            terms['missed_urgent'] = policy.costs['missed_urgent'] * missed
            terms['false_alarm'] = policy.costs['false_alarm'] * (
                label.urgency == 'routine' and urgency == 'urgent')
            if pred.destination != label.destination:
                terms['wrong_destination'] = policy.costs['wrong_destination']
            elif pred.category != label.category:
                terms['wrong_category_same_destination'] = policy.costs[
                    'wrong_category_same_destination']
        rows.append({'report_id': pred.report_id,
                     'scenario_id': reports[pred.report_id].scenario_id,
                     'review': mode == REVIEW, 'urgent': label.urgency == 'urgent',
                     'predicted_urgent': urgency == 'urgent', 'missed_urgent': missed,
                     'auto_error': mode == AUTO and (pred.category != label.category
                         or pred.destination != label.destination or urgency != label.urgency),
                     'cost_terms': terms, 'cost': sum(terms.values()), 'triggers': triggers})
    return rows


def operating_statistics(rows):
    n = len(rows)
    reviews = sum(r['review'] for r in rows)
    return {'urgent_recall': ratio(sum(r['urgent'] and r['predicted_urgent'] for r in rows),
                                   sum(r['urgent'] for r in rows)),
            'review_rate': ratio(reviews, n),
            'auto_routed_error_rate': ratio(sum(r['auto_error'] for r in rows), n - reviews),
            'cost_per_100': ratio(sum(r['cost'] for r in rows) * 100, n)}


def evaluate(preds, labels, reports, policy):
    rows = decision_rows(preds, labels, reports, policy)
    stats = operating_statistics(rows)
    n = len(preds)
    tp = sum(r['urgent'] and r['predicted_urgent'] for r in rows)
    fp = sum(not r['urgent'] and r['predicted_urgent'] for r in rows)
    fn = sum(r['urgent'] and not r['predicted_urgent'] for r in rows)
    result = {decision: classification(
        [getattr(labels[p.report_id], decision) for p in preds],
        [getattr(p, decision) for p in preds], [e.value for e in enum])
        for decision, enum in [('category', Category), ('destination', Destination)]}
    result.update({
        'n': n,
        'urgency': {'recall': stats['urgent_recall'], 'precision': ratio(tp, tp + fp),
                    'counts': {'tp': tp, 'fp': fp, 'fn': fn, 'tn': n - tp - fp - fn}},
        'routing': {'review_rate': stats['review_rate'],
                    'auto_route_coverage': ratio(sum(not r['review'] for r in rows), n),
                    'auto_routed_error_rate': stats['auto_routed_error_rate'],
                    'missed_urgent_count': sum(r['missed_urgent'] for r in rows),
                    'missed_urgent': [
                        {'report_id': p.report_id, 'scenario_id': r['scenario_id'],
                         'text': reports[p.report_id].text[:160], 'urgent_prob': p.urgent_prob,
                         'triggers': r['triggers'] + p.triggers}
                        for p, r in zip(preds, rows, strict=True) if r['missed_urgent']]},
        'cost': {'total': sum(r['cost'] for r in rows), 'per_100': stats['cost_per_100'],
                 'terms': {term: {'total': sum(r['cost_terms'][term] for r in rows),
                                  'per_100': ratio(
                                      100 * sum(r['cost_terms'][term] for r in rows), n)}
                           for term in policy.costs}},
        'reliability': {'error_count': sum(p.error is not None for p in preds),
                        'invalid_output_count': sum('invalid_output' in p.triggers for p in preds),
                        'mean_attempts': ratio(sum(p.attempts for p in preds), n)},
        'latency': {'p50': percentile([p.latency_ms for p in preds], 50),
                    'p95': percentile([p.latency_ms for p in preds], 95),
                    'max': max((p.latency_ms for p in preds), default=None), 'n': n},
        'tokens': {'mean_input': ratio(sum(p.input_tokens for p in preds), n),
                   'mean_output': ratio(sum(p.output_tokens for p in preds), n)},
        'api_cost_per_1000_usd': ratio(sum(p.input_tokens for p in preds), n)
            * PRICE_PER_MTOK_INPUT_USD / 1000,
        'bootstrap_95_ci': cluster_bootstrap(rows, operating_statistics)})
    return result


def table(headers, rows):
    def cell(value):
        return str(value).replace('|', '\\|').replace('\n', ' ').replace('\r', ' ')
    return '\n'.join(['| ' + ' | '.join(map(cell, headers)) + ' |',
                      '| ' + ' | '.join('---' for _ in headers) + ' |'] +
                     ['| ' + ' | '.join(map(cell, row)) + ' |' for row in rows])


def markdown(results):
    lines = ['# Evaluation', '', '## How to read this', '',
             ('Each Incident Report has a Category, Urgency and Destination. A Policy chooses '
             'Auto-route or Review. Missed Urgent counts urgent Incident Reports auto-routed '
             'as routine. Costs are reviewer-minute equivalents; intervals resample whole '
             'Scenarios (1,000 draws, 95%). Urgency recall ignores Routing Mode. Undefined '
             'ratios are zero; unavailable percentiles are null. Latency is in milliseconds '
             'using nearest-rank percentiles. API cost uses cached input tokens.'), '']
    summary = []
    for a, policies in results.items():
        for v, m in policies.items():
            summary.append([a, v, m['category']['accuracy'], m['destination']['accuracy'],
                            m['urgency']['recall'], m['routing']['review_rate'],
                            m['routing']['auto_route_coverage'],
                            m['routing']['auto_routed_error_rate'],
                            m['routing']['missed_urgent_count'], m['cost']['per_100']])
    lines += [table(['Approach', 'Policy', 'Category accuracy', 'Destination accuracy',
                     'Urgent recall', 'Review rate', 'Auto-route coverage', 'Auto-route error rate',
                     'Missed Urgent', 'Cost / 100'], summary), '']
    for a, policies in results.items():
        for v, m in policies.items():
            lines += [f'## {a} / {v}', '']
            for decision, enum in [('category', Category), ('destination', Destination)]:
                labels = [e.value for e in enum]
                lines += [f'### {decision.title()}', '',
                          f"Macro-F1: {m[decision]['macro_f1']}", '',
                          table(['Label', 'Precision', 'Recall', 'F1'],
                                [[label, *[m[decision]['per_class'][label][k]
                                           for k in ('precision', 'recall', 'f1')]]
                                 for label in labels]), '',
                          'Confusion matrix: rows are Labels; columns are Predictions.', '',
                          table(['Label / Prediction', *labels],
                                [[label, *[m[decision]['confusion_matrix'][label][p]
                                           for p in labels]] for label in labels]), '']
            lines += ['### Urgency, reliability and tokens', '',
                      table(['Measure', 'Value'],
                            [[f'Urgency {k}', m['urgency'][k]] for k in ('recall', 'precision')]
                            + [[f'Urgency count {k}', v]
                               for k, v in m['urgency']['counts'].items()]
                            + [[f'Reliability {k}', v] for k, v in m['reliability'].items()]
                            + [[f'Tokens {k}', v] for k, v in m['tokens'].items()]), '']
            lines += ['### Missed Urgent', '', table(
                ['Report', 'Scenario', 'Text', 'Urgent probability', 'Review Triggers'],
                [[r['report_id'], r['scenario_id'], r['text'], r['urgent_prob'],
                  ', '.join(r['triggers'])] for r in m['routing']['missed_urgent']]), '',
                '### Latency and cost', '', table(['Measure', 'Value'],
                [[f'Latency {k}', val] for k, val in m['latency'].items()] +
                [[f'Cost {k}', val] for k, val in m['cost'].items() if k != 'terms'] +
                [['API USD / 1,000', m['api_cost_per_1000_usd']]]), '',
                table(['Cost term', 'Total', 'Per 100'],
                      [[k, val['total'], val['per_100']] for k, val in m['cost']['terms'].items()]),
                '', table(['Bootstrap measure', '95% interval'],
                          m['bootstrap_95_ci'].items()), '']
    return '\n'.join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--split', choices=['build', 'validation', 'test'], required=True)
    parser.add_argument('--labels', choices=['seeded', 'final'], required=True)
    parser.add_argument('--root', type=Path, default=Path('.'))
    args = parser.parse_args(argv)
    reports, _ = split_reports(args.root, args.split)
    labels = load_labels(args.split, args.labels, args.root)
    cached = cached_predictions(args.root, args.split, reports)
    policies = [load_policy(args.root / f'policies/{v}.json') for v in ('v1', 'v2')]
    result = {a: {p.version: evaluate(preds, labels, reports, p) for p in policies}
              for a, preds in cached.items()}
    stem = f'{args.split}_{args.labels}'
    out = args.root / 'results'
    write_json(out / f'metrics_{stem}.json', result)
    rounded = json.loads((out / f'metrics_{stem}.json').read_text(encoding='utf-8'))
    (out / f'report_{stem}.md').write_text(markdown(rounded), encoding='utf-8', newline='\n')


if __name__ == '__main__':
    main()
