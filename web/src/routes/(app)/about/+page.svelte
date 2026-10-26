<script lang="ts">
	import { incidents } from '$lib/data/store.svelte';
	import { actions } from '$lib/actions.svelte';
	import type { PolicyInfo, PolicyVersion } from '$lib/data/types';
	import Icon from '$lib/components/Icon.svelte';

	const REPO = 'https://github.com/r5th/logistics-incident-triage';
	const COST_ROWS: [keyof PolicyInfo['costs'], string][] = [
		['missed_urgent', 'Missed Urgent (urgent report auto-routed as routine)'],
		['wrong_destination', 'Wrong Destination, auto-routed'],
		['false_alarm', 'Routine report auto-routed as urgent'],
		['wrong_category_same_destination', 'Right Destination, wrong Category'],
		['review', 'Sent to Review']
	];
	const policies = $derived(incidents.data?.policies ?? {});
	const versions = $derived((['v1', 'v2'] as PolicyVersion[]).filter((v) => policies[v]));
	const generators = $derived(incidents.data?.generators.filter((g) => !g.startsWith('fixture')) ?? []);
	let cleared = $state(false);
	const stored = $derived(Object.keys(actions.log).length);
</script>

<svelte:head><title>About · Incident triage</title></svelte:head>

<article class="about">
	<h1>About</h1>
	<p class="lede">
		A prototype that triages Incident Reports for one UK road-freight operator. For each report it decides the Category, the
		Urgency and the Destination team, and whether to Auto-route it or hold it for Review by a person. Triage decides where
		attention goes first. It does not decide the outcome.
	</p>

	<h2>How it decides</h2>
	<p>Three approaches read the same report text and nothing else:</p>
	<ul>
		<li><b>A, rules.</b> Transparent keyword rules, one per rule in the label guide. Fast, free and inspectable.</li>
		<li><b>B, TypeSafe.</b> A model answers typed questions about the report and returns calibrated probabilities, with sentence Evidence.</li>
		<li><b>C, cascade.</b> Uses the rules when they are confident, and TypeSafe otherwise.</li>
	</ul>
	<p>
		A Policy then turns the probabilities into a Routing Mode. Thresholds were chosen on the validation split to minimise
		each Policy's total cost, then frozen before the one test run. Every decision shows its Evidence: sentences quoted
		verbatim from the report.
	</p>

	<h2>Policy costs</h2>
	<p>Costs are in reviewer-minute equivalents. Policies v1 and v2 differ only in what a Missed Urgent costs.</p>
	{#if versions.length}
		<div class="table-wrap">
			<table>
				<thead><tr><th scope="col">Error</th>{#each versions as v (v)}<th scope="col" class="num-col">Policy {v}</th>{/each}</tr></thead>
				<tbody>
					{#each COST_ROWS as [key, label] (key)}
						<tr><th scope="row">{label}</th>{#each versions as v (v)}<td class="num num-col">{policies[v]?.costs[key]}</td>{/each}</tr>
					{/each}
				</tbody>
			</table>
		</div>
		{#each versions as v (v)}
			{#if !policies[v]?.frozen}<p class="muted small">Policy {v} thresholds are not frozen yet.</p>{/if}
		{/each}
	{:else if incidents.error}
		<p class="muted">The Policy tables did not load. Reload the page to try again.</p>
	{:else}
		<p class="muted" aria-busy="true">Loading Policy tables…</p>
	{/if}

	<h2>Where the data comes from</h2>
	<ul>
		<li>Every Incident Report is <b>synthetic</b>. No real operator, driver or customer is described.</li>
		<li>
			100 Scenarios were written first, each with its Seeded Label and the label-guide rule that decides it, then four
			paraphrases of each were generated{generators.length ? ` by ${generators.join(', ')}` : ''}: 400 reports in all, varying voice,
			length, order and spelling while keeping every fact that decides the Label.
		</li>
		<li>Scenarios are split 50 / 20 / 30 into build, validation and test (200 / 80 / 120 reports), so paraphrases of one incident never cross splits.</li>
		<li>On test, the Label is a Blind Label: given by the author without seeing the Seeded Label or any prediction, using the Labeller screen.</li>
		<li>Predictions are cached with their raw probabilities, so this demo never calls an API and the numbers are the ones the evaluation scripts reproduce.</li>
	</ul>

	<h2>Limitations</h2>
	<ul>
		<li>One model wrote every report, so voice and vocabulary vary less than real reports do.</li>
		<li>Agreement figures compare the author with the Seeded Labels and with themselves hours later. Neither is agreement between two people.</li>
		<li>The test split is 120 reports from 30 Scenarios, so intervals are wide; they resample whole Scenarios.</li>
		<li>Only UK-style roads and depots, one operator, six Categories and six Destinations.</li>
		<li>Reviewer Actions are kept in this browser only. Nothing is dispatched.</li>
	</ul>

	<h2>Attribution</h2>
	<ul>
		<li>Approach B uses <a href="https://typesafe.ai" rel="external">TypeSafe</a>{incidents.data?.models.length ? ` (model ${incidents.data.models.join(', ')})` : ''}.</li>
		<li>Built with SvelteKit. Icons follow Lucide's geometry (ISC licence). Platform rules from Apple's Human Interface Guidelines.</li>
		<li>Code, data, label guide and evaluation: <a href={REPO} rel="external">github.com/r5th/logistics-incident-triage</a>.</li>
	</ul>

	<h2>Reset the demo</h2>
	<p>
		{stored ? `${stored} reports have Reviewer Actions saved in this browser.` : 'No Reviewer Actions are saved in this browser.'}
	</p>
	<button class="btn clear" type="button" disabled={!stored} onclick={() => { actions.clear(); cleared = true; }}><Icon name="undo" />Clear Reviewer Actions</button>
	<p class="muted small" aria-live="polite">{cleared && !stored ? 'Cleared. The Queue shows every Review item as awaiting again.' : ''}</p>
</article>

<style>
	@media (max-width: 599px) {
		.clear {
			min-height: 44px;
		}
	}
	.about {
		max-width: 72ch;
	}
	.lede {
		font-size: var(--t-title-3);
		line-height: 1.5;
		margin-top: var(--s3);
	}
	h2 {
		margin-top: var(--s6);
	}
	ul {
		padding-left: 1.2em;
		margin: 0 0 var(--s3);
	}
	li {
		margin-bottom: var(--s2);
	}
	th[scope='row'] {
		color: var(--text);
		font-weight: 500;
		font-size: var(--t-row);
		white-space: normal;
	}
	.num-col {
		text-align: right;
	}
	.small {
		font-size: var(--t-row);
		margin-top: var(--s2);
	}
</style>
