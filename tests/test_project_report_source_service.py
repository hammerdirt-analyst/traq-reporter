"""Tests for project-source aggregation from canonical tree payloads."""

from __future__ import annotations

from pathlib import Path
import unittest

from reporter_client.services.content_source_service import ContentSourceService
from reporter_client.services.project_report_services import (
    ProjectMapService,
    ProjectMediaService,
    ProjectReportSourceService,
)
from reporter_client.services.staged_input_service import StagedInputService


class ProjectReportSourceServiceTests(unittest.TestCase):
    def test_build_all_groups_trees_and_derives_project_metrics(self) -> None:
        repo_root = Path(__file__).resolve().parent.parent
        staged_inputs = StagedInputService(
            staging_root=repo_root.parent / "server" / "staging",
            content_dir=repo_root / "content",
            docs_dir=repo_root / "docs",
        )
        content_source = ContentSourceService(content_dir=repo_root / "content")
        tree_sources = staged_inputs.load_tree_report_sources()
        project_descriptions = {
            "Briarwood": content_source.read_project_summary("briarwood"),
            "Arboretum": content_source.read_project_summary("arboretum"),
            "American River": content_source.read_project_summary("american-river"),
        }

        project_sources = ProjectReportSourceService().build_all(
            tree_sources=tree_sources,
            project_descriptions=project_descriptions,
        )

        self.assertEqual(len(project_sources), 3)
        briarwood = next(item for item in project_sources if item.project == "Briarwood")
        self.assertEqual(briarwood.project_slug, "briarwood")
        self.assertEqual(briarwood.tree_count, 4)
        self.assertEqual(briarwood.species_count, 3)
        self.assertEqual(briarwood.earliest_archived_at, "2026-03-25T09:10:08.608364Z")
        self.assertEqual(briarwood.latest_archived_at, "2026-03-25T09:40:08.608364Z")
        self.assertEqual(briarwood.trees[0].tree_id, "briarwood_001")
        self.assertEqual(briarwood.trees[0].tree_doc, "projects/briarwood/trees/briarwood_001.md")
        self.assertEqual(briarwood.trees[0].risk_rating, "low")
        self.assertEqual(
            briarwood.trees[0].main_concerns,
            [
                "The main concern are the branches hanging over the parking lot, and that's it.",
                "the sap ooze in the, there is a, yes, there is sap ooze coming from a crack on the north",
                "the pavement that covers thirty percent of the roots",
            ],
        )
        self.assertEqual(briarwood.canonical_image_caption, "the tree in the middle")

        media = ProjectMediaService().build_media(briarwood)
        self.assertEqual(media.canonical_image.caption, "the tree in the middle")

        project_map = ProjectMapService().build_map(
            project_source=briarwood,
            fallback_map_src="assets/maps/project_alpha_overview.svg",
        )
        self.assertEqual(project_map.image_src, "assets/maps/project_alpha_overview.svg")
        self.assertEqual(len(project_map.geojson_sources), 4)


if __name__ == "__main__":
    unittest.main()
