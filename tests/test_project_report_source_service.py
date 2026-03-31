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
            docs_dir=repo_root / "site-src",
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
        american_river = next(item for item in project_sources if item.project_slug == "american-river")
        self.assertEqual(american_river.tree_count, 1)
        self.assertEqual(american_river.species_count, 1)
        self.assertEqual(american_river.trees[0].tree_id, "american-river_001")
        self.assertEqual(american_river.trees[0].tree_doc, "projects/american-river/trees/american-river_001.md")
        self.assertTrue(american_river.trees[0].risk_rating)
        self.assertTrue(american_river.trees[0].main_concerns)
        self.assertTrue(all(item.project_slug in {"briarwood", "arboretum", "american-river"} for item in project_sources))

        media = ProjectMediaService(
            docs_dir=repo_root / "site-src",
            content_dir=repo_root / "content",
        ).build_media(american_river)
        self.assertEqual(media.canonical_image.caption, "El Manto access, view of the parkway.")
        self.assertEqual(media.canonical_image.image_src, "assets/project-images/american-river.jpg")

        project_map = ProjectMapService().build_map(project_source=american_river)
        self.assertEqual(project_map.image_src, "assets/maps/projects/american-river.jpg")
        self.assertEqual(len(project_map.points), 1)
        self.assertEqual([point.ordinal for point in project_map.points], [1])


if __name__ == "__main__":
    unittest.main()
