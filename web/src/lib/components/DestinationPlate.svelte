<script lang="ts">
	// Signature move: a white direction plate, the same for all six Destinations.
	import type { Destination } from '$lib/data/types';
	import { DESTINATION_NAME } from '$lib/vocab';
	import Icon from './Icon.svelte';
	let { destination, large = false }: { destination: Destination; large?: boolean } = $props();
</script>

<span class="plate plate-dest" class:plate-lg={large}>{DESTINATION_NAME[destination]}<Icon name="arrow" /></span>
