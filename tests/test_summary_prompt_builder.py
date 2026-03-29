"""Tests for summary-slice prompt building."""

from __future__ import annotations

import unittest

from reporter_client.models.home_report_source import HomeReportSource
from reporter_client.models.project_report_source import ProjectReportSource
from reporter_client.models.summary_contexts import HomeSummaryContext, ProjectSummaryContext
from reporter_client.models.tree_report_source import GpsPoint, RiskProfile, TreeReportSource
from reporter_client.services.home_report_services import HomeSummaryService
from reporter_client.services.project_report_services import ProjectSummaryService
from reporter_client.services.summary_services import (
    build_home_summary_prompts,
    build_project_summary_prompts,
    build_tree_summary_prompts,
)
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

    def test_tree_summary_prompt_builder_uses_sections_and_cleaned_transcript(self) -> None:
        context = TreeSummaryContextBuilder().build(
            source=self.tree_source,
            completed_payload=self.completed_payload,
            transcript=self.transcript,
        )

        prompts = build_tree_summary_prompts(context)

        self.assertEqual(prompts.prompt_version, "tree-v1")
        self.assertIn("Return valid JSON only", prompts.user_prompt)
        self.assertIn("Write 2 to 4 short paragraphs", prompts.user_prompt)
        self.assertIn("Crown and branches (JSON)", prompts.user_prompt)
        self.assertIn("Mitigation options (JSON)", prompts.user_prompt)
        self.assertIn("Observed sap ooze.", prompts.user_prompt)
        self.assertNotIn("software test", prompts.user_prompt.lower())

    def test_project_summary_prompt_builder_uses_project_context(self) -> None:
        project_source = ProjectReportSource(
            project="Briarwood",
            project_slug="briarwood",
            project_description="Stable project description.",
            tree_count=4,
            species_count=4,
            earliest_archived_at="2026-03-25T09:10:08.608364Z",
            latest_archived_at="2026-03-25T09:40:08.608364Z",
            canonical_image_src=None,
            canonical_image_caption=None,
            trees=[],
        )
        context = ProjectSummaryContext(
            project_id="briarwood",
            project_name="Briarwood",
            stable_description="Stable project description.",
            project_source=project_source,
        )

        prompts = build_project_summary_prompts(context)

        self.assertEqual(prompts.prompt_version, "project-v1")
        self.assertIn("Project name: Briarwood", prompts.user_prompt)
        self.assertIn("Stable description: Stable project description.", prompts.user_prompt)
        self.assertIn("Assessment count: 4", prompts.user_prompt)

    def test_home_summary_prompt_builder_uses_home_context(self) -> None:
        home_source = HomeReportSource(
            site_title="TRAQ Reporter",
            project_count=3,
            tree_count=10,
            species_count=10,
            earliest_archived_at="2026-03-25T09:10:08.608364Z",
            latest_archived_at="2026-03-25T11:30:08.608364Z",
            projects=[],
        )
        context = HomeSummaryContext(
            home_source=home_source,
            stable_intro="Stable intro.",
            project_summaries=["Briarwood summary", "Arboretum summary"],
        )

        prompts = build_home_summary_prompts(context)

        self.assertEqual(prompts.prompt_version, "home-v1")
        self.assertIn("Site title: TRAQ Reporter", prompts.user_prompt)
        self.assertIn("Stable intro: Stable intro.", prompts.user_prompt)
        self.assertIn("Project summaries:", prompts.user_prompt)
        self.assertIn("Briarwood summary", prompts.user_prompt)


if __name__ == "__main__":
    unittest.main()
