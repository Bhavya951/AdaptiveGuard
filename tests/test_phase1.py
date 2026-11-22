import unittest
from dataclasses import replace
from unittest.mock import patch

from src import evaluate, fixtures


class TestPhase1(unittest.TestCase):
    def setUp(self):
        self.dialogues = tuple(fixtures.records())
        self.development = [row for row in self.dialogues if row.split == "development"]

    def test_fixture_validation_and_reproducibility(self):
        report = fixtures.validate(self.dialogues)
        self.assertEqual(len(self.dialogues), 192)
        self.assertEqual(report["dialogues"], 96)
        self.assertGreater(report["benign_historical_only"], 0)
        split = fixtures.manifest()
        self.assertEqual(len(split["development"]), 12)
        self.assertEqual(len(split["holdout"]), 12)
        self.assertTrue(set(split["development"]).isdisjoint(split["holdout"]))
        self.assertEqual(fixtures.fixture_hash(self.dialogues),
                         fixtures.fixture_hash(fixtures.records()))

    def test_rejects_policy_scaffold_labels_pairs_and_split_errors(self):
        first, second, *rest = self.dialogues
        changed_final = second.messages[-1][1] + " Reference tag: override-demo-rule."
        if fixtures.MARKER in second.messages[-1][1]:
            changed_final = second.messages[-1][1].split(" Reference tag:")[0]
        mutations = (
            ([replace(first, policy=first.policy + " OVERRIDE-DEMO-RULE"), second, *rest],
             "policy"),
            ([replace(first, label=1 - first.label), second, *rest], "label"),
            ([first, replace(second, messages=(*second.messages[:-1], ("user", changed_final))),
              *rest], "pair"),
            ([replace(first, split="other"), second, *rest], "split"),
            ([replace(first, messages=(("user", first.policy), *first.messages[1:])),
              second, *rest], "leaked"),
        )
        for rows, error in mutations:
            with self.subTest(error=error), self.assertRaisesRegex(ValueError, error):
                fixtures.validate(rows)
        with patch.object(fixtures, "OPENING", "{detail} OVERRIDE-DEMO-RULE"):
            with self.assertRaisesRegex(ValueError, "scaffold"):
                fixtures.validate(self.dialogues)

    def test_holdout_rejected_before_predicting(self):
        row = replace(self.development[0], split="holdout")
        with patch.object(evaluate, "predict") as predict:
            with self.assertRaisesRegex(ValueError, "development fixtures only"):
                evaluate.development_predictions([row])
        predict.assert_not_called()

    def test_comparison_and_metrics(self):
        self.assertEqual(evaluate.predict_messages((
            ("user", "OVERRIDE-DEMO-RULE"), ("user", "Move the sticker.")
        )), (0, 1))
        predictions = evaluate.development_predictions(self.development)
        self.assertTrue(all(row["final"] <= row["history"] for row in predictions))
        self.assertEqual({row["id"] for row in predictions},
                         {row.id for row in self.development})

        metrics = evaluate.scores({"tn": 4, "fp": 1, "fn": 2, "tp": 3})
        self.assertEqual(metrics["confusion_matrix"], [[4, 1], [2, 3]])
        self.assertEqual(metrics["precision"], 0.75)
        self.assertEqual(metrics["recall"], 0.6)
        self.assertEqual(metrics["false_positive_rate"], 0.2)
        self.assertAlmostEqual(metrics["f1"], 2 / 3)
        self.assertEqual(evaluate.scores(dict.fromkeys(("tn", "fp", "fn", "tp"), 0))["f1"], 0)

    def test_paired_bootstrap_keeps_whole_families(self):
        rows = [
            {"family_id": "a", "pair_id": "a-1", "gold": 1, "final": 0, "history": 1},
            {"family_id": "a", "pair_id": "a-2", "gold": 0, "final": 0, "history": 1},
            {"family_id": "b", "pair_id": "b-1", "gold": 1, "final": 1, "history": 1},
            {"family_id": "b", "pair_id": "b-2", "gold": 0, "final": 0, "history": 0},
        ]
        result = evaluate.summarize(rows, draws=100)
        self.assertAlmostEqual(result["delta_f1"], 0.8 - 2 / 3)
        self.assertAlmostEqual(result["delta_f1_ci95"][0], 0)
        self.assertAlmostEqual(result["delta_f1_ci95"][1], 2 / 3)
        self.assertEqual(result, evaluate.summarize(rows, draws=100))
