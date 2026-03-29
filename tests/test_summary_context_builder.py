"""Tests for summary-slice context building."""

from __future__ import annotations

import unittest

from reporter_client.models.tree_report_source import GpsPoint, RiskProfile, TreeReportSource
from reporter_client.services.tree_report_services import TreeSummaryContextBuilder


class SummaryContextBuilderTests(unittest.TestCase):
    def setUp(self) -> None:
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
                    "crown_and_branches": {"main_concerns": "branches over target"},
                    "trunk": {"main_concerns": "sap ooze"},
                    "roots_and_root_collar": {"main_concerns": "pavement over roots"},
                    "tree_health_and_species": {"vigor": "high"},
                    "risk_categorization": [{"condition": "extended branches over the parking lot"}],
                    "mitigation_options": {"options": [{"option": "keep pruning and maintaining it well"}]},
                }
            }
        }
        self.transcript = (
            "[trunk]\nObserved sap ooze.\n\n"
            "[notes_explanations_descriptions]\nThis is a software test.\n\n"
            "[crown_and_branches]\nObserved extended branches over the target."
        )

    def test_tree_summary_context_builder_extracts_expected_sections(self) -> None:
        context = TreeSummaryContextBuilder().build(
            source=self.tree_source,
            completed_payload=self.completed_payload,
            transcript=self.transcript,
        )

        self.assertEqual(context.crown_and_branches["main_concerns"], "branches over target")
        self.assertEqual(context.trunk["main_concerns"], "sap ooze")
        self.assertEqual(context.roots_and_root_collar["main_concerns"], "pavement over roots")
        self.assertEqual(context.tree_health_and_species["vigor"], "high")
        self.assertEqual(context.risk_categorization[0]["condition"], "extended branches over the parking lot")
        self.assertEqual(context.mitigation_options[0]["option"], "keep pruning and maintaining it well")

    def test_tree_summary_context_builder_filters_software_test_transcript_blocks(self) -> None:
        context = TreeSummaryContextBuilder().build(
            source=self.tree_source,
            completed_payload=self.completed_payload,
            transcript=self.transcript,
        )

        self.assertIn("Observed sap ooze.", context.transcript)
        self.assertIn("Observed extended branches over the target.", context.transcript)
        self.assertNotIn("software test", context.transcript.lower())


if __name__ == "__main__":
    unittest.main()
