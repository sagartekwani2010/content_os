"""Carousel Specialist agent."""

from __future__ import annotations

import json
from typing import Any

from content_os.config import BrandMemory, ModelsConfig
from content_os.models.content import CarouselPackage, ContentPlanItem
from content_os.models.topics import TopicCandidate
from content_os.tracking.run_logger import (
    TrackedResult,
    TrackedRunner,
    agent_instructions,
    build_agent,
)

AGENT_KEY = "carousel_writer"


def build_context(
    brand: BrandMemory,
    topic: TopicCandidate,
    plan_item: ContentPlanItem | None,
    *,
    slide_range: tuple[int, int],
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
        parts.append(f"  Cover hook direction: {plan_item.primary_hook}")
        parts.append(f"  Why this, this week: {plan_item.reasoning}")
        parts.append("")

    lo, hi = slide_range
    parts.append(f"TARGET: {lo}-{hi} slides. Use the fewest that carry the idea.")
    parts.append("")

    if recent_content:
        parts.append("RECENT CONTENT (do not repeat these angles):")
        for c in recent_content[:10]:
            parts.append(f"  - {c.get('title', '')}")
        parts.append("")

    if historical_insights:
        parts.append("WHAT HAS WORKED FOR THIS ACCOUNT:")
        parts += [f"  - {i}" for i in historical_insights[:10]]

    return "\n".join(parts)


async def write_carousel(
    runner: TrackedRunner,
    brand: BrandMemory,
    topic: TopicCandidate,
    *,
    plan_item: ContentPlanItem | None = None,
    content_id: str | None = None,
    recent_content: list[dict[str, Any]] | None = None,
    historical_insights: list[str] | None = None,
    models: ModelsConfig | None = None,
) -> TrackedResult[CarouselPackage]:
    agent, model, prompt_version = build_agent(
        AGENT_KEY,
        instructions=agent_instructions(AGENT_KEY, models),
        output_type=CarouselPackage,
        models=models,
        name="Carousel Specialist",
    )
    prompt = build_context(
        brand,
        topic,
        plan_item,
        slide_range=brand.production.carousel_slides,
        recent_content=recent_content or [],
        historical_insights=historical_insights or brand.historical_insights,
    )
    return await runner.run(
        agent,
        prompt,
        agent_key=AGENT_KEY,
        workflow_key="carousel",
        model=model,
        prompt_version=prompt_version,
        topic_id=topic.id,
        content_id=content_id,
        extra_metadata={
            "format": "carousel",
            "pillar": plan_item.pillar if plan_item else "",
        },
    )
