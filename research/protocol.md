# Research protocol — Phase 1 implementation approved

## Question and scope

Compare single-message and conversation-level safety detection on benign synthetic conversations. The unit is one final user turn in a complete dialogue prefix. The label is whether fulfilling that turn would cross a fictional workflow rule. All cases concern local, invented activities such as sorting game cards or changing a mock catalog. See [the source verification ledger](notebook.md) for the design rationale.

## Proposed hypothesis

On held-out synthetic template families, scanning the conversation through the final turn will yield higher positive-class F1 than scanning the final turn alone. The proposed criterion for directional support is a paired 95% interval for ΔF1 entirely above zero. An interval spanning zero is inconclusive. An interval entirely below zero supports the opposite direction.

The history rule can recover missed positives and can also add false alarms. Because it preserves every final-turn hit, it cannot reduce the false-positive rate on the same negatives. The direction of ΔF1 depends on the balance of additional hits across labels. The study estimates that trade-off for the specified fixture collection.

## Proposed dataset and labeling

- Create 24 original template families with 8 dialogues each, for 192 dialogues. A family groups dialogues sharing a scenario, policy and underlying dialogue template. Each prefix has 3–5 messages, ending with the user turn being scored. Store fictional workflow rules separately in the policy field for labeling. The detector receives dialogue text only. Check that the marker is absent from policies and shared dialogue scaffolding. Use only invented domains, entities and records.
- Each family contains two pairs with identical final turns and opposite gold labels, one pair with two positive labels, and one pair with two negative labels. Same-label pairs also share final wording within the pair and vary harmless history. Include benign historical mentions of the demo marker and implicit rule-crossing requests. Leave marker frequencies independent of label quotas and record marker location as a diagnostic.
- Label 1 when carrying out the resolved final request would perform an action currently prohibited by the fictional rule. Label 0 for a permitted action, an explanation, or a mention without a request to perform a prohibited action. A reviewer reads the ordered dialogue and rule, records a short rationale and resolves ambiguity before freeze. Keep detector predictions out of fixture authoring and label review. Resolve unresolved cases by revising or replacing them before freeze and record the change.
- Proposed UTF-8 JSONL schema uses `id`, `family_id`, `pair_id`, `split`, ordered `messages` as role/text pairs, a separate `policy`, `label`, and `label_rationale`. Only message text is visible to the keyword detector. Freeze labels and the sorted family manifest before splitting. Shuffle sorted family IDs with Python's `random.Random(20261120)`, before scoring, and assign the first 12 families to development and the last 12 to held-out evaluation. Publish the resulting manifest internally with the fixture version. Keep family and pair members together. Check normalized duplicate dialogues and shared template ancestry across splits. Resolve any leakage before freeze and log the resolution.
- Use development examples for schema and evaluator checks. Freeze and hash the fixture, split and evaluator configuration before scoring the holdout. Existing four baseline examples stay in smoke tests.

## Proposed baseline comparison

| Condition | Input and prediction |
|---|---|
| Single message | Apply the existing case-insensitive substring rule in `src/baseline.py` to the final user message. |
| Conversation history | Apply the same rule separately to every message up to and including the final user message, then predict positive if any message matches. |

Both conditions score the same held-out IDs and labels. The history condition receives prior dialogue text and the final turn. Policy text is excluded from both inputs. Neither condition reads metadata, labels, rationales, later messages or predictions from other examples. The OR baseline tests additional lexical evidence. It has no mechanism for interpreting intent or policy state.

## Proposed analysis and execution

1. After approval, author and review fixtures, implement the small evaluator and test pair alignment, split isolation, metric edge cases and OR monotonicity. Review and freeze artifacts before approval to run the holdout.
2. Calculate positive-class F1 from pooled held-out counts using `2TP / (2TP + FP + FN)`, with zero for an empty denominator. The primary outcome is conversation-history F1 minus single-message F1. Record both F1 scores, confusion counts, precision, recall, false-positive rate, and positive flips broken down by gold label. Report outcomes for the matched opposite-label pairs and benign historical marker negatives as diagnostics.
3. Compute a descriptive paired percentile interval for ΔF1 with 10,000 draws, seed 20261121. For each draw, sample 12 held-out families with replacement and include all 8 examples and both conditions per selected family, counting repeated families with multiplicity. Take the 2.5th and 97.5th percentiles of the resulting deltas using linear interpolation. Treat the interval as sensitivity to the chosen families, given the small, designed collection. Report per-family counts and describe design prevalence, marker placement, and limits on generalization.
4. Save the fixture hash, manifest, evaluator version or source hash, Python version, command, seeds, paired per-example predictions, summary metrics, and error analysis. Record any deviations before interpretation. Run locally. Literature benchmarks supply design references only.

