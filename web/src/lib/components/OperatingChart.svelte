<script lang="ts">
	// Operating-point curve: review rate (x) against Missed Urgent count (y), one line per
	// approach, Policy v1 as a circle and v2 as a square. One y-axis; legend plus direct labels;
	// hover or focus shows a tooltip; a table view carries the same numbers
	// (HIG › Charting data: make every chart accessible, add descriptive text).
	import type { Approach, CurveFile, CurvePoint } from '$lib/data/types';
	import { APPROACH_NAME, pct } from '$lib/vocab';
	import Icon from './Icon.svelte';

	let { curve, approach }: { curve: CurveFile['approaches']; approach: Approach } = $props();

	const W = 640;
	const H = 300;
	const M = { l: 44, r: 40, t: 16, b: 44 };
	const COLORS: Record<Approach, string> = { A: 'var(--series-a)', B: 'var(--series-b)', C: 'var(--series-c)' };

	let asTable = $state(false);
	let tip = $state<{ x: number; y: number; text: string } | null>(null);

	const series = $derived(
		(['A', 'B', 'C'] as Approach[])
			.filter((a) => curve[a])
			.map((a) => {
				const c = curve[a]!;
				const seen: Record<string, CurvePoint> = {};
				for (const pt of c.points) seen[`${pt.review_rate}|${pt.missed_urgent}`] ??= pt;
				const points = Object.values(seen).sort(
					(x, y) => x.review_rate - y.review_rate || y.missed_urgent - x.missed_urgent
				);
				// The sweep varies two thresholds, so many settings share a review rate. The line is
				// the frontier: the fewest Missed Urgent reachable at or below each review rate.
				const front: CurvePoint[] = [];
				for (const p of points) if (!front.length || p.missed_urgent < front.at(-1)!.missed_urgent) front.push(p);
				const xEnd = points.length ? points.at(-1)!.review_rate : 0;
				return { a, points, front, xEnd, v1: c.v1, v2: c.v2 };
			})
	);
	const all = $derived(series.flatMap((s) => [...s.points, ...(s.v1 ? [s.v1] : []), ...(s.v2 ? [s.v2] : [])]));
	const xMax = $derived(Math.min(1, Math.max(0.3, Math.ceil(Math.max(0, ...all.map((p) => p.review_rate)) * 10) / 10)));
	// Whole-number y ticks in even steps: 0, step, 2·step, 3·step, 4·step.
	const yStep = $derived(Math.max(1, Math.ceil(Math.max(0, ...all.map((p) => p.missed_urgent)) / 4)));
	const yMax = $derived(yStep * 4);
	const sx = (v: number) => M.l + (v / xMax) * (W - M.l - M.r);
	const sy = (v: number) => H - M.b - (v / yMax) * (H - M.t - M.b);
	const xTicks = $derived(Array.from({ length: Math.round(xMax * 10) + 1 }, (_, i) => i / 10));
	const yTicks = $derived(Array.from({ length: 5 }, (_, i) => yStep * i));

	// Step line: hold each frontier count until the next review rate that lowers it.
	const path = (pts: CurvePoint[], xEnd: number) =>
		pts
			.map((p, i) => `${i ? `H${sx(p.review_rate).toFixed(1)}V` : `M${sx(p.review_rate).toFixed(1)},`}${sy(p.missed_urgent).toFixed(1)}`)
			.join('') + (pts.length ? `H${sx(xEnd).toFixed(1)}` : '');

	// Direct labels just right of each line's end, stacked upward so they never overlap
	// each other or the Policy marks.
	const ends = $derived.by(() => {
		const e = series
			.filter((s) => s.front.length)
			.map((s) => ({ a: s.a, x: sx(s.xEnd) + 11, y: sy(s.front.at(-1)!.missed_urgent) }))
			.sort((p, q) => q.y - p.y);
		for (let i = 1; i < e.length; i++) if (e[i - 1].y - e[i].y < 14) e[i].y = e[i - 1].y - 14;
		return e;
	});

	const describe = (a: Approach, p: CurvePoint, which?: string) =>
		`${a} ${APPROACH_NAME[a]}${which ? `, Policy ${which}` : ''}: review rate ${pct(p.review_rate)}, ${p.missed_urgent} Missed Urgent`;

	const summary = $derived(
		'Operating points, review rate against Missed Urgent count. ' +
			series
				.map((s) => [s.v1 && describe(s.a, s.v1, 'v1'), s.v2 && describe(s.a, s.v2, 'v2')].filter(Boolean).join('; '))
				.join('. ')
	);

	function show(e: MouseEvent | FocusEvent, text: string) {
		const el = e.currentTarget as SVGElement;
		const box = el.closest('.chart-box')!.getBoundingClientRect();
		const r = el.getBoundingClientRect();
		const sc = el.closest('.chart-scroll')!;
		tip = { x: r.left + r.width / 2 - box.left + sc.scrollLeft, y: r.top - box.top, text };
	}
