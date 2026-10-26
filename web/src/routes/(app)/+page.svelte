<script lang="ts">
	import { onMount, tick } from 'svelte';
	import { goto } from '$app/navigation';
	import { resolve } from '$app/paths';
	import { incidents } from '$lib/data/store.svelte';
	import { actions } from '$lib/actions.svelte';
	import { view } from '$lib/context.svelte';
	import { rowsFor, type Row } from '$lib/rows';
	import type { Destination, Urgency } from '$lib/data/types';
	import { CATEGORY_NAME, DESTINATIONS, DESTINATION_NAME, waited } from '$lib/vocab';
	import Icon from '$lib/components/Icon.svelte';
	import DestinationPlate from '$lib/components/DestinationPlate.svelte';
	import ModePlate from '$lib/components/ModePlate.svelte';
	import UrgencyMark from '$lib/components/UrgencyMark.svelte';
	import ActionStatus from '$lib/components/ActionStatus.svelte';
	import SampleNotice from '$lib/components/SampleNotice.svelte';

	type Show = 'all' | 'awaiting' | 'reviewed' | 'auto';
	let show = $state<Show>('all');
	let urgency = $state<'' | Urgency>('');
	let destination = $state<'' | Destination>('');
	let search = $state('');
	let selected = $state<string | null>(null);
	let searchEl = $state<HTMLInputElement>();
	let searchHint = $state('');

	onMount(() => {
		selected = sessionStorage.getItem('incident-triage:last-opened');
	});

	const all = $derived(
		incidents.data
			? rowsFor(incidents.data, view.approach, view.policy, (id) =>
					actions.last(view.approach, view.policy, id)
				)
			: []
	);
	const counts = $derived({
		all: all.length,
		review: all.filter((r) => r.mode === 'review').length,
		awaiting: all.filter((r) => r.status === 'awaiting').length,
		reviewed: all.filter((r) => r.mode === 'review' && r.status !== 'awaiting').length,
		auto: all.filter((r) => r.mode === 'auto').length
	});

	const filtered = $derived.by(() => {
		const q = search.trim().toLowerCase();
		return all.filter(
			(r) =>
				(show === 'all' ||
					(show === 'awaiting' && r.status === 'awaiting') ||
					(show === 'reviewed' && r.mode === 'review' && r.status !== 'awaiting') ||
					(show === 'auto' && r.mode === 'auto')) &&
				(!urgency || r.urgency === urgency) &&
				(!destination || r.destination === destination) &&
				(!q || r.report.id.toLowerCase().includes(q) || r.report.text.toLowerCase().includes(q))
		);
	});

	// Review items first (awaiting: urgent first, then longest waiting), then reviewed, then
	// auto-routed newest first.
	const sections = $derived.by(() => {
		const awaiting = filtered
			.filter((r) => r.status === 'awaiting')
			.sort(
				(x, y) =>
					Number(y.urgency === 'urgent') - Number(x.urgency === 'urgent') ||
					y.report.waiting_min - x.report.waiting_min
			);
		const reviewed = filtered
			.filter((r) => r.mode === 'review' && r.status !== 'awaiting')
			.sort((x, y) => (y.last?.at ?? '').localeCompare(x.last?.at ?? ''));
		const auto = filtered
			.filter((r) => r.mode === 'auto')
			.sort((x, y) => x.report.waiting_min - y.report.waiting_min);
		return [
			{ key: 'awaiting', title: 'Awaiting review · urgent first', rows: awaiting },
			{ key: 'reviewed', title: 'Reviewed', rows: reviewed },
			{ key: 'auto', title: 'Auto-routed · newest first', rows: auto }
		].filter((s) => s.rows.length);
	});
	const ordered = $derived(sections.flatMap((s) => s.rows));

	const filterWords = $derived(
		[
			show === 'awaiting' ? 'awaiting review' : show === 'reviewed' ? 'reviewed' : show === 'auto' ? 'auto-routed' : '',
			urgency,
			destination ? DESTINATION_NAME[destination] : '',
			search.trim() ? `“${search.trim()}”` : ''
		]
			.filter(Boolean)
			.join(' · ')
	);

	const href = (r: Row) => resolve('/(app)/incident/[id]', { id: r.report.id }) + view.query;

	function open(r: Row) {
		sessionStorage.setItem('incident-triage:last-opened', r.report.id);
		goto(href(r));
	}

	function clearFilters() {
		show = 'all';
		urgency = '';
		destination = '';
		search = '';
	}

	async function move(delta: number) {
		if (!ordered.length) return;
		const i = ordered.findIndex((r) => r.report.id === selected);
		const next = ordered[Math.min(ordered.length - 1, Math.max(0, i < 0 ? 0 : i + delta))];
		selected = next.report.id;
		await tick();
		// Focus the visible link for this report (table on wide screens, list on phones).
		const links = document.querySelectorAll<HTMLAnchorElement>(`[data-rid="${next.report.id}"]`);
		[...links].find((l) => l.offsetParent !== null)?.focus();
	}

	function onKey(e: KeyboardEvent) {
		const t = e.target as HTMLElement;
		if (e.metaKey || e.ctrlKey || e.altKey) return;
		if (t.matches('input, select, textarea')) {
			if (e.key === 'Escape' && t === searchEl) searchEl?.blur();
			return;
		}
		if (e.key === 'j') {
			e.preventDefault();
			move(1);
		} else if (e.key === 'k') {
			e.preventDefault();
			move(-1);
		} else if (e.key === '/') {
			e.preventDefault();
			searchEl?.focus();
			searchEl?.select();
		} else if (e.key === 'Enter' && selected && !t.matches('a, button')) {
			const r = ordered.find((x) => x.report.id === selected);
			if (r) open(r);
		}
	}

	function onSearchKey(e: KeyboardEvent) {
		if (e.key !== 'Enter') return;
		const q = search.trim().toUpperCase();
		const id = /^\d+$/.test(q) ? `R-${q.padStart(4, '0')}` : q;
		const r = all.find((x) => x.report.id === id);
		if (r) open(r);
		else if (/^R-?\d+$/.test(q)) searchHint = `No report ${id} in this split. Check the id, or clear the search.`;
	}
	$effect(() => {
		void search;
		searchHint = '';
	});
	const SHOWS: [Show, string, () => number][] = [
		['all', 'All', () => counts.all],
		['awaiting', 'Awaiting review', () => counts.awaiting],
		['reviewed', 'Reviewed', () => counts.reviewed],
		['auto', 'Auto-routed', () => counts.auto]
	];
