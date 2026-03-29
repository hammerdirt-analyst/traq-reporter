"""Publish staged GeoJSON artifacts into stable site asset paths."""

from __future__ import annotations

import shutil
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class PublishedGeoJsonAsset:
    asset_path: Path
    asset_src: str


class GeoJsonPublishService:
    """Copy source GeoJSON files into the docs asset tree."""

    def publish(self, *, source_geojson_path: Path, tree_id: str, docs_dir: Path) -> PublishedGeoJsonAsset:
        target_dir = docs_dir / "assets" / "geojson"
        target_dir.mkdir(parents=True, exist_ok=True)
        target_path = target_dir / f"{tree_id}.geojson"
        shutil.copyfile(source_geojson_path, target_path)
        return PublishedGeoJsonAsset(
            asset_path=target_path,
            asset_src=f"assets/geojson/{tree_id}.geojson",
        )
