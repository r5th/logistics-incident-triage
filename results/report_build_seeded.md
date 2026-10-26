# Evaluation

## How to read this

Each Incident Report has a Category, Urgency and Destination. A Policy chooses Auto-route or Review. Missed Urgent counts urgent Incident Reports auto-routed as routine. Costs are reviewer-minute equivalents; intervals resample whole Scenarios (1,000 draws, 95%). Urgency recall ignores Routing Mode. Undefined ratios are zero; unavailable percentiles are null. Latency is in milliseconds using nearest-rank percentiles. API cost uses cached input tokens.

| Approach | Policy | Category accuracy | Destination accuracy | Urgent recall | Review rate | Auto-route coverage | Auto-route error rate | Missed Urgent | Cost / 100 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| A | v1 | 0.885 | 0.875 | 0.8167 | 0.13 | 0.87 | 0.1379 | 10 | 146.5 |
| A | v2 | 0.885 | 0.875 | 0.8167 | 0.13 | 0.87 | 0.1379 | 10 | 546.5 |
| B | v1 | 0.9 | 0.905 | 0.9333 | 0.27 | 0.73 | 0.0959 | 0 | 56.0 |
| B | v2 | 0.9 | 0.905 | 0.9333 | 0.27 | 0.73 | 0.0959 | 0 | 56.0 |
| C | v1 | 0.91 | 0.91 | 0.85 | 0.1 | 0.9 | 0.1556 | 9 | 142.0 |
| C | v2 | 0.91 | 0.91 | 0.85 | 0.1 | 0.9 | 0.1556 | 9 | 502.0 |

## A / v1

### Category

Macro-F1: 0.8881

| Label | Precision | Recall | F1 |
| --- | --- | --- | --- |
| vehicle_breakdown | 1.0 | 0.8333 | 0.9091 |
| delivery_delay | 0.8333 | 0.7812 | 0.8065 |
| shipment_damage | 1.0 | 0.9375 | 0.9677 |
| missing_shipment | 0.9655 | 0.875 | 0.918 |
| documentation_issue | 0.9697 | 0.8889 | 0.9275 |
| safety_incident | 0.6667 | 1.0 | 0.8 |

Confusion matrix: rows are Labels; columns are Predictions.

| Label / Prediction | vehicle_breakdown | delivery_delay | shipment_damage | missing_shipment | documentation_issue | safety_incident |
| --- | --- | --- | --- | --- | --- | --- |
| vehicle_breakdown | 30 | 1 | 0 | 0 | 0 | 5 |
| delivery_delay | 0 | 25 | 0 | 0 | 1 | 6 |
| shipment_damage | 0 | 0 | 30 | 1 | 0 | 1 |
| missing_shipment | 0 | 1 | 0 | 28 | 0 | 3 |
| documentation_issue | 0 | 3 | 0 | 0 | 32 | 1 |
| safety_incident | 0 | 0 | 0 | 0 | 0 | 32 |

### Destination

Macro-F1: 0.8815

| Label | Precision | Recall | F1 |
| --- | --- | --- | --- |
| fleet_support | 0.9286 | 0.8125 | 0.8667 |
| customer_desk | 0.9444 | 0.7727 | 0.85 |
| claims | 1.0 | 0.9286 | 0.963 |
| security_investigations | 0.9032 | 0.875 | 0.8889 |
| compliance | 0.9355 | 0.9062 | 0.9206 |
| safety_desk | 0.6667 | 1.0 | 0.8 |

Confusion matrix: rows are Labels; columns are Predictions.

| Label / Prediction | fleet_support | customer_desk | claims | security_investigations | compliance | safety_desk |
| --- | --- | --- | --- | --- | --- | --- |
| fleet_support | 26 | 1 | 0 | 0 | 1 | 4 |
| customer_desk | 0 | 34 | 0 | 2 | 1 | 7 |
| claims | 0 | 0 | 26 | 1 | 0 | 1 |
| security_investigations | 2 | 0 | 0 | 28 | 0 | 2 |
| compliance | 0 | 1 | 0 | 0 | 29 | 2 |
| safety_desk | 0 | 0 | 0 | 0 | 0 | 32 |

### Urgency, reliability and tokens

