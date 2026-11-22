# Implementation walkthrough

## Repository map

| Path | Responsibility |
| --- | --- |
| src/baseline.py and src/evaluate.py | Literal marker and Phase 1 development scoring |
| src/fixtures.py | Phase 1 authored workflow grammar, pair construction and validation |
| src/exploratory.py | Phase 1 policy-aware development comparison |
| src/phase2.py and src/phase2_workflows.py | Phase 2 authored workflows, turn layouts, validation and blinded export |
| src/phase2_detector.py and src/phase2_final_policy.py | Context interpreter C and final-turn heuristic D |
| src/phase2_evaluate.py, src/phase2_analysis.py and src/phase2_identifiability.py | Comparison, paired intervals, coverage, ambiguity bounds and placement probes |
| src/phase2_review.py and nemotron_review.py | Rubric exports, response audits, final roster checks and optional AI review tooling |
| src/phase2_validity_audit.py | Provisional development challenge scoring |
| data/, evidence/, research/, tests/ | Development rows, historical aggregate outputs, study records and software checks |

## From text to decision

An evaluation row is one JSON object per line with IDs for case, family, pair and split, a policy string, ordered role/text pairs, a binary label and an authored rationale. Phase 2 adds a control tag. The evaluation row is richer than the inference input. C's detect(policy, messages) accepts a policy and role/text pairs ending with a user message. It returns a Decision with numeric prediction, reason and optional action, selected rule, evidence turn and evidence text. The review export uses an opaque ID, policy and role/text objects.

In Phase 1, predict lowercases text and searches for the marker. predict_messages calls it on the final message and across the dialogue, yielding the final and OR decisions. The OR rule can only add positives. An unrelated marker in an earlier note can therefore flip a benign final request. The separate exploratory context_rule reads the policy and infers state using the simple Phase 1 grammar.

C normalizes the final text, detects an explicitly embedded user report when present, and calls resolve_request. request distinguishes directives, discussion and references. With a reference such as “Please go ahead with that,” the resolver can use a prior user turn that names the task. Discussion, including recognized quotation or negation, produces a non-execution reason. Unresolved intent produces an unresolved_request reason.

The interpreter matches action and policy patterns in RULES. It expects exactly one applicable rule. current_evidence looks for relevant reports, handling explicit updates and earlier archived text. condition evaluates the rule's corresponding state check, such as occupancy, a measurement threshold or a declared category. With a limit of 6 and a report of 7, the action violates the fictional rule. A reading of 4 permits it. An otherwise explicit request with the report removed produces unresolved_state. D's final_policy_baseline uses policy cues and lexical overlap with the last request.

## Construction, evaluation and review

Phase 1 pairs reuse final wording and vary state or intent. Seeded marker insertion adds superficial noise. Phase 2 renders policy, named action and state from workflows, chooses split-local layouts, and pairs positive requests with permitted actions or benign text tasks. records emits deterministic fixtures and validate checks schema, split membership, duplicates and pair balance. The public structural substitutes exercise the held-out branch of the validators.

Phase 1 development_predictions scores development rows and summarize pools case counts by family. Phase 2 compare gives the historical A/B/C/D comparison. compare_matched_c runs C twice with identical policy and changes only the turns supplied. The evaluator records predictions, metrics and source and fixture digests. input_identifiability groups identical inputs and calculates empirical ceilings from the labels in each group. placement_probe independently varies which turn contains evidence, the policy threshold and the state.

phase2_review.prepare exports blinded packets. validate_packet checks schema and matching IDs, audit_responses summarizes parsing failures and disagreements, adjudicate supports review triage, and verify_final_roster verifies the final response set before returning counts and digests. These checks require human assignment and provenance to establish reviewer independence. The optional Nemotron connector can stage development or challenge requests locally for advisory review. Offline tests and evaluation bypass the external connector.

## Metrics and interpretation

- Precision = TP / (TP + FP), the fraction of flagged cases actually positive.
- Recall = TP / (TP + FN), the fraction of positives flagged.
- FPR = FP / (FP + TN), the fraction of negatives flagged.
- Positive-class F1 = 2TP / (2TP + FP + FN), the harmonic mean of precision and recall.
- Coverage is the resolved share. Mapping an unresolved outcome to 0 or 1 changes the confusion matrix, so the reason counts and both fallback calculations matter.

The paired bootstrap resamples complete families together, pools the confusion counts for each comparison arm and calculates a metric difference for each draw. The middle 95% of these draws gives the percentile interval. This preserves repeated examples and pairing. The interval samples from the available families, with their common templates and fixed marker realization. Phase 2's uniform profiles give a degenerate interval.

Phase 1 gained 12 hits on positives and 12 on negatives with history. In Phase 2, deliberately indirect final texts remove the referent from every final-only input. Identical policy/final inputs represent both labels, placing a ceiling on the standalone condition. Explicit final reports in the probe show the interpreter can work on self-contained input. The challenge informed revisions, so its post-fix outcomes describe regressions. More independently authored self-contained requests, different grammars and independent label review would test which conclusions transfer.
