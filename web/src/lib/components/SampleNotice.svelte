<script lang="ts">
	import Icon from './Icon.svelte';
	let { what = 'reports and numbers' }: { what?: string } = $props();
</script>

<p class="notice" role="note">
	<Icon name="info" />
	<span><b>Sample data.</b> These {what} are made from build-split Scenarios so the screens can be checked before the real predictions are exported. They are not results.</span>
</p>
