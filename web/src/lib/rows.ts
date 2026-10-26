// What the current approach and Policy make of each Incident Report, plus any Reviewer Action.
import type { ActionKind, ReviewerAction } from './actions.svelte';
import type {
	Approach,
	Category,
	Destination,
	IncidentReport,
	IncidentsFile,
	PolicyOutcome,
	PolicyVersion,
	PredictionEntry,
	RoutingMode,
	Urgency
} from './data/types';

export interface Row {
	report: IncidentReport;
	pred: PredictionEntry;
	outcome: PolicyOutcome;
	mode: RoutingMode;
	/** Effective decisions: the reviewer's after an override, otherwise the prediction's. */
	category: Category;
	urgency: Urgency;
	destination: Destination;
	status: ActionKind | 'awaiting' | null;
	last?: ReviewerAction;
}

export function rowFor(
	report: IncidentReport,
	a: Approach,
	p: PolicyVersion,
	lastAction: (id: string) => ReviewerAction | undefined
): Row | null {
	const pred = report.predictions[a];
	const outcome = pred?.policies[p];
	if (!pred || !outcome) return null;
	const mode = outcome.routing_mode;
	const last = mode === 'review' ? lastAction(report.id) : undefined;
	const to = last?.kind === 'override' ? last.to : undefined;
	return {
		report,
		pred,
		outcome,
		mode,
		category: to?.category ?? pred.category.top,
		urgency: to?.urgency ?? outcome.urgency,
		destination: to?.destination ?? pred.destination.top,
		status: mode === 'review' ? (last?.kind ?? 'awaiting') : null,
		last
	};
}

export function rowsFor(
	data: IncidentsFile,
	a: Approach,
	p: PolicyVersion,
	lastAction: (id: string) => ReviewerAction | undefined
): Row[] {
	return data.reports.flatMap((r) => rowFor(r, a, p, lastAction) ?? []);
}

/** Highest first: [top value, its probability], then the runner-up. */
export function ranked<T extends string>(probs: Record<T, number>): [T, number][] {
	return (Object.entries(probs) as [T, number][]).sort((x, y) => y[1] - x[1]);
}
