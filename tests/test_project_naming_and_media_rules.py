"""Tests for shared naming and media-selection rules."""

from __future__ import annotations

import unittest

from reporter_client.services.media_rules import is_lead_tree_caption
from reporter_client.services.project_naming import project_slug


class ProjectNamingAndMediaRuleTests(unittest.TestCase):
    def test_project_slug_normalizes_spacing_and_case(self) -> None:
        self.assertEqual(project_slug("American River"), "american-river")
        self.assertEqual(project_slug("  Briarwood "), "briarwood")

    def test_is_lead_tree_caption_uses_explicit_prefix_rule(self) -> None:
        self.assertTrue(is_lead_tree_caption("The tree: east-facing view"))
        self.assertTrue(is_lead_tree_caption("  the tree: in the middle"))
        self.assertFalse(is_lead_tree_caption("tree in the middle"))
        self.assertFalse(is_lead_tree_caption("trunk"))


if __name__ == "__main__":
    unittest.main()
