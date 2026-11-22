import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from src import phase2, phase2_review


class TestPhase2Review(unittest.TestCase):
    def setUp(self):
        self.rows = tuple(phase2.records("development"))[:2]

    def response(self, row, **changes):
        response = {"id": row.id, "label": 0, "rationale": "Reviewed the active rule.",
                    "ambiguous": False}
        return json.dumps(response | changes)

    def test_missing_and_unfilled_template_are_pending(self):
        first, second = self.rows
        report = phase2_review.audit_responses(self.rows, [
            self.response(first, label=None, rationale="", ambiguous=None), "",
        ])
        self.assertEqual(report["missing_review_ids"], sorted([first.id, second.id]))
        self.assertEqual(report["usable_response_count"], 0)
        self.assertEqual(report["invalid_responses"], [])

    def test_duplicate_responses_are_never_counted_as_usable(self):
        first = self.rows[0]
        line = self.response(first)
        report = phase2_review.audit_responses(self.rows, [line, line])
        self.assertEqual(report["duplicate_response_lines"], {first.id: [1, 2]})
        self.assertIn(first.id, report["missing_review_ids"])
        self.assertEqual(report["conflicting_review_ids"], [])

    def test_conflicting_responses_require_resolution(self):
        first = self.rows[0]
        report = phase2_review.audit_responses(self.rows, [
            self.response(first, label=0), self.response(first, label=1, ambiguous=True),
        ])
        self.assertEqual(report["conflicting_review_ids"], [first.id])
        self.assertEqual(report["ambiguous_review_ids"], [first.id])
        self.assertEqual(report["generator_disagreement_ids"], [])
        self.assertEqual(report["usable_response_count"], 0)

    def test_invalid_responses_report_line_numbers_without_echoing_values(self):
        first = self.rows[0]
        invalid = [
            "{", "[]", self.response(first, id="unknown"), self.response(first, label=True),
            self.response(first, label="1"), self.response(first, rationale="  "),
            self.response(first, ambiguous=0), self.response(first, extra="private"),
            self.response(first).replace('"label": 0', '"label": 0, "label": 1'),
        ]
        report = phase2_review.audit_responses(self.rows, invalid)
        self.assertEqual([issue["line"] for issue in report["invalid_responses"]],
                         list(range(1, len(invalid) + 1)))
        self.assertNotIn("private", json.dumps(report))
        self.assertNotIn("Reviewed the active rule.", json.dumps(report))
        self.assertEqual(report["usable_response_count"], 0)

    def test_disagreement_and_ambiguity_are_unresolved_findings(self):
        first, second = self.rows
        report = phase2_review.audit_responses(self.rows, [
            self.response(first, label=1 - first.label, ambiguous=True),
            self.response(second, label=second.label),
        ])
        self.assertEqual(report["generator_disagreement_ids"], [first.id])
        self.assertEqual(report["ambiguous_review_ids"], [first.id])
        self.assertEqual(report["missing_review_ids"], [])
        self.assertNotIn("gold", json.dumps(report))
        self.assertNotIn("Reviewed the active rule.", json.dumps(report))

    def test_prepare_blinds_and_separates_all_240_examples(self):
        with tempfile.TemporaryDirectory() as temp:
            seen = set()
            for split in phase2.manifest():
                output = Path(temp) / split
                phase2_review.prepare(split, output)
                self.assertEqual({path.name for path in output.iterdir()},
                                 {"review.jsonl", "responses.template.jsonl"})
                packet = [json.loads(line) for line in (output / "review.jsonl").read_bytes().splitlines()]
                responses = [json.loads(line) for line in
                             (output / "responses.template.jsonl").read_bytes().splitlines()]
                self.assertEqual(len(packet), 120)
                self.assertEqual(packet, [phase2.review_record(row) for row in phase2.records(split)])
                self.assertEqual(responses, [
                    {"id": row["id"], "label": None, "rationale": "", "ambiguous": None}
                    for row in packet
                ])
                self.assertTrue(all(set(row) == {"id", "messages", "policy"} for row in packet))
                ids = {row["id"] for row in packet}
                self.assertEqual(len(ids), 120)
                self.assertTrue(seen.isdisjoint(ids))
                seen.update(ids)
                with self.assertRaises(FileExistsError):
                    phase2_review.prepare(split, output)

    def test_adjudication_checks_packet_split_and_writes_only_private_report(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp).resolve()
            packet_directory = root / "packet"
            phase2_review.prepare("development", packet_directory)
            packet = packet_directory / "review.jsonl"
            response = packet_directory / "responses.template.jsonl"
            private = root / "private"
            with patch.object(phase2_review, "PRIVATE_ROOT", private):
                with self.assertRaisesRegex(ValueError, "selected Phase 2 draft split"):
                    phase2_review.adjudicate("holdout", packet, response, "one")
                self.assertFalse(private.exists())
                report = phase2_review.adjudicate("development", packet, response, "one")
                self.assertEqual(report, private / "development" / "adjudication-one.json")
                result = json.loads(report.read_bytes())
                self.assertEqual(len(result["missing_review_ids"]), 120)
                self.assertEqual(result["usable_response_count"], 0)
                with self.assertRaises(FileExistsError):
                    phase2_review.adjudicate("development", packet, response, "one")

    def test_development_generation_stops_before_holdout_rendering(self):
        with patch.object(phase2, "render", wraps=phase2.render) as render:
            self.assertEqual(len(list(phase2.records("development"))), 120)
            self.assertEqual(render.call_count, 120)
