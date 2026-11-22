# AdaptiveGuard Phase 2 — Final report template

**Status: Pending protocol approval, independent label adjudication, freeze and authorized evaluation.**

## Abstract

**PENDING** — Approved question, adjudicated sample, primary effect and uncertainty, false-positive trade-off and scope of inference.

## Protocol and related work

**PENDING** — Approved protocol version and date. The proposal compares full-history C to final-only C for H1 (F1) and H2 (FPR), and defines H3 against an always-positive reference with a coverage floor. Record the final criteria and D's approved role. Describe XSTest and MS-XSB as refusal-evaluation precedents and cite primary sources. [Draft protocol](phase2_protocol.md) · [Phase 1 report](phase1_report.md)

## Corpus and independent labeling

**PENDING** — Final example counts, class balance, family/pair/layout isolation, normalized duplicates and benign control distribution. Record review rounds, human reviewer independence, ambiguity/disagreement and adjudication counts, revisions and re-review. Record any AI-assisted diagnostics with their own provenance. Report holdout custody and use private references for per-case records.

## Detectors and evaluation

**PENDING** — Frozen versions, allowed inputs, identical scored IDs and treatment of unresolved cases. A and B are keyword anchors. C takes policy plus history. Draft D is policy plus final-turn lexical overlap. Document approved conditions, marker absence, policy-access differences and shared rubric or renderer assumptions.

## Confirmatory results

| Condition | TN / FP / FN / TP | Precision | Recall | F1 | FPR | Unresolved / coverage |
| --- | --- | --- | --- | --- | --- | --- |
| C, full history | PENDING | PENDING | PENDING | PENDING | PENDING | PENDING |
| C, final turn only | PENDING | PENDING | PENDING | PENDING | PENDING | PENDING |
| Other approved conditions | PENDING | PENDING | PENDING | PENDING | PENDING | PENDING |

| Contrast | Point estimate | Paired family-bootstrap 95% interval |
| --- | --- | --- |
| Full-history C minus final-only C F1 | PENDING | PENDING |
| Full-history C minus final-only C FPR | PENDING | PENDING |
| Full-history C minus always-positive reference F1 | PENDING | PENDING |

**PENDING** — Adjudicated development results, held-out family confusion counts, paired transitions, matched-pair consistency, error categories by dialogue type, and unresolved cases. Report provisional challenge cases as development regressions. Record sample counts and deviations by section.

Report full-history coverage and its family-bootstrap interval separately from the H1 effect. Record the preapproved H3 integer threshold comparison, its always-positive F1 reference and the unresolved-as-positive sensitivity results. Explain that the exact development policy/final inputs had opposite draft labels and that the matched comparison measures history removal in a reference-dependent task.

The development implementation defaults to 10,000 draws and seed `20261125`, resamples paired whole families with replacement and computes metrics from pooled counts. Its 95% percentile interval uses linear interpolation, with zero for empty metric denominators. **PENDING** — Approve the final settings and record the frozen analysis digest.

## Reproducibility, interpretation and sign-off

**PENDING** — Final digests for corpus, split, expected IDs, detector and analysis sources and configuration. Include environment, clean test run, exact runner, authorization, attempt log, predictions and integrity checks. Summarize supported findings, benchmark-conditional uncertainty, unequal information and algorithms, synthetic prevalence, shared rendering, challenge reuse and coverage. Record independent reviewer, owner and external-sharing decisions.
