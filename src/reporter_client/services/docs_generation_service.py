"""MkDocs page generation from canonical page inputs."""

from __future__ import annotations

from pathlib import Path

from ..builders.about_page_builder import AboutPageBuilder
from ..builders.home_page_builder import HomePageBuilder
from ..builders.project_page_builder import ProjectPageBuilder
from ..builders.tree_page_builder import TreePageBuilder
from ..renderers.about_renderer import AboutRenderer
from ..renderers.home_renderer import HomeRenderer
from ..renderers.project_renderer import ProjectRenderer
from ..renderers.tree_renderer import TreeRenderer
from .staged_input_service import StagedInputService


class DocsGenerationService:
    """Render documentation pages from canonical page inputs."""

    def __init__(self, *, staging_root: Path, content_dir: Path, docs_dir: Path) -> None:
        self._staging_root = staging_root
        self._docs_dir = docs_dir
        template_dir = self._resolve_template_dir()
        self._inputs = StagedInputService(staging_root=staging_root, content_dir=content_dir, docs_dir=docs_dir)
        self._home_builder = HomePageBuilder()
        self._about_builder = AboutPageBuilder()
        self._project_builder = ProjectPageBuilder()
        self._tree_builder = TreePageBuilder()
        self._home_renderer = HomeRenderer(template_dir=template_dir)
        self._about_renderer = AboutRenderer(template_dir=template_dir)
        self._project_renderer = ProjectRenderer(template_dir=template_dir)
        self._tree_renderer = TreeRenderer(template_dir=template_dir)

    def generate(self) -> None:
        """Generate the docs pages used by MkDocs."""
        home_view = self._home_builder.build(self._inputs.load_home_input())
        self._write("index.md", self._home_renderer.render({"view": home_view}))
        about_view = self._about_builder.build(self._inputs.load_about_input())
        self._write("about.md", self._about_renderer.render({"view": about_view}))
        project_inputs = self._inputs.load_project_inputs()
        self._clear_generated_docs(
            subdir="projects",
            keep_paths={f"projects/{project_input.project_id}.md" for project_input in project_inputs},
        )
        for project_input in project_inputs:
            project_view = self._project_builder.build(project_input)
            self._write(f"projects/{project_input.project_id}.md", self._project_renderer.render({"view": project_view}))
        tree_inputs = self._inputs.load_tree_inputs()
        self._clear_generated_tree_docs(keep_paths={tree_input.tree_doc for tree_input in tree_inputs})
        for tree_input in tree_inputs:
            tree_view = self._tree_builder.build(tree_input)
            self._write(tree_input.tree_doc, self._tree_renderer.render({"view": tree_view}))

    def _write(self, relative_path: str, rendered: str) -> None:
        target = self._docs_dir / relative_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(rendered, encoding="utf-8")

    def _clear_generated_docs(self, *, subdir: str, keep_paths: set[str]) -> None:
        target_dir = self._docs_dir / subdir
        if not target_dir.exists():
            return
        keep_names = {Path(path).name for path in keep_paths}
        for path in target_dir.glob("*.md"):
            if path.name not in keep_names:
                path.unlink()

    def _clear_generated_tree_docs(self, *, keep_paths: set[str]) -> None:
        keep_targets = {self._docs_dir / path for path in keep_paths}

        flat_trees_dir = self._docs_dir / "trees"
        if flat_trees_dir.exists():
            for path in flat_trees_dir.rglob("*.md"):
                if path not in keep_targets:
                    path.unlink()

        projects_dir = self._docs_dir / "projects"
        if projects_dir.exists():
            for path in projects_dir.glob("*/trees/*.md"):
                if path not in keep_targets:
                    path.unlink()

    @staticmethod
    def _resolve_template_dir() -> Path:
        """Prefer live workspace templates so uv-run commands reflect edits immediately."""
        workspace_templates = Path.cwd() / "src" / "reporter_client" / "templates"
        if workspace_templates.exists():
            return workspace_templates
        return Path(__file__).resolve().parent.parent / "templates"
