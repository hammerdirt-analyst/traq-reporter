"""Build home page view models."""

from __future__ import annotations

from ..models.page_inputs import HomePageInput
from ..models.page_views import BreadcrumbView, HomePageView, LinkView, MapView, SummaryMetricsView
from ..services.path_service import PathService


class HomePageBuilder:
    """Build the home page view model."""

    def __init__(self) -> None:
        self._paths = PathService()

    def build(self, page_input: HomePageInput) -> HomePageView:
        current_doc = "index.md"
        return HomePageView(
            page_title=page_input.site_title,
            description_markdown=page_input.description_markdown,
            summary_markdown=page_input.summary_markdown,
            breadcrumbs=[BreadcrumbView(label="Home", href=None)],
            combined_map=MapView(
                image_href=page_input.combined_map_src,
                alt=page_input.combined_map_alt,
            ),
            summary_metrics=SummaryMetricsView(
                assessment_count=page_input.summary_metrics.assessment_count,
                tree_count=page_input.summary_metrics.tree_count,
                species_count=page_input.summary_metrics.species_count,
                project_count=page_input.summary_metrics.project_count,
            ),
            project_links=[
                LinkView(
                    label=project.project_name,
                    href=self._paths.doc_link(current_doc, project.project_doc),
                )
                for project in page_input.project_links
            ]
            + [LinkView(label="About", href=self._paths.doc_link(current_doc, "about.md"))],
            updated_at=page_input.updated_at,
        )
