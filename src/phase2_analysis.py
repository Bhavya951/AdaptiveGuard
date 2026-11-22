"""Paired whole-family bootstrap for Phase 2 development predictions."""

import random
from collections import Counter, defaultdict

from src.evaluate import percentile, scores

BOOTSTRAP_SEED = 20261125
BOOTSTRAP_DRAWS = 10_000
CONDITIONS = ("history_keyword", "context")
METRICS = ("f1", "false_positive_rate")


def family_draws(groups, draws, seed):
    rng = random.Random(seed)
    for _ in range(draws):
        yield rng.choices(groups, k=len(groups))


def interval(values):
    values.sort()
    return [percentile(values, p) for p in (0.025, 0.975)]


def differences(groups):
    totals = [Counter(), Counter()]
    for group in groups:
        for total, counts in zip(totals, group):
            total.update(counts)
    baseline, context = map(scores, totals)
    return {metric: context[metric] - baseline[metric] for metric in METRICS}


def paired_family_bootstrap(rows, *, draws=BOOTSTRAP_DRAWS, seed=BOOTSTRAP_SEED,
                            conditions=CONDITIONS):
    baseline, treatment = conditions
    if baseline == treatment:
        raise ValueError("Expected distinct baseline and treatment conditions")
    rows = tuple(rows)
    if not rows or any(row.get("split") != "development" for row in rows):
        raise ValueError("Phase 2 analysis accepts development predictions only")
    if type(draws) is not int or draws < 1 or type(seed) is not int:
        raise ValueError("Expected a positive integer draw count and an integer seed")
    if len({row["id"] for row in rows}) != len(rows):
        raise ValueError("Duplicate prediction ID")
    families = defaultdict(lambda: (Counter(), Counter()))
    for row in rows:
        family, label = row["family_id"], row["draft_label"]
        if not isinstance(family, str) or not family.strip():
            raise ValueError("Expected a family ID")
        for condition, counts in zip(conditions, families[family]):
            prediction = row["predictions"].get(condition)
            if any(type(value) is not int or value not in (0, 1)
                   for value in (label, prediction)):
                raise ValueError("Expected binary labels and paired predictions")
            counts[(("tn", "fp"), ("fn", "tp"))[label][prediction]] += 1

    family_ids = sorted(families)
    groups = [families[family] for family in family_ids]
    samples = {metric: [] for metric in METRICS}
    for sample in family_draws(groups, draws, seed):
        delta = differences(sample)
        for metric in METRICS:
            samples[metric].append(delta[metric])
    return {
        "contrast": f"{treatment} minus {baseline}",
        "seed": seed,
        "draws": draws,
        "family_count": len(groups),
        "differences": differences(groups),
        "percentile_ci95": {metric: interval(values) for metric, values in samples.items()},
        "family_metrics": {
            family: dict(zip(conditions, map(scores, families[family])))
            for family in family_ids
        },
    }


def development_coverage_interval(rows, *, condition):
    families = defaultdict(Counter)
    for row in rows:
        if row.get("split") != "development":
            raise ValueError("Coverage analysis accepts development predictions only")
        counts = families[row["family_id"]]
        counts["total"] += 1
        reason = row["decision_traces"][condition]["reason"]
        counts["resolved"] += not reason.startswith("unresolved")
    if not families:
        raise ValueError("Coverage analysis requires predictions")
    groups = [families[family] for family in sorted(families)]
    return interval([
        sum(group["resolved"] for group in sample) / sum(group["total"] for group in sample)
        for sample in family_draws(groups, BOOTSTRAP_DRAWS, BOOTSTRAP_SEED)
    ])
