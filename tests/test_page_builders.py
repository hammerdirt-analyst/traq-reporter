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
            docs_dir=repo_root / "docs",
        )

    def tearDown(self) -> None:
        self._env_patcher.stop()

    def test_home_page_builder(self) -> None:
        view = HomePageBuilder().build(self.inputs.load_home_input())
        self.assertEqual(view.page_title, "TRAQ Reporter")
        self.assertEqual(view.breadcrumbs[0].label, "Home")
        self.assertEqual(view.summary_metrics.assessment_count, "10")
        self.assertEqual(view.summary_metrics.project_count, "3")
        self.assertFalse(hasattr(view, "combined_map"))
        project_labels = [link.label for link in view.project_links]
        self.assertIn("Briarwood", project_labels)
        self.assertIn("Arboretum", project_labels)
        self.assertIn("American River", project_labels)

    def test_about_page_builder(self) -> None:
        view = AboutPageBuilder().build(self.inputs.load_about_input())
        self.assertEqual(view.page_title, "About Hammerdirt")
        self.assertEqual(view.breadcrumbs[0].href, "/reporter-client/")

    def test_project_page_builder(self) -> None:
        project_input = next(item for item in self.inputs.load_project_inputs() if item.project_id == "briarwood")
        view = ProjectPageBuilder().build(project_input)
        self.assertEqual(view.page_title, "Briarwood")
        self.assertIn("I have been summarized", view.summary_markdown)
        self.assertIn("Briarwood is a community of Rancho Cordova", view.description_markdown)
        self.assertEqual(view.project_image.caption, "Briarwood project image")
        self.assertIn("assets/project-images/briarwood.svg", view.project_image.image_href)
        self.assertIn("assets/maps/projects/briarwood.svg", view.project_map.image_href)
        self.assertEqual(view.tree_cards[0].ordinal, 1)
        self.assertEqual(view.tree_cards[0].job_number, "briarwood_001")
        self.assertEqual(view.tree_cards[0].species_common, "Quercus agrifolia")
        self.assertEqual(view.tree_cards[0].risk_rating, "low")
        self.assertIn("branches hanging over the parking lot", view.tree_cards[0].main_concerns)
        self.assertIn("sap ooze", view.tree_cards[0].main_concerns)
        self.assertIn("thirty percent of the roots", view.tree_cards[0].main_concerns)

    def test_tree_page_builder(self) -> None:
        tree_inputs = self.inputs.load_tree_inputs()
        self.assertEqual(len(tree_inputs), 10)
        target_input = next(item for item in tree_inputs if item.tree_doc == "projects/briarwood/trees/briarwood_001.md")
        view = TreePageBuilder().build(target_input)
        self.assertEqual(view.page_title, "Quercus agrifolia")
        self.assertEqual(view.breadcrumbs[1].label, "Briarwood")
        self.assertEqual(view.completed_inspection_form_link.label, "Completed inspection form")
        self.assertEqual(view.image_gallery[0].caption, "the tree in the middle")
        self.assertIn("assets/images/", view.image_gallery[0].image_href)
        self.assertIn("assets/maps/trees/briarwood_001.svg", view.tree_map.image_href)
        self.assertEqual(view.completed_inspection_form_link.href, "/reporter-client/assets/traq-forms/briarwood_001.pdf")


if __name__ == "__main__":
    unittest.main()
