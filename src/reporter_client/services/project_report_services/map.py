"""Project map mapping service."""

from __future__ import annotations

from dataclasses import dataclass

from ...models.project_report_source import ProjectReportSource


@dataclass(frozen=True)
class ProjectMapArtifact:
    image_src: str
    alt: str
    geojson_sources: list[str]


class ProjectMapService:
    """Build the project-page map artifact from all tree geojson sources."""

    def build_map(
        self,
        *,
        project_source: ProjectReportSource,
        fallback_map_src: str,
        geojson_sources: list[str] | None = None,
    ) -> ProjectMapArtifact:
        resolved_geojson_sources = geojson_sources or [entry.geojson_src for entry in project_source.trees if entry.geojson_src]
        return ProjectMapArtifact(
            image_src=fallback_map_src,
            alt=f"{project_source.project} assessment map",
            geojson_sources=resolved_geojson_sources,
        )
