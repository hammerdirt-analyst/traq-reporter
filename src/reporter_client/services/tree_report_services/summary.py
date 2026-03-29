"""Tree-page summary service."""

from __future__ import annotations

from ...models.summary_artifacts import SummaryArtifact
from ...models.summary_contexts import TreeSummaryContext
from ..summary_services import SummaryGenerator, build_tree_summary_prompts


class TreeSummaryService:
    """Generate narrative content for tree pages."""

    def __init__(self, *, generator: SummaryGenerator | None = None) -> None:
        self._generator = generator or SummaryGenerator()

    def generate(self, context: TreeSummaryContext) -> SummaryArtifact:
        prompts = build_tree_summary_prompts(context)
        return self._generator.generate(
            page_kind="tree",
            source_identifier=context.source.job_id,
            prompts=prompts,
        )
