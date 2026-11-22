import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from src import phase2_review as review


class TestPhase2ReviewPreparation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.items = review.review_items("challenge")
        cls.packet = review.packet_bytes(cls.items)
        cls.templates = [
            {"id": item.id, "label": None, "rationale": "", "ambiguous": None}
            for item in cls.items
        ]

    def test_development_and_challenge_cover_every_source_example_once(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            ids = {}
            for group, count in (("development", 120), ("challenge", 18)):
                directory = root / group
                review.prepare(group, directory)
                packet = (directory / "review.jsonl").read_bytes()
                template = (directory / "responses.template.jsonl").read_bytes()
                ids[group] = review.validate_packet(packet, template, count)
                self.assertEqual(packet, review.packet_bytes(review.review_items(group)))
            self.assertTrue(ids["development"].isdisjoint(ids["challenge"]))
            source = [json.loads(line) for line in review.CHALLENGE_SOURCE.read_bytes().splitlines()]
            self.assertEqual(
                {json.dumps((row["policy"], row["messages"])) for row in source},
                {json.dumps((item.policy, item.messages)) for item in self.items},
            )
            self.assertTrue(ids["challenge"].isdisjoint(row["id"] for row in source))

    def test_short_or_misaligned_template_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "count"):
            review.validate_packet(self.packet, review.jsonl(self.templates[:-1]), 18)
        unrelated = [{**self.templates[0], "id": "f" * 24}, *self.templates[1:]]
        with self.assertRaisesRegex(ValueError, "IDs differ"):
            review.validate_packet(self.packet, review.jsonl(unrelated), 18)

    def test_duplicate_ids_in_packet_template_or_reference_are_rejected(self):
        packet_lines = self.packet.splitlines()
        duplicate_packet = b"\n".join([packet_lines[0], *packet_lines[:-1]])
        duplicate_template = review.jsonl([self.templates[0], *self.templates[:-1]])
        for packet, template in ((duplicate_packet, review.jsonl(self.templates)),
                                 (self.packet, duplicate_template)):
            with self.assertRaisesRegex(ValueError, "Duplicate review ID"):
                review.validate_packet(packet, template, 18)
        with self.assertRaisesRegex(ValueError, "Duplicate reference review ID"):
            review.audit_responses([self.items[0], self.items[0]], [])

    def test_blinding_rejects_hidden_fields_and_prefilled_labels(self):
        examples = [json.loads(line) for line in self.packet.splitlines()]
        for key in ("label", "prediction", "family_id", "category", "rationale"):
            with self.subTest(key=key):
                leaked = [{**examples[0], key: 0}, *examples[1:]]
                with self.assertRaisesRegex(ValueError, "blinded example schema"):
                    review.validate_packet(review.jsonl(leaked), review.jsonl(self.templates), 18)
        prefilled = [{**self.templates[0], "label": 0}, *self.templates[1:]]
        with self.assertRaisesRegex(ValueError, "blank review fields"):
            review.validate_packet(self.packet, review.jsonl(prefilled), 18)

    def test_challenge_adjudication_separates_missing_disagreement_and_conflict(self):
        first, second, third, *_ = self.items
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            packet_directory = root / "packet"
            review.prepare("challenge", packet_directory)
            responses = root / "synthetic-test-input.jsonl"
            responses.write_bytes(review.jsonl([
                {"id": first.id, "label": 1 - first.label, "rationale": "Test explanation.",
                 "ambiguous": True},
                {"id": second.id, "label": 0, "rationale": "Test explanation.",
                 "ambiguous": False},
                {"id": second.id, "label": 1, "rationale": "Test explanation.",
                 "ambiguous": False},
            ]))
            with patch.object(review, "PRIVATE_ROOT", root / "private"):
                output = review.adjudicate("challenge", packet_directory / "review.jsonl",
                                           responses, "test-round")
            result = json.loads(output.read_bytes())
            self.assertEqual(result["expected_count"], 18)
            self.assertEqual(result["usable_response_count"], 1)
            self.assertEqual(len(result["missing_review_ids"]), 17)
            self.assertIn(third.id, result["missing_review_ids"])
            self.assertEqual(result["conflicting_review_ids"], [second.id])
            self.assertEqual(result["ambiguous_review_ids"], [first.id])
            self.assertEqual(result["provisional_disagreement_ids"], [first.id])
            self.assertNotIn("generator_disagreement_ids", result)
            self.assertNotIn("Test explanation.", output.read_text(encoding="utf-8"))

    def test_final_roster_requires_complete_resolved_unique_decisions(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            packet, template, response = (root / name for name in ("packet", "template", "response"))
            packet.write_bytes(self.packet)
            template.write_bytes(review.jsonl(self.templates))
            rows = [dict(row, label=0, rationale="Synthetic schema test.", ambiguous=False)
                    for row in self.templates]
            response.write_bytes(review.jsonl(rows))
            summary = review.verify_final_roster("challenge", packet, template, response)
            self.assertEqual(summary["count"], 18)
            self.assertNotIn("Synthetic schema test.", json.dumps(summary))
            for invalid in (rows[:-1], [rows[0], *rows[:-1]],
                            [dict(rows[0], ambiguous=True), *rows[1:]]):
                response.write_bytes(review.jsonl(invalid))
                with self.assertRaises(ValueError):
                    review.verify_final_roster("challenge", packet, template, response)
