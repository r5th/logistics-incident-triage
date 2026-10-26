<script lang="ts" module>
	// One stroke icon set: Lucide geometry (24 grid, 2px round stroke), inlined so there is no
	// runtime dependency. "review" is Lucide's diamond with an exclamation mark, the diversion
	// plate's symbol. Icons sit beside a visible label, so they are hidden from assistive tech.
	const PATHS = {
		urgent: ['M10.3 3.9 1.8 18a2 2 0 0 0 1.7 3h17a2 2 0 0 0 1.7-3L13.7 3.9a2 2 0 0 0-3.4 0Z', 'M12 9v4', 'M12 17h.01'],
		routine: ['M12 3a9 9 0 1 0 0 18 9 9 0 0 0 0-18Z', 'M12 7v5l3 2'],
		arrow: ['M5 12h14', 'm13 6 6 6-6 6'],
		review: ['M12 2 22 12 12 22 2 12Z', 'M12 8v5', 'M12 16h.01'],
		auto: ['M5 12h14', 'm13 6 6 6-6 6', 'M5 6v12'],
		check: ['M20 6 9 17l-5-5'],
		override: ['M17 3a2.8 2.8 0 0 1 4 4L7.5 20.5 2 22l1.5-5.5Z'],
		escalate: ['m17 11-5-5-5 5', 'm17 18-5-5-5 5'],
		search: ['M11 4a7 7 0 1 0 0 14 7 7 0 0 0 0-14Z', 'm21 21-4.3-4.3'],
		queue: ['M3 6h18', 'M3 12h18', 'M3 18h12'],
		results: ['M3 3v18h18', 'm7 15 4-4 3 3 5-6'],
		label: ['M12 20h9', 'M16.5 3.5a2.1 2.1 0 0 1 3 3L7 19l-4 1 1-4Z'],
		about: ['M12 3a9 9 0 1 0 0 18 9 9 0 0 0 0-18Z', 'M12 16v-4', 'M12 8h.01'],
		back: ['m15 18-6-6 6-6'],
		chev: ['m6 9 6 6 6-6'],
		x: ['M18 6 6 18', 'm6 6 12 12'],
		undo: ['M9 14 4 9l5-5', 'M4 9h10.5a5.5 5.5 0 0 1 0 11H11'],
		download: ['M12 15V3', 'm7 10 5 5 5-5', 'M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4'],
		book: ['M12 7v14', 'M3 18a1 1 0 0 1-1-1V4a1 1 0 0 1 1-1h5a4 4 0 0 1 4 4 4 4 0 0 1 4-4h5a1 1 0 0 1 1 1v13a1 1 0 0 1-1 1h-6a3 3 0 0 0-3 3 3 3 0 0 0-3-3Z'],
		met: ['M12 3a9 9 0 1 0 0 18 9 9 0 0 0 0-18Z', 'm9 12 2 2 4-4'],
		missed: ['M12 3a9 9 0 1 0 0 18 9 9 0 0 0 0-18Z', 'm15 9-6 6', 'm9 9 6 6'],
		menu: ['M4 6h16', 'M4 12h16', 'M4 18h16'],
		info: ['M12 3a9 9 0 1 0 0 18 9 9 0 0 0 0-18Z', 'M12 16v-4', 'M12 8h.01'],
		lock: ['M5 11h14v10H5Z', 'M7 11V7a5 5 0 0 1 10 0v4'],
		external: ['M15 3h6v6', 'M10 14 21 3', 'M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6'],
		table: ['M3 3h18v18H3Z', 'M3 9h18', 'M3 15h18', 'M9 3v18'],
		chart: ['M3 3v18h18', 'm7 15 4-4 3 3 5-6']
	} as const;
	export type IconName = keyof typeof PATHS;
</script>

<script lang="ts">
	let { name, size, class: cls = '' }: { name: IconName; size?: number; class?: string } = $props();
</script>

<svg
	class="ic {cls}"
	viewBox="0 0 24 24"
	width={size}
	height={size}
	fill="none"
	stroke="currentColor"
	stroke-width="2"
	stroke-linecap="round"
	stroke-linejoin="round"
	aria-hidden="true"
	focusable="false"
>
	{#each PATHS[name] as d (d)}<path {d} />{/each}
</svg>
