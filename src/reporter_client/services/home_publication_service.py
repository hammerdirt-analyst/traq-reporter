"""Incremental home/about publication from current project sources."""

from __future__ import annotations

from pathlib import Path

from ..builders.about_page_builder import AboutPageBuilder
from ..builders.home_page_builder import HomePageBuilder
from ..models.page_inputs import AboutPageInput, HomePageInput
from ..renderers.about_renderer import AboutRenderer
from ..renderers.home_renderer import HomeRenderer
from .content_source_service import ContentSourceService
from .home_report_services import HomePageInputService, HomeReportSourceService, HomeSummaryService


class HomePublicationService:
    """Publish the home and about pages from current project sources."""

    _SITE_TITLE = "TRAQ Reporter"
    _ABOUT_TITLE = "About Hammerdirt"

    def __init__(self, *, content_dir: Path, docs_dir: Path, template_dir: Path) -> None:
        self._content_source = ContentSourceService(content_dir=content_dir)
        self._home_builder = HomePageBuilder()
        self._about_builder = AboutPageBuilder()
        self._home_renderer = HomeRenderer(template_dir=template_dir)
        self._about_renderer = AboutRenderer(template_dir=template_dir)
        self._home_page_input_service = HomePageInputService()
        self._home_report_source_service = HomeReportSourceService()
        self._home_summary_service = HomeSummaryService()
        self._docs_dir = docs_dir

    def publish(self, *, project_sources, should_write: bool) -> bool:
        if not should_write:
            return False
        stable_intro = self._content_source.read_home_summary()
        home_source = self._home_report_source_service.build(
            site_title=self._SITE_TITLE,
            project_sources=project_sources,
        )
        project_summaries = [
            project_source.project_description
            for project_source in project_sources
        ]
        from ..models.summary_contexts import HomeSummaryContext

        summary_artifact = self._home_summary_service.generate(
            HomeSummaryContext(
                home_source=home_source,
                stable_intro=stable_intro,
                project_summaries=project_summaries,
            )
        )
        home_input = self._home_page_input_service.build(
            home_source=home_source,
            stable_intro=stable_intro,
            summary_artifact=summary_artifact,
            raw_updated_at=home_source.latest_archived_at,
        )
        about_input = AboutPageInput(
            title=self._ABOUT_TITLE,
            body_markdown=self._content_source.read_about(),
            updated_at=home_source.latest_archived_at,
        )
        self._write("index.md", self._home_renderer.render({"view": self._home_builder.build(home_input)}))
        self._write("about.md", self._about_renderer.render({"view": self._about_builder.build(about_input)}))
        return True

    def _write(self, relative_path: str, rendered: str) -> None:
        target = self._docs_dir / relative_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(rendered, encoding="utf-8")
