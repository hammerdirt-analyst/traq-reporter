"""Shared generation boundary for page-level summaries."""

from __future__ import annotations

import json
import logging
import os
from datetime import UTC, datetime

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover - optional local dependency
    load_dotenv = None

try:
    from openai import OpenAI
except ImportError:  # pragma: no cover - optional local dependency
    OpenAI = None

from ...models.summary_artifacts import SummaryArtifact, SummaryResponse
from ...models.summary_prompts import SummaryPrompts


logger = logging.getLogger("reporter_client.summary")


class SummaryGenerator:
    """Shared generation boundary for page-level summaries."""

    def __init__(self) -> None:
        if load_dotenv is not None:
            load_dotenv()

    def generate(self, *, page_kind: str, source_identifier: str, prompts: SummaryPrompts) -> SummaryArtifact:
        now = datetime.now(UTC).isoformat()
        response_payload, model_name = self._generate_response_payload(prompts, page_kind=page_kind)
        try:
            response = parse_summary_response(response_payload, page_kind=page_kind)
        except (json.JSONDecodeError, ValueError):
            logger.exception(
                "failed to parse %s summary response for %s; payload excerpt=%r",
                page_kind,
                source_identifier,
                response_payload[:1200],
            )
            raise
        return SummaryArtifact(
            page_kind=page_kind,
            source_identifier=source_identifier,
            model_name=model_name,
            prompt_version=prompts.prompt_version,
            generated_at=now,
            summary_text=response.summary_text,
            narrative_blocks=response.narrative_blocks,
        )

    def _generate_response_payload(self, prompts: SummaryPrompts, *, page_kind: str) -> tuple[str, str]:
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            return _build_stub_response_payload(prompts.user_prompt, page_kind=page_kind), "stub-summary-generator"
        if OpenAI is None:
            raise RuntimeError(
                "OpenAI dependency is not installed. Run `uv sync` to install project dependencies."
            )

        model = os.environ.get("REPORTER_OPENAI_SUMMARY_MODEL", "gpt-4o-mini")
        logger.info("requesting %s summary from model %s", page_kind, model)
        client = OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": prompts.system_prompt},
                {"role": "user", "content": prompts.user_prompt},
            ],
            temperature=0.2,
        )
        content = response.choices[0].message.content if response.choices else ""
        payload = _extract_json_payload((content or "").strip())
        return payload, model


def parse_summary_response(payload: str, *, page_kind: str = "generic") -> SummaryResponse:
    data = json.loads(payload)
    if not isinstance(data, dict):
        raise ValueError("Summary response must be a JSON object")

    summary_text = str(data.get("summary_text", "")).strip()
    narrative_blocks_raw = data.get("narrative_blocks", [])
    if not isinstance(narrative_blocks_raw, list):
        raise ValueError("narrative_blocks must be a JSON array")

    narrative_blocks = [str(item).strip() for item in narrative_blocks_raw if str(item).strip()]
    if page_kind == "tree":
        if len(narrative_blocks) == 5:
            summary_text = narrative_blocks[0]
            narrative_blocks = narrative_blocks[1:]
        elif len(narrative_blocks) == 4 and summary_text:
            pass
        else:
            raise ValueError("tree narrative_blocks must contain 5 paragraphs or 4 paragraphs with summary_text")
    elif not summary_text:
        raise ValueError("summary_text is required")
    if not summary_text:
        raise ValueError("summary_text is required")
    if page_kind != "tree" and (len(narrative_blocks) < 2 or len(narrative_blocks) > 4):
        raise ValueError("narrative_blocks must contain 2 to 4 paragraphs")

    return SummaryResponse(
        summary_text=summary_text,
        narrative_blocks=narrative_blocks,
    )


def _extract_json_payload(content: str) -> str:
    if not content:
        raise ValueError("Summary generator returned empty content")
    stripped = content.strip()
    if stripped.startswith("```"):
        lines = stripped.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        stripped = "\n".join(lines).strip()
    return stripped


def _build_stub_response_payload(user_prompt: str, *, page_kind: str) -> str:
    if page_kind == "tree":
        return json.dumps(
            {
                "summary_text": "",
                "narrative_blocks": [
                    _build_stub_summary(user_prompt),
                    "Tree summary paragraph two.",
                    "Tree summary paragraph three.",
                    "Tree summary paragraph four.",
                    "Tree summary paragraph five.",
                ],
            }
        )
    return json.dumps(
        {
            "summary_text": _build_stub_summary(user_prompt),
            "narrative_blocks": [
                "I have been summarized.",
                "I have been summarized again for layout testing.",
            ],
        }
    )


def _build_stub_summary(user_prompt: str) -> str:
    for line in user_prompt.splitlines():
        if line.startswith("Species: "):
            return f"Tree assessment summary for {line.removeprefix('Species: ').strip()}."
        if line.startswith("Project name: "):
            return f"I have been summarized for {line.removeprefix('Project name: ').strip()}."
        if line.startswith("Site title: "):
            return f"I have been summarized for {line.removeprefix('Site title: ').strip()}."
    return "I have been summarized."
