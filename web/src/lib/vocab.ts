// Display names: GLOSSARY.md terms exactly, sentence case for Categories, defined names for
// Destinations (they are team names).
import type { Approach, Category, Destination, IncidentReport } from './data/types';

export const CATEGORIES: Category[] = [
	'vehicle_breakdown',
	'delivery_delay',
	'shipment_damage',
	'missing_shipment',
	'documentation_issue',
	'safety_incident'
];

export const DESTINATIONS: Destination[] = [
	'fleet_support',
	'customer_desk',
	'claims',
	'security_investigations',
	'compliance',
	'safety_desk'
];

export const CATEGORY_NAME: Record<Category, string> = {
	vehicle_breakdown: 'Vehicle breakdown',
	delivery_delay: 'Delivery delay',
	shipment_damage: 'Shipment damage',
	missing_shipment: 'Missing shipment',
	documentation_issue: 'Documentation issue',
	safety_incident: 'Safety incident'
};

export const DESTINATION_NAME: Record<Destination, string> = {
	fleet_support: 'Fleet Support',
	customer_desk: 'Customer Desk',
	claims: 'Claims',
	security_investigations: 'Security & Investigations',
	compliance: 'Compliance',
	safety_desk: 'Safety Desk'
};

export const APPROACH_NAME: Record<Approach, string> = {
	A: 'Rules',
	B: 'TypeSafe',
	C: 'Cascade'
};

export const APPROACH_LINE: Record<Approach, string> = {
	A: 'A rules: transparent keyword rules, one per label-guide rule',
	B: 'B TypeSafe: a model answers typed questions with probabilities',
	C: 'C cascade: rules first, TypeSafe when the rules are unsure'
};

export const ROLE_NAME: Record<IncidentReport['author_role'], string> = {
	driver: 'Driver',
	depot: 'Depot',
	customer: 'Customer',
	subcontractor: 'Subcontractor'
};

export const CHANNEL_NAME: Record<IncidentReport['channel'], string> = {
	app: 'App',
	email: 'Email',
	phone_transcript: 'Phone transcript'
};

export const p2 = (x: number | null | undefined) => (x == null ? '—' : x.toFixed(2));
export const pct = (x: number | null | undefined) => (x == null ? '—' : `${Math.round(x * 100)}%`);

export function waited(min: number): string {
	if (min < 60) return `${min} min`;
	const h = Math.floor(min / 60);
	const m = min % 60;
	return m ? `${h} h ${m} min` : `${h} h`;
}
