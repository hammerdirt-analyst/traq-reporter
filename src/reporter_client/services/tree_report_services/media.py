"""Tree media mapping service."""

from __future__ import annotations

from dataclasses import dataclass

from ...models.page_inputs import ImageAssetInput
from ...models.tree_report_source import TreeReportSource
from ..media_rules import is_lead_tree_caption


@dataclass(frozen=True)
class TreeMediaArtifact:
    lead_image: ImageAssetInput | None
    gallery_images: list[ImageAssetInput]


class TreeMediaService:
    """Map tree-source images into page-ready image assets."""

    def build_media(self, source: TreeReportSource) -> TreeMediaArtifact:
        images = [
            ImageAssetInput(
                image_src=image.image_src,
                caption=image.caption,
            )
            for image in source.images
        ]
        if not images:
            return TreeMediaArtifact(lead_image=None, gallery_images=[])
        lead_index = next(
            (
                index
                for index, image in enumerate(images)
                if is_lead_tree_caption(image.caption)
            ),
            0,
        )
        lead_image = images[lead_index]
        gallery_images = [lead_image, *[image for index, image in enumerate(images) if index != lead_index]]
        return TreeMediaArtifact(lead_image=lead_image, gallery_images=gallery_images)
