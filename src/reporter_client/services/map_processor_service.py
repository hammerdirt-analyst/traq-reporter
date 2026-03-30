"""Shared GeoJSON-to-map processor for tree and project report pages."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


@dataclass(frozen=True)
class MapRenderPoint:
    ordinal: int
    risk_rating: str
    geojson_src: str


@dataclass(frozen=True)
class MapRenderRequest:
    output_asset_src: str
    fallback_image_src: str
    alt: str
    points: list[MapRenderPoint]
    basemap_slug: str | None = None


@dataclass(frozen=True)
class MapRenderArtifact:
    image_src: str
    alt: str
    points: list[MapRenderPoint]


class MapProcessorService:
    """Render numbered risk markers onto a prepared project basemap."""

    _MARKER_RADIUS = 18
    _MARKER_OUTLINE = "#ffffff"
    _TEXT_COLOR = "#111827"

    def __init__(self, *, docs_dir: Path | None = None) -> None:
        self._docs_dir = docs_dir

    def render(self, request: MapRenderRequest) -> MapRenderArtifact:
        if self._docs_dir is None or not request.basemap_slug:
            return self._fallback(request)

        basemap_image_path = self._docs_dir / "assets" / "map-bases" / f"{request.basemap_slug}_base.jpg"
        basemap_metadata_path = self._docs_dir / "assets" / "map-bases" / f"{request.basemap_slug}_base.json"
        if not basemap_image_path.exists() or not basemap_metadata_path.exists():
            return self._fallback(request)

        render_points = self._load_render_points(request.points)
        if not render_points:
            return self._fallback(request)

        try:
            bounds = json.loads(basemap_metadata_path.read_text(encoding="utf-8"))
            image = Image.open(basemap_image_path).convert("RGB")
        except (OSError, json.JSONDecodeError):
            return self._fallback(request)

        annotated = image.copy()
        draw = ImageDraw.Draw(annotated)
        font = ImageFont.load_default()

        for render_point, longitude, latitude in render_points:
            x, y = self._project(longitude, latitude, bounds, annotated.width, annotated.height)
            self._draw_marker(draw, font, x, y, render_point.ordinal, self._risk_color(render_point.risk_rating))

        target_path = self._docs_dir / request.output_asset_src
        target_path.parent.mkdir(parents=True, exist_ok=True)
        annotated.save(target_path, format="JPEG", quality=92)
        return MapRenderArtifact(
            image_src=request.output_asset_src,
            alt=request.alt,
            points=list(request.points),
        )

    def _load_render_points(self, points: list[MapRenderPoint]) -> list[tuple[MapRenderPoint, float, float]]:
        render_points: list[tuple[MapRenderPoint, float, float]] = []
        for render_point in points:
            source_path = self._docs_dir / render_point.geojson_src
            if not source_path.exists():
                continue
            try:
                payload = json.loads(source_path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                continue
            coordinates = self._extract_coordinates(payload)
            if not coordinates:
                continue
            longitude = sum(point[0] for point in coordinates) / len(coordinates)
            latitude = sum(point[1] for point in coordinates) / len(coordinates)
            render_points.append((render_point, longitude, latitude))
        return render_points

    def _extract_coordinates(self, payload: object) -> list[tuple[float, float]]:
        if not isinstance(payload, dict):
            return []
        payload_type = payload.get("type")
        if payload_type == "FeatureCollection":
            points: list[tuple[float, float]] = []
            for feature in payload.get("features", []):
                points.extend(self._extract_coordinates(feature))
            return points
        if payload_type == "Feature":
            return self._extract_coordinates(payload.get("geometry"))
        if payload_type == "GeometryCollection":
            points: list[tuple[float, float]] = []
            for geometry in payload.get("geometries", []):
                points.extend(self._extract_coordinates(geometry))
            return points
        coordinates = payload.get("coordinates")
        if coordinates is None:
            return []
        return self._flatten_points(coordinates)

    def _flatten_points(self, shape: object) -> list[tuple[float, float]]:
        if isinstance(shape, (list, tuple)):
            if len(shape) >= 2 and all(isinstance(value, (int, float)) for value in shape[:2]):
                return [(float(shape[0]), float(shape[1]))]
            points: list[tuple[float, float]] = []
            for item in shape:
                points.extend(self._flatten_points(item))
            return points
        return []

    @staticmethod
    def _project(
        longitude: float,
        latitude: float,
        bounds: dict[str, float],
        width: int,
        height: int,
    ) -> tuple[float, float]:
        west = float(bounds["west"])
        east = float(bounds["east"])
        south = float(bounds["south"])
        north = float(bounds["north"])
        span_x = max(east - west, 1e-12)
        span_y = max(north - south, 1e-12)
        x = ((longitude - west) / span_x) * width
        y = ((north - latitude) / span_y) * height
        clamped_x = max(0.0, min(float(width - 1), x))
        clamped_y = max(0.0, min(float(height - 1), y))
        return clamped_x, clamped_y

    def _draw_marker(
        self,
        draw: ImageDraw.ImageDraw,
        font: ImageFont.ImageFont | ImageFont.FreeTypeFont,
        x: float,
        y: float,
        ordinal: int,
        color: str,
    ) -> None:
        left = x - self._MARKER_RADIUS
        top = y - self._MARKER_RADIUS
        right = x + self._MARKER_RADIUS
        bottom = y + self._MARKER_RADIUS
        draw.ellipse(
            (left, top, right, bottom),
            fill=color,
            outline=self._MARKER_OUTLINE,
            width=3,
        )
        label = str(ordinal)
        bbox = draw.textbbox((0, 0), label, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        draw.text(
            (x - (text_width / 2), y - (text_height / 2) - 1),
            label,
            fill=self._TEXT_COLOR,
            font=font,
        )

    @staticmethod
    def _risk_color(risk_rating: str) -> str:
        normalized = risk_rating.strip().lower()
        if normalized == "high":
            return "#dc2626"
        if normalized == "moderate":
            return "#facc15"
        return "#16a34a"

    @staticmethod
    def _fallback(request: MapRenderRequest) -> MapRenderArtifact:
        return MapRenderArtifact(
            image_src=request.fallback_image_src,
            alt=request.alt,
            points=list(request.points),
        )
