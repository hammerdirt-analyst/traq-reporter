"""Home-page summary service."""

from __future__ import annotations

from ...models.summary_artifacts import SummaryArtifact
from ...models.summary_contexts import HomeSummaryContext
from ..summary_services import SummaryGenerator, build_home_summary_prompts


class HomeSummaryService:
    """Generate narrative content for the home page."""

    def __init__(self, *, generator: SummaryGenerator | None = None) -> None:
        self._generator = generator or SummaryGenerator()

    def generate(self, context: HomeSummaryContext) -> SummaryArtifact:
        prompts = build_home_summary_prompts(context)
        return self._generator.generate(
            page_kind="home",
            source_identifier=context.home_source.site_title,
            prompts=prompts,
        )
