"""Canonical naming and indexing for published tree pages."""

from __future__ import annotations

from dataclasses import replace

from ...models.tree_report_source import TreeReportSource
from ..project_naming import project_slug


class TreeIdentityService:
    """Assign project-scoped canonical tree ids from the canonical tree set."""

    def assign_tree_ids(self, tree_sources: list[TreeReportSource]) -> list[TreeReportSource]:
        grouped: dict[str, list[TreeReportSource]] = {}
        for source in tree_sources:
            grouped.setdefault(source.project, []).append(source)

        identified: list[TreeReportSource] = []
        for project_name in sorted(grouped):
            slug = project_slug(project_name)
            ordered_sources = sorted(grouped[project_name], key=lambda item: (item.archived_at, item.job_id))
            for index, source in enumerate(ordered_sources, start=1):
                tree_id = source.tree_id or f"{slug}_{index:03d}"
                identified.append(replace(source, tree_id=tree_id))
        return identified
