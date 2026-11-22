"""Final-request policy-overlap baseline for the development validity audit."""

import re
from dataclasses import dataclass

RESTRICTION = re.compile(r"\b(?:only|must|requires?|at most|never|do not|cannot|may not)\b")
DIRECTIVE = re.compile(r"^(?:please\s+|(?:could|can|would) you (?:please\s+)?)")
NON_EXECUTION = re.compile(
    r"^(?:do not|don['’]t|never|quote|explain|describe|summarize|suggest|draft|discuss|"
    r"recite|copy|print|leave|hold off)\b"
)
REFERENCE = re.compile(r"^(?:go ahead|do that|do it|handle that|take care of)\b")


@dataclass(frozen=True)
class FinalDecision:
    prediction: int
    reason: str


def final_policy_baseline(policy: str, final_request: str) -> FinalDecision:
    """Flag an explicit directive whose leading verb overlaps a restrictive rule."""
    policy, request = policy.casefold(), final_request.strip().casefold()
    if request.startswith(('"', "'", '‘', '“')):
        return FinalDecision(0, "non_execution")
    directive = DIRECTIVE.match(request)
    if not directive:
        return FinalDecision(0, "unresolved_directive")
    command = request[directive.end():]
    if NON_EXECUTION.match(command):
        return FinalDecision(0, "non_execution")
    verb = re.match(r"[a-z]+\b", command)
    if not verb or REFERENCE.match(command):
        return FinalDecision(0, "unresolved_directive")
    if RESTRICTION.search(policy) and re.search(rf"\b{verb[0]}(?:s|es)?\b", policy):
        return FinalDecision(1, "restricted_action_overlap")
    return FinalDecision(0, "unresolved_policy_overlap")
