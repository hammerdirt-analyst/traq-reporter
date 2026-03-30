"""Shared media-selection rules."""

from __future__ import annotations


LEAD_TREE_CAPTION_PREFIX = "the tree:"


def is_lead_tree_caption(caption: str) -> bool:
    return caption.strip().lower().startswith(LEAD_TREE_CAPTION_PREFIX)
