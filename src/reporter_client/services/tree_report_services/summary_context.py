"""Build tree-summary contexts from completed payloads and transcripts."""

from __future__ import annotations

from ...models.summary_contexts import TreeSummaryContext
from ...models.tree_report_source import TreeReportSource


class TreeSummaryContextBuilder:
    """Build prompt-ready tree summary contexts."""

    def build(self, *, source: TreeReportSource, completed_payload: dict, transcript: str) -> TreeSummaryContext:
        form_data = completed_payload.get("form", {}).get("data", {})
        mitigation_options = form_data.get("mitigation_options", {}).get("options", []) or []
        return TreeSummaryContext(
            source=source,
            crown_and_branches=dict(form_data.get("crown_and_branches", {}) or {}),
            trunk=dict(form_data.get("trunk", {}) or {}),
            roots_and_root_collar=dict(form_data.get("roots_and_root_collar", {}) or {}),
            tree_health_and_species=dict(form_data.get("tree_health_and_species", {}) or {}),
            risk_categorization=list(form_data.get("risk_categorization", []) or []),
            mitigation_options=[dict(item) for item in mitigation_options],
            transcript=_clean_transcript(transcript),
        )


def _clean_transcript(transcript: str) -> str:
    cleaned_blocks: list[str] = []
    for block in transcript.split("\n\n"):
        lowered = block.lower()
        if "software test" in lowered:
            continue
        cleaned_blocks.append(block.strip())
    return "\n\n".join(block for block in cleaned_blocks if block).strip()
