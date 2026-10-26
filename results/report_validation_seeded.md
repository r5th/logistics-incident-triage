# Evaluation

## How to read this

Each Incident Report has a Category, Urgency and Destination. A Policy chooses Auto-route or Review. Missed Urgent counts urgent Incident Reports auto-routed as routine. Costs are reviewer-minute equivalents; intervals resample whole Scenarios (1,000 draws, 95%). Urgency recall ignores Routing Mode. Undefined ratios are zero; unavailable percentiles are null. Latency is in milliseconds using nearest-rank percentiles. API cost uses cached input tokens.

| Approach | Policy | Category accuracy | Destination accuracy | Urgent recall | Review rate | Auto-route coverage | Auto-route error rate | Missed Urgent | Cost / 100 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| A | v1 | 0.7 | 0.675 | 0.6667 | 0.3125 | 0.6875 | 0.2909 | 7 | 268.75 |
| A | v2 | 0.7 | 0.675 | 0.6667 | 0.3125 | 0.6875 | 0.2909 | 7 | 968.75 |
| B | v1 | 0.95 | 0.9375 | 0.75 | 0.275 | 0.725 | 0.1724 | 2 | 115.0 |
| B | v2 | 0.95 | 0.9375 | 0.75 | 0.275 | 0.725 | 0.1724 | 2 | 315.0 |
| C | v1 | 0.925 | 0.9 | 0.625 | 0.1625 | 0.8375 | 0.209 | 7 | 241.25 |
| C | v2 | 0.925 | 0.9 | 0.625 | 0.1625 | 0.8375 | 0.209 | 7 | 941.25 |

## A / v1

### Category

Macro-F1: 0.7337

| Label | Precision | Recall | F1 |
| --- | --- | --- | --- |
| vehicle_breakdown | 1.0 | 0.6667 | 0.8 |
| delivery_delay | 0.7143 | 0.625 | 0.6667 |
| shipment_damage | 0.8571 | 0.75 | 0.8 |
| missing_shipment | 1.0 | 0.75 | 0.8571 |
| documentation_issue | 1.0 | 0.75 | 0.8571 |
| safety_incident | 0.3077 | 0.6667 | 0.4211 |

Confusion matrix: rows are Labels; columns are Predictions.

| Label / Prediction | vehicle_breakdown | delivery_delay | shipment_damage | missing_shipment | documentation_issue | safety_incident |
| --- | --- | --- | --- | --- | --- | --- |
| vehicle_breakdown | 8 | 0 | 0 | 0 | 0 | 4 |
| delivery_delay | 0 | 10 | 0 | 0 | 0 | 6 |
| shipment_damage | 0 | 0 | 12 | 0 | 0 | 4 |
| missing_shipment | 0 | 0 | 0 | 12 | 0 | 4 |
| documentation_issue | 0 | 0 | 2 | 0 | 6 | 0 |
| safety_incident | 0 | 4 | 0 | 0 | 0 | 8 |

### Destination

Macro-F1: 0.7084

| Label | Precision | Recall | F1 |
| --- | --- | --- | --- |
| fleet_support | 1.0 | 0.6667 | 0.8 |
| customer_desk | 1.0 | 0.4 | 0.5714 |
| claims | 0.8571 | 0.75 | 0.8 |
| security_investigations | 0.8 | 1.0 | 0.8889 |
| compliance | 0.7143 | 0.8333 | 0.7692 |
| safety_desk | 0.3077 | 0.6667 | 0.4211 |

Confusion matrix: rows are Labels; columns are Predictions.

| Label / Prediction | fleet_support | customer_desk | claims | security_investigations | compliance | safety_desk |
| --- | --- | --- | --- | --- | --- | --- |
| fleet_support | 8 | 0 | 0 | 0 | 0 | 4 |
| customer_desk | 0 | 8 | 0 | 2 | 0 | 10 |
| claims | 0 | 0 | 12 | 0 | 0 | 4 |
| security_investigations | 0 | 0 | 0 | 8 | 0 | 0 |
| compliance | 0 | 0 | 2 | 0 | 10 | 0 |
| safety_desk | 0 | 0 | 0 | 0 | 4 | 8 |

