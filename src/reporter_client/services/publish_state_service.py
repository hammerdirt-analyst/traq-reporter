"""Incremental publish-state tracking for staged job bundles."""

from __future__ import annotations

import json
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path

from ..models.publish_index import PublishIndex, PublishPlan, PublishRecord, PublishWorkItem, StagedManifestRecord
from .project_naming import project_slug


class PublishStateService:
    """Track processed jobs and compute incremental publish work."""

    def load_index(self, index_path: Path) -> PublishIndex:
        if not index_path.exists():
            return PublishIndex()
        raw = json.loads(index_path.read_text(encoding="utf-8"))
        return PublishIndex(
            records={
                str(job_id): PublishRecord(
                    job_id=str(record.get("job_id", job_id)),
                    client_revision_id=str(record.get("client_revision_id", "")),
                    tree_id=str(record.get("tree_id", "")),
                    project=str(record.get("project", "")),
                    last_built_at=str(record.get("last_built_at", "")),
                )
                for job_id, record in raw.get("records", {}).items()
            }
        )

    def save_index(self, index_path: Path, index: PublishIndex) -> None:
        index_path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "records": {
                job_id: asdict(record)
                for job_id, record in sorted(index.records.items())
            }
        }
        index_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def load_staged_manifest_record(self, manifest_path: Path) -> StagedManifestRecord:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        return StagedManifestRecord(
            manifest_path=str(manifest_path),
            job_id=str(manifest.get("job_id", "")),
            client_revision_id=str(manifest.get("client_revision_id", "")),
            project=str(manifest.get("project", "")),
        )

    def build_plan(self, *, staged_records: list[StagedManifestRecord], index: PublishIndex) -> PublishPlan:
        new_jobs: list[PublishWorkItem] = []
        changed_jobs: list[PublishWorkItem] = []
        unchanged_jobs: list[PublishWorkItem] = []

        project_counters = self._project_counters(index)

        for staged_record in sorted(staged_records, key=lambda item: (item.project, item.job_id)):
            existing = index.records.get(staged_record.job_id)
            if existing is not None:
                tree_id = existing.tree_id
                status = "unchanged" if existing.client_revision_id == staged_record.client_revision_id else "changed"
            else:
                tree_id = self._next_tree_id(staged_record.project, project_counters)
                status = "new"

            item = PublishWorkItem(
                manifest_path=staged_record.manifest_path,
                job_id=staged_record.job_id,
                client_revision_id=staged_record.client_revision_id,
                project=staged_record.project,
                tree_id=tree_id,
                status=status,
            )
            if status == "new":
                new_jobs.append(item)
            elif status == "changed":
                changed_jobs.append(item)
            else:
                unchanged_jobs.append(item)

        return PublishPlan(
            new_jobs=new_jobs,
            changed_jobs=changed_jobs,
            unchanged_jobs=unchanged_jobs,
        )

    def apply_plan(self, *, index: PublishIndex, plan: PublishPlan, built_at: str | None = None) -> PublishIndex:
        timestamp = built_at or datetime.now(timezone.utc).isoformat()
        updated_records = dict(index.records)
        for item in [*plan.new_jobs, *plan.changed_jobs]:
            updated_records[item.job_id] = PublishRecord(
                job_id=item.job_id,
                client_revision_id=item.client_revision_id,
                tree_id=item.tree_id,
                project=item.project,
                last_built_at=timestamp,
            )
        return PublishIndex(records=updated_records)

    def _project_counters(self, index: PublishIndex) -> dict[str, int]:
        counters: dict[str, int] = {}
        for record in index.records.values():
            slug = project_slug(record.project)
            prefix = f"{slug}_"
            if not record.tree_id.startswith(prefix):
                continue
            suffix = record.tree_id.removeprefix(prefix)
            if not suffix.isdigit():
                continue
            counters[slug] = max(counters.get(slug, 0), int(suffix))
        return counters

    def _next_tree_id(self, project: str, project_counters: dict[str, int]) -> str:
        slug = project_slug(project)
        next_value = project_counters.get(slug, 0) + 1
        project_counters[slug] = next_value
        return f"{slug}_{next_value:03d}"
