"""Tests for summary-slice generator and response parsing."""

from __future__ import annotations

import unittest
from unittest.mock import patch

from reporter_client.models.summary_prompts import SummaryPrompts
from reporter_client.services.summary_services import SummaryGenerator, _extract_json_payload, parse_summary_response


class SummaryGeneratorTests(unittest.TestCase):
    def setUp(self) -> None:
        self._env_patcher = patch.dict("os.environ", {"OPENAI_API_KEY": ""}, clear=False)
        self._env_patcher.start()

    def tearDown(self) -> None:
        self._env_patcher.stop()

    def test_generator_returns_stub_artifact_without_api_key(self) -> None:
        prompts = SummaryPrompts(
            system_prompt="system",
            user_prompt="Species: Quercus agrifolia",
            prompt_version="tree-v1",
        )

        artifact = SummaryGenerator().generate(
            page_kind="tree",
            source_identifier="job-123",
            prompts=prompts,
        )

        self.assertEqual(artifact.page_kind, "tree")
        self.assertEqual(artifact.source_identifier, "job-123")
        self.assertEqual(artifact.model_name, "stub-summary-generator")
        self.assertEqual(artifact.prompt_version, "tree-v1")
        self.assertIn("Quercus agrifolia", artifact.summary_text)
        self.assertEqual(
            artifact.narrative_blocks,
            [
                "Tree summary paragraph two.",
                "Tree summary paragraph three.",
                "Tree summary paragraph four.",
                "Tree summary paragraph five.",
            ],
        )

    def test_parse_summary_response_accepts_valid_payload(self) -> None:
        response = parse_summary_response(
            '{"summary_text":"Lead summary.","narrative_blocks":["Paragraph 1.","Paragraph 2."]}'
        )

        self.assertEqual(response.summary_text, "Lead summary.")
        self.assertEqual(response.narrative_blocks, ["Paragraph 1.", "Paragraph 2."])

    def test_parse_summary_response_rejects_non_array_narrative_blocks(self) -> None:
        with self.assertRaisesRegex(ValueError, "narrative_blocks must be a JSON array"):
            parse_summary_response('{"summary_text":"Lead summary.","narrative_blocks":"Paragraph 1."}')

    def test_parse_summary_response_rejects_wrong_paragraph_count(self) -> None:
        with self.assertRaisesRegex(ValueError, "narrative_blocks must contain 2 to 4 paragraphs"):
            parse_summary_response('{"summary_text":"Lead summary.","narrative_blocks":["Paragraph 1."]}')

    def test_parse_summary_response_normalizes_tree_five_block_payload(self) -> None:
        response = parse_summary_response(
            '{"summary_text":"Lead summary.","narrative_blocks":["Paragraph 1.","Paragraph 2.","Paragraph 3.","Paragraph 4.","Paragraph 5."]}',
            page_kind="tree",
        )

        self.assertEqual(response.summary_text, "Paragraph 1.")
        self.assertEqual(
            response.narrative_blocks,
            ["Paragraph 2.", "Paragraph 3.", "Paragraph 4.", "Paragraph 5."],
        )

    def test_parse_summary_response_requires_four_tree_narrative_blocks(self) -> None:
        with self.assertRaisesRegex(ValueError, "tree narrative_blocks must contain 5 paragraphs or 4 paragraphs with summary_text"):
            parse_summary_response(
                '{"summary_text":"Lead summary.","narrative_blocks":["Paragraph 1.","Paragraph 2.","Paragraph 3."]}',
                page_kind="tree",
            )

    def test_parse_summary_response_requires_summary_text(self) -> None:
        with self.assertRaisesRegex(ValueError, "summary_text is required"):
            parse_summary_response('{"summary_text":"","narrative_blocks":["Paragraph 1.","Paragraph 2."]}')

    def test_extract_json_payload_strips_markdown_fences(self) -> None:
        payload = _extract_json_payload(
            '```json\n{"summary_text":"Lead summary.","narrative_blocks":["Paragraph 1.","Paragraph 2."]}\n```'
        )

        self.assertEqual(
            payload,
            '{"summary_text":"Lead summary.","narrative_blocks":["Paragraph 1.","Paragraph 2."]}',
        )


if __name__ == "__main__":
    unittest.main()
