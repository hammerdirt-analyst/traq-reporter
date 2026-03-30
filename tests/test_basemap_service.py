"""Tests for standalone basemap generation."""

from __future__ import annotations

import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from PIL import Image

from reporter_client.services.basemap_service import BasemapService, BoundingBox


class BasemapServiceTests(unittest.TestCase):
    def test_build_writes_image_and_metadata_for_exact_bbox(self) -> None:
        def fake_tile_fetcher(zoom: int, tile_x: int, tile_y: int) -> bytes:
            image = Image.new("RGB", (256, 256), (tile_x % 255, tile_y % 255, zoom % 255))
            from io import BytesIO

            buffer = BytesIO()
            image.save(buffer, format="PNG")
            return buffer.getvalue()

        bbox = BoundingBox(
            west=-121.28101670195525,
            east=-121.27448722406692,
            south=38.613356397796935,
            north=38.61699761222076,
        )

        with TemporaryDirectory() as tmp_dir:
            docs_dir = Path(tmp_dir) / "docs"
            result = BasemapService(tile_fetcher=fake_tile_fetcher).build(
                docs_dir=docs_dir,
                slug="briarwood",
                bbox=bbox,
                zoom=16,
            )

            self.assertEqual(result.image_src, "assets/map-bases/briarwood_base.jpg")
            self.assertEqual(result.metadata_src, "assets/map-bases/briarwood_base.json")
            self.assertTrue(result.image_path.exists())
            self.assertTrue(result.metadata_path.exists())
            self.assertGreater(result.width, 0)
            self.assertGreater(result.height, 0)

            metadata = json.loads(result.metadata_path.read_text(encoding="utf-8"))
            self.assertEqual(metadata["west"], bbox.west)
            self.assertEqual(metadata["east"], bbox.east)
            self.assertEqual(metadata["south"], bbox.south)
            self.assertEqual(metadata["north"], bbox.north)
            self.assertEqual(metadata["zoom"], 16)
            self.assertEqual(metadata["width"], result.width)
            self.assertEqual(metadata["height"], result.height)

    def test_build_uses_exact_bbox_without_padding(self) -> None:
        bbox = BoundingBox(
            west=-121.28101670195525,
            east=-121.27448722406692,
            south=38.613356397796935,
            north=38.61699761222076,
        )

        with TemporaryDirectory() as tmp_dir:
            docs_dir = Path(tmp_dir) / "docs"
            result = BasemapService(tile_fetcher=self._single_color_tile).build(
                docs_dir=docs_dir,
                slug="briarwood",
                bbox=bbox,
                zoom=16,
            )

            metadata = json.loads(result.metadata_path.read_text(encoding="utf-8"))
            self.assertEqual(metadata["west"], -121.28101670195525)
            self.assertEqual(metadata["east"], -121.27448722406692)
            self.assertEqual(metadata["south"], 38.613356397796935)
            self.assertEqual(metadata["north"], 38.61699761222076)

    @staticmethod
    def _single_color_tile(zoom: int, tile_x: int, tile_y: int) -> bytes:
        from io import BytesIO

        image = Image.new("RGB", (256, 256), (200, 210, 220))
        buffer = BytesIO()
        image.save(buffer, format="PNG")
        return buffer.getvalue()


if __name__ == "__main__":
    unittest.main()
