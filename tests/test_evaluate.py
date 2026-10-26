import json
import shutil
from dataclasses import replace
from pathlib import Path

import pytest

from eval import evaluate
from triage.policy import load_policy
from triage.schema import load_predictions, write_predictions

FIXTURES = Path(__file__).parent / 'fixtures/eval'


@pytest.fixture
def workspace(tmp_path):
    (tmp_path / 'data/labels').mkdir(parents=True)
    for name in ('reports', 'scenarios'):
        shutil.copy(FIXTURES / f'{name}.jsonl', tmp_path / f'data/{name}.jsonl')
    shutil.copytree('policies', tmp_path / 'policies')
    for split in ('validation', 'test'):
        preds = [p for p in load_predictions(FIXTURES / 'predictions.jsonl')
                 if p.report_id.startswith(split)]
        write_predictions(tmp_path / f'results/predictions/A_{split}.jsonl', preds)
    for v in ('v1', 'v2'):
        path = tmp_path / f'policies/{v}.json'
        raw = json.loads(path.read_text(encoding='utf-8'))
        raw['thresholds'] = {a: {'urgent_threshold': .5, 'review_band': [0, 0],
                                'min_category_prob': 0, 'min_destination_prob': 0} for a in 'ABC'}
        raw['frozen'] = False  # the repo's Policies may be frozen; tests start unfrozen
        raw.pop('frozen_on', None)
        evaluate.write_json(path, raw)
    return tmp_path


def blind_rows(root):
    reports, _ = evaluate.split_reports(root, 'test')
    return [dict(report_id=rid, category='shipment_damage', urgency='routine',
                 destination='claims', labelled_at='2026-10-27', **{'pass': 1}) for rid in reports]


def test_evaluate_hand_computed_and_byte_identical(workspace):
    args = ['--root', str(workspace), '--split', 'validation', '--labels', 'seeded']
    evaluate.main(args)
    paths = [workspace / f'results/{prefix}_validation_seeded.{ext}'
             for prefix, ext in [('metrics', 'json'), ('report', 'md')]]
    before = [p.read_bytes() for p in paths]
    m = json.loads(before[0])['A']['v1']
    assert m['urgency'] == {'recall': .6667, 'precision': .6667,
                            'counts': {'tp': 2, 'fp': 1, 'fn': 1, 'tn': 0}}
    assert m['routing']['missed_urgent_count'] == 1
    assert m['routing']['auto_routed_error_rate'] == .5
    assert m['routing']['missed_urgent'][0]['report_id'] == 'validation-0'
    assert len(m['routing']['missed_urgent'][0]['text']) == 160
    assert m['cost']['total'] == 22
    assert m['cost']['per_100'] == 550
    assert m['latency'] == {'p50': 20, 'p95': 100, 'max': 100, 'n': 4}
    assert m['tokens'] == {'mean_input': 100, 'mean_output': 10}
    assert m['api_cost_per_1000_usd'] == .0042
    assert 'How to read this' in before[1].decode()
    assert '| shipment_damage | 1.0 | 1.0 | 1.0 |' in before[1].decode()
    evaluate.main(args)
    assert [p.read_bytes() for p in paths] == before


def test_label_precedence_and_restrictions(workspace):
    with pytest.raises(ValueError, match='require'):
        evaluate.load_labels('test', 'final', workspace)
    rows = blind_rows(workspace)
    # A later pass must never replace pass 1 for final Labels.
    later = {**rows[0], 'pass': 2, 'urgency': 'urgent'}
    evaluate.write_json(workspace / 'data/labels/blind_test.json', [*rows, later])
    assert evaluate.load_labels('test', 'final', workspace)['test-0'].urgency == 'routine'
    adjudicated = [{**r, 'urgency': 'urgent', 'seeded': {}, 'blind': {}, 'ruling_note': 'U1'}
                   for r in rows]
    evaluate.write_json(workspace / 'data/labels/adjudicated_test.json', adjudicated)
    assert evaluate.load_labels('test', 'final', workspace)['test-0'].urgency == 'urgent'
    assert evaluate.load_labels('test', 'seeded', workspace)['test-3'].urgency == 'routine'
    with pytest.raises(ValueError, match='test only'):
        evaluate.load_labels('validation', 'final', workspace)
    evaluate.write_json(workspace / 'data/labels/adjudicated_test.json', adjudicated[:1])
    with pytest.raises(ValueError, match='cover every'):
        evaluate.load_labels('test', 'final', workspace)


@pytest.mark.parametrize('change,expected', [
    ({}, {'missed_urgent': 20}),
    ({'urgent_prob': .9}, {}),
    ({'destination': 'fleet_support'}, {'missed_urgent': 20, 'wrong_destination': 5}),
    ({'category': 'vehicle_breakdown'}, {'missed_urgent': 20,
                                       'wrong_category_same_destination': 1}),
    ({'error': 'timeout'}, {'review': 1}),
    ({'triggers': ['invalid_output']}, {'review': 1}),
])
def test_cost_terms(workspace, change, expected):
    pred = load_predictions(workspace / 'results/predictions/A_validation.jsonl')[0]
    policy = load_policy(workspace / 'policies/v1.json')
    reports, _ = evaluate.split_reports(workspace, 'validation')
    labels = evaluate.load_labels('validation', 'seeded', workspace)
    row = evaluate.decision_rows([replace(pred, **change)], labels, reports, policy)[0]
    assert row['cost_terms'] == {k: expected.get(k, 0) for k in policy.costs}
    assert row['cost'] == sum(expected.values())
    # Also exercise false_alarm on a routine Label.
    routine = load_predictions(workspace / 'results/predictions/A_validation.jsonl')[3]
    row = evaluate.decision_rows([routine], labels, reports, policy)[0]
    assert row['cost_terms']['false_alarm'] == 2


def test_partial_cache_refused(workspace):
    reports, _ = evaluate.split_reports(workspace, 'validation')
    path = workspace / 'results/predictions/A_validation.jsonl'
    write_predictions(path, load_predictions(path)[:1])
    with pytest.raises(ValueError, match='exactly once'):
        evaluate.cached_predictions(workspace, 'validation', reports)


def test_approach_thresholds_and_empty_band(workspace):
    policy = load_policy(workspace / 'policies/v1.json')
    policy.thresholds['A'].update(urgent_threshold=.95, review_band=[.9, .9])
    pred = load_predictions(workspace / 'results/predictions/A_validation.jsonl')[1]
    from triage.policy import predicted_urgency, routing_mode
    assert predicted_urgency(pred, policy) == 'routine'
    assert predicted_urgency(replace(pred, approach='B'), policy) == 'urgent'
    assert routing_mode(pred, policy) == ('auto', [])
