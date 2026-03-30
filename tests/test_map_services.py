"""Tests for the GeoJSON-to-map service contract."""

from __future__ import annotations

import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from reporter_client.models.project_report_source import ProjectReportSource, ProjectTreeEntry
from reporter_client.models.tree_report_source import GpsPoint, RiskProfile, TreeGeoJsonSource, TreeReportSource
from reporter_client.services.map_processor_service import MapProcessorRequest, MapProcessorService
from reporter_client.services.project_report_services import ProjectMapService
from reporter_client.services.tree_report_services import TreeMapService


class MapProcessorServiceTests(unittest.TestCase):
    def test_render_writes_svg_when_geojson_assets_exist(self) -> None:
        with TemporaryDirectory() as tempdir:
            docs_dir = Path(tempdir) / "docs"
            geojson_dir = docs_dir / "assets" / "geojson"
            geojson_dir.mkdir(parents=True, exist_ok=True)
            (geojson_dir / "example_001.geojson").write_text(
                json.dumps(
                    {
                        "type": "FeatureCollection",
                        "features": [
                            {
                                "type": "Feature",
                                "geometry": {"type": "Point", "coordinates": [-121.29, 38.62]},
                                "properties": {},
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )

            artifact = MapProcessorService(docs_dir=docs_dir).render(
                MapProcessorRequest(
                    output_asset_src="assets/maps/trees/example_001.svg",
                    fallback_image_src="assets/maps/placeholder.svg",
                    alt="Example map",
                    geojson_sources=["assets/geojson/example_001.geojson"],
                )
            )

            self.assertEqual(artifact.image_src, "assets/maps/trees/example_001.svg")
            rendered_map = docs_dir / "assets" / "maps" / "trees" / "example_001.svg"
            self.assertTrue(rendered_map.exists())
            self.assertIn("<svg", rendered_map.read_text(encoding="utf-8"))

    def test_render_falls_back_when_geojson_assets_are_missing(self) -> None:
        with TemporaryDirectory() as tempdir:
            artifact = MapProcessorService(docs_dir=Path(tempdir) / "docs").render(
                MapProcessorRequest(
                    output_asset_src="assets/maps/trees/example_001.svg",
                    fallback_image_src="assets/maps/placeholder.svg",
                    alt="Example map",
                    geojson_sources=["assets/geojson/example_001.geojson"],
                )
            )

        self.assertEqual(artifact.image_src, "assets/maps/placeholder.svg")


class TreeMapServiceTests(unittest.TestCase):
    def test_build_map_uses_published_tree_geojson_asset(self) -> None:
        source = TreeReportSource(
            project="Briarwood",
            job_id="job_123",
            client_revision_id="rev_123",
            archived_at="2026-03-28T12:00:00Z",
            species="Quercus agrifolia",
            dbh=30,
            height=40,
            gps=GpsPoint(latitude=38.0, longitude=-121.0),
            risk_profile=RiskProfile(
                overall_tree_risk="low",
                overall_residual_risk="low",
                recommended_inspection_interval="12 months",
            ),
            assessor_name="Assessor",
            transcript="Transcript",
            completed_inspection_form_url="assets/traq-forms/briarwood_001.pdf",
            tree_id="briarwood_001",
            geojson=TreeGeoJsonSource(geojson_src="assets/geojson/briarwood_001.geojson"),
        )

        artifact = TreeMapService().build_map(source)

        self.assertEqual(artifact.image_src, "../assets/maps/job_123_locator.svg")
        self.assertEqual(artifact.geojson_asset_src, "assets/geojson/briarwood_001.geojson")


class ProjectMapServiceTests(unittest.TestCase):
    def test_build_map_uses_all_project_tree_geojson_assets(self) -> None:
        with TemporaryDirectory() as tempdir:
            docs_dir = Path(tempdir) / "docs"
            geojson_dir = docs_dir / "assets" / "geojson"
            geojson_dir.mkdir(parents=True, exist_ok=True)
            (geojson_dir / "briarwood_001.geojson").write_text(
                json.dumps(
                    {"type": "FeatureCollection", "features": [{"type": "Feature", "geometry": {"type": "Point", "coordinates": [-121.29, 38.62]}, "properties": {}}]}
                ),
                encoding="utf-8",
            )
            (geojson_dir / "briarwood_002.geojson").write_text(
                json.dumps(
                    {"type": "FeatureCollection", "features": [{"type": "Feature", "geometry": {"type": "Point", "coordinates": [-121.28, 38.63]}, "properties": {}}]}
                ),
                encoding="utf-8",
            )

            project_source = ProjectReportSource(
                project="Briarwood",
                project_slug="briarwood",
                project_description="Description",
                tree_count=2,
                species_count=2,
                earliest_archived_at="2026-03-28T12:00:00Z",
                latest_archived_at="2026-03-29T12:00:00Z",
                canonical_image_src=None,
                canonical_image_caption=None,
                trees=[
                    ProjectTreeEntry(
                        tree_id="briarwood_001",
                        job_id="job_1",
                        tree_doc="projects/briarwood/trees/briarwood_001.md",
                        species="Quercus agrifolia",
                        risk_rating="low",
                        main_concerns=["Concern one"],
                        archived_at="2026-03-28T12:00:00Z",
                        transcript="Transcript one",
                        geojson_src="assets/geojson/briarwood_001.geojson",
                        canonical_image_src=None,
                        canonical_image_caption=None,
                    ),
                    ProjectTreeEntry(
                        tree_id="briarwood_002",
                        job_id="job_2",
                        tree_doc="projects/briarwood/trees/briarwood_002.md",
                        species="Platanus racemosa",
                        risk_rating="moderate",
                        main_concerns=["Concern two"],
                        archived_at="2026-03-29T12:00:00Z",
                        transcript="Transcript two",
                        geojson_src="assets/geojson/briarwood_002.geojson",
                        canonical_image_src=None,
                        canonical_image_caption=None,
                    ),
                ],
            )

            artifact = ProjectMapService(docs_dir=docs_dir).build_map(
                project_source=project_source,
                fallback_map_src="assets/maps/project_alpha_overview.svg",
            )

            self.assertEqual(artifact.image_src, "assets/maps/projects/briarwood.svg")
            self.assertEqual(
                artifact.geojson_sources,
                ["assets/geojson/briarwood_001.geojson", "assets/geojson/briarwood_002.geojson"],
            )
            self.assertTrue((docs_dir / "assets" / "maps" / "projects" / "briarwood.svg").exists())


if __name__ == "__main__":
    unittest.main()
