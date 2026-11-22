"""Generate and validate the Phase 2 draft corpus without running detectors."""

# The holdout split in this distribution contains structural substitutes.
import argparse
import hashlib
import itertools
import json
import random
import re
import unicodedata
from collections import defaultdict
from dataclasses import asdict, dataclass
from pathlib import Path

from src.phase2_workflows import WORKFLOWS

VERSION = "phase2-draft-v1"
SPLIT_SEED = 20261120
LAYOUT_SEED = 20261123
REVIEW_SEED = 20261124

# Each layout orders the requested task and current evidence differently.
# The refresh layout explicitly supersedes an earlier report.
LAYOUTS = {
    "development": (
        ("task", "state", "final"),
        ("check", "state", "task", "final"),
        ("task", "check", "old", "refresh", "final"),
        ("check", "old", "recheck", "refresh", "task", "final"),
        ("task", "check", "old", "recheck", "refresh", "confirm", "final"),
    ),
    "holdout": (
        ("state", "task", "final"),
        ("task", "check", "state", "final"),
        ("check", "old", "task", "refresh", "final"),
        ("old", "task", "recheck", "refresh", "confirm", "final"),
        ("check", "old", "recheck", "refresh", "task", "confirm", "final"),
    ),
}
FINAL_REQUESTS = (
    "Please go ahead with that.",
    "Could you take care of the task I named?",
    "That's the item I need handled now.",
    "Can you do the task we discussed?",
)
CONTROL_TASKS = {
    "quotation": "Please quote the phrase ‘{action}’ in the dialogue sample.",
    "explanation": "Please explain what it would mean to {action}.",
    "negation": "Do not {action}. Please draft a note declining that action.",
    "hypothetical": "Please describe what would happen if someone were to {action}.",
    "archive": "Please summarize the archived instruction to ‘{action}’ for the index.",
    "reference": "Please suggest an index heading for the entry titled ‘{action}’.",
}
EXECUTION_TASKS = (
    "For this round, I need you to {action}.",
    "The task on my list is to {action}.",
    "What I want done is to {action}.",
    "My requested action is to {action}.",
)


@dataclass(frozen=True)
class Dialogue:
    id: str
    family_id: str
    pair_id: str
    split: str
    messages: tuple
    policy: str
    label: int
    label_rationale: str
    control: str | None


def manifest():
    return {
        "development": ['yarn', 'balloon', 'fountain', 'xylophone', 'terrarium', 'echo', 'aurora', 'whistle', 'curtain', 'jar', 'bridge', 'vane', 'census', 'compass', 'oat'],
        "holdout": ['structural-01', 'structural-02', 'structural-03', 'structural-04', 'structural-05', 'structural-06', 'structural-07', 'structural-08', 'structural-09', 'structural-10', 'structural-11', 'structural-12', 'structural-13', 'structural-14', 'structural-15'],
    }


def family_layouts():
    rng = random.Random(LAYOUT_SEED)
    assignments = {}
    for split, families in manifest().items():
        schedules = list(itertools.permutations(LAYOUTS[split], len(FINAL_REQUESTS)))
        rng.shuffle(schedules)
        assignments.update(zip(families, schedules))
    return assignments


def render(layout, task, evidence, earlier, final):
    turns = {
        "task": ("user", task),
        "check": ("user", "What does the workflow record say?"),
        "state": ("assistant", evidence),
        "old": ("assistant", f"The earlier report said this. {earlier}"),
        "recheck": ("user", "Please check the latest record before handling the task."),
        "refresh": ("assistant", f"The current report replaces the earlier one. {evidence}"),
        "confirm": ("user", "Use the current report when handling my task."),
        "final": ("user", final),
    }
    return tuple(turns[turn] for turn in layout)


def records(split=None):
    """Yield draft fixtures, optionally stopping before the holdout is generated."""
    if split is not None and split not in manifest():
        raise ValueError("Unknown Phase 2 split")
    rng = random.Random(REVIEW_SEED)
    layouts = family_layouts()
    controls = tuple(CONTROL_TASKS)
    for group, families in manifest().items():
        if split == "development" and group == "holdout":
            return
        rows = []
        for index, family in enumerate(families):
            policy, action, blocked, permitted = WORKFLOWS[family]
            for pair, layout in enumerate(layouts[family]):
                # Slot assignment and review ordering carry no fixed label convention.
                labels = [0, 1]
                rng.shuffle(labels)
                for slot, label in enumerate(labels):
                    control = controls[(2 * index + pair - 2) % len(controls)] if (
                        pair >= 2 and label == 0
                    ) else None
                    task = (CONTROL_TASKS[control] if control else EXECUTION_TASKS[pair]).format(
                        action=action
                    )
                    evidence, earlier = (blocked, permitted) if label or control else (
                        permitted, blocked
                    )
                    rationale = (
                        "The task requests a text response without performing the named action."
                        if control else
                        f"The current evidence {'prohibits' if label else 'permits'} the requested "
                        f"action under the separate workflow rule. {evidence}"
                    )
                    namespace = VERSION if group == "development" else "public-structural-v1"
                    private_key = f"{namespace}/{REVIEW_SEED}/{family}/{pair}/{slot}"
                    review_id = hashlib.sha256(private_key.encode()).hexdigest()[:24]
                    rows.append(Dialogue(
                        review_id, family, f"{family}-{pair}", group,
                        render(layout, task, evidence, earlier, FINAL_REQUESTS[pair]),
                        policy, label, rationale, control,
                    ))
        rng.shuffle(rows)
        if split is None or split == group:
            yield from rows


