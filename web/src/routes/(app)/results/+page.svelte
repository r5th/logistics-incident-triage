<script lang="ts">
	import { onMount } from 'svelte';
	import { resolve } from '$app/paths';
	import { loadCurve, loadResults } from '$lib/data/load';
	import type { ApproachPolicyMetrics, Approach, CurveFile, Interval, PolicyVersion, ResultsFile } from '$lib/data/types';
	import { view } from '$lib/context.svelte';
	import { APPROACH_NAME, p2, pct } from '$lib/vocab';
	import Icon from '$lib/components/Icon.svelte';
	import SampleNotice from '$lib/components/SampleNotice.svelte';
	import OperatingChart from '$lib/components/OperatingChart.svelte';

	const REPO = 'https://github.com/r5th/logistics-incident-triage';
	let results = $state<ResultsFile | null>(null);
	let curve = $state<CurveFile | null>(null);
	let error = $state<string | null>(null);

	onMount(() => {
		Promise.all([loadResults(), loadCurve()])
			.then(([r, c]) => {
				results = r;
				curve = c;
			})
			.catch((e: Error) => (error = e.message));
	});

	const APPROACHES: Approach[] = ['A', 'B', 'C'];
	const POLICIES: PolicyVersion[] = ['v1', 'v2'];
	const m = $derived(results?.metrics ?? null);
	const cols = $derived(
		APPROACHES.filter((a) => m?.[a]).flatMap((a) => POLICIES.filter((p) => m?.[a]?.[p]).map((p) => ({ a, p, x: m![a]![p]! })))
	);

	function interval(i: Interval | undefined): [number, number] | null {
		if (!i) return null;
		if (Array.isArray(i)) return i;
		if ('lo' in i) return [i.lo, i.hi];
		return [i.low, i.high];
	}

	const ms = (v: number | null) => (v == null ? '—' : v < 10 ? `${v.toFixed(1)} ms` : `${Math.round(v)} ms`);
	const usd = (v: number) => (v > 0 && v < 0.01 ? 'under US$0.01' : `US$${v.toFixed(2)}`);

	type RowDef = {
		label: string;
		target?: string;
		value: (x: ApproachPolicyMetrics) => string;
		met?: (x: ApproachPolicyMetrics) => boolean | null;
		ci?: (x: ApproachPolicyMetrics) => Interval | undefined;
		ciFmt?: (v: number) => string;
	};
	// Targets from docs/build-plan.md "Goal".
	const ROWS: RowDef[] = [
		{ label: 'Urgent recall', target: '≥ 0.98', value: (x) => p2(x.urgency.recall), met: (x) => x.urgency.recall >= 0.98, ci: (x) => x.bootstrap_95_ci?.urgent_recall, ciFmt: p2 },
		{ label: 'Missed Urgent', value: (x) => String(x.routing.missed_urgent_count) },
		{ label: 'Review rate', target: '≤ 25%', value: (x) => pct(x.routing.review_rate), met: (x) => x.routing.review_rate <= 0.25, ci: (x) => x.bootstrap_95_ci?.review_rate, ciFmt: pct },
		{ label: 'Auto-routed error rate', value: (x) => pct(x.routing.auto_routed_error_rate), ci: (x) => x.bootstrap_95_ci?.auto_routed_error_rate, ciFmt: pct },
		{ label: 'Category accuracy', value: (x) => pct(x.category.accuracy) },
		{ label: 'Destination accuracy', value: (x) => pct(x.destination.accuracy) },
		{ label: 'Cost per 100 reports', value: (x) => `${x.cost.per_100.toFixed(1)} min`, ci: (x) => x.bootstrap_95_ci?.cost_per_100, ciFmt: (v) => v.toFixed(1) },
		{ label: 'p95 latency', target: '< 1 s', value: (x) => ms(x.latency.p95), met: (x) => (x.latency.p95 == null ? null : x.latency.p95 < 1000) },
		{ label: 'API cost per 1,000', target: '< US$1', value: (x) => usd(x.api_cost_per_1000_usd), met: (x) => x.api_cost_per_1000_usd < 1 }
	];

	const current = $derived(m?.[view.approach]?.[view.policy] ?? null);
	const headline = $derived.by(() => {
		if (!current) return '';
		const checks = ROWS.filter((r) => r.met).map((r) => r.met!(current));
		const met = checks.filter((c) => c === true).length;
		return `Approach ${view.approach} (${APPROACH_NAME[view.approach]}) under Policy ${view.policy}: urgent recall ${p2(current.urgency.recall)}, review rate ${pct(current.routing.review_rate)}, ${current.routing.missed_urgent_count} Missed Urgent. It meets ${met} of ${checks.length} targets.`;
	});
	const missed = $derived(
		APPROACHES.flatMap((a) => (m?.[a]?.[view.policy]?.routing.missed_urgent ?? []).map((c) => ({ a, c })))
	);
	const labelsWord = $derived(results?.labels === 'final' ? 'final (Blind) Labels' : 'Seeded Labels');
