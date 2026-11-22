import io
import json
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

import nemotron_review
from src.phase2_review import packet_bytes, review_items


class TestBlindedPreparation(unittest.TestCase):
    def test_offline_export_contains_only_canonical_reviewer_fields(self):
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            packet = root / "packet.jsonl"
            packet.write_bytes(packet_bytes(review_items("development")))
            output = root / "ai"
            with (patch.object(nemotron_review, "configuration") as config,
                  patch.object(nemotron_review, "request") as request,
                  patch("sys.argv", ["nemotron_review.py", "--prepare-blinded", "development",
                                     str(packet), "--output", str(output)]),
                  redirect_stdout(io.StringIO())):
                nemotron_review.main()
            config.assert_not_called()
            request.assert_not_called()
            contents = (output / "requests.jsonl").read_bytes().splitlines()
            self.assertEqual(len(contents), 120)
            self.assertEqual([json.loads(line)["messages"][1]["content"].encode()
                              for line in contents], packet.read_bytes().splitlines())
            for line in packet.read_bytes().splitlines():
                self.assertEqual(set(json.loads(line)), {"id", "policy", "messages"})

    def test_rejects_tampered_payload_and_holdout(self):
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            packet = root / "packet.jsonl"
            packet.write_bytes(b'{"label":1,"predictions":{}}\n')
            for split in ("development", "holdout"):
                with self.subTest(split=split), self.assertRaises(ValueError):
                    nemotron_review.prepare_blinded(split, packet, root / "ai")
            self.assertFalse((root / "ai").exists())


class TestNemotronReview(unittest.TestCase):
    def test_key_check_sends_no_material_and_prints_no_key_metadata(self):
        with (
            patch("sys.argv", ["nemotron_review.py", "--check"]),
            patch.object(nemotron_review, "configuration",
                         return_value=("mock-key", "nvidia/nemotron-demo:free")),
            patch.object(nemotron_review, "request",
                         return_value={"data": {"label": "private-label"}}) as request,
            redirect_stdout(io.StringIO()) as output,
        ):
            nemotron_review.main()

        request.assert_called_once_with("/key", "mock-key")
        self.assertIn("accepted", output.getvalue())
        self.assertNotIn("mock-key", output.getvalue())
        self.assertNotIn("private-label", output.getvalue())

    def test_paid_model_is_rejected_before_request(self):
        with (
            patch("sys.argv", ["nemotron_review.py", "research/protocol.md"]),
            patch.object(nemotron_review, "configuration",
                         return_value=("mock-key", "nvidia/nemotron-demo")),
            patch.object(nemotron_review, "request") as request,
        ):
            with self.assertRaisesRegex(SystemExit, ":free"):
                nemotron_review.main()

        request.assert_not_called()
