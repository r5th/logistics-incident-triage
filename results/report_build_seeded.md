# Evaluation

## How to read this

Each Incident Report has a Category, Urgency and Destination. A Policy chooses Auto-route or Review. Missed Urgent counts urgent Incident Reports auto-routed as routine. Costs are reviewer-minute equivalents; intervals resample whole Scenarios (1,000 draws, 95%). Urgency recall ignores Routing Mode. Undefined ratios are zero; unavailable percentiles are null. Latency is in milliseconds using nearest-rank percentiles. API cost uses cached input tokens.

| Approach | Policy | Category accuracy | Destination accuracy | Urgent recall | Review rate | Auto-route coverage | Auto-route error rate | Missed Urgent | Cost / 100 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| A | v1 | 0.96 | 0.96 | 0.9833 | 0.08 | 0.92 | 0.0326 | 1 | 28.5 |
| A | v2 | 0.96 | 0.96 | 0.9833 | 0.08 | 0.92 | 0.0326 | 1 | 68.5 |
| B | v1 | 0.9 | 0.905 | 0.9333 | 0.27 | 0.73 | 0.0959 | 0 | 56.0 |
| B | v2 | 0.9 | 0.905 | 0.9333 | 0.27 | 0.73 | 0.0959 | 0 | 56.0 |
| C | v1 | 0.95 | 0.96 | 0.9833 | 0.09 | 0.91 | 0.0549 | 1 | 35.5 |
| C | v2 | 0.95 | 0.96 | 0.9833 | 0.09 | 0.91 | 0.0549 | 1 | 75.5 |

## A / v1

### Category

Macro-F1: 0.9609

| Label | Precision | Recall | F1 |
| --- | --- | --- | --- |
| vehicle_breakdown | 1.0 | 0.9444 | 0.9714 |
| delivery_delay | 0.8378 | 0.9688 | 0.8986 |
| shipment_damage | 1.0 | 0.9375 | 0.9677 |
| missing_shipment | 0.9697 | 1.0 | 0.9846 |
| documentation_issue | 0.9706 | 0.9167 | 0.9429 |
| safety_incident | 1.0 | 1.0 | 1.0 |

Confusion matrix: rows are Labels; columns are Predictions.

| Label / Prediction | vehicle_breakdown | delivery_delay | shipment_damage | missing_shipment | documentation_issue | safety_incident |
| --- | --- | --- | --- | --- | --- | --- |
| vehicle_breakdown | 34 | 2 | 0 | 0 | 0 | 0 |
| delivery_delay | 0 | 31 | 0 | 0 | 1 | 0 |
| shipment_damage | 0 | 1 | 30 | 1 | 0 | 0 |
| missing_shipment | 0 | 0 | 0 | 32 | 0 | 0 |
| documentation_issue | 0 | 3 | 0 | 0 | 33 | 0 |
| safety_incident | 0 | 0 | 0 | 0 | 0 | 32 |

### Destination

Macro-F1: 0.9618

| Label | Precision | Recall | F1 |
| --- | --- | --- | --- |
| fleet_support | 1.0 | 0.9062 | 0.9508 |
| customer_desk | 0.8958 | 0.9773 | 0.9348 |
| claims | 1.0 | 0.9286 | 0.963 |
| security_investigations | 0.9412 | 1.0 | 0.9697 |
| compliance | 0.9677 | 0.9375 | 0.9524 |
| safety_desk | 1.0 | 1.0 | 1.0 |

Confusion matrix: rows are Labels; columns are Predictions.

| Label / Prediction | fleet_support | customer_desk | claims | security_investigations | compliance | safety_desk |
| --- | --- | --- | --- | --- | --- | --- |
| fleet_support | 29 | 2 | 0 | 0 | 1 | 0 |
| customer_desk | 0 | 43 | 0 | 1 | 0 | 0 |
| claims | 0 | 1 | 26 | 1 | 0 | 0 |
| security_investigations | 0 | 0 | 0 | 32 | 0 | 0 |
| compliance | 0 | 2 | 0 | 0 | 30 | 0 |
| safety_desk | 0 | 0 | 0 | 0 | 0 | 32 |

