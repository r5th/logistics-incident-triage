# Logistics Incident Triage

Triage of incident reports for one road-freight operator: deciding where attention should go first, not deciding the outcome.

## Reports and labels

**Incident Report**:
A free-text account of something that went wrong on a road-freight job, as submitted by a driver, depot or customer.
_Avoid_: Ticket, case, message

**Scenario**:
One underlying incident from which one or more Incident Reports are written as paraphrases; the unit by which data is split.
_Avoid_: Template, seed (as a data unit)

**Label**:
The reference answer for an Incident Report: its Category, Urgency and Destination.
_Avoid_: Ground truth, tag

**Blind Label**:
A Label given by a human who could see neither the seeded Label nor any prediction.
_Avoid_: Review, relabel

## Triage decisions

**Category**:
What happened, as one of six: vehicle breakdown, delivery delay, shipment damage, missing shipment, documentation issue, safety incident.
_Avoid_: Type, class, intent

**Urgency**:
How quickly a report needs attention, either urgent or routine; decided independently of Category.
_Avoid_: Priority, severity

**Destination**:
The team that should handle a report: Fleet Support, Customer Desk, Claims, Security & Investigations, Compliance, or Safety Desk.
_Avoid_: Queue, owner, assignee

**Evidence**:
Sentences quoted verbatim from the Incident Report that support a triage decision.
_Avoid_: Rationale, explanation

## Routing and review

**Routing Mode**:
Whether a report is auto-routed to its Destination or held for review; never itself a Destination.
_Avoid_: Abstention (as a label), escalation

**Auto-route**:
The Routing Mode in which the triage decisions go straight to the Destination without a human (Straive's Tier 1).
_Avoid_: Autonomous, straight-through

**Review**:
The Routing Mode in which a human sees the proposed decisions and Evidence before anything is routed (Straive's Tier 1.5).
_Avoid_: Abstain, human-in-the-loop

**Review Trigger**:
A named, inspectable reason a report was sent to Review, such as missing location, conflicting signals, or low probability.
_Avoid_: Flag, uncertainty

**Reviewer Action**:
What a reviewer does with a report in Review: accept, override, or escalate.
_Avoid_: Approve, disposition

**Missed Urgent**:
An urgent report that was auto-routed as routine; the costliest error.
_Avoid_: False negative (in prose)

**Policy**:
A versioned set of thresholds, Review Triggers and error costs that decides Routing Mode; v1 and v2 differ only in the Missed Urgent cost.
_Avoid_: Config, ruleset

**Operating Point**:
One choice of Policy thresholds, described by its review rate and Missed Urgent count.
_Avoid_: Setting, threshold (alone)
