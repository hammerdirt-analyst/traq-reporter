"""Tests for summary-slice prompt building."""

from __future__ import annotations

import unittest

from reporter_client.models.tree_report_source import GpsPoint, RiskProfile, TreeReportSource
from reporter_client.services.summary_services import build_tree_summary_prompts
from reporter_client.services.tree_report_services import TreeSummaryContextBuilder


class SummaryPromptBuilderTests(unittest.TestCase):
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
        self.transcript = (
            "[trunk]\nObserved sap ooze.\n\n"
            "[notes_explanations_descriptions]\nThis is a software test.\n\n"
            "[crown_and_branches]\nObserved extended branches over the target."
        )

    def test_tree_summary_prompt_builder_uses_form_sections_only(self) -> None:
        context = TreeSummaryContextBuilder().build(
            source=self.tree_source,
            completed_payload=self.completed_payload,
            transcript=self.transcript,
        )

        prompts = build_tree_summary_prompts(context)

        self.assertEqual(prompts.prompt_version, "tree-v1")
        self.assertIn("Return valid JSON only", prompts.user_prompt)
        self.assertIn("Write five short paragraphs in this exact order", prompts.user_prompt)
        self.assertIn("The narrative_blocks array must contain exactly 5 paragraphs.", prompts.user_prompt)
        self.assertIn("Do not mention the assessor in the body; that belongs in the signature block.", prompts.user_prompt)
        self.assertNotIn("Assessor name:", prompts.user_prompt)
        self.assertIn("Extracted form data (JSON):", prompts.user_prompt)
        self.assertIn("\"site_factors\"", prompts.user_prompt)
        self.assertIn("\"target_assessment\"", prompts.user_prompt)
        self.assertIn("\"load_factors\"", prompts.user_prompt)
        self.assertIn("\"crown_and_branches\"", prompts.user_prompt)
        self.assertIn("\"risk_categorization\"", prompts.user_prompt)
        self.assertIn("\"mitigation_options\"", prompts.user_prompt)
        self.assertNotIn("Transcript:", prompts.user_prompt)
        self.assertNotIn("Observed sap ooze.", prompts.user_prompt)
        self.assertNotIn("software test", prompts.user_prompt.lower())


if __name__ == "__main__":
    unittest.main()