</script>

<div class="chart-head">
	<ul class="legend" aria-label="Legend">
		{#each series as s (s.a)}
			<li class:current={s.a === approach}><span class="sw-line" style="background: {COLORS[s.a]}"></span>{s.a} {APPROACH_NAME[s.a]}</li>
		{/each}
		<li><svg class="mk" viewBox="0 0 12 12" aria-hidden="true"><circle cx="6" cy="6" r="4.5" fill="var(--text-2)" /></svg>Policy v1</li>
		<li><svg class="mk" viewBox="0 0 12 12" aria-hidden="true"><rect x="1" y="1" width="10" height="10" fill="none" stroke="var(--text-2)" stroke-width="1.6" /></svg>Policy v2</li>
		<li><span class="sw-dash"></span>25% review-rate target</li>
	</ul>
	<button class="btn btn-quiet" type="button" aria-pressed={asTable} onclick={() => (asTable = !asTable)}>
		<Icon name={asTable ? 'chart' : 'table'} />{asTable ? 'Show as chart' : 'Show as table'}
	</button>
</div>

{#if !series.length}
	<p class="empty">No operating-point curve yet. It appears once eval/tune.py has written results/curve_*.json.</p>
{:else if asTable}
	<div class="table-wrap">
		<table>
			<caption class="visually-hidden">Operating points by approach</caption>
			<thead><tr><th scope="col">Approach</th><th scope="col">Review rate</th><th scope="col">Missed Urgent</th><th scope="col">Urgent threshold</th><th scope="col">Review band</th><th scope="col">Policy</th></tr></thead>
			<tbody>
				{#each series as s (s.a)}
					{#each s.points as p, i (i)}
						{@const tag = [s.v1 && s.v1.review_rate === p.review_rate && s.v1.missed_urgent === p.missed_urgent ? 'v1' : '', s.v2 && s.v2.review_rate === p.review_rate && s.v2.missed_urgent === p.missed_urgent ? 'v2' : ''].filter(Boolean).join(', ')}
						<tr>
							<td>{s.a} {APPROACH_NAME[s.a]}</td>
							<td class="num">{pct(p.review_rate)}</td>
							<td class="num">{p.missed_urgent}</td>
							<td class="num">{p.urgent_threshold?.toFixed(2) ?? '—'}</td>
							<td class="num">{Array.isArray(p.band) ? `${p.band[0].toFixed(2)} to ${p.band[1].toFixed(2)}` : (p.band?.toFixed(2) ?? '—')}</td>
							<td>{tag || '—'}</td>
						</tr>
					{/each}
				{/each}
			</tbody>
		</table>
	</div>
{:else}
	<div class="chart-box"><div class="chart-scroll">
		<svg viewBox="0 0 {W} {H}" role="img" aria-labelledby="chart-desc" class="chart" onmouseleave={() => (tip = null)}>
			<desc id="chart-desc">{summary}</desc>
			<g class="grid" aria-hidden="true">
				{#each yTicks as v (v)}
					<line x1={M.l} x2={W - M.r} y1={sy(v)} y2={sy(v)} />
					<text x={M.l - 8} y={sy(v)} dy="0.32em" text-anchor="end">{v}</text>
				{/each}
				{#each xTicks as v (v)}
					<text x={sx(v)} y={H - M.b + 22} text-anchor="middle">{pct(v)}</text>
				{/each}
				<line class="axis" x1={M.l} x2={W - M.r} y1={sy(0)} y2={sy(0)} />
				<text class="axis-title" x={(M.l + W - M.r) / 2} y={H - 6} text-anchor="middle">Review rate</text>
				<text class="axis-title" x={12} y={M.t + (H - M.t - M.b) / 2} text-anchor="middle" transform="rotate(-90 12 {M.t + (H - M.t - M.b) / 2})">Missed Urgent</text>
				{#if xMax >= 0.25}
					<line class="target" x1={sx(0.25)} x2={sx(0.25)} y1={M.t} y2={sy(0)} />
				{/if}
			</g>
			{#each series as s (s.a)}
				<g class="series" class:dim={s.a !== approach} style="--c: {COLORS[s.a]}">
					{#each s.points as p, i (i)}
						<circle class="other" cx={sx(p.review_rate)} cy={sy(p.missed_urgent)} r="2" />
					{/each}
					<path d={path(s.front, s.xEnd)} />
					{#each s.front as p, i (i)}
						<circle class="hit" cx={sx(p.review_rate)} cy={sy(p.missed_urgent)} r="9" role="presentation" onmouseenter={(e) => show(e, describe(s.a, p))} />
						<circle class="dot" cx={sx(p.review_rate)} cy={sy(p.missed_urgent)} r="3" />
					{/each}
					{#if s.v2}
						<rect class="mark2" x={sx(s.v2.review_rate) - 8} y={sy(s.v2.missed_urgent) - 8} width="16" height="16" role="presentation" onmouseenter={(e) => show(e, describe(s.a, s.v2!, 'v2'))} />
					{/if}
					{#if s.v1}
						<circle class="mark" cx={sx(s.v1.review_rate)} cy={sy(s.v1.missed_urgent)} r="5" role="presentation" onmouseenter={(e) => show(e, describe(s.a, s.v1!, 'v1'))} />
					{/if}
				</g>
			{/each}
			{#each ends as e (e.a)}
				<text class="end-label" x={e.x} y={e.y} dy="0.32em" text-anchor="start" aria-hidden="true">{e.a}</text>
			{/each}
		</svg>
		</div>
		{#if tip}
			<div class="tip" role="status" style="left: {tip.x}px; top: {tip.y}px">{tip.text}</div>
		{/if}
	</div>
	<p class="chart-note">Each line is the fewest Missed Urgent reachable at that review rate; faint dots are the other threshold settings swept. A v1 circle inside a v2 square means both Policies chose the same Operating Point.</p>
{/if}

<style>
	.chart-head {
		display: flex;
		justify-content: space-between;
		align-items: flex-start;
		gap: var(--s3);
		flex-wrap: wrap;
		margin-bottom: var(--s2);
	}
	.legend {
		display: flex;
		flex-wrap: wrap;
		gap: var(--s1) var(--s4);
		list-style: none;
		margin: 0;
		padding: 0;
		font-size: var(--t-caption);
		color: var(--text-2);
	}
	.legend li {
		display: inline-flex;
		align-items: center;
		gap: 6px;
		min-height: 24px;
	}
	.legend li.current {
		color: var(--text);
		font-weight: 650;
	}
	.sw-line {
		width: 16px;
		height: 2px;
		border-radius: 1px;
	}
	.sw-dash {
		width: 16px;
		border-top: 1.5px dashed var(--text-2);
	}
	.mk {
		width: 12px;
		height: 12px;
	}
	.chart-box {
		position: relative;
	}
	.chart-scroll {
		overflow-x: auto;
	}
	.chart {
		width: 100%;
		min-width: 560px; /* below this the 12px chart text shrinks past legibility; scroll instead */
		max-width: 760px; /* keeps 12px chart text near 12px on wide screens */
		height: auto;
		display: block;
		overflow: visible;
	}
	.grid line {
		stroke: var(--sep);
		stroke-width: 1;
	}
	.grid .axis {
		stroke: var(--text-2);
	}
	.grid .target {
		stroke: var(--text-2);
		stroke-dasharray: 4 4;
	}
	.grid text {
		fill: var(--text-2);
		font-size: 12px;
		font-variant-numeric: tabular-nums;
	}
	.grid .axis-title {
		font-weight: 600;
	}
	.series path {
		fill: none;
		stroke: var(--c);
		stroke-width: 2;
		stroke-linejoin: round;
	}
	.series .dot {
		fill: var(--c);
		stroke: var(--surface);
		stroke-width: 2;
	}
	.series .other {
		fill: var(--c);
		opacity: 0.28;
	}
	.series .mark2 {
		fill: none;
		stroke: var(--c);
		stroke-width: 2;
		cursor: default;
	}
	.series .hit {
		fill: transparent;
	}
	.series .mark {
		fill: var(--c);
		stroke: var(--surface);
		stroke-width: 2;
		cursor: default;
	}
	.series.dim path,
	.series.dim .dot,
	.series.dim .mark,
	.series.dim .mark2 {
		opacity: 0.55;
	}
	.end-label {
		fill: var(--text);
		font-size: 12px;
		font-weight: 650;
	}
	.tip {
		position: absolute;
		transform: translate(-50%, calc(-100% - 8px));
		background: var(--text);
		color: var(--surface);
		font-size: var(--t-caption);
		font-weight: 600;
		padding: 4px 8px;
		border-radius: 4px;
		white-space: nowrap;
		pointer-events: none;
	}
	.chart-note {
		font-size: var(--t-caption);
		color: var(--text-2);
		margin: var(--s2) 0 0;
	}
	.empty {
		color: var(--text-2);
		font-size: var(--t-small);
	}
</style>
