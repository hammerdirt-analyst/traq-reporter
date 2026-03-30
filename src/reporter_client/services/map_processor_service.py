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
    longitude: float | None = None
    latitude: float | None = None


@dataclass(frozen=True)
class MapRenderRequest:
    output_asset_src: str
    fallback_image_src: str
    alt: str
    points: list[MapRenderPoint]
    basemap_slug: str | None = None
    crop_width: int | None = None
    crop_height: int | None = None
    marker_radius: int | None = None
    marker_font_size: int | None = None


@dataclass(frozen=True)
class MapRenderArtifact:
    image_src: str
    alt: str
    points: list[MapRenderPoint]


class MapProcessorService:
    """Render numbered risk markers onto a prepared project basemap."""

    _MARKER_RADIUS = 18
    _MARKER_FONT_SIZE = 16
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
        crop_box = self._crop_box(
            request=request,
            bounds=bounds,
            image_width=annotated.width,
            image_height=annotated.height,
            render_points=render_points,
        )
        crop_left, crop_top, crop_right, crop_bottom = crop_box
        if crop_box != (0, 0, annotated.width, annotated.height):
            annotated = annotated.crop(crop_box)
        draw = ImageDraw.Draw(annotated)
        marker_radius = request.marker_radius or self._MARKER_RADIUS
        marker_font_size = request.marker_font_size or self._MARKER_FONT_SIZE
        font = self._load_font(marker_font_size)

        for render_point, longitude, latitude in render_points:
            x, y = self._project(longitude, latitude, bounds, image.width, image.height)
            x -= crop_left
            y -= crop_top
            self._draw_marker(
                draw,
                font,
                x,
                y,
                render_point.ordinal,
                self._risk_color(render_point.risk_rating),
                marker_radius=marker_radius,
            )

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
            if render_point.longitude is not None and render_point.latitude is not None:
                render_points.append((render_point, render_point.longitude, render_point.latitude))
                continue
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

    def _crop_box(
        self,
        *,
        request: MapRenderRequest,
        bounds: dict[str, float],
        image_width: int,
        image_height: int,
        render_points: list[tuple[MapRenderPoint, float, float]],
    ) -> tuple[int, int, int, int]:
        if not request.crop_width or not request.crop_height or not render_points:
            return (0, 0, image_width, image_height)

        target_width = min(request.crop_width, image_width)
        target_height = min(request.crop_height, image_height)
        center_longitude = render_points[0][1]
        center_latitude = render_points[0][2]
        center_x, center_y = self._project(center_longitude, center_latitude, bounds, image_width, image_height)
        left = int(round(center_x - (target_width / 2)))
        top = int(round(center_y - (target_height / 2)))
        max_left = image_width - target_width
        max_top = image_height - target_height
        left = max(0, min(max_left, left))
        top = max(0, min(max_top, top))
        return (left, top, left + target_width, top + target_height)

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
        *,
        marker_radius: int,
    ) -> None:
        left = x - marker_radius
        top = y - marker_radius
        right = x + marker_radius
        bottom = y + marker_radius
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
    def _load_font(size: int) -> ImageFont.ImageFont | ImageFont.FreeTypeFont:
        try:
            return ImageFont.truetype("DejaVuSans-Bold.ttf", size)
        except OSError:
            return ImageFont.load_default()

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
