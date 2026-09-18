"""Discovery workflow: source material in, candidate topics persisted."""

from __future__ import annotations

from typing import Any

from agents import trace

from content_os.agents import trend_scout
from content_os.config import load_brand, load_models_config
from content_os.storage.repositories import Repositories
from content_os.tracking.run_logger import TrackedRunner


async def run_discovery(
    repos: Repositories,
    sources: list[dict[str, Any]],
    *,
    max_topics: int = 10,
) -> dict[str, Any]:
    brand = load_brand()
    models = load_models_config()

    run_id = repos.runs.create(
        "discover", {"source_count": len(sources), "max_topics": max_topics}
    )
    runner = TrackedRunner(repos, run_id, models)

    created: list[str] = []
    duplicates: list[str] = []

    try:
        with trace(
            models.workflow_name("discover"),
            group_id=run_id,
            metadata={"run_id": run_id, "sources": str(len(sources))},
        ):
            result = await trend_scout.discover_topics(
                runner,
                brand,
                sources,
                existing_topics=repos.topics.recent_titles(60),
                recent_content=repos.content.recent_for_context(20),
                max_topics=max_topics,
                models=models,
            )

        for draft in result.output.topics:
            candidate = trend_scout.draft_to_candidate(draft, run_id)
            topic_id, is_new = repos.topics.upsert(candidate)
            (created if is_new else duplicates).append(topic_id)

        repos.runs.complete(run_id, "COMPLETED")
        return {
            "run_id": run_id,
            "proposed": len(result.output.topics),
            "created": created,
            "duplicates": duplicates,
            "discarded_reasons": result.output.discarded_reasons,
            "tokens": result.total_tokens,
            "cost": result.estimated_cost,
            "trace_id": result.trace_id,
        }
    except Exception as exc:
        repos.runs.complete(run_id, "FAILED", str(exc)[:500])
        raise
