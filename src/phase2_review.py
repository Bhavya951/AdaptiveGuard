"""Prepare blinded Phase 2 review packets and triage independent submissions."""

import argparse
import hashlib
import json
import re
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

from src.phase2 import jsonl, manifest, records, review_record

PRIVATE_ROOT = Path(__file__).resolve().parents[1] / "results/private/phase2-review"
CHALLENGE_SOURCE = PRIVATE_ROOT.parents[2] / "research/phase2_validity_challenge.jsonl"
RESPONSE_FIELDS = {"id", "label", "rationale", "ambiguous"}


@dataclass(frozen=True)
class ChallengeItem:
    id: str
    label: int
    messages: tuple
    policy: str


def review_items(split):
    if split != "challenge":
        return tuple(records(split))
    items = []
    for line in CHALLENGE_SOURCE.read_text(encoding="utf-8").splitlines():
        row = json.loads(line, object_pairs_hook=unique_fields)
        label = row["expected_label"]
        if (row["label_status"] != "provisional" or type(label) is not int
                or label not in (0, 1) or not row["rationale"].strip()):
            raise ValueError("Challenge requires explicit provisional labels and rationales")
        opaque_id = hashlib.sha256(f"phase2-review-challenge-v1/{row['id']}".encode()).hexdigest()[:24]
        items.append(ChallengeItem(opaque_id, label, tuple(map(tuple, row["messages"])), row["policy"]))
    return tuple(sorted(items, key=lambda item: item.id))


def packet_bytes(rows):
    return jsonl(review_record(row) for row in rows)


def prepare(split, output):
    rows = review_items(split)
    packet = packet_bytes(rows)
    template = jsonl({"id": row.id, "label": None, "rationale": "", "ambiguous": None}
                     for row in rows)
    validate_packet(packet, template, 18 if split == "challenge" else 120)
    output = Path(output)
    output.mkdir(parents=True, exist_ok=False)
    (output / "review.jsonl").write_bytes(packet)
    (output / "responses.template.jsonl").write_bytes(template)


def unique_fields(pairs):
    result = dict(pairs)
    if len(result) != len(pairs):
        raise ValueError("Repeated JSON field")
    return result


def validate_packet(packet, template, expected_count):
    """Check the reviewer-facing schema and one empty response row per opaque ID."""
    def parse(data):
        rows = [json.loads(line, object_pairs_hook=unique_fields) for line in data.splitlines()]
        if len(rows) != expected_count:
            raise ValueError("Unexpected review packet or template count")
        ids = set()
        for row in rows:
            if (not isinstance(row, dict) or not isinstance(row.get("id"), str)
                    or not re.fullmatch(r"[a-f0-9]{24}", row["id"])):
                raise ValueError("Invalid opaque review ID")
            if row["id"] in ids:
                raise ValueError("Duplicate review ID")
            ids.add(row["id"])
        return rows, ids

    examples, example_ids = parse(packet)
    responses, response_ids = parse(template)
    if example_ids != response_ids:
        raise ValueError("Packet and template IDs differ")
    for row in examples:
        if (set(row) != {"id", "messages", "policy"}
                or not isinstance(row["policy"], str) or not row["policy"].strip()
                or not isinstance(row["messages"], list) or not row["messages"]):
            raise ValueError("Invalid blinded example schema")
        for turn in row["messages"]:
            if (not isinstance(turn, dict) or set(turn) != {"role", "text"}
                    or turn["role"] not in ("user", "assistant")
                    or not isinstance(turn["text"], str) or not turn["text"].strip()):
                raise ValueError("Invalid blinded message schema")
        if row["messages"][-1]["role"] != "user":
            raise ValueError("Blinded dialogue must end with a user request")
    for row in responses:
        if row != {"id": row["id"], "label": None, "rationale": "", "ambiguous": None}:
            raise ValueError("Response template must contain only blank review fields")
    return example_ids


def audit_responses(rows, lines, disagreement_key="generator_disagreement_ids"):
    """Return issue IDs and line numbers without exporting either set of labels."""
    rows = tuple(rows)
    draft = {row.id: row.label for row in rows}
    if len(draft) != len(rows):
        raise ValueError("Duplicate reference review ID")
    seen = defaultdict(list)
    valid = defaultdict(list)
    invalid = []
    for line_number, line in enumerate(lines, 1):
        if not line.strip():
            continue
        try:
            response = json.loads(line, object_pairs_hook=unique_fields)
        except ValueError:
            invalid.append({"line": line_number, "reason": "invalid JSON or repeated field"})
            continue
        if not isinstance(response, dict):
            invalid.append({"line": line_number, "reason": "expected a JSON object"})
            continue
        example_id = response.get("id")
        if not isinstance(example_id, str) or example_id not in draft:
            invalid.append({"line": line_number, "reason": "unknown or invalid example ID"})
            continue
        seen[example_id].append(line_number)
        if set(response) != RESPONSE_FIELDS:
            invalid.append({"line": line_number, "reason": "incorrect response fields"})
            continue
        label, rationale, ambiguous = (response[key] for key in ("label", "rationale", "ambiguous"))
        if label is None and rationale == "" and ambiguous is None:
            continue
        if (type(label) is not int or label not in (0, 1)
                or not isinstance(rationale, str) or not rationale.strip()
                or type(ambiguous) is not bool):
            invalid.append({"line": line_number, "reason": "invalid label, rationale or ambiguity"})
            continue
        valid[example_id].append((label, ambiguous))

    duplicates = {example_id: locations for example_id, locations in seen.items()
                  if len(locations) > 1}
    conflicts = sorted(example_id for example_id in duplicates
                       if len({label for label, _ in valid[example_id]}) > 1)
    usable = {example_id: responses[0] for example_id, responses in valid.items()
              if responses and example_id not in duplicates}
    return {
        "expected_count": len(draft),
        "usable_response_count": len(usable),
        "missing_review_ids": sorted(set(draft) - usable.keys()),
        "duplicate_response_lines": duplicates,
        "conflicting_review_ids": conflicts,
        "invalid_responses": invalid,
        "ambiguous_review_ids": sorted(example_id for example_id, responses in valid.items()
                                       if any(ambiguous for _, ambiguous in responses)),
        disagreement_key: sorted(example_id for example_id, (label, _) in usable.items()
                                 if label != draft[example_id]),
    }


