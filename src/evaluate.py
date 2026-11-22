"""Run the approved Phase 1 development evaluation."""
import argparse
import hashlib
import json
import platform
import random
from collections import Counter, defaultdict
from pathlib import Path

from src.baseline import predict
from src.fixtures import (
    MARKER_SEED, SPLIT_SEED, VERSION, canonical_fixture, fixture_hash, manifest,
    records, validate,
)

BOOTSTRAP_SEED = 20261121
BOOTSTRAP_DRAWS = 10_000
CONDITIONS = ("final", "history")


def predict_messages(messages):
    final = predict(messages[-1][1])
    history = int(final or any(predict(text) for _, text in messages[:-1]))
    return final, history


def development_predictions(dialogues):
    predictions = []
    for row in dialogues:
        if row.split != "development":
            raise ValueError("Phase 1 scoring accepts development fixtures only")
        final, history = predict_messages(row.messages)
        predictions.append({
            "id": row.id, "family_id": row.family_id, "pair_id": row.pair_id,
            "gold": row.label, "final": final, "history": history,
        })
    if not predictions:
        raise ValueError("No development predictions")
    return predictions


def ratio(numerator, denominator):
    return numerator / denominator if denominator else 0.0


def scores(counts):
    tn, fp, fn, tp = (counts[label] for label in ("tn", "fp", "fn", "tp"))
    return {
        "confusion_matrix": [[tn, fp], [fn, tp]],
        "precision": ratio(tp, tp + fp),
        "recall": ratio(tp, tp + fn),
        "false_positive_rate": ratio(fp, fp + tn),
        "f1": ratio(2 * tp, 2 * tp + fp + fn),
    }


def percentile(sorted_values, fraction):
    position = (len(sorted_values) - 1) * fraction
    lower = int(position)
    upper = min(lower + 1, len(sorted_values) - 1)
    return sorted_values[lower] + (position - lower) * (
        sorted_values[upper] - sorted_values[lower]
    )


def pool(families):
    pooled = {condition: Counter() for condition in CONDITIONS}
    for family in families:
        for condition in CONDITIONS:
            pooled[condition].update(family[condition])
    return {condition: scores(counts) for condition, counts in pooled.items()}


def delta(metrics):
    return metrics["history"]["f1"] - metrics["final"]["f1"]


def summarize(predictions, draws=BOOTSTRAP_DRAWS):
    families = defaultdict(lambda: {condition: Counter() for condition in CONDITIONS})
    flips = Counter()
    pair_labels = defaultdict(set)
    for row in predictions:
        pair_labels[row["pair_id"]].add(row["gold"])
        for condition in CONDITIONS:
            outcome = (("tn", "fp"), ("fn", "tp"))[row["gold"]][row[condition]]
            families[row["family_id"]][condition][outcome] += 1
        if row["history"] > row["final"]:
            flips[row["gold"]] += 1
    family_ids = sorted(families)
    groups = [families[family] for family in family_ids]
    rng = random.Random(BOOTSTRAP_SEED)
    deltas = sorted(delta(pool(rng.choices(groups, k=len(groups)))) for _ in range(draws))
    metrics = pool(groups)
    matched = [row for row in predictions if pair_labels[row["pair_id"]] == {0, 1}]
    pair_errors = {
        condition: sum(row[condition] != row["gold"] for row in matched)
        for condition in CONDITIONS
    }
    return {
        "metrics": metrics,
        "delta_f1": delta(metrics),
        "delta_f1_ci95": [percentile(deltas, 0.025), percentile(deltas, 0.975)],
        "positive_flips": {"negative_gold": flips[0], "positive_gold": flips[1]},
        "opposite_label_pair_diagnostic": {"dialogues": len(matched), "errors": pair_errors},
        "family_confusion_counts": families,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True, help="New artifact directory")
    args = parser.parse_args()
    dialogues = tuple(records())
    prevalence = validate(dialogues)
    digest = fixture_hash(dialogues)
    if digest != fixture_hash(records()):
        raise SystemExit("Fixture regeneration was not reproducible")
    development = [row for row in dialogues if row.split == "development"]
    predictions = development_predictions(development)
    summary = summarize(predictions)
    src = Path(__file__).resolve().parent
    config = {
        "split": "development", "fixture_version": VERSION, "fixture_sha256": digest,
        "development_fixture_sha256": fixture_hash(development),
        "python": platform.python_version(), "split_seed": SPLIT_SEED,
        "marker_seed": MARKER_SEED, "bootstrap_seed": BOOTSTRAP_SEED,
        "bootstrap_draws": BOOTSTRAP_DRAWS, "family_manifest": manifest(),
        "command": ["python", "-m", "src.evaluate", "--output", str(args.output)],
        "source_sha256": {
            name: hashlib.sha256((src / name).read_bytes()).hexdigest()
            for name in ("baseline.py", "fixtures.py", "evaluate.py")
        },
    }
    report = {"configuration": config, "marker_prevalence": prevalence, **summary}
    args.output.mkdir(parents=True, exist_ok=False)
    (args.output / "development-fixtures.jsonl").write_bytes(canonical_fixture(development))
    for name, content in (("report.json", report), ("predictions.json", predictions)):
        (args.output / name).write_text(json.dumps(content, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "split": "development", "dialogues": len(development), "fixture_sha256": digest,
        "marker_prevalence": prevalence, "metrics": summary["metrics"],
        "positive_flips": summary["positive_flips"], "delta_f1": summary["delta_f1"],
        "delta_f1_ci95": summary["delta_f1_ci95"],
    }, indent=2))


if __name__ == "__main__":
    main()