### Urgency, reliability and tokens

| Measure | Value |
| --- | --- |
| Urgency recall | 0.9833 |
| Urgency precision | 0.8806 |
| Urgency count fn | 1 |
| Urgency count fp | 8 |
| Urgency count tn | 132 |
| Urgency count tp | 59 |
| Reliability error_count | 0 |
| Reliability invalid_output_count | 0 |
| Reliability mean_attempts | 1.0 |
| Tokens mean_input | 0.0 |
| Tokens mean_output | 0.0 |

### Missed Urgent

| Report | Scenario | Text | Urgent probability | Review Triggers |
| --- | --- | --- | --- | --- |
| R-0292 | S-045 | Caller: NV20 TCH inbound Dover with chilled French cheese for Brackenridge Foods is held for a missing export health certificate. Desk: Right, go on. Caller: It | 0.05 |  |

### Latency and cost

| Measure | Value |
| --- | --- |
| Latency max | 1.7525 |
| Latency n | 200 |
| Latency p50 | 1.03 |
| Latency p95 | 1.2985 |
| Cost per_100 | 28.5 |
| Cost total | 57 |
| API USD / 1,000 | 0.0 |

| Cost term | Total | Per 100 |
| --- | --- | --- |
| false_alarm | 0 | 0.0 |
| missed_urgent | 20 | 10.0 |
| review | 16 | 8.0 |
| wrong_category_same_destination | 1 | 0.5 |
| wrong_destination | 20 | 10.0 |

| Bootstrap measure | 95% interval |
| --- | --- |
| auto_routed_error_rate | [0.0105, 0.0585] |
| cost_per_100 | [10.5, 56.5] |
| review_rate | [0.025, 0.155] |
| urgent_recall | [0.9412, 1.0] |

## A / v2

### Category

Macro-F1: 0.9609

| Label | Precision | Recall | F1 |
| --- | --- | --- | --- |
| vehicle_breakdown | 1.0 | 0.9444 | 0.9714 |
| delivery_delay | 0.8378 | 0.9688 | 0.8986 |
| shipment_damage | 1.0 | 0.9375 | 0.9677 |
| missing_shipment | 0.9697 | 1.0 | 0.9846 |
| documentation_issue | 0.9706 | 0.9167 | 0.9429 |
| safety_incident | 1.0 | 1.0 | 1.0 |

Confusion matrix: rows are Labels; columns are Predictions.

| Label / Prediction | vehicle_breakdown | delivery_delay | shipment_damage | missing_shipment | documentation_issue | safety_incident |
| --- | --- | --- | --- | --- | --- | --- |
| vehicle_breakdown | 34 | 2 | 0 | 0 | 0 | 0 |
| delivery_delay | 0 | 31 | 0 | 0 | 1 | 0 |
| shipment_damage | 0 | 1 | 30 | 1 | 0 | 0 |
| missing_shipment | 0 | 0 | 0 | 32 | 0 | 0 |
| documentation_issue | 0 | 3 | 0 | 0 | 33 | 0 |
| safety_incident | 0 | 0 | 0 | 0 | 0 | 32 |

### Destination

Macro-F1: 0.9618

| Label | Precision | Recall | F1 |
| --- | --- | --- | --- |
| fleet_support | 1.0 | 0.9062 | 0.9508 |
| customer_desk | 0.8958 | 0.9773 | 0.9348 |
| claims | 1.0 | 0.9286 | 0.963 |
| security_investigations | 0.9412 | 1.0 | 0.9697 |
| compliance | 0.9677 | 0.9375 | 0.9524 |
| safety_desk | 1.0 | 1.0 | 1.0 |

