"""Text-only rule interpreter for fictional workflows."""

import re
from dataclasses import dataclass

NUMBERS = {word: value for value, word in enumerate(
    "zero one two three four five six seven eight nine ten".split()
)}
NUMBER = r"(?:\d+|" + "|".join(NUMBERS) + ")"
REFERENCE = re.compile(
    r"(?:go ahead with (?:that|the cue)|(?:take care of|do|handle) (?:that|the task\b.*)|"
    r"that(?:'s| is) the item i need handled now)"
)
DECLARATION = re.compile(
    r"(?:for this round, )?i need you to (.+)|"
    r"(?:the task on my list|what i want done|my requested action|my cue) is to (.+)"
)
TEXT_TASK = re.compile(
    r"(?:quote|explain|describe|summarize|suggest|draft|discuss)\b"
)
CANCEL = re.compile(r"(?:do not|don't|never|cancel|hold off|leave .+ (?:shut|closed))\b")
ARCHIVED = re.compile(r"(?:the earlier report|previously\b|archived\b)")
UPDATE = re.compile(r"^(?:the current report replaces the earlier one[.:]|(?:correction|update|now):)\s*")
USER_REPORT = re.compile(r"^i (?:just )?(?:checked|measured|confirmed): ([^.?!]+)[.?!]\s+(.+)$")
QUOTED = re.compile(r"(?<!\w)'[^']+'(?!\w)|\"[^\"]+\"")
ACTION_VERBS = r"project|send|move|count|add|open|record|sound|award|combine|pool|give|reveal|submit|activate|feed"
COMPOUND = re.compile(
    rf"\b(?:and then|and also|or else|(?:and|or) (?:{ACTION_VERBS}|do|play)\b)"
)

# The action pattern establishes applicability. The policy pattern identifies a
# constraint, and the corresponding interpreter extracts operands from evidence.
RULES = (
    ("empty space", r"only into an empty (\w+)", r"project\b", "occupancy"),
    ("single occupancy", r"only one .+ at a time", r"(?:send|move) .+ across", "bridge"),
    ("occupied item", r"count only occupied \w+", r"(?:add|count) (?:the )?(\w+ nest)\b", "nest"),
    ("all lights", r"only after both cue lamps light up", r"open .+ curtain", "lamps"),
    ("motion stopped", r"only when the pointer has stopped moving", r"record .+ direction", "motion"),
    ("destination reached", r"only at the destination pier", r"sound .+ whistle", "arrival"),
    ("minimum measurement", r"shortest measured tail wins", r"award .+ to (?:the )?(\w+) ribbon", "minimum"),
    ("different origins", r"made in different rooms", r"combine\b", "origins"),
    ("shared origin", r"only scraps from the same dye bath", r"pool\b", "bath"),
    ("direction away", r"point away from the hidden counter", r"give (north|south|east|west)\b", "direction"),
    ("holder authorization", r"current clue holder reveal", r"reveal .+ on behalf of (?:the )?(.+)", "holder"),
    ("declared category", r"declared texture category",
     r"submit (?:the )?(.+) in (?:the )?(\w+) class", "category"),
    ("majority", r"only a majority unlocks a pattern", r"activate (?:the )?(\w+) pattern", "majority"),
    ("strict upper limit", rf"gauge drops below ({NUMBER})\b", r"feed\b", "threshold"),
    ("reversed sequence", r"reversing the three-note demo", r"give .+ token\b", "reverse"),
)


@dataclass(frozen=True)
class Decision:
    prediction: int
    reason: str
    action: str | None = None
    rule: str | None = None
    evidence_turn: int | None = None
    evidence: str | None = None


def plain(text):
    return " ".join(text.lower().translate(str.maketrans("‘’“”", "''\"\"")).split())


def request(text):
    """Resolve one task-bearing clause, preserving negation and quoted scope."""
    surface = QUOTED.sub("<quotation>", text).strip(" .?!")
    surface = re.sub(r"^(?:please |(?:could|can|would) you (?:please )?)", "", surface)
    if REFERENCE.fullmatch(surface):
        return "reference", None
    if COMPOUND.search(surface):
        return "ambiguous", None
    declaration = DECLARATION.fullmatch(surface)
    if declaration:
        surface = declaration[1] or declaration[2]
    if re.fullmatch(r"(?:put|copy|print) <quotation> (?:on|in) .+", surface):
        return "discussion", None
    if CANCEL.match(surface) or TEXT_TASK.match(surface) or surface.startswith("<quotation>"):
        # A negated action can accompany a text task. A second execution
        # request, however, requires disambiguation.
        following = re.split(r"[.!?]\s+", surface)[1:]
        if any(not TEXT_TASK.match(clause.removeprefix("please ")) for clause in following):
            return "ambiguous", None
        return "discussion", None
    if declaration or re.match(rf"(?:{ACTION_VERBS})\b", surface):
        if re.search(r"[.!?]\s", surface):
            return "ambiguous", None
        return "execute", surface
    return "unknown", None


def resolve_request(messages, final_request):
    intent, action = request(final_request)
    if intent != "reference":
        return intent, action
    candidates = {parsed for role, text in messages[:-1] if role == "user"
                  if (parsed := request(plain(text)))[0] != "unknown"}
    if len(candidates) == 1:
        return candidates.pop()
    return "ambiguous", None


