# AdaptiveGuard Phase 1 — Keyword detection over fictional dialogues

**Internal report · 2026-11-21 · Independent human review pending**

## Abstract

We compared a literal keyword rule applied to the final user message (A) with the same rule applied across the full dialogue (B). The 192 authored dialogues were grouped into 24 fictional workflow families, with 96 dialogues and 12 families per split. In the single authorized held-out run, positive-class F1 rose from 0.24324324324324326 to 0.42857142857142855, a difference of +0.1853281853281853. The paired family-bootstrap 95% interval was [0.08922397047397046, 0.29852770358089487]. B added 12 true positives and 12 false positives, raising FPR by 0.25.

## Question and related work

The project objective is to “Compare single-message and conversation-level safety detection on benign synthetic conversations.” The classification unit is the final user request in one authored dialogue. A positive label means carrying out the resolved request would violate the active fictional workflow rule.

XSTest compares language-model responses for 250 hand-crafted safe prompts and 200 unsafe contrasts. MS-XSB evaluates language-model responses in scenario dialogues using up to four prior model responses and manual response evaluation. Both studies provide design precedents for evaluating false alarms and contextual variation. AdaptiveGuard instead scores action requests with a deterministic keyword rule. [Röttger et al., NAACL 2024](https://aclanthology.org/2024.naacl-long.301/) · [Yuan et al., arXiv v3](https://arxiv.org/html/2510.08158v3)

## Data and methods

Each family shares a three-message grammar and contains four matched pairs, two with opposite labels and one each with two positive or two negative labels. Each split contains 48 positives and 48 negatives. The split holds out workflow families while retaining the dialogue grammar. The generator derives labels and rationales from current state and requested action. Its structural checks establish consistency with that recipe. Independent human review of the rendered labels remains pending.

Both conditions use a case-insensitive substring search for `override-demo-rule`. A sees the final message and B ORs hits over all dialogue messages through that turn. Both receive message text alone. The generator draws final-turn marker insertion once per pair with probability 0.25 and opening-turn insertion once per dialogue with probability 0.35. Placement is independent of the label. The schema records ID, family, pair, split, role/text messages, policy, label and rationale.

The primary outcome is positive-class F1 for B minus A. F1 is `2TP / (2TP + FP + FN)` and FPR is `FP / (FP + TN)`. The paired bootstrap drew 12 whole families with replacement per replicate, kept both predictions together for each sampled family, and recomputed the difference from pooled counts. The 95% interval uses linearly interpolated 2.5th and 97.5th percentiles from 10,000 draws.

## Results

| Split and condition | TN / FP / FN / TP | Precision | Recall | FPR | F1 |
| --- | --- | ---: | ---: | ---: | ---: |
| Development A | 39 / 9 / 43 / 5 | 0.35714285714285715 | 0.10416666666666667 | 0.1875 | 0.16129032258064516 |
| Development B | 24 / 24 / 27 / 21 | 0.4666666666666667 | 0.4375 | 0.5 | 0.45161290322580644 |
| Holdout A | 31 / 17 / 39 / 9 | 0.34615384615384615 | 0.1875 | 0.3541666666666667 | 0.24324324324324326 |
| Holdout B | 19 / 29 / 27 / 21 | 0.42 | 0.4375 | 0.6041666666666666 | 0.42857142857142855 |

Development ΔF1 was +0.29032258064516125 [0.1681539289102738, 0.43171797489516806]. Holdout ΔF1 was +0.1853281853281853 [0.08922397047397046, 0.29852770358089487].

| Held-out label | A 0 → B 0 | A 0 → B 1 | A 1 → B 0 | A 1 → B 1 |
| --- | ---: | ---: | ---: | ---: |
| Negative | 19 | 12 | 0 | 17 |
| Positive | 27 | 12 | 0 | 9 |

The separate exploratory policy-aware prototype agreed with all 96 development labels. It had access to fictional policy text and was written for the same grammar and rubric used to construct the labels. Its score describes development agreement.

## Interpretation

Scanning more text increased marker exposure. Under the frozen marker placement and balanced prevalence, the added hits raised recall and F1 while increasing false alarms. The rule has no representation of policy, intent or state. The interval describes variation across the 12 designed held-out families under one marker realization. The common grammar, constructed 50/50 prevalence, formula-derived labels and small family count limit the result. The study used no natural dialogue, trained classifier, cost-sensitive threshold evaluation, systematic adversarial robustness experiment or deployment. Its conclusion is specific to this synthetic benchmark and fixed rule.

## Reproducibility and sign-off

Python 3.15.2 on Windows. The split seed was `20261120`, marker seed `20261122`, and bootstrap seed `20261121`. The development command was `python -m src.evaluate --output results/private/phase1-development` with a new output directory. The holdout log records one authorized attempt via a `python -` wrapper. Standalone wrapper source is unavailable. Audit the saved predictions and retain the one-run record.

| Artifact | SHA-256 |
| --- | --- |
| `results/private/phase1-frozen-corpus/corpus.jsonl` | `ba230180a938025d06790a077fca7e52f1edfaa84c7e9f97aa01987dc777eafa` |
| `results/private/phase1-frozen-corpus/manifest.json` | `af0a22d623d1b81679a7939063e8ad7958e6f632d67968df167abe0b21f26824` |
| `results/private/phase1-development/development-fixtures.jsonl` | `6803f63e26646d942163c0ec22df00687c1ffa5561bafe9c760e3f298a584b2a` |
| `results/private/phase1-holdout/predictions.json` | `7ba6e52ae0a44217d152eadd45a7c95b570fb74071df0e6ee3c818db83a3c53c` |
| `results/private/phase1-holdout/report.json` | `0b3066fe8c784b4d05d5d9e85d2b3269d661925b1204c00d75c2838cf4394b99` |
| `src/baseline.py` | `a8d1069a34dfec93eb1217034b77a597f73391d57d574105634a5fbc13160c7d` |
| `src/fixtures.py` | `060a24519a379fd7f6885325c57e5b3851c5be13cc75174dbdb3ee0a8d20049b` |
| `src/evaluate.py` | `ea9d6a9d8d03a86b296809ce24ad48842596694025f7989ad9c197a17d1a25c2` |

Codex drafted this report, checked the hashes above and recomputed both splits' metrics and intervals from saved predictions. Repository verification is recorded separately in [the progress log](../notes/progress.md). Owner review of labels, artifacts, interpretation and any external sharing remains pending. Record any subsequent label disagreements in a separate review record.
