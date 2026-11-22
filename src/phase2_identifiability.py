"""Development-only check of what a final-turn condition can identify."""

import json
from collections import Counter, defaultdict
from dataclasses import asdict
from fractions import Fraction

from src.evaluate import scores
from src.phase2 import records
from src.phase2_detector import detect
from src.phase2_evaluate import compare_matched_c, validate_development
from src.phase2_final_policy import final_policy_baseline


def input_identifiability(rows):
    """In-sample ceilings for deterministic rules over exact policy/final inputs."""
    rows = tuple(rows)
    validate_development(rows)
    groups = defaultdict(Counter)
    for row in rows:
        groups[(row["policy"], tuple(row["messages"][-1]))][row["label"]] += 1
    positives = sum(group[1] for group in groups.values())
    # An F1-optimal set of positive groups is a prefix ordered by positive share.
    # Adding a group helps exactly when its positive share exceeds current F1 / 2.
    ordered = sorted(groups.values(), key=lambda group: Fraction(group[1], group.total()),
                     reverse=True)
    best_f1, tp, selected = 0.0, 0, 0
    for group in ordered:
        tp += group[1]
        selected += group.total()
        best_f1 = max(best_f1, 2 * tp / (positives + selected))
    return {
        "exact_input_groups": len(groups),
        "opposite_label_groups": sum(bool(group[0] and group[1]) for group in groups.values()),
        "examples_in_opposite_label_groups": sum(group.total() for group in groups.values()
                                                if group[0] and group[1]),
        "accuracy_ceiling": sum(max(group.values()) for group in groups.values()) / len(rows),
        "f1_ceiling": best_f1,
    }


def placement_probe():
    """Cross policy thresholds with state values and move the same evidence across turns."""
    results = []
    for threshold in (6, 8):
        policy = f"Feed the cloth snail only when the moisture gauge drops below {threshold}."
        for reading in (4, 7, 9):
            evidence = f"The gauge reads {reading}"
            action = "Please feed the cloth snail."
            separate = (("assistant", evidence + "."), ("user", action))
            embedded = (("user", f"I just checked: {evidence}. {action}"),)
            results.append({
                "threshold": threshold, "reading": reading,
                "authored_expectation": int(reading >= threshold),
                "history_separate": asdict(detect(policy, separate)),
                "final_separate": asdict(detect(policy, separate[-1:])),
                "final_embedded": asdict(detect(policy, embedded)),
                "d_final_separate": asdict(final_policy_baseline(policy, action)),
                "d_final_embedded": asdict(final_policy_baseline(policy, embedded[-1][1])),
            })
    return results


def main():
    rows = [asdict(row) for row in records("development")]
    comparison, _ = compare_matched_c(rows)
    probes = placement_probe()
    probe_metrics = {}
    for model in ("history_separate", "final_separate", "final_embedded",
                  "d_final_separate", "d_final_embedded"):
        counts = Counter((("tn", "fp"), ("fn", "tp"))[row["authored_expectation"]][
            row[model]["prediction"]] for row in probes)
        probe_metrics[model] = scores(counts)
    print(json.dumps({
        "development": input_identifiability(rows),
        "matched_c": comparison,
        "placement_probe": probes,
        "placement_probe_metrics": probe_metrics,
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