### Urgency, reliability and tokens

| Measure | Value |
| --- | --- |
| Urgency recall | 0.6667 |
| Urgency precision | 1.0 |
| Urgency count fn | 8 |
| Urgency count fp | 0 |
| Urgency count tn | 56 |
| Urgency count tp | 16 |
| Reliability error_count | 0 |
| Reliability invalid_output_count | 0 |
| Reliability mean_attempts | 1.0 |
| Tokens mean_input | 0.0 |
| Tokens mean_output | 0.0 |

### Missed Urgent

| Report | Scenario | Text | Urgent probability | Review Triggers |
| --- | --- | --- | --- | --- |
| R-0019 | S-061 | Driver's report, as received: It's UN1263 paint, class 3 flammable, in 25-litre steel drums. They're upright, no leak seen and no smell. Customer in Bradford ha | 0.05 |  |
| R-0099 | S-061 | Hello, passing on the driver's account below.  Customer in Bradford has refused damaged Pennine Paints drums: three dented, with a lid cracked on one. All uprig | 0.05 |  |
| R-0204 | S-061 | At the Pennine Paints customer in Bradford, opening the trailer revealed three dented drums and one cracked lid. It's UN1263 paint, class 3 flammable, in 25-lit | 0.05 |  |
| R-0234 | S-001 | NV22 HPL has tipped at Brackenridge RDC Doncaster, three pallets short. Driver says the seal was intact when he opened the artic. Goods-in say the number on the | 0.05 |  |
| R-0286 | S-001 | Driver's report, as received: Driver says the seal was intact when he opened the artic. Goods-in say the number on the doors doesn't match the manifest. Three p | 0.05 |  |
| R-0297 | S-052 | Caller: NV20 RXC has rear-ended a car in slow traffic on the A34 near Oxford. Desk: Right, go on. Caller: The car driver says their neck hurts. Police are comin | 0.05 |  |
| R-0315 | S-061 | Caller: At the Pennine Paints customer in Bradford, opening the trailer revealed three dented drums and one cracked lid. Desk: Right, go on. Caller: The 25-litr | 0.05 |  |

### Latency and cost

| Measure | Value |
| --- | --- |
| Latency max | 1.5871 |
| Latency n | 80 |
| Latency p50 | 1.0019 |
| Latency p95 | 1.2848 |
| Cost per_100 | 268.75 |
| Cost total | 215 |
| API USD / 1,000 | 0.0 |

| Cost term | Total | Per 100 |
| --- | --- | --- |
| false_alarm | 0 | 0.0 |
| missed_urgent | 140 | 175.0 |
| review | 25 | 31.25 |
| wrong_category_same_destination | 0 | 0.0 |
| wrong_destination | 50 | 62.5 |

| Bootstrap measure | 95% interval |
| --- | --- |
| auto_routed_error_rate | [0.1026, 0.5] |
| cost_per_100 | [81.25, 515.0] |
| review_rate | [0.125, 0.5] |
| urgent_recall | [0.35, 0.9167] |

## A / v2

### Category

Macro-F1: 0.7337

| Label | Precision | Recall | F1 |
| --- | --- | --- | --- |
| vehicle_breakdown | 1.0 | 0.6667 | 0.8 |
| delivery_delay | 0.7143 | 0.625 | 0.6667 |
| shipment_damage | 0.8571 | 0.75 | 0.8 |
| missing_shipment | 1.0 | 0.75 | 0.8571 |
| documentation_issue | 1.0 | 0.75 | 0.8571 |
| safety_incident | 0.3077 | 0.6667 | 0.4211 |

Confusion matrix: rows are Labels; columns are Predictions.

| Label / Prediction | vehicle_breakdown | delivery_delay | shipment_damage | missing_shipment | documentation_issue | safety_incident |
| --- | --- | --- | --- | --- | --- | --- |
| vehicle_breakdown | 8 | 0 | 0 | 0 | 0 | 4 |
| delivery_delay | 0 | 10 | 0 | 0 | 0 | 6 |
| shipment_damage | 0 | 0 | 12 | 0 | 0 | 4 |
| missing_shipment | 0 | 0 | 0 | 12 | 0 | 4 |
| documentation_issue | 0 | 0 | 2 | 0 | 6 | 0 |
| safety_incident | 0 | 4 | 0 | 0 | 0 | 8 |

