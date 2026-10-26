# Static Svelte demo on frozen, committed predictions

The demo is a static Svelte app on GitHub Pages that reads frozen prediction and evaluation JSON committed to the repo, with Reviewer Actions kept in the browser. It works with no API key, assessors can't run up cost, and the numbers in the demo are byte-for-byte the ones the eval scripts reproduce. The same app hosts the blind-labelling mode.

## Considered Options

- Streamlit Community Cloud or a Hugging Face Space: faster to build, but it offers little design control and needs a running Python server, which can be asleep when the assessor opens the link.

## Consequences

Triaging a new report live needs a key and is a stretch goal behind a serverless function; the core demo never calls an API.
