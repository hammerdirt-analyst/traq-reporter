"""Context models for page-level summary generation."""

from __future__ import annotations

from dataclasses import dataclass

from .home_report_source import HomeReportSource
from .project_report_source import ProjectReportSource
from .tree_report_source import TreeReportSource


@dataclass(frozen=True)
class TreeSummaryContext:
    source: TreeReportSource
    crown_and_branches: dict
    trunk: dict
    roots_and_root_collar: dict
    tree_health_and_species: dict
    risk_categorization: list[dict]
    mitigation_options: list[dict]
    transcript: str


@dataclass(frozen=True)
class ProjectSummaryContext:
    project_id: str
    project_name: str
    stable_description: str
    project_source: ProjectReportSource


@dataclass(frozen=True)
class HomeSummaryContext:
    home_source: HomeReportSource
    stable_intro: str
    project_summaries: list[str]