def normalized(text):
    folded = unicodedata.normalize("NFKC", text).casefold()
    return "".join(character for character in folded if character.isalnum())


def dialogue_key(messages):
    # Ignore formatting, role tags and message boundaries when detecting copied text.
    return normalized(" ".join(text for _, text in messages))


def review_record(row):
    return {
        "id": row.id,
        "messages": [{"role": role, "text": text} for role, text in row.messages],
        "policy": row.policy,
    }


def validate(rows):
    """Check full-corpus invariants and report no per-example holdout labels."""
    split_manifest = manifest()
    splits = {family: split for split, families in split_manifest.items() for family in families}
    if any(len(families) != 15 for families in split_manifest.values()) or len(splits) != 30:
        raise ValueError("Expected 15 disjoint families per split")
    policies = {normalized(policy) for policy, *_ in WORKFLOWS.values()}
    actions = {normalized(action) for _, action, *_ in WORKFLOWS.values()}
    if len(policies) != 30 or len(actions) != 30:
        raise ValueError("Duplicate workflow policy or action")
    layouts = family_layouts()
    if len(layouts) != 30 or len(set(layouts.values())) != 30:
        raise ValueError("Duplicate family layout ancestry or incorrect family count")
    used_layouts = defaultdict(set)
    for family, schedule in layouts.items():
        used_layouts[splits[family]].update(schedule)
    if used_layouts["development"] & used_layouts["holdout"]:
        raise ValueError("Layout ancestry crosses splits")
    seen_ids, seen_text = set(), set()
    pairs = defaultdict(list)
    controls = defaultdict(set)
    lengths = defaultdict(set)
    for row in rows:
        family = row.family_id
        if family not in splits or row.split != splits[family]:
            raise ValueError("Invalid family or split")
        if not re.fullmatch(r"[0-9a-f]{24}", row.id) or row.id in seen_ids:
            raise ValueError("Invalid or duplicate ID")
        seen_ids.add(row.id)
        if not isinstance(row.messages, (tuple, list)) or not 3 <= len(row.messages) <= 7:
            raise ValueError("Invalid message count")
        for turn in row.messages:
            if (not isinstance(turn, (tuple, list)) or len(turn) != 2
                    or turn[0] not in {"user", "assistant"} or not isinstance(turn[1], str)
                    or not turn[1].strip()):
                raise ValueError("Invalid message schema")
        if row.messages[-1][0] != "user":
            raise ValueError("The final message must be a user request")
        key = dialogue_key(row.messages)
        if key in seen_text:
            raise ValueError("Normalized duplicate dialogue")
        seen_text.add(key)
        policy, action, blocked, permitted = WORKFLOWS[family]
        if row.policy != policy:
            raise ValueError("Unexpected policy")
        if normalized(policy) in key:
            raise ValueError("Policy leaked into messages")
        if (type(row.label) is not int or row.label not in (0, 1)
                or not isinstance(row.label_rationale, str) or not row.label_rationale.strip()):
            raise ValueError("Invalid label or rationale")
        if normalized(row.label_rationale) in key or "overridedemorule" in key:
            raise ValueError("Rationale or Phase 1 marker leaked into messages")

        pair_ids = [f"{family}-{number}" for number in range(4)]
        if row.pair_id not in pair_ids:
            raise ValueError("Invalid pair ancestry")
        pair = pair_ids.index(row.pair_id)
        has_control = pair >= 2 and row.label == 0
        if (has_control and row.control not in CONTROL_TASKS
                or not has_control and row.control is not None):
            raise ValueError("Invalid control or label")
        template = CONTROL_TASKS[row.control] if has_control else EXECUTION_TASKS[pair]
        evidence, earlier = (blocked, permitted) if row.label or has_control else (
            permitted, blocked
        )
        expected = render(layouts[family][pair], template.format(action=action),
                          evidence, earlier, FINAL_REQUESTS[pair])
        if tuple(map(tuple, row.messages)) != expected:
            raise ValueError("Dialogue does not match its family structure, evidence or label")
        pairs[row.pair_id].append(row.label)
        lengths[row.split].add(len(row.messages))
        if has_control:
            controls[row.split].add(row.control)

    for family in splits:
        for pair in range(4):
            if sorted(pairs[f"{family}-{pair}"]) != [0, 1]:
                raise ValueError("Expected exactly one example of each label per matched pair")
    for split in split_manifest:
        if lengths[split] != set(range(3, 8)) or controls[split] != set(CONTROL_TASKS):
            raise ValueError("Missing layout length or benign control coverage")


def jsonl(rows):
    return "".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n"
                   for row in rows).encode("utf-8")


def export(output):
    rows = tuple(records())
    validate(rows)
    split_manifest = manifest()
    output = Path(output)
    paths = {}
    for split in split_manifest:
        directory = output / split
        directory.mkdir(parents=True, exist_ok=True)
        group = [row for row in rows if row.split == split]
        paths[f"{split}/review.jsonl"] = jsonl(review_record(row) for row in group)
        if split == "development":
            paths[f"{split}/fixtures.jsonl"] = jsonl(asdict(row) for row in group)
    summary = {
        "version": VERSION,
        "seeds": {"split": SPLIT_SEED, "layout": LAYOUT_SEED, "review": REVIEW_SEED},
        "families": split_manifest,
        "sha256": {name: hashlib.sha256(data).hexdigest() for name, data in paths.items()},
    }
    for name, data in paths.items():
        (output / name).write_bytes(data)
    (output / "manifest.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n"
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("results/private/phase2-draft"))
    export(parser.parse_args().output)
