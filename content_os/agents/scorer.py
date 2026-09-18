"""Opportunity Scorer agent.

Rates a topic on six dimensions and estimates saturation. Returns judgements
only. The weighted total, the time decay, the saturation penalty, and the
brand-fit veto are all computed in content_os.tools.scoring, so the arithmetic
is testable and the model cannot quietly change how ranking works.
"""

from __future__ import annotations

import json

from content_os.config import BrandMemory, ModelsConfig, ScoringConfig
from content_os.models.topics import TopicCandidate, TopicRating
from content_os.tracking.run_logger import (
    TrackedResult,
    TrackedRunner,
    agent_instructions,
    build_agent,
)

AGENT_KEY = "scorer"


def build_context(
    brand: BrandMemory,
    topic: TopicCandidate,
    cfg: ScoringConfig,
    historical_insights: list[str] | None = None,
) -> str:
    parts = [brand.as_prompt_context(), ""]

    parts.append("TOPIC TO SCORE:")
    parts.append(
        json.dumps(
            {
                "title": topic.title,
                "summary": topic.summary,
                "why_it_matters": topic.why_it_matters,
                "discussion_angle": topic.discussion_angle,
                "potential_angles": topic.potential_angles,
                "trend_signals": topic.trend_signals,
                "content_pillars": topic.content_pillars,
                "target_audience": topic.target_audience,
                "source_types": topic.source_types,
                "source_count": len(topic.source_urls),
                "event_date": topic.event_date.isoformat() if topic.event_date else None,
                "scout_estimated_saturation": topic.estimated_saturation,
            },
            indent=2,
        )
    )
    parts.append("")
    parts.append(f"VALID PILLAR KEYS: {', '.join(brand.pillar_keys)}")
    parts.append("VALID FORMATS: reel, carousel, trial_reel")
    parts.append("")

    # The veto threshold is surfaced so the agent understands the consequence of
    # a low brand-fit rating, but the rule itself is enforced in Python.
    parts.append(
        f"NOTE: a brand_fit rating below {cfg.brand_fit_veto.threshold} means this "
        f"topic cannot be automatically recommended, regardless of how high the "
        f"other dimensions are. Rate honestly; the rule is applied in code, not "
        f"by you."
    )

    if historical_insights:
        parts.append("")
        parts.append("WHAT PAST PERFORMANCE HAS SHOWN FOR THIS ACCOUNT:")
        parts += [f"  - {i}" for i in historical_insights[:10]]

    return "\n".join(parts)


async def rate_topic(
    runner: TrackedRunner,
    brand: BrandMemory,
    topic: TopicCandidate,
    cfg: ScoringConfig,
    *,
    historical_insights: list[str] | None = None,
    models: ModelsConfig | None = None,
) -> TrackedResult[TopicRating]:
    agent, model, prompt_version = build_agent(
        AGENT_KEY,
        instructions=agent_instructions(AGENT_KEY, models),
        output_type=TopicRating,
        models=models,
        name="Opportunity Scorer",
    )
    prompt = build_context(brand, topic, cfg, historical_insights)
    return await runner.run(
        agent,
        prompt,
        agent_key=AGENT_KEY,
        workflow_key="score",
        model=model,
        prompt_version=prompt_version,
        topic_id=topic.id,
    )
