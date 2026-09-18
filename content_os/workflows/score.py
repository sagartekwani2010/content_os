"""Scoring workflow.

The agent rates; content_os.tools.scoring computes. Every scored topic writes a
new immutable row, so rescoring a topic after a prompt change preserves the
earlier verdict for comparison.
"""

from __future__ import annotations

import asyncio
from typing import Any

from agents import trace

from content_os.agents import scorer
from content_os.config import load_brand, load_models_config, load_scoring_config
from content_os.models.topics import TopicCandidate, TopicStatus
from content_os.storage.repositories import Repositories
from content_os.tools.scoring import score_topic
from content_os.tracking.run_logger import TrackedRunner


async def _score_one(
    runner: TrackedRunner,
    repos: Repositories,
    brand: Any,
    cfg: Any,
    topic: TopicCandidate,
    run_id: str,
    models: Any,
    semaphore: asyncio.Semaphore,
) -> dict[str, Any]:
    async with semaphore:
        try:
            result = await scorer.rate_topic(
                runner,
                brand,
                topic,
                cfg,
                historical_insights=brand.historical_insights,
                models=models,
            )
        except Exception as exc:  # noqa: BLE001 - one bad topic must not stop the run
            return {"topic_id": topic.id, "title": topic.title, "error": str(exc)[:200]}

    score = score_topic(
        topic,
        result.output,
        cfg,
        scoring_model=result.model,
        scoring_prompt_version=result.prompt_version,
        run_id=run_id,
    )
    repos.scores.insert(score)
    repos.topics.set_status(
        topic.id, TopicStatus.VETOED if score.vetoed else TopicStatus.SCORED
    )

    return {
        "topic_id": topic.id,
        "title": topic.title,
        "base_score": score.base_score,
        "adjusted_score": score.adjusted_score,
        "brand_fit": score.brand_fit,
        "saturation_penalty": score.saturation_penalty,
        "vetoed": score.vetoed,
        "veto_flag": score.veto_flag,
        "pillar": score.recommended_pillar,
        "format": score.recommended_format,
        "tokens": result.total_tokens,
        "cost": result.estimated_cost,
    }


async def run_scoring(
    repos: Repositories,
    *,
    rescore_all: bool = False,
    limit: int = 50,
    concurrency: int = 4,
) -> dict[str, Any]:
    brand = load_brand()
    cfg = load_scoring_config()
    models = load_models_config()

    topics = (
        repos.topics.list(limit=limit)
        if rescore_all
        else repos.topics.unscored(limit=limit)
    )
    if not topics:
        return {"run_id": None, "scored": [], "message": "No topics needed scoring."}

    run_id = repos.runs.create(
        "score", {"count": len(topics), "rescore_all": rescore_all}
    )
    runner = TrackedRunner(repos, run_id, models)
    semaphore = asyncio.Semaphore(concurrency)

    try:
        with trace(
            models.workflow_name("score"),
            group_id=run_id,
            metadata={"run_id": run_id, "topics": str(len(topics))},
        ):
            results = await asyncio.gather(
                *[
                    _score_one(
                        runner, repos, brand, cfg, t, run_id, models, semaphore
                    )
                    for t in topics
                ]
            )

        scored = [r for r in results if "error" not in r]
        failed = [r for r in results if "error" in r]
        scored.sort(key=lambda r: r["adjusted_score"], reverse=True)

        repos.runs.complete(run_id, "COMPLETED" if not failed else "PARTIAL")
        return {
            "run_id": run_id,
            "scored": scored,
            "failed": failed,
            "vetoed": [r for r in scored if r["vetoed"]],
            "total_tokens": sum(r.get("tokens", 0) for r in scored),
            "total_cost": round(sum(r.get("cost", 0.0) for r in scored), 4),
        }
    except Exception as exc:
        repos.runs.complete(run_id, "FAILED", str(exc)[:500])
        raise