Confusion matrix: rows are Labels; columns are Predictions.

| Label / Prediction | fleet_support | customer_desk | claims | security_investigations | compliance | safety_desk |
| --- | --- | --- | --- | --- | --- | --- |
| fleet_support | 29 | 2 | 0 | 0 | 1 | 0 |
| customer_desk | 0 | 43 | 0 | 1 | 0 | 0 |
| claims | 0 | 1 | 26 | 1 | 0 | 0 |
| security_investigations | 0 | 0 | 0 | 32 | 0 | 0 |
| compliance | 0 | 2 | 0 | 0 | 30 | 0 |
| safety_desk | 0 | 0 | 0 | 0 | 0 | 32 |

### Urgency, reliability and tokens

| Measure | Value |
| --- | --- |
| Urgency recall | 0.9833 |
| Urgency precision | 0.8806 |
| Urgency count fn | 1 |
| Urgency count fp | 8 |
| Urgency count tn | 132 |
| Urgency count tp | 59 |
| Reliability error_count | 0 |
| Reliability invalid_output_count | 0 |
| Reliability mean_attempts | 1.0 |
| Tokens mean_input | 0.0 |
| Tokens mean_output | 0.0 |

### Missed Urgent

| Report | Scenario | Text | Urgent probability | Review Triggers |
| --- | --- | --- | --- | --- |
| R-0292 | S-045 | Caller: NV20 TCH inbound Dover with chilled French cheese for Brackenridge Foods is held for a missing export health certificate. Desk: Right, go on. Caller: It | 0.05 |  |

### Latency and cost

| Measure | Value |
| --- | --- |
| Latency max | 1.7525 |
| Latency n | 200 |
| Latency p50 | 1.03 |
| Latency p95 | 1.2985 |
| Cost per_100 | 68.5 |
| Cost total | 137 |
| API USD / 1,000 | 0.0 |

| Cost term | Total | Per 100 |
| --- | --- | --- |
| false_alarm | 0 | 0.0 |
| missed_urgent | 100 | 50.0 |
| review | 16 | 8.0 |
| wrong_category_same_destination | 1 | 0.5 |
| wrong_destination | 20 | 10.0 |

| Bootstrap measure | 95% interval |
| --- | --- |
| auto_routed_error_rate | [0.0105, 0.0585] |
| cost_per_100 | [10.5, 177.5] |
| review_rate | [0.025, 0.155] |
| urgent_recall | [0.9412, 1.0] |

## B / v1

### Category

Macro-F1: 0.9008

| Label | Precision | Recall | F1 |
| --- | --- | --- | --- |
| vehicle_breakdown | 0.9655 | 0.7778 | 0.8615 |
| delivery_delay | 0.9118 | 0.9688 | 0.9394 |
| shipment_damage | 0.9615 | 0.7812 | 0.8621 |
| missing_shipment | 0.9412 | 1.0 | 0.9697 |
| documentation_issue | 1.0 | 0.8889 | 0.9412 |
| safety_incident | 0.7111 | 1.0 | 0.8312 |

Confusion matrix: rows are Labels; columns are Predictions.

| Label / Prediction | vehicle_breakdown | delivery_delay | shipment_damage | missing_shipment | documentation_issue | safety_incident |
| --- | --- | --- | --- | --- | --- | --- |
| vehicle_breakdown | 28 | 0 | 0 | 1 | 0 | 7 |
| delivery_delay | 0 | 31 | 1 | 0 | 0 | 0 |
| shipment_damage | 0 | 0 | 25 | 1 | 0 | 6 |
| missing_shipment | 0 | 0 | 0 | 32 | 0 | 0 |
| documentation_issue | 1 | 3 | 0 | 0 | 32 | 0 |
| safety_incident | 0 | 0 | 0 | 0 | 0 | 32 |

### Destination

Macro-F1: 0.8977

