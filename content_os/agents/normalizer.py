"""Normalizer agent.

Canonicalizes topics, assigns consistent tags, and catches semantic duplicates
that exact string matching missed.

Deliberately runs after the deterministic slug match rather than instead of it.
Exact duplicates are settled in Python for free; the model only sees the residue
that actually needs judgement. That keeps the highest-volume agent in the system
shallow and cheap, which is why it runs on the smallest model at low effort.
"""

from __future__ import annotations

import json
from typing import Any

from pydantic import BaseModel, Field

from content_os.config import ModelsConfig
from content_os.ids import slugify
from content_os.models.topics import TopicCandidate
from content_os.tracking.run_logger import (
    TrackedResult,
    TrackedRunner,
    agent_instructions,
    build_agent,
)

AGENT_KEY = "normalizer"

# Only a high-confidence duplicate is merged automatically. A wrongly discarded
# topic is invisible and unrecoverable; a duplicate that slips through is
# obvious and cheap to remove.
AUTO_MERGE_CONFIDENCE = "high"


class NormalizedTopic(BaseModel):
    index: int = Field(description="Position of the topic in the input list.")
    canonical_topic: str
    tags: list[str]
    duplicate_of_id: str | None
    duplicate_confidence: str
    normalization_note: str


class NormalizationResult(BaseModel):
    topics: list[NormalizedTopic]


def build_context(
    candidates: list[TopicCandidate], existing: list[dict[str, str]]
) -> str:
    parts = ["NEW TOPICS TO NORMALIZE:"]
    parts.append(
        json.dumps(
            [
                {
                    "index": index,
                    "title": topic.title,
                    "proposed_canonical": topic.canonical_topic,
                    "summary": topic.summary[:400],
                }
                for index, topic in enumerate(candidates)
            ],
            indent=2,
        )
    )
    parts.append("")

    if existing:
        parts.append(
            "EXISTING TOPICS IN THE DATABASE (check for semantic duplicates):"
        )
        parts.append(json.dumps(existing[:80], indent=2))
    else:
        parts.append("EXISTING TOPICS: none. No duplicates are possible.")

    return "\n".join(parts)


async def normalize(
    runner: TrackedRunner,
    candidates: list[TopicCandidate],
    existing: list[dict[str, str]],
    *,
    models: ModelsConfig | None = None,
) -> TrackedResult[NormalizationResult]:
    agent, model, prompt_version = build_agent(
        AGENT_KEY,
        instructions=agent_instructions(AGENT_KEY, models),
        output_type=NormalizationResult,
        models=models,
        name="Normalizer",
    )
    return await runner.run(
        agent,
        build_context(candidates, existing),
        agent_key=AGENT_KEY,
        workflow_key="discover",
        model=model,
        prompt_version=prompt_version,
    )


def apply(
    candidates: list[TopicCandidate], result: NormalizationResult
) -> tuple[list[TopicCandidate], list[dict[str, str]]]:
    """Apply normalization to the candidates.

    Returns (kept, merged). Merged topics are reported rather than silently
    dropped, so a wrong merge is visible in the discovery output.
    """
    by_index = {entry.index: entry for entry in result.topics}
    kept: list[TopicCandidate] = []
    merged: list[dict[str, str]] = []

    for index, topic in enumerate(candidates):
        entry = by_index.get(index)
        if entry is None:
            kept.append(topic)
            continue

        if (
            entry.duplicate_of_id
            and entry.duplicate_confidence.lower() == AUTO_MERGE_CONFIDENCE
        ):
            merged.append(
                {
                    "title": topic.title,
                    "duplicate_of": entry.duplicate_of_id,
                    "note": entry.normalization_note,
                }
            )
            continue

        if entry.canonical_topic:
            topic.canonical_topic = slugify(entry.canonical_topic)
        if entry.tags:
            # Tags ride alongside trend signals rather than needing a column;
            # they are prefixed so they stay distinguishable.
            topic.trend_signals = list(topic.trend_signals) + [
                f"tag:{t}" for t in entry.tags
            ]
        kept.append(topic)

    return kept, merged
