"""Tests for reporter YAML configuration loading."""

from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from reporter_client.services.config_service import ConfigService


class ConfigServiceTests(unittest.TestCase):
    def test_load_resolves_paths_relative_to_config_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            config_dir = Path(tmp_dir)
            config_path = config_dir / "reporter_client.yaml"
            config_path.write_text(
                "\n".join(
                    [
                        "staging:",
                        "  root: ../server/testdata/staged_jobs_manual",
                        "publish:",
                        "  index_path: .state/publish_index.json",
                        "paths:",
                        "  examples_dir: examples",
                        "  content_dir: content",
                        "  docs_dir: docs",
                    ]
                ),
                encoding="utf-8",
            )

            config = ConfigService().load(config_path)

            self.assertEqual(config.staging.root, (config_dir / "../server/testdata/staged_jobs_manual").resolve())
            self.assertEqual(config.publish.index_path, (config_dir / ".state/publish_index.json").resolve())
            self.assertEqual(config.paths.examples_dir, (config_dir / "examples").resolve())
            self.assertEqual(config.paths.content_dir, (config_dir / "content").resolve())
            self.assertEqual(config.paths.docs_dir, (config_dir / "docs").resolve())


if __name__ == "__main__":
    unittest.main()
