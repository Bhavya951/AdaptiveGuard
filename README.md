# AdaptiveGuard

AdaptiveGuard studies whether earlier dialogue turns improve classification of the final request under a fictional workflow policy. A positive prediction means that carrying out the request would violate the rule. All scenarios use invented settings, such as a paper-token shelf or a cloth snail.

## Research design

Phase 1 tested whether scanning the whole dialogue for a literal marker improves positive-class F1, and measured the associated false alarms. Detector A checks the last user message. Detector B applies the same substring check to all turns and combines hits with OR. The 192 synthetic examples share a three-turn grammar and are split by family into 96 development and 96 held-out examples. Marker placement was seeded separately from label construction.

Phase 2 tests a narrower question. Would the same rule interpreter, C, achieve higher F1 when given earlier turns along with the policy? The proposed secondary hypotheses are lower FPR and higher F1 than an always-positive reference with at least 80% coverage. The 120 development dialogues include matched requests, changed state, and benign controls such as quotation or explanation. C resolves intent and action, matches the active policy, then checks the latest interpretable state. D is a final-turn policy heuristic using lexical cues. A, B and D serve as diagnostics.

See the [Phase 1 protocol](research/protocol.md) and [Phase 2 protocol](research/phase2_protocol.md).

## Phase 1 frozen synthetic holdout

The saved results are from one authorized run. There were 48 positives and 48 negatives.

| Condition | TN / FP / FN / TP | Precision | Recall | FPR | F1 |
| --- | --- | ---: | ---: | ---: | ---: |
| Final message (A) | 31 / 17 / 39 / 9 | 0.3462 | 0.1875 | 0.3542 | 0.2432 |
| Full history (B) | 19 / 29 / 27 / 21 | 0.4200 | 0.4375 | 0.6042 | 0.4286 |

F1 rose by **0.1853**, with a paired family-bootstrap 95% interval of **[0.0892, 0.2985]**. History added 12 true positives and 12 false positives. FPR rose by 25 percentage points. More turns gave the substring rule more opportunities to match. See the [Phase 1 report](research/phase1_report.md).

## Phase 2 development only

| Matched C condition | Precision | Recall | FPR | F1 | Coverage |
| --- | ---: | ---: | ---: | ---: | ---: |
| Full history | 1.000 | 1.000 | 0.000 | 1.000 | 120/120 |
| Final turn | 0.000 | 0.000 | 0.000 | 0.000 | 0/120 |

Under the default numeric mapping of unresolved to 0, paired ΔF1 was +1.000 [1.000, 1.000] and ΔFPR was 0.000 [0.000, 0.000]. Under a fallback of 1, final-turn F1 is 0.667 and FPR is 1.000. Confidence intervals use 10,000 paired whole-family resamples. Identical count profiles across families explain the zero widths. Each of the 60 exact policy/final-message groups has opposing draft labels. Any deterministic classifier with those inputs can achieve at most 0.500 accuracy or 0.667 positive-class F1 on those labels.

Marker baselines A and B both had F1 of zero on the marker-free development comparison. The authored challenge exposed 12 unresolved results for the original C. The revised C resolved all 18 after those cases informed development. D remained at F1 0.600 and FPR 0.600 on that challenge. See the [validity audit](research/phase2_validity_audit.md) and [final handoff](research/PROJECT1_FINAL_HANDOFF.md).

**The Phase 2 protected holdout remains unevaluated.** Independent first-pass judgments, adjudication, protocol freeze, and separate holdout authorization are pending. The shared Phase 1 grammar, fixed marker realization and formula-derived labels bound what its bootstrap interval represents. Phase 2's hand-written parser supports limited phrasings and its main ablation deliberately removes necessary context. These experiments provide evidence about the authored fixtures and the tested rules.

## Run locally

Python 3.11 or later, using the standard library. Local verification used Python 3.15.2 on Windows. GitHub Actions is configured for Python 3.11. The demo and evaluators run offline.

```sh
python -B demo.py
python -B -m unittest discover -s tests -v
python -B verify_clean.py
python -B -m src.baseline
python -B -m src.evaluate --output results/local/phase1
python -B -m src.exploratory --development results/local/phase1 --output results/local/exploratory
python -B -m src.phase2_evaluate --output results/local/phase2
python -B -m src.phase2_evaluate --matched-c --output results/local/matched
python -B -m src.phase2_identifiability
python -B -m src.phase2_validity_audit --output results/local/challenge
```

Choose a fresh output directory for each artifact-producing command. The development files in `data/` match the archived development fixtures byte-for-byte. Historical aggregate reports are in `evidence/`. Phase 1's complete public fixture digest and the source digests reflect this distribution. The generator's `holdout` branch uses replacement fixtures for structural tests. Historical reports refer to the original internal runs and their archival paths.

## Further reading

- [Implementation walkthrough](docs/IMPLEMENTATION_EXPLAINED.md)
- [Offline demo guide](docs/DEMO.md)
- [Interview preparation](docs/INTERVIEW_PREPARATION.md)
- [Paper guide](docs/RESEARCH_PAPERS_EXPLAINED.md)
- [Röttger et al., XSTest, NAACL 2024](https://aclanthology.org/2024.naacl-long.301/)
- [Yuan et al., Beyond Over-Refusal, 2025 arXiv v3](https://arxiv.org/html/2510.08158v3)
- [AI assistance and human verification status](notes/ai_usage.md)
