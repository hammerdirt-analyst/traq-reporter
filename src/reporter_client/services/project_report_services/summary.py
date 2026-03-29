"""Project-page summary service."""

from __future__ import annotations

from ...models.summary_artifacts import SummaryArtifact
from ...models.summary_contexts import ProjectSummaryContext
from ..summary_services import SummaryGenerator, build_project_summary_prompts


class ProjectSummaryService:
    """Generate narrative content for project pages."""

    def __init__(self, *, generator: SummaryGenerator | None = None) -> None:
        self._generator = generator or SummaryGenerator()

    def generate(self, context: ProjectSummaryContext) -> SummaryArtifact:
        prompts = build_project_summary_prompts(context)
        return self._generator.generate(
            page_kind="project",
            source_identifier=context.project_id,
            prompts=prompts,
        )
