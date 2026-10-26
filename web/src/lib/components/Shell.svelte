<script lang="ts">
	// Navigation: rail ≥ 1024px, app bar with a menu 600–1023px, app bar + tab bar < 600px
	// (HIG › Layout [web] breakpoints; HIG › Tab bars: navigation only, always visible, labelled).
	import type { Snippet } from 'svelte';
	import { page } from '$app/state';
	import { resolve } from '$app/paths';
	import { view } from '$lib/context.svelte';
	import { APPROACH_LINE } from '$lib/vocab';
	import type { Approach, PolicyVersion } from '$lib/data/types';
	import Icon, { type IconName } from './Icon.svelte';

	let {
		title,
		awaiting = null,
		showContext = true,
		back = null,
		children
	}: {
		title: string;
		awaiting?: number | null;
		showContext?: boolean;
		back?: { href: string; label: string } | null;
		children: Snippet;
	} = $props();

	let menuOpen = $state(false);

	type NavItem = { key: string; href: string; label: string; icon: IconName; carry: boolean };
	const items = $derived<NavItem[]>([
		{ key: 'queue', href: resolve('/'), label: 'Queue', icon: 'queue', carry: true },
		{ key: 'results', href: resolve('/results'), label: 'Results', icon: 'results', carry: true },
		{ key: 'label', href: resolve('/label'), label: 'Labeller', icon: 'label', carry: false },
		{ key: 'about', href: resolve('/about'), label: 'About', icon: 'about', carry: true }
	]);

	const current = $derived.by(() => {
		const id = page.route.id ?? '';
		if (id.includes('/incident') || id === '/(app)') return 'queue';
		if (id.includes('/results')) return 'results';
		if (id.includes('/label')) return 'label';
		if (id.includes('/about')) return 'about';
		return '';
	});

	const link = (it: NavItem) => it.href + (it.carry ? view.query : '');
	const APPROACHES: Approach[] = ['A', 'B', 'C'];
	const POLICIES: PolicyVersion[] = ['v1', 'v2'];
</script>

