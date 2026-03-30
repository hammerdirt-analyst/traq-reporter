"""Discover staged job manifests from the configured staging root."""

from __future__ import annotations

import json
from pathlib import Path

from ..models.publish_index import StagedManifestRecord


class StagedManifestService:
    """Load staged manifest headers for planning incremental publication work."""

    def discover(self, staging_root: Path) -> list[StagedManifestRecord]:
        jobs_dir = staging_root / "jobs"
        manifests = sorted(path for path in jobs_dir.glob("*/manifest.json") if path.is_file())
        return [self._load_record(path) for path in manifests]

    @staticmethod
    def _load_record(manifest_path: Path) -> StagedManifestRecord:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        return StagedManifestRecord(
            manifest_path=str(manifest_path),
            job_id=str(manifest.get("job_id", "")),
            client_revision_id=str(manifest.get("client_revision_id", "")),
            project=str(manifest.get("project", "")),
        )
