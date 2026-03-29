"""Tree page renderer."""

from __future__ import annotations

from .base_renderer import BaseRenderer


class TreeRenderer(BaseRenderer):
    """Render a tree page."""

    template_name = "pages/tree.md.j2"
