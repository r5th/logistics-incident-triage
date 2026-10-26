<script lang="ts">
	import { page } from '$app/state';
	import { resolve } from '$app/paths';
</script>

<svelte:head><title>Not found · Incident triage</title></svelte:head>

<main class="err">
	<h1>{page.status === 404 ? 'This page does not exist' : 'Something went wrong'}</h1>
	<p>{page.status === 404 ? 'Check the address, or start from the Queue.' : 'Reload the page to try again.'}</p>
	<a class="btn btn-primary" href={resolve('/')}>Go to the Queue</a>
</main>

<style>
	.err {
		max-width: 60ch;
		margin: 15vh auto;
		padding: 0 var(--s5);
	}
	h1 {
		margin-bottom: var(--s3);
	}
</style>