</script>

<svelte:head><title>Results · Incident triage</title></svelte:head>

<div class="page-head">
	<h1>Results</h1>
	{#if results?.split}<span class="sub">{results.split} split · scored against {labelsWord} · {cols[0]?.x.n ?? 0} reports</span>{/if}
</div>

{#if error}
	<div class="panel" role="alert"><p>The results did not load ({error}).</p><button class="btn" type="button" onclick={() => location.reload()}>Reload the page</button></div>
{:else if !results}
	<div class="panel" aria-busy="true" aria-label="Loading results"><span class="skeleton" style="width: 60%"></span><span class="skeleton" style="width: 90%"></span><span class="skeleton" style="width: 80%"></span></div>
{:else if !m || !cols.length}
	<div class="panel">
		<h2>No results yet</h2>
		<p class="muted">Run <b>eval/evaluate.py</b>, then <b>eval/export_web.py</b>, and rebuild. Numbers appear here exactly as the scripts write them.</p>
	</div>
{:else}
	{#if results.fixture}<SampleNotice what="numbers" />{/if}
	<p class="headline">{headline}</p>
	{#if results.split !== 'test'}
		<p class="muted small">These are {results.split}-split numbers. The one test run is reported here once it exists.</p>
	{/if}

	<section aria-labelledby="h-sum">
		<h2 id="h-sum">Approaches and Policies against the targets</h2>
		<div class="table-wrap summary">
			<table>
				<thead>
					<tr>
						<th scope="col" rowspan="2">Measure</th>
						{#each APPROACHES.filter((a) => m[a]) as a (a)}
							<th scope="colgroup" colspan={POLICIES.filter((p) => m[a]?.[p]).length} class="grp">{a} {APPROACH_NAME[a]}</th>
						{/each}
					</tr>
					<tr>
						{#each cols as c (c.a + c.p)}<th scope="col" class:cur={c.a === view.approach && c.p === view.policy}>{c.p}</th>{/each}
					</tr>
				</thead>
				<tbody>
					{#each ROWS as r (r.label)}
						<tr>
							<th scope="row">{r.label}{#if r.target}<span class="target">target {r.target}</span>{/if}</th>
							{#each cols as c (c.a + c.p)}
								{@const met = r.met?.(c.x)}
								{@const ci = interval(r.ci?.(c.x))}
								<td class="num" class:cur={c.a === view.approach && c.p === view.policy}>
									<span class="v">{r.value(c.x)}</span>
									{#if met === true}<span class="res met"><Icon name="met" />Met</span>{:else if met === false}<span class="res missed"><Icon name="missed" />Missed</span>{/if}
									{#if ci && r.ciFmt}<span class="ci">{r.ciFmt(ci[0])} to {r.ciFmt(ci[1])}</span>{/if}
								</td>
							{/each}
						</tr>
					{/each}
				</tbody>
			</table>
		</div>
		<p class="muted small">Cost is in reviewer-minutes under each Policy's error costs. Ranges are 95% intervals from resampling whole Scenarios. The highlighted column is the approach and Policy picked in the menu.</p>
	</section>

	<section aria-labelledby="h-curve" class="panel">
		<h2 id="h-curve">Operating points</h2>
		<p class="muted small">Each line sweeps one approach's Review band: more reports sent to Review (right) should mean fewer Missed Urgent (down). {curve?.split ? `From the ${curve.split} split.` : ''}</p>
		<OperatingChart curve={curve?.approaches ?? {}} approach={view.approach} />
	</section>

	<section aria-labelledby="h-missed">
		<h2 id="h-missed">Missed Urgent under Policy {view.policy}</h2>
		{#if !missed.length}
			<p class="panel none"><Icon name="met" />None. No urgent report was auto-routed as routine by any approach.</p>
		{:else}
			<div class="table-wrap">
				<table>
					<thead><tr><th scope="col">Approach</th><th scope="col">Report</th><th scope="col">Urgent probability</th><th scope="col">Routed as</th><th scope="col">Text</th></tr></thead>
					<tbody>
						{#each missed as { a, c } (a + c.report_id)}
							<tr>
								<td>{a}</td>
								<td><a class="rid" href={resolve('/(app)/incident/[id]', { id: c.report_id }) + `?a=${a}&p=${view.policy}`}>{c.report_id}</a></td>
								<td class="num">{p2(c.urgent_prob)}</td>
								<td>Auto-route, routine</td>
								<td class="txt">{c.text}{c.text.length >= 160 ? '…' : ''}</td>
							</tr>
						{/each}
					</tbody>
				</table>
			</div>
		{/if}
	</section>

	<section aria-labelledby="h-lat">
		<h2 id="h-lat">Latency and cost</h2>
		<div class="table-wrap">
			<table>
				<thead><tr><th scope="col">Approach</th><th scope="col">p50</th><th scope="col">p95</th><th scope="col">Max</th><th scope="col">Input tokens per report</th><th scope="col">Output tokens per report</th><th scope="col">API cost per 1,000</th></tr></thead>
				<tbody>
					{#each APPROACHES.filter((a) => m[a]?.[view.policy] ?? m[a]?.v1) as a (a)}
						{@const x = (m[a]?.[view.policy] ?? m[a]?.v1)!}
						<tr>
							<th scope="row">{a} {APPROACH_NAME[a]}</th>
							<td class="num">{ms(x.latency.p50)}</td>
							<td class="num">{ms(x.latency.p95)}</td>
							<td class="num">{ms(x.latency.max)}</td>
							<td class="num">{Math.round(x.tokens.mean_input).toLocaleString('en-GB')}</td>
							<td class="num">{Math.round(x.tokens.mean_output).toLocaleString('en-GB')}</td>
							<td class="num">{usd(x.api_cost_per_1000_usd)}</td>
						</tr>
					{/each}
				</tbody>
			</table>
		</div>
		<p class="muted small">Latency is per report, nearest-rank percentiles. Cascade C counts A's time plus B's when it hands over. Rules cost nothing to run.</p>
	</section>

	{#if results.report_path}
		<p class="report-link">
			<a href="{REPO}/blob/main/{results.report_path}" rel="external">Read the full report on GitHub<Icon name="external" /></a>
			<span class="muted small">Per-class tables, confusion matrices and every cost term, from {results.report_path}.</span>
		</p>
	{/if}
{/if}

<style>
	section {
		margin-top: var(--s6);
	}
	section.panel {
		margin-top: var(--s6);
	}
	.headline {
		font-size: var(--t-title-3);
		font-weight: 600;
		line-height: 1.4;
		max-width: 68ch;
		text-wrap: pretty;
	}
	.small {
		font-size: var(--t-row);
	}
	.summary th[scope='row'] {
		color: var(--text);
		font-size: var(--t-row);
		font-weight: 600;
		white-space: nowrap;
	}
	.summary .grp {
		text-align: center;
		color: var(--text);
		border-left: 1px solid var(--sep);
	}
	.target {
		display: block;
		color: var(--text-2);
		font-weight: 500;
		font-size: var(--t-caption);
	}
	td {
		white-space: nowrap;
		vertical-align: top;
	}
	.cur {
		background: var(--accent-tint);
	}
	th.cur {
		color: var(--text);
	}
	.v {
		font-weight: 650;
		margin-right: var(--s2);
	}
	.res {
		display: inline-flex;
		align-items: center;
		gap: 4px;
		font-size: var(--t-caption);
		font-weight: 650;
	}
	.res.met {
		color: var(--met-text);
	}
	.res.missed {
		color: var(--urgent);
	}
	.ci {
		display: block;
		font-size: var(--t-caption);
		color: var(--text-2);
	}
	.none {
		display: flex;
		gap: var(--s2);
		align-items: center;
		font-size: var(--t-small);
	}
	.txt {
		white-space: normal;
		min-width: 28ch;
		max-width: 60ch;
		color: var(--text-2);
	}
	.rid {
		font-weight: 650;
	}
	.report-link {
		margin-top: var(--s6);
		display: flex;
		flex-direction: column;
		gap: 2px;
	}
	.report-link a {
		display: inline-flex;
		align-items: center;
		gap: 6px;
		font-weight: 600;
		min-height: 44px;
	}
	section.panel :global(.btn-quiet) {
		min-height: 44px;
	}
</style>
