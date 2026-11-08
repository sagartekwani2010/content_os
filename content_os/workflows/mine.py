"""Brand mining workflow: topics generated from the brand, not the news."""

from __future__ import annotations

from typing import Any

from content_os.codex_runtime import trace

from content_os.agents import brand_miner
from content_os.config import load_brand, load_models_config
from content_os.storage.repositories import Repositories
from content_os.tracking.run_logger import TrackedRunner


async def run_mining(
    repos: Repositories, *, max_topics: int = 10
) -> dict[str, Any]:
    brand = load_brand()
    models = load_models_config()

    run_id = repos.runs.create("mine", {"max_topics": max_topics})
    runner = TrackedRunner(repos, run_id, models)

    created: list[str] = []
    duplicates: list[str] = []

    try:
        with trace(
            models.workflow_name("mine"),
            group_id=run_id,
            metadata={"run_id": run_id, "source": "brand_memory"},
        ):
            result = await brand_miner.mine(
                runner,
                brand,
                existing_topics=repos.topics.recent_titles(60),
                recent_content=repos.content.recent_for_context(20),
                max_topics=max_topics,
                models=models,
            )

        for topic in result.output.topics:
            candidate = brand_miner.to_candidate(topic, run_id)
            topic_id, is_new = repos.topics.upsert(candidate)
            (created if is_new else duplicates).append(topic_id)

        repos.runs.complete(run_id, "COMPLETED")
        return {
            "run_id": run_id,
            "proposed": len(result.output.topics),
            "created": created,
            "duplicates": duplicates,
            "rationale": result.output.rationale,
            "topics": result.output.topics,
            "tokens": result.total_tokens,
            "cost": result.estimated_cost,
            "trace_id": result.trace_id,
        }
    except Exception as exc:
        repos.runs.complete(run_id, "FAILED", str(exc)[:500])
        raise