def adjudicate(split, packet, responses, review_round):
    if not re.fullmatch(r"[a-zA-Z0-9_-]+", review_round):
        raise ValueError("Use letters, digits, hyphens or underscores for the review round")
    rows = review_items(split)
    expected = packet_bytes(rows)
    if Path(packet).read_bytes() != expected:
        raise ValueError("Review packet does not match the selected Phase 2 draft split")
    submitted = Path(responses).read_bytes()
    disagreement_key = ("provisional_disagreement_ids" if split == "challenge"
                        else "generator_disagreement_ids")
    report = audit_responses(rows, submitted.decode("utf-8-sig").splitlines(), disagreement_key)
    report.update({
        "split": split,
        "packet_sha256": hashlib.sha256(expected).hexdigest(),
        "responses_sha256": hashlib.sha256(submitted).hexdigest(),
    })
    directory = PRIVATE_ROOT / split
    if directory.resolve() != directory:
        raise ValueError("The private review report directory must not redirect to another path")
    directory.mkdir(parents=True, exist_ok=True)
    report_path = directory / f"adjudication-{review_round}.json"
    with report_path.open("x", encoding="utf-8", newline="\n") as handle:
        json.dump(report, handle, indent=2, sort_keys=True)
        handle.write("\n")
    return report_path


def verify_final_roster(split, packet, template, responses):
    """Validate a human adjudication roster against blinded inputs, without draft labels."""
    if split not in ("development", "holdout", "challenge"):
        raise ValueError("Unknown review split")
    packet_data, template_data, response_data = (
        Path(path).read_bytes() for path in (packet, template, responses)
    )
    expected = validate_packet(packet_data, template_data, 18 if split == "challenge" else 120)
    seen = set()
    for line in response_data.decode("utf-8-sig").splitlines():
        row = json.loads(line, object_pairs_hook=unique_fields)
        if not isinstance(row, dict) or set(row) != RESPONSE_FIELDS:
            raise ValueError("Invalid final decision fields")
        example_id = row["id"]
        if not isinstance(example_id, str) or example_id not in expected or example_id in seen:
            raise ValueError("Unknown or duplicate final decision ID")
        if (type(row["label"]) is not int or row["label"] not in (0, 1)
                or not isinstance(row["rationale"], str) or not row["rationale"].strip()
                or row["ambiguous"] is not False):
            raise ValueError("Final decisions require a binary label, rationale and resolved status")
        seen.add(example_id)
    if seen != expected:
        raise ValueError("Final decisions do not cover every packet ID")
    return {"split": split, "count": len(seen),
            "packet_sha256": hashlib.sha256(packet_data).hexdigest(),
            "template_sha256": hashlib.sha256(template_data).hexdigest(),
            "final_roster_sha256": hashlib.sha256(response_data).hexdigest()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    subcommands = parser.add_subparsers(dest="command", required=True)
    preparation = subcommands.add_parser("prepare")
    preparation.add_argument("--output", type=Path, required=True)
    adjudication = subcommands.add_parser("adjudicate")
    adjudication.add_argument("--packet", type=Path, required=True)
    adjudication.add_argument("--responses", type=Path, required=True)
    adjudication.add_argument("--round", required=True)
    verification = subcommands.add_parser("verify-final")
    verification.add_argument("--packet", type=Path, required=True)
    verification.add_argument("--template", type=Path, required=True)
    verification.add_argument("--responses", type=Path, required=True)
    for command in (preparation, adjudication, verification):
        command.add_argument("--split", choices=(*manifest(), "challenge"), required=True)
    arguments = parser.parse_args()
    try:
        if arguments.command == "prepare":
            prepare(arguments.split, arguments.output)
            print(f"Prepared blinded review files in {arguments.output}")
        elif arguments.command == "adjudicate":
            path = adjudicate(arguments.split, arguments.packet, arguments.responses, arguments.round)
            print(f"Saved private adjudication report to {path}")
        else:
            try:
                result = verify_final_roster(
                    arguments.split, arguments.packet, arguments.template, arguments.responses
                )
            except (OSError, ValueError):
                parser.exit(1, "Final roster verification failed. Check private input files.\n")
            print(json.dumps(result, sort_keys=True))
    except (OSError, ValueError) as error:
        parser.exit(1, f"Review command failed: {error}\n")


if __name__ == "__main__":
    main()
