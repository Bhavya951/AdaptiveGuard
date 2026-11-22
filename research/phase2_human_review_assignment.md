# Phase 2 human-review assignment and adjudication

**Assignment pending.** Record names privately before distributing packets.

| Assignment | Owner fills in |
| --- | --- |
| Independent reviewer(s), per group | Development 120, challenge 18, holdout 120. Confirm who covers each group and the number of independent first passes. |
| Adjudicator | Confirm who resolves issues and signs the final label roster. |
| Holdout custodian | Confirm who distributes the restricted packet and retains the holdout responses, final labels and audit records. |

1. Confirm that reviewers are independent of fixture authoring and detector development. Give each reviewer only their group's `review.jsonl`, blank response template, and [rubric](phase2_reviewer_guide.md). The custodian handles the holdout handoff privately.
2. Have each reviewer return a private response file with opaque ID, label, rationale, and ambiguity flag. Preserve each original submission with group and round. Keep draft labels, detector predictions, AI judgments and other reviewers' answers out of the first pass.
3. Use the internal triage commands to check gaps, invalid entries, duplicates, ambiguity and disagreements. Request corrections or missing responses. The adjudicator records the final human judgment, rationale, and any revision by ID. Have revised examples independently reviewed again.
4. Check complete one-to-one final label coverage and retain decisions, revisions and digests privately. The custodian signs off on the holdout roster and access controls. Keep the adjudicated corpus distinct from the generator draft. Nemotron may flag issues if separately authorized, with separate provenance.

Run the final roster verifier against the exact packet version, its blank template,
and the signed-off JSONL. For holdout, only the custodian runs this in the
authorized restricted workspace. Match the packet digest to the approved packet
inventory. The verifier checks completeness and emits counts and digests.
Human identity, independence and adjudication provenance are signed off separately.

```powershell
python -m src.phase2_review verify-final --split development --packet path/to/review.jsonl --template path/to/responses.template.jsonl --responses path/to/final-adjudicated.jsonl
```

The final roster retains the four response fields. Use `ambiguous: false` only
after the issue is resolved. Keep original ambiguity flags, competing readings
and revision history in the adjudication record.
