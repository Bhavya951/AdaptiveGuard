import unittest

from src.phase2_analysis import paired_family_bootstrap


def row(example, family, label, baseline, context):
    return {"id": example, "family_id": family, "split": "development",
            "draft_label": label, "predictions": {"history_keyword": baseline, "context": context}}


class TestPhase2Analysis(unittest.TestCase):
    def test_complete_families_and_paired_percentiles(self):
        rows = [row("a", "first", 1, 0, 1), row("b", "first", 0, 1, 0),
                row("c", "second", 1, 1, 0), row("d", "second", 0, 0, 1)]
        result = paired_family_bootstrap(rows)
        self.assertEqual(result, paired_family_bootstrap(reversed(rows)))
        self.assertEqual(result["draws"], 10_000)
        self.assertEqual(result["differences"], {"f1": 0.0, "false_positive_rate": 0.0})
        self.assertEqual(result["percentile_ci95"],
                         {"f1": [-1.0, 1.0], "false_positive_rate": [-1.0, 1.0]})
        self.assertEqual(result["family_metrics"]["first"]["context"]["confusion_matrix"],
                         [[1, 0], [0, 1]])

    def test_unequal_family_sizes_pool_counts(self):
        rows = [row("a", "first", 1, 0, 1), row("b", "first", 0, 1, 0),
                row("c", "first", 0, 1, 0), row("d", "second", 1, 1, 0),
                row("e", "second", 0, 0, 1)]
        result = paired_family_bootstrap(rows, draws=5, seed=8)
        self.assertAlmostEqual(result["differences"]["f1"], 0.1)
        self.assertAlmostEqual(result["differences"]["false_positive_rate"], -1 / 3)
        self.assertEqual(result["seed"], 8)

    def test_identical_detectors_have_zero_delta_in_every_draw(self):
        rows = [row("a", "first", 1, 1, 1), row("b", "first", 0, 0, 0),
                row("c", "second", 1, 0, 0), row("d", "second", 0, 1, 1)]
        self.assertEqual(paired_family_bootstrap(rows, draws=50)["percentile_ci95"],
                         {"f1": [0.0, 0.0], "false_positive_rate": [0.0, 0.0]})

    def test_rejects_holdout_duplicates_and_unpaired_predictions(self):
        valid = row("a", "first", 1, 0, 1)
        for rows in ([], [dict(valid, split="holdout")], [valid, valid],
                     [dict(valid, predictions={"context": 1})]):
            with self.subTest(rows=rows), self.assertRaises(ValueError):
                paired_family_bootstrap(rows)