### Destination

Macro-F1: 0.7084

| Label | Precision | Recall | F1 |
| --- | --- | --- | --- |
| fleet_support | 1.0 | 0.6667 | 0.8 |
| customer_desk | 1.0 | 0.4 | 0.5714 |
| claims | 0.8571 | 0.75 | 0.8 |
| security_investigations | 0.8 | 1.0 | 0.8889 |
| compliance | 0.7143 | 0.8333 | 0.7692 |
| safety_desk | 0.3077 | 0.6667 | 0.4211 |

Confusion matrix: rows are Labels; columns are Predictions.

| Label / Prediction | fleet_support | customer_desk | claims | security_investigations | compliance | safety_desk |
| --- | --- | --- | --- | --- | --- | --- |
| fleet_support | 8 | 0 | 0 | 0 | 0 | 4 |
| customer_desk | 0 | 8 | 0 | 2 | 0 | 10 |
| claims | 0 | 0 | 12 | 0 | 0 | 4 |
| security_investigations | 0 | 0 | 0 | 8 | 0 | 0 |
| compliance | 0 | 0 | 2 | 0 | 10 | 0 |
| safety_desk | 0 | 0 | 0 | 0 | 4 | 8 |

### Urgency, reliability and tokens

| Measure | Value |
| --- | --- |
| Urgency recall | 0.6667 |
| Urgency precision | 1.0 |
| Urgency count fn | 8 |
| Urgency count fp | 0 |
| Urgency count tn | 56 |
| Urgency count tp | 16 |
| Reliability error_count | 0 |
| Reliability invalid_output_count | 0 |
| Reliability mean_attempts | 1.0 |
| Tokens mean_input | 0.0 |
| Tokens mean_output | 0.0 |

### Missed Urgent

| Report | Scenario | Text | Urgent probability | Review Triggers |
| --- | --- | --- | --- | --- |
| R-0019 | S-061 | Driver's report, as received: It's UN1263 paint, class 3 flammable, in 25-litre steel drums. They're upright, no leak seen and no smell. Customer in Bradford ha | 0.05 |  |
| R-0099 | S-061 | Hello, passing on the driver's account below.  Customer in Bradford has refused damaged Pennine Paints drums: three dented, with a lid cracked on one. All uprig | 0.05 |  |
| R-0204 | S-061 | At the Pennine Paints customer in Bradford, opening the trailer revealed three dented drums and one cracked lid. It's UN1263 paint, class 3 flammable, in 25-lit | 0.05 |  |
| R-0234 | S-001 | NV22 HPL has tipped at Brackenridge RDC Doncaster, three pallets short. Driver says the seal was intact when he opened the artic. Goods-in say the number on the | 0.05 |  |
| R-0286 | S-001 | Driver's report, as received: Driver says the seal was intact when he opened the artic. Goods-in say the number on the doors doesn't match the manifest. Three p | 0.05 |  |
| R-0297 | S-052 | Caller: NV20 RXC has rear-ended a car in slow traffic on the A34 near Oxford. Desk: Right, go on. Caller: The car driver says their neck hurts. Police are comin | 0.05 |  |
| R-0315 | S-061 | Caller: At the Pennine Paints customer in Bradford, opening the trailer revealed three dented drums and one cracked lid. Desk: Right, go on. Caller: The 25-litr | 0.05 |  |

### Latency and cost

| Measure | Value |
| --- | --- |
| Latency max | 1.5871 |
| Latency n | 80 |
| Latency p50 | 1.0019 |
| Latency p95 | 1.2848 |
| Cost per_100 | 968.75 |
| Cost total | 775 |
| API USD / 1,000 | 0.0 |

| Cost term | Total | Per 100 |
| --- | --- | --- |
| false_alarm | 0 | 0.0 |
| missed_urgent | 700 | 875.0 |
| review | 25 | 31.25 |
| wrong_category_same_destination | 0 | 0.0 |
| wrong_destination | 50 | 62.5 |

