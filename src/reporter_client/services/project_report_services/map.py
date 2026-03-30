"""Project map mapping service."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from ...models.project_report_source import ProjectReportSource
from ..map_processor_service import MapProcessorRequest, MapProcessorService


@dataclass(frozen=True)
class ProjectMapArtifact:
    image_src: str
    alt: str
    geojson_sources: list[str]


class ProjectMapService:
    """Build the project-page map artifact from all tree geojson sources."""

    def __init__(self, *, docs_dir: Path | None = None, map_processor_service: MapProcessorService | None = None) -> None:
        self._map_processor_service = map_processor_service or MapProcessorService(docs_dir=docs_dir)

    def build_map(
        self,
        *,
        project_source: ProjectReportSource,
        fallback_map_src: str,
        geojson_sources: list[str] | None = None,
    ) -> ProjectMapArtifact:
        resolved_geojson_sources = geojson_sources or [entry.geojson_src for entry in project_source.trees if entry.geojson_src]
        map_artifact = self._map_processor_service.render(
            MapProcessorRequest(
                output_asset_src=f"assets/maps/projects/{project_source.project_slug}.svg",
                fallback_image_src=fallback_map_src,
                alt=f"{project_source.project} assessment map",
                geojson_sources=resolved_geojson_sources,
            )
        )
        return ProjectMapArtifact(
            image_src=map_artifact.image_src,
            alt=map_artifact.alt,
            geojson_sources=map_artifact.geojson_sources,
        )