| Label | Precision | Recall | F1 |
| --- | --- | --- | --- |
| fleet_support | 0.8125 | 0.8125 | 0.8125 |
| customer_desk | 0.9767 | 0.9545 | 0.9655 |
| claims | 1.0 | 0.6786 | 0.8085 |
| security_investigations | 0.9143 | 1.0 | 0.9552 |
| compliance | 1.0 | 0.9375 | 0.9677 |
| safety_desk | 0.7805 | 1.0 | 0.8767 |

Confusion matrix: rows are Labels; columns are Predictions.

| Label / Prediction | fleet_support | customer_desk | claims | security_investigations | compliance | safety_desk |
| --- | --- | --- | --- | --- | --- | --- |
| fleet_support | 26 | 0 | 0 | 0 | 0 | 6 |
| customer_desk | 1 | 42 | 0 | 1 | 0 | 0 |
| claims | 3 | 1 | 19 | 2 | 0 | 3 |
| security_investigations | 0 | 0 | 0 | 32 | 0 | 0 |
| compliance | 2 | 0 | 0 | 0 | 30 | 0 |
| safety_desk | 0 | 0 | 0 | 0 | 0 | 32 |

### Urgency, reliability and tokens

| Measure | Value |
| --- | --- |
| Urgency recall | 0.9333 |
| Urgency precision | 0.9492 |
| Urgency count fn | 4 |
| Urgency count fp | 3 |
| Urgency count tn | 137 |
| Urgency count tp | 56 |
| Reliability error_count | 0 |
| Reliability invalid_output_count | 0 |
| Reliability mean_attempts | 1.0 |
| Tokens mean_input | 2368.01 |
| Tokens mean_output | 349.5 |

### Missed Urgent

| Report | Scenario | Text | Urgent probability | Review Triggers |
| --- | --- | --- | --- | --- |

### Latency and cost

| Measure | Value |
| --- | --- |
| Latency max | 1457.3707 |
| Latency n | 200 |
| Latency p50 | 229.2962 |
| Latency p95 | 291.1166 |
| Cost per_100 | 56.0 |
| Cost total | 112 |
| API USD / 1,000 | 0.0995 |

| Cost term | Total | Per 100 |
| --- | --- | --- |
| false_alarm | 0 | 0.0 |
| missed_urgent | 0 | 0.0 |
| review | 54 | 27.0 |
| wrong_category_same_destination | 3 | 1.5 |
| wrong_destination | 55 | 27.5 |

| Bootstrap measure | 95% interval |
| --- | --- |
| auto_routed_error_rate | [0.0263, 0.1871] |
| cost_per_100 | [32.0, 87.5] |
| review_rate | [0.17, 0.38] |
| urgent_recall | [0.825, 1.0] |

## B / v2

### Category

Macro-F1: 0.9008

| Label | Precision | Recall | F1 |
| --- | --- | --- | --- |
| vehicle_breakdown | 0.9655 | 0.7778 | 0.8615 |
| delivery_delay | 0.9118 | 0.9688 | 0.9394 |
| shipment_damage | 0.9615 | 0.7812 | 0.8621 |
| missing_shipment | 0.9412 | 1.0 | 0.9697 |
| documentation_issue | 1.0 | 0.8889 | 0.9412 |
| safety_incident | 0.7111 | 1.0 | 0.8312 |

Confusion matrix: rows are Labels; columns are Predictions.

| Label / Prediction | vehicle_breakdown | delivery_delay | shipment_damage | missing_shipment | documentation_issue | safety_incident |
| --- | --- | --- | --- | --- | --- | --- |
| vehicle_breakdown | 28 | 0 | 0 | 1 | 0 | 7 |
| delivery_delay | 0 | 31 | 1 | 0 | 0 | 0 |
| shipment_damage | 0 | 0 | 25 | 1 | 0 | 6 |
| missing_shipment | 0 | 0 | 0 | 32 | 0 | 0 |
| documentation_issue | 1 | 3 | 0 | 0 | 32 | 0 |
| safety_incident | 0 | 0 | 0 | 0 | 0 | 32 |

