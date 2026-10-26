<script lang="ts">
	import { onMount } from 'svelte';
	import { page } from '$app/state';
	import { resolve } from '$app/paths';
	import Shell from '$lib/components/Shell.svelte';
	import { incidents } from '$lib/data/store.svelte';
	import { actions } from '$lib/actions.svelte';
	import { view } from '$lib/context.svelte';
	import { rowsFor } from '$lib/rows';

	let { children } = $props();

	onMount(() => {
		incidents.start();
		actions.load();
	});

	const awaiting = $derived(
		incidents.data
			? rowsFor(incidents.data, view.approach, view.policy, (id) =>
					actions.last(view.approach, view.policy, id)
				).filter((r) => r.status === 'awaiting').length
			: null
	);

	const TITLES: Record<string, string> = {
		'/(app)': 'Queue',
		'/(app)/results': 'Results',
		'/(app)/about': 'About',
		'/(app)/incident/[id]': 'Incident Report'
	};
	const title = $derived(TITLES[page.route.id ?? ''] ?? 'Incident triage');
	const back = $derived(
		page.route.id === '/(app)/incident/[id]' ? { href: resolve('/') + view.query, label: 'Queue' } : null
	);
</script>

<Shell {title} {awaiting} {back}>
	{@render children()}
</Shell>
