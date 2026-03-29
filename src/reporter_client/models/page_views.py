"""View models consumed by page templates."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class BreadcrumbView:
    label: str
    href: str | None


@dataclass(frozen=True)
class LinkView:
    label: str
    href: str


@dataclass(frozen=True)
class MapView:
    image_href: str
    alt: str


@dataclass(frozen=True)
class SummaryMetricsView:
    assessment_count: str
    tree_count: str
    species_count: str
    project_count: str | None = None


@dataclass(frozen=True)
class TreeRowView:
    job_number: str
    tree_href: str
    species_common: str
    dbh: str
    height: str
    risk_rating: str
    main_concerns: str


@dataclass(frozen=True)
class ImageAssetView:
    image_href: str
    caption: str


@dataclass(frozen=True)
class HomePageView:
    page_title: str
    description_markdown: str
    summary_markdown: str
    breadcrumbs: list[BreadcrumbView]
    combined_map: MapView
    summary_metrics: SummaryMetricsView
    project_links: list[LinkView]
    updated_at: str


@dataclass(frozen=True)
class ProjectPageView:
    page_title: str
    description_markdown: str
    summary_markdown: str
    breadcrumbs: list[BreadcrumbView]
    project_map: MapView
    project_image: ImageAssetView | None
    summary_metrics: SummaryMetricsView
    tree_rows: list[TreeRowView]
    updated_at: str


@dataclass(frozen=True)
class TreePageView:
    page_title: str
    title_text: str
    breadcrumbs: list[BreadcrumbView]
    facts: list[tuple[str, str]]
    tree_map: MapView
    image_gallery: list[ImageAssetView]
    summary_text: str
    narrative_paragraphs: list[str]
    completed_inspection_form_link: LinkView
    updated_at: str


@dataclass(frozen=True)
class AboutPageView:
    page_title: str
    breadcrumbs: list[BreadcrumbView]
    body_markdown: str
    updated_at: str
