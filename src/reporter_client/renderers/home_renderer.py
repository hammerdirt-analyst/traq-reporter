"""Home page renderer."""

from __future__ import annotations

from .base_renderer import BaseRenderer


class HomeRenderer(BaseRenderer):
    """Render the home page."""

    template_name = "pages/home.md.j2"
