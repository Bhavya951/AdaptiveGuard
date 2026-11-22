"""Compare unchanged keyword baselines and Detector C on saved development data."""

import argparse
import hashlib
import json
import platform
from collections import Counter, defaultdict
from dataclasses import asdict
from pathlib import Path

from src.evaluate import predict_messages, scores
from src.phase2_analysis import development_coverage_interval, paired_family_bootstrap
from src.phase2_detector import detect

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "data/phase2-development.jsonl"
CONDITIONS = ("final_keyword", "history_keyword", "context")
MATCHED_CONDITIONS = ("context_final", "context_history")
OUTCOMES = (("tn", "fp"), ("fn", "tp"))


def validate_development(rows):
    if not rows or any(row.get("split") != "development" for row in rows):
        raise ValueError("Phase 2 scoring accepts development fixtures only")
    if len({row["id"] for row in rows}) != len(rows):
        raise ValueError("Duplicate development ID")
    if any(type(row["label"]) is not int or row["label"] not in (0, 1) for row in rows):
        raise ValueError("Expected binary draft labels")


def compare(rows):
    validate_development(rows)
    counts = {model: Counter(dict.fromkeys(("tn", "fp", "fn", "tp"), 0))
              for model in CONDITIONS}
    errors = {model: {"fp": Counter(), "fn": Counter()} for model in CONDITIONS}
    pairs = defaultdict(list)
    predictions = []
    for row in rows:
        messages = tuple(tuple(turn) for turn in row["messages"])
        policy = row["policy"]
        final, history = predict_messages(messages)
        decision = detect(policy, messages)

        reference = row["label"]
        outputs = dict(zip(CONDITIONS, (final, history, decision.prediction)))
        category = row["control"] or "execution"
        if category == "execution":
            category = "execution_updated_state" if any(
                "current report replaces" in text.lower() for role, text in messages
                if role == "assistant"
            ) else "execution_single_state"
        for model, output in outputs.items():
            outcome = (("tn", "fp"), ("fn", "tp"))[reference][output]
            counts[model][outcome] += 1
            if outcome in errors[model]:
                errors[model][outcome][category] += 1
        pairs[row["pair_id"]].append((reference, outputs))
        predictions.append({
            "id": row["id"], "split": row["split"], "family_id": row["family_id"],
            "draft_label": reference, "predictions": outputs,
            "dialogue_type": category, "message_count": len(messages),
            "context_trace": asdict(decision),
        })

    matched = [pair for pair in pairs.values()
               if len(pair) == 2 and {label for label, _ in pair} == {0, 1}]
    return {
        "examples": len(predictions),
        "metrics": {model: scores(count) for model, count in counts.items()},
        "errors_by_dialogue_type": errors,
        "context_error_reasons": Counter(
            row["context_trace"]["reason"] for row in predictions
            if row["draft_label"] != row["predictions"]["context"]
        ),
        "context_decision_reasons": Counter(row["context_trace"]["reason"] for row in predictions),
        "matched_pairs": {
            "count": len(matched),
            "both_correct": {model: sum(all(outputs[model] == label for label, outputs in pair)
                                        for pair in matched) for model in CONDITIONS},
        },
    }, predictions


def compare_matched_c(rows):
    rows = tuple(rows)
    validate_development(rows)
    predictions = []
    counts = {model: Counter() for model in MATCHED_CONDITIONS}
    sensitivity = {model: Counter() for model in MATCHED_CONDITIONS}
    unresolved = {model: {0: Counter(), 1: Counter()} for model in MATCHED_CONDITIONS}
    label_counts = Counter(row["label"] for row in rows)
    for row in sorted(rows, key=lambda row: row["id"]):
        messages = tuple(map(tuple, row["messages"]))
        label = row["label"]
        outputs, traces = {}, {}
        for model, turns in zip(MATCHED_CONDITIONS, (messages[-1:], messages)):
            decision = detect(row["policy"], turns)
            pending = decision.reason.startswith("unresolved")
            primary = 0 if pending else decision.prediction
            outputs[model] = primary
            traces[model] = asdict(decision)
            counts[model][OUTCOMES[label][primary]] += 1
            sensitivity[model][OUTCOMES[label][int(pending or primary)]] += 1
            if pending:
                unresolved[model][label][decision.reason] += 1
        predictions.append({
            "id": row["id"], "split": row["split"], "family_id": row["family_id"],
            "draft_label": label, "predictions": outputs, "decision_traces": traces,
        })

    coverage = {}
    for model, reasons in unresolved.items():
        by_label = {}
        for label in (0, 1):
            total = label_counts[label]
            resolved = total - sum(reasons[label].values())
            by_label[label] = {"resolved": resolved, "total": total,
                               "rate": resolved / total if total else None}
        resolved = sum(group["resolved"] for group in by_label.values())
        coverage[model] = {"resolved": resolved, "total": len(rows),
                           "rate": resolved / len(rows), "by_label": by_label}
    return {
        "examples": len(rows),
        "metrics": {model: scores(count) for model, count in counts.items()},
        "unresolved_as_positive_metrics": {
            model: scores(count) for model, count in sensitivity.items()
        },
        "unresolved_by_label_and_reason": unresolved,
        "coverage": coverage,
        "paired_family_bootstrap": paired_family_bootstrap(
            predictions, conditions=MATCHED_CONDITIONS
        ),
        "h3_development_diagnostic": {
            "always_positive_comparison": paired_family_bootstrap(
                [{**row, "predictions": {**row["predictions"], "always_positive": 1}}
                 for row in predictions],
                conditions=("always_positive", "context_history"),
            ),
            "history_coverage_ci95": development_coverage_interval(
                predictions, condition="context_history"
            ),
        },
    }, predictions


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path, help="New artifact directory")
    parser.add_argument("--matched-c", action="store_true", help="Compare full-history and final-turn C")
    args = parser.parse_args()
    if FIXTURES.resolve() != FIXTURES:
        raise SystemExit("Development fixture path must not redirect to another location")
    data = FIXTURES.read_bytes()
    rows = [json.loads(line) for line in data.splitlines()]
    if len(rows) != 120:
        raise SystemExit("Expected 120 saved development fixtures")
    command = ["python", "-m", "src.phase2_evaluate", "--output", str(args.output)]
    if args.matched_c:
        summary, predictions = compare_matched_c(rows)
        command.append("--matched-c")
    else:
        summary, predictions = compare(rows)
        summary["paired_family_bootstrap"] = paired_family_bootstrap(predictions)
    summary["configuration"] = {
        "scope": "Phase 2 development only",
        "reference": "generator draft labels, pending independent review",
        "python": platform.python_version(),
        "command": command,
        "development_fixture_sha256": hashlib.sha256(data).hexdigest(),
        "source_sha256": {name: hashlib.sha256((ROOT / "src" / name).read_bytes()).hexdigest()
                          for name in ("phase2_detector.py", "phase2_evaluate.py", "phase2_analysis.py",
                                       "baseline.py", "evaluate.py")},
    }
    args.output.mkdir(parents=True, exist_ok=False)
    for name, content in (("report.json", summary), ("predictions.json", predictions)):
        (args.output / name).write_text(json.dumps(content, indent=2, sort_keys=True) + "\n",
                                       encoding="utf-8", newline="\n")
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
