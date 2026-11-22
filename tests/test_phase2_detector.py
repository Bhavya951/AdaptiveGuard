import unittest
from dataclasses import asdict
from unittest.mock import patch

from src.phase2_detector import detect
from src.phase2 import records
from src.phase2_evaluate import compare, compare_matched_c


class TestPhase2Detector(unittest.TestCase):
    POLICY = "A practice stage opens its curtain only after both cue lamps light up."
    TASK = ("user", "I need you to open the blue curtain.")
    BLOCKED = ("assistant", "The right lamp is off.")
    ALLOWED = ("assistant", "Both cue lamps are on.")
    FINAL = ("user", "Please handle that.")

    def test_matched_final_requests(self):
        blocked = detect(self.POLICY, (self.TASK, self.BLOCKED, self.FINAL))
        allowed = detect(self.POLICY, (self.TASK, self.ALLOWED, self.FINAL))
        self.assertEqual((blocked.prediction, allowed.prediction), (1, 0))
        self.assertEqual(blocked.reason, "violation")
        self.assertEqual(blocked.evidence_turn, 2)
        self.assertEqual(blocked.action, "open the blue curtain")

    def test_non_execution_does_not_trigger_on_action_mentions(self):
        for text in (
            "Please quote ‘open the blue curtain’ in a note.",
            "Please explain why someone might open the blue curtain.",
            "Don't open the blue curtain. Please draft a note about the cue lamps.",
            "Please describe what would happen if they opened the blue curtain.",
            "Please summarize the archived instruction to open the blue curtain.",
            "Please suggest a title for the entry ‘open the blue curtain’.",
        ):
            with self.subTest(text=text):
                result = detect(self.POLICY, (("user", text), self.BLOCKED, self.FINAL))
                self.assertEqual((result.prediction, result.reason), (0, "non_execution"))

    def test_clear_direct_request_takes_precedence_over_earlier_discussion(self):
        result = detect(self.POLICY, (
            ("user", "Please explain the curtains."), self.BLOCKED,
            ("user", "Could you open the blue curtain?"),
        ))
        self.assertEqual(result.prediction, 1)

    def test_ambiguous_requests_are_explicitly_unresolved(self):
        for messages in (
            (self.BLOCKED, self.FINAL),
            (self.TASK, ("user", "Please draft a note."), self.BLOCKED, self.FINAL),
            (self.BLOCKED, ("user", "Please open the curtain or move the cart.")),
        ):
            with self.subTest(messages=messages):
                result = detect(self.POLICY, messages)
                self.assertEqual((result.prediction, result.reason), (0, "unresolved_request"))

    def test_varied_lengths_use_current_state_and_skip_archived_reports(self):
        for length in range(3, 8):
            with self.subTest(length=length):
                extra_turns = (
                    ("assistant", "The earlier report said this. The left lamp is off."),
                    ("user", "Please check the workflow record."),
                    ("assistant", "The earlier report said this. The right lamp is off."),
                    ("user", "Use the current report when handling my task."),
                )[:length - 3]
                messages = (self.TASK, *extra_turns,
                            ("assistant", "Update: Both cue lamps are lit."), self.FINAL)
                result = detect(self.POLICY, messages)
                self.assertEqual((result.prediction, result.reason), (0, "permitted"))
                self.assertEqual(result.evidence_turn, length - 1)
        updated = detect(self.POLICY, (
            self.TASK, self.ALLOWED, ("assistant", "Now: The left cue lamp is dark."),
            ("assistant", "Got it."), self.FINAL,
        ))
        self.assertEqual((updated.prediction, updated.evidence_turn), (1, 3))

    def test_unknown_state_and_policy_are_auditable(self):
        missing = detect(self.POLICY, (self.TASK, ("assistant", "No reading yet."), self.FINAL))
        unsupported = detect("Always speak softly.", (self.TASK, self.BLOCKED, self.FINAL))
        self.assertEqual(missing.reason, "unresolved_state")
        self.assertEqual(unsupported.reason, "unresolved_policy_or_action")

    def test_threshold_uses_values_in_policy_and_evidence(self):
        messages = (("assistant", "The gauge reads 6."), ("user", "Feed the paper snail."))
        lower = detect("Feed only when the gauge drops below six.", messages)
        higher = detect("Feed only when the gauge drops below seven.", messages)
        self.assertEqual((lower.prediction, higher.prediction), (1, 0))


