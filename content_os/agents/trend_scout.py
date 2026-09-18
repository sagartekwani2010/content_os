"""Trend Scout agent.

Finds candidate topics worth building content around. Explicitly not a news
summarizer: the agent's value is deciding what is interesting and what angle
exists, which is judgement. Identity, timestamps, and deduplication are handled
in Python afterwards.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any

from content_os.config import BrandMemory, ModelsConfig
from content_os.ids import new_id, slugify
from content_os.models.topics import (
    TopicCandidate,
    TopicDiscoveryResult,
    TopicStatus,
)
from content_os.tracking.run_logger import (
    TrackedResult,
    TrackedRunner,
    agent_instructions,
    build_agent,
)

AGENT_KEY = "trend_scout"


def build_context(
    brand: BrandMemory,
    sources: list[dict[str, Any]],
    existing_topics: list[str],
    recent_content: list[dict[str, Any]],
    max_topics: int,
) -> str:
    parts = [brand.as_prompt_context(), ""]

    parts.append(f"TASK: Review the source material and propose at most "
                 f"{max_topics} candidate topics.")
    parts.append("")

    if existing_topics:
        parts.append(
            "EXISTING CANDIDATE TOPICS (do not propose near-duplicates of these):"
        )
        parts += [f"  - {t}" for t in existing_topics[:60]]
        parts.append("")

    if recent_content:
        parts.append("RECENTLY PUBLISHED OR PLANNED CONTENT (avoid repeating):")
        for c in recent_content[:20]:
            parts.append(
                f"  - [{c.get('format', '?')}/{c.get('pillar', '?')}] {c.get('title', '')}"
            )
        parts.append("")

    parts.append(f"TODAY: {datetime.now(timezone.utc).date().isoformat()}")
    parts.append("")
    parts.append("SOURCE MATERIAL:")
    parts.append(json.dumps(sources, indent=2, default=str))

    return "\n".join(parts)


async def discover_topics(
    runner: TrackedRunner,
    brand: BrandMemory,
    sources: list[dict[str, Any]],
    *,
    existing_topics: list[str] | None = None,
    recent_content: list[dict[str, Any]] | None = None,
    max_topics: int = 10,
    models: ModelsConfig | None = None,
) -> TrackedResult[TopicDiscoveryResult]:
    agent, model, prompt_version = build_agent(
        AGENT_KEY,
        instructions=agent_instructions(AGENT_KEY, models),
        output_type=TopicDiscoveryResult,
        models=models,
        name="Trend Scout",
    )
    prompt = build_context(
        brand, sources, existing_topics or [], recent_content or [], max_topics
    )
    return await runner.run(
        agent,
        prompt,
        agent_key=AGENT_KEY,
        workflow_key="discover",
        model=model,
        prompt_version=prompt_version,
    )


def draft_to_candidate(draft: Any, run_id: str | None) -> TopicCandidate:
    """Convert an agent draft into a storable topic.

    Python owns the id, the discovery timestamp, and the canonical slug. The
    agent never sees or invents any of them.
    """
    event_date = None
    if getattr(draft, "event_date_iso", None):
        try:
            parsed = datetime.fromisoformat(draft.event_date_iso.replace("Z", "+00:00"))
            event_date = parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)
        except (ValueError, AttributeError):
            # A malformed date is dropped rather than guessed. Time decay runs
            # off this field, so a wrong date is worse than no date.
            event_date = None

    now = datetime.now(timezone.utc)
    freshness = None
    if event_date:
        freshness = max(0.0, (now - event_date).total_seconds() / 3600.0)

    return TopicCandidate(
        id=new_id("topic"),
        title=draft.title,
        canonical_topic=slugify(draft.canonical_topic),
        summary=draft.summary,
        source_urls=list(draft.source_urls),
        source_types=list(draft.source_types),
        discovered_at=now,
        event_date=event_date,
        trend_signals=list(draft.trend_signals),
        target_audience=list(draft.target_audience),
        potential_angles=list(draft.potential_angles),
        content_pillars=list(draft.content_pillars),
        estimated_saturation=float(draft.estimated_saturation),
        freshness_hours=freshness,
        status=TopicStatus.CANDIDATE,
        run_id=run_id,
        why_it_matters=getattr(draft, "why_it_matters", ""),
        discussion_angle=getattr(draft, "discussion_angle", ""),
    )
