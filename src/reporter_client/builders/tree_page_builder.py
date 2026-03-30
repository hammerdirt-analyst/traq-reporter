"""Build tree page view models."""

from __future__ import annotations

from ..models.page_inputs import TreePageInput
from ..models.page_views import BreadcrumbView, ImageAssetView, LinkView, MapView, TreePageView
from ..services.media_rules import is_lead_tree_caption
from ..services.path_service import PathService


class TreePageBuilder:
    """Build the tree page view model."""

    def __init__(self) -> None:
        self._paths = PathService()

    def build(self, page_input: TreePageInput) -> TreePageView:
        current_doc = page_input.tree_doc
        project_href = self._paths.doc_link(current_doc, page_input.project_doc)
        facts = [(label, value if label != "Project" else f"[{value}]({project_href})") for label, value in page_input.facts]
        ordered_gallery = self._ordered_gallery(page_input=page_input, current_doc=current_doc)
        return TreePageView(
            page_title=page_input.tree_name,
            title_text=page_input.title_text,
            breadcrumbs=[
                BreadcrumbView(label="Home", href="/reporter-client/"),
                BreadcrumbView(label=page_input.project_name, href=project_href),
                BreadcrumbView(label=page_input.tree_name, href=None),
            ],
            facts=facts,
            tree_map=MapView(
                image_href=self._paths.asset_link(current_doc, page_input.tree_map.image_src),
                alt=page_input.tree_map.alt,
            ),
            image_gallery=ordered_gallery,
            summary_text=page_input.summary_text,
            narrative_paragraphs=list(page_input.narrative_paragraphs),
            completed_inspection_form_link=LinkView(
                label="Completed inspection form",
                href=page_input.completed_inspection_form_url,
            ),
            updated_at=page_input.updated_at,
        )

    def _ordered_gallery(self, *, page_input: TreePageInput, current_doc: str) -> list[ImageAssetView]:
        rendered_images = [
            ImageAssetView(
                image_href=self._paths.asset_link(current_doc, image.image_src),
                caption=image.caption,
            )
            for image in page_input.image_gallery
        ]
        if not rendered_images:
            return []

        lead_index = next(
            (index for index, image in enumerate(rendered_images) if is_lead_tree_caption(image.caption)),
            0,
        )
        lead_image = rendered_images[lead_index]
        remaining_images = [image for index, image in enumerate(rendered_images) if index != lead_index]
        return [lead_image, *remaining_images]
