"""Local publish-index models for incremental staged-job processing."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class PublishRecord:
    job_id: str
    client_revision_id: str
    tree_id: str
    project: str
    last_built_at: str = ""


@dataclass(frozen=True)
class PublishIndex:
    records: dict[str, PublishRecord] = field(default_factory=dict)


@dataclass(frozen=True)
class StagedManifestRecord:
    manifest_path: str
    job_id: str
    client_revision_id: str
    project: str


@dataclass(frozen=True)
class PublishWorkItem:
    manifest_path: str
    job_id: str
    client_revision_id: str
    project: str
    tree_id: str
    status: str


@dataclass(frozen=True)
class PublishPlan:
    new_jobs: list[PublishWorkItem] = field(default_factory=list)
    changed_jobs: list[PublishWorkItem] = field(default_factory=list)
    unchanged_jobs: list[PublishWorkItem] = field(default_factory=list)


@dataclass(frozen=True)
class PublicationExecutionResult:
    new_jobs: int
    changed_jobs: int
    unchanged_jobs: int
    tree_pages_written: int
    project_pages_written: int
    home_updated: bool
    affected_projects: list[str] = field(default_factory=list)