| Measure | Value |
| --- | --- |
| Urgency recall | 0.8167 |
| Urgency precision | 0.8596 |
| Urgency count fn | 11 |
| Urgency count fp | 8 |
| Urgency count tn | 132 |
| Urgency count tp | 49 |
| Reliability error_count | 0 |
| Reliability invalid_output_count | 0 |
| Reliability mean_attempts | 1.0 |
| Tokens mean_input | 0.0 |
| Tokens mean_output | 0.0 |

### Missed Urgent

| Report | Scenario | Text | Urgent probability | Review Triggers |
| --- | --- | --- | --- | --- |
| R-0010 | S-048 | Caller: At 09:30 during trans-shipping at Northvale Daventry depot, a forklift crushed two Halcyon Medical insulin cartons. Desk: Right, go on. Caller: Two Halc | 0.05 |  |
| R-0100 | S-048 | Hello, passing on the driver's account below.  We can't get replacement insulin to the hospital pharmacy before today's four o'clock window. No one was hurt. Th | 0.05 |  |
| R-0120 | S-015 | Hello, passing on the depot's account below.  NVT 5120, loaded with Sable Electronics laptops, is showing a move away from Northvale Thurrock yard towards the A | 0.05 |  |
| R-0160 | S-048 | Driver's report, as received: The insulin pens inside are broken; nobody hurt. We can't get replacement insulin to the hospital pharmacy before today's four o'c | 0.05 | location_missing |
| R-0168 | S-045 | NV20 TCH inbound Dover with chilled French cheese for Brackenridge Foods is held for a missing export health certificate. Reefer fuel shows about two hours left | 0.05 |  |
| R-0184 | S-045 | Hello, passing on the driver's account below.  The inspection area at Dover won't allow refuelling of chilled trailer NV20 TCH's reefer. Box reading four degree | 0.05 |  |
| R-0188 | S-100 | Driver's report, as received: They're for a hospital laboratory in Carlisle by 18:00. Tacho shows driver has reached nine hours driving and must stop. A timing  | 0.05 |  |
| R-0292 | S-045 | Caller: NV20 TCH inbound Dover with chilled French cheese for Brackenridge Foods is held for a missing export health certificate. Desk: Right, go on. Caller: It | 0.05 |  |
| R-0368 | S-048 | At 09:30 during trans-shipping at Northvale Daventry depot, a forklift crushed two Halcyon Medical insulin cartons. The insulin pens inside are broken; nobody h | 0.05 |  |
| R-0370 | S-100 | Hello, passing on the driver's account below.  A timing update on NV70 HSE, Halcyon Medical reagents for blood testing at a Carlisle hospital lab, due six this  | 0.05 |  |

### Latency and cost

| Measure | Value |
| --- | --- |
| Latency max | 7.1075 |
| Latency n | 200 |
| Latency p50 | 1.2298 |
| Latency p95 | 2.8846 |
| Cost per_100 | 146.5 |
| Cost total | 293 |
| API USD / 1,000 | 0.0 |

| Cost term | Total | Per 100 |
| --- | --- | --- |
| false_alarm | 0 | 0.0 |
| missed_urgent | 200 | 100.0 |
| review | 26 | 13.0 |
| wrong_category_same_destination | 2 | 1.0 |
| wrong_destination | 65 | 32.5 |

| Bootstrap measure | 95% interval |
| --- | --- |
| auto_routed_error_rate | [0.0621, 0.2295] |
| cost_per_100 | [56.5, 273.5] |
| review_rate | [0.065, 0.205] |
| urgent_recall | [0.625, 0.9737] |

## A / v2

### Category

Macro-F1: 0.8881

| Label | Precision | Recall | F1 |
| --- | --- | --- | --- |
| vehicle_breakdown | 1.0 | 0.8333 | 0.9091 |
| delivery_delay | 0.8333 | 0.7812 | 0.8065 |
| shipment_damage | 1.0 | 0.9375 | 0.9677 |
| missing_shipment | 0.9655 | 0.875 | 0.918 |
| documentation_issue | 0.9697 | 0.8889 | 0.9275 |
| safety_incident | 0.6667 | 1.0 | 0.8 |

Confusion matrix: rows are Labels; columns are Predictions.

