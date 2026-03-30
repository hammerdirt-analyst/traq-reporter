"""Incremental tree publication from staged bundles."""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path

from ..builders.tree_page_builder import TreePageBuilder
from ..models.publish_index import PublishWorkItem
from ..renderers.tree_renderer import TreeRenderer
from .tree_report_services import (
    StagedTreeBundleService,
    TreeArtifactPublishService,
    TreeMapService,
    TreePageInputService,
    TreeSummaryContextBuilder,
    TreeSummaryService,
)


class TreePublicationService:
    """Publish changed tree pages from staged job bundles."""

    def __init__(self, *, docs_dir: Path, template_dir: Path) -> None:
        self._docs_dir = docs_dir
        self._builder = TreePageBuilder()
        self._renderer = TreeRenderer(template_dir=template_dir)
        self._staged_tree_bundle_service = StagedTreeBundleService()
        self._tree_artifact_publish_service = TreeArtifactPublishService()
        self._tree_page_input_service = TreePageInputService(
            tree_map_service=TreeMapService(docs_dir=docs_dir)
        )
        self._tree_summary_context_builder = TreeSummaryContextBuilder()
        self._tree_summary_service = TreeSummaryService()

    def load_current_records(
        self,
        *,
        work_items: list[PublishWorkItem],
        changed_job_ids: set[str],
    ):
        records = []
        for item in work_items:
            record = self._staged_tree_bundle_service.build_record_from_manifest(Path(item.manifest_path))
            record = replace(record, source=replace(record.source, tree_id=item.tree_id))
            source = (
                self._tree_artifact_publish_service.publish(source=record.source, docs_dir=self._docs_dir)
                if item.job_id in changed_job_ids
                else self._tree_artifact_publish_service.link_existing(record.source)
            )
            records.append(replace(record, source=source))
        return records

    def publish_tree_pages(self, records, *, target_job_ids: set[str]) -> int:
        written = 0
        for record in records:
            if record.source.job_id not in target_job_ids:
                continue
            summary_context = self._tree_summary_context_builder.build(
                source=record.source,
                completed_payload=record.completed_payload,
                transcript=record.source.transcript,
            )
            summary_artifact = self._tree_summary_service.generate(summary_context)
            page_input = self._tree_page_input_service.build(record.source, summary_artifact)
            page_view = self._builder.build(page_input)
            self._write(page_input.tree_doc, self._renderer.render({"view": page_view}))
            written += 1
        return written

    def _write(self, relative_path: str, rendered: str) -> None:
        target = self._docs_dir / relative_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(rendered, encoding="utf-8")
