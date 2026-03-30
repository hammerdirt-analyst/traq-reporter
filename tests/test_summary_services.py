"""Tests for the remaining tree summary service wrapper."""

from __future__ import annotations

import unittest
from unittest.mock import patch

from reporter_client.models.tree_report_source import GpsPoint, RiskProfile, TreeReportSource
from reporter_client.services.tree_report_services import TreeSummaryContextBuilder, TreeSummaryService


class SummaryServiceWrapperTests(unittest.TestCase):
    def setUp(self) -> None:
        self._env_patcher = patch.dict("os.environ", {"OPENAI_API_KEY": ""}, clear=False)
        self._env_patcher.start()
        self.tree_source = TreeReportSource(
            project="Briarwood",
            job_id="job-123",
            client_revision_id="rev-123",
            archived_at="2026-03-26T00:00:00Z",
            species="Quercus agrifolia",
            dbh=20,
            height=54,
            gps=GpsPoint(latitude=38.62, longitude=-121.29),
            risk_profile=RiskProfile(
                overall_tree_risk="low",
                overall_residual_risk="low",
                recommended_inspection_interval="18 months",
            ),
            assessor_name="Roger Erismann",
            transcript="transcript",
            completed_inspection_form_url="https://client-ops.example.test/completed/job-123",
        )
        self.completed_payload = {
            "form": {
                "data": {
                    "site_factors": {"history_of_failures": "none"},
                    "target_assessment": {"targets": [{"label": "ParkingLot", "zone_within_drip_line": True}]},
                    "load_factors": {"wind_exposure": "partial"},
                    "crown_and_branches": {"main_concerns": "branches over target"},
                    "trunk": {"main_concerns": "sap ooze"},
                    "roots_and_root_collar": {"main_concerns": "pavement over roots"},
                    "tree_health_and_species": {"vigor": "high"},
                    "risk_categorization": [{"condition": "extended branches over the parking lot"}],
                    "mitigation_options": {"options": [{"option": "keep pruning and maintaining it well"}]},
                }
            }
        }

    def tearDown(self) -> None:
        self._env_patcher.stop()

    def test_tree_summary_service_returns_tree_artifact(self) -> None:
        context = TreeSummaryContextBuilder().build(
            source=self.tree_source,
            completed_payload=self.completed_payload,
            transcript="[trunk]\\nObserved sap ooze.",
        )

        artifact = TreeSummaryService().generate(context)

        self.assertEqual(artifact.page_kind, "tree")
        self.assertEqual(artifact.source_identifier, "job-123")
        self.assertEqual(artifact.prompt_version, "tree-v1")
        self.assertIn("Quercus agrifolia", artifact.summary_text)


if __name__ == "__main__":
    unittest.main()
