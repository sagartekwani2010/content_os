"""Brand Miner agent.

Generates topics from the brand rather than from the news.

Every other topic source here is reactive: the scout waits for something to
happen. That produces competent topical commentary and no persona. Series
episodes, identity content, and recurring experiment formats have to be
generated from the brand profile itself, and nothing else in the pipeline can
produce them.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, Field

from content_os.config import BrandMemory, ModelsConfig
from content_os.ids import new_id, slugify
from content_os.models.topics import TopicCandidate, TopicStatus
from content_os.tracking.run_logger import (
    TrackedResult,
    TrackedRunner,
    agent_instructions,
    build_agent,
)

AGENT_KEY = "brand_miner"


class BrandTopic(BaseModel):
    title: str
    canonical_topic: str
    summary: str

    origin: str
    series_name: str | None

    why_only_this_brand: str
    discussion_angle: str

    potential_angles: list[str]
    content_pillars: list[str]
    target_audience: list[str]

    requires_work: list[str]
    estimated_saturation: float = Field(ge=0.0, le=1.0)


class BrandMiningResult(BaseModel):
    topics: list[BrandTopic]
    rationale: str


def build_context(
    brand: BrandMemory,
    existing_topics: list[str],
    recent_content: list[dict[str, Any]],
    max_topics: int,
) -> str:
    parts = [brand.as_prompt_context(), ""]
    parts.append(
        f"TASK: Propose at most {max_topics} topics generated from the brand "
        f"itself. Cover every signature series with at least one concrete "
        f"episode, plus identity content and experiment formats."
    )
    parts.append("")
    parts.append(f"VALID PILLAR KEYS: {', '.join(brand.pillar_keys)}")
    parts.append("")

    if existing_topics:
        parts.append("EXISTING TOPICS (do not duplicate these):")
        parts += [f"  - {t}" for t in existing_topics[:60]]
        parts.append("")

    if recent_content:
        parts.append("RECENT CONTENT (do not repeat these):")
        for c in recent_content[:15]:
            parts.append(f"  - [{c.get('format', '?')}] {c.get('title', '')}")

    return "\n".join(parts)


async def mine(
    runner: TrackedRunner,
    brand: BrandMemory,
    *,
    existing_topics: list[str] | None = None,
    recent_content: list[dict[str, Any]] | None = None,
    max_topics: int = 10,
    models: ModelsConfig | None = None,
) -> TrackedResult[BrandMiningResult]:
    agent, model, prompt_version = build_agent(
        AGENT_KEY,
        instructions=agent_instructions(AGENT_KEY, models),
        output_type=BrandMiningResult,
        models=models,
        name="Brand Miner",
    )
    prompt = build_context(
        brand, existing_topics or [], recent_content or [], max_topics
    )
    return await runner.run(
        agent,
        prompt,
        agent_key=AGENT_KEY,
        workflow_key="mine",
        model=model,
        prompt_version=prompt_version,
    )


def to_candidate(topic: BrandTopic, run_id: str | None) -> TopicCandidate:
    """Convert a mined topic into a storable candidate.

    Signals record where the idea came from, so a later analysis can ask whether
    brand-generated topics outperform reactive ones. That is a question worth
    being able to answer.
    """
    signals = [f"origin:{topic.origin}"]
    if topic.series_name:
        signals.append(f"series:{topic.series_name}")
    signals += [f"requires:{w}" for w in topic.requires_work[:4]]

    return TopicCandidate(
        id=new_id("topic"),
        title=topic.title,
        canonical_topic=slugify(topic.canonical_topic),
        summary=topic.summary,
        source_urls=[],
        source_types=["brand_memory"],
        discovered_at=datetime.now(timezone.utc),
        event_date=None,
        trend_signals=signals,
        target_audience=list(topic.target_audience),
        potential_angles=list(topic.potential_angles),
        content_pillars=list(topic.content_pillars),
        estimated_saturation=float(topic.estimated_saturation),
        status=TopicStatus.CANDIDATE,
        run_id=run_id,
        why_it_matters=topic.why_only_this_brand,
        discussion_angle=topic.discussion_angle,
    )
