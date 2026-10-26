"""Agreement of Seeded Labels with Blind Labels and of two blind passes by one person."""

import argparse
import json
import sys
from pathlib import Path

if __package__ in (None, ''):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from eval.evaluate import label_from_row, load_labels, table, write_json
from eval.metrics import agreement


def compare(left, right, ids):
    return {decision: agreement([getattr(left[r], decision) for r in ids],
                                [getattr(right[r], decision) for r in ids])
            for decision in ('category', 'urgency', 'destination')}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path('.'))
    args = parser.parse_args(argv)
    seeded = load_labels('test', 'seeded', args.root)
    rows = json.loads((args.root / 'data/labels/blind_test.json').read_text(encoding='utf-8'))
    passes = {1: {}, 2: {}}
    for row in rows:
        rid, number = row['report_id'], row['pass']
        if number not in passes or rid not in seeded or rid in passes[number]:
            raise ValueError('invalid or duplicate Blind Label')
        passes[number][rid] = label_from_row(row)
    if set(passes[1]) != set(seeded):
        raise ValueError('blind pass 1 must cover all test Incident Reports')
    result = {'seeded_vs_blind_pass_1': compare(seeded, passes[1], sorted(seeded)),
              'blind_pass_1_vs_pass_2': compare(passes[1], passes[2],
                                               sorted(passes[1].keys() & passes[2].keys()))}
    out = args.root / 'results'
    write_json(out / 'agreement.json', result)
    result = json.loads((out / 'agreement.json').read_text(encoding='utf-8'))
    lines = ['## Label agreement', '',
             ('These are not inter-rater agreement between two people. Seeded Labels versus '
             'Blind Labels compare the Scenario design with one person’s labelling; blind '
             'pass 1 versus pass 2 measures that person’s repeat agreement. κ is null when '
             'chance agreement is one or there are no paired Labels.'), '']
    for name, decisions in result.items():
        lines += [f'### {name}', '', table(['Decision', 'κ', 'Raw agreement', 'n'],
                  [[d, v['kappa'], v['raw_agreement'], v['n']] for d, v in decisions.items()]), '']
    (out / 'agreement.md').write_text('\n'.join(lines), encoding='utf-8', newline='\n')


if __name__ == '__main__':
    main()
