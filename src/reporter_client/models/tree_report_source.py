"""Internal reporting source model for one completed tree assessment."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class GpsPoint:
    latitude: float | None
    longitude: float | None


@dataclass(frozen=True)
class RiskProfile:
    overall_tree_risk: str
    overall_residual_risk: str
    recommended_inspection_interval: str


@dataclass(frozen=True)
class TreeImageSource:
    image_src: str
    caption: str


@dataclass(frozen=True)
class TreeGeoJsonSource:
    geojson_src: str


@dataclass(frozen=True)
class TreeReportSource:
    project: str
    job_id: str
    client_revision_id: str
    archived_at: str
    species: str
    dbh: float | int | None
    height: float | int | None
    gps: GpsPoint
    risk_profile: RiskProfile
    assessor_name: str
    transcript: str
    completed_inspection_form_url: str
    tree_id: str = ""
    project_ordinal: int = 1
    main_concerns: list[str] = field(default_factory=list)
    images: list[TreeImageSource] = field(default_factory=list)
    geojson: TreeGeoJsonSource | None = None
