"""Pure evaluation statistics. Undefined ratios are zero; empty percentiles are None."""

import math
import random


def ratio(numerator, denominator):
    return numerator / denominator if denominator else 0.0


def classification(actual, predicted, labels):
    if len(actual) != len(predicted):
        raise ValueError("decision lengths differ")
    matrix = {a: {p: 0 for p in labels} for a in labels}
    for a, p in zip(actual, predicted, strict=True):
        matrix[a][p] += 1
    per_class = {}
    for label in labels:
        tp = matrix[label][label]
        precision = ratio(tp, sum(matrix[a][label] for a in labels))
        recall = ratio(tp, sum(matrix[label].values()))
        per_class[label] = {"precision": precision, "recall": recall,
                            "f1": ratio(2 * precision * recall, precision + recall)}
    return {"accuracy": ratio(sum(matrix[a][a] for a in labels), len(actual)),
            "macro_f1": ratio(sum(v["f1"] for v in per_class.values()), len(labels)),
            "per_class": per_class, "confusion_matrix": matrix}


def agreement(actual, predicted):
    if len(actual) != len(predicted):
        raise ValueError("decision lengths differ")
    n = len(actual)
    raw = ratio(sum(a == p for a, p in zip(actual, predicted, strict=True)), n)
    labels = sorted(set(actual) | set(predicted))
    chance = sum(ratio(actual.count(a), n) * ratio(predicted.count(a), n) for a in labels)
    # Perfect constant labels have no disagreement, but chance agreement is also one.
    kappa = None if not n or chance == 1 else (raw - chance) / (1 - chance)
    return {"kappa": kappa, "raw_agreement": raw, "n": n}


def percentile(values, percent):
    """Nearest-rank percentile: sorted[ceil(percent / 100 * n) - 1]."""
    if not 0 <= percent <= 100:
        raise ValueError("percent must be in [0, 100]")
    ordered = sorted(values)
    return ordered[max(0, math.ceil(percent / 100 * len(ordered)) - 1)] if ordered else None


def cluster_bootstrap(rows, statistic, resamples=1000):
    """95% interval, resampling entire Scenarios, including repeated draws, with a fixed RNG."""
    clusters = {}
    for row in rows:
        clusters.setdefault(row['scenario_id'], []).append(row)
    ids = sorted(clusters)
    if not ids:
        return {key: [None, None] for key in statistic([])}
    rng = random.Random(20261027)
    samples = {}
    for _ in range(resamples):
        drawn = [row for _ in ids for row in clusters[rng.choice(ids)]]
        for key, value in statistic(drawn).items():
            samples.setdefault(key, []).append(value)
    return {key: [percentile(values, 2.5), percentile(values, 97.5)]
            for key, values in samples.items()}
