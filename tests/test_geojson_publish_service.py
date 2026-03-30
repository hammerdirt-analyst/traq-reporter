"""Tests for GeoJSON publishing and map-contract handoff."""

from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from reporter_client.models.project_report_source import ProjectReportSource, ProjectTreeEntry
from reporter_client.models.tree_report_source import GpsPoint, RiskProfile, TreeGeoJsonSource, TreeReportSource
from reporter_client.services.geojson_publish_service import GeoJsonPublishService
from reporter_client.services.project_report_services import ProjectMapService
from reporter_client.services.tree_report_services import TreeMapService


class GeoJsonPublishServiceTests(unittest.TestCase):
    def test_publish_copies_geojson_to_docs_asset_path(self) -> None:
        service = GeoJsonPublishService()
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            source_geojson = root / "staging" / "final.geojson"
            source_geojson.parent.mkdir(parents=True, exist_ok=True)
            source_geojson.write_text('{"type":"FeatureCollection","features":[]}', encoding="utf-8")
            docs_dir = root / "docs"

            published = service.publish(
                source_geojson_path=source_geojson,
                tree_id="briarwood_001",
                docs_dir=docs_dir,
            )

            self.assertEqual(published.asset_src, "assets/geojson/briarwood_001.geojson")
            self.assertTrue(published.asset_path.exists())
            self.assertEqual(
                published.asset_path.read_text(encoding="utf-8"),
                '{"type":"FeatureCollection","features":[]}',
            )

    def test_tree_map_service_accepts_published_geojson_asset_path(self) -> None:
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
            completed_inspection_form_url="https://client-ops.example.test/completed/job-123",
            tree_id="briarwood_001",
            geojson=TreeGeoJsonSource(geojson_src="/tmp/staged/final.geojson"),
        )

        artifact = TreeMapService().build_map(source, geojson_asset_src="assets/geojson/briarwood_001.geojson")

        self.assertEqual(artifact.geojson_asset_src, "assets/geojson/briarwood_001.geojson")
        self.assertIn("locator", artifact.image_src)

    def test_project_map_service_accepts_project_geojson_asset_list(self) -> None:
        project_source = ProjectReportSource(
            project="Briarwood",
            project_slug="briarwood",
            project_description="Stable description.",
            tree_count=2,
            species_count=2,
            earliest_archived_at="2026-03-25T09:10:08.608364Z",
            latest_archived_at="2026-03-25T09:20:08.608364Z",
            canonical_image_src=None,
            canonical_image_caption=None,
            trees=[
                ProjectTreeEntry(
                    tree_id="briarwood_001",
                    job_id="job_1",
                    tree_doc="projects/briarwood/trees/briarwood_001.md",
                    species="Quercus agrifolia",
                    risk_rating="low",
                    main_concerns=[],
                    archived_at="2026-03-25T09:10:08.608364Z",
                    transcript="",
                    geojson_src="/tmp/staged/final_1.geojson",
                    canonical_image_src=None,
                    canonical_image_caption=None,
                    dbh=20,
                    height=54,
                ),
                ProjectTreeEntry(
                    tree_id="briarwood_002",
                    job_id="job_2",
                    tree_doc="projects/briarwood/trees/briarwood_002.md",
                    species="Platanus racemosa",
                    risk_rating="moderate",
                    main_concerns=[],
                    archived_at="2026-03-25T09:20:08.608364Z",
                    transcript="",
                    geojson_src="/tmp/staged/final_2.geojson",
                    canonical_image_src=None,
                    canonical_image_caption=None,
                    dbh=22,
                    height=60,
                ),
            ],
        )

        artifact = ProjectMapService().build_map(
            project_source=project_source,
            fallback_map_src="assets/maps/project_alpha_overview.svg",
        )

        self.assertEqual(
            [point.geojson_src for point in artifact.points],
            ["/tmp/staged/final_1.geojson", "/tmp/staged/final_2.geojson"],
        )
        self.assertEqual([point.ordinal for point in artifact.points], [1, 2])
        self.assertEqual([point.risk_rating for point in artifact.points], ["low", "moderate"])
        self.assertEqual(artifact.image_src, "assets/maps/project_alpha_overview.svg")


if __name__ == "__main__":
    unittest.main()
