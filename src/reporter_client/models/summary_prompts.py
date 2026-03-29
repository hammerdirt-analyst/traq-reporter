"""Prompt payload models for summary generation."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SummaryPrompts:
    system_prompt: str
    user_prompt: str
    prompt_version: str
