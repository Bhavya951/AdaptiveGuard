"""Exploratory comparison using only the saved Phase 1 development fixtures."""
import argparse
import hashlib
import json
import platform
import re
from collections import Counter
from pathlib import Path

from src.evaluate import predict_messages, scores

ROOT = Path(__file__).resolve().parents[1]
DEVELOPMENT = ROOT / "results/private/phase1-development"


def context_rule(policy, messages):
    """Flag requests to perform the policy action while its blocking state holds."""
    opening, state, final = (text for _, text in messages)
    rule = re.fullmatch(r"In the .+?, do not (.+?) while the item is (.+)\.", policy)
    current = re.fullmatch(r"The item for this task is currently (.+)\.", state)
    if not rule or not current:
        raise ValueError("Unsupported synthetic policy or state")
    action, blocked = rule.groups()
    request = final.partition(" Reference tag:")[0]
    if request == f"Can you explain what it means to {action}?":
        performs_action = False
    elif request in (f"Please {action}.", f"Go ahead and {action}."):
        performs_action = True
    elif request == "Could you make that change now?" and (
        f"The change under discussion is to {action}." in opening
    ):
        performs_action = True
    else:
        raise ValueError("Unsupported synthetic request or unresolved reference")
    return int(performs_action and current[1] == blocked)


def compare(fixtures):
    if not fixtures or any(row["split"] != "development" for row in fixtures):
        raise ValueError("This comparison accepts development data only")
    predictions = []
    counts = {model: Counter() for model in ("keyword", "context")}
    paired = dict.fromkeys(("both_correct", "keyword_only_wrong",
                            "context_only_wrong", "both_wrong"), 0)
    for row in fixtures:
        _, keyword = predict_messages(row["messages"])
        context = context_rule(row["policy"], row["messages"])
        gold = row["label"]
        predictions.append({
            "id": row["id"], "family_id": row["family_id"], "pair_id": row["pair_id"],
            "gold": gold, "keyword": keyword, "context": context,
        })
        for model, predicted in (("keyword", keyword), ("context", context)):
            outcome = (("tn", "fp"), ("fn", "tp"))[gold][predicted]
            counts[model][outcome] += 1
        category = (("both_correct", "context_only_wrong"),
                    ("keyword_only_wrong", "both_wrong"))
        paired[category[keyword != gold][context != gold]] += 1
    return predictions, {model: scores(count) for model, count in counts.items()}, paired


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True, help="New artifact directory")
    parser.add_argument("--development", type=Path, default=DEVELOPMENT,
                        help="Artifact directory from src.evaluate")
    args = parser.parse_args()
    reference = json.loads((args.development / "report.json").read_bytes())
    config = reference["configuration"]
    fixture_bytes = (args.development / "development-fixtures.jsonl").read_bytes()
    if sha256(fixture_bytes) != config["development_fixture_sha256"]:
        raise SystemExit("Saved development fixture hash mismatch")
    frozen = {name: sha256((ROOT / "src" / name).read_bytes())
              for name in config["source_sha256"]}
    if frozen != config["source_sha256"]:
        raise SystemExit("Frozen Phase 1 source hash mismatch")
    rows = [json.loads(line) for line in fixture_bytes.splitlines()]
    predictions, metrics, paired = compare(rows)
    prior = {row["id"]: row["history"]
             for row in json.loads((args.development / "predictions.json").read_bytes())}
    if {row["id"]: row["keyword"] for row in predictions} != prior:
        raise SystemExit("Keyword predictions differ from saved development predictions")
    report = {
        "scope": "exploratory development only",
        "configuration": {
            "python": platform.python_version(), "dialogues": len(rows),
            "family_ids": sorted({row["family_id"] for row in rows}),
            "development_fixture_sha256": sha256(fixture_bytes),
            "source_sha256": {**frozen, "exploratory.py": sha256(Path(__file__).read_bytes())},
        },
        "metrics": metrics,
        "paired_errors": paired,
    }
    args.output.mkdir(parents=True, exist_ok=False)
    for name, data in (("predictions.json", predictions), ("report.json", report)):
        (args.output / name).write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
