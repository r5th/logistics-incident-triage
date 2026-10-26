# Evaluation

## How to read this

Each Incident Report has a Category, Urgency and Destination. A Policy chooses Auto-route or Review. Missed Urgent counts urgent Incident Reports auto-routed as routine. Costs are reviewer-minute equivalents; intervals resample whole Scenarios (1,000 draws, 95%). Urgency recall and precision ignore Routing Mode. Urgent recall alone can be met by calling everything urgent, so read it with urgent precision. False alarms are routine reports auto-routed as urgent. Undefined ratios are zero; unavailable percentiles are null. Latency is in milliseconds using nearest-rank percentiles. API cost uses cached input tokens.

| Approach | Policy | Category accuracy | Destination accuracy | Urgent recall | Urgent precision | Predicted urgent rate | False alarms | Review rate | Auto-route coverage | Auto-route error rate | Missed Urgent | Cost / 100 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| A | v1 | 0.6875 | 0.7125 | 1.0 | 0.3 | 1.0 | 0 | 1.0 | 0.0 | 0.0 | 0 | 100.0 |
| A | v2 | 0.6875 | 0.7125 | 1.0 | 0.3 | 1.0 | 0 | 1.0 | 0.0 | 0.0 | 0 | 100.0 |
| B | v1 | 0.95 | 0.9375 | 1.0 | 0.3529 | 0.85 | 5 | 0.5375 | 0.4625 | 0.1351 | 0 | 66.25 |
| B | v2 | 0.95 | 0.9375 | 1.0 | 0.3529 | 0.85 | 5 | 0.5375 | 0.4625 | 0.1351 | 0 | 66.25 |
| C | v1 | 0.925 | 0.9125 | 1.0 | 0.3478 | 0.8625 | 0 | 0.8 | 0.2 | 0.0 | 0 | 80.0 |
| C | v2 | 0.925 | 0.9125 | 1.0 | 0.3478 | 0.8625 | 0 | 0.8 | 0.2 | 0.0 | 0 | 80.0 |

## A / v1

### Category

Macro-F1: 0.7003

| Label | Precision | Recall | F1 |
| --- | --- | --- | --- |
| vehicle_breakdown | 1.0 | 0.6667 | 0.8 |
| delivery_delay | 0.4242 | 0.875 | 0.5714 |
| shipment_damage | 0.8571 | 0.75 | 0.8 |
| missing_shipment | 1.0 | 0.75 | 0.8571 |
| documentation_issue | 1.0 | 0.75 | 0.8571 |
| safety_incident | 0.4286 | 0.25 | 0.3158 |

Confusion matrix: rows are Labels; columns are Predictions.

| Label / Prediction | vehicle_breakdown | delivery_delay | shipment_damage | missing_shipment | documentation_issue | safety_incident |
| --- | --- | --- | --- | --- | --- | --- |
| vehicle_breakdown | 8 | 2 | 0 | 0 | 0 | 2 |
| delivery_delay | 0 | 14 | 0 | 0 | 0 | 2 |
| shipment_damage | 0 | 4 | 12 | 0 | 0 | 0 |
| missing_shipment | 0 | 4 | 0 | 12 | 0 | 0 |
| documentation_issue | 0 | 0 | 2 | 0 | 6 | 0 |
| safety_incident | 0 | 9 | 0 | 0 | 0 | 3 |

### Destination

Macro-F1: 0.7091

| Label | Precision | Recall | F1 |
| --- | --- | --- | --- |
| fleet_support | 1.0 | 0.6667 | 0.8 |
| customer_desk | 0.5926 | 0.8 | 0.6809 |
| claims | 0.8571 | 0.75 | 0.8 |
| security_investigations | 0.8 | 1.0 | 0.8889 |
| compliance | 0.7143 | 0.8333 | 0.7692 |
| safety_desk | 0.4286 | 0.25 | 0.3158 |

Confusion matrix: rows are Labels; columns are Predictions.

