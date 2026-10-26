<script lang="ts">
	import { tick } from 'svelte';
	import { page } from '$app/state';
	import { resolve } from '$app/paths';
	import { incidents } from '$lib/data/store.svelte';
	import { actions, type ReviewerAction } from '$lib/actions.svelte';
	import { view } from '$lib/context.svelte';
	import { rowFor, ranked } from '$lib/rows';
	import type { Category, Destination, PolicyThresholds, Urgency } from '$lib/data/types';
	import {
		CATEGORIES,
		CATEGORY_NAME,
		CHANNEL_NAME,
		DESTINATIONS,
		DESTINATION_NAME,
		ROLE_NAME,
		p2
	} from '$lib/vocab';
	import Icon from '$lib/components/Icon.svelte';
	import DestinationPlate from '$lib/components/DestinationPlate.svelte';
	import ModePlate from '$lib/components/ModePlate.svelte';
	import UrgencyMark from '$lib/components/UrgencyMark.svelte';
	import ActionStatus from '$lib/components/ActionStatus.svelte';
	import SampleNotice from '$lib/components/SampleNotice.svelte';

	const id = $derived(page.params.id ?? '');
	const a = $derived(view.approach);
	const p = $derived(view.policy);
	const report = $derived(incidents.data?.reports.find((r) => r.id === id));
	const row = $derived(report ? rowFor(report, a, p, () => actions.last(a, p, id)) : null);
	const log = $derived(actions.list(a, p, id));
	const t = $derived<PolicyThresholds | undefined>(incidents.data?.policies[p]?.thresholds[a]);

	// Reviewer Action forms (inline, never a modal: direction › what not to do).
	let form = $state<'override' | 'escalate' | null>(null);
	let note = $state('');
	let error = $state('');
	let oCategory = $state<Category>('vehicle_breakdown');
	let oUrgency = $state<Urgency>('routine');
	let oDestination = $state<Destination>('fleet_support');
	let undoBtn = $state<HTMLButtonElement>();
	let firstField = $state<HTMLSelectElement | HTMLTextAreaElement>();

	async function openForm(kind: 'override' | 'escalate') {
		if (!row) return;
		form = kind;
		note = '';
		error = '';
		oCategory = row.category;
		oUrgency = row.urgency;
		oDestination = row.destination;
		await tick();
		firstField?.focus();
	}

	async function logged() {
		form = null;
		await tick();
		undoBtn?.focus();
	}

	function accept() {
		actions.add(a, p, id, { kind: 'accept' });
		logged();
	}

	function saveOverride(e: SubmitEvent) {
		e.preventDefault();
		if (!row) return;
		const from = { category: row.pred.category.top, urgency: row.outcome.urgency, destination: row.pred.destination.top };
		const to = { category: oCategory, urgency: oUrgency, destination: oDestination };
		if (from.category === to.category && from.urgency === to.urgency && from.destination === to.destination) {
			error = 'Change at least one decision, or use Accept and route instead.';
			return;
		}
		if (!note.trim()) {
			error = 'Add a note so the override can be audited.';
			return;
		}
		actions.add(a, p, id, { kind: 'override', note: note.trim(), from, to });
		logged();
	}

	function saveEscalate(e: SubmitEvent) {
		e.preventDefault();
		if (!note.trim()) {
			error = 'Add a note so the receiving team knows why it was escalated.';
			return;
		}
		actions.add(a, p, id, { kind: 'escalate', note: note.trim() });
		logged();
	}

	const clock = (iso: string) => new Date(iso).toLocaleTimeString('en-GB', { hour12: false });

	function actionText(x: ReviewerAction): string {
		if (x.kind === 'accept') return `Accepted and routed to ${row ? DESTINATION_NAME[row.pred.destination.top] : ''}`;
		if (x.kind === 'escalate') return 'Escalated';
		const parts: string[] = [];
		if (x.from && x.to) {
			if (x.from.category !== x.to.category) parts.push(`${CATEGORY_NAME[x.from.category]} → ${CATEGORY_NAME[x.to.category]}`);
			if (x.from.urgency !== x.to.urgency) parts.push(`${x.from.urgency} → ${x.to.urgency}`);
			if (x.from.destination !== x.to.destination) parts.push(`${DESTINATION_NAME[x.from.destination]} → ${DESTINATION_NAME[x.to.destination]}`);
		}
		return `Overrode ${parts.join('; ')}`;
	}

	const evidence = $derived(new Set(row?.pred.evidence ?? []));
	const evidenceList = $derived((row?.pred.evidence ?? []).map((i) => i + 1).join(', ') || 'none');

	const approachEvent = $derived.by(() => {
		if (!row) return '';
		const ms = `${row.pred.latency_ms < 10 ? row.pred.latency_ms.toFixed(1) : Math.round(row.pred.latency_ms)} ms`;
		if (row.pred.error) return `Returned an error: ${row.pred.error}`;
		if (a === 'A') return `Rules decided · ${ms}`;
		if (a === 'B') return `TypeSafe decided · ${ms}`;
		return row.pred.source === 'A'
			? `Rules confident, used the rules · ${ms}`
			: `Rules not confident, sent to TypeSafe · ${ms}`;
	});

	const cat = $derived(row ? ranked(row.pred.category.probs) : []);
	const catLow = $derived(!!t && !!cat[0] && cat[0][1] < t.min_category_prob);
	const up = $derived(row?.pred.urgent_prob ?? 0);
	const inBand = $derived(!!t && up >= t.review_band[0] && up <= t.review_band[1]);
	const dest = $derived(row ? ranked(row.pred.destination.probs) : []);
	const destLow = $derived(!!t && !!dest[0] && dest[0][1] < t.min_destination_prob);

	function onKey(e: KeyboardEvent) {
		if (e.key === 'Escape' && form) {
			form = null;
		}
	}
