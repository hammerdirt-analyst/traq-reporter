"""Load repo-local YAML configuration for the reporter client."""

from __future__ import annotations

from pathlib import Path

import yaml

from ..models.app_config import AppConfig, PathConfig, PublishConfig, StagingConfig


class ConfigService:
    """Load and normalize application configuration."""

    def load(self, config_path: Path) -> AppConfig:
        raw = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
        base_dir = config_path.parent

        staging_root = self._resolve_path(base_dir, raw.get("staging", {}).get("root", "../server/testdata/staged_jobs_manual"))
        publish_index = self._resolve_path(base_dir, raw.get("publish", {}).get("index_path", ".state/publish_index.json"))
        examples_dir = self._resolve_path(base_dir, raw.get("paths", {}).get("examples_dir", "examples"))
        content_dir = self._resolve_path(base_dir, raw.get("paths", {}).get("content_dir", "content"))
        docs_dir = self._resolve_path(base_dir, raw.get("paths", {}).get("docs_dir", "docs"))

        return AppConfig(
            staging=StagingConfig(root=staging_root),
            publish=PublishConfig(index_path=publish_index),
            paths=PathConfig(
                examples_dir=examples_dir,
                content_dir=content_dir,
                docs_dir=docs_dir,
            ),
        )

    @staticmethod
    def _resolve_path(base_dir: Path, raw_path: str) -> Path:
        path = Path(str(raw_path))
        if path.is_absolute():
            return path
        return (base_dir / path).resolve()
