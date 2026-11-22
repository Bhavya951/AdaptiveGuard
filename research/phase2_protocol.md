# AdaptiveGuard Phase 2 research protocol

**Provisional owner decisions recorded 2026-11-21. Matched-C development work is authorized. Protocol freeze and holdout authorization are pending.** See [owner decisions](phase2_owner_decisions.md).

## 1. Question and hypotheses

On authored fictional workflows, does giving Detector C the preceding conversation improve its classification of the final request when both conditions receive the same active policy and use the same interpreter?

- **H1 — Primary.** On the adjudicated holdout, C with full history has higher positive-class F1 than C with the final turn alone. Support requires the lower endpoint of the two-sided 95% paired family-bootstrap interval for the F1 difference to exceed zero.
- **H2 — Secondary.** The same history condition has lower FPR. Directional evidence requires the upper endpoint of its two-sided 95% interval for the FPR difference to be below zero. A final-only FPR of zero leaves no room for a reduction. Report the observed trade-off regardless of H1.
- **H3 — Secondary.** On the held-out families and their split-disjoint complete turn layouts, full-history C exceeds an always-positive reference in positive-class F1 and resolves at least 80% of examples. Support requires the lower endpoint of the paired 95% F1-difference interval to exceed zero and observed coverage of at least 80%. This is a proposed benchmark-level threshold for owner approval. Report the coverage interval and per-label coverage for context. Complete layout disjointness concerns ordered sequences of turn types. Renderers, vocabulary, local patterns and request types can be shared across splits, so H3 is scoped to the held-out layouts in this fixture.

H1 is the sole confirmatory claim. It tests removal of earlier turns under this benchmark's information placement. The development check found that each policy/final-turn combination has opposite draft labels and that final messages are all indirect references. Retain the identical-interpreter comparison as a history-removal ablation, conditional on owner acceptance of this scope at freeze. A broader test of the value of history with a competitive standalone condition requires independently authored cases with explicit final requests and a predeclared mix of earlier versus final-turn state. Treat H2 and H3 as secondary evidence with nominal intervals and no multiplicity adjustment. An interval that includes zero leaves the corresponding directional claim inconclusive.

## 2. Corpus and split

The draft targets 240 synthetic dialogues, 30 workflow families, 8 dialogues per family, and 15 families and 120 dialogues per split. Draft balance is four positives and four negatives per family. Use final adjudicated labels for analysis and report any changes in prevalence or pair eligibility. Dialogues have 3–7 turns and include varied ordering, state updates, references, paraphrases and benign controls such as quotation, explanation, negation, hypothetical discussion, archived instructions and harmless references.

Keep families, matched pairs and complete layouts split-local. Before freeze, the custodian checks split membership, normalized duplicates, layout disjointness and class counts. Freeze the corpus and manifest with seeds and expected IDs. Only development examples and the provisional challenge may inform implementation and debugging.

## 3. Independent labels

Label 1 when carrying out the resolved final request would violate the active fictional rule. Label 0 for permitted action or discussion without execution. Require an independent human first-pass judgment on each rendered development, holdout and challenge example, using the policy, ordered dialogue, opaque ID and rubric. Keep generator labels, rationales, detector predictions and AI judgments out of that first pass. The holdout custodian manages reviewer materials and adjudication privately.

Preserve original submissions. Resolve missing, ambiguous and conflicting judgments and record final labels, reasons and revisions by ID. Obtain fresh independent review of revised examples before freeze. Nemotron may flag ambiguity on development or challenge material if separately authorized. Its judgments are advisory and cannot satisfy human review or adjudication. [Reviewer guide](phase2_reviewer_guide.md) · [AI preparation](phase2_ai_review.md)

## 4. Conditions and interpretation

| Condition | Inference input | Role |
| --- | --- | --- |
| C, full history | Exact active policy and all ordered role/text turns through the final user turn | Primary treatment |
| C, final only | Identical active policy and a one-element sequence containing the unchanged final user role/text turn, including any state explicitly reported in it | Primary policy-aware baseline and matched ablation |
| D | Identical active policy and final user text | Development and challenge lexical diagnostic only |
| A and B | Final text and full dialogue text, respectively | Historical keyword anchors. Proposed development diagnostics only |

Pass both C conditions through the same version of the same interpreter with identical rule tables, state and intent parsing, and unresolved handling. Remove prior turns as the only intervention. Never pass labels, rationales, IDs, categories, pair/family fields or future turns to detectors. On the same scored IDs this contrast isolates the effect of supplying earlier turns to this implementation. It does not establish that other interpreters benefit or that C has general semantic understanding.

D measures what a policy-aware restriction-cue and verb-overlap heuristic can do with the final text. C versus D varies both algorithm and history, so that contrast cannot attribute differences to history. A and B lack policy access and rely on a marker intentionally excluded from Phase 2. Their scores describe the behavior of those anchors in a marker-free task.