| Label / Prediction | vehicle_breakdown | delivery_delay | shipment_damage | missing_shipment | documentation_issue | safety_incident |
| --- | --- | --- | --- | --- | --- | --- |
| vehicle_breakdown | 30 | 1 | 0 | 0 | 0 | 5 |
| delivery_delay | 0 | 25 | 0 | 0 | 1 | 6 |
| shipment_damage | 0 | 0 | 30 | 1 | 0 | 1 |
| missing_shipment | 0 | 1 | 0 | 28 | 0 | 3 |
| documentation_issue | 0 | 3 | 0 | 0 | 32 | 1 |
| safety_incident | 0 | 0 | 0 | 0 | 0 | 32 |

### Destination

Macro-F1: 0.8815

| Label | Precision | Recall | F1 |
| --- | --- | --- | --- |
| fleet_support | 0.9286 | 0.8125 | 0.8667 |
| customer_desk | 0.9444 | 0.7727 | 0.85 |
| claims | 1.0 | 0.9286 | 0.963 |
| security_investigations | 0.9032 | 0.875 | 0.8889 |
| compliance | 0.9355 | 0.9062 | 0.9206 |
| safety_desk | 0.6667 | 1.0 | 0.8 |

Confusion matrix: rows are Labels; columns are Predictions.

| Label / Prediction | fleet_support | customer_desk | claims | security_investigations | compliance | safety_desk |
| --- | --- | --- | --- | --- | --- | --- |
| fleet_support | 26 | 1 | 0 | 0 | 1 | 4 |
| customer_desk | 0 | 34 | 0 | 2 | 1 | 7 |
| claims | 0 | 0 | 26 | 1 | 0 | 1 |
| security_investigations | 2 | 0 | 0 | 28 | 0 | 2 |
| compliance | 0 | 1 | 0 | 0 | 29 | 2 |
| safety_desk | 0 | 0 | 0 | 0 | 0 | 32 |

### Urgency, reliability and tokens

| Measure | Value |
| --- | --- |
| Urgency recall | 0.8167 |
| Urgency precision | 0.8596 |
| Urgency count fn | 11 |
| Urgency count fp | 8 |
| Urgency count tn | 132 |
| Urgency count tp | 49 |
| Reliability error_count | 0 |
| Reliability invalid_output_count | 0 |
| Reliability mean_attempts | 1.0 |
| Tokens mean_input | 0.0 |
| Tokens mean_output | 0.0 |

### Missed Urgent

| Report | Scenario | Text | Urgent probability | Review Triggers |
| --- | --- | --- | --- | --- |
| R-0010 | S-048 | Caller: At 09:30 during trans-shipping at Northvale Daventry depot, a forklift crushed two Halcyon Medical insulin cartons. Desk: Right, go on. Caller: Two Halc | 0.05 |  |
| R-0100 | S-048 | Hello, passing on the driver's account below.  We can't get replacement insulin to the hospital pharmacy before today's four o'clock window. No one was hurt. Th | 0.05 |  |
| R-0120 | S-015 | Hello, passing on the depot's account below.  NVT 5120, loaded with Sable Electronics laptops, is showing a move away from Northvale Thurrock yard towards the A | 0.05 |  |
| R-0160 | S-048 | Driver's report, as received: The insulin pens inside are broken; nobody hurt. We can't get replacement insulin to the hospital pharmacy before today's four o'c | 0.05 | location_missing |
| R-0168 | S-045 | NV20 TCH inbound Dover with chilled French cheese for Brackenridge Foods is held for a missing export health certificate. Reefer fuel shows about two hours left | 0.05 |  |
| R-0184 | S-045 | Hello, passing on the driver's account below.  The inspection area at Dover won't allow refuelling of chilled trailer NV20 TCH's reefer. Box reading four degree | 0.05 |  |
| R-0188 | S-100 | Driver's report, as received: They're for a hospital laboratory in Carlisle by 18:00. Tacho shows driver has reached nine hours driving and must stop. A timing  | 0.05 |  |
| R-0292 | S-045 | Caller: NV20 TCH inbound Dover with chilled French cheese for Brackenridge Foods is held for a missing export health certificate. Desk: Right, go on. Caller: It | 0.05 |  |
| R-0368 | S-048 | At 09:30 during trans-shipping at Northvale Daventry depot, a forklift crushed two Halcyon Medical insulin cartons. The insulin pens inside are broken; nobody h | 0.05 |  |
| R-0370 | S-100 | Hello, passing on the driver's account below.  A timing update on NV70 HSE, Halcyon Medical reagents for blood testing at a Carlisle hospital lab, due six this  | 0.05 |  |

