# Phase 2 Detector C and development comparison

## Inference contract

`src.phase2_detector.detect(policy, messages)` takes one string containing the
active fictional policy and an ordered tuple of `(role, text)` turns ending
with the target user request. It receives no other fields. The evaluator
passes the policy and dialogue explicitly and uses fixture metadata only for
split checks, scoring and error reporting. Detector C imports no generator or
fixture modules.

The final-message baseline scans only the last user message for the fixed
Phase 1 marker. The full-history baseline applies the same substring rule
over all messages. Detector C receives the policy text because it needs the
external workflow constraint to decide whether execution is permitted. This
gives C information the unchanged baselines do not receive and prevents
attributing the difference solely to use of message history.

Detector C resolves a direct request or a reference with a unique prior task.
It recognizes negated requests, quotations and text deliverables as
non-execution. It uses the latest assistant report, skipping recognized
archival reports and acknowledgments. It selects an applicable constraint
from the policy and evaluates it on values extracted from the request and
report. Constraint operations include numeric thresholds, relative
measurements, equality, majority votes and sequence reversal. The decision
records a binary prediction, a reason, and, when available, the resolved
action, rule type and one-based evidence turn.

For binary scoring, an unresolved request, unsupported policy/action, or
unknown state returns 0 with a separate unresolved reason. This fallback can
miss violations. It is a scoring choice and does not establish that execution
is permitted.

## Development results

The saved development snapshot contains 120 examples from 15 families.
References are generator draft labels, with independent review pending.
All three detectors scored the same IDs. Confusion matrices use rows for
actual classes and columns for predictions, ordered 0 then 1.

| Detector | Precision | Recall | F1 | False-positive rate | Confusion matrix |
| --- | ---: | ---: | ---: | ---: | --- |
| A, final-message keyword | 0.000 | 0.000 | 0.000 | 0.000 | [[60, 0], [60, 0]] |
| B, full-history keyword | 0.000 | 0.000 | 0.000 | 0.000 | [[60, 0], [60, 0]] |
| C, context-aware rules | 1.000 | 1.000 | 1.000 | 0.000 | [[60, 0], [0, 60]] |

Each keyword baseline missed 24 execution requests with a single state report
and 36 execution requests with updated state. They made no positive
predictions because the fixtures exclude their marker. Precision is reported
as 0 when there are no positive predictions. Detector C made no errors against
the draft labels. Its decisions were 60 violations, 30 permitted requests,
and 30 non-execution cases. It classified both members correctly in all 60
matched pairs. A and B classified both members correctly in zero pairs.

## Limitations and reproduction

The policy grammar, action patterns and evidence parsers were written for
visible development wording and policy types. They do not read the generator's
hidden state or exact blocking/permitted fixture strings. They encode the
same underlying fictional constraints and rely on restricted report
phrasing. Request resolution has limited paraphrase and reference coverage,
and the latest-report rule assumes one active task with consolidated evidence.
Results measure agreement on the development fixtures using draft labels.
They provide no estimate of performance on unseen workflows or evidence of a
lower false-positive rate than B. The comparison also favors C through its
additional input and through the absence of the baseline marker.

From the repository root, use a new output directory for a rerun.

```powershell
python -m unittest discover -s tests -p test_phase2_detector.py -v
python -m src.phase2_evaluate --output results/private/phase2-development-comparison
```

The command reads the fixed saved development fixture and stores
`report.json` and `predictions.json` with development metrics, decision traces,
input and source hashes, and Python version. The holdout was left unopened
and unscored. The scoped test run avoids corpus-wide tests that generate
holdout examples.
