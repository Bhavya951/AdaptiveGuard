import unittest
from dataclasses import asdict

from src.phase2 import records
from src.phase2_identifiability import input_identifiability, placement_probe


class TestIdentifiability(unittest.TestCase):
    def test_actual_development_exact_inputs_conflict(self):
        result = input_identifiability(asdict(row) for row in records("development"))
        self.assertEqual(result, {
            "exact_input_groups": 60, "opposite_label_groups": 60,
            "examples_in_opposite_label_groups": 120, "accuracy_ceiling": 0.5,
            "f1_ceiling": 2 / 3,
        })

    def test_policy_and_evidence_placement_controls(self):
        rows = placement_probe()
        self.assertEqual(len(rows), 6)
        for row in rows:
            with self.subTest(threshold=row["threshold"], reading=row["reading"]):
                self.assertEqual(row["history_separate"]["prediction"], row["authored_expectation"])
                self.assertEqual(row["final_embedded"]["prediction"], row["authored_expectation"])
                self.assertIn(row["final_embedded"]["reason"], ("permitted", "violation"))
                self.assertEqual(row["final_separate"]["reason"], "unresolved_state")
        self.assertEqual([row["final_embedded"]["prediction"] for row in rows
                          if row["reading"] == 7], [1, 0])