### Destination

Macro-F1: 0.8977

| Label | Precision | Recall | F1 |
| --- | --- | --- | --- |
| fleet_support | 0.8125 | 0.8125 | 0.8125 |
| customer_desk | 0.9767 | 0.9545 | 0.9655 |
| claims | 1.0 | 0.6786 | 0.8085 |
| security_investigations | 0.9143 | 1.0 | 0.9552 |
| compliance | 1.0 | 0.9375 | 0.9677 |
| safety_desk | 0.7805 | 1.0 | 0.8767 |

Confusion matrix: rows are Labels; columns are Predictions.

| Label / Prediction | fleet_support | customer_desk | claims | security_investigations | compliance | safety_desk |
| --- | --- | --- | --- | --- | --- | --- |
| fleet_support | 26 | 0 | 0 | 0 | 0 | 6 |
| customer_desk | 1 | 42 | 0 | 1 | 0 | 0 |
| claims | 3 | 1 | 19 | 2 | 0 | 3 |
| security_investigations | 0 | 0 | 0 | 32 | 0 | 0 |
| compliance | 2 | 0 | 0 | 0 | 30 | 0 |
| safety_desk | 0 | 0 | 0 | 0 | 0 | 32 |

### Urgency, reliability and tokens

| Measure | Value |
| --- | --- |
| Urgency recall | 0.9333 |
| Urgency precision | 0.9492 |
| Urgency count fn | 4 |
| Urgency count fp | 3 |
| Urgency count tn | 137 |
| Urgency count tp | 56 |
| Reliability error_count | 0 |
| Reliability invalid_output_count | 0 |
| Reliability mean_attempts | 1.0 |
| Tokens mean_input | 2368.01 |
| Tokens mean_output | 349.5 |

### Missed Urgent

| Report | Scenario | Text | Urgent probability | Review Triggers |
| --- | --- | --- | --- | --- |

### Latency and cost

| Measure | Value |
| --- | --- |
| Latency max | 1457.3707 |
| Latency n | 200 |
| Latency p50 | 229.2962 |
| Latency p95 | 291.1166 |
| Cost per_100 | 56.0 |
| Cost total | 112 |
| API USD / 1,000 | 0.0995 |

| Cost term | Total | Per 100 |
| --- | --- | --- |
| false_alarm | 0 | 0.0 |
| missed_urgent | 0 | 0.0 |
| review | 54 | 27.0 |
| wrong_category_same_destination | 3 | 1.5 |
| wrong_destination | 55 | 27.5 |

| Bootstrap measure | 95% interval |
| --- | --- |
| auto_routed_error_rate | [0.0263, 0.1871] |
| cost_per_100 | [32.0, 87.5] |
| review_rate | [0.17, 0.38] |
| urgent_recall | [0.825, 1.0] |

## C / v1

### Category

Macro-F1: 0.9499

| Label | Precision | Recall | F1 |
| --- | --- | --- | --- |
| vehicle_breakdown | 0.9722 | 0.9722 | 0.9722 |
| delivery_delay | 0.8857 | 0.9688 | 0.9254 |
| shipment_damage | 1.0 | 0.9062 | 0.9508 |
| missing_shipment | 0.9412 | 1.0 | 0.9697 |
| documentation_issue | 0.9688 | 0.8611 | 0.9118 |
| safety_incident | 0.9412 | 1.0 | 0.9697 |

Confusion matrix: rows are Labels; columns are Predictions.

