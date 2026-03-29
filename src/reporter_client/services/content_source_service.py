"""Markdown content loading for authored publication text."""

from __future__ import annotations

from pathlib import Path


class ContentSourceService:
    """Load authored Markdown fragments from the content directory."""

    def __init__(self, *, content_dir: Path) -> None:
        self._content_dir = content_dir

    def read_home_summary(self) -> str:
        """Return the authored home summary Markdown."""
        return self._read_required("home_summary.md")

    def read_about(self) -> str:
        """Return the authored About page Markdown."""
        return self._read_required("about.md")

    def read_project_summary(self, project_id: str) -> str:
        """Return the authored project summary Markdown."""
        return self._read_required(f"projects/{project_id}.md")

    def project_summary_exists(self, project_id: str) -> bool:
        """Return whether authored project Markdown exists for the project."""
        return (self._content_dir / "projects" / f"{project_id}.md").exists()

    def _read_required(self, relative_path: str) -> str:
        path = self._content_dir / relative_path
        return path.read_text(encoding="utf-8").strip() + "\n"
