"""Reel Specialist agent."""

from __future__ import annotations

import json
from typing import Any

from content_os.config import BrandMemory, ModelsConfig
from content_os.models.brief import ContentBrief, ExecutionPlan
from content_os.models.content import ContentPlanItem, ReelPackage
from content_os.models.topics import TopicCandidate
from content_os.tracking.run_logger import (
    TrackedResult,
    TrackedRunner,
    agent_instructions,
    build_agent,
)

AGENT_KEY = "reel_writer"


def build_context(
    brand: BrandMemory,
    topic: TopicCandidate,
    plan_item: ContentPlanItem | None,
    *,
    duration_hint: tuple[int, int],
    recent_content: list[dict[str, Any]],
    historical_insights: list[str],
) -> str:
    parts = [brand.as_prompt_context(), ""]

    parts.append("TOPIC:")
    parts.append(
        json.dumps(
            {
                "title": topic.title,
                "summary": topic.summary,
                "why_it_matters": topic.why_it_matters,
                "discussion_angle": topic.discussion_angle,
                "potential_angles": topic.potential_angles,
                "trend_signals": topic.trend_signals,
                "source_urls": topic.source_urls,
            },
            indent=2,
        )
    )
    parts.append("")

    if plan_item:
        parts.append("STRATEGIC BRIEF FROM THE CONTENT STRATEGIST:")
        parts.append(f"  Working title: {plan_item.proposed_title}")
        parts.append(f"  Pillar: {plan_item.pillar}")
        parts.append(f"  Strategic role: {plan_item.strategic_role}")
        parts.append(f"  Urgency: {plan_item.urgency}")
        parts.append(f"  Primary hook direction: {plan_item.primary_hook}")
        if plan_item.alternate_hooks:
            parts.append(f"  Alternate hook directions: {plan_item.alternate_hooks}")
        parts.append(f"  Why this, this week: {plan_item.reasoning}")
        parts.append("")

    lo, hi = duration_hint
    parts.append(f"TARGET DURATION: {lo}-{hi} seconds. Shorter is usually better.")
    parts.append(
        f"AVATAR SHARE: roughly "
        f"{int(brand.production.avatar_share_target * 100)}% of Reels are "
        f"avatar-delivered. Prefer avatar unless the idea genuinely needs "
        f"something else, and say so explicitly if it does."
    )
    parts.append(f"PRODUCTION MODES: {', '.join(brand.production.available_modes)}")
    parts.append("")

    if recent_content:
        parts.append("RECENT CONTENT (do not repeat these hooks or angles):")
        for c in recent_content[:10]:
            parts.append(f"  - {c.get('title', '')} | hook: {c.get('hook') or 'n/a'}")
        parts.append("")

    if historical_insights:
        parts.append("WHAT HAS WORKED FOR THIS ACCOUNT:")
        parts += [f"  - {i}" for i in historical_insights[:10]]

    return "\n".join(parts)


async def write_reel(
    runner: TrackedRunner,
    brand: BrandMemory,
    topic: TopicCandidate,
    *,
    plan_item: ContentPlanItem | None = None,
    content_id: str | None = None,
    recent_content: list[dict[str, Any]] | None = None,
    historical_insights: list[str] | None = None,
    models: ModelsConfig | None = None,
) -> TrackedResult[ReelPackage]:
    agent, model, prompt_version = build_agent(
        AGENT_KEY,
        instructions=agent_instructions(AGENT_KEY, models),
        output_type=ReelPackage,
        models=models,
        name="Reel Specialist",
    )
    prompt = build_context(
        brand,
        topic,
        plan_item,
        duration_hint=brand.production.default_reel_seconds,
        recent_content=recent_content or [],
        historical_insights=historical_insights or brand.historical_insights,
    )
    return await runner.run(
        agent,
        prompt,
        agent_key=AGENT_KEY,
        workflow_key="reel",
        model=model,
        prompt_version=prompt_version,
        topic_id=topic.id,
        content_id=content_id,
        extra_metadata={"format": "reel", "pillar": plan_item.pillar if plan_item else ""},
    )


# --------------------------------------------------------------------------
# Brief-driven path. The human owns strategy; this writes the execution.
# --------------------------------------------------------------------------


