"""Performance Analyst agent.

Interprets measured performance. Every number it sees was computed
deterministically; the agent's job is meaning and confidence, and the schema
forces it to separate observation from hypothesis from recommendation so a guess
never feeds back into scoring as a fact.
"""

from __future__ import annotations

import json
from typing import Any

from content_os.config import BrandMemory, ModelsConfig
from content_os.models.experiments import PerformanceAnalysis
from content_os.tracking.run_logger import (
    TrackedResult,
    TrackedRunner,
    agent_instructions,
    build_agent,
)

AGENT_KEY = "performance_analyst"


def build_context(
    brand: BrandMemory,
    analytics: dict[str, Any],
    dimension_correlation: dict[str, Any],
    *,
    measured_posts: int,
) -> str:
    parts = [brand.as_prompt_context(), ""]

    parts.append(f"MEASURED POSTS AVAILABLE: {measured_posts}")
    if measured_posts < 5:
        parts.append(
            "WARNING: this is a very small sample. Almost nothing here can "
            "support a high-confidence conclusion. Say so plainly rather than "
            "manufacturing insight."
        )
    parts.append("")

    parts.append("AGGREGATED PERFORMANCE (computed deterministically, not by you):")
    parts.append(json.dumps(analytics, indent=2, default=str)[:12000])
    parts.append("")

    parts.append("OPPORTUNITY SCORE DIMENSION CORRELATION WITH PERFORMANCE:")
    parts.append(json.dumps(dimension_correlation, indent=2, default=str)[:3000])
    parts.append("")
    parts.append(
        "A null correlation means insufficient data or no variance, not a weak "
        "relationship. Report it as 'cannot tell yet'."
    )

    return "\n".join(parts)


async def analyse(
    runner: TrackedRunner,
    brand: BrandMemory,
    analytics: dict[str, Any],
    dimension_correlation: dict[str, Any],
    *,
    measured_posts: int,
    models: ModelsConfig | None = None,
) -> TrackedResult[PerformanceAnalysis]:
    agent, model, prompt_version = build_agent(
        AGENT_KEY,
        instructions=agent_instructions(AGENT_KEY, models),
        output_type=PerformanceAnalysis,
        models=models,
        name="Performance Analyst",
    )
    prompt = build_context(
        brand, analytics, dimension_correlation, measured_posts=measured_posts
    )
    return await runner.run(
        agent,
        prompt,
        agent_key=AGENT_KEY,
        workflow_key="analyze",
        model=model,
        prompt_version=prompt_version,
    )
