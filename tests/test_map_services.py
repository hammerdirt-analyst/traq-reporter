"""Tests for the GeoJSON-to-map service contract."""

from __future__ import annotations

import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from PIL import Image

from reporter_client.models.project_report_source import ProjectReportSource, ProjectTreeEntry
from reporter_client.models.tree_report_source import GpsPoint, RiskProfile, TreeGeoJsonSource, TreeReportSource
from reporter_client.services.map_processor_service import MapProcessorService, MapRenderPoint, MapRenderRequest
from reporter_client.services.project_report_services import ProjectMapService
from reporter_client.services.tree_report_services import TreeMapService


class MapProcessorServiceTests(unittest.TestCase):
    def test_render_writes_map_when_geojson_assets_exist(self) -> None:
        with TemporaryDirectory() as tempdir:
            docs_dir = Path(tempdir) / "docs"
            map_base_dir = docs_dir / "assets" / "map-bases"
            geojson_dir = docs_dir / "assets" / "geojson"
            map_base_dir.mkdir(parents=True, exist_ok=True)
            geojson_dir.mkdir(parents=True, exist_ok=True)
            Image.new("RGB", (320, 240), (235, 239, 244)).save(map_base_dir / "briarwood_base.jpg", format="JPEG")
            (map_base_dir / "briarwood_base.json").write_text(
                json.dumps(
                    {
                        "west": -121.30,
                        "east": -121.28,
                        "south": 38.61,
                        "north": 38.63,
                        "width": 320,
                        "height": 240,
                        "zoom": 16,
                    }
                ),
                encoding="utf-8",
            )
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
                MapRenderRequest(
                    output_asset_src="assets/maps/trees/example_001.jpg",
                    fallback_image_src="assets/maps/placeholder.jpg",
                    alt="Example map",
                    basemap_slug="briarwood",
                    points=[
                        MapRenderPoint(
                            ordinal=1,
                            risk_rating="low",
                            geojson_src="assets/geojson/example_001.geojson",
                        )
                    ],
                )
            )

            self.assertEqual(artifact.image_src, "assets/maps/trees/example_001.jpg")
            rendered_map = docs_dir / "assets" / "maps" / "trees" / "example_001.jpg"
            self.assertTrue(rendered_map.exists())
            with Image.open(rendered_map) as image:
                self.assertEqual(image.format, "JPEG")
                self.assertEqual(image.size, (320, 240))
            self.assertEqual(artifact.points[0].ordinal, 1)
            self.assertEqual(artifact.points[0].risk_rating, "low")

    def test_render_falls_back_when_geojson_assets_are_missing(self) -> None:
        with TemporaryDirectory() as tempdir:
            artifact = MapProcessorService(docs_dir=Path(tempdir) / "docs").render(
                MapRenderRequest(
                    output_asset_src="assets/maps/trees/example_001.jpg",
                    fallback_image_src="assets/maps/placeholder.jpg",
                    alt="Example map",
                    basemap_slug="briarwood",
                    points=[
                        MapRenderPoint(
                            ordinal=1,
                            risk_rating="low",
                            geojson_src="assets/geojson/example_001.geojson",
                        )
                    ],
                )
            )

        self.assertEqual(artifact.image_src, "assets/maps/placeholder.jpg")


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

        self.assertEqual(artifact.image_src, "../assets/maps/job_123_locator.jpg")
        self.assertEqual(artifact.ordinal, 1)
        self.assertEqual(artifact.risk_rating, "low")
        self.assertEqual(artifact.geojson_asset_src, "assets/geojson/briarwood_001.geojson")

    def test_build_map_renders_cropped_tree_map_from_gps_when_basemap_exists(self) -> None:
        with TemporaryDirectory() as tempdir:
            docs_dir = Path(tempdir) / "docs"
            map_base_dir = docs_dir / "assets" / "map-bases"
            map_base_dir.mkdir(parents=True, exist_ok=True)
            Image.new("RGB", (400, 300), (235, 239, 244)).save(map_base_dir / "briarwood_base.jpg", format="JPEG")
            (map_base_dir / "briarwood_base.json").write_text(
                json.dumps(
                    {
                        "west": -121.30,
                        "east": -121.27,
                        "south": 38.61,
                        "north": 38.64,
                        "width": 400,
                        "height": 300,
                        "zoom": 16,
                    }
                ),
                encoding="utf-8",
            )
            source = TreeReportSource(
                project="Briarwood",
                job_id="job_123",
                client_revision_id="rev_123",
                archived_at="2026-03-28T12:00:00Z",
                species="Quercus agrifolia",
                dbh=30,
                height=40,
                gps=GpsPoint(latitude=38.62, longitude=-121.29),
                risk_profile=RiskProfile(
                    overall_tree_risk="low",
                    overall_residual_risk="low",
                    recommended_inspection_interval="12 months",
                ),
                assessor_name="Assessor",
                transcript="Transcript",
                completed_inspection_form_url="assets/traq-forms/briarwood_001.pdf",
                tree_id="briarwood_001",
                geojson=None,
            )

            artifact = TreeMapService(docs_dir=docs_dir).build_map(source)

            self.assertEqual(artifact.image_src, "assets/maps/trees/briarwood_001.jpg")
            rendered_map = docs_dir / "assets" / "maps" / "trees" / "briarwood_001.jpg"
            self.assertTrue(rendered_map.exists())
            with Image.open(rendered_map) as image:
                self.assertEqual(image.format, "JPEG")
                self.assertEqual(image.size, (320, 240))


class ProjectMapServiceTests(unittest.TestCase):
    def test_build_map_uses_all_project_tree_geojson_assets(self) -> None:
        with TemporaryDirectory() as tempdir:
            docs_dir = Path(tempdir) / "docs"
            map_base_dir = docs_dir / "assets" / "map-bases"
            geojson_dir = docs_dir / "assets" / "geojson"
            map_base_dir.mkdir(parents=True, exist_ok=True)
            geojson_dir.mkdir(parents=True, exist_ok=True)
            Image.new("RGB", (400, 300), (235, 239, 244)).save(map_base_dir / "briarwood_base.jpg", format="JPEG")
            (map_base_dir / "briarwood_base.json").write_text(
                json.dumps(
                    {
                        "west": -121.30,
                        "east": -121.27,
                        "south": 38.61,
                        "north": 38.64,
                        "width": 400,
                        "height": 300,
                        "zoom": 16,
                    }
                ),
                encoding="utf-8",
            )
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

            self.assertEqual(artifact.image_src, "assets/maps/projects/briarwood.jpg")
            self.assertEqual(
                [point.ordinal for point in artifact.points],
                [1, 2],
            )
            self.assertEqual(
                [point.risk_rating for point in artifact.points],
                ["low", "moderate"],
            )
            self.assertTrue((docs_dir / "assets" / "maps" / "projects" / "briarwood.jpg").exists())
            with Image.open(docs_dir / "assets" / "maps" / "projects" / "briarwood.jpg") as image:
                self.assertEqual(image.format, "JPEG")
                self.assertEqual(image.size, (400, 300))


if __name__ == "__main__":
    unittest.main()
