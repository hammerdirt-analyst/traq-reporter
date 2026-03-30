"""Build project page view models."""

from __future__ import annotations

from ..models.page_inputs import ProjectPageInput
from ..models.page_views import (
    BreadcrumbView,
    ImageAssetView,
    MapView,
    ProjectTreeCardView,
    ProjectPageView,
    SummaryMetricsView,
)
from ..services.path_service import PathService


class ProjectPageBuilder:
    """Build the project page view model."""

    def __init__(self) -> None:
        self._paths = PathService()

    def build(self, page_input: ProjectPageInput) -> ProjectPageView:
        current_doc = f"projects/{page_input.project_id}.md"
        return ProjectPageView(
            page_title=page_input.project_name,
            description_markdown=page_input.description_markdown,
            summary_markdown=page_input.summary_markdown,
            breadcrumbs=[
                BreadcrumbView(label="Home", href="/reporter-client/"),
                BreadcrumbView(label=page_input.project_name, href=None),
            ],
            project_map=MapView(
                image_href=self._paths.asset_link(current_doc, page_input.map_src),
                alt=page_input.map_alt,
            ),
            project_image=(
                ImageAssetView(
                    image_href=self._paths.asset_link(current_doc, page_input.project_image.image_src),
                    caption=page_input.project_image.caption,
                )
                if page_input.project_image
                else None
            ),
            summary_metrics=SummaryMetricsView(
                assessment_count=page_input.summary_metrics.assessment_count,
                tree_count=page_input.summary_metrics.tree_count,
                species_count=page_input.summary_metrics.species_count,
            ),
            tree_cards=[
                ProjectTreeCardView(
                    ordinal=card.ordinal,
                    job_number=card.job_number,
                    tree_href=self._paths.doc_link(current_doc, card.tree_doc),
                    species_common=card.species_common,
                    risk_rating=card.risk_rating,
                    main_concerns=card.main_concerns,
                )
                for card in page_input.tree_cards
            ],
            updated_at=page_input.updated_at,
        )
