"""Prompt builders for page-level summaries."""

from __future__ import annotations

import json

from ...models.summary_contexts import TreeSummaryContext
from ...models.summary_prompts import SummaryPrompts


def build_tree_summary_prompts(context: TreeSummaryContext) -> SummaryPrompts:
    source = context.source
    form_data = {
        "site_factors": context.site_factors,
        "target_assessment": context.target_assessment,
        "load_factors": context.load_factors,
        "crown_and_branches": context.crown_and_branches,
        "trunk": context.trunk,
        "roots_and_root_collar": context.roots_and_root_collar,
        "tree_health_and_species": context.tree_health_and_species,
        "risk_categorization": context.risk_categorization,
        "mitigation_options": context.mitigation_options,
    }
    system_prompt = (
        "You are a professional arborist report writer. "
        "Write clear, client-facing narrative text from a TRAQ assessment form. "
        "Use complete sentences, no bullets, and a conservative factual tone appropriate for a legal document. "
        "Do not add any advice or reccomendations or commentary report what is in the form data"
    )
    user_prompt = (
        "Return valid JSON only with this shape:\n"
        '{"summary_text": "...", "narrative_blocks": ["...", "..."]}\n'
        "The narrative_blocks array must contain exactly 5 paragraphs.\n"
        "Do not wrap the JSON in markdown fences.\n\n"
        "Write five short paragraphs in this exact order:\n"
        "1) Combine site factors with the tree details and assessment context.\n"
        "2) Target assessment with tree health & species profile. Explicitly name the targets and describe how far they are (e.g., within dripline, within 1x height).\n"
        "3) Crown & branches and trunk defects together.\n"
        "4) Roots & root collar with load factors.\n"
        "5) Overall risk, mitigation option(s), and expected residual risk after mitigation.\n\n"
        "Do not repeat customer contact info or job address; those belong in the letter header.\n"
        "Do not mention the assessor in the body; that belongs in the signature block.\n"
        "Use extracted form data as the primary source of truth (this reflects user-reviewed corrections).\n"
        "Keep language conservative and factual for a legal document; do not overstate certainty.\n"
        "Do not add conclusions or recommendations.\n\n"
        f"Species: {source.species}\n"
        f"DBH: {source.dbh}\n"
        f"Height: {source.height}\n"
        f"Overall tree risk: {source.risk_profile.overall_tree_risk}\n"
        f"Residual risk: {source.risk_profile.overall_residual_risk}\n"
        f"Inspection interval: {source.risk_profile.recommended_inspection_interval}\n\n"
        "Extracted form data (JSON):\n"
        f"{json.dumps(form_data, ensure_ascii=True)}\n"
    )
    return SummaryPrompts(system_prompt=system_prompt, user_prompt=user_prompt, prompt_version="tree-v1")
