import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vite';

export default defineConfig({
	plugins: [sveltekit()],
	// The Labeller reads docs/label-guide.md from the repo root at build time.
	server: { fs: { allow: ['..'] } }
});
