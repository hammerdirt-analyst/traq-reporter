"""Repository boundary for generated summary artifacts."""

from __future__ import annotations

from ...models.summary_artifacts import SummaryArtifact


class SummaryRepository:
    """Placeholder storage boundary for generated summaries."""

    def save(self, artifact: SummaryArtifact) -> None:
        """Persist a generated summary artifact."""
        raise NotImplementedError("Summary repository is not implemented yet")
