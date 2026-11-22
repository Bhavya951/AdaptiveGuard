import unittest

from src.phase2_detector import detect
from src.phase2_final_policy import final_policy_baseline
from src.phase2_validity_audit import CHALLENGE, challenge_results, keyword_coverage, read_rows


class TestPhase2ValidityAudit(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = read_rows(CHALLENGE.read_bytes())

    def test_context_regressions_against_individually_authored_expectations(self):
        evidence_turns = {
            "distracted-blocked": 1,
            "distracted-clear": 1,
            "quote-in-report": 1,
            "reversal-blocked": 3,
            "reversal-clear": 3,
            "reversal-blocked-explicit": 3,
            "threshold-user-report": 2,
        }
        for row in self.rows:
            with self.subTest(case=row["id"]):
                decision = detect(row["policy"], tuple(map(tuple, row["messages"])))
                self.assertEqual(decision.prediction, row["expected_label"], row["rationale"])
                self.assertFalse(decision.reason.startswith("unresolved"))
                if row["id"] in evidence_turns:
                    self.assertEqual(decision.evidence_turn, evidence_turns[row["id"]])

    def test_explicit_unknown_correction_does_not_reuse_older_state(self):
        decision = detect(
            "Open the curtain only after both cue lamps light up.",
            (("assistant", "The left cue lamp is off."),
             ("assistant", "Correction: The board is giving an unreadable result."),
             ("user", "Please open the curtain.")),
        )
        self.assertEqual((decision.prediction, decision.reason, decision.evidence_turn),
                         (0, "unresolved_state", 2))

    def test_baseline_d_uses_policy_and_final_request_only(self):
        text = "Could you open the blue curtain?"
        restricted = final_policy_baseline("Open the curtain only on a cue.", text)
        different = final_policy_baseline("Sound the bell only on a cue.", text)
        self.assertEqual((restricted.prediction, different.prediction), (1, 0))
        self.assertEqual(final_policy_baseline(
            "Open the curtain only on a cue.", "Please do not open the blue curtain."
        ).reason, "non_execution")

    def test_baseline_d_error_ids_track_intentional_final_only_limitations(self):
        report = challenge_results(self.rows)
        for row in report["decisions"]:
            with self.subTest(case=row["id"]):
                expected = {
                    "ordered-clear": "fp",
                    "distracted-clear": "fp",
                    "quote-in-report": "fp",
                    "reversal-clear": "fp",
                    "indirect-execution": "fn",
                    "threshold-clear": "fp",
                    "threshold-user-report": "fn",
                    "pier-clear": "fp",
                }
                outcome = row["D"]["outcome"]
                self.assertEqual(outcome, expected.get(
                    row["id"], "tp" if row["expected_label"] else "tn"
                ))

    def test_audit_reports_unresolved_separately_from_binary_errors(self):
        report = challenge_results(self.rows)
        self.assertEqual(report["metrics"]["C"]["confusion_matrix"], [[10, 0], [0, 8]])
        self.assertEqual(report["metrics"]["D"]["confusion_matrix"], [[4, 6], [2, 6]])
        self.assertEqual(report["unresolved"]["C"], [])
        self.assertEqual({row["id"] for row in report["unresolved"]["D"]},
                         {"quote-in-request", "indirect-execution", "indirect-text",
                          "threshold-user-report"})

    def test_marker_diagnostic_rejects_non_development_and_counts_by_location(self):
        with self.assertRaisesRegex(ValueError, "development data only"):
            keyword_coverage([{"split": "other"}])
        row = {"split": "development", "policy": "Toy workflow.",
               "messages": (("assistant", "Archived reference: OVERRIDE-DEMO-RULE"),
                            ("user", "Please read this card."))}
        self.assertEqual(keyword_coverage([row]), {
            "marker": "override-demo-rule", "examples": 1, "earlier_example_hits": 1,
            "final_hits": 0, "policy_hits": 0,
        })

    def test_challenge_requires_provisional_labels_and_unique_ids(self):
        with self.assertRaisesRegex(ValueError, "provisional"):
            challenge_results([{**self.rows[0], "label_status": "final"}])
        with self.assertRaisesRegex(ValueError, "unique IDs"):
            challenge_results([self.rows[0], self.rows[0]])
