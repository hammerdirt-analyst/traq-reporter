"""Build home page inputs from home report sources."""

from __future__ import annotations

from ...models.home_report_source import HomeReportSource
from ...models.page_inputs import HomePageInput, ProjectLinkInput, SummaryMetricsInput


class HomePageInputService:
    """Map home report sources into home page inputs."""

    def build(
        self,
        *,
        home_source: HomeReportSource,
        stable_intro: str,
        raw_updated_at: str,
    ) -> HomePageInput:
        return HomePageInput(
            site_title=home_source.site_title,
            description_markdown=stable_intro,
            summary_metrics=SummaryMetricsInput(
                assessment_count=str(home_source.tree_count),
                tree_count=str(home_source.tree_count),
                species_count=str(home_source.species_count),
                project_count=str(home_source.project_count),
            ),
            project_links=[
                ProjectLinkInput(
                    project_id=project.project_slug,
                    project_name=project.project_name,
                    project_doc=project.project_doc,
                )
                for project in home_source.projects
            ],
            updated_at=home_source.latest_archived_at or raw_updated_at,
        )
