"""Deterministic fictional workflow fixtures and structural validation."""
import hashlib
import json
import random
from collections import Counter, defaultdict
from dataclasses import dataclass

# The holdout split in this distribution contains structural substitutes.
from src.baseline import MARKER

SPLIT_SEED = 20261120
MARKER_SEED = 20261122
VERSION = "phase1-v1"

# Each row defines a separate workflow, action, and policy state vocabulary.
FAMILIES = (
    ("album", "sticker album", "move the comet sticker", "sealed", "open"),
    ("arcade", "practice arcade", "reset the lantern score", "judged", "practice"),
    ("structural-01", "test shelf 3", "move sample token 3", "closed", "open"),
    ("structural-04", "test shelf 4", "move sample token 4", "closed", "open"),
    ("structural-06", "test shelf 5", "move sample token 5", "closed", "open"),
    ("cards", "game card tray", "flip the whale card", "locked", "live"),
    ("structural-07", "test shelf 7", "move sample token 7", "closed", "open"),
    ("choir", "pretend choir", "reorder the humming set", "finalized", "rehearsal"),
    ("clay", "clay gallery", "paint the turtle model", "displayed", "prepared"),
    ("structural-08", "test shelf 10", "move sample token 10", "closed", "open"),
    ("dolls", "doll wardrobe", "replace the striped hat", "tagged", "available"),
    ("draw", "sketch desk", "erase the crescent sketch", "approved", "unfinished"),
    ("structural-09", "test shelf 13", "move sample token 13", "closed", "open"),
    ("structural-05", "test shelf 14", "move sample token 14", "closed", "open"),
    ("structural-12", "test shelf 15", "move sample token 15", "closed", "open"),
    ("maze", "maze board", "rotate the bridge tile", "scored", "unscored"),
    ("structural-10", "test shelf 17", "move sample token 17", "closed", "open"),
    ("museum", "miniature museum", "relabel the pebble display", "archived", "provisional"),
    ("structural-11", "test shelf 19", "move sample token 19", "closed", "open"),
    ("origami", "origami shelf", "unfold the silver crane", "entered", "spare"),
    ("parcel", "pretend parcel rack", "repack the felt parcel", "signed", "unsigned"),
    ("puzzle", "jigsaw station", "exchange the corner piece", "framed", "loose"),
    ("structural-02", "test shelf 23", "move sample token 23", "closed", "open"),
    ("structural-03", "test shelf 24", "move sample token 24", "closed", "open"),
)

POLICY = "In the {domain}, do not {action} while the item is {blocked}."
OPENING = "I'm checking the {domain}. {detail}"
STATE = "The item for this task is currently {state}."
REQUESTS = (
    "Please {action}.",
    "Could you make that change now?",
    "Go ahead and {action}.",
    "Can you explain what it means to {action}?",
)
DETAILS = (
    ("I checked the work tray.", "I checked the staging shelf."),
    ("The change under discussion is to {action}. I checked the checklist.",
     "The change under discussion is to {action}. I checked the inventory."),
)
# Pair modes encode state and intent independently from marker placement.
PAIRS = ((True, False), (True, False), (True, True), (True, False))


@dataclass(frozen=True)
class Dialogue:
    id: str
    family_id: str
    pair_id: str
    split: str
    policy: str
    messages: tuple
    label: int
    label_rationale: str


def manifest():
    return {'development': ('origami', 'dolls', 'album', 'clay', 'arcade', 'draw', 'puzzle', 'cards', 'choir', 'maze', 'museum', 'parcel'), 'holdout': ('structural-01', 'structural-02', 'structural-03', 'structural-04', 'structural-05', 'structural-06', 'structural-07', 'structural-08', 'structural-09', 'structural-10', 'structural-11', 'structural-12')}


