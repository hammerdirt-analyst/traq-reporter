"""Tests for summary service architecture skeleton."""

from __future__ import annotations

import unittest
from unittest.mock import patch

from reporter_client.models.home_report_source import HomeReportSource
from reporter_client.models.project_report_source import ProjectReportSource
from reporter_client.models.summary_contexts import HomeSummaryContext, ProjectSummaryContext, TreeSummaryContext
from reporter_client.models.tree_report_source import GpsPoint, RiskProfile, TreeReportSource
from reporter_client.services.home_report_services import HomeSummaryService
from reporter_client.services.project_report_services import ProjectSummaryService
from reporter_client.services.summary_services import (
    _extract_json_payload,
    build_tree_summary_prompts,
    parse_summary_response,
)
from reporter_client.services.tree_report_services import TreeSummaryContextBuilder, TreeSummaryService


class SummaryServiceTests(unittest.TestCase):
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

    def tearDown(self) -> None:
        self._env_patcher.stop()

    def test_tree_summary_context_builder(self) -> None:
        context = TreeSummaryContextBuilder().build(
            source=self.tree_source,
            completed_payload=self.completed_payload,
            transcript=self.transcript,
        )
        self.assertEqual(context.crown_and_branches["main_concerns"], "branches over target")
        self.assertEqual(context.trunk["main_concerns"], "sap ooze")
        self.assertEqual(context.mitigation_options[0]["option"], "keep pruning and maintaining it well")
        self.assertIn("Observed sap ooze.", context.transcript)
        self.assertNotIn("software test", context.transcript.lower())

    def test_tree_summary_prompt_builder_uses_sections_and_transcript(self) -> None:
        context = TreeSummaryContextBuilder().build(
            source=self.tree_source,
            completed_payload=self.completed_payload,
            transcript=self.transcript,
        )
        prompts = build_tree_summary_prompts(context)
        self.assertIn("Write 2 to 4 short paragraphs", prompts.user_prompt)
        self.assertIn("Crown and branches (JSON)", prompts.user_prompt)
        self.assertIn("Mitigation options (JSON)", prompts.user_prompt)
        self.assertIn("Observed sap ooze.", prompts.user_prompt)
        self.assertNotIn("software test", prompts.user_prompt.lower())

    def test_tree_summary_service(self) -> None:
        context = TreeSummaryContextBuilder().build(
            source=self.tree_source,
            completed_payload=self.completed_payload,
            transcript=self.transcript,
        )
        artifact = TreeSummaryService().generate(context)
        self.assertEqual(artifact.page_kind, "tree")
        self.assertEqual(artifact.source_identifier, "job-123")
        self.assertIn("Quercus agrifolia", artifact.summary_text)
        self.assertEqual(artifact.prompt_version, "tree-v1")

    def test_parse_summary_response(self) -> None:
        response = parse_summary_response(
            '{"summary_text":"Lead summary.","narrative_blocks":["Paragraph 1.","Paragraph 2."]}'
        )
        self.assertEqual(response.summary_text, "Lead summary.")
        self.assertEqual(response.narrative_blocks, ["Paragraph 1.", "Paragraph 2."])

    def test_extract_json_payload_strips_markdown_fences(self) -> None:
        payload = _extract_json_payload(
            '```json\n{"summary_text":"Lead summary.","narrative_blocks":["Paragraph 1.","Paragraph 2."]}\n```'
        )
        self.assertEqual(
            payload,
            '{"summary_text":"Lead summary.","narrative_blocks":["Paragraph 1.","Paragraph 2."]}',
        )

    def test_project_summary_service(self) -> None:
        project_source = ProjectReportSource(
            project="Briarwood",
            project_slug="briarwood",
            project_description="Stable project description.",
            tree_count=1,
            species_count=1,
            earliest_archived_at="2026-03-26T00:00:00Z",
            latest_archived_at="2026-03-26T00:00:00Z",
            canonical_image_src=None,
            canonical_image_caption=None,
            trees=[],
        )
        artifact = ProjectSummaryService().generate(
            ProjectSummaryContext(
                project_id="briarwood",
                project_name="Briarwood",
                stable_description="Stable project description.",
                project_source=project_source,
            )
        )
        self.assertEqual(artifact.page_kind, "project")
        self.assertEqual(artifact.source_identifier, "briarwood")
        self.assertIn("Briarwood", artifact.summary_text)
        self.assertEqual(artifact.prompt_version, "project-v1")

    def test_home_summary_service(self) -> None:
        home_source = HomeReportSource(
            site_title="Hammerdirt Tree Reporting",
            project_count=3,
            tree_count=10,
            species_count=10,
            earliest_archived_at="2026-03-25T09:10:08.608364Z",
            latest_archived_at="2026-03-25T11:30:08.608364Z",
            projects=[],
        )
        artifact = HomeSummaryService().generate(
            HomeSummaryContext(
                home_source=home_source,
                stable_intro="Stable intro.",
                project_summaries=["Briarwood summary"],
            )
        )
        self.assertEqual(artifact.page_kind, "home")
        self.assertEqual(artifact.source_identifier, "Hammerdirt Tree Reporting")
        self.assertIn("Hammerdirt Tree Reporting", artifact.summary_text)
        self.assertEqual(artifact.prompt_version, "home-v1")


if __name__ == "__main__":
    unittest.main()
