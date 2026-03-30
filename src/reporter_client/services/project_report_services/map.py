"""Project map mapping service."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from ...models.project_report_source import ProjectReportSource
from ..map_processor_service import MapProcessorService, MapRenderPoint, MapRenderRequest


@dataclass(frozen=True)
class ProjectMapArtifact:
    image_src: str
    alt: str
    points: list[MapRenderPoint]


class ProjectMapService:
    """Build the project-page map artifact from all tree geojson sources."""

    _MARKER_RADIUS = 8
    _MARKER_FONT_SIZE = 6

    def __init__(self, *, docs_dir: Path | None = None, map_processor_service: MapProcessorService | None = None) -> None:
        self._map_processor_service = map_processor_service or MapProcessorService(docs_dir=docs_dir)

    def build_map(
        self,
        *,
        project_source: ProjectReportSource,
        fallback_map_src: str,
    ) -> ProjectMapArtifact:
        points = [
            MapRenderPoint(
                ordinal=index,
                risk_rating=entry.risk_rating,
                geojson_src=entry.geojson_src,
            )
            for index, entry in enumerate(project_source.trees, start=1)
            if entry.geojson_src
        ]
        map_artifact = self._map_processor_service.render(
            MapRenderRequest(
                output_asset_src=f"assets/maps/projects/{project_source.project_slug}.jpg",
                fallback_image_src=fallback_map_src,
                alt=f"{project_source.project} assessment map",
                basemap_slug=project_source.project_slug,
                marker_radius=self._MARKER_RADIUS,
                marker_font_size=self._MARKER_FONT_SIZE,
                points=points,
            )
        )
        return ProjectMapArtifact(
            image_src=map_artifact.image_src,
            alt=map_artifact.alt,
            points=map_artifact.points,
        )
