# Phase 2 owner decisions

**Provisional decisions recorded 2026-11-21. Final protocol freeze remains pending.** [Protocol](phase2_protocol.md)

| Decision | Owner disposition and remaining work |
| --- | --- |
| Primary comparison | Provisionally approved. Compare full-history C against final-turn C using the same policy and interpreter on the same IDs. Positive-class F1 is the primary metric. |
| Detector D | Diagnostic only, on development and challenge. D's lexical rule and shorter input prevent attributing a C-versus-D difference to history alone. A and B remain historical development diagnostics under the draft. |
| Bootstrap | Approved for development preparation and proposed freeze settings. Use 10,000 paired whole-family draws with seed `20261125`. |
| Unresolved decisions | Approved. Score unresolved predictions as 0 in primary metrics and as 1 in sensitivity analysis. Keep both runs on identical IDs. |
| H3 | Keep separate from H1. The proposed coverage rule is `5 × resolved ≥ 4 × eligible` for full-history C, counting every frozen eligible ID in the denominator and every non-`unresolved` decision as resolved. Confirm this threshold and the H3 configuration before freeze. |
| Human review | Independent human judgments and documented adjudication are required. Reviewer(s), adjudicator, custodian and number of first passes remain unassigned or unconfirmed. Nemotron judgments are advisory only. [Assignment and adjudication](phase2_human_review_assignment.md) |

Before signing off on freeze, confirm role assignments and label process, complete human review and adjudication, verify matched C on adjudicated development data, finalize H2/H3 and reporting settings, and verify the runner and frozen configuration. Authorize any holdout run separately after freeze.

At freeze, explicitly accept or revise H1's interpretation as a history-removal
ablation on authored reference-dependent dialogues. The development
identifiability check established that every exact policy/final input has
opposite draft labels. This design supports a narrow ablation. A classification
claim about self-contained final turns needs a separate, balanced design.
