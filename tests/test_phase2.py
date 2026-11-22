import hashlib
import json
import tempfile
import unittest
from collections import Counter, defaultdict
from dataclasses import replace
from pathlib import Path
from unittest.mock import patch

from src import phase2


class TestPhase2(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = tuple(phase2.records())
        cls.development = tuple(row for row in cls.rows if row.split == "development")

    def test_schema_and_corpus_size(self):
        phase2.validate(self.rows)
        self.assertEqual(Counter(row.split for row in self.rows),
                         {"development": 120, "holdout": 120})
        for split in phase2.manifest():
            self.assertEqual({len(row.messages) for row in self.rows if row.split == split},
                             set(range(3, 8)))
        first, *rest = self.rows
        with self.assertRaisesRegex(ValueError, "message schema"):
            phase2.validate([replace(first, messages=(("system", "bad"),
                                                       *first.messages[1:])), *rest])

    def test_determinism_and_output_checksums(self):
        with tempfile.TemporaryDirectory() as tmp:
            first, second = Path(tmp) / "first", Path(tmp) / "second"
            phase2.export(first)
            phase2.export(second)
            manifest = json.loads((first / "manifest.json").read_bytes())
            for filename in ["manifest.json", *manifest["sha256"]]:
                self.assertEqual((first / filename).read_bytes(),
                                 (second / filename).read_bytes())
            for filename, digest in manifest["sha256"].items():
                self.assertEqual(hashlib.sha256((first / filename).read_bytes()).hexdigest(),
                                 digest)

    def test_family_balance_matched_requests_and_controls(self):
        families = defaultdict(Counter)
        pairs = defaultdict(list)
        for row in self.development:
            families[row.family_id][row.label] += 1
            pairs[row.pair_id].append(row)
        self.assertEqual(len(families), 15)
        for counts in families.values():
            self.assertEqual(counts, {0: 4, 1: 4})
        self.assertEqual(len(pairs), 60)
        for left, right in pairs.values():
            self.assertEqual({left.label, right.label}, {0, 1})
            self.assertEqual(left.messages[-1], right.messages[-1])
        benign = [row for row in self.development if row.control]
        self.assertEqual(len(benign), 30)
        self.assertEqual({row.control for row in benign}, set(phase2.CONTROL_TASKS))
        self.assertTrue(all(row.label == 0 for row in benign))

    def test_family_pair_and_layout_isolation(self):
        split = phase2.manifest()
        assignments = phase2.family_layouts()
        self.assertEqual(len(set(assignments.values())), 30)
        self.assertTrue(set(split["development"]).isdisjoint(split["holdout"]))
        layouts = {name: {layout for family in families for layout in assignments[family]}
                   for name, families in split.items()}
        self.assertTrue(layouts["development"].isdisjoint(layouts["holdout"]))
        families, pairs = defaultdict(set), defaultdict(set)
        for row in self.rows:
            families[row.family_id].add(row.split)
            pairs[row.pair_id].add(row.split)
        self.assertEqual(len(families), 30)
        self.assertEqual(len(pairs), 120)
        self.assertTrue(all(len(group) == 1 for group in (*families.values(), *pairs.values())))
        first, *rest = self.rows
        with self.assertRaisesRegex(ValueError, "split"):
            phase2.validate([replace(first, split="other"), *rest])

    def test_duplicate_text_rejected_across_splits(self):
        development = self.development[0]
        holdout = next(row for row in self.rows if row.split == "holdout")
        reformatted = tuple((role, "  " + message.upper() + " !")
                            for role, message in development.messages)
        with self.assertRaisesRegex(ValueError, "Normalized duplicate"):
            phase2.validate([development, replace(holdout, messages=reformatted)])

    def test_policy_and_rationale_separation(self):
        first = self.development[0]
        for text, error in ((first.policy, "Policy leaked"),
                            (first.label_rationale, "Rationale"),
                            ("OVERRIDE-DEMO-RULE", "marker")):
            with self.subTest(error=error), self.assertRaisesRegex(ValueError, error):
                messages = (("user", text), *first.messages[1:])
                phase2.validate([replace(first, messages=messages)])

    def test_mislabeled_development_example_rejected(self):
        row = next(row for row in self.development if row.pair_id.endswith("-0"))
        with self.assertRaisesRegex(ValueError, "evidence or label"):
            phase2.validate([replace(row, label=1 - row.label)])

    def test_exports_are_blinded_and_holdout_is_separate(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp)
            phase2.export(output)
            self.assertEqual({path.name for path in (output / "holdout").iterdir()},
                             {"review.jsonl"})
            known_review_ids = {row.id for row in self.rows}
            seen = set()
            for split in phase2.manifest():
                lines = (output / split / "review.jsonl").read_text(encoding="utf-8").splitlines()
                self.assertEqual(len(lines), 120)
                for line in lines:
                    record = json.loads(line)
                    self.assertEqual(set(record), {"id", "messages", "policy"})
                    self.assertTrue(all(set(turn) == {"role", "text"}
                                        for turn in record["messages"]))
                    self.assertNotIn(record["id"], seen)
                    seen.add(record["id"])
            self.assertEqual(seen, known_review_ids)
            dev_lines = (output / "development" / "fixtures.jsonl").read_bytes().splitlines()
            self.assertEqual({json.loads(line)["id"] for line in dev_lines},
                             {row.id for row in self.development})

    def test_rejects_shared_layout_ancestry(self):
        assignments = phase2.family_layouts()
        split = phase2.manifest()
        development = assignments[split["development"][0]]
        holdout = split["holdout"][0]
        assignments[holdout] = (development[0], *assignments[holdout][1:])
        with patch.object(phase2, "family_layouts", return_value=assignments):
            with self.assertRaisesRegex(ValueError, "ancestry crosses splits"):
                phase2.validate(self.rows)
