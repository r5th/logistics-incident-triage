// The approach (A/B/C) and Policy (v1/v2) the Queue, detail and Results show. They live in the
// URL (?a=B&p=v2) so a shared link or a reload shows the same thing.
import { goto } from '$app/navigation';
import { page } from '$app/state';
import type { Approach, PolicyVersion } from './data/types';

export const DEFAULT_APPROACH: Approach = 'C';
export const DEFAULT_POLICY: PolicyVersion = 'v1';

class ViewContext {
	// Prerendering cannot read query strings, and the first client render must match the
	// prerendered HTML, so the URL is only read once the app has mounted.
	mounted = $state(false);

	get approach(): Approach {
		if (!this.mounted) return DEFAULT_APPROACH;
		const a = page.url.searchParams.get('a');
		return a === 'A' || a === 'B' || a === 'C' ? a : DEFAULT_APPROACH;
	}

	get policy(): PolicyVersion {
		if (!this.mounted) return DEFAULT_POLICY;
		const p = page.url.searchParams.get('p');
		return p === 'v1' || p === 'v2' ? p : DEFAULT_POLICY;
	}

	/** Query string to carry the current choice onto a link ('' for the defaults). */
	get query(): string {
		return queryFor(this.approach, this.policy);
	}

	set(next: { approach?: Approach; policy?: PolicyVersion }) {
		const url = new URL(page.url);
		const q = queryFor(next.approach ?? this.approach, next.policy ?? this.policy);
		url.search = q;
		goto(url, { replaceState: true, keepFocus: true, noScroll: true });
	}
}

function queryFor(a: Approach, p: PolicyVersion): string {
	const q = new URLSearchParams();
	if (a !== DEFAULT_APPROACH) q.set('a', a);
	if (p !== DEFAULT_POLICY) q.set('p', p);
	const s = q.toString();
	return s ? `?${s}` : '';
}

export const view = new ViewContext();