class TestPhase2DevelopmentComparison(unittest.TestCase):
    def test_rejects_non_development_before_running_any_detector(self):
        with patch("src.phase2_evaluate.detect") as context, patch(
                "src.phase2_evaluate.predict_messages") as keyword:
            with self.assertRaisesRegex(ValueError, "development fixtures only"):
                compare([{"split": "development"}, {"split": "holdout"}])
            context.assert_not_called()
            keyword.assert_not_called()

    def test_comparison_passes_only_text_inputs_and_scores_all_ids(self):
        rows = [asdict(row) for row in records("development")]
        with patch("src.phase2_evaluate.detect", wraps=detect) as context:
            report, predictions = compare(rows)
        self.assertEqual(report["examples"], 120)
        self.assertEqual({row["id"] for row in rows}, {row["id"] for row in predictions})
        self.assertEqual(context.call_count, 120)
        for row, call in zip(rows, context.call_args_list):
            self.assertEqual(call.args, (row["policy"], tuple(map(tuple, row["messages"]))))
            self.assertEqual(call.kwargs, {})
        for metrics in report["metrics"].values():
            self.assertEqual(sum(map(sum, metrics["confusion_matrix"])), 120)


class TestMatchedCDevelopmentComparison(unittest.TestCase):
    def test_paired_inputs_metrics_coverage_and_determinism(self):
        case = TestPhase2Detector
        rows = [
            {"id": "a", "family_id": "one", "split": "development", "label": 1,
             "policy": case.POLICY, "messages": (case.TASK, case.BLOCKED, case.FINAL)},
            {"id": "b", "family_id": "two", "split": "development", "label": 0,
             "policy": case.POLICY, "messages": (case.BLOCKED, ("user", "Please explain why."))},
        ]
        with patch("src.phase2_evaluate.detect", wraps=detect) as resolver:
            report, predictions = compare_matched_c(rows)
        self.assertEqual([call.args for call in resolver.call_args_list], [
            (row["policy"], turns)
            for row in rows for turns in (row["messages"][-1:], row["messages"])
        ])
        self.assertEqual((report, predictions), compare_matched_c(reversed(rows)))
        self.assertEqual([row["id"] for row in predictions], ["a", "b"])
        self.assertEqual(report["metrics"]["context_final"]["confusion_matrix"], [[1, 0], [1, 0]])
        self.assertEqual(report["metrics"]["context_history"]["confusion_matrix"], [[1, 0], [0, 1]])
        self.assertEqual(report["unresolved_as_positive_metrics"]["context_final"]["confusion_matrix"],
                         [[1, 0], [0, 1]])
        self.assertEqual(report["coverage"]["context_final"]["rate"], 0.5)
        self.assertEqual(report["coverage"]["context_final"]["by_label"][1]["rate"], 0)
        self.assertEqual(report["unresolved_by_label_and_reason"]["context_final"][1],
                         {"unresolved_request": 1})
        analysis = report["paired_family_bootstrap"]
        self.assertEqual(analysis["contrast"], "context_history minus context_final")
        self.assertEqual((analysis["draws"], analysis["seed"]), (10_000, 20261125))
        self.assertEqual(analysis["differences"], {"f1": 1.0, "false_positive_rate": 0.0})
        h3 = report["h3_development_diagnostic"]
        self.assertEqual(h3["history_coverage_ci95"], [1.0, 1.0])
        self.assertAlmostEqual(h3["always_positive_comparison"]["differences"]["f1"], 1 / 3)

    def test_rejects_non_development_before_inference(self):
        with patch("src.phase2_evaluate.detect") as resolver:
            with self.assertRaisesRegex(ValueError, "development fixtures only"):
                compare_matched_c([{"split": "development"}, {"split": "holdout"}])
            resolver.assert_not_called()
