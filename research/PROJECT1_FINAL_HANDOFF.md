# AdaptiveGuard Project 1 final handoff

**2026-11-21 · Engineering preparation provisionally complete. Phase 2 scientific validation and protocol freeze are pending.**

## Verified evidence

Phase 1 completed one authorized, frozen synthetic holdout evaluation. Full-history keyword F1 was 0.4286 versus 0.2432 for the final-message rule. The paired difference was +0.1853 with a 95% interval of [0.0892, 0.2985]. FPR rose from 0.3542 to 0.6042, adding 12 true and 12 false positives. Recomputed the metrics and interval from saved predictions and verified the recorded frozen corpus, manifest, predictions, report, development fixture and source digests. Label independence and owner sign-off remain pending. [Phase 1 report](phase1_report.md)

Phase 2's original 120-example draft-label comparison had F1 0 for the marker-only A and B and F1 1.000 for original C. On the 18 authored challenge cases, C changed from F1 0.364, FPR 0.100 and 12 unresolved to F1 1.000, FPR 0 and zero unresolved. D remained at F1 0.600, FPR 0.600 and four unresolved. These challenge failures were used to revise C. The challenge is a regression set with provisional expectations. [Development validity audit](phase2_validity_audit.md)

## Matched-C diagnosis

All 120 final-turn outcomes were `unresolved_request`, split evenly by draft label. All four final-message templates are indirect references to an earlier task. C searches earlier user turns for the referent. Even an explicit action needs current state, which C can obtain from an earlier assistant report or a supported report in the final user message. The unchanged active policy gives the constraint rather than the current state or whether the user requested execution. Both matched conditions receive identical policy strings and use the same interpreter.

Grouping actual development examples by the exact supplied policy and final role/text yields 60 input groups, each with opposite draft labels. Every deterministic final-input-only classifier must issue the same prediction within each group. Its empirical accuracy ceiling on these labels is 0.500 and its positive-class F1 ceiling is 0.667, achieved by predicting positive throughout. This is a dataset diagnostic computed with draft labels. It is neither an attainable accuracy guarantee on new cases nor an independent test result.

| Matched-C development condition | Resolved | F1 | FPR | F1 / FPR, mapping unresolved to 1 |
| --- | ---: | ---: | ---: | ---: |
| Full history | 120 / 120 | 1.000 | 0.000 | 1.000 / 0.000 |
| Final turn | 0 / 120 | 0.000 | 0.000 | 0.667 / 1.000 |

With 10,000 paired family draws and seed `20261125`, ΔF1 is +1.000 [1.000, 1.000] and ΔFPR is 0.000 [0.000, 0.000]. Full-history coverage is 1.000 [1.000, 1.000]. F1 versus always-positive differs by +0.333 [0.333, 0.333]. The zero-width intervals reflect uniform family count profiles in this authored sample. Unresolved prevalence and fallback policy materially change the final-turn scores.

## Functional comparison and interpretation

Added a deterministic six-case development probe crossing policy thresholds 6 and 8 with state readings 4, 7 and 9. For the same policy, action and state, C resolved all six and matched all authored expectations both when the report appeared in an earlier turn supplied to C and when it appeared explicitly inside the final turn. With the earlier report withheld from an otherwise explicit request, all six outcomes were `unresolved_state`. At reading 7, changing only the policy threshold changed the decision. On the same self-contained final messages, D returned 0 throughout. When given just the explicit directive, D returned 1 throughout. D's lexical cues and handling of report-prefixed directives explain this contrast in the probe. Two identical C conditions isolate the available evidence, the threshold test varies policy, and C versus D on the exact same inputs varies the algorithm. The probe uses one familiar rule and interpreter-supported surface forms. Its outcomes establish a functional path and regressions, with authored expectations.

