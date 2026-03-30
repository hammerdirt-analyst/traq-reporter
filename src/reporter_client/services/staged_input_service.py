"""Build canonical page inputs from staged job bundles and authored content."""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path

from ..models.home_report_source import HomeReportSource
from ..models.page_inputs import AboutPageInput, HomePageInput, ProjectPageInput, TreePageInput
from ..models.project_report_source import ProjectReportSource
from ..models.summary_contexts import HomeSummaryContext, ProjectSummaryContext
from .content_source_service import ContentSourceService
from .home_report_services import HomePageInputService, HomeReportSourceService, HomeSummaryService
from .project_naming import project_slug
from .project_report_services import (
    ProjectMapService,
    ProjectMediaService,
    ProjectPageInputService,
    ProjectReportSourceService,
    ProjectSummaryService,
)
from .tree_report_services import (
    StagedTreeBundleService,
    TreeArtifactPublishService,
    TreeIdentityService,
    TreeMapService,
    TreePageInputService,
    TreeSummaryContextBuilder,
    TreeSummaryService,
)


class StagedInputService:
    """Build page input objects from staged job bundles and authored content."""

    _SITE_TITLE = "TRAQ Reporter"
    _ABOUT_TITLE = "About Hammerdirt"
    _HOME_MAP_SRC = "assets/maps/all-projects-overview.svg"
    _HOME_MAP_ALT = "Combined assessment map"
    _PROJECT_MAPS = {
        "Briarwood": "assets/maps/project_alpha_overview.svg",
        "Arboretum": "assets/maps/project_bravo_overview.svg",
        "American River": "assets/maps/project_charlie_overview.svg",
    }

    def __init__(self, *, staging_root: Path, content_dir: Path, docs_dir: Path) -> None:
        self._staging_root = staging_root
        self._docs_dir = docs_dir
        self._content_source = ContentSourceService(content_dir=content_dir)
        self._home_report_source_service = HomeReportSourceService()
        self._home_page_input_service = HomePageInputService()
        self._home_summary_service = HomeSummaryService()
        self._project_page_input_service = ProjectPageInputService(
            project_media_service=ProjectMediaService(docs_dir=docs_dir),
            project_map_service=ProjectMapService(docs_dir=docs_dir)
        )
        self._project_report_source_service = ProjectReportSourceService()
        self._project_summary_service = ProjectSummaryService()
        self._staged_tree_bundle_service = StagedTreeBundleService()
        self._tree_artifact_publish_service = TreeArtifactPublishService()
        self._tree_identity_service = TreeIdentityService()
        self._tree_page_input_service = TreePageInputService(
            tree_map_service=TreeMapService(docs_dir=docs_dir)
        )
        self._tree_summary_context_builder = TreeSummaryContextBuilder()
        self._tree_summary_service = TreeSummaryService()

    def load_home_input(self) -> HomePageInput:
        stable_intro = self._content_source.read_home_summary()
        project_sources = self._load_project_report_sources()
        home_source = self._home_report_source_service.build(
            site_title=self._SITE_TITLE,
            project_sources=project_sources,
        )
        project_summaries = [
            self._project_summary_service.generate(self._build_project_summary_context(project_source)).summary_text
            for project_source in project_sources
        ]
        home_summary = self._home_summary_service.generate(
            self._build_home_summary_context(home_source, stable_intro, project_summaries)
        )
        return self._home_page_input_service.build(
            home_source=home_source,
            stable_intro=stable_intro,
            summary_artifact=home_summary,
            combined_map_src=self._HOME_MAP_SRC,
            combined_map_alt=self._HOME_MAP_ALT,
            raw_updated_at=home_source.latest_archived_at,
        )

    def load_about_input(self) -> AboutPageInput:
        latest_updated_at = self._latest_archived_at()
        return AboutPageInput(
            title=self._ABOUT_TITLE,
            body_markdown=self._content_source.read_about(),
            updated_at=latest_updated_at,
        )

    def load_project_inputs(self) -> list[ProjectPageInput]:
        project_sources = self._load_project_report_sources()
        inputs: list[ProjectPageInput] = []
        for project_source in project_sources:
            summary_artifact = self._project_summary_service.generate(
                self._build_project_summary_context(project_source)
            )
            inputs.append(
                self._project_page_input_service.build(
                    project_source=project_source,
                    summary_artifact=summary_artifact,
                    area_map_src=self._PROJECT_MAPS[project_source.project],
                )
            )
        return inputs

    def load_tree_inputs(self) -> list[TreePageInput]:
        inputs: list[TreePageInput] = []
        for record in self._load_staged_tree_records():
            summary_context = self._tree_summary_context_builder.build(
                source=record.source,
                completed_payload=record.completed_payload,
                transcript=record.source.transcript,
            )
            summary_artifact = self._tree_summary_service.generate(summary_context)
            inputs.append(self._tree_page_input_service.build(record.source, summary_artifact))
        return inputs

    def load_tree_report_sources(self):
        return [record.source for record in self._load_staged_tree_records()]

    def _load_project_report_sources(self) -> list[ProjectReportSource]:
        project_descriptions = {
            "Briarwood": self._content_source.read_project_summary("briarwood"),
            "Arboretum": self._content_source.read_project_summary("arboretum"),
            "American River": self._content_source.read_project_summary("american-river"),
        }
        return self._project_report_source_service.build_all(
            tree_sources=self.load_tree_report_sources(),
            project_descriptions=project_descriptions,
        )

    def _load_staged_tree_records(self):
        provisional_records = [
            self._staged_tree_bundle_service.build_record_from_manifest(manifest_path)
            for manifest_path in self._manifest_paths()
        ]
        identified_sources = self._tree_identity_service.assign_tree_ids([record.source for record in provisional_records])
        payload_by_job_id = {record.source.job_id: record.completed_payload for record in provisional_records}
        published_sources = [
            self._tree_artifact_publish_service.publish(source=source, docs_dir=self._docs_dir)
            for source in identified_sources
        ]
        return [
            replace(record, source=source)
            for source in published_sources
            for record in provisional_records
            if record.source.job_id == source.job_id
        ]

    def _manifest_paths(self) -> list[Path]:
        jobs_dir = self._staging_root / "jobs"
        return sorted(path for path in jobs_dir.glob("*/manifest.json") if path.is_file())

    def _latest_archived_at(self) -> str:
        sources = self.load_tree_report_sources()
        return max((source.archived_at for source in sources), default="")

    @staticmethod
    def _build_project_summary_context(project_source: ProjectReportSource) -> ProjectSummaryContext:
        return ProjectSummaryContext(
            project_id=project_source.project_slug,
            project_name=project_source.project,
            stable_description=project_source.project_description,
            project_source=project_source,
        )

    @staticmethod
    def _build_home_summary_context(
        home_source: HomeReportSource,
        stable_intro: str,
        project_summaries: list[str],
    ) -> HomeSummaryContext:
        return HomeSummaryContext(
            home_source=home_source,
            stable_intro=stable_intro,
            project_summaries=project_summaries,
        )