def current_evidence(messages, interpret, user_report):
    if user_report is not None:
        evidence = QUOTED.sub("", user_report)
        return len(messages), evidence, interpret(evidence)
    for index in range(len(messages) - 2, -1, -1):
        role, text = messages[index]
        if role != "assistant":
            continue
        state = QUOTED.sub("", plain(text))
        if ARCHIVED.match(state):
            continue
        update = UPDATE.match(state)
        evidence = UPDATE.sub("", state)
        satisfied = interpret(evidence)
        # An explicit replacement supersedes the earlier state even when
        # the replacement cannot be resolved. Unrelated turns do not.
        if update or satisfied is not None:
            return index + 1, evidence, satisfied
    return None, None, None


def number(token):
    return int(token) if token.isdecimal() else NUMBERS[token]


def contrast(evidence, satisfies, violates):
    permitted = bool(re.search(satisfies, evidence))
    blocked = bool(re.search(violates, evidence))
    return permitted if permitted != blocked else None


def condition(kind, rule, action, evidence):
    """Return whether the policy condition holds, or None if unresolved."""
    if kind == "occupancy":
        location = re.escape(rule[1])
        return contrast(evidence, rf"\b{location} is empty\b",
                        rf"\b(?:seated|sitting|standing) in the {location}\b|"
                        rf"\b{location} is (?:occupied|not empty)\b")
    if kind == "bridge":
        return contrast(evidence, r"bridge is clear", r"cart is (?:still )?on the bridge")
    if kind == "nest":
        nest = re.escape(action[1])
        return contrast(evidence, rf"\b(?:sitting|nesting) in the {nest}\b|\b{nest} is occupied\b",
                        rf"\b{nest} is empty\b")
    if kind == "lamps":
        return contrast(evidence, r"both cue (?:lamps|lights) are (?:lit|on)",
                        r"(?:lamp|one|cue|light) is (?:dark|off|unlit|out)")
    if kind == "motion":
        return contrast(evidence, r"pointer has (?:settled|stopped)", r"pointer is (?:still )?(?:swaying|moving)")
    if kind == "arrival":
        return contrast(evidence, r"(?:tied up|is|has arrived) at the destination pier",
                        r"cast off from .+ starting pier|still at the starting pier|"
                        r"not (?:at|reached) the destination pier")
    if kind == "minimum":
        measurements = {name: number(value) for name, value in re.findall(
            rf"(\w+) tail measures ({NUMBER})\b", evidence
        )}
        target = action[1]
        if target in measurements and len(measurements) > 1:
            return measurements[target] == min(measurements.values())
        return None
    if kind in {"origins", "bath"}:
        pattern = (r"came from (?:the )?(\w+) room" if kind == "origins"
                   else r"came from bath (\w+)")
        origins = re.findall(pattern, evidence)
        if len(origins) == 2:
            return (origins[0] == origins[1]) == (kind == "bath")
        if len(origins) == 1 and evidence.startswith("both "):
            return kind == "bath"
        return None
    if kind == "direction":
        observed = re.search(r"counter is (?:due )?(north|south|east|west)\b", evidence)
        opposite = {"north": "south", "south": "north", "east": "west", "west": "east"}
        return action[1] == opposite[observed[1]] if observed else None
    if kind == "holder":
        holder = re.search(r"(?:^|[.!?] )(?:the )?([\w -]+) holds the clue tile\b", evidence)
        return holder[1] == action[1] if holder else None
    if kind == "category":
        item = re.escape(action[1])
        description = re.search(rf"describes (?:the )?{item} as (\w+)\b", evidence)
        return description[1] == action[2] if description else None
    if kind == "majority":
        votes = re.search(rf"({NUMBER}) drops voted for the (\w+) and ({NUMBER}) voted for other patterns", evidence)
        if votes and votes[2] == action[1]:
            return number(votes[1]) > number(votes[3])
        return None
    if kind == "threshold":
        observed = re.search(rf"(?:gauge reads|(?:moisture )?reading is(?: at)?) ({NUMBER})\b", evidence)
        return number(observed[1]) < number(rule[1]) if observed else None
    if kind == "reverse":
        demo = re.search(r"demo was ([a-g-]+) and .+ played ([a-g-]+)", evidence)
        if demo:
            return demo[1].split("-")[::-1] == demo[2].split("-")
        return None
    raise ValueError(f"Unknown rule interpreter {kind}")


def detect(policy: str, messages: tuple[tuple[str, str], ...]) -> Decision:
    """Use only the active rule text and ordered role/text turns ending at the request."""
    if not messages or messages[-1][0] != "user":
        raise ValueError("The dialogue must end with a user turn")
    final = plain(messages[-1][1])
    report = USER_REPORT.fullmatch(final)
    intent, action = resolve_request(messages, report[2] if report else final)
    if intent == "discussion":
        return Decision(0, "non_execution")
    if intent != "execute":
        return Decision(0, "unresolved_request")
    policy = plain(policy)
    applicable = []
    for name, policy_pattern, action_pattern, kind in RULES:
        rule_match = re.search(policy_pattern, policy)
        action_match = re.search(action_pattern, action)
        if rule_match and action_match:
            applicable.append((name, rule_match, action_match, kind))
    if len(applicable) != 1:
        return Decision(0, "unresolved_policy_or_action", action)
    name, rule_match, action_match, kind = applicable[0]
    def interpret(evidence):
        return condition(kind, rule_match, action_match, evidence)

    turn, evidence, satisfied = current_evidence(messages, interpret, report[1] if report else None)
    if satisfied is None:
        return Decision(0, "unresolved_state", action, name, turn, evidence)
    return Decision(int(not satisfied), "permitted" if satisfied else "violation",
                    action, name, turn, evidence)
