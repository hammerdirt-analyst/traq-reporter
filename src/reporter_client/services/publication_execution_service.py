"""Incremental staged publication orchestration."""

from __future__ import annotations

import logging
from pathlib import Path

from ..models.publish_index import PublicationExecutionResult, PublishWorkItem
from .project_naming import project_slug
from .home_publication_service import HomePublicationService
from .project_publication_service import ProjectPublicationService
from .publish_state_service import PublishStateService
from .staged_manifest_service import StagedManifestService
from .tree_publication_service import TreePublicationService


logger = logging.getLogger("reporter_client.publish")


class PublicationExecutionService:
    """Execute staged publication work using the local publish index."""

    def __init__(self, *, staging_root: Path, content_dir: Path, docs_dir: Path, index_path: Path) -> None:
        self._staging_root = staging_root
        self._content_dir = content_dir
        self._docs_dir = docs_dir
        self._index_path = index_path
        template_dir = self._resolve_template_dir()
        self._manifest_service = StagedManifestService()
        self._publish_state_service = PublishStateService()
        self._tree_publication_service = TreePublicationService(docs_dir=docs_dir, template_dir=template_dir)
        self._project_publication_service = ProjectPublicationService(
            content_dir=content_dir,
            docs_dir=docs_dir,
            template_dir=template_dir,
        )
        self._home_publication_service = HomePublicationService(
            content_dir=content_dir,
            docs_dir=docs_dir,
            template_dir=template_dir,
        )

    def run(self) -> PublicationExecutionResult:
        logger.info("loading publish index from %s", self._index_path)
        index = self._publish_state_service.load_index(self._index_path)
        logger.info("discovering staged manifests under %s", self._staging_root)
        staged_records = self._manifest_service.discover(self._staging_root)
        staged_job_ids = {record.job_id for record in staged_records}
        removed_job_ids = set(index.records) - staged_job_ids
        removed_projects = {index.records[job_id].project for job_id in removed_job_ids}
        plan = self._publish_state_service.build_plan(staged_records=staged_records, index=index)
        logger.info(
            "publish plan: %s new, %s changed, %s unchanged, %s removed",
            len(plan.new_jobs),
            len(plan.changed_jobs),
            len(plan.unchanged_jobs),
            len(removed_job_ids),
        )

        work_items = [*plan.new_jobs, *plan.changed_jobs, *plan.unchanged_jobs]
        changed_job_ids = {item.job_id for item in [*plan.new_jobs, *plan.changed_jobs]}
        records = self._tree_publication_service.load_current_records(
            work_items=work_items,
            changed_job_ids=changed_job_ids,
        )
        self._clear_generated_tree_docs(keep_paths={self._tree_doc_path(record.source) for record in records})

        logger.info("publishing changed tree pages and repairing missing current tree pages")
        tree_pages_written = self._tree_publication_service.publish_tree_pages(
            records,
            target_job_ids=changed_job_ids,
        )
        all_tree_sources = [record.source for record in records]
        affected_projects = sorted({item.project for item in [*plan.new_jobs, *plan.changed_jobs]} | removed_projects)
        project_sources = self._project_publication_service.build_project_sources(all_tree_sources)
        self._clear_generated_project_docs(keep_paths={self._project_doc_path(source.project) for source in project_sources})
        logger.info("publishing %s project page(s)", len(project_sources))
        project_pages_written = self._project_publication_service.publish_project_pages(
            project_sources=project_sources,
            target_projects={source.project for source in project_sources},
        )
        should_write_home = bool(changed_job_ids or removed_job_ids)
        logger.info("updating home/about: %s", "yes" if should_write_home else "no")
        home_updated = self._home_publication_service.publish(
            project_sources=project_sources,
            should_write=should_write_home,
        )

        if changed_job_ids or removed_job_ids:
            updated_index = self._publish_state_service.apply_plan(index=index, plan=plan)
            self._publish_state_service.save_index(self._index_path, updated_index)
            logger.info("wrote publish index to %s", self._index_path)

        return PublicationExecutionResult(
            new_jobs=len(plan.new_jobs),
            changed_jobs=len(plan.changed_jobs),
            unchanged_jobs=len(plan.unchanged_jobs),
            tree_pages_written=tree_pages_written,
            project_pages_written=project_pages_written,
            home_updated=home_updated,
            affected_projects=affected_projects,
        )

    @staticmethod
    def _resolve_template_dir() -> Path:
        workspace_templates = Path.cwd() / "src" / "reporter_client" / "templates"
        if workspace_templates.exists():
            return workspace_templates
        return Path(__file__).resolve().parent.parent / "templates"

    def _clear_generated_tree_docs(self, *, keep_paths: set[Path]) -> None:
        projects_dir = self._docs_dir / "projects"
        if not projects_dir.exists():
            return
        for path in projects_dir.glob("*/trees/*.md"):
            if path not in keep_paths:
                path.unlink()

    def _clear_generated_project_docs(self, *, keep_paths: set[Path]) -> None:
        projects_dir = self._docs_dir / "projects"
        if not projects_dir.exists():
            return
        keep_names = {path.name for path in keep_paths}
        for path in projects_dir.glob("*.md"):
            if path.name not in keep_names:
                path.unlink()

    def _tree_doc_path(self, source) -> Path:
        slug = project_slug(source.project)
        return self._docs_dir / "projects" / slug / "trees" / f"{source.tree_id}.md"

    def _project_doc_path(self, project_name: str) -> Path:
        return self._docs_dir / "projects" / f"{project_slug(project_name)}.md"
