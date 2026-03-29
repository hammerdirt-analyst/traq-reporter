"""Tests for staged job bundle loading into canonical tree report sources."""

from __future__ import annotations

from pathlib import Path
import unittest

from reporter_client.services.tree_report_services import StagedTreeBundleService


class StagedTreeBundleServiceTests(unittest.TestCase):
    def test_build_from_manifest_maps_staged_job_bundle(self) -> None:
        repo_root = Path(__file__).resolve().parent.parent
        manifest_path = repo_root.parent / "server" / "testdata" / "staged_jobs_manual" / "jobs" / "J0003" / "manifest.json"
        if not manifest_path.exists():
            self.skipTest(f"Staged bundle fixture not found: {manifest_path}")

        source = StagedTreeBundleService().build_from_manifest(manifest_path)

        self.assertEqual(source.project, "Briarwood")
        self.assertEqual(source.job_id, "job_b62ffe12501c")
        self.assertEqual(source.client_revision_id, "ea4941e6-ca8c-464f-8370-ad47bd75c818")
        self.assertEqual(source.species, "Quercus agrifolia")
        self.assertEqual(source.dbh, 20)
        self.assertEqual(source.height, 54)
        self.assertEqual(source.risk_profile.overall_tree_risk, "low")
        self.assertEqual(source.assessor_name, "Roger Erismann")
        self.assertEqual(len(source.images), 3)
        self.assertTrue(source.images[0].image_src.endswith("images/d754d568-5b72-418e-9e09-f84e8f6bc183.report.jpg"))
        self.assertEqual(source.images[0].caption, "the tree in the middle")
        self.assertIsNotNone(source.geojson)
        self.assertTrue(source.geojson.geojson_src.endswith("final.geojson"))
        self.assertTrue(source.completed_inspection_form_url.endswith("traq_page1.pdf"))
        self.assertIn("[client_tree_details]", source.transcript)


if __name__ == "__main__":
    unittest.main()
