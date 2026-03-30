"""Publish tree-linked staged artifacts into stable site asset paths."""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path

from ...models.tree_report_source import TreeGeoJsonSource, TreeImageSource, TreeReportSource
from ..geojson_publish_service import GeoJsonPublishService
from ..image_publish_service import ImagePublishService
from ..traq_pdf_publish_service import TraqPdfPublishService


class TreeArtifactPublishService:
    """Publish staged tree artifacts and return a page-safe tree source."""

    def __init__(
        self,
        *,
        geojson_publish_service: GeoJsonPublishService | None = None,
        image_publish_service: ImagePublishService | None = None,
        traq_pdf_publish_service: TraqPdfPublishService | None = None,
    ) -> None:
        self._geojson_publish_service = geojson_publish_service or GeoJsonPublishService()
        self._image_publish_service = image_publish_service or ImagePublishService()
        self._traq_pdf_publish_service = traq_pdf_publish_service or TraqPdfPublishService()

    def publish(self, *, source: TreeReportSource, docs_dir: Path) -> TreeReportSource:
        if not source.tree_id:
            raise ValueError("tree_id is required before publishing tree artifacts")

        published_geojson = None
        if source.geojson and source.geojson.geojson_src:
            geojson_asset = self._geojson_publish_service.publish(
                source_geojson_path=Path(source.geojson.geojson_src),
                tree_id=source.tree_id,
                docs_dir=docs_dir,
            )
            published_geojson = TreeGeoJsonSource(geojson_src=geojson_asset.asset_src)

        published_images = [
            TreeImageSource(
                image_src=self._image_publish_service.publish(
                    source_image_path=Path(image.image_src),
                    tree_id=source.tree_id,
                    image_index=index,
                    docs_dir=docs_dir,
                ).asset_src,
                caption=image.caption,
            )
            for index, image in enumerate(source.images, start=1)
        ]

        completed_inspection_form_url = source.completed_inspection_form_url
        if completed_inspection_form_url:
            pdf_asset = self._traq_pdf_publish_service.publish(
                source_pdf_path=Path(completed_inspection_form_url),
                tree_id=source.tree_id,
                docs_dir=docs_dir,
            )
            completed_inspection_form_url = pdf_asset.asset_src

        return replace(
            source,
            geojson=published_geojson,
            images=published_images,
            completed_inspection_form_url=completed_inspection_form_url,
        )
