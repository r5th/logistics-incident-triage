<script lang="ts">
	// Blind labelling. A Blind Label must be given without seeing the Seeded Label or any
	// prediction (GLOSSARY.md), so this route reads exactly one data file, labelling.json
	// (report ids and text only), and deliberately imports nothing from $lib/data/load or
	// $lib/data/store, which can fetch incidents.json. The label guide is bundled at build time.
	import { onDestroy, onMount, tick } from 'svelte';
	import { asset } from '$app/paths';
	import Shell from '$lib/components/Shell.svelte';
	import Icon from '$lib/components/Icon.svelte';
	import SampleNotice from '$lib/components/SampleNotice.svelte';
	import type { BlindLabelRow, Category, Destination, LabellingFile, Urgency } from '$lib/data/types';
	import { CATEGORIES, CATEGORY_NAME, DESTINATIONS, DESTINATION_NAME } from '$lib/vocab';
	import { CATEGORY_CODES, QUICK_REFERENCE } from '$lib/labelGuide';

	const KEY = 'incident-triage:blind-labels:v1';
	const PASS2_DELAY_MS = 4 * 60 * 60 * 1000; // build plan: re-label ≥ 4 h after pass 1
	const DEST_KEYS = ['a', 'b', 'c', 'd', 'e', 'f'];

	type Saved = { category: Category; urgency: Urgency; destination: Destination; labelled_at: string };
	type Draft = Partial<Omit<Saved, 'labelled_at'>>;
	type Store = {
		labels: { 1: Record<string, Saved>; 2: Record<string, Saved> };
		pass1_finished_at: string | null;
		pass: 1 | 2;
		cursor: { 1: number; 2: number };
	};

	let file = $state<LabellingFile | null>(null);
	let loadError = $state<string | null>(null);
	let store = $state<Store>({ labels: { 1: {}, 2: {} }, pass1_finished_at: null, pass: 1, cursor: { 1: 0, 2: 0 } });
	let draft = $state<Draft>({});
	let now = $state(Date.now());
	let guideOpen = $state(true);
	let hint = $state('');
	let textEl = $state<HTMLElement>();
	let timer: ReturnType<typeof setInterval> | undefined;

	onMount(() => {
		try {
			const saved = JSON.parse(localStorage.getItem(KEY) ?? 'null');
			if (saved?.labels) store = saved;
		} catch {
			/* a corrupt entry starts fresh; nothing to recover */
		}
		guideOpen = matchMedia('(min-width: 1200px)').matches;
		timer = setInterval(() => (now = Date.now()), 30_000);
		fetch(asset('/data/labelling.json'))
			.then((r) => {
				if (!r.ok) throw new Error(`HTTP ${r.status}`);
				return r.json();
			})
			.then((d: LabellingFile) => {
				file = d;
				loadDraft();
			})
			.catch((e: Error) => (loadError = e.message));
	});
	onDestroy(() => clearInterval(timer));

	function persist() {
		localStorage.setItem(KEY, JSON.stringify(store));
	}

	// Pass 2 re-labels the fixed seeded sample in a different, also seeded, order.
	function shuffled<T>(xs: T[], seed: number): T[] {
		let s = seed >>> 0;
		const rand = () => {
			s = (s + 0x6d2b79f5) >>> 0;
			let t = s;
			t = Math.imul(t ^ (t >>> 15), t | 1);
			t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
			return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
		};
		const out = [...xs];
		for (let i = out.length - 1; i > 0; i--) {
			const j = Math.floor(rand() * (i + 1));
			[out[i], out[j]] = [out[j], out[i]];
		}
		return out;
	}

	const order = $derived.by(() => {
		if (!file) return [];
		if (store.pass === 1) return file.reports;
		const byId = new Map(file.reports.map((r) => [r.id, r]));
		return shuffled(file.pass2_ids, file.seed + 2).flatMap((id) => byId.get(id) ?? []);
	});
	const index = $derived(Math.min(store.cursor[store.pass], Math.max(0, order.length - 1)));
	const current = $derived(order[index]);
	const done = $derived(order.filter((r) => store.labels[store.pass][r.id]).length);
	const pass1Done = $derived(!!file && file.reports.every((r) => store.labels[1][r.id]));
	const unlockAt = $derived(store.pass1_finished_at ? Date.parse(store.pass1_finished_at) + PASS2_DELAY_MS : null);
	const pass2Open = $derived(unlockAt != null && now >= unlockAt);
	const complete = $derived(!!(draft.category && draft.urgency && draft.destination));
	const totalLabels = $derived(Object.keys(store.labels[1]).length + Object.keys(store.labels[2]).length);

	const hhmm = (t: number) => new Date(t).toLocaleTimeString('en-GB', { hour: '2-digit', minute: '2-digit', hour12: false });
	const dayAndTime = (t: number) => new Date(t).toLocaleString('en-GB', { weekday: 'short', hour: '2-digit', minute: '2-digit', hour12: false });

	function loadDraft() {
		const saved = current ? store.labels[store.pass][current.id] : undefined;
		draft = saved ? { category: saved.category, urgency: saved.urgency, destination: saved.destination } : {};
		hint = '';
	}

	async function go(i: number) {
		store.cursor[store.pass] = Math.max(0, Math.min(order.length - 1, i));
		persist();
		loadDraft();
		await tick();
		textEl?.focus();
	}

	function save() {
		if (!current) return;
		if (!complete) {
			const missing = [!draft.category && 'a Category', !draft.urgency && 'an Urgency', !draft.destination && 'a Destination'].filter(Boolean);
			hint = `Pick ${missing.join(' and ')} to save this Label.`;
			return;
		}
		store.labels[store.pass][current.id] = {
			category: draft.category!,
			urgency: draft.urgency!,
			destination: draft.destination!,
			labelled_at: new Date().toISOString()
		};
		if (store.pass === 1 && !store.pass1_finished_at && file?.reports.every((r) => store.labels[1][r.id])) {
			store.pass1_finished_at = new Date().toISOString();
		}
		persist();
		// Next unlabelled report after this one, else stay.
		const next = order.findIndex((r, i) => i > index && !store.labels[store.pass][r.id]);
		const wrap = order.findIndex((r) => !store.labels[store.pass][r.id]);
		go(next >= 0 ? next : wrap >= 0 ? wrap : index);
	}

	function setPass(p: 1 | 2) {
		if (p === 2 && !pass2Open) return;
		store.pass = p;
		persist();
		loadDraft();
	}

	function download() {
		const rows: BlindLabelRow[] = ([1, 2] as const).flatMap((pass) =>
			Object.entries(store.labels[pass])
				.sort(([x], [y]) => x.localeCompare(y))
				.map(([report_id, l]) => ({ report_id, category: l.category, urgency: l.urgency, destination: l.destination, pass, labelled_at: l.labelled_at }))
		);
		const blob = new Blob([JSON.stringify(rows, null, 2) + '\n'], { type: 'application/json' });
		const a = document.createElement('a');
		a.href = URL.createObjectURL(blob);
		a.download = 'blind_test.json';
		a.click();
		URL.revokeObjectURL(a.href);
	}

	function onKey(e: KeyboardEvent) {
		if (!current || e.metaKey || e.ctrlKey || e.altKey) return;
		const t = e.target as HTMLElement;
		if (t.matches('input, select, textarea')) return;
		const k = e.key.toLowerCase();
		const n = Number(k);
		if (n >= 1 && n <= 6) draft.category = CATEGORIES[n - 1];
		else if (k === 'u') draft.urgency = 'urgent';
		else if (k === 'r') draft.urgency = 'routine';
		else if (DEST_KEYS.includes(k)) draft.destination = DESTINATIONS[DEST_KEYS.indexOf(k)];
		else if (k === 'g') guideOpen = !guideOpen;
		else if (e.key === 'ArrowLeft') go(index - 1);
		else if (e.key === 'ArrowRight') go(index + 1);
		else if (e.key === 'Enter' && (!t.matches('button, a') || t.dataset.pick !== undefined)) save();
		else return;
		e.preventDefault();
		hint = '';
	}
