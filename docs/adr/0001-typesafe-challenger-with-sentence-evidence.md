# TypeSafe as the AI approach, with Evidence chosen from the report's own sentences

The AI approach uses TypeSafe typed questions (Choice for Category, Urgency and Destination; Noul for Review Triggers) instead of a generative LLM with JSON output. TypeSafe returns calibrated probabilities, so Review thresholds chosen on validation data mean something; a generative model's self-reported confidence does not. TypeSafe has no free-text extraction, so Evidence is a Choice over the report's own sentences, which also means a quote can never be invented.

## Considered Options

- Generative LLM (Gemini or Groq free tier) with schema-validated JSON: rejected because its confidence is uncalibrated and its quotes need checking against the source.
- Both, as three approaches: rejected for time; the third approach is the rules-then-TypeSafe cascade instead.
