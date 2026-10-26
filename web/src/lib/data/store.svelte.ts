// Shared, lazily loaded incidents.json for the Queue, detail, Results and About screens.
// The blind-labelling route never touches this module (see routes/label/+page.svelte).
import { loadIncidents } from './load';
import type { IncidentsFile } from './types';

class IncidentsStore {
	data = $state<IncidentsFile | null>(null);
	error = $state<string | null>(null);
	private started = false;

	start() {
		if (this.started) return;
		this.started = true;
		loadIncidents()
			.then((d) => (this.data = d))
			.catch((e: Error) => {
				this.error = e.message;
				this.started = false;
			});
	}
}

export const incidents = new IncidentsStore();
