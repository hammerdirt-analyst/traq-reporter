"""Build project page inputs from project report sources."""

from __future__ import annotations

from ...models.page_inputs import ProjectPageInput, SummaryMetricsInput, TreeRowInput
from ...models.project_report_source import ProjectReportSource
from ...models.summary_artifacts import SummaryArtifact
from .map import ProjectMapService
from .media import ProjectMediaService


class ProjectPageInputService:
    """Map project report sources into project page inputs."""

    def __init__(
        self,
        *,
        project_media_service: ProjectMediaService | None = None,
        project_map_service: ProjectMapService | None = None,
    ) -> None:
        self._project_media_service = project_media_service or ProjectMediaService()
        self._project_map_service = project_map_service or ProjectMapService()

    def build(
        self,
        *,
        project_source: ProjectReportSource,
        summary_artifact: SummaryArtifact,
        area_map_src: str,
    ) -> ProjectPageInput:
        media = self._project_media_service.build_media(project_source)
        project_map = self._project_map_service.build_map(
            project_source=project_source,
            fallback_map_src=area_map_src,
        )
        return ProjectPageInput(
            project_id=project_source.project_slug,
            project_name=project_source.project,
            description_markdown=project_source.project_description,
            summary_markdown=summary_artifact.summary_text,
            map_src=project_map.image_src,
            map_alt=project_map.alt,
            project_image=media.canonical_image,
            summary_metrics=SummaryMetricsInput(
                assessment_count=str(project_source.tree_count),
                tree_count=str(project_source.tree_count),
                species_count=str(project_source.species_count),
            ),
            tree_rows=[
                TreeRowInput(
                    job_number=entry.tree_id,
                    tree_doc=entry.tree_doc,
                    species_common=entry.species,
                    dbh=self._display_measure(entry.dbh, "in"),
                    height=self._display_measure(entry.height, "ft"),
                    risk_rating=entry.risk_rating,
                    main_concerns="; ".join(entry.main_concerns),
                )
                for entry in project_source.trees
            ],
            updated_at=project_source.latest_archived_at,
        )

    @staticmethod
    def _display_measure(value: float | int | None, unit: str) -> str:
        if value is None:
            return ""
        return f"{value} {unit}"