| Label / Prediction | fleet_support | customer_desk | claims | security_investigations | compliance | safety_desk |
| --- | --- | --- | --- | --- | --- | --- |
| fleet_support | 8 | 2 | 0 | 0 | 0 | 2 |
| customer_desk | 0 | 16 | 0 | 2 | 0 | 2 |
| claims | 0 | 4 | 12 | 0 | 0 | 0 |
| security_investigations | 0 | 0 | 0 | 8 | 0 | 0 |
| compliance | 0 | 0 | 2 | 0 | 10 | 0 |
| safety_desk | 0 | 5 | 0 | 0 | 4 | 3 |

### Urgency, reliability and tokens

| Measure | Value |
| --- | --- |
| Urgency recall | 1.0 |
| Urgency precision | 0.3 |
| Urgency predicted_urgent_rate | 1.0 |
| Urgency false_alarms | 0 |
| Urgency count fn | 0 |
| Urgency count fp | 56 |
| Urgency count tn | 0 |
| Urgency count tp | 24 |
| Reliability error_count | 0 |
| Reliability invalid_output_count | 0 |
| Reliability mean_attempts | 1.0 |
| Tokens mean_input | 0.0 |
| Tokens mean_output | 0.0 |

### Missed Urgent

| Report | Scenario | Text | Urgent probability | Review Triggers |
| --- | --- | --- | --- | --- |

### Latency and cost

| Measure | Value |
| --- | --- |
| Latency max | 1.687 |
| Latency n | 80 |
| Latency p50 | 1.0257 |
| Latency p95 | 1.3168 |
| Cost per_100 | 100.0 |
| Cost total | 80 |
| API USD / 1,000 | 0.0 |

| Cost term | Total | Per 100 |
| --- | --- | --- |
| false_alarm | 0 | 0.0 |
| missed_urgent | 0 | 0.0 |
| review | 80 | 100.0 |
| wrong_category_same_destination | 0 | 0.0 |
| wrong_destination | 0 | 0.0 |

| Bootstrap measure | 95% interval |
| --- | --- |
| auto_routed_error_rate | [0.0, 0.0] |
| cost_per_100 | [100.0, 100.0] |
| predicted_urgent_rate | [1.0, 1.0] |
| review_rate | [1.0, 1.0] |
| urgent_precision | [0.1, 0.5] |
| urgent_recall | [1.0, 1.0] |

## A / v2

### Category

Macro-F1: 0.7003

| Label | Precision | Recall | F1 |
| --- | --- | --- | --- |
| vehicle_breakdown | 1.0 | 0.6667 | 0.8 |
| delivery_delay | 0.4242 | 0.875 | 0.5714 |
| shipment_damage | 0.8571 | 0.75 | 0.8 |
| missing_shipment | 1.0 | 0.75 | 0.8571 |
| documentation_issue | 1.0 | 0.75 | 0.8571 |
| safety_incident | 0.4286 | 0.25 | 0.3158 |

Confusion matrix: rows are Labels; columns are Predictions.

| Label / Prediction | vehicle_breakdown | delivery_delay | shipment_damage | missing_shipment | documentation_issue | safety_incident |
| --- | --- | --- | --- | --- | --- | --- |
| vehicle_breakdown | 8 | 2 | 0 | 0 | 0 | 2 |
| delivery_delay | 0 | 14 | 0 | 0 | 0 | 2 |
| shipment_damage | 0 | 4 | 12 | 0 | 0 | 0 |
| missing_shipment | 0 | 4 | 0 | 12 | 0 | 0 |
| documentation_issue | 0 | 0 | 2 | 0 | 6 | 0 |
| safety_incident | 0 | 9 | 0 | 0 | 0 | 3 |

### Destination

Macro-F1: 0.7091

| Label | Precision | Recall | F1 |
| --- | --- | --- | --- |
| fleet_support | 1.0 | 0.6667 | 0.8 |
| customer_desk | 0.5926 | 0.8 | 0.6809 |
| claims | 0.8571 | 0.75 | 0.8 |
| security_investigations | 0.8 | 1.0 | 0.8889 |
| compliance | 0.7143 | 0.8333 | 0.7692 |
| safety_desk | 0.4286 | 0.25 | 0.3158 |

