// The label guide's quick-reference table, copied from docs/label-guide.md at build time so the
// Labeller always shows the guide the Labels are defined by. It holds rules only: no Label,
// Scenario or prediction.
import guide from '../../../docs/label-guide.md?raw';

/** Text with `code` spans marked, so they can be set in bold. */
export type Rich = { text: string; code: boolean }[];
export interface GuideRow {
	step: string;
	rule: string;
	decide: Rich;
}

const rich = (s: string): Rich =>
	s.split('`').map((text, i) => ({ text, code: i % 2 === 1 })).filter((x) => x.text);

const section = guide.split('## 1. Quick reference')[1]?.split('\n## ')[0] ?? '';

export const CATEGORY_CODES: Rich = rich(
	(section.match(/Category codes:([\s\S]*?)\n\n/)?.[1] ?? '').replace(/\s+/g, ' ').trim()
);

export const QUICK_REFERENCE: GuideRow[] = section
	.split('\n')
	.filter((l) => l.startsWith('|') && !/^\|\s*-/.test(l) && !/^\|\s*Step\s*\|/.test(l))
	.map((l) => {
		const [step, rule, decide] = l.split('|').slice(1, -1).map((c) => c.trim());
		return { step, rule: rule.replaceAll('`', ''), decide: rich(decide ?? '') };
	});
