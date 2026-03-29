"""Shared renderer plumbing."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader


class BaseRenderer:
    """Render one page from a Jinja template."""

    template_name: str

    def __init__(self, *, template_dir: Path) -> None:
        self._environment = Environment(
            loader=FileSystemLoader(str(template_dir)),
            autoescape=False,
            trim_blocks=True,
            lstrip_blocks=True,
        )

    def render(self, context: dict[str, Any]) -> str:
        """Render the page with the supplied context."""
        return self._environment.get_template(self.template_name).render(**context).strip() + "\n"
