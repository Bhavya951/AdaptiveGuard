# Experiment and validation log

Updated: 2026-11-20

The authorized Phase 1 synthetic held-out evaluation completed once. This log
also records software tests and the original toy smoke check; neither the smoke
check nor unit tests are scientific evidence. No real-world model evaluation
or adversarial robustness experiment has been run.

## 2026-11-20 — baseline test suite

- Command: `python -m unittest discover -s tests -v`
- Environment: Python 3.15.2
- Outcome: 4 tests passed (`test_invalid`, `test_metrics`, `test_predict`,
  `test_run`).
- Artifacts: console output only; no experiment result file was created.

## 2026-11-20 — synthetic baseline smoke check

- Command: `python -m src.baseline`
- Input: the four hard-coded examples in `src/baseline.py`; no external data.
- Output: TP=2, FP=0, FN=0, TN=2; precision=1.0, recall=1.0, F1=1.0.
- Interpretation: verifies that the toy keyword rule matches these four
  constructed examples. It does not evaluate conversation-level detection,
  generalization, or real-world safety.
- Reproducibility limits: no separate raw prediction log, dataset split, or
  random seed; there is no approved experiment configuration.
- Artifacts: console output only.

## External review

Nemotron was not called. No request or output exists to record.

A subsequent approved reviewer run is recorded in [progress.md](progress.md).
It was a review of the draft protocol. No scientific experiment was run.

## 2026-11-20 Phase 1 development check

- Python 3.15.2. `python -m unittest discover -s tests -v` passed 11 tests.
- `python -m src.evaluate --output results/private/phase1-development` validated
  192 records and scored 96 development dialogues in 12 families.
- Full fixture SHA-256 is
  `ba230180a938025d06790a077fca7e52f1edfaa84c7e9f97aa01987dc777eafa`.
  The report retains the family manifest, source hashes and seeds.
- Development marker counts were 35 historical and 14 final, including 15
  negative examples with historical-only markers. Counts can overlap.
- Confusion matrix rows are gold negative and gold positive, and columns are
  predicted negative and predicted positive.

| Condition | Confusion matrix | Precision | Recall | FPR | F1 |
|---|---|---:|---:|---:|---:|
| Final message | [[39, 9], [43, 5]] | 0.3571 | 0.1042 | 0.1875 | 0.1613 |
| Full history | [[24, 24], [27, 21]] | 0.4667 | 0.4375 | 0.5000 | 0.4516 |

Development ΔF1 was +0.2903, with a 95% paired family bootstrap interval of
[0.1682, 0.4317] from 10,000 draws. The history rule recovered 16 positives and
added 15 false alarms. The rerun reproduced fixture and prediction bytes and
all report fields except the output path. These development metrics do not
evaluate the held-out hypothesis. No holdout predictions or metrics were generated.

## 2026-11-20 held-out preflight

The user authorized one held-out run using the frozen protocol and prohibited
dataset regeneration. The three evaluator source hashes and the saved
development fixture hash matched the development report. The Python version,
fixture version, split seed, marker seed, bootstrap seed, draw count, and the
family manifest derived from the frozen family list matched the recorded
configuration. No dialogue records were regenerated.

The Phase 1 runner exported only the 96 development dialogues. The workspace
contains a recorded SHA-256 for the full 192-dialogue corpus, but no saved
full-corpus or holdout fixture snapshot. Consequently the full-corpus digest
could not be verified from existing fixture bytes. The run stopped at preflight.
Zero holdout predictions, metrics, or result artifacts were created. The
held-out hypothesis remains untested.

## 2026-11-20 authorized holdout

The user authorized deterministic in-memory reconstruction. The full canonical
hash, saved development bytes, split manifest, Python version, source hashes
and seeds passed preflight. Saved the full corpus and manifest as read-only
local files. Manifest SHA-256:
`af0a22d623d1b81679a7939063e8ad7958e6f632d67968df167abe0b21f26824`.

Ran the frozen detector and summary functions once on 96 holdout dialogues.
Saved paired predictions, metrics, transitions, configuration and hashes to
`results/private/phase1-holdout`. Verified the saved prediction count, the raw
prediction and snapshot manifest hashes, and the single start/completion in
the run log without scoring again. Holdout ΔF1 +0.1853 [0.0892, 0.2985].
See the [Phase 1 research report](../research/protocol.md) for all metrics,
development comparison and limitations. Human review is pending.

## 2026-11-20 independent holdout artifact audit

This coordinator audit read the saved artifacts and independently recomputed
the confusion counts, precision, recall, FPR, F1, paired transitions, point
ΔF1, and family-bootstrap interval from the saved 96 prediction rows. It did
not regenerate fixtures, invoke the evaluator, score the holdout again, or
write to frozen artifacts.

| Condition | TN / FP / FN / TP | Precision | Recall | FPR | F1 |
|---|---:|---:|---:|---:|---:|
| Final message | 31 / 17 / 39 / 9 | 0.3461538462 | 0.1875 | 0.3541666667 | 0.2432432432 |
| Full history | 19 / 29 / 27 / 21 | 0.42 | 0.4375 | 0.6041666667 | 0.4285714286 |

Paired transitions, final → history:

| Gold label | 0→0 | 0→1 | 1→0 | 1→1 |
|---|---:|---:|---:|---:|
| Negative (0) | 19 | 12 | 0 | 17 |
| Positive (1) | 27 | 12 | 0 | 9 |

Recomputed ΔF1: `0.1853281853281853`. Recomputed 95% percentile interval:
`[0.08922397047397046, 0.29852770358089487]`, using 10,000 paired draws of
12 whole families with replacement, seed `20261121`, and linear interpolation.
Both match the saved report. The run log contains one evaluation start and one
completion, and the report records attempt 1.

SHA-256 comparisons all matched:

- Holdout report to run-log digest:
  `0b3066fe8c784b4d05d5d9e85d2b3269d661925b1204c00d75c2838cf4394b99`
- Raw predictions:
  `7ba6e52ae0a44217d152eadd45a7c95b570fb74071df0e6ee3c818db83a3c53c`
- Frozen manifest:
  `af0a22d623d1b81679a7939063e8ad7958e6f632d67968df167abe0b21f26824`
- Frozen corpus:
  `ba230180a938025d06790a077fca7e52f1edfaa84c7e9f97aa01987dc777eafa`
- Development fixture:
  `6803f63e26646d942163c0ec22df00687c1ffa5561bafe9c760e3f298a584b2a`
- Recorded source hashes for `baseline.py`, `fixtures.py`, and `evaluate.py`
  also match the current files.

The full test suite was run once during this audit:
`python -m unittest discover -s tests -v` — 15 passed on Python 3.15.2.
This is software validation, not a new experiment.

Interpretation remains limited to the seeded synthetic corpus. The higher F1
co-occurs with higher FPR; no claim of semantic context understanding or
adversarial robustness follows.
