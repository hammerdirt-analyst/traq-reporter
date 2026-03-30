"""Build project reporting sources from canonical tree payloads."""

from __future__ import annotations

from collections import defaultdict

from ...models.project_report_source import ProjectReportSource, ProjectTreeEntry
from ...models.tree_report_source import TreeReportSource
from ..media_rules import is_lead_tree_caption
from ..project_naming import project_slug


class ProjectReportSourceService:
    """Aggregate canonical tree payloads into project reporting sources."""

    def build_all(
        self,
        *,
        tree_sources: list[TreeReportSource],
        project_descriptions: dict[str, str],
    ) -> list[ProjectReportSource]:
        grouped: dict[str, list[TreeReportSource]] = defaultdict(list)
        for source in tree_sources:
            grouped[source.project].append(source)

        project_sources: list[ProjectReportSource] = []
        for project_name in sorted(grouped):
            project_tree_sources = sorted(grouped[project_name], key=lambda item: (item.archived_at, item.job_id))
            entries = [self._build_tree_entry(source) for source in project_tree_sources]
            archived_dates = [entry.archived_at for entry in entries]
            canonical_entry = next(
                (entry for entry in entries if entry.canonical_image_src),
                entries[0] if entries else None,
            )
            project_sources.append(
                ProjectReportSource(
                    project=project_name,
                    project_slug=project_slug(project_name),
                    project_description=project_descriptions.get(project_name, ""),
                    tree_count=len(entries),
                    species_count=len({entry.species for entry in entries}),
                    earliest_archived_at=min(archived_dates) if archived_dates else "",
                    latest_archived_at=max(archived_dates) if archived_dates else "",
                    canonical_image_src=canonical_entry.canonical_image_src if canonical_entry else None,
                    canonical_image_caption=canonical_entry.canonical_image_caption if canonical_entry else None,
                    trees=entries,
                )
            )
        return project_sources

    def _build_tree_entry(self, source: TreeReportSource) -> ProjectTreeEntry:
        canonical_image = next(
            (image for image in source.images if is_lead_tree_caption(image.caption)),
            source.images[0] if source.images else None,
        )
        slug = project_slug(source.project)
        return ProjectTreeEntry(
            tree_id=source.tree_id,
            job_id=source.job_id,
            tree_doc=f"projects/{slug}/trees/{source.tree_id}.md",
            species=source.species,
            risk_rating=source.risk_profile.overall_tree_risk,
            main_concerns=list(source.main_concerns),
            archived_at=source.archived_at,
            transcript=source.transcript,
            geojson_src=source.geojson.geojson_src if source.geojson else None,
            canonical_image_src=canonical_image.image_src if canonical_image else None,
            canonical_image_caption=canonical_image.caption if canonical_image else None,
            dbh=source.dbh,
            height=source.height,
        )
