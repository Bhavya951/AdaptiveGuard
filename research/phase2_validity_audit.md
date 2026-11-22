# Phase 2 development validity audit

## Why A and B returned zero

The unchanged keyword baselines scan for the Phase 1 demo marker
`override-demo-rule`. Phase 1 inserted that artificial cue to test marker
exposure. Phase 2 authors natural-language fictional workflow evidence without
inserting the cue, and its validator explicitly rejects the normalized marker
in dialogue text. The saved 120-example development snapshot has zero marker
hits in final turns, earlier turns, and separate policy strings. Both frozen
keyword rules therefore predict 0 on every example. Their zero F1 reflects the
missing cue. Their zero FPR comes from making no positive predictions.

The original A/B/C development report and predictions are preserved in
`results/private/phase2-development-comparison`.

## Baseline D

D receives the exact same policy string as C and only the final user text.
It case-folds both, recognizes a leading `please`, `could you`, `can you`, or
`would you`, and looks for a leading verb in the remaining request. It skips
recognized negations and text-only directives. It predicts 1 when the policy
includes a restriction cue such as `only` or `must` and contains the verb as a
whole word with an optional `s` or `es` ending. Other inputs return 0 with a
non-execution or unresolved reason. The rule uses no earlier turns, and the
restriction cue and shared verb are sufficient to flag even permitted
instances. D controls for access to policy text, but its lexical decision rule
differs from C's parsing and state reasoning.

## Challenge and results

The challenge contains 18 manually authored examples, with 8 expected
violations and 10 expected negatives across three fictional policy types.
The examples were written separately from the fixture generator, with explicit
provisional labels and rationales. They cover report-first ordering, distractors,
quoted requests and quoted reports, negation, state reversals, indirect
references, paraphrased measurements, and state stated in the final user turn.

| Detector and run | F1 | FPR | Confusion matrix `[[TN, FP], [FN, TP]]` | Unresolved |
| --- | ---: | ---: | --- | ---: |
| C, pre-fix | 0.364 | 0.100 | `[[9, 1], [6, 2]]` | 12 |
| C, post-fix | 1.000 | 0.000 | `[[10, 0], [0, 8]]` | 0 |
| D, both runs | 0.600 | 0.600 | `[[4, 6], [2, 6]]` | 4 |

Pre-fix C treated an archived quotation as live evidence, producing one
false positive. Its six false negatives came from losing state behind an
irrelevant turn, failing to parse a paraphrased state reversal, missing an
indirect cue reference, missing a paraphrased measurement, failing to split a
final-turn user report from its request, and missing a negated arrival
report. Six additional unresolved negatives scored correctly because
unresolved maps to binary 0.

Post-fix C strips quoted evidence, skips irrelevant reports, and treats
explicit corrections as superseding previous state even when the new report
is unresolved. It recognizes the additional request and state phrasings
observed in this challenge. Each challenge ID has a regression assertion.

D's six false positives fall into altered ordering, irrelevant context,
paraphrased measurement, negated arrival evidence, quoted state, and state
reversal. It flags the restricted action in these cases regardless of state.
The two false negatives were the indirect execution request and the final-turn
report followed by a request. Both were unresolved, as were the quoted
caption request and the indirect explanation request. Regression tests record
these expected baseline limitations, and D stayed fixed between runs.

## Reproduction and interpretation

Executed from the repository root, before and after editing C, respectively:

```powershell
python -m src.phase2_validity_audit --output results/private/phase2-validity/pre-fix
python -m src.phase2_validity_audit --output results/private/phase2-validity/post-fix
python -m unittest discover -s tests -p 'test_phase2_validity_audit.py' -v
python -m unittest discover -s tests -p 'test_phase2_detector.py' -v
```

Each audit directory stores the report and exact version of C used. The pre-fix
source SHA-256 matches the source recorded for C in the original comparison.
Both runs use the same challenge, development input, and D source hashes.
Use a fresh output directory for a rerun. Running the audit with the current
detector source produces post-fix results.

The examples diagnose failure modes in three types of fictional rules.
C was revised on these cases, so post-fix agreement establishes regression
coverage on the edited-on challenge. It gives no independent estimate of
generalization. D's FPR depends on its deliberate choice to flag lexical
overlap even when state could permit execution. The difference between C and
D cannot be attributed solely to history access. The challenge labels and
primary dataset labels still need independent review. Holdout evaluation
remains subject to freeze and approval.