Confusion matrix: rows are Labels; columns are Predictions.

| Label / Prediction | fleet_support | customer_desk | claims | security_investigations | compliance | safety_desk |
| --- | --- | --- | --- | --- | --- | --- |
| fleet_support | 8 | 2 | 0 | 0 | 0 | 2 |
| customer_desk | 0 | 16 | 0 | 2 | 0 | 2 |
| claims | 0 | 4 | 12 | 0 | 0 | 0 |
| security_investigations | 0 | 0 | 0 | 8 | 0 | 0 |
| compliance | 0 | 0 | 2 | 0 | 10 | 0 |
| safety_desk | 0 | 5 | 0 | 0 | 4 | 3 |

### Urgency, reliability and tokens

| Measure | Value |
| --- | --- |
| Urgency recall | 1.0 |
| Urgency precision | 0.3 |
| Urgency predicted_urgent_rate | 1.0 |
| Urgency false_alarms | 0 |
| Urgency count fn | 0 |
| Urgency count fp | 56 |
| Urgency count tn | 0 |
| Urgency count tp | 24 |
| Reliability error_count | 0 |
| Reliability invalid_output_count | 0 |
| Reliability mean_attempts | 1.0 |
| Tokens mean_input | 0.0 |
| Tokens mean_output | 0.0 |

### Missed Urgent

| Report | Scenario | Text | Urgent probability | Review Triggers |
| --- | --- | --- | --- | --- |

### Latency and cost

| Measure | Value |
| --- | --- |
| Latency max | 1.687 |
| Latency n | 80 |
| Latency p50 | 1.0257 |
| Latency p95 | 1.3168 |
| Cost per_100 | 100.0 |
| Cost total | 80 |
| API USD / 1,000 | 0.0 |

| Cost term | Total | Per 100 |
| --- | --- | --- |
| false_alarm | 0 | 0.0 |
| missed_urgent | 0 | 0.0 |
| review | 80 | 100.0 |
| wrong_category_same_destination | 0 | 0.0 |
| wrong_destination | 0 | 0.0 |

| Bootstrap measure | 95% interval |
| --- | --- |
| auto_routed_error_rate | [0.0, 0.0] |
| cost_per_100 | [100.0, 100.0] |
| predicted_urgent_rate | [1.0, 1.0] |
| review_rate | [1.0, 1.0] |
| urgent_precision | [0.1, 0.5] |
| urgent_recall | [1.0, 1.0] |

## B / v1

### Category

Macro-F1: 0.9429

| Label | Precision | Recall | F1 |
| --- | --- | --- | --- |
| vehicle_breakdown | 1.0 | 0.6667 | 0.8 |
| delivery_delay | 1.0 | 1.0 | 1.0 |
| shipment_damage | 1.0 | 1.0 | 1.0 |
| missing_shipment | 1.0 | 1.0 | 1.0 |
| documentation_issue | 1.0 | 1.0 | 1.0 |
| safety_incident | 0.75 | 1.0 | 0.8571 |

Confusion matrix: rows are Labels; columns are Predictions.

| Label / Prediction | vehicle_breakdown | delivery_delay | shipment_damage | missing_shipment | documentation_issue | safety_incident |
| --- | --- | --- | --- | --- | --- | --- |
| vehicle_breakdown | 8 | 0 | 0 | 0 | 0 | 4 |
| delivery_delay | 0 | 16 | 0 | 0 | 0 | 0 |
| shipment_damage | 0 | 0 | 16 | 0 | 0 | 0 |
| missing_shipment | 0 | 0 | 0 | 16 | 0 | 0 |
| documentation_issue | 0 | 0 | 0 | 0 | 8 | 0 |
| safety_incident | 0 | 0 | 0 | 0 | 0 | 12 |

