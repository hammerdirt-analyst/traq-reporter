"""Publish staged tree image artifacts into stable site asset paths."""

from __future__ import annotations

import shutil
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class PublishedImageAsset:
    asset_path: Path
    asset_src: str


class ImagePublishService:
    """Copy source images into the docs asset tree."""

    def publish(self, *, source_image_path: Path, tree_id: str, image_index: int, docs_dir: Path) -> PublishedImageAsset:
        suffix = source_image_path.suffix or ".jpg"
        target_dir = docs_dir / "assets" / "images" / tree_id
        target_dir.mkdir(parents=True, exist_ok=True)
        target_path = target_dir / f"image_{image_index:02d}{suffix}"
        shutil.copyfile(source_image_path, target_path)
        return PublishedImageAsset(
            asset_path=target_path,
            asset_src=f"assets/images/{tree_id}/{target_path.name}",
        )
