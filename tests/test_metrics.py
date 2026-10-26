import pytest

from eval.metrics import agreement, classification, cluster_bootstrap, percentile


def test_kappa_known_two_by_two():
    # Matrix [[20, 5], [10, 15]]: observed=35/50=.7;
    # chance=(25*30+25*20)/50**2=.5; kappa=(.7-.5)/(1-.5)=.4.
    result = agreement(['a'] * 25 + ['b'] * 25,
                       ['a'] * 20 + ['b'] * 5 + ['a'] * 10 + ['b'] * 15)
    assert result['kappa'] == pytest.approx(.4)
    assert result['raw_agreement'] == .7
    assert result['n'] == 50
    assert agreement(['a'], ['a']) == {'kappa': None, 'raw_agreement': 1, 'n': 1}


def test_nearest_rank_p95():
    assert percentile(list(range(1, 21)), 95) == 19
    assert percentile([5, 1, 3, 2], 50) == 2


def test_classification_fixed_order_and_hand_computed_values():
    result = classification(['a', 'a', 'b'], ['a', 'b', 'b'], ['b', 'a', 'c'])
    assert result['accuracy'] == pytest.approx(2 / 3)
    assert result['macro_f1'] == pytest.approx(4 / 9)
    assert result['per_class']['a'] == {'precision': 1, 'recall': .5, 'f1': 2 / 3}
    assert result['confusion_matrix'] == {
        'b': {'b': 1, 'a': 0, 'c': 0}, 'a': {'b': 1, 'a': 1, 'c': 0},
        'c': {'b': 0, 'a': 0, 'c': 0}}
    assert list(result['confusion_matrix']) == ['b', 'a', 'c']


def test_bootstrap_draws_whole_scenarios_with_multiplicity_and_fixed_seed():
    rows = [{'scenario_id': 'a', 'value': v} for v in [1, 2, 3]] + [
        {'scenario_id': 'b', 'value': 9}]
    observed = []

    def statistic(sample):
        observed.append(sorted(r['value'] for r in sample))
        return {'mean': sum(r['value'] for r in sample) / len(sample)}

    first = cluster_bootstrap(rows, statistic)
    assert first == {'mean': [2, 9]}
    assert len(observed) == 1000
    assert {tuple(s) for s in observed} == {
        (1, 1, 2, 2, 3, 3), (1, 2, 3, 9), (9, 9)}
    draws = observed.copy()
    observed.clear()
    assert cluster_bootstrap(rows, statistic) == {'mean': [2, 9]}
    assert observed == draws