**H1 remains testable as a narrow history-removal ablation.** The proposed holdout estimand is the effect of supplying earlier turns on C in this deliberately reference-dependent fixture. A winning result would support that claim. A broader, competitive final-turn test needs independently authored examples with explicit final tasks and enough current evidence in some final turns, alongside cases with earlier evidence or referents. Predeclare the strata and retain all conditions and rates. The existing holdout is preserved. [Protocol and scoring rules](phase2_protocol.md) · [Owner decisions](phase2_owner_decisions.md)

H3 is separate. The provisional coverage rule counts all frozen eligible cases and passes at `5 × resolved ≥ 4 × eligible` for full-history C. It additionally requires a positive lower 95% paired F1-difference bound versus always-positive. This remains a proposed freeze setting. A and B are historical diagnostics and D remains diagnostic only.

## Reviewer and holdout status

Regenerated and verified the saved development and challenge packets and blank templates byte-for-byte. The packets contain one opaque ID, fictional policy and ordered dialogue per case. Existing holdout packets remain with the protected workflow. Added a final-roster validator that verifies the complete, unique packet ID set, binary decisions, rationales and resolved ambiguity, and emits only counts and digests. Human provenance still requires actual signatures and assignment. No human judgments or adjudicated labels were created, and no Nemotron requests were made. [Assignments and commands](phase2_human_review_assignment.md)

**Phase 2 holdout status:** no holdout label or prediction inspection, detector inference, bootstrap, or evaluation in this pass. No protected holdout files opened or modified. Split metadata checks confirmed disjoint family membership and complete layouts. Unit tests use generated fixtures for structural checks. The existing evaluation entry points remain development-only.

## Verification and reproduction

Python 3.15.2 on Windows. `python -B -m unittest discover -s tests -v` passed 64 tests. `python -B verify_clean.py` passed 64 tests from an isolated source copy and fresh virtual environment. Hosted CI remains unverified because the local workspace has no Git metadata or hosted run evidence.

```powershell
python -B -m src.phase2_identifiability
python -B -m src.phase2_evaluate --matched-c --output results/private/phase2-matched-c-inspection
python -B verify_clean.py
```

Use a new output directory. Two temporary matched-C runs produced equal prediction bytes and reports apart from the recorded output destination. Verified their source and development fixture hashes, confirmed saved fixture bytes matched deterministic regeneration, and checked the interval and coverage outputs. XSTest and MS-XSB were checked against their primary records. Both concern refusal behavior and serve as design precedents. The reports make no novelty or deployment claim. [XSTest](https://aclanthology.org/2024.naacl-long.301/) · [MS-XSB](https://arxiv.org/html/2510.08158v3)

## Before scientific closeout

1. Assign independent reviewers, an adjudicator and a holdout custodian. Confirm the number of first passes, complete review, adjudicate and record private provenance and digests.
2. Obtain owner acceptance of the narrow primary estimand and exact H3 criterion. Verify matched C on adjudicated development labels and finalize the runner and analysis against synthetic fixtures.
3. Freeze adjudicated corpus, IDs, eligibility, sources, commands, environment, configuration and attempt ledger. Obtain explicit separate authorization for the custodian to run the Phase 2 holdout once.
4. Report the authorized results and deviations in the [Phase 2 report template](phase2_final_report_template.md). Phase 1 owner sign-off and external-sharing approval remain separate.

## Files changed in this pass

- Code: `src/phase2_analysis.py`, `src/phase2_evaluate.py`, `src/phase2_identifiability.py`, `src/phase2_review.py`.
- Tests: `tests/test_phase2_detector.py`, `tests/test_phase2_identifiability.py`, `tests/test_phase2_review_preparation.py`.
- Documentation: `README.md`, `notes/progress.md`, `research/phase2_ai_review.md`, `research/phase2_final_report_template.md`, `research/phase2_human_review_assignment.md`, `research/phase2_owner_decisions.md`, `research/phase2_protocol.md`, and this handoff.
- Removed: `prompts/CODEX.md`, `prompts/VSCODE_AGENT.md`. Both were manual kickoff prompts with no runtime or reproduction role. The agent contract, active Nemotron prompt, research records and frozen artifacts were preserved.
