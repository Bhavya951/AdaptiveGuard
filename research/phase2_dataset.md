# Phase 2 draft dataset and review handoff

Run `python -m src.phase2` from the repository root to regenerate the draft in
`results/private/phase2-draft`. An optional `--output` path writes another
copy. The manifest records the version, seeds, split membership and SHA-256
checksums of exported files. Draft generation does not run a detector.

The 30 fictional workflows have separately authored rules, actions and
evidence. Each family contributes four opposite-label pairs with identical
final requests. In two pairs the current evidence changes whether the requested
action is permitted. In the other two the evidence forbids the named action
in both dialogues, and the requested deliverable changes from execution to a
benign text task. Each split covers quotation, explanation, negation,
hypothetical discussion, archived instructions and harmless references.

Development and holdout each use five different message layouts covering
lengths three through seven. Families have distinct four-layout assignments.
Some layouts present the task first and others present the evidence first.
Longer layouts explicitly replace an earlier report with a current report.
The splits share turn-building code and some phrases, including matched final
requests and control phrasing. Performance on these fixtures would therefore
only test generalization across the authored workflows and layout orderings.

## Prepare and submit independent reviews

Run these commands from the repository root. Each output directory must be
new. To regenerate an existing packet, choose a fresh output directory.

```powershell
python -m src.phase2_review prepare --split development --output results/private/phase2-review/development/packet
python -m src.phase2_review prepare --split holdout --output results/private/phase2-review/holdout/packet
```

Give the reviewer only `review.jsonl` and `responses.template.jsonl` from the
appropriate packet directory. Each dialogue record provides an opaque ID,
ordered messages and a separate fictional policy. Keep the draft fixtures,
generator source, manifest and adjudication reports out of the blind handoff.

Reviewers make a copy of the template named `responses.jsonl` and fill one row
per ID. Keep the ID intact. Enter integer `1` if executing the resolved final
request would violate the active rule and integer `0` if execution would be
permitted or the request merely discusses an action. Write a short rationale
and set `ambiguous` to JSON `true` or `false`. If a case is ambiguous, give
the best-supported label and describe the uncertainty. Blank template rows
remain pending.

## Triage and adjudicate

Keep the original packet bytes and the returned response file. Use a unique
round name to preserve the report from each submission. For example, after
saving the returned development response file in its split directory, run:

```powershell
python -m src.phase2_review adjudicate --split development --packet results/private/phase2-review/development/packet/review.jsonl --responses results/private/phase2-review/development/responses.jsonl --round round-1
```

For holdout, use `--split holdout` and the corresponding holdout paths. The
command verifies that the packet matches the selected draft split and writes
`adjudication-<round>.json` in that split's private review directory. The report
identifies generator disagreements, ambiguous cases, missing usable reviews,
and duplicate or conflicting submissions. A duplicate blocks the affected ID
from comparison until corrected. Line-level diagnostics flag malformed and
invalid responses. Reports include input checksums and omit both label values
and rationales.

Keep returned holdout responses, reports and manual decisions under
`results/private/phase2-review/holdout` and restrict access to the holdout
review and adjudication team. A disagreement ID can reveal a draft label when
paired with a submitted binary label. The directory layout and CLI prevent
routine cross-split exports, while access control is the repository owner's
responsibility. Development review commands stop before generating holdout
fixtures.

Have a human adjudicator resolve disagreements and ambiguity against the
policy and dialogue. Record each decision by ID with the adjudicated label,
rationale and any revision in a separate private record. If a dialogue is
revised, obtain a new independent review for the revised content. The script
only reports issues and never assigns final labels. Independent review and
manual adjudication must finish before dataset freeze.

The separate 18-example development challenge uses the same review and
response schema. Its private adjudication report compares submissions against
the manually authored provisional expectations. See the reviewer guide and
pre-freeze checklist for the three-packet handoff and exact adjudication commands.