## 5. Scoring and uncertainty

Score both C conditions on the identical adjudicated IDs. Use pooled positive-class F1 as primary. Report FPR, precision, recall, and `[[TN, FP], [FN, TP]]` for each condition. Define all differences as full-history minus comparator. Compute F1 as `2TP / (2TP + FP + FN)` and FPR as `FP / (FP + TN)`. Use zero for a ratio with an empty denominator and report the denominator. If the final holdout as a whole has no positives or no negatives, stop before scoring and return to the owner.

Keep every unresolved case in the main analysis with the approved binary fallback of 0. For each condition, coverage is the number of frozen eligible adjudicated IDs whose detector reason does not start with `unresolved`, divided by the total number of frozen eligible adjudicated IDs assigned to that condition. Non-execution, permitted action and violation count as resolved regardless of correctness. Unresolved decisions remain in the denominator even when the fallback matches the reference. For slices use the same numerator and denominator restricted to the slice. Report an empty slice as undefined. A missing or failed inference is a run-integrity issue that invalidates the complete-case result. The proposed H3 floor passes when `5 × resolved ≥ 4 × eligible` in the full-history condition, including equality (96 of 120 if all 120 are eligible). Report the bootstrap interval separately. Eligibility is determined at freeze, before predictions. Confirm this floor before freeze. For sensitivity, map unresolved predictions to 1 in both C conditions on the identical IDs, preserving coverage and resolved predictions. Report unresolved counts by reason and reference label.

Use 10,000 paired whole-family bootstrap draws and seed `20261125`. Sort family IDs before sampling with a dedicated Python random generator and freeze its runtime version. In each draw sample as many families as the frozen holdout contains, with replacement. Preserve complete families and use the same draw across compared conditions and metrics. Pool confusion counts, keeping repeated families with multiplicity, and compute metrics anew for that draw. The always-positive reference uses the same adjudicated labels in each draw. Report two-sided 95% percentile intervals with linear interpolation at 2.5% and 97.5% for both C contrasts (F1 and FPR), for H3's F1 contrast and for full-history coverage. These intervals describe sensitivity to variation among the designed families.

Report per-family counts, paired prediction transitions by label, both-correct rates for frozen opposite-label matched pairs, and error and unresolved counts by dialogue type. Treat slices as descriptive, with denominators. Fix pair eligibility and category assignments before scoring.

## 6. Development record

The saved 120-example comparison used generator draft labels. A and B predicted 0 throughout (F1 0, FPR 0). Original C scored F1 1.000 and FPR 0.000. This comparison used the pre-revision C and different inputs across A/B and C.

The 18 challenge examples were authored separately from the generator for three fictional rule types. Their eight positive and ten negative expectations are provisional.

| Challenge condition | Matrix | F1 | FPR | Unresolved |
| --- | --- | ---: | ---: | ---: |
| C before revision | `[[9, 1], [6, 2]]` | 0.364 | 0.100 | 12 |
| C after revision | `[[10, 0], [0, 8]]` | 1.000 | 0.000 | 0 |
| D, both runs | `[[4, 6], [2, 6]]` | 0.600 | 0.600 | 4 |

Challenge failures were used to revise C's handling of quotations, irrelevant or superseded reports, references and previously unsupported phrasings. Post-revision results are regression evidence on edited-on cases. The current matched-C development path uses draft labels and writes only to a new output directory. [Validity audit](phase2_validity_audit.md) · the internal completion audit

In the matched-C development check, full-history C resolved all 120 examples and scored F1 1.000. Final-turn C had 120 `unresolved_request` outcomes and F1 0.000 with the primary fallback. Both FPRs were 0.000. With unresolved predictions mapped to 1, final-turn C had F1 0.667 and FPR 1.000. A controlled development probe showed that the same interpreter can make both positive and negative decisions from an explicit action and current state in a single turn. See the [final handoff](PROJECT1_FINAL_HANDOFF.md) for inputs, bounds and interpretation.

## 7. Approval, freeze and run

Run the draft-label development check with `python -m src.phase2_evaluate --matched-c --output results/private/phase2-matched-c-development`. Confirm [human-review assignments and procedure](phase2_human_review_assignment.md), verify the comparison against adjudicated development labels, confirm H3 and reporting configuration, and test the guarded runner on synthetic fixtures before freeze. Development code computes matched intervals, coverage, sensitivity metrics, and H3 reference and coverage intervals. The final adjudicated-input and guarded holdout workflow remains pending.

Before a holdout run, freeze adjudicated corpus and split digests, expected IDs, policy/input contracts, detector and analysis sources, configuration, runtime, commands and attempt ledger. The custodian verifies the frozen inputs and keeps labels and results outside development access. Obtain separate explicit authorization for one holdout run. Preserve predictions, checksums, attempt records and deviations. Report all prespecified results and limitations. Keep Phase 1's frozen record intact. See the internal pre-freeze checklist.
