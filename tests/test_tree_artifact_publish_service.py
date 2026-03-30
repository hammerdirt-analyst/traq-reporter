"""Tests for publishing tree-linked staged artifacts into docs assets."""

from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from reporter_client.models.tree_report_source import GpsPoint, RiskProfile, TreeGeoJsonSource, TreeImageSource, TreeReportSource
from reporter_client.services.tree_report_services import TreeArtifactPublishService


class TreeArtifactPublishServiceTests(unittest.TestCase):
    def test_publish_rewrites_geojson_image_and_pdf_paths_to_published_assets(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            staged_geojson = root / "staging" / "final.geojson"
            staged_pdf = root / "staging" / "traq_page1.pdf"
            staged_image = root / "staging" / "images" / "tree.report.jpg"
            staged_geojson.parent.mkdir(parents=True, exist_ok=True)
            staged_geojson.write_text('{"type":"FeatureCollection","features":[]}', encoding="utf-8")
            staged_pdf.write_bytes(b"%PDF-1.4\nfake pdf content\n")
            staged_image.parent.mkdir(parents=True, exist_ok=True)
            staged_image.write_bytes(b"fake image bytes")
            docs_dir = root / "docs"

            source = TreeReportSource(
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
                completed_inspection_form_url=str(staged_pdf),
                tree_id="briarwood_001",
                images=[TreeImageSource(image_src=str(staged_image), caption="the tree in the middle")],
                geojson=TreeGeoJsonSource(geojson_src=str(staged_geojson)),
            )

            published = TreeArtifactPublishService().publish(source=source, docs_dir=docs_dir)

            self.assertEqual(published.geojson.geojson_src, "assets/geojson/briarwood_001.geojson")
            self.assertEqual(published.images[0].image_src, "assets/images/briarwood_001/image_01.jpg")
            self.assertEqual(published.completed_inspection_form_url, "assets/traq-forms/briarwood_001.pdf")
            self.assertTrue((docs_dir / "assets" / "geojson" / "briarwood_001.geojson").exists())
            self.assertTrue((docs_dir / "assets" / "images" / "briarwood_001" / "image_01.jpg").exists())
            self.assertTrue((docs_dir / "assets" / "traq-forms" / "briarwood_001.pdf").exists())

    def test_publish_requires_tree_id(self) -> None:
        source = TreeReportSource(
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
            completed_inspection_form_url="",
        )

        with tempfile.TemporaryDirectory() as tmp_dir:
            with self.assertRaisesRegex(ValueError, "tree_id is required"):
                TreeArtifactPublishService().publish(source=source, docs_dir=Path(tmp_dir))


if __name__ == "__main__":
    unittest.main()
