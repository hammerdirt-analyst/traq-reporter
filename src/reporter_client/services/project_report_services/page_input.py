"""Build project page inputs from project report sources."""

from __future__ import annotations

from ...models.page_inputs import ProjectPageInput, ProjectTreeCardInput, SummaryMetricsInput
from ...models.project_report_source import ProjectReportSource
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
            map_src=project_map.image_src,
            map_alt=project_map.alt,
            project_image=media.canonical_image,
            summary_metrics=SummaryMetricsInput(
                assessment_count=str(project_source.tree_count),
                tree_count=str(project_source.tree_count),
                species_count=str(project_source.species_count),
            ),
            tree_cards=[
                ProjectTreeCardInput(
                    ordinal=index,
                    job_number=entry.tree_id,
                    tree_doc=entry.tree_doc,
                    species_common=entry.species,
                    risk_rating=entry.risk_rating,
                    main_concerns="; ".join(entry.main_concerns),
                )
                for index, entry in enumerate(project_source.trees, start=1)
            ],
            updated_at=project_source.latest_archived_at,
        )
