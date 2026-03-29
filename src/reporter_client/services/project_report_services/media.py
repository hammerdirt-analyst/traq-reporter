"""Project media mapping service."""

from __future__ import annotations

from dataclasses import dataclass

from ...models.page_inputs import ImageAssetInput
from ...models.project_report_source import ProjectReportSource


@dataclass(frozen=True)
class ProjectMediaArtifact:
    canonical_image: ImageAssetInput | None


class ProjectMediaService:
    """Select the canonical project image from project tree entries."""

    def build_media(self, project_source: ProjectReportSource) -> ProjectMediaArtifact:
        entry = next(
            (tree for tree in project_source.trees if tree.canonical_image_src),
            project_source.trees[0] if project_source.trees else None,
        )
        if not entry or not entry.canonical_image_src:
            return ProjectMediaArtifact(canonical_image=None)
        return ProjectMediaArtifact(
            canonical_image=ImageAssetInput(
                image_src=entry.canonical_image_src,
                caption=entry.canonical_image_caption or "project_page_input.project_image.caption",
            )
        )