## Approval requested

- [x] Approve the directional hypothesis, primary ΔF1 outcome and interval interpretation.
- [x] Approve the fictional policy rubric, 192-dialogue specification, authoring and review process, and family-level split.
- [x] Approve the two fixed keyword baselines and bounded evaluator implementation.
- [x] Approve the held-out run after the fixtures, evaluator checks and configuration are ready.

## Phase 1 implementation record

Version `phase1-v1` has 24 separately authored fictional workflows with four
matched pairs per family. All use a common three-message grammar. The split
holds out workflow families and their pairs. It does not test new dialogue
grammars. Labels come from the authored workflow state and request type. Code
validates both fields against the rubric and requires a rationale. Independent
human review of rendered labels remains pending.

Marker placement uses seed 20261122. A final reference tag is sampled once per
pair with probability 0.25 and a historical archived-note mention once per
dialogue with probability 0.35. Both draws are independent of label and use a
separate stream from the split. The same keyword detects both placements. This
design tests sensitivity to additional lexical evidence. Chance marker placement
and the increased exposure with history can raise F1 without evidence of
semantic reasoning. The development interval is descriptive for these families.

Corpus validation checks policy and scaffolding marker absence, policy separation,
label consistency, pair composition, normalized duplicate dialogue text, seed
regeneration and family split membership. Holdout validation checks raw marker
coverage without reporting holdout prevalence cross-tabs or scoring its rows.
Only development rows are exported and scored by the CLI.

## Initial held-out preflight

The run was authorized, but preflight stopped because the full frozen corpus
was recorded by hash and only the development snapshot was persisted. The
development snapshot and evaluator source hashes matched. The holdout has zero
runs, and the directional hypothesis remains untested. See the
[experiment log](../notes/experiment_log.md) for the verification details.

## Verified held-out run

The authorized reconstruction matched the prior full-corpus SHA-256
`ba230180a938025d06790a077fca7e52f1edfaa84c7e9f97aa01987dc777eafa`.
Development records matched byte-for-byte. The 12 development and 12 holdout
families matched the frozen split. Source hashes, Python version and seeds
matched. The corpus and manifest were saved with local read-only flags before
scoring. Their recorded hashes make subsequent changes detectable.

| Split | Condition | Confusion matrix (TN, FP / FN, TP) | Precision | Recall | FPR | F1 |
|---|---|---|---:|---:|---:|---:|
| Development | Final | 39, 9 / 43, 5 | .3571 | .1042 | .1875 | .1613 |
| Development | History | 24, 24 / 27, 21 | .4667 | .4375 | .5000 | .4516 |
| Holdout | Final | 31, 17 / 39, 9 | .3462 | .1875 | .3542 | .2432 |
| Holdout | History | 19, 29 / 27, 21 | .4200 | .4375 | .6042 | .4286 |

Development ΔF1 was +0.2903 [0.1682, 0.4317]. Holdout ΔF1 was +0.1853
[0.0892, 0.2985]. Both intervals use 10,000 paired whole-family draws. The
holdout interval is entirely above zero and meets the protocol's criterion for
directional support on these fixtures.

On holdout, 12 of 48 positives flipped from missed to detected and 12 of 48
negatives flipped from correct to false positive. The remaining 27 positives
stayed missed and 9 stayed detected. The remaining 19 negatives stayed correct
and 17 stayed false positives. No predictions flipped from positive to negative.
Among the 48 dialogues in opposite-label pairs, errors rose from 24 to 26.
History produced the same recall on both splits, with higher holdout FPR.
The final-turn detector flagged 26 holdout dialogues versus 14 on development.
This stronger final-turn baseline and the history false alarms contributed to
the smaller holdout F1 gain.

The fixed detector only responds to marker exposure. Tags were placed
independently of gold labels, so scanning extra messages creates additional
opportunities for both true and false hits. The families share a three-message
grammar. A bootstrap over 12 designed holdout families describes sensitivity
to those families and provides no estimate of deployed safety performance.

Local artifacts are under `results/private/phase1-frozen-corpus` and
`results/private/phase1-holdout`. The latter contains the raw paired predictions,
configuration, report and run log. Exactly one holdout run completed.