### Destination

Macro-F1: 0.9346

| Label | Precision | Recall | F1 |
| --- | --- | --- | --- |
| fleet_support | 1.0 | 0.75 | 0.8571 |
| customer_desk | 0.9091 | 1.0 | 0.9524 |
| claims | 1.0 | 1.0 | 1.0 |
| security_investigations | 1.0 | 1.0 | 1.0 |
| compliance | 1.0 | 0.8333 | 0.9091 |
| safety_desk | 0.8 | 1.0 | 0.8889 |

Confusion matrix: rows are Labels; columns are Predictions.

| Label / Prediction | fleet_support | customer_desk | claims | security_investigations | compliance | safety_desk |
| --- | --- | --- | --- | --- | --- | --- |
| fleet_support | 9 | 0 | 0 | 0 | 0 | 3 |
| customer_desk | 0 | 20 | 0 | 0 | 0 | 0 |
| claims | 0 | 0 | 16 | 0 | 0 | 0 |
| security_investigations | 0 | 0 | 0 | 8 | 0 | 0 |
| compliance | 0 | 2 | 0 | 0 | 10 | 0 |
| safety_desk | 0 | 0 | 0 | 0 | 0 | 12 |

### Urgency, reliability and tokens

| Measure | Value |
| --- | --- |
| Urgency recall | 1.0 |
| Urgency precision | 0.3529 |
| Urgency predicted_urgent_rate | 0.85 |
| Urgency false_alarms | 5 |
| Urgency count fn | 0 |
| Urgency count fp | 44 |
| Urgency count tn | 12 |
| Urgency count tp | 24 |
| Reliability error_count | 0 |
| Reliability invalid_output_count | 0 |
| Reliability mean_attempts | 1.0 |
| Tokens mean_input | 2370.4125 |
| Tokens mean_output | 347.5625 |

### Missed Urgent

| Report | Scenario | Text | Urgent probability | Review Triggers |
| --- | --- | --- | --- | --- |

### Latency and cost

| Measure | Value |
| --- | --- |
| Latency max | 355.9587 |
| Latency n | 80 |
| Latency p50 | 222.4682 |
| Latency p95 | 277.0583 |
| Cost per_100 | 66.25 |
| Cost total | 53 |
| API USD / 1,000 | 0.0996 |

| Cost term | Total | Per 100 |
| --- | --- | --- |
| false_alarm | 10 | 12.5 |
| missed_urgent | 0 | 0.0 |
| review | 43 | 53.75 |
| wrong_category_same_destination | 0 | 0.0 |
| wrong_destination | 0 | 0.0 |

| Bootstrap measure | 95% interval |
| --- | --- |
| auto_routed_error_rate | [0.0, 0.3333] |
| cost_per_100 | [45.0, 90.0] |
| predicted_urgent_rate | [0.7, 0.975] |
| review_rate | [0.375, 0.7] |
| urgent_precision | [0.1231, 0.5902] |
| urgent_recall | [1.0, 1.0] |

## B / v2

### Category

Macro-F1: 0.9429

| Label | Precision | Recall | F1 |
| --- | --- | --- | --- |
| vehicle_breakdown | 1.0 | 0.6667 | 0.8 |
| delivery_delay | 1.0 | 1.0 | 1.0 |
| shipment_damage | 1.0 | 1.0 | 1.0 |
| missing_shipment | 1.0 | 1.0 | 1.0 |
| documentation_issue | 1.0 | 1.0 | 1.0 |
| safety_incident | 0.75 | 1.0 | 0.8571 |

Confusion matrix: rows are Labels; columns are Predictions.

| Label / Prediction | vehicle_breakdown | delivery_delay | shipment_damage | missing_shipment | documentation_issue | safety_incident |
| --- | --- | --- | --- | --- | --- | --- |
| vehicle_breakdown | 8 | 0 | 0 | 0 | 0 | 4 |
| delivery_delay | 0 | 16 | 0 | 0 | 0 | 0 |
| shipment_damage | 0 | 0 | 16 | 0 | 0 | 0 |
| missing_shipment | 0 | 0 | 0 | 16 | 0 | 0 |
| documentation_issue | 0 | 0 | 0 | 0 | 8 | 0 |
| safety_incident | 0 | 0 | 0 | 0 | 0 | 12 |

