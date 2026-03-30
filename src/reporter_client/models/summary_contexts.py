"""Context models for page-level summary generation."""

from __future__ import annotations

from dataclasses import dataclass

from .tree_report_source import TreeReportSource


@dataclass(frozen=True)
class TreeSummaryContext:
    source: TreeReportSource
    site_factors: dict
    target_assessment: dict
    load_factors: dict
    crown_and_branches: dict
    trunk: dict
    roots_and_root_collar: dict
    tree_health_and_species: dict
    risk_categorization: list[dict]
    mitigation_options: list[dict]
    transcript: str
