"""Tests for canonical page builders."""

from __future__ import annotations

from pathlib import Path
import unittest
from unittest.mock import patch

from reporter_client.builders.about_page_builder import AboutPageBuilder
from reporter_client.builders.home_page_builder import HomePageBuilder
from reporter_client.builders.project_page_builder import ProjectPageBuilder
from reporter_client.builders.tree_page_builder import TreePageBuilder
from reporter_client.services.staged_input_service import StagedInputService


class PageBuilderTests(unittest.TestCase):
    def setUp(self) -> None:
        self._env_patcher = patch.dict("os.environ", {"OPENAI_API_KEY": ""}, clear=False)
        self._env_patcher.start()
        repo_root = Path(__file__).resolve().parent.parent
        self.inputs = StagedInputService(
            staging_root=repo_root.parent / "server" / "staging",
            content_dir=repo_root / "content",
            docs_dir=repo_root / "site-src",
        )

    def tearDown(self) -> None:
        self._env_patcher.stop()

    def test_home_page_builder(self) -> None:
        view = HomePageBuilder().build(self.inputs.load_home_input())
        self.assertEqual(view.page_title, "TRAQ Reporter")
        self.assertEqual(view.breadcrumbs[0].label, "Home")
        self.assertEqual(view.summary_metrics.assessment_count, str(len(self.inputs.load_tree_inputs())))
        self.assertEqual(view.summary_metrics.project_count, "3")
        self.assertFalse(hasattr(view, "combined_map"))
        project_labels = [link.label for link in view.project_links]
        self.assertIn("Briarwood", project_labels)
        self.assertIn("Arboretum", project_labels)
        self.assertIn("American River", project_labels)

    def test_about_page_builder(self) -> None:
        view = AboutPageBuilder().build(self.inputs.load_about_input())
        self.assertEqual(view.page_title, "About Hammerdirt")
        self.assertEqual(view.breadcrumbs[0].href, "/traq-reporter/")

    def test_project_page_builder(self) -> None:
        project_input = next(item for item in self.inputs.load_project_inputs() if item.project_id == "american-river")
        view = ProjectPageBuilder().build(project_input)
        self.assertEqual(view.page_title, "American River")
        self.assertIn("American River", view.description_markdown)
        self.assertEqual(view.project_image.caption, "El Manto access, view of the parkway.")
        self.assertIn("assets/project-images/american-river.jpg", view.project_image.image_href)
        self.assertIn("assets/maps/projects/american-river.jpg", view.project_map.image_href)
        self.assertEqual(view.tree_cards[0].ordinal, 1)
        self.assertEqual(view.tree_cards[0].job_number, "american-river_001")
        self.assertTrue(view.tree_cards[0].species_common)
        self.assertTrue(view.tree_cards[0].risk_rating)

    def test_tree_page_builder(self) -> None:
        tree_inputs = self.inputs.load_tree_inputs()
        self.assertGreaterEqual(len(tree_inputs), 1)
        target_input = tree_inputs[0]
        view = TreePageBuilder().build(target_input)
        self.assertTrue(view.page_title)
        self.assertEqual(view.breadcrumbs[1].label, "American River")
        self.assertEqual(view.completed_inspection_form_link.label, "Completed inspection form")
        self.assertTrue(view.image_gallery[0].caption)
        self.assertIn("assets/images/", view.image_gallery[0].image_href)
        self.assertIn("assets/maps/trees/american-river_001.jpg", view.tree_map.image_href)
        self.assertEqual(view.completed_inspection_form_link.href, "/traq-reporter/assets/traq-forms/american-river_001.pdf")


if __name__ == "__main__":
    unittest.main()
