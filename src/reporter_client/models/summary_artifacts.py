"""Artifact models for generated summaries with provenance."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SummaryResponse:
    summary_text: str
    narrative_blocks: list[str]


@dataclass(frozen=True)
class SummaryArtifact:
    page_kind: str
    source_identifier: str
    model_name: str
    prompt_version: str
    generated_at: str
    summary_text: str
    narrative_blocks: list[str]
