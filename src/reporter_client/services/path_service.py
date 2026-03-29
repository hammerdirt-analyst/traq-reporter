"""Path helpers for generated documentation pages."""

from __future__ import annotations

from pathlib import PurePosixPath


class PathService:
    """Build stable relative links between generated page locations."""

    SITE_ROOT = "/reporter-client"

    @staticmethod
    def doc_link(from_doc: str, to_doc: str) -> str:
        """Return a root-relative directory-style link to another generated doc."""
        target = PurePosixPath(to_doc).with_suffix("")
        if str(target.name) == "index":
            target = target.parent
        target_text = str(target).strip("/")
        if not target_text:
            return f"{PathService.SITE_ROOT}/"
        return f"{PathService.SITE_ROOT}/{target_text}/"

    @staticmethod
    def asset_link(from_doc: str, asset_path: str) -> str:
        """Return a relative path from one generated doc to a static asset."""
        return PathService._relative_path(PathService._served_dir(PurePosixPath(from_doc)), PurePosixPath(asset_path))

    @staticmethod
    def _served_dir(doc_path: PurePosixPath) -> PurePosixPath:
        if doc_path.stem == "index":
            return doc_path.parent
        return doc_path.with_suffix("")

    @staticmethod
    def _relative_path(base_dir: PurePosixPath, target: PurePosixPath) -> str:
        base_parts = base_dir.parts
        target_parts = target.parts
        common = 0
        while common < min(len(base_parts), len(target_parts)) and base_parts[common] == target_parts[common]:
            common += 1
        up = [".."] * (len(base_parts) - common)
        down = list(target_parts[common:])
        parts = up + down
        if not parts:
            return "./"
        text = "/".join(parts)
        return f"{text}/" if target.suffix == "" else text
