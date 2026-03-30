"""Shared project naming helpers."""

from __future__ import annotations


def project_slug(project_name: str) -> str:
    return project_name.strip().lower().replace(" ", "-")
