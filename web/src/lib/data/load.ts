import { asset } from '$app/paths';
import type { CurveFile, IncidentsFile, ResultsFile } from './types';

// One request per file per session; every page that needs a file shares the promise.
const cache = new Map<string, Promise<unknown>>();

export function loadJson<T>(name: string): Promise<T> {
	let p = cache.get(name);
	if (!p) {
		p = fetch(asset(`/data/${name}`)).then((r) => {
			if (!r.ok) throw new Error(`${name}: HTTP ${r.status}`);
			return r.json();
		});
		p.catch(() => cache.delete(name));
		cache.set(name, p);
	}
	return p as Promise<T>;
}

export const loadIncidents = () => loadJson<IncidentsFile>('incidents.json');
export const loadResults = () => loadJson<ResultsFile>('results.json');
export const loadCurve = () => loadJson<CurveFile>('curve.json');
