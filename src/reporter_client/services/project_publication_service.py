"""Incremental project publication from current tree sources."""

from __future__ import annotations

from pathlib import Path

from ..builders.project_page_builder import ProjectPageBuilder
from ..models.project_report_source import ProjectReportSource
from ..renderers.project_renderer import ProjectRenderer
from .content_source_service import ContentSourceService
from .project_report_services import (
    ProjectMapService,
    ProjectPageInputService,
    ProjectReportSourceService,
    ProjectSummaryService,
)


class ProjectPublicationService:
    """Publish affected project pages from the current tree source set."""

    _PROJECT_MAPS = {
        "Briarwood": "assets/maps/project_alpha_overview.svg",
        "Arboretum": "assets/maps/project_bravo_overview.svg",
        "American River": "assets/maps/project_charlie_overview.svg",
    }

    def __init__(self, *, content_dir: Path, docs_dir: Path, template_dir: Path) -> None:
        self._content_source = ContentSourceService(content_dir=content_dir)
        self._builder = ProjectPageBuilder()
        self._renderer = ProjectRenderer(template_dir=template_dir)
        self._page_input_service = ProjectPageInputService(
            project_map_service=ProjectMapService(docs_dir=docs_dir)
        )
        self._report_source_service = ProjectReportSourceService()
        self._summary_service = ProjectSummaryService()
        self._docs_dir = docs_dir

    def build_project_sources(self, tree_sources) -> list[ProjectReportSource]:
        project_descriptions = {
            "Briarwood": self._content_source.read_project_summary("briarwood"),
            "Arboretum": self._content_source.read_project_summary("arboretum"),
            "American River": self._content_source.read_project_summary("american-river"),
        }
        return self._report_source_service.build_all(
            tree_sources=tree_sources,
            project_descriptions=project_descriptions,
        )

    def publish_project_pages(self, *, project_sources: list[ProjectReportSource], target_projects: set[str]) -> int:
        written = 0
        for project_source in project_sources:
            if project_source.project not in target_projects:
                continue
            summary_artifact = self._summary_service.generate(
                self._summary_service_context(project_source)
            )
            page_input = self._page_input_service.build(
                project_source=project_source,
                summary_artifact=summary_artifact,
                area_map_src=self._PROJECT_MAPS[project_source.project],
            )
            page_view = self._builder.build(page_input)
            self._write(f"projects/{project_source.project_slug}.md", self._renderer.render({"view": page_view}))
            written += 1
        return written

    @staticmethod
    def _summary_service_context(project_source: ProjectReportSource):
        from ..models.summary_contexts import ProjectSummaryContext

        return ProjectSummaryContext(
            project_id=project_source.project_slug,
            project_name=project_source.project,
            stable_description=project_source.project_description,
            project_source=project_source,
        )

    def _write(self, relative_path: str, rendered: str) -> None:
        target = self._docs_dir / relative_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(rendered, encoding="utf-8")
