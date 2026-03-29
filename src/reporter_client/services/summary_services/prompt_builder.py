"""Prompt builders for page-level summaries."""

from __future__ import annotations

import json

from ...models.summary_contexts import HomeSummaryContext, ProjectSummaryContext, TreeSummaryContext
from ...models.summary_prompts import SummaryPrompts


def build_tree_summary_prompts(context: TreeSummaryContext) -> SummaryPrompts:
    source = context.source
    system_prompt = (
        "You are a professional arborist report writer. "
        "Write clear, client-facing narrative text using extracted field data as the primary source of truth "
        "and transcript content as supporting context. Use complete sentences, no bullets, no direct quotes, "
        "and a conservative factual tone."
    )
    user_prompt = (
        "Return valid JSON only with this shape:\n"
        '{\"summary_text\": \"...\", \"narrative_blocks\": [\"...\", \"...\"]}\n'
        "The narrative_blocks array must contain 2 to 4 paragraphs.\n"
        "Do not wrap the JSON in markdown fences.\n\n"
        "Write 2 to 4 short paragraphs for a tree assessment page.\n"
        "Present the tree, the conditions of concern, and proposed mitigation options in an easy-to-read format.\n"
        "Use extracted form values as primary truth.\n"
        "Use transcript content only as supporting context.\n"
        "Do not include assessor contact information.\n"
        "Do not quote the transcript directly.\n"
        "Do not invent observations.\n\n"
        "Cover these topics across the summary:\n"
        "1) overall tree identity and general condition\n"
        "2) crown and branches, trunk, roots/root collar, and tree health/species context\n"
        "3) conditions of concern from risk categorization\n"
        "4) proposed mitigation options only if they are present in source data\n\n"
        f"Species: {source.species}\n"
        f"DBH: {source.dbh}\n"
        f"Height: {source.height}\n"
        f"Overall tree risk: {source.risk_profile.overall_tree_risk}\n"
        f"Residual risk: {source.risk_profile.overall_residual_risk}\n"
        f"Inspection interval: {source.risk_profile.recommended_inspection_interval}\n\n"
        "Crown and branches (JSON):\n"
        f"{json.dumps(context.crown_and_branches, ensure_ascii=True)}\n\n"
        "Trunk (JSON):\n"
        f"{json.dumps(context.trunk, ensure_ascii=True)}\n\n"
        "Roots and root collar (JSON):\n"
        f"{json.dumps(context.roots_and_root_collar, ensure_ascii=True)}\n\n"
        "Tree health and species (JSON):\n"
        f"{json.dumps(context.tree_health_and_species, ensure_ascii=True)}\n\n"
        "Conditions of concern / risk categorization (JSON):\n"
        f"{json.dumps(context.risk_categorization, ensure_ascii=True)}\n\n"
        "Mitigation options (JSON):\n"
        f"{json.dumps(context.mitigation_options, ensure_ascii=True)}\n\n"
        "Transcript:\n"
        f"{context.transcript}\n"
    )
    return SummaryPrompts(system_prompt=system_prompt, user_prompt=user_prompt, prompt_version="tree-v1")


def build_project_summary_prompts(context: ProjectSummaryContext) -> SummaryPrompts:
    system_prompt = (
        "You are a professional arborist report writer. "
        "Write clear project-level narrative summary text for clients based on stable project description "
        "and current assessment activity."
    )
    user_prompt = (
        "Return valid JSON only with this shape:\n"
        '{\"summary_text\": \"...\", \"narrative_blocks\": [\"...\", \"...\"]}\n'
        "The narrative_blocks array must contain 2 to 4 paragraphs.\n"
        "Do not wrap the JSON in markdown fences.\n\n"
        "Write a concise project summary.\n"
        "Use the stable project description as context.\n"
        "Use the current set of tree assessments to describe current activity without overstating conclusions.\n\n"
        f"Project name: {context.project_name}\n"
        f"Stable description: {context.stable_description}\n"
        f"Assessment count: {context.project_source.tree_count}\n"
        f"Species count: {context.project_source.species_count}\n"
        f"Earliest assessment: {context.project_source.earliest_archived_at}\n"
        f"Latest assessment: {context.project_source.latest_archived_at}\n"
    )
    return SummaryPrompts(system_prompt=system_prompt, user_prompt=user_prompt, prompt_version="project-v1")


def build_home_summary_prompts(context: HomeSummaryContext) -> SummaryPrompts:
    system_prompt = (
        "You are a professional arborist report writer. "
        "Write clear site-wide narrative summary text for clients using project-level summaries and stable framing."
    )
    joined_project_summaries = "\n".join(context.project_summaries)
    user_prompt = (
        "Return valid JSON only with this shape:\n"
        '{\"summary_text\": \"...\", \"narrative_blocks\": [\"...\", \"...\"]}\n'
        "The narrative_blocks array must contain 2 to 4 paragraphs.\n"
        "Do not wrap the JSON in markdown fences.\n\n"
        "Write a concise home-page summary.\n"
        "Use the stable introduction as framing.\n"
        "Use the project summaries to describe current activity across the site.\n\n"
        f"Site title: {context.home_source.site_title}\n"
        f"Stable intro: {context.stable_intro}\n"
        f"Project count: {context.home_source.project_count}\n"
        f"Tree count: {context.home_source.tree_count}\n"
        f"Species count: {context.home_source.species_count}\n"
        f"Earliest assessment: {context.home_source.earliest_archived_at}\n"
        f"Latest assessment: {context.home_source.latest_archived_at}\n"
        "Project summaries:\n"
        f"{joined_project_summaries}\n"
    )
    return SummaryPrompts(system_prompt=system_prompt, user_prompt=user_prompt, prompt_version="home-v1")
