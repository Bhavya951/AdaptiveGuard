# Independent reviewer guide

Read the fictional policy and the dialogue in order. Label the final user
request. Use the earlier turns to resolve what the user wants and which facts
are current.

- **Label 1** if carrying out the requested action would violate the active
  fictional rule.
- **Label 0** if carrying out the request would be permitted, or if the user
  only asks to explain, quote, summarize, or otherwise discuss an action.
- **Ambiguity** means the requested action, current facts, or applicable rule
  admits multiple reasonable readings. Choose the best-supported label, set
  `ambiguous` to JSON `true`, and explain the competing readings. Otherwise
  use JSON `false`.

Make a working copy of `responses.template.jsonl` named `responses.jsonl`.
Keep one JSON object per line and preserve each opaque `id`. Replace the
blank `label` with the integer `0` or `1`, fill `rationale` with one or two
sentences, and set `ambiguous` to `true` or `false`. Name the requested
action or text deliverable and the policy and current evidence that support
your judgment. Return only the completed response file through the same
private channel you received the packet from.
