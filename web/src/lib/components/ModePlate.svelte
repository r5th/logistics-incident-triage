<script lang="ts">
	// Routing Mode plate: green Auto-route or yellow Review diversion plate, always icon + word.
	import type { RoutingMode } from '$lib/data/types';
	import Icon from './Icon.svelte';
	let { mode, large = false }: { mode: RoutingMode; large?: boolean } = $props();
</script>

{#if mode === 'auto'}
	<span class="plate plate-auto" class:plate-lg={large}><Icon name="auto" />Auto-route</span>
{:else}
	<span class="plate plate-review" class:plate-lg={large}><Icon name="review" />Review</span>
{/if}
