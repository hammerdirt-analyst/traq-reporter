"""Tests for the documentation generation service."""

from __future__ import annotations

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
        content_source = ContentSourceService(content_dir=repo_root / "content")
        with patch.dict("os.environ", {"OPENAI_API_KEY": ""}, clear=False), TemporaryDirectory() as tempdir:
            docs_dir = Path(tempdir) / "docs"
            service = DocsGenerationService(
                examples_dir=repo_root / "examples",
                content_dir=repo_root / "content",
                docs_dir=docs_dir,
            )

            service.generate()

            home_page = (docs_dir / "index.md").read_text(encoding="utf-8")
            about_page = (docs_dir / "about.md").read_text(encoding="utf-8")
            project_page = (docs_dir / "projects" / "briarwood.md").read_text(encoding="utf-8")
            bravo_page = (docs_dir / "projects" / "arboretum.md").read_text(encoding="utf-8")
            tree_page = (docs_dir / "projects" / "briarwood" / "trees" / "briarwood_001.md").read_text(encoding="utf-8")
            extra_tree_page = (docs_dir / "projects" / "arboretum" / "trees" / "arboretum_001.md").read_text(encoding="utf-8")

            self.assertIn(content_source.read_home_summary().strip(), home_page)
            self.assertIn("I have been summarized", home_page)
            self.assertIn('<a href="/reporter-client/about/">About</a>', home_page)
            self.assertRegex(home_page, r'updated_at: "\d{4}-\d{2}-\d{2} \d{2}:\d{2}"')
            self.assertIn(content_source.read_about().strip(), about_page)
            self.assertIn("I have been summarized", project_page)
            self.assertIn(content_source.read_project_summary("briarwood").strip(), project_page)
            self.assertIn(content_source.read_project_summary("arboretum").strip(), bravo_page)
            self.assertNotIn("Dominant Species", project_page)
            self.assertIn("I have been summarized.", tree_page)
            self.assertIn("Completed inspection form", tree_page)
            self.assertIn("Completed inspection form", extra_tree_page)
            self.assertNotIn("Sample tree page:", project_page)
            self.assertIn("briarwood_001", project_page)
            self.assertIn("Extended branches over the parking area", project_page)


if __name__ == "__main__":
    unittest.main()
