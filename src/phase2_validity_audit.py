"""Run the Phase 2 development validity audit against a fixed authored challenge."""

import argparse
import hashlib
import inspect
import json
import platform
from collections import Counter
from pathlib import Path

from src.baseline import MARKER, predict
from src.evaluate import scores
from src.phase2_detector import detect
from src.phase2_evaluate import FIXTURES
from src.phase2_final_policy import final_policy_baseline

ROOT = Path(__file__).resolve().parents[1]
CHALLENGE = ROOT / "research/phase2_validity_challenge.jsonl"


def read_rows(data):
    return [json.loads(line) for line in data.splitlines()]


def keyword_coverage(rows):
    if not rows or any(row.get("split") != "development" for row in rows):
        raise ValueError("Keyword diagnostics require development data only")
    return {
        "marker": MARKER,
        "examples": len(rows),
        "final_hits": sum(predict(row["messages"][-1][1]) for row in rows),
        "earlier_example_hits": sum(any(predict(text) for _, text in row["messages"][:-1])
                                    for row in rows),
        "policy_hits": sum(predict(row["policy"]) for row in rows),
    }


def challenge_results(rows):
    if (not rows or len({row["id"] for row in rows}) != len(rows)
            or any(row.get("label_status") != "provisional"
                   or type(row.get("expected_label")) is not int
                   or row["expected_label"] not in (0, 1) or not row["rationale"].strip()
                   for row in rows)):
        raise ValueError("Challenge requires unique IDs and explicit provisional labels")
    counts = {name: Counter(dict.fromkeys(("tn", "fp", "fn", "tp"), 0)) for name in ("C", "D")}
    errors = {name: {"fp": Counter(), "fn": Counter()} for name in counts}
    unresolved = {name: [] for name in counts}
    decisions = []
    for row in rows:
        messages = tuple(map(tuple, row["messages"]))
        reference = row["expected_label"]
        case = {"id": row["id"], "category": row["category"], "expected_label": reference}
        for name, decision in (
            ("C", detect(row["policy"], messages)),
            ("D", final_policy_baseline(row["policy"], messages[-1][1])),
        ):
            outcome = (("tn", "fp"), ("fn", "tp"))[reference][decision.prediction]
            counts[name][outcome] += 1
            if outcome in errors[name]:
                errors[name][outcome][row["category"]] += 1
            if decision.reason.startswith("unresolved"):
                unresolved[name].append({"id": row["id"], "reason": decision.reason})
            case[name] = {"prediction": decision.prediction, "reason": decision.reason,
                          "outcome": outcome}
        decisions.append(case)
    return {
        "examples": len(rows),
        "metrics": {name: scores(counts[name]) for name in counts},
        "errors_by_category": errors,
        "unresolved": unresolved,
        "decisions": decisions,
    }


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    if FIXTURES.resolve() != FIXTURES or CHALLENGE.resolve() != CHALLENGE:
        raise SystemExit("Audit input paths must not redirect")
    development = FIXTURES.read_bytes()
    challenge = CHALLENGE.read_bytes()
    context_source = Path(inspect.getfile(detect)).read_bytes()
    report = {
        "configuration": {
            "scope": "development only",
            "reference": "manually authored provisional expectations",
            "python": platform.python_version(),
            "development_sha256": sha256(development),
            "challenge_sha256": sha256(challenge),
            "context_source_sha256": sha256(context_source),
            "final_policy_source_sha256": sha256(
                Path(inspect.getfile(final_policy_baseline)).read_bytes()
            ),
        },
        "keyword_coverage": keyword_coverage(read_rows(development)),
        **challenge_results(read_rows(challenge)),
    }
    args.output.mkdir(parents=True, exist_ok=False)
    (args.output / "report.json").write_bytes(
        (json.dumps(report, indent=2, sort_keys=True) + "\n").encode("utf-8")
    )
    (args.output / "context_source.py").write_bytes(context_source)


if __name__ == "__main__":
    main()
