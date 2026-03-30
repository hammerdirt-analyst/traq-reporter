"""Build tree page inputs from canonical tree sources."""

from __future__ import annotations

from ...models.page_inputs import MapAssetInput, TreePageInput
from ...models.summary_artifacts import SummaryArtifact
from ...models.tree_report_source import TreeReportSource
from ..project_naming import project_slug
from .map import TreeMapService
from .media import TreeMediaService


class TreePageInputService:
    """Map canonical tree sources into tree page inputs."""

    def __init__(
        self,
        *,
        tree_map_service: TreeMapService | None = None,
        tree_media_service: TreeMediaService | None = None,
    ) -> None:
        self._tree_map_service = tree_map_service or TreeMapService()
        self._tree_media_service = tree_media_service or TreeMediaService()

    def build(self, source: TreeReportSource, summary_artifact: SummaryArtifact) -> TreePageInput:
        tree_map = self._tree_map_service.build_map(source)
        media = self._tree_media_service.build_media(source)
        slug = project_slug(source.project)
        return TreePageInput(
            tree_doc=f"projects/{slug}/trees/{source.tree_id}.md",
            project_name=source.project,
            project_doc=f"projects/{slug}.md",
            tree_name=str(source.species),
            title_text=f"{source.dbh} in DBH | {source.height} ft tall",
            facts=[
                ("Overall Tree Risk", str(source.risk_profile.overall_tree_risk)),
                ("Residual Risk", str(source.risk_profile.overall_residual_risk)),
                ("Inspection Interval", str(source.risk_profile.recommended_inspection_interval)),
            ],
            tree_map=MapAssetInput(image_src=tree_map.image_src, alt=tree_map.alt),
            image_gallery=media.gallery_images,
            summary_text=summary_artifact.summary_text,
            narrative_paragraphs=list(summary_artifact.narrative_blocks),
            completed_inspection_form_url=str(source.completed_inspection_form_url),
            updated_at=str(source.archived_at),
        )
