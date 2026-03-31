"""Tree map mapping service."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from ...models.tree_report_source import TreeReportSource
from ..project_naming import project_slug
from ..map_processor_service import MapProcessorService, MapRenderPoint, MapRenderRequest


@dataclass(frozen=True)
class TreeMapArtifact:
    image_src: str
    alt: str
    ordinal: int
    risk_rating: str
    geojson_asset_src: str | None = None


class TreeMapService:
    """Build the tree-page map asset from the tree source."""

    _PLACEHOLDER_IMAGE_SRC = "../assets/maps/job_123_locator.jpg"
    _CROP_WIDTH = 320
    _CROP_HEIGHT = 240

    def __init__(self, *, docs_dir: Path | None = None, map_processor_service: MapProcessorService | None = None) -> None:
        self._map_processor_service = map_processor_service or MapProcessorService(docs_dir=docs_dir)

    def build_map(self, source: TreeReportSource, *, geojson_asset_src: str | None = None) -> TreeMapArtifact:
        resolved_geojson_asset_src = geojson_asset_src or (source.geojson.geojson_src if source.geojson else None)
        ordinal = source.project_ordinal or 1
        map_artifact = self._map_processor_service.render(
            MapRenderRequest(
                output_asset_src=f"assets/maps/trees/{source.tree_id}.jpg" if source.tree_id else self._PLACEHOLDER_IMAGE_SRC,
                alt=f"{source.species} locator map",
                basemap_slug=project_slug(source.project),
                crop_width=self._CROP_WIDTH,
                crop_height=self._CROP_HEIGHT,
                points=[
                    MapRenderPoint(
                        ordinal=ordinal,
                        risk_rating=source.risk_profile.overall_tree_risk,
                        geojson_src=resolved_geojson_asset_src or "",
                        longitude=source.gps.longitude,
                        latitude=source.gps.latitude,
                    )
                ]
                if source.gps or resolved_geojson_asset_src
                else [],
            )
        )
        return TreeMapArtifact(
            image_src=map_artifact.image_src,
            alt=map_artifact.alt,
            ordinal=ordinal,
            risk_rating=source.risk_profile.overall_tree_risk,
            geojson_asset_src=resolved_geojson_asset_src,
        )
