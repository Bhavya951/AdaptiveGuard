# Interview preparation

## 30-second introduction

AdaptiveGuard is an offline Python study of how earlier conversation affects a rule-based safety decision in fictional workflows. A keyword baseline gained F1 on a frozen synthetic holdout but also produced more false positives. A second phase compares the same policy interpreter with and without earlier turns. Its development results illustrate what happens when the final turn omits necessary evidence. Independent labels and the Phase 2 holdout evaluation are pending.

## Two-minute explanation

- **0:00–0:30** Define the positive label. The user asks for something that would break an active fictional rule if carried out. The dataset contains authored conversations grouped by family, with matched wording and variations in state or intent.
- **0:30–1:00** Explain A and B. A searches the last message for a literal marker, and B searches all turns. On the single frozen Phase 1 run, F1 rose from 0.2432 to 0.4286 and FPR rose from 0.3542 to 0.6042. History added equal numbers of true and false positives.
- **1:00–1:30** Explain C's ablation. Both arms use the same interpreter and policy. C recovers the task and state from history. The development final turns are all indirect, so the final-only arm resolves none. Changing the unresolved fallback radically changes the reported metrics.
- **1:30–2:00** Explain the remaining research. The challenge informed fixes, draft labels follow generator rules, and the Phase 2 protected split is unevaluated. A broader comparison needs independently authored examples with mixed history requirements and independently adjudicated labels.

## Technical questions and answers

1. **What is classified?** The action requested by the last user turn under the active fictional rule.
2. **Why use synthetic examples?** They provide control over wording, intent, state, and policy and support deterministic reconstruction of development evidence.
3. **What do A and B measure?** Final-turn marker detection and monotonic OR detection over the entire dialogue.
4. **Could B reduce false positives under the same marker rule?** On the same examples, adding search scope can only preserve or add positive predictions.
5. **What changed in Phase 1?** Recall increased from 0.1875 to 0.4375, and false-positive rate increased by 0.25.
6. **Why report precision and recall?** They show how often alerts are correct and how many positive cases the detector catches.
7. **What is FPR's denominator?** All truly negative cases. The fraction of alerts that are false uses a different denominator.
8. **What is F1?** The harmonic mean of precision and recall for the positive class.
9. **Why pair the predictions?** Both conditions see the same cases, so preserving their joint outcomes measures their difference directly.
10. **Why bootstrap families?** Examples in one family share a workflow and templates, so resampling independent rows can overstate precision.
11. **Does the Phase 1 interval establish statistical significance?** Its positive lower bound supports the directional comparison under the specified family-resampling analysis for this fixture. Population-level and real-world inference require stronger sampling assumptions.
12. **What does C parse?** Intent, action or referent, applicability of a policy pattern, and current matching evidence.
13. **What makes matched C an ablation?** The available earlier turns are removed while the policy, code and evaluated examples stay fixed.
14. **What does D add?** A diagnostic lexical baseline with policy access. Its contrast with full C also changes the algorithm.
15. **What is the always-positive reference on balanced data?** Precision 0.5, recall 1, F1 0.667 and FPR 1.
16. **Why can a final-only classifier reach at most 0.500 accuracy on Phase 2 development?** Every exact policy and final-turn group contains both labels, so a deterministic prediction can match only one in each pair.
17. **Why does coverage matter?** A numeric 0 may mean permission or a failure to resolve. In the final-only C run all cases were unresolved.
18. **Why are some intervals zero-width?** Each family has the same relevant count profile, so the metric is invariant to which families are resampled.
19. **How did you control leakage?** Families and pairs stay within their splits, predictor inputs exclude annotation metadata, and only development and challenge cases inform code changes. Common grammar and authored rubric still constrain independence.
20. **What did the challenge show?** The original C struggled with authored edge cases. The same cases verified the fixes and remain regression evidence.
21. **What were the negative findings?** History raised Phase 1 false alarms, both Phase 2 marker baselines missed all positives, final-only C had zero coverage, and D had high challenge FPR.
22. **Has Phase 2 been independently validated?** The holdout remains unevaluated. Review, adjudication, freeze and separate run authorization remain pending.
23. **How was AI used?** Copilot SDK and Codex assisted with setup, research drafts, implementation and checks. Nemotron reviewed a draft protocol. The AI log records the contribution and verification status.
24. **What should you verify personally before presenting?** Trace a positive and an unresolved result in code, recompute one metric from counts, check the source papers, explain the split and provenance, and describe which work you actually performed or reviewed.
25. **What would you test next?** Independently authored examples with mixed self-contained and reference-dependent turns, label disagreements adjudicated before freeze, and predeclared reporting for each stratum.
