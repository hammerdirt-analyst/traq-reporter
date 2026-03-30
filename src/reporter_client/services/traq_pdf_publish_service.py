"""Publish staged TRAQ form PDFs into stable site asset paths."""

from __future__ import annotations

import shutil
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class PublishedTraqPdfAsset:
    asset_path: Path
    asset_src: str


class TraqPdfPublishService:
    """Copy staged TRAQ PDFs into the docs asset tree."""

    def publish(self, *, source_pdf_path: Path, tree_id: str, docs_dir: Path) -> PublishedTraqPdfAsset:
        target_dir = docs_dir / "assets" / "traq-forms"
        target_dir.mkdir(parents=True, exist_ok=True)
        target_path = target_dir / f"{tree_id}.pdf"
        shutil.copyfile(source_pdf_path, target_path)
        return PublishedTraqPdfAsset(
            asset_path=target_path,
            asset_src=f"assets/traq-forms/{tree_id}.pdf",
        )