### Latency and cost

| Measure | Value |
| --- | --- |
| Latency max | 7.1075 |
| Latency n | 200 |
| Latency p50 | 1.2298 |
| Latency p95 | 2.8846 |
| Cost per_100 | 546.5 |
| Cost total | 1093 |
| API USD / 1,000 | 0.0 |

| Cost term | Total | Per 100 |
| --- | --- | --- |
| false_alarm | 0 | 0.0 |
| missed_urgent | 1000 | 500.0 |
| review | 26 | 13.0 |
| wrong_category_same_destination | 2 | 1.0 |
| wrong_destination | 65 | 32.5 |

| Bootstrap measure | 95% interval |
| --- | --- |
| auto_routed_error_rate | [0.0621, 0.2295] |
| cost_per_100 | [104.0, 1151.0] |
| review_rate | [0.065, 0.205] |
| urgent_recall | [0.625, 0.9737] |

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

Macro-F1: 0.9105

| Label | Precision | Recall | F1 |
| --- | --- | --- | --- |
| vehicle_breakdown | 0.9706 | 0.9167 | 0.9429 |
| delivery_delay | 0.8182 | 0.8438 | 0.8308 |
| shipment_damage | 1.0 | 0.9062 | 0.9508 |
| missing_shipment | 0.9394 | 0.9688 | 0.9538 |
| documentation_issue | 0.9677 | 0.8333 | 0.8955 |
| safety_incident | 0.8 | 1.0 | 0.8889 |

Confusion matrix: rows are Labels; columns are Predictions.

| Label / Prediction | vehicle_breakdown | delivery_delay | shipment_damage | missing_shipment | documentation_issue | safety_incident |
| --- | --- | --- | --- | --- | --- | --- |
| vehicle_breakdown | 33 | 0 | 0 | 1 | 0 | 2 |
| delivery_delay | 0 | 27 | 0 | 0 | 1 | 4 |
| shipment_damage | 0 | 0 | 29 | 1 | 0 | 2 |
| missing_shipment | 0 | 1 | 0 | 31 | 0 | 0 |
| documentation_issue | 1 | 5 | 0 | 0 | 30 | 0 |
| safety_incident | 0 | 0 | 0 | 0 | 0 | 32 |

### Destination

Macro-F1: 0.9112

| Label | Precision | Recall | F1 |
| --- | --- | --- | --- |
| fleet_support | 0.8788 | 0.9062 | 0.8923 |
| customer_desk | 0.9737 | 0.8409 | 0.9024 |
| claims | 1.0 | 0.8571 | 0.9231 |
| security_investigations | 0.9091 | 0.9375 | 0.9231 |
| compliance | 0.9375 | 0.9375 | 0.9375 |
| safety_desk | 0.8 | 1.0 | 0.8889 |

Confusion matrix: rows are Labels; columns are Predictions.

| Label / Prediction | fleet_support | customer_desk | claims | security_investigations | compliance | safety_desk |
| --- | --- | --- | --- | --- | --- | --- |
| fleet_support | 29 | 0 | 0 | 0 | 1 | 2 |
| customer_desk | 0 | 37 | 0 | 2 | 1 | 4 |
| claims | 0 | 1 | 24 | 1 | 0 | 2 |
| security_investigations | 2 | 0 | 0 | 30 | 0 | 0 |
| compliance | 2 | 0 | 0 | 0 | 30 | 0 |
| safety_desk | 0 | 0 | 0 | 0 | 0 | 32 |

### Urgency, reliability and tokens

| Measure | Value |
| --- | --- |
| Urgency recall | 0.85 |
| Urgency precision | 1.0 |
| Urgency count fn | 9 |
| Urgency count fp | 0 |
| Urgency count tn | 140 |
| Urgency count tp | 51 |
| Reliability error_count | 0 |
| Reliability invalid_output_count | 0 |
| Reliability mean_attempts | 1.0 |
| Tokens mean_input | 777.535 |
| Tokens mean_output | 115.205 |

### Missed Urgent

