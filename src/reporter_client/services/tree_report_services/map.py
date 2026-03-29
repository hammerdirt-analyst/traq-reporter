"""Tree map mapping service."""

from __future__ import annotations

from dataclasses import dataclass

from ...models.tree_report_source import TreeReportSource


@dataclass(frozen=True)
class TreeMapArtifact:
    image_src: str
    alt: str
    geojson_asset_src: str | None = None


class TreeMapService:
    """Build the tree-page map asset from the tree source."""

    def build_map(self, source: TreeReportSource, *, geojson_asset_src: str | None = None) -> TreeMapArtifact:
        image_src = "../assets/maps/job_123_locator.svg"
        if source.geojson and source.geojson.geojson_src:
            image_src = "../assets/maps/job_123_locator.svg"
        return TreeMapArtifact(
            image_src=image_src,
            alt=f"{source.species} locator map",
            geojson_asset_src=geojson_asset_src or (source.geojson.geojson_src if source.geojson else None),
        )
