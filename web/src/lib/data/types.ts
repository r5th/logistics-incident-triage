/**
 * The JSON the demo reads from `web/static/data/`, written by `eval/export_web.py`
 * (or, until real predictions exist, by `web/scripts/make_fixtures.py` with `fixture: true`).
 * Vocabulary follows GLOSSARY.md; enum values follow `src/triage/schema.py`.
 */

export type Category =
	| 'vehicle_breakdown'
	| 'delivery_delay'
	| 'shipment_damage'
	| 'missing_shipment'
	| 'documentation_issue'
	| 'safety_incident';

export type Destination =
	| 'fleet_support'
	| 'customer_desk'
	| 'claims'
	| 'security_investigations'
	| 'compliance'
	| 'safety_desk';

export type Urgency = 'urgent' | 'routine';
export type RoutingMode = 'auto' | 'review';
export type Approach = 'A' | 'B' | 'C';
export type PolicyVersion = 'v1' | 'v2';
export type Split = 'build' | 'validation' | 'test';

export interface Label {
	category: Category;
	urgency: Urgency;
	destination: Destination;
}

/** A named, inspectable reason a report was sent to Review, in plain words. */
export interface ReviewTrigger {
	name: string;
	detail: string;
	/** "Policy v1" for a threshold, "Approach B" for a trigger the approach raised itself. */
	source: string;
}

/** What one Policy makes of one Prediction. */
export interface PolicyOutcome {
	urgency: Urgency;
	routing_mode: RoutingMode;
	/** Empty when auto-routed. */
	review_triggers: ReviewTrigger[];
}

export interface Decision<T extends string> {
	top: T;
	/** Probability of every value; sums to about 1. */
	probs: Record<T, number>;
}

/** One approach's triage decisions for one Incident Report. */
export interface PredictionEntry {
	category: Decision<Category>;
	urgent_prob: number;
	destination: Decision<Destination>;
	/** Indices into `IncidentReport.sentences` quoted as Evidence. */
	evidence: number[];
	latency_ms: number;
	model: string | null;
	version: string;
	/** Cascade only: whose prediction C used. */
	source: 'A' | 'B' | null;
	error: string | null;
	policies: Partial<Record<PolicyVersion, PolicyOutcome>>;
}

export interface IncidentReport {
	id: string;
	text: string;
	/** `text` split into sentences (verbatim substrings), as the approaches split it. */
	sentences: string[];
	author_role: 'driver' | 'depot' | 'customer' | 'subcontractor';
	channel: 'app' | 'email' | 'phone_transcript';
	/** 24-hour clock time on the demo night shift. */
	received: string;
	/** Minutes between `received` and `IncidentsFile.demo_clock`. */
	waiting_min: number;
	predictions: Partial<Record<Approach, PredictionEntry>>;
	/** Present unless the split's Labels are hidden (test before Blind Labels exist). */
	label?: Label;
}

export interface PolicyThresholds {
	urgent_threshold: number;
	review_band: [number, number];
	min_category_prob: number;
	min_destination_prob: number;
}

export interface PolicyInfo {
	version: PolicyVersion;
	frozen: boolean;
	/** Reviewer-minute equivalents. */
	costs: {
		missed_urgent: number;
		wrong_destination: number;
		false_alarm: number;
		wrong_category_same_destination: number;
		review: number;
	};
	forcing_triggers: string[];
	thresholds: Record<Approach, PolicyThresholds>;
}

/** `incidents.json` */
export interface IncidentsFile {
	fixture: boolean;
	split: Split;
	/** Where `label` comes from; null when Labels are hidden. */
	labels_source: 'seeded' | 'final' | null;
	demo_clock: string;
	approaches: Approach[];
	/** Model ids that wrote the reports (`generator` in data/reports.jsonl). */
	generators: string[];
	/** Model ids that made predictions. */
	models: string[];
	policies: Partial<Record<PolicyVersion, PolicyInfo>>;
	reports: IncidentReport[];
}

// ---------------------------------------------------------------------------------------------
// results.json: `results/metrics_<split>_<labels>.json` from eval/evaluate.py
// (docs/briefs/j2-eval-harness.md step 4), wrapped with where it came from.

export interface ClassMetrics {
	accuracy: number;
	macro_f1?: number;
	per_class?: Record<string, { precision: number; recall: number; f1: number }>;
	confusion_matrix?: Record<string, Record<string, number>>;
}

export interface MissedUrgentCase {
	report_id: string;
	scenario_id: string;
	/** First 160 characters. */
	text: string;
	urgent_prob: number;
	triggers: string[];
}

/** A 95% interval; evaluate.py may write it as a pair or as an object. */
export type Interval = [number, number] | { lo: number; hi: number } | { low: number; high: number };

export interface ApproachPolicyMetrics {
	n: number;
	category: ClassMetrics;
	destination: ClassMetrics;
	urgency: {
		recall: number;
		precision: number;
		predicted_urgent_rate: number;
		false_alarms: number;
		counts?: { tp: number; fp: number; fn: number; tn: number };
	};
	routing: {
		review_rate: number;
		auto_route_coverage: number;
		auto_routed_error_rate: number;
		missed_urgent_count: number;
		missed_urgent: MissedUrgentCase[];
	};
	cost: {
		total: number;
		per_100: number;
		terms: Record<string, { total: number; per_100: number }>;
	};
	reliability?: { error_count: number; invalid_output_count: number; mean_attempts: number };
	latency: { p50: number | null; p95: number | null; max: number | null; n: number };
	tokens: { mean_input: number; mean_output: number };
	api_cost_per_1000_usd: number;
	bootstrap_95_ci?: Partial<
		Record<
			| 'urgent_recall'
			| 'urgent_precision'
			| 'predicted_urgent_rate'
			| 'review_rate'
			| 'auto_routed_error_rate'
			| 'cost_per_100',
			Interval
		>
	>;
}

export type MetricsFile = Partial<
	Record<Approach, Partial<Record<PolicyVersion, ApproachPolicyMetrics>>>
>;

/** `results.json` */
export interface ResultsFile {
	fixture: boolean;
	split: Split | null;
	labels: 'seeded' | 'final' | null;
	/** Repo-relative path of the markdown report, e.g. results/report_test_final.md. */
	report_path: string | null;
	metrics: MetricsFile | null;
}

// ---------------------------------------------------------------------------------------------
// curve.json: `results/curve_<split>.json` from eval/tune.py (J2 step 5), normalised.

export interface CurvePoint {
	review_rate: number;
	missed_urgent: number;
	cost_v1?: number;
	cost_v2?: number;
	urgent_threshold?: number;
	band?: [number, number] | number;
}

/** `curve.json` */
export interface CurveFile {
	fixture: boolean;
	split: Split | null;
	approaches: Partial<
		Record<Approach, { points: CurvePoint[]; v1: CurvePoint | null; v2: CurvePoint | null }>
	>;
}

// ---------------------------------------------------------------------------------------------

/** `labelling.json`: test reports for blind labelling. Ids and text only, by design. */
export interface LabellingFile {
	fixture: boolean;
	seed: number;
	/** Shuffled with `seed`. */
	reports: { id: string; text: string }[];
	/** The fixed seeded sample re-labelled in pass 2. */
	pass2_ids: string[];
}

/** One row of `data/labels/blind_test.json` (J2 brief step 3). */
export interface BlindLabelRow extends Label {
	report_id: string;
	pass: 1 | 2;
	/** ISO 8601, UTC. */
	labelled_at: string;
}
