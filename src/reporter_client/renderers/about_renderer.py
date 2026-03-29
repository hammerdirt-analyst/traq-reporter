"""About page renderer."""

from __future__ import annotations

from .base_renderer import BaseRenderer


class AboutRenderer(BaseRenderer):
    """Render the About page."""

    template_name = "pages/about.md.j2"
