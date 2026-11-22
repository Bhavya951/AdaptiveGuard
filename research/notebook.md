# Research notebook

Updated 2026-11-20. AdaptiveGuard compares single-message and conversation-history detection on benign synthetic dialogues. The existing baseline recognizes one literal marker in four embedded smoke examples. The comparison remains a draft.

## Source verification ledger

Codex checked original bibliographic records and full-text methods and results. Human verification is pending.

| Primary source | Verified method and result | Relevance to AdaptiveGuard |
|---|---|---|
| Paul Röttger, Hannah Rose Kirk, Bertie Vidgen, Giuseppe Attanasio, Federico Bianchi, and Dirk Hovy (NAACL 2024, pp. 5377–5400). [XSTest](https://aclanthology.org/2024.naacl-long.301/) | Sections 3.1–3.2 and 4.2–4.3 describe hand-crafted standalone prompts and human coding of full compliance and partial or full refusal. The suite definition and tables identify 250 safe and 200 contrasting unsafe prompts. The opening sentence of §4.3 inconsistently lists 200 safe prompts. Reported refusal patterns differ by model and prompt type. | Supports including benign lexical contrasts and explicit error categories. The paper measures responses to single-turn prompts. [Full text](https://aclanthology.org/2024.naacl-long.301.pdf) |
| Shuzhou Yuan, Ercong Nie, Yinuo Sun, Chenxuan Zhao, William LaCroix, and Michael Färber (2025 arXiv preprint, v3, DOI 10.48550/arXiv.2510.08158). [Beyond Over-Refusal](https://arxiv.org/abs/2510.08158v3) | Sections 3.2.1–3.2.2 describe 30 constructed scenarios with 20 prompts each, a context condition that uses up to four prior model responses, a context-removed comparison, and manual response evaluation. The reported effect of removing context varies by model. | Supports grouping related cases by scenario and comparing context conditions. AdaptiveGuard will use fixed authored histories for both conditions, which avoids feedback from earlier generated responses. [Full text](https://arxiv.org/html/2510.08158v3#S3.SS2) |

The sources establish precedent for lexical contrasts and context comparisons. They provide no direct performance estimate for the proposed keyword study. No novelty claim is established. The proposed fixture specification uses original benign synthetic material and imports neither benchmark.