| Label / Prediction | vehicle_breakdown | delivery_delay | shipment_damage | missing_shipment | documentation_issue | safety_incident |
| --- | --- | --- | --- | --- | --- | --- |
| vehicle_breakdown | 35 | 0 | 0 | 1 | 0 | 0 |
| delivery_delay | 0 | 31 | 0 | 0 | 1 | 0 |
| shipment_damage | 0 | 0 | 29 | 1 | 0 | 2 |
| missing_shipment | 0 | 0 | 0 | 32 | 0 | 0 |
| documentation_issue | 1 | 4 | 0 | 0 | 31 | 0 |
| safety_incident | 0 | 0 | 0 | 0 | 0 | 32 |

### Destination

Macro-F1: 0.9577

| Label | Precision | Recall | F1 |
| --- | --- | --- | --- |
| fleet_support | 0.9394 | 0.9688 | 0.9538 |
| customer_desk | 0.9773 | 0.9773 | 0.9773 |
| claims | 1.0 | 0.8571 | 0.9231 |
| security_investigations | 0.9412 | 1.0 | 0.9697 |
| compliance | 0.9677 | 0.9375 | 0.9524 |
| safety_desk | 0.9412 | 1.0 | 0.9697 |

Confusion matrix: rows are Labels; columns are Predictions.

| Label / Prediction | fleet_support | customer_desk | claims | security_investigations | compliance | safety_desk |
| --- | --- | --- | --- | --- | --- | --- |
| fleet_support | 31 | 0 | 0 | 0 | 1 | 0 |
| customer_desk | 0 | 43 | 0 | 1 | 0 | 0 |
| claims | 0 | 1 | 24 | 1 | 0 | 2 |
| security_investigations | 0 | 0 | 0 | 32 | 0 | 0 |
| compliance | 2 | 0 | 0 | 0 | 30 | 0 |
| safety_desk | 0 | 0 | 0 | 0 | 0 | 32 |

### Urgency, reliability and tokens

| Measure | Value |
| --- | --- |
| Urgency recall | 0.9833 |
| Urgency precision | 1.0 |
| Urgency count fn | 1 |
| Urgency count fp | 0 |
| Urgency count tn | 140 |
| Urgency count tp | 59 |
| Reliability error_count | 0 |
| Reliability invalid_output_count | 0 |
| Reliability mean_attempts | 1.0 |
| Tokens mean_input | 681.93 |
| Tokens mean_output | 101.03 |

### Missed Urgent

| Report | Scenario | Text | Urgent probability | Review Triggers |
| --- | --- | --- | --- | --- |
| R-0292 | S-045 | Caller: NV20 TCH inbound Dover with chilled French cheese for Brackenridge Foods is held for a missing export health certificate. Desk: Right, go on. Caller: It | 0.05 |  |

### Latency and cost

| Measure | Value |
| --- | --- |
| Latency max | 359.4024 |
| Latency n | 200 |
| Latency p50 | 1.1318 |
| Latency p95 | 253.1374 |
| Cost per_100 | 35.5 |
| Cost total | 71 |
| API USD / 1,000 | 0.0286 |

| Cost term | Total | Per 100 |
| --- | --- | --- |
| false_alarm | 0 | 0.0 |
| missed_urgent | 20 | 10.0 |
| review | 18 | 9.0 |
| wrong_category_same_destination | 3 | 1.5 |
| wrong_destination | 30 | 15.0 |

| Bootstrap measure | 95% interval |
| --- | --- |
| auto_routed_error_rate | [0.0157, 0.1033] |
| cost_per_100 | [12.5, 69.5] |
| review_rate | [0.03, 0.17] |
| urgent_recall | [0.9412, 1.0] |

## C / v2

### Category

Macro-F1: 0.9499

| Label | Precision | Recall | F1 |
| --- | --- | --- | --- |
| vehicle_breakdown | 0.9722 | 0.9722 | 0.9722 |
| delivery_delay | 0.8857 | 0.9688 | 0.9254 |
| shipment_damage | 1.0 | 0.9062 | 0.9508 |
| missing_shipment | 0.9412 | 1.0 | 0.9697 |
| documentation_issue | 0.9688 | 0.8611 | 0.9118 |
| safety_incident | 0.9412 | 1.0 | 0.9697 |

