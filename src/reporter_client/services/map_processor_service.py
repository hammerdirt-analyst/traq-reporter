"""Shared GeoJSON-to-map processor for tree and project report pages."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class MapProcessorRequest:
    output_asset_src: str
    fallback_image_src: str
    alt: str
    geojson_sources: list[str]


@dataclass(frozen=True)
class MapProcessorArtifact:
    image_src: str
    alt: str
    geojson_sources: list[str]


class MapProcessorService:
    """Render a simple SVG map from published GeoJSON assets."""

    _WIDTH = 640
    _HEIGHT = 360
    _PADDING = 32
    _PALETTE = ("#14532d", "#0f766e", "#9a3412", "#4338ca", "#be123c")

    def __init__(self, *, docs_dir: Path | None = None) -> None:
        self._docs_dir = docs_dir

    def render(self, request: MapProcessorRequest) -> MapProcessorArtifact:
        if self._docs_dir is None:
            return MapProcessorArtifact(
                image_src=request.fallback_image_src,
                alt=request.alt,
                geojson_sources=list(request.geojson_sources),
            )

        layers = self._load_layers(request.geojson_sources)
        if not layers:
            return MapProcessorArtifact(
                image_src=request.fallback_image_src,
                alt=request.alt,
                geojson_sources=list(request.geojson_sources),
            )

        target_path = self._docs_dir / request.output_asset_src
        target_path.parent.mkdir(parents=True, exist_ok=True)
        target_path.write_text(self._build_svg(layers), encoding="utf-8")
        return MapProcessorArtifact(
            image_src=request.output_asset_src,
            alt=request.alt,
            geojson_sources=list(request.geojson_sources),
        )

    def _load_layers(self, geojson_sources: list[str]) -> list[tuple[int, list[tuple[str, object]], list[tuple[float, float]]]]:
        layers: list[tuple[int, list[tuple[str, object]], list[tuple[float, float]]]] = []
        for index, asset_src in enumerate(geojson_sources):
            source_path = self._docs_dir / asset_src
            if not source_path.exists():
                continue
            try:
                payload = json.loads(source_path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                continue
            shapes = self._extract_shapes(payload)
            points: list[tuple[float, float]] = []
            for _, shape in shapes:
                points.extend(self._flatten_points(shape))
            if points:
                layers.append((index, shapes, points))
        return layers

    def _build_svg(self, layers: list[tuple[int, list[tuple[str, object]], list[tuple[float, float]]]]) -> str:
        all_points = [point for _, _, points in layers for point in points]
        min_x = min(point[0] for point in all_points)
        max_x = max(point[0] for point in all_points)
        min_y = min(point[1] for point in all_points)
        max_y = max(point[1] for point in all_points)

        span_x = max(max_x - min_x, 1e-9)
        span_y = max(max_y - min_y, 1e-9)
        usable_width = self._WIDTH - (self._PADDING * 2)
        usable_height = self._HEIGHT - (self._PADDING * 2)

        def project(point: tuple[float, float]) -> tuple[float, float]:
            if span_x <= 1e-8 and span_y <= 1e-8:
                return self._WIDTH / 2, self._HEIGHT / 2
            scale = min(usable_width / span_x if span_x > 1e-8 else usable_width, usable_height / span_y if span_y > 1e-8 else usable_height)
            draw_width = span_x * scale
            draw_height = span_y * scale
            offset_x = (self._WIDTH - draw_width) / 2
            offset_y = (self._HEIGHT - draw_height) / 2
            x = offset_x + ((point[0] - min_x) * scale if span_x > 1e-8 else draw_width / 2)
            y = offset_y + ((max_y - point[1]) * scale if span_y > 1e-8 else draw_height / 2)
            return round(x, 2), round(y, 2)

        svg_parts = [
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{self._WIDTH}" height="{self._HEIGHT}" viewBox="0 0 {self._WIDTH} {self._HEIGHT}" role="img">',
            '<rect width="100%" height="100%" fill="#f8fafc"/>',
            f'<rect x="{self._PADDING / 2}" y="{self._PADDING / 2}" width="{self._WIDTH - self._PADDING}" height="{self._HEIGHT - self._PADDING}" fill="#ffffff" stroke="#cbd5e1" stroke-width="1"/>',
        ]

        for layer_index, shapes, _ in layers:
            color = self._PALETTE[layer_index % len(self._PALETTE)]
            fill = self._with_alpha(color, "0.18")
            for geometry_type, shape in shapes:
                svg_parts.extend(self._render_shape(geometry_type, shape, color, fill, project))

        svg_parts.append("</svg>")
        return "\n".join(svg_parts)

    def _render_shape(
        self,
        geometry_type: str,
        shape: object,
        color: str,
        fill: str,
        project,
    ) -> list[str]:
        if geometry_type == "Point":
            x, y = project(shape)
            return [f'<circle cx="{x}" cy="{y}" r="7" fill="{color}" stroke="#ffffff" stroke-width="2"/>']
        if geometry_type == "MultiPoint":
            return [
                f'<circle cx="{x}" cy="{y}" r="6" fill="{color}" stroke="#ffffff" stroke-width="2"/>'
                for x, y in (project(point) for point in shape)
            ]
        if geometry_type == "LineString":
            points = " ".join(f"{x},{y}" for x, y in (project(point) for point in shape))
            return [f'<polyline points="{points}" fill="none" stroke="{color}" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>']
        if geometry_type == "MultiLineString":
            parts: list[str] = []
            for line in shape:
                points = " ".join(f"{x},{y}" for x, y in (project(point) for point in line))
                parts.append(
                    f'<polyline points="{points}" fill="none" stroke="{color}" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>'
                )
            return parts
        if geometry_type == "Polygon":
            return self._render_polygon(shape, color, fill, project)
        if geometry_type == "MultiPolygon":
            parts: list[str] = []
            for polygon in shape:
                parts.extend(self._render_polygon(polygon, color, fill, project))
            return parts
        return []

    @staticmethod
    def _render_polygon(shape, color: str, fill: str, project) -> list[str]:
        parts: list[str] = []
        for ring_index, ring in enumerate(shape):
            points = " ".join(f"{x},{y}" for x, y in (project(point) for point in ring))
            ring_fill = fill if ring_index == 0 else "#ffffff"
            parts.append(
                f'<polygon points="{points}" fill="{ring_fill}" stroke="{color}" stroke-width="2" stroke-linejoin="round"/>'
            )
        return parts

    def _extract_shapes(self, payload: object) -> list[tuple[str, object]]:
        if not isinstance(payload, dict):
            return []
        payload_type = payload.get("type")
        if payload_type == "FeatureCollection":
            shapes: list[tuple[str, object]] = []
            for feature in payload.get("features", []):
                shapes.extend(self._extract_shapes(feature))
            return shapes
        if payload_type == "Feature":
            return self._extract_shapes(payload.get("geometry"))
        if payload_type == "GeometryCollection":
            shapes: list[tuple[str, object]] = []
            for geometry in payload.get("geometries", []):
                shapes.extend(self._extract_shapes(geometry))
            return shapes
        coordinates = payload.get("coordinates")
        if payload_type in {"Point", "MultiPoint", "LineString", "MultiLineString", "Polygon", "MultiPolygon"} and coordinates is not None:
            return [(payload_type, coordinates)]
        return []

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
    def _with_alpha(color: str, alpha: str) -> str:
        color = color.lstrip("#")
        if len(color) != 6:
            return f"rgba(20, 83, 45, {alpha})"
        red = int(color[0:2], 16)
        green = int(color[2:4], 16)
        blue = int(color[4:6], 16)
        return f"rgba({red}, {green}, {blue}, {alpha})"