{#snippet contextControls(onShell: boolean)}
	<div class="ctx" class:ctx-onshell={onShell}>
		<div>
			<div class="ctx-label" id="ctx-a-{onShell}">Approach</div>
			<div class="seg" role="group" aria-labelledby="ctx-a-{onShell}">
				{#each APPROACHES as a (a)}
					<button type="button" aria-pressed={view.approach === a} onclick={() => view.set({ approach: a })}>{a}</button>
				{/each}
			</div>
			<p class="ctx-line">{APPROACH_LINE[view.approach]}</p>
		</div>
		<div>
			<div class="ctx-label" id="ctx-p-{onShell}">Policy</div>
			<div class="seg" role="group" aria-labelledby="ctx-p-{onShell}">
				{#each POLICIES as p (p)}
					<button type="button" aria-pressed={view.policy === p} onclick={() => view.set({ policy: p })}>{p}</button>
				{/each}
			</div>
			<p class="ctx-line">v1 and v2 differ only in the cost of a Missed Urgent (20 or 100 reviewer-minutes).</p>
		</div>
	</div>
{/snippet}

<a class="skip" href="#main">Skip to content</a>
<div class="app">
	<nav class="rail" aria-label="Main">
		<a class="brand" href={resolve('/') + view.query}><span class="brand-mark"><Icon name="arrow" /></span>Incident triage</a>
		<ul class="nav">
			{#each items as it (it.key)}
				<li>
					<a href={link(it)} aria-current={current === it.key ? 'page' : undefined}>
						<Icon name={it.icon} />{it.label}
						{#if it.key === 'queue' && awaiting}<span class="badge num" aria-label="{awaiting} awaiting review">{awaiting}</span>{/if}
					</a>
				</li>
			{/each}
		</ul>
		{#if showContext}{@render contextControls(true)}{/if}
		<p class="foot">Synthetic reports. Nothing is dispatched.</p>
	</nav>

	<header class="appbar">
		{#if back}
			<a class="appbar-back" href={back.href}><Icon name="back" /><span>{back.label}</span></a>
		{:else}
			<span class="appbar-title">{title}</span>
		{/if}
		<button
				type="button"
				class="appbar-btn"
				class:nav-only={!showContext}
				aria-expanded={menuOpen}
				aria-controls="appbar-panel"
				onclick={() => (menuOpen = !menuOpen)}
			>
				{#if showContext}<span class="num">{view.approach} · Policy {view.policy}</span>{/if}
				<span class="menu-word"><Icon name={menuOpen ? 'x' : 'menu'} /><span class="visually-hidden">Menu</span></span>
			</button>
	</header>
	{#if menuOpen}
		<div class="appbar-panel" id="appbar-panel">
			<ul class="nav nav-panel">
				{#each items as it (it.key)}
					<li>
						<a href={link(it)} aria-current={current === it.key ? 'page' : undefined} onclick={() => (menuOpen = false)}>
							<Icon name={it.icon} />{it.label}
							{#if it.key === 'queue' && awaiting}<span class="badge num">{awaiting}</span>{/if}
						</a>
					</li>
				{/each}
			</ul>
			{#if showContext}{@render contextControls(true)}{/if}
		</div>
	{/if}

	<main class="main" id="main" tabindex="-1">
		{@render children()}
	</main>

	<nav class="tabbar" aria-label="Main">
		{#each items as it (it.key)}
			<a href={link(it)} aria-current={current === it.key ? 'page' : undefined}>
				<span class="tab-ic"><Icon name={it.icon} />{#if it.key === 'queue' && awaiting}<span class="dot num" aria-label="{awaiting} awaiting review">{awaiting}</span>{/if}</span>
				{it.label}
			</a>
		{/each}
	</nav>
</div>

<style>
	.skip {
		position: absolute;
		left: var(--s3);
		top: -60px;
		z-index: 10;
		background: var(--surface);
		padding: var(--s2) var(--s3);
		border-radius: var(--r-ctl);
	}
	.skip {
		min-height: 44px;
		display: inline-flex;
		align-items: center;
	}
	.skip:focus {
		top: var(--s3);
	}
	.app {
		display: grid;
		grid-template-columns: 232px minmax(0, 1fr);
		min-height: 100vh;
		/* The rail's blue runs the full page height even where the sticky rail ends. */
		background: linear-gradient(to right, var(--shell) 232px, transparent 232px);
	}
	.rail {
		grid-row: 1 / span 3;
		background: var(--shell);
		color: var(--shell-text);
		display: flex;
		flex-direction: column;
		padding: var(--s4) var(--s3);
		gap: var(--s5);
		position: sticky;
		top: 0;
		height: 100vh;
		overflow-y: auto;
	}
	.brand {
		display: flex;
		align-items: center;
		gap: var(--s2);
		font-weight: 650;
		font-size: var(--t-body);
		padding: var(--s1) var(--s2);
		color: var(--shell-text);
		text-decoration: none;
		border-radius: var(--r-ctl);
	}
	.brand-mark {
		width: 22px;
		height: 22px;
		border: 2px solid currentColor;
		border-radius: 4px;
		display: grid;
		place-items: center;
	}
	.brand-mark :global(.ic) {
		width: 14px;
		height: 14px;
	}
	.nav {
		display: flex;
		flex-direction: column;
		gap: 2px;
		list-style: none;
		margin: 0;
		padding: 0;
	}
	.nav a {
		display: flex;
		align-items: center;
		gap: var(--s3);
		padding: var(--s2) var(--s3);
		min-height: 40px;
		border-radius: var(--r-ctl);
		color: var(--shell-text-2);
		text-decoration: none;
		font-size: var(--t-small);
		font-weight: 500;
		transition: background-color var(--dur) var(--ease);
	}
	.nav a:hover {
		background: var(--shell-hover);
		color: var(--shell-text);
	}
	.nav a[aria-current='page'] {
		background: var(--shell-active);
		color: var(--shell-text);
		font-weight: 600;
	}
	.nav :global(.ic) {
		width: 18px;
		height: 18px;
	}
	.rail :global(:focus-visible),
	.appbar :global(:focus-visible),
	.appbar-panel :global(:focus-visible) {
		outline-color: var(--shell-text);
	}
	.badge {
		margin-left: auto;
		background: var(--review);
		color: var(--on-review);
		font-size: var(--t-caption);
		font-weight: 700;
		border-radius: 999px;
		padding: 0 7px;
		line-height: 20px;
	}
	.ctx {
		margin-top: auto;
		display: flex;
		flex-direction: column;
		gap: var(--s4);
		padding: 0 var(--s1);
	}
	.ctx-label {
		font-size: var(--t-caption);
		color: var(--shell-text-2);
		margin-bottom: var(--s1);
		font-weight: 600;
	}
	.ctx-line {
		font-size: var(--t-caption);
		color: var(--shell-text-2);
		margin: 6px 0 0;
		line-height: 1.4;
	}
	.seg {
		display: grid;
		grid-auto-flow: column;
		grid-auto-columns: 1fr;
		background: rgb(0 0 0 / 0.25);
		border-radius: var(--r-ctl);
		padding: 2px;
	}
	.seg button {
		border: 0;
		background: none;
		color: var(--shell-text-2);
		font-size: var(--t-row);
		font-weight: 600;
		min-height: 30px;
		border-radius: 4px;
		cursor: pointer;
		transition: background-color var(--dur) var(--ease);
	}
	.seg button:hover {
		color: var(--shell-text);
		background: var(--shell-hover);
	}
	.seg button[aria-pressed='true'] {
		background: var(--shell-text);
		color: var(--shell);
	}
	.foot {
		font-size: var(--t-caption);
		color: var(--shell-text-2);
		padding: 0 var(--s1);
		margin: 0;
	}
	.main {
		min-width: 0;
		padding: var(--s5) var(--s6) var(--s7);
		outline: none;
	}
	.appbar,
	.tabbar,
	.appbar-panel {
		display: none;
	}

	/* Medium and compact: the rail becomes an app bar. */
	@media (max-width: 1023px) {
		.app {
			display: block;
			background: none;
		}
		.rail {
			display: none;
		}
		.appbar {
			display: flex;
			align-items: center;
			gap: var(--s3);
			background: var(--shell);
			color: var(--shell-text);
			padding: 4px var(--s2) 4px var(--s4);
			min-height: 52px;
			position: sticky;
			top: 0;
			z-index: 5;
		}
		.appbar-title {
			font-size: 1.0625rem;
			font-weight: 650;
		}
		.appbar-back {
			display: inline-flex;
			align-items: center;
			gap: 2px;
			color: var(--shell-text);
			text-decoration: none;
			font-size: var(--t-body);
			font-weight: 600;
			min-height: 44px;
			margin-left: calc(var(--s2) * -1);
			padding-right: var(--s2);
		}
		.appbar-back :global(.ic) {
			width: 22px;
			height: 22px;
		}
		.appbar-btn {
			margin-left: auto;
			display: inline-flex;
			align-items: center;
			gap: var(--s2);
			min-height: 44px;
			min-width: 44px;
			justify-content: center;
			padding: 0 var(--s2);
			background: none;
			border: 0;
			color: var(--shell-text);
			font-size: var(--t-row);
			font-weight: 600;
			cursor: pointer;
			border-radius: var(--r-ctl);
		}
		.appbar-btn > .num {
			border: 1.5px solid var(--shell-text-2);
			border-radius: 6px;
			padding: 4px 8px;
		}
		.menu-word :global(.ic) {
			width: 22px;
			height: 22px;
		}
		.appbar-panel {
			display: block;
			background: var(--shell);
			color: var(--shell-text);
			padding: var(--s2) var(--s4) var(--s4);
			position: sticky;
			top: 52px;
			z-index: 4;
			border-top: 1px solid var(--shell-hover);
		}
		.appbar-panel .ctx {
			margin-top: var(--s4);
			padding: 0;
		}
		.seg button {
			min-height: 44px;
		}
		.nav a {
			min-height: 44px;
		}
		.main {
			padding: var(--s4) var(--s5) var(--s7);
		}
	}

	/* Compact: bottom tab bar for navigation; the menu keeps only Approach and Policy. */
	@media (max-width: 599px) {
		.app {
			padding-bottom: calc(64px + env(safe-area-inset-bottom));
		}
		.nav-panel,
		.nav-only {
			display: none;
		}
		.appbar-panel .ctx {
			margin-top: var(--s2);
		}
		.main {
			padding: var(--s3) var(--s4) var(--s5);
		}
		.tabbar {
			display: grid;
			grid-template-columns: repeat(4, 1fr);
			position: fixed;
			bottom: 0;
			left: 0;
			right: 0;
			background: var(--surface);
			border-top: 1px solid var(--sep);
			padding: 4px 0 calc(4px + env(safe-area-inset-bottom));
			z-index: 5;
		}
		.tabbar a {
			display: flex;
			flex-direction: column;
			align-items: center;
			gap: 2px;
			min-height: 52px;
			justify-content: center;
			font-size: 0.6875rem;
			font-weight: 600;
			color: var(--text-2);
			text-decoration: none;
		}
		.tab-ic {
			position: relative;
			display: inline-flex;
		}
		.tab-ic :global(.ic) {
			width: 22px;
			height: 22px;
		}
		.dot {
			position: absolute;
			top: -4px;
			left: 14px;
			background: var(--review);
			color: var(--on-review);
			box-shadow: 0 0 0 1.5px var(--review-edge);
			font-size: 0.6875rem;
			font-weight: 700;
			border-radius: 999px;
			padding: 0 5px;
			line-height: 16px;
		}
		.tabbar a[aria-current='page'] {
			color: var(--accent);
		}
	}
</style>
