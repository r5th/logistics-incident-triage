<script lang="ts">
	import '../app.css';
	import { onMount } from 'svelte';
	import { view } from '$lib/context.svelte';
	let { children } = $props();
	onMount(() => {
		view.mounted = true;
	});
</script>

{@render children()}