| Report | Scenario | Text | Urgent probability | Review Triggers |
| --- | --- | --- | --- | --- |
| R-0010 | S-048 | Caller: At 09:30 during trans-shipping at Northvale Daventry depot, a forklift crushed two Halcyon Medical insulin cartons. Desk: Right, go on. Caller: Two Halc | 0.05 |  |
| R-0100 | S-048 | Hello, passing on the driver's account below.  We can't get replacement insulin to the hospital pharmacy before today's four o'clock window. No one was hurt. Th | 0.05 |  |
| R-0120 | S-015 | Hello, passing on the depot's account below.  NVT 5120, loaded with Sable Electronics laptops, is showing a move away from Northvale Thurrock yard towards the A | 0.05 |  |
| R-0168 | S-045 | NV20 TCH inbound Dover with chilled French cheese for Brackenridge Foods is held for a missing export health certificate. Reefer fuel shows about two hours left | 0.05 |  |
| R-0184 | S-045 | Hello, passing on the driver's account below.  The inspection area at Dover won't allow refuelling of chilled trailer NV20 TCH's reefer. Box reading four degree | 0.05 |  |
| R-0188 | S-100 | Driver's report, as received: They're for a hospital laboratory in Carlisle by 18:00. Tacho shows driver has reached nine hours driving and must stop. A timing  | 0.05 |  |
| R-0292 | S-045 | Caller: NV20 TCH inbound Dover with chilled French cheese for Brackenridge Foods is held for a missing export health certificate. Desk: Right, go on. Caller: It | 0.05 |  |
| R-0368 | S-048 | At 09:30 during trans-shipping at Northvale Daventry depot, a forklift crushed two Halcyon Medical insulin cartons. The insulin pens inside are broken; nobody h | 0.05 |  |
| R-0370 | S-100 | Hello, passing on the driver's account below.  A timing update on NV70 HSE, Halcyon Medical reagents for blood testing at a Carlisle hospital lab, due six this  | 0.05 |  |

### Latency and cost

| Measure | Value |
| --- | --- |
| Latency max | 359.4547 |
| Latency n | 200 |
| Latency p50 | 1.8086 |
| Latency p95 | 254.4501 |
| Cost per_100 | 142.0 |
| Cost total | 284 |
| API USD / 1,000 | 0.0327 |

| Cost term | Total | Per 100 |
| --- | --- | --- |
| false_alarm | 0 | 0.0 |
| missed_urgent | 180 | 90.0 |
| review | 20 | 10.0 |
| wrong_category_same_destination | 4 | 2.0 |
| wrong_destination | 80 | 40.0 |

| Bootstrap measure | 95% interval |
| --- | --- |
| auto_routed_error_rate | [0.0745, 0.2514] |
| cost_per_100 | [60.5, 256.0] |
| review_rate | [0.04, 0.18] |
| urgent_recall | [0.7, 0.9737] |

## C / v2

### Category

Macro-F1: 0.9105

| Label | Precision | Recall | F1 |
| --- | --- | --- | --- |
| vehicle_breakdown | 0.9706 | 0.9167 | 0.9429 |
| delivery_delay | 0.8182 | 0.8438 | 0.8308 |
| shipment_damage | 1.0 | 0.9062 | 0.9508 |
| missing_shipment | 0.9394 | 0.9688 | 0.9538 |
| documentation_issue | 0.9677 | 0.8333 | 0.8955 |
| safety_incident | 0.8 | 1.0 | 0.8889 |

Confusion matrix: rows are Labels; columns are Predictions.

| Label / Prediction | vehicle_breakdown | delivery_delay | shipment_damage | missing_shipment | documentation_issue | safety_incident |
| --- | --- | --- | --- | --- | --- | --- |
| vehicle_breakdown | 33 | 0 | 0 | 1 | 0 | 2 |
| delivery_delay | 0 | 27 | 0 | 0 | 1 | 4 |
| shipment_damage | 0 | 0 | 29 | 1 | 0 | 2 |
| missing_shipment | 0 | 1 | 0 | 31 | 0 | 0 |
| documentation_issue | 1 | 5 | 0 | 0 | 30 | 0 |
| safety_incident | 0 | 0 | 0 | 0 | 0 | 32 |

### Destination

Macro-F1: 0.9112

| Label | Precision | Recall | F1 |
| --- | --- | --- | --- |
| fleet_support | 0.8788 | 0.9062 | 0.8923 |
| customer_desk | 0.9737 | 0.8409 | 0.9024 |
| claims | 1.0 | 0.8571 | 0.9231 |
| security_investigations | 0.9091 | 0.9375 | 0.9231 |
| compliance | 0.9375 | 0.9375 | 0.9375 |
| safety_desk | 0.8 | 1.0 | 0.8889 |

