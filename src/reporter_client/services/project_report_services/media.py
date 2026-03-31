"""Project media mapping service."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from ...models.page_inputs import ImageAssetInput
from ...models.project_report_source import ProjectReportSource
from ..project_naming import project_slug


@dataclass(frozen=True)
class ProjectMediaArtifact:
    canonical_image: ImageAssetInput | None


class ProjectMediaService:
    """Resolve the authored project image from the project image asset directory."""

    _SUPPORTED_SUFFIXES = (".jpg", ".jpeg", ".png", ".svg", ".webp")

    def __init__(self, *, docs_dir: Path | None = None, content_dir: Path | None = None) -> None:
        self._docs_dir = docs_dir
        self._content_dir = content_dir

    def build_media(self, project_source: ProjectReportSource) -> ProjectMediaArtifact:
        image_src = self._resolve_project_image_src(project_source.project)
        if not image_src:
            return ProjectMediaArtifact(canonical_image=None)
        metadata = self._load_project_image_metadata(project_source.project)
        return ProjectMediaArtifact(
            canonical_image=ImageAssetInput(
                image_src=image_src,
                caption=metadata.get("caption") or f"{project_source.project} project image",
            )
        )

    def _resolve_project_image_src(self, project_name: str) -> str | None:
        slug = project_slug(project_name)
        if self._docs_dir is None:
            return f"assets/project-images/{slug}.svg"
        for suffix in self._SUPPORTED_SUFFIXES:
            candidate = self._docs_dir / "assets" / "project-images" / f"{slug}{suffix}"
            if candidate.exists():
                return f"assets/project-images/{slug}{suffix}"
        return f"assets/project-images/{slug}.svg"

    def _load_project_image_metadata(self, project_name: str) -> dict[str, str]:
        if self._content_dir is None:
            return {}
        slug = project_slug(project_name)
        metadata_path = self._content_dir / "project-images" / f"{slug}.json"
        if not metadata_path.exists():
            return {}
        raw = json.loads(metadata_path.read_text(encoding="utf-8"))
        return {
            "caption": str(raw.get("caption", "")).strip(),
            "alt": str(raw.get("alt", "")).strip(),
        }
