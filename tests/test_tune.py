import hashlib
import json
from dataclasses import replace

import pytest

from eval import tune
from triage.policy import load_policy
from triage.schema import load_predictions

from .test_evaluate import blind_rows
from .test_evaluate import workspace as eval_workspace

workspace = eval_workspace


def test_tuning_cost_then_review_then_lexicographic(workspace):
    labels = tune.load_labels('validation', 'seeded', workspace)
    preds = load_predictions(workspace / 'results/predictions/A_validation.jsonl')
    policy = load_policy(workspace / 'policies/v1.json')
    # All are urgent/routine as predicted at .05 except the last (routine at .9).
    # Reviewing just that last report is impossible without reviewing the urgent .9 too.
    # With no forcing triggers best cost is 2 (one false alarm), zero Review; smallest tuple.
    got = tune.tune_thresholds(preds, labels, policy)
    assert got == {'urgent_threshold': .05, 'review_band': [.05, .05],
                   'min_category_prob': 0, 'min_destination_prob': 0}
    # A .05 urgent report is correct at the lowest threshold. A nonempty band at .05
    # would incur Review cost, so the empty-band convention affects the optimum.
    assert tune.tune_thresholds([replace(preds[0], urgent_prob=.05)], labels, policy) == got
    # Two equal probabilities: one correct urgent plus one false alarm costs 2;
    # reviewing both also costs 2. The lower Review rate must win that cost tie.
    tied = [replace(preds[0], urgent_prob=.1), replace(preds[3], urgent_prob=.1)]
    assert tune.tune_thresholds(tied, labels, policy) == got
    # If false alarms are more expensive, four Reviews beat the false alarm.
    expensive = replace(policy, costs={**policy.costs, 'false_alarm': 10})
    assert tune.tune_thresholds(preds, labels, expensive) == {
        'urgent_threshold': .05, 'review_band': [.05, .9],
        'min_category_prob': 0, 'min_destination_prob': 0}


def test_refuses_test_tuning_and_unfrozen_test_curve(workspace):
    with pytest.raises(SystemExit, match='2'):
        tune.main(['--policy', 'v1', '--split', 'test', '--root', str(workspace)])
    with pytest.raises(ValueError, match='both Policies frozen'):
        tune.curve(workspace, 'test')
    tune.curve(workspace, 'validation')
    points = json.loads((workspace / 'results/curve_validation.json').read_text())['A']
    chosen = [p for p in points if p['chosen']]
    assert [(p['sweep_policy'], p['review_rate'], p['missed_urgent'],
             p['cost_v1'], p['cost_v2']) for p in chosen] == [
                 ('v1', 0, 1, 22, 102), ('v2', 0, 1, 22, 102)]


def test_freeze_provenance_and_unfreeze(workspace):
    tune.main(['--policy', 'v1', '--freeze', '--root', str(workspace)])
    raw = json.loads((workspace / 'policies/v1.json').read_text())
    assert raw['frozen'] is True
    name = 'results/predictions/A_validation.jsonl'
    assert raw['frozen_on'] == {'split': 'validation', 'predictions_sha256': {
        name: hashlib.sha256((workspace / name).read_bytes()).hexdigest()}}
    assert raw['thresholds']['A']['urgent_threshold'] == .05
    tune.main(['--policy', 'v1', '--root', str(workspace)])
    raw = json.loads((workspace / 'policies/v1.json').read_text())
    assert raw['frozen'] is False
    assert 'frozen_on' not in raw
    tune.main(['--policy', 'v1', '--freeze', '--root', str(workspace)])
    tune.main(['--policy', 'v2', '--freeze', '--root', str(workspace)])
    tune.write_json(workspace / 'data/labels/blind_test.json', blind_rows(workspace))
    tune.curve(workspace, 'test')
    points = json.loads((workspace / 'results/curve_test.json').read_text())['A']
    assert sum(p['chosen'] for p in points) == 2