Confusion matrix: rows are Labels; columns are Predictions.

| Label / Prediction | fleet_support | customer_desk | claims | security_investigations | compliance | safety_desk |
| --- | --- | --- | --- | --- | --- | --- |
| fleet_support | 29 | 0 | 0 | 0 | 1 | 2 |
| customer_desk | 0 | 37 | 0 | 2 | 1 | 4 |
| claims | 0 | 1 | 24 | 1 | 0 | 2 |
| security_investigations | 2 | 0 | 0 | 30 | 0 | 0 |
| compliance | 2 | 0 | 0 | 0 | 30 | 0 |
| safety_desk | 0 | 0 | 0 | 0 | 0 | 32 |

### Urgency, reliability and tokens

| Measure | Value |
| --- | --- |
| Urgency recall | 0.85 |
| Urgency precision | 1.0 |
| Urgency count fn | 9 |
| Urgency count fp | 0 |
| Urgency count tn | 140 |
| Urgency count tp | 51 |
| Reliability error_count | 0 |
| Reliability invalid_output_count | 0 |
| Reliability mean_attempts | 1.0 |
| Tokens mean_input | 777.535 |
| Tokens mean_output | 115.205 |

### Missed Urgent

| Report | Scenario | Text | Urgent probability | Review Triggers |
| --- | --- | --- | --- | --- |
| R-0010 | S-048 | Caller: At 09:30 during trans-shipping at Northvale Daventry depot, a forklift crushed two Halcyon Medical insulin cartons. Desk: Right, go on. Caller: Two Halc | 0.05 |  |
| R-0100 | S-048 | Hello, passing on the driver's account below.  We can't get replacement insulin to the hospital pharmacy before today's four o'clock window. No one was hurt. Th | 0.05 |  |
| R-0120 | S-015 | Hello, passing on the depot's account below.  NVT 5120, loaded with Sable Electronics laptops, is showing a move away from Northvale Thurrock yard towards the A | 0.05 |  |
| R-0168 | S-045 | NV20 TCH inbound Dover with chilled French cheese for Brackenridge Foods is held for a missing export health certificate. Reefer fuel shows about two hours left | 0.05 |  |
| R-0184 | S-045 | Hello, passing on the driver's account below.  The inspection area at Dover won't allow refuelling of chilled trailer NV20 TCH's reefer. Box reading four degree | 0.05 |  |
| R-0188 | S-100 | Driver's report, as received: They're for a hospital laboratory in Carlisle by 18:00. Tacho shows driver has reached nine hours driving and must stop. A timing  | 0.05 |  |
| R-0292 | S-045 | Caller: NV20 TCH inbound Dover with chilled French cheese for Brackenridge Foods is held for a missing export health certificate. Desk: Right, go on. Caller: It | 0.05 |  |
| R-0368 | S-048 | At 09:30 during trans-shipping at Northvale Daventry depot, a forklift crushed two Halcyon Medical insulin cartons. The insulin pens inside are broken; nobody h | 0.05 |  |
| R-0370 | S-100 | Hello, passing on the driver's account below.  A timing update on NV70 HSE, Halcyon Medical reagents for blood testing at a Carlisle hospital lab, due six this  | 0.05 |  |

### Latency and cost

| Measure | Value |
| --- | --- |
| Latency max | 359.4547 |
| Latency n | 200 |
| Latency p50 | 1.8086 |
| Latency p95 | 254.4501 |
| Cost per_100 | 502.0 |
| Cost total | 1004 |
| API USD / 1,000 | 0.0327 |

| Cost term | Total | Per 100 |
| --- | --- | --- |
| false_alarm | 0 | 0.0 |
| missed_urgent | 900 | 450.0 |
| review | 20 | 10.0 |
| wrong_category_same_destination | 4 | 2.0 |
| wrong_destination | 80 | 40.0 |

| Bootstrap measure | 95% interval |
| --- | --- |
| auto_routed_error_rate | [0.0745, 0.2514] |
| cost_per_100 | [109.0, 1035.5] |
| review_rate | [0.04, 0.18] |
| urgent_recall | [0.7, 0.9737] |