</script>

					{#snippet bar(top: number, runner: number, tick: number, low: boolean, band?: [number, number])}
						<div class="bar" class:low aria-hidden="true">
							{#if band}<span class="band" style="left: {band[0] * 100}%; width: {(band[1] - band[0]) * 100}%"></span>{/if}
							<i style="width: {top * 100}%"></i>
							{#if runner > 0}<i class="runner" style="width: {runner * 100}%"></i>{/if}
							<b style="left: {tick * 100}%"></b>
						</div>
					{/snippet}
					{#snippet labelLine(match: boolean, text: string)}
						<div class="label-line">
							<Icon name={match ? 'met' : 'missed'} />Label: {text} · {match ? 'matches' : 'differs'}
						</div>
					{/snippet}

<svelte:head><title>{id} · Incident triage</title></svelte:head>
<svelte:window onkeydown={onKey} />

<a class="crumb" href={resolve('/') + view.query}><Icon name="back" />Queue</a>

{#if incidents.error}
	<div class="panel empty" role="alert">
		<p>The reports did not load ({incidents.error}).</p>
		<button class="btn" type="button" onclick={() => location.reload()}>Reload the page</button>
	</div>
{:else if !incidents.data}
	<div aria-busy="true" aria-label="Loading report">
		<h1>{id}</h1>
		<div class="panel" style="margin-top: var(--s5)"><span class="skeleton" style="width: 80%"></span><span class="skeleton" style="width: 65%"></span><span class="skeleton" style="width: 72%"></span></div>
	</div>
{:else if !report}
	<div class="panel empty">
		<h1>{id}</h1>
		<p>There is no report {id} in the {incidents.data.split} split.</p>
		<a class="btn" href={resolve('/') + view.query}>Go back to the Queue</a>
	</div>
{:else if !row}
	<div class="panel empty">
		<h1>{id}</h1>
		<p>Approach {a} has no prediction for this report under Policy {p}. Pick another approach.</p>
	</div>
{:else}
	{#if incidents.data.fixture}<SampleNotice what="reports and predictions" />{/if}

	<header class="detail-head">
		<div>
			<h1 class="num">{report.id}</h1>
			<p class="meta-line">
				{ROLE_NAME[report.author_role]} · {CHANNEL_NAME[report.channel]} · received <span class="num">{report.received}</span> · synthetic
			</p>
			<div class="route" role="group" aria-label="Route">
				<UrgencyMark urgency={row.urgency} large />
				<ModePlate mode={row.mode} large />
				<span class="route-sep" aria-hidden="true"><Icon name="arrow" /></span>
				<DestinationPlate destination={row.destination} large />
			</div>
		</div>
		{#if row.mode === 'review'}
			<div class="head-actions">
				{#if row.last}
					<div class="logged" aria-live="polite">
						<ActionStatus status={row.last.kind} />
						<span class="muted num">at {clock(row.last.at)}</span>
						<button class="btn" type="button" bind:this={undoBtn} onclick={() => actions.undo(a, p, id)}><Icon name="undo" />Undo</button>
					</div>
				{:else}
					<div class="actions">
						<button class="btn btn-primary" type="button" onclick={accept}><Icon name="check" />Accept and route</button>
						<button class="btn" type="button" aria-expanded={form === 'override'} onclick={() => openForm('override')}><Icon name="override" />Override</button>
						<button class="btn" type="button" aria-expanded={form === 'escalate'} onclick={() => openForm('escalate')}><Icon name="escalate" />Escalate</button>
					</div>
				{/if}
				<p class="demo-line">This is a demo: nothing is dispatched. Reviewer Actions stay in this browser.</p>
			</div>
		{/if}
	</header>

	{#if form === 'override'}
		<form class="panel inline-form" onsubmit={saveOverride} aria-labelledby="ov-title" novalidate>
			<h2 id="ov-title">Override the triage decisions</h2>
			<div class="form-grid">
				<div class="field">
					<label for="ov-cat">Category</label>
					<select id="ov-cat" class="select" bind:value={oCategory} bind:this={firstField}>
						{#each CATEGORIES as c (c)}<option value={c}>{CATEGORY_NAME[c]}</option>{/each}
					</select>
				</div>
				<div class="field">
					<label for="ov-urg">Urgency</label>
					<select id="ov-urg" class="select" bind:value={oUrgency}>
						<option value="urgent">Urgent</option>
						<option value="routine">Routine</option>
					</select>
				</div>
				<div class="field">
					<label for="ov-dest">Destination</label>
					<select id="ov-dest" class="select" bind:value={oDestination}>
						{#each DESTINATIONS as d (d)}<option value={d}>{DESTINATION_NAME[d]}</option>{/each}
					</select>
				</div>
			</div>
			<div class="field">
				<label for="ov-note">Note</label>
				<textarea id="ov-note" class="input" bind:value={note} aria-invalid={!!error} aria-describedby="ov-err" placeholder="Why the decisions change"></textarea>
			</div>
			<p id="ov-err" class="err-slot" aria-live="polite">{#if error}<span class="field-error"><Icon name="info" />{error}</span>{/if}</p>
			<div class="actions">
				<button class="btn btn-primary" type="submit">Save override</button>
				<button class="btn" type="button" onclick={() => (form = null)}>Cancel</button>
			</div>
		</form>
	{:else if form === 'escalate'}
		<form class="panel inline-form" onsubmit={saveEscalate} aria-labelledby="es-title" novalidate>
			<h2 id="es-title">Escalate this report</h2>
			<div class="field">
				<label for="es-note">Note</label>
				<textarea id="es-note" class="input" bind:value={note} bind:this={firstField} aria-invalid={!!error} aria-describedby="es-err" placeholder="What the receiving team needs to know"></textarea>
			</div>
			<p id="es-err" class="err-slot" aria-live="polite">{#if error}<span class="field-error"><Icon name="info" />{error}</span>{/if}</p>
			<div class="actions">
				<button class="btn btn-primary" type="submit">Escalate</button>
				<button class="btn" type="button" onclick={() => (form = null)}>Cancel</button>
			</div>
		</form>
	{/if}

	<div class="grid">
		<div class="col">
			<section class="panel o1" aria-labelledby="h-report">
				<h2 id="h-report">Incident Report</h2>
				<p class="report">
					{#each report.sentences as s, i (i)}{#if evidence.has(i)}<mark>{s}</mark><sup class="ev" aria-label="sentence {i + 1}, Evidence">{i + 1}</sup>{:else}<span>{s}</span><sup class="muted" aria-label="sentence {i + 1}">{i + 1}</sup>{/if}{' '}{/each}
				</p>
				<p class="legend"><span class="sw" aria-hidden="true"></span>Evidence: sentences quoted as support for the triage decisions (highlighted and underlined)</p>
			</section>
			<section class="panel o4" aria-labelledby="h-hist">
				<h2 id="h-hist">Decision history</h2>
				<ol class="hist">
					<li><time class="num">{report.received}</time><span class="who">System</span><span>Received by {CHANNEL_NAME[report.channel].toLowerCase()} from a {report.author_role}</span></li>
					<li><time class="num">{report.received}</time><span class="who">Approach {a}</span><span>{approachEvent}</span></li>
					<li>
						<time class="num">{report.received}</time><span class="who">Policy {p}</span>
						<span>{#if row.mode === 'review'}Sent to Review · {row.outcome.review_triggers.length} Review {row.outcome.review_triggers.length === 1 ? 'Trigger' : 'Triggers'}{:else}Auto-routed to {DESTINATION_NAME[row.pred.destination.top]}{/if}</span>
					</li>
					{#each log as x, i (i)}
						<li>
							<time class="num">{clock(x.at)}</time><span class="who">Reviewer</span>
							<span>{actionText(x)}{#if x.note}<span class="note">“{x.note}”</span>{/if}</span>
						</li>
					{/each}
					{#if row.status === 'awaiting'}
						<li><time>—</time><span class="who">Reviewer</span><span class="pending">Awaiting a Reviewer Action</span></li>
					{/if}
				</ol>
			</section>
		</div>
		<div class="col">
			<section class="panel o2" aria-labelledby="h-dec">
				<h2 id="h-dec">Triage decisions</h2>
				<p class="dec-sub">Approach {a} · Policy {p}{#if row.last?.kind === 'override'} · the route above shows the reviewer's override{/if}</p>
				<dl>

					<div class="dec">
						<dt>Category</dt>
						<dd>
							<div class="val"><span>{CATEGORY_NAME[row.pred.category.top]}</span><span class="prob num">{p2(cat[0][1])}</span></div>
							{@render bar(cat[0][1], cat[1]?.[1] ?? 0, t?.min_category_prob ?? 0, catLow)}
							<div class="meta num">
								Next: {cat[1] ? `${CATEGORY_NAME[cat[1][0]]} ${p2(cat[1][1])}` : 'none'} · minimum {p2(t?.min_category_prob)}{catLow ? ' (below)' : ''} · Evidence {evidenceList}
							</div>
							{#if report.label}{@render labelLine(report.label.category === row.pred.category.top, CATEGORY_NAME[report.label.category])}{/if}
						</dd>
					</div>

					<div class="dec">
						<dt>Urgency</dt>
						<dd>
							<div class="val"><UrgencyMark urgency={row.outcome.urgency} /><span class="prob num">{p2(up)}</span></div>
							{@render bar(up, 0, t?.urgent_threshold ?? 0.5, inBand, t?.review_band)}
							<div class="meta num">
								Urgent probability {p2(up)} · threshold {p2(t?.urgent_threshold)} · Review band {p2(t?.review_band[0])} to {p2(t?.review_band[1])}{inBand ? ' (inside)' : ''} · Evidence {evidenceList}
							</div>
							{#if report.label}{@render labelLine(report.label.urgency === row.outcome.urgency, report.label.urgency)}{/if}
						</dd>
					</div>

					<div class="dec">
						<dt>Destination</dt>
						<dd>
							<div class="val"><DestinationPlate destination={row.pred.destination.top} /><span class="prob num">{p2(dest[0][1])}</span></div>
							{@render bar(dest[0][1], dest[1]?.[1] ?? 0, t?.min_destination_prob ?? 0, destLow)}
							<div class="meta num">
								Next: {dest[1] ? `${DESTINATION_NAME[dest[1][0]]} ${p2(dest[1][1])}` : 'none'} · minimum {p2(t?.min_destination_prob)}{destLow ? ' (below)' : ''} · Evidence {evidenceList}
							</div>
							{#if report.label}{@render labelLine(report.label.destination === row.pred.destination.top, DESTINATION_NAME[report.label.destination])}{/if}
						</dd>
					</div>
				</dl>
				<p class="legend">Bar: top value, then the runner-up (lighter). Tick: the Policy's threshold.</p>
			</section>
			<section class="panel o3" aria-labelledby="h-trig">
				<h2 id="h-trig">Review Triggers</h2>
				{#if row.mode === 'review' && row.outcome.review_triggers.length}
					<ul class="trigs">
						{#each row.outcome.review_triggers as tr (tr.name)}
							<li class="trig">
								<Icon name="review" />
								<div><b>{tr.name}</b><span>{tr.detail}</span></div>
								<span class="chip">{tr.source}</span>
							</li>
						{/each}
					</ul>
				{:else}
					<p class="muted none">No Review Triggers. Auto-routed by Policy {p}.</p>
				{/if}
			</section>
		</div>
	</div>

	{#if row.mode === 'review'}
		<div class="actionbar">
			{#if row.last}
				<ActionStatus status={row.last.kind} />
				<button class="btn" type="button" onclick={() => actions.undo(a, p, id)}><Icon name="undo" />Undo</button>
			{:else}
				<button class="btn btn-primary" type="button" onclick={accept}>Accept</button>
				<button class="btn" type="button" onclick={() => openForm('override')}>Override</button>
				<button class="btn" type="button" onclick={() => openForm('escalate')}>Escalate</button>
			{/if}
		</div>
	{/if}
{/if}

<style>
	.crumb {
		display: inline-flex;
		align-items: center;
		gap: 4px;
		font-size: var(--t-small);
		font-weight: 500;
		margin-bottom: var(--s3);
		text-decoration: none;
		min-height: 32px;
	}
	.crumb:hover {
		text-decoration: underline;
	}
	.empty {
		text-align: left;
	}
	.empty h1 {
		margin-bottom: var(--s3);
	}
	.detail-head {
		display: flex;
		align-items: flex-end;
		justify-content: space-between;
		gap: var(--s4) var(--s5);
		margin-bottom: var(--s5);
		flex-wrap: wrap;
	}
	.meta-line {
		color: var(--text-2);
		font-size: var(--t-small);
		margin: 2px 0 0;
	}
	.route {
		display: flex;
		align-items: center;
		gap: var(--s3);
		flex-wrap: wrap;
		margin-top: var(--s3);
	}
	.route-sep {
		color: var(--text-2);
		display: inline-flex;
	}
	.head-actions {
		display: flex;
		flex-direction: column;
		align-items: flex-end;
		gap: var(--s2);
	}
	.actions {
		display: flex;
		gap: var(--s2);
		flex-wrap: wrap;
	}
	.logged {
		display: flex;
		align-items: center;
		gap: var(--s3);
		font-size: var(--t-small);
	}
	.demo-line {
		font-size: var(--t-caption);
		color: var(--text-2);
		margin: 0;
	}
	.inline-form {
		margin-bottom: var(--s4);
		display: flex;
		flex-direction: column;
		gap: var(--s3);
		animation: open var(--dur) var(--ease);
	}
	.inline-form h2 {
		margin: 0;
	}
	@keyframes open {
		from {
			opacity: 0;
			transform: translateY(-4px);
		}
	}
	.form-grid {
		display: grid;
		grid-template-columns: repeat(3, minmax(0, 1fr));
		gap: var(--s3);
	}
	.err-slot {
		margin: 0;
		min-height: 1.2em;
	}
	.grid {
		display: grid;
		grid-template-columns: minmax(0, 1fr) 440px;
		gap: var(--s5);
		align-items: start;
	}
	.col {
		display: flex;
		flex-direction: column;
		gap: var(--s4);
	}
	.col > .panel + .panel {
		margin-top: 0;
	}
	.report {
		font-size: var(--t-body);
		line-height: 1.65;
		max-width: 68ch;
		margin: 0;
	}
	/* Evidence: fill + 2px underline, so it reads without colour. */
	.report mark {
		background: var(--evidence);
		color: inherit;
		box-shadow: inset 0 -2px 0 var(--evidence-line);
		padding: 1px 2px;
		border-radius: 2px;
		-webkit-box-decoration-break: clone;
		box-decoration-break: clone;
	}
	.report sup {
		font-size: 0.6875rem;
		font-weight: 700;
		margin-left: 2px;
		font-variant-numeric: tabular-nums;
	}
	.report sup.ev {
		color: var(--accent);
	}
	.legend {
		display: flex;
		gap: var(--s2);
		align-items: center;
		margin: var(--s4) 0 0;
		font-size: var(--t-caption);
		color: var(--text-2);
	}
	.sw {
		display: inline-block;
		width: 14px;
		height: 10px;
		flex: none;
		background: var(--evidence);
		box-shadow: inset 0 -2px 0 var(--evidence-line);
		border-radius: 2px;
	}
	.dec-sub {
		font-size: var(--t-caption);
		color: var(--text-2);
		margin: -6px 0 var(--s3);
	}
	dl {
		margin: 0;
	}
	.dec {
		display: grid;
		grid-template-columns: 96px minmax(0, 1fr);
		gap: 2px var(--s3);
		padding: var(--s3) 0;
		border-top: 1px solid var(--sep);
	}
	.dec:first-of-type {
		border-top: 0;
		padding-top: 0;
	}
	dt {
		font-size: var(--t-row);
		color: var(--text-2);
		padding-top: 4px;
	}
	dd {
		margin: 0;
	}
	.val {
		font-weight: 650;
		display: flex;
		align-items: center;
		gap: 8px;
		justify-content: space-between;
		min-height: 26px;
	}
	.prob {
		font-weight: 650;
		font-size: var(--t-small);
	}
	/* Stacked probability bar: top value, 2px surface gap, runner-up at 45% (dataviz marks). */
	.bar {
		position: relative;
		display: flex;
		gap: 2px;
		height: 6px;
		background: var(--surface-2);
		border-radius: 3px;
		margin: 6px 0 4px;
	}
	.bar i {
		display: block;
		height: 100%;
		background: var(--text);
		border-radius: 3px;
	}
	.bar i.runner {
		opacity: 0.45;
	}
	.bar.low i:not(.runner) {
		background: var(--review);
		box-shadow: 0 0 0 1px var(--review-edge);
	}
	.bar .band {
		position: absolute;
		top: -2px;
		bottom: -2px;
		border: 1px dashed var(--text-2);
		border-radius: 3px;
	}
	.bar b {
		position: absolute;
		top: -3px;
		width: 2px;
		height: 12px;
		background: var(--text-2);
		border-radius: 1px;
		margin-left: -1px;
	}
	.meta {
		font-size: var(--t-caption);
		color: var(--text-2);
	}
	.label-line {
		display: flex;
		align-items: center;
		gap: 6px;
		font-size: var(--t-caption);
		color: var(--text-2);
		margin-top: 4px;
	}
	.trigs {
		list-style: none;
		margin: 0;
		padding: 0;
	}
	.trig {
		display: grid;
		grid-template-columns: 20px minmax(0, 1fr) auto;
		gap: var(--s2);
		padding: var(--s2) 0;
		font-size: var(--t-small);
	}
	.trig > :global(.ic) {
		width: 18px;
		height: 18px;
		margin-top: 1px;
	}
	.trig b {
		display: block;
		font-weight: 650;
	}
	.trig span {
		color: var(--text-2);
	}
	.chip {
		font-size: var(--t-caption);
		font-weight: 650;
		border: 1px solid var(--sep);
		border-radius: 4px;
		padding: 1px 6px;
		align-self: start;
		white-space: nowrap;
	}
	.none {
		font-size: var(--t-small);
		margin: 0;
	}
	.hist {
		list-style: none;
		margin: 0;
		padding: 0;
		font-size: var(--t-row);
	}
	.hist li {
		display: grid;
		grid-template-columns: 72px 92px minmax(0, 1fr);
		gap: var(--s3);
		padding: 7px 0;
		border-top: 1px solid var(--sep);
	}
	.hist li:first-child {
		border-top: 0;
	}
	.hist time {
		color: var(--text-2);
	}
	.who {
		font-weight: 600;
	}
	.note {
		display: block;
		color: var(--text-2);
	}
	.pending {
		color: var(--text-2);
		font-style: italic;
	}
	.actionbar {
		display: none;
	}

	@media (max-width: 1023px) {
		.grid {
			grid-template-columns: minmax(0, 1fr);
		}
		.head-actions {
			align-items: flex-start;
		}
	}
	@media (max-width: 599px) {
		.crumb,
		.head-actions {
			display: none;
		}
		.detail-head {
			margin-bottom: var(--s4);
		}
		.route {
			margin-top: var(--s3);
			gap: var(--s2);
		}
		.route > :global(.urg) {
			width: 100%;
		}
		.route :global(.plate-lg) {
			font-size: 0.9375rem;
			padding: 7px 10px;
			gap: 8px;
		}
		.form-grid {
			grid-template-columns: minmax(0, 1fr);
		}
		.inline-form :global(.select),
		.inline-form :global(.input),
		.inline-form :global(.btn) {
			min-height: 44px;
			font-size: var(--t-body);
		}
		.grid {
			display: flex;
			flex-direction: column;
			gap: var(--s3);
		}
		.col {
			display: contents;
		}
		.o1 {
			order: 1;
		}
		.o2 {
			order: 2;
		}
		.o3 {
			order: 3;
		}
		.o4 {
			order: 4;
		}
		.panel {
			padding: var(--s4);
		}
		.dec {
			grid-template-columns: minmax(0, 1fr);
		}
		.hist li {
			grid-template-columns: 64px minmax(0, 1fr);
		}
		.hist li > span:last-child {
			grid-column: 2;
		}
		.actionbar {
			display: grid;
			grid-template-columns: 1.4fr 1fr 1fr;
			align-items: center;
			gap: var(--s2);
			position: fixed;
			left: 0;
			right: 0;
			bottom: calc(61px + env(safe-area-inset-bottom));
			background: var(--surface);
			border-top: 1px solid var(--sep);
			padding: var(--s2) var(--s4);
			z-index: 4;
		}
		.actionbar :global(.btn) {
			min-height: 44px;
			padding: 0 8px;
		}
		.actionbar :global(.status) {
			grid-column: span 2;
		}
		:global(.main):has(.actionbar) {
			padding-bottom: 96px;
		}
	}
</style>