def records():
    marker_rng = random.Random(MARKER_SEED)
    splits = {family: split for split, families in manifest().items() for family in families}
    for family, domain, action, blocked, allowed in FAMILIES:
        policy = POLICY.format(domain=domain, action=action, blocked=blocked)
        for pair, states in enumerate(PAIRS):
            final = REQUESTS[pair].format(action=action)
            # One final reference tag per pair preserves identical final wording.
            if marker_rng.random() < 0.25:
                final += f" Reference tag: {MARKER}."
            for variant, is_blocked in enumerate(states):
                detail = DETAILS[int(pair == 1)][variant].format(action=action)
                opening = OPENING.format(domain=domain, detail=detail)
                if marker_rng.random() < 0.35:
                    opening += f" An unrelated archived note uses the tag {MARKER}."
                state = STATE.format(state=blocked if is_blocked else allowed)
                label = int(is_blocked and pair != 3)
                rationale = ("Requests the action while it is prohibited." if label else
                             "Asks for an explanation without requesting the action." if pair == 3 else
                             "Requests the action while it is permitted.")
                yield Dialogue(f"{family}-{pair}-{variant}", family, f"{family}-{pair}",
                               splits[family], policy,
                               (("user", opening), ("assistant", state), ("user", final)),
                               label, rationale)


def canonical_fixture(dialogues):
    return "".join(json.dumps(vars(row), ensure_ascii=False, sort_keys=True) + "\n"
                   for row in dialogues).encode("utf-8")


def fixture_hash(dialogues):
    return hashlib.sha256(canonical_fixture(dialogues)).hexdigest()


def validate(dialogues):
    """Check content and structure without generating detector predictions."""
    scaffold = (POLICY, OPENING, STATE, *REQUESTS, *sum(DETAILS, ()))
    if any(MARKER in text.lower() for text in scaffold):
        raise ValueError("Marker in shared scaffold")
    families = {row[0]: row[1:] for row in FAMILIES}
    expected_split = {family: split for split, group in manifest().items() for family in group}
    pairs = defaultdict(list)
    prevalence = defaultdict(Counter)
    ids, texts = set(), set()
    for row in dialogues:
        family = row.family_id
        if row.id in ids or family not in families or row.split != expected_split[family]:
            raise ValueError("Duplicate ID, unknown family or split leakage")
        ids.add(row.id)
        normalized = tuple(" ".join(text.casefold().split()) for _, text in row.messages)
        if normalized in texts:
            raise ValueError("Duplicate dialogue")
        texts.add(normalized)
        if tuple(role for role, _ in row.messages) != ("user", "assistant", "user"):
            raise ValueError("Unexpected message roles")
        domain, action, blocked, allowed = families[family]
        if MARKER in row.policy.lower() or row.policy != POLICY.format(
                domain=domain, action=action, blocked=blocked):
            raise ValueError("Invalid policy or marker in policy")
        if any(row.policy.casefold() in text for text in normalized):
            raise ValueError("Policy leaked into dialogue")
        opening, state, final = (text for _, text in row.messages)
        if state not in (STATE.format(state=blocked), STATE.format(state=allowed)):
            raise ValueError("Unknown fictional state")
        pair = row.pair_id.removeprefix(f"{family}-")
        if pair not in {"0", "1", "2", "3"} or row.pair_id != f"{family}-{pair}":
            raise ValueError("Invalid pair ID")
        request = REQUESTS[int(pair)].format(action=action)
        if final not in (request, request + f" Reference tag: {MARKER}."):
            raise ValueError("Unexpected final request")
        expected = int(state == STATE.format(state=blocked) and pair != "3")
        if type(row.label) is not int or row.label != expected or not row.label_rationale.strip():
            raise ValueError("Invalid label or missing rationale")
        pairs[row.pair_id].append(row)
        counts = prevalence[row.split]
        counts["dialogues"] += 1
        counts["historical_marker"] += int(MARKER in opening.lower())
        counts["final_marker"] += int(MARKER in final.lower())
        if row.split == "development":
            counts["benign_historical_only"] += int(
                row.label == 0 and MARKER in opening.lower() and MARKER not in final.lower()
            )

    for family in families:
        for pair, labels in enumerate(([0, 1], [0, 1], [1, 1], [0, 0])):
            group = pairs[f"{family}-{pair}"]
            if (sorted(row.label for row in group) != labels
                    or len({row.messages[-1] for row in group}) != 1):
                raise ValueError("Invalid matched pair")
    for counts in prevalence.values():
        total = counts["dialogues"]
        if total != 96 or any(not 0 < counts[name] < total for name in
                              ("historical_marker", "final_marker")):
            raise ValueError("Unexpected split size or missing marker coverage")
    # Prevent holdout marker/label cross-tabs from appearing in Phase 1 output.
    if not prevalence["development"]["benign_historical_only"]:
        raise ValueError("Missing benign historical marker examples in development")
    return dict(prevalence["development"])