Confusion matrix: rows are Labels; columns are Predictions.

| Label / Prediction | vehicle_breakdown | delivery_delay | shipment_damage | missing_shipment | documentation_issue | safety_incident |
| --- | --- | --- | --- | --- | --- | --- |
| vehicle_breakdown | 35 | 0 | 0 | 1 | 0 | 0 |
| delivery_delay | 0 | 31 | 0 | 0 | 1 | 0 |
| shipment_damage | 0 | 0 | 29 | 1 | 0 | 2 |
| missing_shipment | 0 | 0 | 0 | 32 | 0 | 0 |
| documentation_issue | 1 | 4 | 0 | 0 | 31 | 0 |
| safety_incident | 0 | 0 | 0 | 0 | 0 | 32 |

### Destination

Macro-F1: 0.9577

| Label | Precision | Recall | F1 |
| --- | --- | --- | --- |
| fleet_support | 0.9394 | 0.9688 | 0.9538 |
| customer_desk | 0.9773 | 0.9773 | 0.9773 |
| claims | 1.0 | 0.8571 | 0.9231 |
| security_investigations | 0.9412 | 1.0 | 0.9697 |
| compliance | 0.9677 | 0.9375 | 0.9524 |
| safety_desk | 0.9412 | 1.0 | 0.9697 |

Confusion matrix: rows are Labels; columns are Predictions.

| Label / Prediction | fleet_support | customer_desk | claims | security_investigations | compliance | safety_desk |
| --- | --- | --- | --- | --- | --- | --- |
| fleet_support | 31 | 0 | 0 | 0 | 1 | 0 |
| customer_desk | 0 | 43 | 0 | 1 | 0 | 0 |
| claims | 0 | 1 | 24 | 1 | 0 | 2 |
| security_investigations | 0 | 0 | 0 | 32 | 0 | 0 |
| compliance | 2 | 0 | 0 | 0 | 30 | 0 |
| safety_desk | 0 | 0 | 0 | 0 | 0 | 32 |

### Urgency, reliability and tokens

| Measure | Value |
| --- | --- |
| Urgency recall | 0.9833 |
| Urgency precision | 1.0 |
| Urgency count fn | 1 |
| Urgency count fp | 0 |
| Urgency count tn | 140 |
| Urgency count tp | 59 |
| Reliability error_count | 0 |
| Reliability invalid_output_count | 0 |
| Reliability mean_attempts | 1.0 |
| Tokens mean_input | 681.93 |
| Tokens mean_output | 101.03 |

### Missed Urgent

| Report | Scenario | Text | Urgent probability | Review Triggers |
| --- | --- | --- | --- | --- |
| R-0292 | S-045 | Caller: NV20 TCH inbound Dover with chilled French cheese for Brackenridge Foods is held for a missing export health certificate. Desk: Right, go on. Caller: It | 0.05 |  |

### Latency and cost

| Measure | Value |
| --- | --- |
| Latency max | 359.4024 |
| Latency n | 200 |
| Latency p50 | 1.1318 |
| Latency p95 | 253.1374 |
| Cost per_100 | 75.5 |
| Cost total | 151 |
| API USD / 1,000 | 0.0286 |

| Cost term | Total | Per 100 |
| --- | --- | --- |
| false_alarm | 0 | 0.0 |
| missed_urgent | 100 | 50.0 |
| review | 18 | 9.0 |
| wrong_category_same_destination | 3 | 1.5 |
| wrong_destination | 30 | 15.0 |

| Bootstrap measure | 95% interval |
| --- | --- |
| auto_routed_error_rate | [0.0157, 0.1033] |
| cost_per_100 | [12.5, 190.5] |
| review_rate | [0.03, 0.17] |
| urgent_recall | [0.9412, 1.0] |
