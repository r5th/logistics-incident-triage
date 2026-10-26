<script lang="ts">
	// HIG › Accessibility: convey information with more than colour alone (icon + word).
	import type { Urgency } from '$lib/data/types';
	import Icon from './Icon.svelte';
	let { urgency, large = false }: { urgency: Urgency; large?: boolean } = $props();
</script>

{#if urgency === 'urgent'}
	<span class="urg urg-urgent" class:urg-lg={large}><Icon name="urgent" />Urgent</span>
{:else}
	<span class="urg urg-routine" class:urg-lg={large}><Icon name="routine" />Routine</span>
{/if}
