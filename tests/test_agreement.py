import json

import pytest

from eval import agreement
from eval.evaluate import write_json

from .test_evaluate import blind_rows
from .test_evaluate import workspace as eval_workspace

workspace = eval_workspace


def test_agreement_uses_pass_1_and_paired_pass_2_only(workspace):
    rows = blind_rows(workspace)
    # Seeded urgency urgent,urgent,urgent,routine; blind urgent,routine,urgent,routine.
    rows[0]['urgency'] = rows[2]['urgency'] = 'urgent'
    rows += [{**rows[0], 'pass': 2}, {**rows[1], 'pass': 2, 'urgency': 'urgent'}]
    write_json(workspace / 'data/labels/blind_test.json', rows)
    agreement.main(['--root', str(workspace)])
    result = json.loads((workspace / 'results/agreement.json').read_text())
    # observed=.75, chance=.75*.5+.25*.5=.5 => kappa=.5.
    assert result['seeded_vs_blind_pass_1']['urgency'] == {
        'kappa': .5, 'raw_agreement': .75, 'n': 4}
    assert result['blind_pass_1_vs_pass_2']['urgency'] == {
        'kappa': 0, 'raw_agreement': .5, 'n': 2}
    assert result['seeded_vs_blind_pass_1']['category']['n'] == 4
    assert 'not inter-rater agreement between two people' in (
        workspace / 'results/agreement.md').read_text(encoding='utf-8')
    write_json(workspace / 'data/labels/blind_test.json', rows[1:])
    with pytest.raises(ValueError, match='cover all'):
        agreement.main(['--root', str(workspace)])
