"""Application configuration models."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class StagingConfig:
    root: Path


@dataclass(frozen=True)
class PublishConfig:
    index_path: Path


@dataclass(frozen=True)
class PathConfig:
    examples_dir: Path
    content_dir: Path
    docs_dir: Path


@dataclass(frozen=True)
class AppConfig:
    staging: StagingConfig
    publish: PublishConfig
    paths: PathConfig
