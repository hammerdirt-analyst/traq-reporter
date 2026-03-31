"""Canonical input models consumed by page builders."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SummaryMetricsInput:
    assessment_count: str
    tree_count: str
    species_count: str
    project_count: str | None = None


@dataclass(frozen=True)
class ProjectLinkInput:
    project_id: str
    project_name: str
    project_doc: str


@dataclass(frozen=True)
class ProjectTreeCardInput:
    ordinal: int
    job_number: str
    tree_doc: str
    species_common: str
    risk_rating: str
    main_concerns: str


@dataclass(frozen=True)
class ImageAssetInput:
    image_src: str
    caption: str


@dataclass(frozen=True)
class MapAssetInput:
    image_src: str
    alt: str


@dataclass(frozen=True)
class HomePageInput:
    site_title: str
    description_markdown: str
    summary_metrics: SummaryMetricsInput
    project_links: list[ProjectLinkInput]
    updated_at: str


@dataclass(frozen=True)
class ProjectPageInput:
    project_id: str
    project_name: str
    description_markdown: str
    map_src: str
    map_alt: str
    project_image: ImageAssetInput | None
    summary_metrics: SummaryMetricsInput
    tree_cards: list[ProjectTreeCardInput]
    updated_at: str
    empty_state_notice: str = ""


@dataclass(frozen=True)
class TreePageInput:
    tree_doc: str
    project_name: str
    project_doc: str
    tree_name: str
    title_text: str
    facts: list[tuple[str, str]]
    tree_map: MapAssetInput
    image_gallery: list[ImageAssetInput]
    summary_text: str
    narrative_paragraphs: list[str]
    completed_inspection_form_url: str
    updated_at: str


@dataclass(frozen=True)
class AboutPageInput:
    title: str
    body_markdown: str
    updated_at: str
