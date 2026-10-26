import { readFileSync } from 'node:fs';
import type { EntryGenerator } from './$types';

// Prerender one page per report in the exported incidents.json (read at build time).
export const entries: EntryGenerator = () => {
	try {
		const data = JSON.parse(readFileSync('static/data/incidents.json', 'utf-8'));
		return data.reports.map((r: { id: string }) => ({ id: r.id }));
	} catch {
		return [];
	}
};
