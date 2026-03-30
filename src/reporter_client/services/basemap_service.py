"""Standalone basemap generation from OpenStreetMap tiles."""

from __future__ import annotations

import io
import json
import logging
import math
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from PIL import Image


logger = logging.getLogger("reporter_client.basemap")


@dataclass(frozen=True)
class BoundingBox:
    west: float
    east: float
    south: float
    north: float


@dataclass(frozen=True)
class BasemapBuildResult:
    image_path: Path
    metadata_path: Path
    image_src: str
    metadata_src: str
    width: int
    height: int
    zoom: int


class BasemapService:
    """Fetch OSM tiles for an exact bounding box and build a basemap image."""

    TILE_SIZE = 256
    DEFAULT_ZOOM = 16
    DEFAULT_USER_AGENT = "TRAQ-Reporter/1.0 (+https://hammerdirt.solutions)"

    def __init__(self, *, tile_fetcher: Callable[[int, int, int], bytes] | None = None) -> None:
        self._tile_fetcher = tile_fetcher or self._fetch_osm_tile

    def build(
        self,
        *,
        docs_dir: Path,
        slug: str,
        bbox: BoundingBox,
        zoom: int | None = None,
    ) -> BasemapBuildResult:
        resolved_zoom = zoom if zoom is not None else self.DEFAULT_ZOOM
        target_dir = docs_dir / "assets" / "map-bases"
        target_dir.mkdir(parents=True, exist_ok=True)
        logger.info(
            "building basemap for %s at zoom %s from west=%s east=%s south=%s north=%s",
            slug,
            resolved_zoom,
            bbox.west,
            bbox.east,
            bbox.south,
            bbox.north,
        )

        image = self._render_basemap_image(bbox=bbox, zoom=resolved_zoom)
        image_path = target_dir / f"{slug}_base.jpg"
        metadata_path = target_dir / f"{slug}_base.json"
        image.save(image_path, format="JPEG", quality=92)
        metadata_path.write_text(
            json.dumps(
                {
                    "west": bbox.west,
                    "east": bbox.east,
                    "south": bbox.south,
                    "north": bbox.north,
                    "width": image.width,
                    "height": image.height,
                    "zoom": resolved_zoom,
                },
                indent=2,
            ),
            encoding="utf-8",
        )

        return BasemapBuildResult(
            image_path=image_path,
            metadata_path=metadata_path,
            image_src=f"assets/map-bases/{slug}_base.jpg",
            metadata_src=f"assets/map-bases/{slug}_base.json",
            width=image.width,
            height=image.height,
            zoom=resolved_zoom,
        )

    def _render_basemap_image(self, *, bbox: BoundingBox, zoom: int) -> Image.Image:
        west_world, north_world = self._lonlat_to_world(bbox.west, bbox.north, zoom)
        east_world, south_world = self._lonlat_to_world(bbox.east, bbox.south, zoom)

        min_tile_x = math.floor(west_world / self.TILE_SIZE)
        max_tile_x = math.floor((east_world - 1e-9) / self.TILE_SIZE)
        min_tile_y = math.floor(north_world / self.TILE_SIZE)
        max_tile_y = math.floor((south_world - 1e-9) / self.TILE_SIZE)

        tile_columns = max_tile_x - min_tile_x + 1
        tile_rows = max_tile_y - min_tile_y + 1
        canvas = Image.new("RGB", (tile_columns * self.TILE_SIZE, tile_rows * self.TILE_SIZE))

        for tile_x in range(min_tile_x, max_tile_x + 1):
            for tile_y in range(min_tile_y, max_tile_y + 1):
                tile = Image.open(io.BytesIO(self._tile_fetcher(zoom, tile_x, tile_y))).convert("RGB")
                offset_x = (tile_x - min_tile_x) * self.TILE_SIZE
                offset_y = (tile_y - min_tile_y) * self.TILE_SIZE
                canvas.paste(tile, (offset_x, offset_y))

        crop_left = int(round(west_world - (min_tile_x * self.TILE_SIZE)))
        crop_top = int(round(north_world - (min_tile_y * self.TILE_SIZE)))
        crop_right = int(round(east_world - (min_tile_x * self.TILE_SIZE)))
        crop_bottom = int(round(south_world - (min_tile_y * self.TILE_SIZE)))
        return canvas.crop((crop_left, crop_top, crop_right, crop_bottom))

    @staticmethod
    def _lonlat_to_world(lon: float, lat: float, zoom: int) -> tuple[float, float]:
        lat = max(min(lat, 85.05112878), -85.05112878)
        scale = BasemapService.TILE_SIZE * (2**zoom)
        x = (lon + 180.0) / 360.0 * scale
        lat_rad = math.radians(lat)
        y = (1.0 - math.log(math.tan(lat_rad) + (1 / math.cos(lat_rad))) / math.pi) / 2.0 * scale
        return x, y

    @staticmethod
    def _fetch_osm_tile(zoom: int, tile_x: int, tile_y: int) -> bytes:
        url = f"https://tile.openstreetmap.org/{zoom}/{tile_x}/{tile_y}.png"
        request = urllib.request.Request(
            url,
            headers={
                "User-Agent": BasemapService.DEFAULT_USER_AGENT,
                "Accept": "image/png,image/*;q=0.8,*/*;q=0.5",
            },
        )
        with urllib.request.urlopen(request, timeout=30) as response:
            return response.read()
