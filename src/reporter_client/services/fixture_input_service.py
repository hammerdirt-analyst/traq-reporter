"""Load fixture JSON and authored Markdown into canonical page input objects."""

from __future__ import annotations

import json
from pathlib import Path

from ..models.home_report_source import HomeReportSource
from ..models.page_inputs import (
    AboutPageInput,
    HomePageInput,
    ProjectLinkInput,
    ProjectPageInput,
    TreePageInput,
)
from ..models.project_report_source import ProjectReportSource
from ..models.tree_report_source import GpsPoint, RiskProfile, TreeGeoJsonSource, TreeImageSource, TreeReportSource
from .content_source_service import ContentSourceService
from .home_report_services import HomePageInputService, HomeReportSourceService, HomeSummaryService
from .project_report_services import (
    ProjectPageInputService,
    ProjectReportSourceService,
    ProjectSummaryService,
)
from .tree_report_services import (
    TreeIdentityService,
    TreePageInputService,
    TreeSummaryContextBuilder,
    TreeSummaryService,
)


class FixtureInputService:
    """Build page input objects from fixture JSON and authored Markdown."""

    def __init__(self, *, examples_dir: Path, content_dir: Path) -> None:
        self._examples_dir = examples_dir
        self._content_source = ContentSourceService(content_dir=content_dir)
        self._home_report_source_service = HomeReportSourceService()
        self._home_page_input_service = HomePageInputService()
        self._home_summary_service = HomeSummaryService()
        self._project_page_input_service = ProjectPageInputService()
        self._project_report_source_service = ProjectReportSourceService()
        self._project_summary_service = ProjectSummaryService()
        self._tree_identity_service = TreeIdentityService()
        self._tree_page_input_service = TreePageInputService()
        self._tree_summary_context_builder = TreeSummaryContextBuilder()
        self._tree_summary_service = TreeSummaryService()

    def load_home_input(self) -> HomePageInput:
        raw = self._load_json("site_home.json")
        stable_intro = self._content_source.read_home_summary()
        project_sources = self._load_project_report_sources()
        home_source = self._home_report_source_service.build(
            site_title=str(raw["site_title"]),
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
            combined_map_src=str(raw["combined_map"]["image_src"]),
            combined_map_alt=str(raw["combined_map"]["image_alt"]),
            raw_updated_at=str(raw["updated_at"]),
        )

    def load_about_input(self) -> AboutPageInput:
        raw = self._load_json("about_page.json")
        return AboutPageInput(
            title=str(raw["title"]),
            body_markdown=self._content_source.read_about(),
            updated_at=str(raw["updated_at"]),
        )

    def load_project_inputs(self) -> list[ProjectPageInput]:
        home = self._load_json("site_home.json")
        area_map_by_project = {
            str(project["project_name"]): {
                "project_id": str(project["project_id"]),
                "project_doc": str(project["project_doc"]),
                "area_map_src": str(project["area_map_src"]),
            }
            for project in home["project_links"]
        }
        project_sources = self._load_project_report_sources()
        inputs: list[ProjectPageInput] = []
        for project_source in project_sources:
            project_meta = area_map_by_project[project_source.project]
            summary_artifact = self._project_summary_service.generate(
                self._build_project_summary_context(project_source)
            )
            inputs.append(
                self._project_page_input_service.build(
                    project_source=project_source,
                    summary_artifact=summary_artifact,
                    area_map_src=project_meta["area_map_src"],
                )
            )
        return inputs

    def load_tree_inputs(self) -> list[TreePageInput]:
        inputs: list[TreePageInput] = []
        for source in self.load_tree_report_sources():
            summary_context = self._tree_summary_context_builder.build(
                source=source,
                completed_payload={"form": {"data": {}}},
                transcript=source.transcript,
            )
            summary_artifact = self._tree_summary_service.generate(summary_context)
            inputs.append(self._tree_page_input_service.build(source, summary_artifact))
        return inputs

    def load_tree_report_sources(self) -> list[TreeReportSource]:
        raw_sources = self._load_json("tree_report_sources.json")
        tree_sources = [self._tree_report_source_from_dict(raw) for raw in raw_sources]
        return self._tree_identity_service.assign_tree_ids(tree_sources)

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

    def _load_json(self, name: str) -> dict:
        path = self._examples_dir / name
        return json.loads(path.read_text(encoding="utf-8"))

    def _tree_report_source_from_dict(self, raw: dict) -> TreeReportSource:
        return TreeReportSource(
            project=str(raw.get("project", "")),
            job_id=str(raw["job_id"]),
            client_revision_id=str(raw["client_revision_id"]),
            archived_at=str(raw["archived_at"]),
            species=str(raw["species"]),
            dbh=raw["dbh"],
            height=raw["height"],
            gps=GpsPoint(
                latitude=raw["gps"]["latitude"],
                longitude=raw["gps"]["longitude"],
            ),
            risk_profile=RiskProfile(
                overall_tree_risk=str(raw["risk_profile"]["overall_tree_risk"]),
                overall_residual_risk=str(raw["risk_profile"]["overall_residual_risk"]),
                recommended_inspection_interval=str(raw["risk_profile"]["recommended_inspection_interval"]),
            ),
            assessor_name=str(raw["assessor_name"]),
            tree_id=str(raw.get("tree_id", "")),
            main_concerns=[str(item) for item in raw.get("main_concerns", []) if str(item).strip()],
            images=[
                TreeImageSource(
                    image_src=str(image["image_src"]),
                    caption=str(image["caption"]),
                )
                for image in raw.get("images", [])
            ],
            geojson=(
                TreeGeoJsonSource(
                    geojson_src=str(raw["geojson"]["geojson_src"]),
                )
                if raw.get("geojson")
                else None
            ),
            transcript=str(raw["transcript"]),
            completed_inspection_form_url=str(raw["completed_inspection_form_url"]),
        )

    @staticmethod
    def _build_project_summary_context(project_source: ProjectReportSource):
        from ..models.summary_contexts import ProjectSummaryContext

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
    ):
        from ..models.summary_contexts import HomeSummaryContext

        return HomeSummaryContext(
            home_source=home_source,
            stable_intro=stable_intro,
            project_summaries=project_summaries,
        )
