"""Tests for incremental publish-state tracking."""

from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from reporter_client.models.publish_index import PublishIndex, PublishRecord
from reporter_client.services.publish_state_service import PublishStateService


class PublishStateServiceTests(unittest.TestCase):
    def test_build_plan_marks_new_changed_and_unchanged_jobs(self) -> None:
        service = PublishStateService()
        index = PublishIndex(
            records={
                "job_b62ffe12501c": PublishRecord(
                    job_id="job_b62ffe12501c",
                    client_revision_id="rev_existing",
                    tree_id="briarwood_001",
                    project="Briarwood",
                    last_built_at="2026-03-28T00:00:00Z",
                ),
                "job_existing_same": PublishRecord(
                    job_id="job_existing_same",
                    client_revision_id="rev_same",
                    tree_id="briarwood_002",
                    project="Briarwood",
                    last_built_at="2026-03-28T00:00:00Z",
                ),
            }
        )
        staged_records = [
            service.load_staged_manifest_record(self._write_manifest("job_existing_same", "rev_same", "Briarwood")),
            service.load_staged_manifest_record(self._write_manifest("job_b62ffe12501c", "rev_changed", "Briarwood")),
            service.load_staged_manifest_record(self._write_manifest("job_new_001", "rev_new", "Briarwood")),
        ]

        plan = service.build_plan(staged_records=staged_records, index=index)

        self.assertEqual([item.job_id for item in plan.new_jobs], ["job_new_001"])
        self.assertEqual(plan.new_jobs[0].tree_id, "briarwood_003")
        self.assertEqual([item.job_id for item in plan.changed_jobs], ["job_b62ffe12501c"])
        self.assertEqual(plan.changed_jobs[0].tree_id, "briarwood_001")
        self.assertEqual([item.job_id for item in plan.unchanged_jobs], ["job_existing_same"])
        self.assertEqual(plan.unchanged_jobs[0].tree_id, "briarwood_002")

    def test_apply_plan_updates_index_records(self) -> None:
        service = PublishStateService()
        index = PublishIndex()
        staged_record = service.load_staged_manifest_record(self._write_manifest("job_new_001", "rev_new", "Arboretum"))
        plan = service.build_plan(staged_records=[staged_record], index=index)

        updated = service.apply_plan(index=index, plan=plan, built_at="2026-03-28T18:00:00Z")

        self.assertIn("job_new_001", updated.records)
        self.assertEqual(updated.records["job_new_001"].tree_id, "arboretum_001")
        self.assertEqual(updated.records["job_new_001"].last_built_at, "2026-03-28T18:00:00Z")

    def test_load_and_save_index_round_trip(self) -> None:
        service = PublishStateService()
        index = PublishIndex(
            records={
                "job_1": PublishRecord(
                    job_id="job_1",
                    client_revision_id="rev_1",
                    tree_id="briarwood_001",
                    project="Briarwood",
                    last_built_at="2026-03-28T18:00:00Z",
                )
            }
        )
        with tempfile.TemporaryDirectory() as tmp_dir:
            index_path = Path(tmp_dir) / "publish_index.json"
            service.save_index(index_path, index)
            loaded = service.load_index(index_path)

        self.assertEqual(loaded, index)

    def _write_manifest(self, job_id: str, client_revision_id: str, project: str) -> Path:
        tmp_dir = Path(tempfile.mkdtemp())
        manifest_path = tmp_dir / "manifest.json"
        manifest_path.write_text(
            json.dumps(
                {
                    "job_id": job_id,
                    "client_revision_id": client_revision_id,
                    "project": project,
                }
            ),
            encoding="utf-8",
        )
        return manifest_path


if __name__ == "__main__":
    unittest.main()
