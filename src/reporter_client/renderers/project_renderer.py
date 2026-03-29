"""Project page renderer."""

from __future__ import annotations

from .base_renderer import BaseRenderer


class ProjectRenderer(BaseRenderer):
    """Render a project page."""

    template_name = "pages/project.md.j2"