def build_brief_context(
    brand: BrandMemory,
    brief: "ContentBrief",
    plan: "ExecutionPlan",
    selected_hook: str,
    alternate_hooks: list[str],
    recent_content: list[dict[str, Any]],
) -> str:
    parts = [brief.as_prompt_context(), ""]

    parts.append("=== EXECUTION PLAN (approved sequencing) ===")
    parts.append(f"Opening strategy: {plan.opening_strategy}")
    parts.append("Narrative arc:")
    parts += [f"  {i}. {beat}" for i, beat in enumerate(plan.narrative_arc, 1)]
    parts.append("Key learning points:")
    parts += [f"  - {p}" for p in plan.key_learning_points]
    parts.append("Supporting examples:")
    parts += [f"  - {e}" for e in plan.supporting_examples]
    parts.append("Visual beats:")
    parts += [f"  - {v}" for v in plan.visual_beats]
    parts.append(f"Closing strategy: {plan.closing_strategy}")
    parts.append("Section coverage plan:")
    parts += [f"  - {c}" for c in plan.section_coverage_plan]

    parts += ["", "=== SELECTED HOOK (use this) ===", selected_hook]
    if alternate_hooks:
        parts.append("Alternates to carry through unchanged:")
        parts += [f"  - {h}" for h in alternate_hooks]

    parts += ["", "=== BRAND ===", brand.as_prompt_context()]

    if recent_content:
        parts += ["", "RECENT CONTENT (do not repeat):"]
        for c in recent_content[:10]:
            parts.append(f"  - {c.get('title', '')}")

    parts += [
        "",
        f"Write the reel. Cover every mandatory section and list them in "
        "sections_covered using the brief's wording. learning_payoff, "
        "save_reason and share_reason are required and must be specific.",
    ]
    return "\n".join(parts)


async def write_reel_from_brief(
    runner: TrackedRunner,
    brand: BrandMemory,
    brief: "ContentBrief",
    plan: "ExecutionPlan",
    *,
    selected_hook: str,
    alternate_hooks: list[str],
    content_id: str | None = None,
    recent_content: list[dict[str, Any]] | None = None,
    models: ModelsConfig | None = None,
) -> TrackedResult[ReelPackage]:
    agent, model, prompt_version = build_agent(
        AGENT_KEY,
        instructions=agent_instructions(AGENT_KEY, models),
        output_type=ReelPackage,
        models=models,
        name="Reel Specialist",
    )
    result = await runner.run(
        agent,
        build_brief_context(
            brand, brief, plan, selected_hook, alternate_hooks, recent_content or []
        ),
        agent_key=AGENT_KEY,
        workflow_key="produce",
        model=model,
        prompt_version=prompt_version,
        content_id=content_id,
        extra_metadata={"brief_id": brief.brief_id, "format": "reel"},
    )
    # The brief owns identity. Reassert rather than trusting it survived.
    result.output.brief_id = brief.brief_id
    return result


async def rewrite_reel_after_story_review(
    runner: TrackedRunner,
    brand: BrandMemory,
    package: ReelPackage,
    review: Any,
    *,
    topic_title: str,
    content_id: str | None = None,
    models: ModelsConfig | None = None,
    brief: ContentBrief | None = None,
) -> TrackedResult[ReelPackage]:
    """Apply one targeted narrative revision before any asset work starts."""
    agent, model, prompt_version = build_agent(
        AGENT_KEY,
        instructions=agent_instructions(AGENT_KEY, models),
        output_type=ReelPackage,
        models=models,
        name="Reel Specialist Revision",
    )
    parts: list[str] = []
    if brief is not None:
        parts += [brief.as_prompt_context(), ""]
    parts += [
        brand.as_prompt_context(),
        "",
        f"UNDERLYING TOPIC: {topic_title}",
        "",
        "THE REEL BELOW FAILED A STORY REVIEW. Rewrite it once. Preserve the "
        "brief, factual claims, learning payoff and topic. Do not merely polish "
        "sentences: remove repetition, create a distinct story turn and make "
        "each scene earn its time.",
        "",
        "STORY REVIEW:",
        review.model_dump_json(indent=2),
        "",
        "CURRENT REEL:",
        package.model_dump_json(indent=2),
    ]
    result = await runner.run(
        agent,
        "\n".join(parts),
        agent_key=AGENT_KEY,
        workflow_key="story_revision",
        model=model,
        prompt_version=prompt_version,
        content_id=content_id,
        extra_metadata={"format": "reel", "revision_reason": "story_judge"},
    )
    if brief is not None:
        result.output.brief_id = brief.brief_id
    return result