| Bootstrap measure | 95% interval |
| --- | --- |
| auto_routed_error_rate | [0.1026, 0.5] |
| cost_per_100 | [83.75, 2200.0] |
| review_rate | [0.125, 0.5] |
| urgent_recall | [0.35, 0.9167] |

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
| Urgency recall | 0.75 |
| Urgency precision | 0.8571 |
| Urgency count fn | 6 |
| Urgency count fp | 3 |
| Urgency count tn | 53 |
| Urgency count tp | 18 |
| Reliability error_count | 0 |
| Reliability invalid_output_count | 0 |
| Reliability mean_attempts | 1.0 |
| Tokens mean_input | 2370.4125 |
| Tokens mean_output | 347.5625 |

### Missed Urgent

| Report | Scenario | Text | Urgent probability | Review Triggers |
| --- | --- | --- | --- | --- |
| R-0234 | S-001 | NV22 HPL has tipped at Brackenridge RDC Doncaster, three pallets short. Driver says the seal was intact when he opened the artic. Goods-in say the number on the | 0.1 | cargo_missing, multiple_issues |
| R-0286 | S-001 | Driver's report, as received: Driver says the seal was intact when he opened the artic. Goods-in say the number on the doors doesn't match the manifest. Three p | 0.08 | cargo_missing, multiple_issues |

### Latency and cost

| Measure | Value |
| --- | --- |
| Latency max | 355.9587 |
| Latency n | 80 |
| Latency p50 | 222.4682 |
| Latency p95 | 277.0583 |
| Cost per_100 | 115.0 |
| Cost total | 92 |
| API USD / 1,000 | 0.0996 |

| Cost term | Total | Per 100 |
| --- | --- | --- |
| false_alarm | 4 | 5.0 |
| missed_urgent | 40 | 50.0 |
| review | 22 | 27.5 |
| wrong_category_same_destination | 1 | 1.25 |
| wrong_destination | 25 | 31.25 |

| Bootstrap measure | 95% interval |
| --- | --- |
| auto_routed_error_rate | [0.0357, 0.3333] |
| cost_per_100 | [40.0, 225.0] |
| review_rate | [0.1125, 0.4625] |
| urgent_recall | [0.5, 1.0] |

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
| Urgency recall | 0.75 |
| Urgency precision | 0.8571 |
| Urgency count fn | 6 |
| Urgency count fp | 3 |
| Urgency count tn | 53 |
| Urgency count tp | 18 |
| Reliability error_count | 0 |
| Reliability invalid_output_count | 0 |
| Reliability mean_attempts | 1.0 |
| Tokens mean_input | 2370.4125 |
| Tokens mean_output | 347.5625 |

### Missed Urgent

| Report | Scenario | Text | Urgent probability | Review Triggers |
| --- | --- | --- | --- | --- |
| R-0234 | S-001 | NV22 HPL has tipped at Brackenridge RDC Doncaster, three pallets short. Driver says the seal was intact when he opened the artic. Goods-in say the number on the | 0.1 | cargo_missing, multiple_issues |
| R-0286 | S-001 | Driver's report, as received: Driver says the seal was intact when he opened the artic. Goods-in say the number on the doors doesn't match the manifest. Three p | 0.08 | cargo_missing, multiple_issues |

### Latency and cost

| Measure | Value |
| --- | --- |
| Latency max | 355.9587 |
| Latency n | 80 |
| Latency p50 | 222.4682 |
| Latency p95 | 277.0583 |
| Cost per_100 | 315.0 |
| Cost total | 252 |
| API USD / 1,000 | 0.0996 |

| Cost term | Total | Per 100 |
| --- | --- | --- |
| false_alarm | 4 | 5.0 |
| missed_urgent | 200 | 250.0 |
| review | 22 | 27.5 |
| wrong_category_same_destination | 1 | 1.25 |
| wrong_destination | 25 | 31.25 |

| Bootstrap measure | 95% interval |
| --- | --- |
| auto_routed_error_rate | [0.0357, 0.3333] |
| cost_per_100 | [40.0, 826.25] |
| review_rate | [0.1125, 0.4625] |
| urgent_recall | [0.5, 1.0] |

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

Macro-F1: 0.893

