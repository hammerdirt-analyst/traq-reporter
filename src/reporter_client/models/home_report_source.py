"""Home reporting source models derived from project reporting sources."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class HomeProjectEntry:
    project_name: str
    project_slug: str
    project_doc: str
    tree_count: int
    species_count: int


@dataclass(frozen=True)
class HomeReportSource:
    site_title: str
    project_count: int
    tree_count: int
    species_count: int
    earliest_archived_at: str
    latest_archived_at: str
    projects: list[HomeProjectEntry]
