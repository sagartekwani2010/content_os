"""Reel Specialist agent."""

from __future__ import annotations

import json
from typing import Any

from content_os.config import BrandMemory, ModelsConfig
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