### Destination

Macro-F1: 0.9346

| Label | Precision | Recall | F1 |
| --- | --- | --- | --- |
| fleet_support | 1.0 | 0.75 | 0.8571 |
| customer_desk | 0.9091 | 1.0 | 0.9524 |
| claims | 1.0 | 1.0 | 1.0 |
| security_investigations | 1.0 | 1.0 | 1.0 |
| compliance | 1.0 | 0.8333 | 0.9091 |
| safety_desk | 0.8 | 1.0 | 0.8889 |

Confusion matrix: rows are Labels; columns are Predictions.

| Label / Prediction | fleet_support | customer_desk | claims | security_investigations | compliance | safety_desk |
| --- | --- | --- | --- | --- | --- | --- |
| fleet_support | 9 | 0 | 0 | 0 | 0 | 3 |
| customer_desk | 0 | 20 | 0 | 0 | 0 | 0 |
| claims | 0 | 0 | 16 | 0 | 0 | 0 |
| security_investigations | 0 | 0 | 0 | 8 | 0 | 0 |
| compliance | 0 | 2 | 0 | 0 | 10 | 0 |
| safety_desk | 0 | 0 | 0 | 0 | 0 | 12 |

### Urgency, reliability and tokens

| Measure | Value |
| --- | --- |
| Urgency recall | 1.0 |
| Urgency precision | 0.3529 |
| Urgency predicted_urgent_rate | 0.85 |
| Urgency false_alarms | 5 |
| Urgency count fn | 0 |
| Urgency count fp | 44 |
| Urgency count tn | 12 |
| Urgency count tp | 24 |
| Reliability error_count | 0 |
| Reliability invalid_output_count | 0 |
| Reliability mean_attempts | 1.0 |
| Tokens mean_input | 2370.4125 |
| Tokens mean_output | 347.5625 |

### Missed Urgent

| Report | Scenario | Text | Urgent probability | Review Triggers |
| --- | --- | --- | --- | --- |

### Latency and cost

| Measure | Value |
| --- | --- |
| Latency max | 355.9587 |
| Latency n | 80 |
| Latency p50 | 222.4682 |
| Latency p95 | 277.0583 |
| Cost per_100 | 66.25 |
| Cost total | 53 |
| API USD / 1,000 | 0.0996 |

| Cost term | Total | Per 100 |
| --- | --- | --- |
| false_alarm | 10 | 12.5 |
| missed_urgent | 0 | 0.0 |
| review | 43 | 53.75 |
| wrong_category_same_destination | 0 | 0.0 |
| wrong_destination | 0 | 0.0 |

| Bootstrap measure | 95% interval |
| --- | --- |
| auto_routed_error_rate | [0.0, 0.3333] |
| cost_per_100 | [45.0, 90.0] |
| predicted_urgent_rate | [0.7, 0.975] |
| review_rate | [0.375, 0.7] |
| urgent_precision | [0.1231, 0.5902] |
| urgent_recall | [1.0, 1.0] |

## C / v1

### Category

Macro-F1: 0.9209

| Label | Precision | Recall | F1 |
| --- | --- | --- | --- |
| vehicle_breakdown | 1.0 | 0.8333 | 0.9091 |
| delivery_delay | 0.8 | 1.0 | 0.8889 |
| shipment_damage | 1.0 | 1.0 | 1.0 |
| missing_shipment | 1.0 | 1.0 | 1.0 |
| documentation_issue | 1.0 | 1.0 | 1.0 |
| safety_incident | 0.8 | 0.6667 | 0.7273 |

Confusion matrix: rows are Labels; columns are Predictions.

