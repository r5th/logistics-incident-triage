import adapter from '@sveltejs/adapter-static';
import { vitePreprocess } from '@sveltejs/vite-plugin-svelte';

/** @type {import('@sveltejs/kit').Config} */
const config = {
	preprocess: vitePreprocess(),
	kit: {
		// 404.html lets GitHub Pages serve unknown paths (for example a report id exported later).
		adapter: adapter({ strict: true, fallback: '404.html' }),
		// GitHub Pages serves the repo under /logistics-incident-triage; local dev uses ''.
		paths: { base: process.env.BASE_PATH ?? '', relative: false },
		prerender: { handleMissingId: 'warn' }
	}
};

export default config;
