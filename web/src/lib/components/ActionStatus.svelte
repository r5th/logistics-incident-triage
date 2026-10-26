<script lang="ts">
	import type { ActionKind } from '$lib/actions.svelte';
	import Icon, { type IconName } from './Icon.svelte';
	let { status }: { status: ActionKind | 'awaiting' | null } = $props();
	const SHOW: Record<string, [IconName, string]> = {
		awaiting: ['routine', 'Awaiting review'],
		accept: ['check', 'Accepted'],
		override: ['override', 'Overridden'],
		escalate: ['escalate', 'Escalated']
	};
</script>

{#if status}
	<span class="status" class:status-awaiting={status === 'awaiting'}><Icon name={SHOW[status][0]} />{SHOW[status][1]}</span>
{:else}
	<span class="muted" aria-label="No Reviewer Action: auto-routed">—</span>
{/if}
