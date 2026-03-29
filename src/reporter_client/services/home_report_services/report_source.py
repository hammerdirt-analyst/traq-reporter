"""Build home reporting sources from project reporting sources."""

from __future__ import annotations

from ...models.home_report_source import HomeProjectEntry, HomeReportSource
from ...models.project_report_source import ProjectReportSource


class HomeReportSourceService:
    """Aggregate project sources into the home reporting source."""

    def build(self, *, site_title: str, project_sources: list[ProjectReportSource]) -> HomeReportSource:
        earliest_dates = [project.earliest_archived_at for project in project_sources if project.earliest_archived_at]
        latest_dates = [project.latest_archived_at for project in project_sources if project.latest_archived_at]
        all_species = {
            entry.species
            for project in project_sources
            for entry in project.trees
        }
        return HomeReportSource(
            site_title=site_title,
            project_count=len(project_sources),
            tree_count=sum(project.tree_count for project in project_sources),
            species_count=len(all_species),
            earliest_archived_at=min(earliest_dates) if earliest_dates else "",
            latest_archived_at=max(latest_dates) if latest_dates else "",
            projects=[
                HomeProjectEntry(
                    project_name=project.project,
                    project_slug=project.project_slug,
                    project_doc=f"projects/{project.project_slug}.md",
                    tree_count=project.tree_count,
                    species_count=project.species_count,
                )
                for project in project_sources
            ],
        )