</script>

<svelte:head><title>Labeller · Incident triage</title></svelte:head>
<svelte:window onkeydown={onKey} />

<Shell title="Labeller" showContext={false}>
	<div class="page-head">
		<h1>Blind labelling</h1>
		{#if file}<span class="sub num">Pass {store.pass} · {done} of {order.length} labelled</span>{/if}
	</div>

	{#if loadError}
		<div class="panel" role="alert"><p>The reports to label did not load ({loadError}).</p><button class="btn" type="button" onclick={() => location.reload()}>Reload the page</button></div>
	{:else if !file}
		<div class="panel" aria-busy="true" aria-label="Loading reports to label"><span class="skeleton" style="width: 70%"></span><span class="skeleton" style="width: 85%"></span></div>
	{:else if !file.reports.length}
		<div class="panel"><p>There are no test reports to label yet. Export them with <b>eval/export_web.py</b>, then rebuild.</p></div>
	{:else}
		{#if file.fixture}<SampleNotice what="reports to label" />{/if}
		<p class="intro">Label each report from its text alone, using the label guide. This screen never shows a Seeded Label or a prediction. Labels save in this browser as you go.</p>

		<div class="passbar">
			<div class="tabs" role="group" aria-label="Pass">
				<button type="button" aria-pressed={store.pass === 1} onclick={() => setPass(1)}>Pass 1 <span class="count num">{Object.keys(store.labels[1]).length}/{file.reports.length}</span></button>
				<button type="button" aria-pressed={store.pass === 2} disabled={!pass2Open} onclick={() => setPass(2)}>
					{#if !pass2Open}<Icon name="lock" />{/if}Pass 2 <span class="count num">{Object.keys(store.labels[2]).length}/{file.pass2_ids.length}</span>
				</button>
			</div>
			<p class="unlock">
				{#if pass2Open}Pass 2 re-labels {file.pass2_ids.length} reports, picked by a fixed seed.
				{:else if unlockAt}Pass 2 unlocks at {dayAndTime(unlockAt)}, 4 hours after pass 1 finished.
				{:else}Pass 2 unlocks 4 hours after pass 1 is finished.{/if}
			</p>
			<button class="btn" type="button" onclick={download} disabled={!totalLabels}><Icon name="download" />Download labels</button>
		</div>

		<div class="progress" role="progressbar" aria-label="Pass {store.pass} progress" aria-valuemin={0} aria-valuemax={order.length} aria-valuenow={done}>
			<i style="transform: scaleX({done / Math.max(1, order.length)})"></i>
		</div>

		<div class="work" class:with-guide={guideOpen}>
			<div class="main-col">
				{#if store.pass === 1 && pass1Done && store.pass1_finished_at}
					<p class="notice" role="status"><Icon name="met" /><span>Pass 1 is complete ({file.reports.length} of {file.reports.length}, finished {hhmm(Date.parse(store.pass1_finished_at))}). Download the labels and save them as <b>data/labels/blind_test.json</b>. You can still revise any report below.</span></p>
				{/if}
				{#if current}
					<section class="panel report-card" aria-labelledby="rep-id">
						<div class="rep-head">
							<h2 id="rep-id" class="num">{current.id}</h2>
							<span class="muted num">{index + 1} of {order.length}{#if store.labels[store.pass][current.id]} · labelled{/if}</span>
						</div>
						<p class="report" tabindex="-1" bind:this={textEl}>{current.text}</p>
					</section>

					<section class="panel picks" aria-label="Label">
						<fieldset>
							<legend>Category <span class="keys"><span class="kbd">1</span>–<span class="kbd">6</span></span></legend>
							<div class="opts opts-3">
								{#each CATEGORIES as c, i (c)}
									<button type="button" class="opt" data-pick aria-pressed={draft.category === c} onclick={() => (draft.category = c)}><span class="kbd">{i + 1}</span>{CATEGORY_NAME[c]}</button>
								{/each}
							</div>
						</fieldset>
						<fieldset>
							<legend>Urgency <span class="keys"><span class="kbd">u</span> <span class="kbd">r</span></span></legend>
							<div class="opts opts-2">
								<button type="button" class="opt" data-pick aria-pressed={draft.urgency === 'urgent'} onclick={() => (draft.urgency = 'urgent')}><span class="kbd">u</span><Icon name="urgent" />Urgent</button>
								<button type="button" class="opt" data-pick aria-pressed={draft.urgency === 'routine'} onclick={() => (draft.urgency = 'routine')}><span class="kbd">r</span><Icon name="routine" />Routine</button>
							</div>
						</fieldset>
						<fieldset>
							<legend>Destination <span class="keys"><span class="kbd">a</span>–<span class="kbd">f</span></span></legend>
							<div class="opts opts-3">
								{#each DESTINATIONS as d, i (d)}
									<button type="button" class="opt" data-pick aria-pressed={draft.destination === d} onclick={() => (draft.destination = d)}><span class="kbd">{DEST_KEYS[i]}</span>{DESTINATION_NAME[d]}</button>
								{/each}
							</div>
						</fieldset>
						<p class="err-slot" aria-live="polite">{#if hint}<span class="field-error"><Icon name="info" />{hint}</span>{/if}</p>
						<div class="nav-row">
							<button class="btn" type="button" onclick={() => go(index - 1)} disabled={index === 0}><Icon name="back" />Previous <span class="kbd">←</span></button>
							<button class="btn" type="button" onclick={() => go(index + 1)} disabled={index >= order.length - 1}>Next <span class="kbd">→</span></button>
							<button class="btn btn-primary save" type="button" onclick={save}>Save and next <span class="kbd kbd-on">Enter</span></button>
						</div>
					</section>
				{/if}
			</div>

			<aside class="guide" aria-labelledby="guide-h">
				<button class="btn guide-toggle" type="button" aria-expanded={guideOpen} aria-controls="guide-body" onclick={() => (guideOpen = !guideOpen)}>
					<Icon name="book" /><span id="guide-h">{guideOpen ? 'Hide label guide' : 'Show label guide'}</span><span class="kbd">g</span>
				</button>
				{#if guideOpen}
					<div class="panel guide-body" id="guide-body">
						<h2>Label guide: quick reference</h2>
						<p class="codes">{#each CATEGORY_CODES as s, i (i)}{#if s.code}<b>{s.text}</b>{:else}{s.text}{/if}{/each}</p>
						<table>
							<thead><tr><th scope="col">Step</th><th scope="col">Rule</th><th scope="col">Decide</th></tr></thead>
							<tbody>
								{#each QUICK_REFERENCE as r, i (i)}
									<tr class:first={!!r.step}>
										<th scope="row">{r.step}</th>
										<td class="rule">{r.rule}</td>
										<td>{#each r.decide as s, j (j)}{#if s.code}<b>{s.text}</b>{:else}{s.text}{/if}{/each}</td>
									</tr>
								{/each}
							</tbody>
						</table>
					</div>
				{/if}
			</aside>
		</div>
	{/if}
</Shell>

<style>
	.intro {
		color: var(--text-2);
		font-size: var(--t-small);
		max-width: 80ch;
	}
	.passbar {
		display: flex;
		align-items: center;
		gap: var(--s3) var(--s4);
		flex-wrap: wrap;
		margin-bottom: var(--s3);
	}
	.passbar .btn {
		margin-left: auto;
	}
	.tabs {
		display: inline-flex;
		background: var(--surface-2);
		border-radius: var(--r-ctl);
		padding: 3px;
		gap: 2px;
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
	}
	.tabs button[aria-pressed='true'] {
		background: var(--surface);
		color: var(--text);
		box-shadow: 0 1px 2px rgb(0 0 0 / 0.12);
	}
	.tabs button:disabled {
		cursor: not-allowed;
	}
	.count {
		font-weight: 500;
	}
	.unlock {
		margin: 0;
		font-size: var(--t-row);
		color: var(--text-2);
	}
	.progress {
		height: 6px;
		background: var(--surface-2);
		border-radius: 3px;
		margin-bottom: var(--s5);
		overflow: hidden;
	}
	.progress i {
		display: block;
		height: 100%;
		background: var(--accent);
		transform-origin: left;
		transition: transform var(--dur) var(--ease);
	}
	.work {
		display: grid;
		grid-template-columns: minmax(0, 1fr) auto;
		gap: var(--s5);
		align-items: start;
	}
	.work.with-guide {
		grid-template-columns: minmax(0, 1fr) minmax(320px, 440px);
	}
	.main-col {
		display: flex;
		flex-direction: column;
		gap: var(--s4);
		min-width: 0;
	}
	.main-col > .panel + .panel {
		margin-top: 0;
	}
	.rep-head {
		display: flex;
		align-items: baseline;
		justify-content: space-between;
		gap: var(--s3);
		font-size: var(--t-row);
	}
	.report {
		font-size: var(--t-body);
		line-height: 1.65;
		max-width: 68ch;
		margin: 0;
		outline: none;
		white-space: pre-line;
	}
	fieldset {
		border: 0;
		padding: 0;
		margin: 0 0 var(--s4);
	}
	legend {
		font-size: var(--t-row);
		font-weight: 650;
		margin-bottom: var(--s2);
		display: flex;
		gap: var(--s2);
		align-items: center;
	}
	.keys {
		font-weight: 500;
		color: var(--text-2);
	}
	.opts {
		display: grid;
		gap: var(--s2);
	}
	.opts-3 {
		grid-template-columns: repeat(3, minmax(0, 1fr));
	}
	.opts-2 {
		grid-template-columns: repeat(2, minmax(0, 1fr));
		max-width: 420px;
	}
	.opt {
		display: flex;
		align-items: center;
		gap: var(--s2);
		min-height: 44px;
		padding: 0 var(--s3);
		border: 1px solid var(--ctl-border);
		border-radius: var(--r-ctl);
		background: var(--surface);
		font-size: var(--t-small);
		font-weight: 500;
		text-align: left;
		cursor: pointer;
		transition: background-color var(--dur) var(--ease);
	}
	.opt:hover {
		background: var(--surface-2);
	}
	/* Selected: accent tint + accent edge + bold, so it does not rely on colour alone. */
	.opt[aria-pressed='true'] {
		background: var(--accent-tint);
		border-color: var(--accent);
		box-shadow: inset 0 0 0 1px var(--accent);
		font-weight: 650;
	}
	.opt[aria-pressed='true'] .kbd {
		background: var(--accent);
		color: var(--on-accent);
		border-color: var(--accent);
	}
	.err-slot {
		min-height: 1.4em;
		margin: 0 0 var(--s2);
	}
	.nav-row {
		display: flex;
		gap: var(--s2);
		flex-wrap: wrap;
	}
	.save {
		margin-left: auto;
	}
	.kbd-on {
		background: transparent;
		color: var(--on-accent);
		border-color: color-mix(in srgb, var(--on-accent) 60%, transparent);
	}
	.guide {
		position: sticky;
		top: var(--s4);
		display: flex;
		flex-direction: column;
		gap: var(--s2);
		align-items: stretch;
		max-height: calc(100vh - var(--s6));
	}
	.guide-toggle {
		justify-content: flex-start;
	}
	.guide-toggle .kbd {
		margin-left: auto;
	}
	.guide-body {
		overflow: auto;
		padding: var(--s4);
	}
	.codes {
		font-size: var(--t-caption);
		color: var(--text-2);
	}
	.guide-body table {
		font-size: var(--t-caption);
	}
	.guide-body th,
	.guide-body td {
		padding: 6px 6px;
		vertical-align: top;
		border-bottom: 1px solid var(--sep);
		white-space: normal;
		line-height: 1.45;
	}
	.guide-body th[scope='row'] {
		color: var(--text);
		font-weight: 650;
	}
	.guide-body tr.first td,
	.guide-body tr.first th {
		border-top: 1px solid var(--text-2);
	}
	.guide-body .rule {
		font-weight: 650;
		white-space: nowrap;
	}

	@media (max-width: 1023px) {
		.work,
		.work.with-guide {
			grid-template-columns: minmax(0, 1fr);
		}
		.guide {
			position: static;
			max-height: none;
			order: -1;
		}
	}
	@media (max-width: 599px) {
		.opts-3 {
			grid-template-columns: repeat(2, minmax(0, 1fr));
		}
		.opt .kbd,
		legend .keys,
		.nav-row .kbd,
		.guide-toggle .kbd {
			display: none;
		}
		.passbar .btn {
			margin-left: 0;
		}
		.tabs button,
		.btn {
			min-height: 44px;
		}
		.save {
			width: 100%;
			margin-left: 0;
			order: -1;
		}
	}
</style>
