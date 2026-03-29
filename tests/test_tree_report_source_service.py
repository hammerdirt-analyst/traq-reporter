"""Tests for tree report source mapping from completed inspection payloads."""

from __future__ import annotations

from dataclasses import asdict
import json
from pathlib import Path
import unittest

from reporter_client.services.tree_report_services import TreeReportSourceService


class TreeReportSourceServiceTests(unittest.TestCase):
    def test_build_maps_confirmed_fields_from_completed_payload(self) -> None:
        repo_root = Path(__file__).resolve().parent.parent
        completed_payload = json.loads((repo_root / "examples" / "example_raw_output_from_api.json").read_text(encoding="utf-8"))
        transcript = (repo_root / "examples" / "example_raw_transcript_from_api.txt").read_text(encoding="utf-8")
        expected = json.loads((repo_root / "examples" / "tree_report_source.sample.json").read_text(encoding="utf-8"))

        service = TreeReportSourceService(
            completed_form_url_resolver=lambda payload: f"https://client-ops.example.test/completed/{payload['job_id']}"
        )

        tree_report_source = service.build(completed_payload, transcript=transcript)
        result = asdict(tree_report_source)

        self.assertEqual(result["project"], expected["project"])
        self.assertEqual(result["job_id"], expected["job_id"])
        self.assertEqual(result["client_revision_id"], expected["client_revision_id"])
        self.assertEqual(result["archived_at"], expected["archived_at"])
        self.assertEqual(result["species"], expected["species"])
        self.assertEqual(result["dbh"], expected["dbh"])
        self.assertEqual(result["height"], expected["height"])
        self.assertEqual(result["gps"], expected["gps"])
        self.assertEqual(result["risk_profile"], expected["risk_profile"])
        self.assertEqual(result["assessor_name"], expected["assessor_name"])
        self.assertEqual(result["tree_id"], expected["tree_id"])
        self.assertEqual(result["main_concerns"], expected["main_concerns"])
        self.assertEqual(result["images"], expected["images"])
        self.assertEqual(result["geojson"], expected["geojson"])
        self.assertEqual(result["transcript"], transcript)
        self.assertEqual(result["completed_inspection_form_url"], expected["completed_inspection_form_url"])


if __name__ == "__main__":
    unittest.main()