| Label | Precision | Recall | F1 |
| --- | --- | --- | --- |
| fleet_support | 1.0 | 0.8333 | 0.9091 |
| customer_desk | 0.9091 | 1.0 | 0.9524 |
| claims | 1.0 | 1.0 | 1.0 |
| security_investigations | 1.0 | 1.0 | 1.0 |
| compliance | 0.7143 | 0.8333 | 0.7692 |
| safety_desk | 0.8 | 0.6667 | 0.7273 |

Confusion matrix: rows are Labels; columns are Predictions.

| Label / Prediction | fleet_support | customer_desk | claims | security_investigations | compliance | safety_desk |
| --- | --- | --- | --- | --- | --- | --- |
| fleet_support | 10 | 0 | 0 | 0 | 0 | 2 |
| customer_desk | 0 | 20 | 0 | 0 | 0 | 0 |
| claims | 0 | 0 | 16 | 0 | 0 | 0 |
| security_investigations | 0 | 0 | 0 | 8 | 0 | 0 |
| compliance | 0 | 2 | 0 | 0 | 10 | 0 |
| safety_desk | 0 | 0 | 0 | 0 | 4 | 8 |

### Urgency, reliability and tokens

| Measure | Value |
| --- | --- |
| Urgency recall | 0.625 |
| Urgency precision | 1.0 |
| Urgency count fn | 9 |
| Urgency count fp | 0 |
| Urgency count tn | 56 |
| Urgency count tp | 15 |
| Reliability error_count | 0 |
| Reliability invalid_output_count | 0 |
| Reliability mean_attempts | 1.0 |
| Tokens mean_input | 1298.1875 |
| Tokens mean_output | 188.425 |

### Missed Urgent

| Report | Scenario | Text | Urgent probability | Review Triggers |
| --- | --- | --- | --- | --- |
| R-0019 | S-061 | Driver's report, as received: It's UN1263 paint, class 3 flammable, in 25-litre steel drums. They're upright, no leak seen and no smell. Customer in Bradford ha | 0.05 |  |
| R-0099 | S-061 | Hello, passing on the driver's account below.  Customer in Bradford has refused damaged Pennine Paints drums: three dented, with a lid cracked on one. All uprig | 0.05 |  |
| R-0204 | S-061 | At the Pennine Paints customer in Bradford, opening the trailer revealed three dented drums and one cracked lid. It's UN1263 paint, class 3 flammable, in 25-lit | 0.05 |  |
| R-0234 | S-001 | NV22 HPL has tipped at Brackenridge RDC Doncaster, three pallets short. Driver says the seal was intact when he opened the artic. Goods-in say the number on the | 0.05 |  |
| R-0286 | S-001 | Driver's report, as received: Driver says the seal was intact when he opened the artic. Goods-in say the number on the doors doesn't match the manifest. Three p | 0.05 |  |
| R-0297 | S-052 | Caller: NV20 RXC has rear-ended a car in slow traffic on the A34 near Oxford. Desk: Right, go on. Caller: The car driver says their neck hurts. Police are comin | 0.05 |  |
| R-0315 | S-061 | Caller: At the Pennine Paints customer in Bradford, opening the trailer revealed three dented drums and one cracked lid. Desk: Right, go on. Caller: The 25-litr | 0.05 |  |

### Latency and cost

| Measure | Value |
| --- | --- |
| Latency max | 296.22 |
| Latency n | 80 |
| Latency p50 | 214.7112 |
| Latency p95 | 248.5422 |
| Cost per_100 | 241.25 |
| Cost total | 193 |
| API USD / 1,000 | 0.0545 |

| Cost term | Total | Per 100 |
| --- | --- | --- |
| false_alarm | 0 | 0.0 |
| missed_urgent | 140 | 175.0 |
| review | 13 | 16.25 |
| wrong_category_same_destination | 0 | 0.0 |
| wrong_destination | 40 | 50.0 |

| Bootstrap measure | 95% interval |
| --- | --- |
| auto_routed_error_rate | [0.0571, 0.4] |
| cost_per_100 | [51.25, 500.0] |
| review_rate | [0.0375, 0.325] |
| urgent_recall | [0.3125, 0.9167] |

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

Macro-F1: 0.893