| Label / Prediction | vehicle_breakdown | delivery_delay | shipment_damage | missing_shipment | documentation_issue | safety_incident |
| --- | --- | --- | --- | --- | --- | --- |
| vehicle_breakdown | 10 | 0 | 0 | 0 | 0 | 2 |
| delivery_delay | 0 | 16 | 0 | 0 | 0 | 0 |
| shipment_damage | 0 | 0 | 16 | 0 | 0 | 0 |
| missing_shipment | 0 | 0 | 0 | 16 | 0 | 0 |
| documentation_issue | 0 | 0 | 0 | 0 | 8 | 0 |
| safety_incident | 0 | 4 | 0 | 0 | 0 | 8 |

### Destination

Macro-F1: 0.9067

| Label | Precision | Recall | F1 |
| --- | --- | --- | --- |
| fleet_support | 1.0 | 0.9167 | 0.9565 |
| customer_desk | 0.9091 | 1.0 | 0.9524 |
| claims | 1.0 | 1.0 | 1.0 |
| security_investigations | 1.0 | 1.0 | 1.0 |
| compliance | 0.7143 | 0.8333 | 0.7692 |
| safety_desk | 0.8889 | 0.6667 | 0.7619 |

Confusion matrix: rows are Labels; columns are Predictions.

| Label / Prediction | fleet_support | customer_desk | claims | security_investigations | compliance | safety_desk |
| --- | --- | --- | --- | --- | --- | --- |
| fleet_support | 11 | 0 | 0 | 0 | 0 | 1 |
| customer_desk | 0 | 20 | 0 | 0 | 0 | 0 |
| claims | 0 | 0 | 16 | 0 | 0 | 0 |
| security_investigations | 0 | 0 | 0 | 8 | 0 | 0 |
| compliance | 0 | 2 | 0 | 0 | 10 | 0 |
| safety_desk | 0 | 0 | 0 | 0 | 4 | 8 |

### Urgency, reliability and tokens

| Measure | Value |
| --- | --- |
| Urgency recall | 1.0 |
| Urgency precision | 0.3478 |
| Urgency predicted_urgent_rate | 0.8625 |
| Urgency false_alarms | 0 |
| Urgency count fn | 0 |
| Urgency count fp | 45 |
| Urgency count tn | 11 |
| Urgency count tp | 24 |
| Reliability error_count | 0 |
| Reliability invalid_output_count | 0 |
| Reliability mean_attempts | 1.0 |
| Tokens mean_input | 1327.6 |
| Tokens mean_output | 192.6875 |

### Missed Urgent

| Report | Scenario | Text | Urgent probability | Review Triggers |
| --- | --- | --- | --- | --- |

### Latency and cost

| Measure | Value |
| --- | --- |
| Latency max | 296.2984 |
| Latency n | 80 |
| Latency p50 | 214.7498 |
| Latency p95 | 248.5584 |
| Cost per_100 | 80.0 |
| Cost total | 64 |
| API USD / 1,000 | 0.0558 |

| Cost term | Total | Per 100 |
| --- | --- | --- |
| false_alarm | 0 | 0.0 |
| missed_urgent | 0 | 0.0 |
| review | 64 | 80.0 |
| wrong_category_same_destination | 0 | 0.0 |
| wrong_destination | 0 | 0.0 |

| Bootstrap measure | 95% interval |
| --- | --- |
| auto_routed_error_rate | [0.0, 0.0] |
| cost_per_100 | [63.75, 93.75] |
| predicted_urgent_rate | [0.7125, 0.9875] |
| review_rate | [0.6375, 0.9375] |
| urgent_precision | [0.1194, 0.5806] |
| urgent_recall | [1.0, 1.0] |

## C / v2

### Category

Macro-F1: 0.9209

| Label | Precision | Recall | F1 |
| --- | --- | --- | --- |
| vehicle_breakdown | 1.0 | 0.8333 | 0.9091 |
| delivery_delay | 0.8 | 1.0 | 0.8889 |
| shipment_damage | 1.0 | 1.0 | 1.0 |
| missing_shipment | 1.0 | 1.0 | 1.0 |
| documentation_issue | 1.0 | 1.0 | 1.0 |
| safety_incident | 0.8 | 0.6667 | 0.7273 |

