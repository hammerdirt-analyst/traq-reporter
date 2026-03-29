"""Load staged job bundles into canonical tree reporting sources."""

from __future__ import annotations

import json
from pathlib import Path

from .report_source import TreeReportSourceService
from ...models.tree_report_source import TreeReportSource


class StagedTreeBundleService:
    """Adapt a staged job bundle manifest into a canonical tree report source."""

    def build_from_manifest(self, manifest_path: Path) -> TreeReportSource:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        bundle_dir = manifest_path.parent
        completed_payload = self._load_completed_payload(bundle_dir, manifest)
        transcript = str(completed_payload.get("transcript", ""))
        return TreeReportSourceService(
            completed_form_url_resolver=lambda payload: self._resolve_completed_form_path(bundle_dir, manifest)
        ).build(completed_payload, transcript=transcript)

    def _load_completed_payload(self, bundle_dir: Path, manifest: dict) -> dict:
        final_json_path = self._resolve_bundle_path(bundle_dir, manifest.get("artifacts", {}).get("final_json"))
        completed_payload = json.loads(final_json_path.read_text(encoding="utf-8"))
        completed_payload["project"] = str(manifest.get("project", completed_payload.get("project", "")))
        completed_payload["client_revision_id"] = str(
            manifest.get("client_revision_id", completed_payload.get("client_revision_id", ""))
        )
        completed_payload["archived_at"] = str(manifest.get("archived_at", completed_payload.get("archived_at", "")))
        completed_payload["report_images"] = [
            {
                "path": str(self._resolve_bundle_path(bundle_dir, image.get("source_path"))),
                "caption": str(image.get("caption", "")),
            }
            for image in manifest.get("images", [])
        ]
        geojson_path = self._resolve_bundle_path(bundle_dir, manifest.get("artifacts", {}).get("final_geojson"))
        if geojson_path:
            completed_payload["geojson_url"] = str(geojson_path)
        return completed_payload

    def _resolve_completed_form_path(self, bundle_dir: Path, manifest: dict) -> str:
        return str(self._resolve_bundle_path(bundle_dir, manifest.get("artifacts", {}).get("traq_pdf")) or "")

    @staticmethod
    def _resolve_bundle_path(bundle_dir: Path, raw_path: object) -> Path | None:
        path_text = str(raw_path or "").strip()
        if not path_text:
            return None
        path = Path(path_text)
        if path.is_absolute():
            return path
        return (bundle_dir / path).resolve()
