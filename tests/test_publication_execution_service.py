"""Tests for incremental staged publication execution."""

from __future__ import annotations

import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from reporter_client.services.publication_execution_service import PublicationExecutionService


class PublicationExecutionServiceTests(unittest.TestCase):
    def test_run_processes_new_jobs_then_skips_unchanged_jobs(self) -> None:
        repo_root = Path(__file__).resolve().parent.parent
        with TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            docs_dir = root / "docs"
            index_path = root / ".state" / "publish_index.json"
            service = PublicationExecutionService(
                staging_root=repo_root.parent / "server" / "staging",
                content_dir=repo_root / "content",
                docs_dir=docs_dir,
                index_path=index_path,
            )

            first = service.run()
            second = service.run()

            self.assertEqual(first.new_jobs, 10)
            self.assertEqual(first.changed_jobs, 0)
            self.assertEqual(first.unchanged_jobs, 0)
            self.assertEqual(first.tree_pages_written, 10)
            self.assertEqual(first.project_pages_written, 3)
            self.assertTrue(first.home_updated)
            self.assertEqual(second.new_jobs, 0)
            self.assertEqual(second.changed_jobs, 0)
            self.assertEqual(second.unchanged_jobs, 10)
            self.assertEqual(second.tree_pages_written, 0)
            self.assertEqual(second.project_pages_written, 0)
            self.assertFalse(second.home_updated)
            self.assertTrue((docs_dir / "projects" / "briarwood" / "trees" / "briarwood_001.md").exists())
            self.assertTrue(index_path.exists())

    def test_run_processes_changed_revision_only(self) -> None:
        repo_root = Path(__file__).resolve().parent.parent
        with TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            staging_root = root / "staging"
            self._copy_tree(repo_root.parent / "server" / "staging", staging_root)
            docs_dir = root / "docs"
            index_path = root / ".state" / "publish_index.json"
            service = PublicationExecutionService(
                staging_root=staging_root,
                content_dir=repo_root / "content",
                docs_dir=docs_dir,
                index_path=index_path,
            )
            first = service.run()
            manifest_path = staging_root / "jobs" / "J0003" / "manifest.json"
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest["client_revision_id"] = f'{manifest["client_revision_id"]}-updated'
            manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

            second = service.run()

            self.assertEqual(first.new_jobs, 10)
            self.assertEqual(second.new_jobs, 0)
            self.assertEqual(second.changed_jobs, 1)
            self.assertEqual(second.unchanged_jobs, 9)
            self.assertEqual(second.tree_pages_written, 1)
            self.assertEqual(second.project_pages_written, 1)
            self.assertTrue(second.home_updated)
            self.assertEqual(second.affected_projects, ["Briarwood"])

    def _copy_tree(self, source: Path, destination: Path) -> None:
        for path in source.rglob("*"):
            relative = path.relative_to(source)
            target = destination / relative
            if path.is_dir():
                target.mkdir(parents=True, exist_ok=True)
            else:
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(path.read_bytes())
