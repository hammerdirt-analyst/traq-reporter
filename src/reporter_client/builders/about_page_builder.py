"""Build about page view models."""

from __future__ import annotations

from ..models.page_inputs import AboutPageInput
from ..models.page_views import AboutPageView, BreadcrumbView


class AboutPageBuilder:
    """Build the About page view model."""

    def build(self, page_input: AboutPageInput) -> AboutPageView:
        return AboutPageView(
            page_title=page_input.title,
            breadcrumbs=[
                BreadcrumbView(label="Home", href="/reporter-client/"),
                BreadcrumbView(label=page_input.title, href=None),
            ],
            body_markdown=page_input.body_markdown,
            updated_at=page_input.updated_at,
        )
