"""Discovery workflow: source material in, candidate topics persisted."""

from __future__ import annotations

from typing import Any

from agents import trace

from content_os.agents import normalizer, trend_scout
from content_os.config import load_brand, load_models_config
from content_os.storage.repositories import Repositories
from content_os.tracking.run_logger import TrackedRunner


async def run_discovery(
    repos: Repositories,
    sources: list[dict[str, Any]],
    *,
    max_topics: int = 10,
    normalize_topics: bool = True,
) -> dict[str, Any]:
    brand = load_brand()
    models = load_models_config()

    run_id = repos.runs.create(
        "discover", {"source_count": len(sources), "max_topics": max_topics}
    )
    runner = TrackedRunner(repos, run_id, models)

    created: list[str] = []
    duplicates: list[str] = []
    merged: list[dict[str, str]] = []

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

            candidates = [
                trend_scout.draft_to_candidate(d, run_id)
                for d in result.output.topics
            ]

            # Normalization runs only when there is something to normalize, and
            # only on what the exact-match slug check could not already settle.
            norm_cost = 0.0
            norm_tokens = 0
            normalization_error: str | None = None
            if candidates and normalize_topics:
                existing = [
                    {"id": t.id, "title": t.title, "canonical": t.canonical_topic}
                    for t in repos.topics.list(limit=80)
                ]
                try:
                    norm = await normalizer.normalize(
                        runner, candidates, existing, models=models
                    )
                    candidates, merged = normalizer.apply(candidates, norm.output)
                    norm_cost = norm.estimated_cost
                    norm_tokens = norm.total_tokens
                except Exception as exc:  # noqa: BLE001
                    # Normalization is an improvement, not a requirement. Losing
                    # it costs tidier canonical names, not the discovery run, and
                    # the exact-match slug check still deduplicates.
                    merged = []
                    normalization_error = f"{type(exc).__name__}: {exc}"

        for candidate in candidates:
            topic_id, is_new = repos.topics.upsert(candidate)
            (created if is_new else duplicates).append(topic_id)

        repos.runs.complete(run_id, "COMPLETED")
        return {
            "run_id": run_id,
            "proposed": len(result.output.topics),
            "created": created,
            "duplicates": duplicates,
            "merged": merged,
            "normalization_error": normalization_error,
            "discarded_reasons": result.output.discarded_reasons,
            "tokens": result.total_tokens + norm_tokens,
            "cost": round(result.estimated_cost + norm_cost, 6),
            "trace_id": result.trace_id,
        }
    except Exception as exc:
        repos.runs.complete(run_id, "FAILED", str(exc)[:500])
        raise
