# Exploratory context rule

This follow-up uses the 96 saved Phase 1 development dialogues from 12 families.
Both rules score the same fixture IDs with the same original labels and confusion
matrix formulas. The full-history keyword predictions matched the saved Phase 1
development predictions exactly.

The context rule parses the fictional policy for its blocked action and state.
It reads the state from the preceding assistant message and flags execution
requests only when that state applies. Indirect requests must refer to the policy
action in the opening message. Explanation requests do not trigger the rule.
Reference tags are ignored when parsing intent.

The context rule has access to the fictional policy. The frozen keyword detector
retains its original dialogue-only input. Neither rule receives the gold label
or rationale when predicting. This comparison measures a handcrafted policy-aware
rule against the existing baseline, with different input information.

| Rule | TN / FP / FN / TP | Precision | Recall | F1 | False-positive rate |
|---|---:|---:|---:|---:|---:|
| Full-history keyword | 24 / 24 / 27 / 21 | 0.4667 | 0.4375 | 0.4516 | 0.5000 |
| Context-aware | 48 / 0 / 0 / 48 | 1.0000 | 1.0000 | 1.0000 | 0.0000 |

Both rules were correct on 45 dialogues. The keyword rule alone was wrong on 51
(24 false positives and 27 false negatives). The context rule alone was wrong on
zero, and both rules were wrong on zero.

The context rule closely mirrors the labeling rubric and was written for the
development fixture grammar. Its perfect agreement checks that grammar and
rubric on this split. Generalization to other wording or workflows is untested.
The implementation raises an error for unsupported request forms. This was an
exploratory development run, with no held-out evaluation.

## Reproduce

```bash
python -m unittest discover -s tests -v
python -m src.exploratory --output results/private/exploratory-development-rerun
```

Use a new output directory. The original exploratory report and paired
predictions are in `results/private/exploratory-development`.