Confusion matrix: rows are Labels; columns are Predictions.

| Label / Prediction | vehicle_breakdown | delivery_delay | shipment_damage | missing_shipment | documentation_issue | safety_incident |
| --- | --- | --- | --- | --- | --- | --- |
| vehicle_breakdown | 10 | 0 | 0 | 0 | 0 | 2 |
| delivery_delay | 0 | 16 | 0 | 0 | 0 | 0 |
| shipment_damage | 0 | 0 | 16 | 0 | 0 | 0 |
| missing_shipment | 0 | 0 | 0 | 16 | 0 | 0 |
| documentation_issue | 0 | 0 | 0 | 0 | 8 | 0 |
| safety_incident | 0 | 4 | 0 | 0 | 0 | 8 |

### Destination

Macro-F1: 0.9067

| Label | Precision | Recall | F1 |
| --- | --- | --- | --- |
| fleet_support | 1.0 | 0.9167 | 0.9565 |
| customer_desk | 0.9091 | 1.0 | 0.9524 |
| claims | 1.0 | 1.0 | 1.0 |
| security_investigations | 1.0 | 1.0 | 1.0 |
| compliance | 0.7143 | 0.8333 | 0.7692 |
| safety_desk | 0.8889 | 0.6667 | 0.7619 |

Confusion matrix: rows are Labels; columns are Predictions.

| Label / Prediction | fleet_support | customer_desk | claims | security_investigations | compliance | safety_desk |
| --- | --- | --- | --- | --- | --- | --- |
| fleet_support | 11 | 0 | 0 | 0 | 0 | 1 |
| customer_desk | 0 | 20 | 0 | 0 | 0 | 0 |
| claims | 0 | 0 | 16 | 0 | 0 | 0 |
| security_investigations | 0 | 0 | 0 | 8 | 0 | 0 |
| compliance | 0 | 2 | 0 | 0 | 10 | 0 |
| safety_desk | 0 | 0 | 0 | 0 | 4 | 8 |

### Urgency, reliability and tokens

| Measure | Value |
| --- | --- |
| Urgency recall | 1.0 |
| Urgency precision | 0.3478 |
| Urgency predicted_urgent_rate | 0.8625 |
| Urgency false_alarms | 0 |
| Urgency count fn | 0 |
| Urgency count fp | 45 |
| Urgency count tn | 11 |
| Urgency count tp | 24 |
| Reliability error_count | 0 |
| Reliability invalid_output_count | 0 |
| Reliability mean_attempts | 1.0 |
| Tokens mean_input | 1327.6 |
| Tokens mean_output | 192.6875 |

### Missed Urgent

| Report | Scenario | Text | Urgent probability | Review Triggers |
| --- | --- | --- | --- | --- |

### Latency and cost

| Measure | Value |
| --- | --- |
| Latency max | 296.2984 |
| Latency n | 80 |
| Latency p50 | 214.7498 |
| Latency p95 | 248.5584 |
| Cost per_100 | 80.0 |
| Cost total | 64 |
| API USD / 1,000 | 0.0558 |

| Cost term | Total | Per 100 |
| --- | --- | --- |
| false_alarm | 0 | 0.0 |
| missed_urgent | 0 | 0.0 |
| review | 64 | 80.0 |
| wrong_category_same_destination | 0 | 0.0 |
| wrong_destination | 0 | 0.0 |

| Bootstrap measure | 95% interval |
| --- | --- |
| auto_routed_error_rate | [0.0, 0.0] |
| cost_per_100 | [63.75, 93.75] |
| predicted_urgent_rate | [0.7125, 0.9875] |
| review_rate | [0.6375, 0.9375] |
| urgent_precision | [0.1194, 0.5806] |
| urgent_recall | [1.0, 1.0] |
