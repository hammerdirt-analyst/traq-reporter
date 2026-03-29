"""Project reporting source models derived from canonical tree payloads."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ProjectTreeEntry:
    tree_id: str
    job_id: str
    tree_doc: str
    species: str
    risk_rating: str
    main_concerns: list[str]
    archived_at: str
    transcript: str
    geojson_src: str | None
    canonical_image_src: str | None
    canonical_image_caption: str | None
    dbh: float | int | None = None
    height: float | int | None = None


@dataclass(frozen=True)
class ProjectReportSource:
    project: str
    project_slug: str
    project_description: str
    tree_count: int
    species_count: int
    earliest_archived_at: str
    latest_archived_at: str
    canonical_image_src: str | None
    canonical_image_caption: str | None
    trees: list[ProjectTreeEntry]
