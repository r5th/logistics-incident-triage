# Straive Research and Logistics Incident-Triage Prototype Plan

**Research date:** 26 October 2026  
**Status:** Research and implementation plan only. No prototype, evaluation results, user-feedback findings, or production savings are claimed here.

> **Provenance:** produced by ChatGPT at the author's request; saved verbatim except for this note.
> Companion note: [straive-values.md](straive-values.md) (GPT-6.1 Sol via Claude Code).
>
> **Correction (checked 2026-10-26 by Claude Code against the source):** §1 says the Smart Triage
> Engine involves "human approval, exception handling, and traceability". On the
> [AI customer experience](https://www.straive.com/ai-customer-experience/) page the Smart Triage
> Engine sits in *Tier 1 (Autonomous AI Resolution)* and is described only as identifying intent,
> classifying, prioritising and routing. Human approval, exception/escalation handling and
> traceability are separate *Tier 1.5 (AI Resolution with Human Oversight)* capabilities.

## Conclusion

Build a small, auditable logistics incident-triage system—not a general-purpose chatbot. Its value should be demonstrated through correct routing, detection of urgent incidents, sensible human review, and reproducible measurements of mistakes, latency, and cost. A rules baseline and one structured-output language-model approach are sufficient to make a credible comparison; a multi-agent architecture is unnecessary for this scope.

The strongest submission will connect a clearly bounded operational problem to evidence that another person can reproduce. Keep report classification, urgency, and destination separate, make uncertain cases visible, and demonstrate how a stricter missed-urgent policy changes the balance between dangerous misses and human-review workload.

## 1. What the research supports

These are source-based findings, distinct from the proposed implementation below:

- **Company context.** Straive describes enterprise data, analytics, and AI services across sectors including finance, education, research, and manufacturing. Its positioning supports a workflow-oriented framing rather than a model-only demonstration. [Straive](https://www.straive.com/)
- **Closest workflow analogue.** Straive's customer-experience offering describes a Smart Triage Engine involving intent identification, classification, prioritization, and routing, with human approval, exception handling, and traceability. This is relevant evidence of a triage pattern, not proof of a specific logistics deployment. [AI customer experience](https://www.straive.com/ai-customer-experience/)
- **Operational visibility analogue.** Straive's IT and technology operations material includes incident visualization, tracking, and dashboards. This supports the usefulness of a visible incident queue and decision history, but is ITSM evidence rather than logistics-specific evidence. [IT and tech operations](https://www.straive.com/it-and-tech-ops/)
- **Engineering signals—not the assessment rubric.** An experienced AI Engineer vacancy emphasizes confidence and source traceability, human-in-the-loop controls, auditability, retries, validation, secrets management, regression testing, and cost. These are useful quality signals, but the vacancy is not an internship marking guide and should not be presented as one. [Official AI Engineer vacancy](https://www.straive.com/careers/job-postings/job-description/?id=a6a0b266107183)

These sources help explain why an operationally useful, inspectable prototype is appropriate. They do not establish Straive's internal logistics taxonomy, production architecture, preferred technology stack, or undisclosed assessment expectations.

## 2. User-provided requirements

The following faithfully restates the supplied brief; it is not a quotation from Straive's website, and none of these items is marked complete.

### Problem and evidence

- Help a logistics operator classify incoming incident reports, route urgent incidents, and identify cases needing human review.
- Use at least **300 documented, nonconfidential reports** with clear provenance.
- Have labels for at least **50 reports independently reviewed**.
- Compare at least **two approaches**, including a simple baseline.
- Evaluate quality, costly misroutes, latency, cost, mistakes, and abstention or human-review behavior.
- Show a changed requirement, such as a new category or a stricter penalty for missing urgent incidents.

### Submission

- Provide a **public GitHub repository** containing the prototype, with a demo link or reproducible run instructions. Link the live demo in the README when available.
- Include data provenance, evaluation scripts and results, a one-page business summary, and attribution for collaborators and AI assistance.
- Include user feedback if possible, clearly identifying who reviewed what and the limits of that feedback.
- Keep the repository accessible after the deadline.

### Assessment distinctions

Part B has four equally weighted criteria worth **10 points each**, for **40 points total**: problem framing; correctness; reproducible evidence and cost; and demo. The user-provided submission screenshot confirms that the URL field carries **zero automatic marks**: a valid URL alone earns neither project-quality nor walkthrough credit. The **live walkthrough carries 10 points separately**; do not fold those points into Part B's 40-point total.

The supplied material does not establish a deadline, required stack, or budget. Confirm those constraints before committing to a hosting plan or paid API usage.

## 3. Recommended scope and decision design

Use a bounded **road-freight operations** scenario, with a single operator and a small set of plausible destination teams. This is a design recommendation, not an additional requirement or a claim about Straive's customers.

A workable starting taxonomy has six categories: vehicle breakdown, delivery delay, shipment damage, missing shipment, documentation issue, and safety incident. Write definitions, exclusions, and difficult examples before generating or labeling reports. If a report mentions multiple issues, specify how the primary category is selected and how secondary hazards are retained.

Treat three decisions independently:

| Decision | Question | Example output |
|---|---|---|
| Category | What happened? | Vehicle breakdown |
| Urgency | How quickly does this need attention? | Urgent |
| Destination | Who should handle it? | Fleet support |

A breakdown is not automatically urgent; circumstances determine urgency. Conversely, a delivery-delay report can contain a safety concern. Define the policy explicitly rather than hiding urgency inside a category label.

Use a consistent output schema containing category, urgency, proposed destination, supporting report excerpts, missing information, and a review-required flag with reasons. Evidence must come from the report rather than invented context. Missing critical information, contradictory statements, unsupported categories, and invalid output should trigger review or a documented fallback.

This prototype recommends routing and escalation; it must not dispatch responders, change shipments, or perform live remediation.

## 4. Data, provenance, and independent review

Plan for **300 reports**, split into **180 development, 60 validation, and 60 held-out test reports**. These counts are recommendations that meet the minimum, not prescribed assessment splits. Use development data to build rules and prompts; use validation data for thresholds and policy selection; reserve test data for the final frozen comparison.

Split at the **underlying scenario level**. Near-duplicate reports, paraphrases of one incident, and variants generated from the same scenario must stay in one split. Otherwise, apparent performance can reflect memorization rather than generalization.

Record each report's identifier, origin, creation or collection method, permission or license where relevant, synthetic status, scenario identifier, and split. For synthetic data, document the generation process and its limitations. Do not imply that synthetic reports represent the frequency or complexity of real logistics incidents.

Create a written annotation guide covering category, urgency, destination, review need, and ambiguity. Include routine, urgent, multi-issue, incomplete, and contradictory cases. Ensure urgent examples are present in each evaluation split, while documenting that any chosen class distribution is a design choice rather than an operational estimate.

Have a second human independently label all **60 test reports**, without seeing the initial labels or model predictions. Preserve initial labels, independent labels, disagreements, and adjudicated outcomes. Explain who reviewed the data and how disagreements were resolved. Freeze the evaluation labels before examining test predictions.

A second prompt to the same AI generator is not independent human review. If a nonhuman interpretation of the brief is necessary, ask the organizer rather than silently treating automated relabeling as equivalent. Reviewer access is an important early dependency.

## 5. Two approaches and a fair comparison

### A. Simple rules baseline

Implement transparent keyword and pattern rules, a small destination lookup, and explicit defaults. Handle obvious safety language, common incident terms, and missing information. The baseline should be genuinely executable and reasonably tuned—not intentionally weak.

### B. Structured-output language-model challenger

Use one model with the same report content and the same category definitions. Validate outputs against the schema and allowed values. Apply bounded retries for recoverable failures, log attempts, and send unresolved failures to review. Record the model identifier, prompt version, relevant settings, and dependency versions.

Both approaches must receive the same permitted inputs and be evaluated on the same held-out reports. Do not give the challenger hidden labels or additional scenario metadata. Account for all model calls, including retries and invalid responses. Store secrets outside the repository and document how to supply them safely.

Model-reported confidence is not a calibrated probability. If it is used at all, test its relationship to errors on validation data. Evidence completeness, rule conflicts, and schema validity can provide more interpretable review triggers.

## 6. Evaluation and changed-requirement experiment

Report more than overall accuracy:

- **Classification and routing:** per-class results, macro-averaged metrics, and confusion matrices for category and destination.
- **Urgency:** urgent-case recall, counts of missed urgent incidents, and the actual dangerous misses with brief explanations.
- **Operational errors:** cost-weighted mistakes under an explicitly hypothetical penalty policy, alongside unweighted counts.
- **Human review:** abstention rate, automatic-routing coverage, and error rate among automatically routed cases.
- **Reliability and speed:** API failures, invalid outputs, retries, median latency, and a tail-latency measure such as the 95th percentile, with sample sizes.
- **Cost:** measured API cost per report and for the evaluation, plus separately stated assumptions for reviewer time and cost.

Do not present an illustrative penalty policy as an industry standard. Explain why missing an urgent safety case is assigned a larger penalty than a routine routing correction. Include review burden so that sending every report to a human does not appear to be a cost-free optimum. Keep measured API expenditure separate from assumed labor costs and projected business impacts.

For the required change, choose a **stricter missed-urgent penalty**. Version the original and revised policies. Select any revised thresholds or rules on validation data, freeze both policies, then compare them on the same held-out test set. Show changes in missed urgent incidents, automatic-routing errors, review workload, latency, and total modeled cost.

Do not tune again after inspecting test failures. Report counts alongside rates: 60 test reports cannot support strong reliability claims. Discuss small-sample limitations and label ambiguity. If the challenger or revised policy does not improve the intended outcome, report that honestly and explain the trade-off rather than selecting only favorable examples.

## 7. Demo and reproducible repository

Build a compact queue with an incident-detail view showing the original report, category, urgency, proposed team, supporting evidence, missing information, and review reasons. Provide **approve, override, and escalate** controls with a local decision history. Make clear that these demonstrate workflow decisions rather than actual operational actions.

Walk through one routine case, one urgent case, and one ambiguous case. Show a failure or override and the changed-policy comparison, not only successful predictions. If possible, ask a logistics-informed reviewer or representative user to try the workflow and record actionable feedback without claiming broad validation.

Suggested repository layout:

```text
README.md
data/                 # Reports, provenance, split manifest, reviewed labels
docs/                 # Label guide, business summary, limitations, attribution
src/                  # Baseline, challenger, schema, routing and review policy
eval/                 # Evaluation and policy-comparison scripts
results/              # Frozen metrics, configurations, error analysis
demo/                 # Queue and incident-detail interface
tests/                # Schema, policy, fallback and regression checks
```

Document environment setup, dependencies, configuration, dataset access, baseline execution, challenger execution, evaluation, and demo startup. State what requires an API key and what can run without one. Test instructions from a clean environment, including expected outputs and a transparent estimate of paid-run cost.

Inspect files **and Git history** before publishing. Exclude credentials, personal information, client logs, and confidential data. Credit collaborators and AI assistance concretely, including generation, coding, editing, or labeling support as applicable.

The one-page business summary should cover the problem, proposed workflow, measured results when available, review burden, risks, assumptions, and the next pilot. Do not claim realized savings without operational evidence.

## 8. Build order and final checklist

1. Confirm constraints and secure an independent reviewer; finalize scope and label guide.
2. Create the documented dataset and scenario-level splits; complete review and adjudication.
3. Implement and test the rules baseline, then the validated challenger.
4. Freeze configurations; run evaluation and the changed-policy experiment.
5. Build the demo around observed successes, failures, and review decisions.
6. Write the business summary, provenance, limitations, and attribution; verify reproducibility.

Before submission, check that all 300 reports are documented, at least 50 labels have independent review, both approaches run, evaluation includes cost and mistakes, the requirement change is evidenced, and the demo or run instructions work. Confirm the public repository is accessible, required presentation material is prepared, and access will remain available after the deadline. These are completion checks for future work—not claims that the work has already been done.