</script>

<svelte:head><title>Queue · Incident triage</title></svelte:head>
<svelte:window onkeydown={onKey} />

<div class="page-head">
	<h1>Queue</h1>
	{#if incidents.data}
		<span class="sub num">
			{counts.all} Incident Reports · {counts.review} sent to Review · {counts.awaiting} awaiting a Reviewer Action
		</span>
	{/if}
</div>

{#if incidents.data?.fixture}<SampleNotice what="reports and predictions" />{/if}

<div class="toolbar">
	<div class="tabs" role="group" aria-label="Show">
		{#each SHOWS as [key, label, count] (key)}
			<button type="button" aria-pressed={show === key} onclick={() => (show = key)}>
				{label} <span class="count num">{incidents.data ? count() : ''}</span>
			</button>
		{/each}
	</div>
	<div class="filters">
		<label class="pick">
			<span class="visually-hidden">Urgency</span>
			<select class="select" bind:value={urgency}>
				<option value="">Urgency: any</option>
				<option value="urgent">Urgent</option>
				<option value="routine">Routine</option>
			</select>
		</label>
		<label class="pick">
			<span class="visually-hidden">Destination</span>
			<select class="select" bind:value={destination}>
				<option value="">Destination: any</option>
				{#each DESTINATIONS as d (d)}<option value={d}>{DESTINATION_NAME[d]}</option>{/each}
			</select>
		</label>
	</div>
	<div class="search">
		<label for="q" class="visually-hidden">Find a report by id or text</label>
		<Icon name="search" />
		<input
			id="q"
			type="search"
			class="input"
			placeholder="Report id or text"
			autocomplete="off"
			bind:this={searchEl}
			bind:value={search}
			onkeydown={onSearchKey}
			aria-describedby="q-hint"
		/>
		<span class="kbd" aria-hidden="true">/</span>
	</div>
</div>
<p class="hint" id="q-hint" aria-live="polite">
	{#if searchHint}<span class="field-error"><Icon name="info" />{searchHint}</span>{:else}<span class="keys"><span class="kbd">j</span> <span class="kbd">k</span> move · <span class="kbd">Enter</span> opens · <span class="kbd">/</span> finds a report id</span>{/if}
</p>

{#if incidents.error}
	<div class="table-wrap empty" role="alert">
		<p>The reports did not load ({incidents.error}).</p>
		<button class="btn" type="button" onclick={() => location.reload()}>Reload the page</button>
	</div>
{:else if !incidents.data}
	<div class="table-wrap" aria-busy="true" aria-label="Loading reports">
		{#each Array(8) as _, i (i)}
			<div class="sk-row"><span class="skeleton" style="width: 9%"></span><span class="skeleton" style="width: 34%"></span><span class="skeleton" style="width: 14%"></span><span class="skeleton" style="width: 12%"></span></div>
		{/each}
	</div>
{:else if !all.length}
	<div class="table-wrap empty">
		<p>No Incident Reports to show for approach {view.approach} on the {incidents.data.split} split yet.</p>
		<p>Export them with <b>python -m uv run python eval/export_web.py</b>, then rebuild.</p>
	</div>
{:else if !ordered.length}
	<div class="table-wrap empty">
		<p>No reports match {filterWords}.</p>
		<button class="btn" type="button" onclick={clearFilters}>Show all reports</button>
	</div>
{:else}
	<div class="table-wrap desk">
		<table>
			<thead>
				<tr>
					<th scope="col">Urgency</th>
					<th scope="col">Report</th>
					<th scope="col" class="col-cat">Category</th>
					<th scope="col">Destination</th>
					<th scope="col">Routing Mode</th>
					<th scope="col">Reviewer Action</th>
					<th scope="col" class="col-time">Received</th>
				</tr>
			</thead>
			{#each sections as s (s.key)}
				<tbody>
					<tr class="section-row"><th scope="rowgroup" colspan="7">{s.title}</th></tr>
					{#each s.rows as r (r.report.id)}
						<tr class:sel={selected === r.report.id} onclick={() => open(r)}>
							<td><UrgencyMark urgency={r.urgency} /></td>
							<td class="col-report">
								<a class="rid" href={href(r)} data-rid={r.report.id} onclick={(e) => { e.preventDefault(); e.stopPropagation(); open(r); }} onfocus={() => (selected = r.report.id)}>{r.report.id}</a>
								<span class="excerpt">{r.report.text}</span>
								<span class="time-inline num muted">{r.report.received}{#if r.status === 'awaiting'} · waiting {waited(r.report.waiting_min)}{/if}</span>
							</td>
							<td class="col-cat">{CATEGORY_NAME[r.category]}</td>
							<td><DestinationPlate destination={r.destination} /></td>
							<td><ModePlate mode={r.mode} /></td>
							<td><ActionStatus status={r.status} /></td>
							<td class="col-time num">
								{r.report.received}
								{#if r.status === 'awaiting'}<span class="wait muted">waiting {waited(r.report.waiting_min)}</span>{/if}
							</td>
						</tr>
					{/each}
				</tbody>
			{/each}
		</table>
	</div>

	<div class="list">
		{#each sections as s (s.key)}
			<h2 class="li-group">{s.title}</h2>
			<ul>
				{#each s.rows as r (r.report.id)}
					<li>
						<a class="li" class:sel={selected === r.report.id} href={href(r)} data-rid={r.report.id} onclick={(e) => { e.preventDefault(); open(r); }}>
							<span class="li-top">
								<UrgencyMark urgency={r.urgency} />
								<span class="rid">{r.report.id}</span>
								<span class="li-time num">{r.report.received}{#if r.status === 'awaiting'} · {waited(r.report.waiting_min)}{/if}</span>
							</span>
							<span class="li-text">{r.report.text}</span>
							<span class="li-plates">
								<ModePlate mode={r.mode} />
								<DestinationPlate destination={r.destination} />
								{#if r.status && r.status !== 'awaiting'}<ActionStatus status={r.status} />{/if}
							</span>
						</a>
					</li>
				{/each}
			</ul>
		{/each}
	</div>
{/if}

<p class="foot-note">
	All reports are synthetic. Times are on the demo clock ({incidents.data?.demo_clock ?? '08:00'}); Reviewer Actions stay in this browser.
</p>

<style>
	.toolbar {
		display: flex;
		gap: var(--s3);
		align-items: center;
		flex-wrap: wrap;
		margin-bottom: var(--s2);
	}
	.tabs {
		display: inline-flex;
		background: var(--surface-2);
		border-radius: var(--r-ctl);
		padding: 3px;
		gap: 2px;
		max-width: 100%;
		overflow-x: auto;
	}
	.tabs button {
		border: 0;
		background: none;
		padding: 0 12px;
		min-height: 34px;
		border-radius: 4px;
		font-size: var(--t-row);
		font-weight: 600;
		color: var(--text-2);
		cursor: pointer;
		display: inline-flex;
		gap: 6px;
		align-items: center;
		white-space: nowrap;
		transition: background-color var(--dur) var(--ease);
	}
	.tabs button:hover {
		color: var(--text);
	}
	.tabs button[aria-pressed='true'] {
		background: var(--surface);
		color: var(--text);
		box-shadow: 0 1px 2px rgb(0 0 0 / 0.12);
	}
	.count {
		font-weight: 500;
		color: var(--text-2);
	}
	.filters {
		display: flex;
		gap: var(--s2);
	}
	.select {
		min-height: 36px;
		font-size: var(--t-row);
	}
	.search {
		margin-left: auto;
		position: relative;
		display: flex;
		align-items: center;
		width: 260px;
		color: var(--text-2);
	}
	.search > :global(.ic) {
		position: absolute;
		left: 10px;
		width: 16px;
		height: 16px;
		pointer-events: none;
	}
	.search .input {
		width: 100%;
		min-height: 36px;
		padding-left: 32px;
		padding-right: 32px;
		font-size: var(--t-row);
	}
	.search .kbd {
		position: absolute;
		right: 8px;
	}
	.hint {
		font-size: var(--t-caption);
		color: var(--text-2);
		min-height: 1.4em;
		margin: 0 0 var(--s3);
	}
	.sk-row {
		display: flex;
		gap: var(--s5);
		padding: 14px 12px;
		border-bottom: 1px solid var(--sep);
	}
	.section-row th {
		background: var(--surface-2);
		color: var(--text-2);
		font-weight: 600;
		font-size: var(--t-caption);
		padding: 6px 12px;
		border-top: 1px solid var(--sep);
	}
	tbody:first-of-type .section-row th {
		border-top: 0;
	}
	tbody tr:not(.section-row) {
		cursor: pointer;
	}
	tbody tr:not(.section-row) td {
		height: 44px;
		transition: background-color var(--dur) var(--ease);
	}
	tbody tr:not(.section-row):hover td {
		background: var(--surface-2);
	}
	/* Selection is tint + 1px outline, never a side stripe (direction › what not to do). */
	tr.sel td {
		background: var(--accent-tint) !important;
	}
	tr.sel {
		outline: 1px solid var(--accent);
		outline-offset: -1px;
	}
	.col-report .rid {
		color: var(--text);
		text-decoration: none;
		display: inline-block;
		border-radius: 2px;
	}
	.col-report .rid:hover {
		text-decoration: underline;
	}
	.excerpt {
		color: var(--text-2);
		display: block;
		max-width: 44ch;
		overflow: hidden;
		text-overflow: ellipsis;
		white-space: nowrap;
	}
	.col-cat {
		white-space: nowrap;
	}
	.col-time {
		color: var(--text-2);
		white-space: nowrap;
	}
	.wait {
		display: block;
		font-size: var(--t-caption);
	}
	.time-inline {
		display: none;
		font-size: var(--t-caption);
	}
	.list {
		display: none;
	}
	.foot-note {
		margin-top: var(--s3);
		font-size: var(--t-caption);
		color: var(--text-2);
	}

	@media (max-width: 1023px) {
		.col-cat,
		.col-time {
			display: none;
		}
		.time-inline {
			display: block;
		}
		.search {
			margin-left: 0;
			flex: 1 1 220px;
		}
	}
	@media (max-width: 599px) {
		.desk,
		.hint {
			display: none;
		}
		.toolbar {
			gap: var(--s2);
		}
		.tabs {
			margin: 0 calc(var(--s4) * -1);
			padding: 3px var(--s4);
			border-radius: 0;
			width: calc(100% + var(--s4) * 2);
			max-width: none;
		}
		.tabs button {
			min-height: 44px;
		}
		.filters {
			width: 100%;
		}
		.pick {
			flex: 1;
			min-width: 0;
		}
		.pick .select,
		.search .input {
			width: 100%;
			min-height: 44px;
			font-size: var(--t-body);
		}
		.search {
			width: 100%;
		}
		.search .kbd {
			display: none;
		}
		.list {
			display: block;
			background: var(--surface);
			border: 1px solid var(--sep);
			border-radius: var(--r-panel);
			margin-top: var(--s3);
			overflow: hidden;
		}
		.list ul {
			list-style: none;
			margin: 0;
			padding: 0;
		}
		.li-group {
			margin: 0;
			padding: 6px var(--s4);
			font-size: var(--t-caption);
			font-weight: 600;
			color: var(--text-2);
			background: var(--surface-2);
			border-top: 1px solid var(--sep);
		}
		.li-group:first-child {
			border-top: 0;
		}
		.li {
			display: block;
			padding: var(--s3) var(--s4);
			border-top: 1px solid var(--sep);
			text-decoration: none;
			color: inherit;
			min-height: 44px;
		}
		li:first-child .li {
			border-top: 0;
		}
		.li.sel {
			background: var(--accent-tint);
			outline: 1px solid var(--accent);
			outline-offset: -1px;
		}
		.li-top {
			display: flex;
			align-items: center;
			gap: var(--s2);
			font-size: var(--t-row);
		}
		.li-time {
			margin-left: auto;
			color: var(--text-2);
		}
		.li-text {
			font-size: var(--t-small);
			color: var(--text-2);
			margin: 4px 0 8px;
			display: -webkit-box;
			line-clamp: 2;
			-webkit-line-clamp: 2;
			-webkit-box-orient: vertical;
			overflow: hidden;
		}
		.li-plates {
			display: flex;
			gap: 6px;
			flex-wrap: wrap;
			align-items: center;
			font-size: var(--t-row);
		}
	}
</style>