| Label | Precision | Recall | F1 |
| --- | --- | --- | --- |
| fleet_support | 1.0 | 0.8333 | 0.9091 |
| customer_desk | 0.9091 | 1.0 | 0.9524 |
| claims | 1.0 | 1.0 | 1.0 |
| security_investigations | 1.0 | 1.0 | 1.0 |
| compliance | 0.7143 | 0.8333 | 0.7692 |
| safety_desk | 0.8 | 0.6667 | 0.7273 |

Confusion matrix: rows are Labels; columns are Predictions.

| Label / Prediction | fleet_support | customer_desk | claims | security_investigations | compliance | safety_desk |
| --- | --- | --- | --- | --- | --- | --- |
| fleet_support | 10 | 0 | 0 | 0 | 0 | 2 |
| customer_desk | 0 | 20 | 0 | 0 | 0 | 0 |
| claims | 0 | 0 | 16 | 0 | 0 | 0 |
| security_investigations | 0 | 0 | 0 | 8 | 0 | 0 |
| compliance | 0 | 2 | 0 | 0 | 10 | 0 |
| safety_desk | 0 | 0 | 0 | 0 | 4 | 8 |

### Urgency, reliability and tokens

| Measure | Value |
| --- | --- |
| Urgency recall | 0.625 |
| Urgency precision | 1.0 |
| Urgency count fn | 9 |
| Urgency count fp | 0 |
| Urgency count tn | 56 |
| Urgency count tp | 15 |
| Reliability error_count | 0 |
| Reliability invalid_output_count | 0 |
| Reliability mean_attempts | 1.0 |
| Tokens mean_input | 1298.1875 |
| Tokens mean_output | 188.425 |

### Missed Urgent

| Report | Scenario | Text | Urgent probability | Review Triggers |
| --- | --- | --- | --- | --- |
| R-0019 | S-061 | Driver's report, as received: It's UN1263 paint, class 3 flammable, in 25-litre steel drums. They're upright, no leak seen and no smell. Customer in Bradford ha | 0.05 |  |
| R-0099 | S-061 | Hello, passing on the driver's account below.  Customer in Bradford has refused damaged Pennine Paints drums: three dented, with a lid cracked on one. All uprig | 0.05 |  |
| R-0204 | S-061 | At the Pennine Paints customer in Bradford, opening the trailer revealed three dented drums and one cracked lid. It's UN1263 paint, class 3 flammable, in 25-lit | 0.05 |  |
| R-0234 | S-001 | NV22 HPL has tipped at Brackenridge RDC Doncaster, three pallets short. Driver says the seal was intact when he opened the artic. Goods-in say the number on the | 0.05 |  |
| R-0286 | S-001 | Driver's report, as received: Driver says the seal was intact when he opened the artic. Goods-in say the number on the doors doesn't match the manifest. Three p | 0.05 |  |
| R-0297 | S-052 | Caller: NV20 RXC has rear-ended a car in slow traffic on the A34 near Oxford. Desk: Right, go on. Caller: The car driver says their neck hurts. Police are comin | 0.05 |  |
| R-0315 | S-061 | Caller: At the Pennine Paints customer in Bradford, opening the trailer revealed three dented drums and one cracked lid. Desk: Right, go on. Caller: The 25-litr | 0.05 |  |

### Latency and cost

| Measure | Value |
| --- | --- |
| Latency max | 296.22 |
| Latency n | 80 |
| Latency p50 | 214.7112 |
| Latency p95 | 248.5422 |
| Cost per_100 | 941.25 |
| Cost total | 753 |
| API USD / 1,000 | 0.0545 |

| Cost term | Total | Per 100 |
| --- | --- | --- |
| false_alarm | 0 | 0.0 |
| missed_urgent | 700 | 875.0 |
| review | 13 | 16.25 |
| wrong_category_same_destination | 0 | 0.0 |
| wrong_destination | 40 | 50.0 |

| Bootstrap measure | 95% interval |
| --- | --- |
| auto_routed_error_rate | [0.0571, 0.4] |
| cost_per_100 | [52.5, 2181.25] |
| review_rate | [0.0375, 0.325] |
| urgent_recall | [0.3125, 0.9167] |
