"""Tests for TRAQ PDF publishing."""

from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from reporter_client.services.traq_pdf_publish_service import TraqPdfPublishService


class TraqPdfPublishServiceTests(unittest.TestCase):
    def test_publish_copies_pdf_to_docs_asset_path(self) -> None:
        service = TraqPdfPublishService()
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            source_pdf = root / "staging" / "traq_page1.pdf"
            source_pdf.parent.mkdir(parents=True, exist_ok=True)
            source_pdf.write_bytes(b"%PDF-1.4\nfake pdf content\n")
            docs_dir = root / "docs"

            published = service.publish(
                source_pdf_path=source_pdf,
                tree_id="briarwood_001",
                docs_dir=docs_dir,
            )

            self.assertEqual(published.asset_src, "assets/traq-forms/briarwood_001.pdf")
            self.assertTrue(published.asset_path.exists())
            self.assertEqual(published.asset_path.read_bytes(), b"%PDF-1.4\nfake pdf content\n")

    def test_publish_overwrites_existing_pdf_on_rerun(self) -> None:
        service = TraqPdfPublishService()
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            docs_dir = root / "docs"
            source_pdf = root / "staging" / "traq_page1.pdf"
            source_pdf.parent.mkdir(parents=True, exist_ok=True)
            source_pdf.write_bytes(b"%PDF-1.4\nfirst content\n")

            service.publish(
                source_pdf_path=source_pdf,
                tree_id="briarwood_001",
                docs_dir=docs_dir,
            )

            source_pdf.write_bytes(b"%PDF-1.4\nupdated content\n")
            published = service.publish(
                source_pdf_path=source_pdf,
                tree_id="briarwood_001",
                docs_dir=docs_dir,
            )

            self.assertEqual(published.asset_path.read_bytes(), b"%PDF-1.4\nupdated content\n")


if __name__ == "__main__":
    unittest.main()
