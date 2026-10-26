// Reviewer Actions, kept in this browser only (ADR-0002): nothing is sent anywhere.
// Keyed by approach, Policy and report, because a report in Review under one choice may be
// auto-routed under another.
import type { Approach, Category, Destination, PolicyVersion, Urgency } from './data/types';

export type ActionKind = 'accept' | 'override' | 'escalate';

export interface ReviewerAction {
	kind: ActionKind;
	/** ISO 8601 time the action was logged. */
	at: string;
	note?: string;
	/** Override only: the reviewer's decisions, and what they replaced. */
	to?: { category: Category; urgency: Urgency; destination: Destination };
	from?: { category: Category; urgency: Urgency; destination: Destination };
}

const KEY = 'incident-triage:reviewer-actions:v1';

const keyOf = (a: Approach, p: PolicyVersion, id: string) => `${a}|${p}|${id}`;

class ReviewerActions {
	log = $state<Record<string, ReviewerAction[]>>({});
	loaded = $state(false);

	load() {
		try {
			this.log = JSON.parse(localStorage.getItem(KEY) ?? '{}');
		} catch {
			this.log = {};
		}
		this.loaded = true;
		addEventListener('storage', (e) => {
			if (e.key === KEY) this.log = JSON.parse(e.newValue ?? '{}');
		});
	}

	private save() {
		localStorage.setItem(KEY, JSON.stringify(this.log));
	}

	list(a: Approach, p: PolicyVersion, id: string): ReviewerAction[] {
		return this.log[keyOf(a, p, id)] ?? [];
	}

	last(a: Approach, p: PolicyVersion, id: string): ReviewerAction | undefined {
		return this.list(a, p, id).at(-1);
	}

	add(a: Approach, p: PolicyVersion, id: string, action: Omit<ReviewerAction, 'at'>) {
		const k = keyOf(a, p, id);
		this.log[k] = [...(this.log[k] ?? []), { ...action, at: new Date().toISOString() }];
		this.save();
	}

	undo(a: Approach, p: PolicyVersion, id: string) {
		const k = keyOf(a, p, id);
		const rest = (this.log[k] ?? []).slice(0, -1);
		if (rest.length) this.log[k] = rest;
		else delete this.log[k];
		this.save();
	}

	clear() {
		this.log = {};
		this.save();
	}
}

export const actions = new ReviewerActions();
