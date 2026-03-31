"""Tests for the documentation generation service."""

from __future__ import annotations

import shutil
from pathlib import Path
import re
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from reporter_client.services.content_source_service import ContentSourceService
from reporter_client.services.docs_generation_service import DocsGenerationService


class DocsGenerationServiceTests(unittest.TestCase):
    def test_generate_writes_pages_with_authored_markdown_and_footer(self) -> None:
        repo_root = Path(__file__).resolve().parent.parent
        staging_root = repo_root.parent / "server" / "staging"
        content_source = ContentSourceService(content_dir=repo_root / "content")
        with patch.dict("os.environ", {"OPENAI_API_KEY": ""}, clear=False), TemporaryDirectory() as tempdir:
            docs_dir = Path(tempdir) / "docs"
            shutil.copytree(
                repo_root / "docs" / "assets" / "map-bases",
                docs_dir / "assets" / "map-bases",
                dirs_exist_ok=True,
            )
            service = DocsGenerationService(
                staging_root=staging_root,
                content_dir=repo_root / "content",
                docs_dir=docs_dir,
            )

            service.generate()

            home_page = (docs_dir / "index.md").read_text(encoding="utf-8")
            about_page = (docs_dir / "about.md").read_text(encoding="utf-8")
            project_page = (docs_dir / "projects" / "american-river.md").read_text(encoding="utf-8")
            tree_page = (docs_dir / "projects" / "american-river" / "trees" / "american-river_001.md").read_text(encoding="utf-8")

            self.assertIn(content_source.read_home_summary().strip(), home_page)
            self.assertNotIn("I have been summarized", home_page)
            self.assertIn('href="/traq-reporter/about/">About</a>', home_page)
            self.assertRegex(home_page, r'updated_at: "\d{4}-\d{2}-\d{2} \d{2}:\d{2}"')
            self.assertIn(content_source.read_about().strip(), about_page)
            self.assertNotIn("I have been summarized", project_page)
            self.assertIn(content_source.read_project_summary("american-river").strip(), project_page)
            self.assertNotIn("Dominant Species", project_page)
            self.assertIn("Tree assessment summary for", tree_page)
            self.assertIn("Completed inspection form", tree_page)
            self.assertNotIn("Sample tree page:", project_page)
            self.assertIn("american-river_001", project_page)
            self.assertIn("assets/maps/projects/american-river.jpg", project_page)
            self.assertIn("assets/maps/trees/american-river_001.jpg", tree_page)
            self.assertIn("assets/project-images/american-river.svg", project_page)
            self.assertIn("assets/images/", tree_page)
            self.assertIn("/traq-reporter/assets/traq-forms/american-river_001.pdf", tree_page)
            self.assertIn("project-tree-card__number", project_page)
            self.assertNotIn("Combined assessment map", home_page)


if __name__ == "__main__":
    unittest.main()
