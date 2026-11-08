"""Performance analysis workflow.

Numbers are computed deterministically and handed to the analyst, which supplies
interpretation. Findings are stored typed, so an observation and a hypothesis
stay distinguishable when they feed back into future scoring.
"""

from __future__ import annotations

from typing import Any

from content_os.codex_runtime import trace

from content_os.agents import performance_analyst
from content_os.config import load_brand, load_models_config
from content_os.storage.repositories import Repositories
from content_os.tools.analytics import (
    build_dataset,
    leaderboard,
    scoring_dimension_correlation,
)
from content_os.tracking.run_logger import TrackedRunner


async def run_analysis(repos: Repositories) -> dict[str, Any]:
    brand = load_brand()
    models = load_models_config()

    dataset = build_dataset(repos)
    if not dataset:
        return {
            "run_id": None,
            "measured_posts": 0,
            "message": (
                "No performance data yet. Ingest metrics first with "
                "`cli.py ingest-performance <file.csv>`."
            ),
        }

    board = leaderboard(repos, n=20)
    correlation = scoring_dimension_correlation(repos)

    run_id = repos.runs.create("analyze", {"measured_posts": len(dataset)})
    runner = TrackedRunner(repos, run_id, models)

    analytics = {
        "measured_posts": board["measured_posts"],
        "by_pillar": board["by_pillar"],
        "by_format": board["by_format"],
        "by_hook_type": board["by_hook_type"],
        "by_delivery": board["by_delivery"],
        "by_duration": board["by_duration"],
        "top": [
            {
                "title": t["title"], "pillar": t["pillar"], "format": t["format"],
                "hook_type": t["hook_type"], "delivery": t["delivery_mode"],
                "performance_score": t["performance_score"], "metrics": t["metrics"],
            }
            for t in board["top"][:10]
        ],
        "bottom": [
            {
                "title": t["title"], "pillar": t["pillar"], "format": t["format"],
                "hook_type": t["hook_type"],
                "performance_score": t["performance_score"],
            }
            for t in board["bottom"][:5]
        ],
    }

    try:
        with trace(
            models.workflow_name("analyze"),
            group_id=run_id,
            metadata={"run_id": run_id, "measured_posts": str(len(dataset))},
        ):
            result = await performance_analyst.analyse(
                runner, brand, analytics, correlation,
                measured_posts=len(dataset), models=models,
            )

        analysis = result.output
        stored = 0
        for finding in (
            list(analysis.observations)
            + list(analysis.hypotheses)
            + list(analysis.recommendations)
        ):
            repos.findings.insert(finding, run_id)
            stored += 1

        repos.runs.complete(run_id, "COMPLETED")
        return {
            "run_id": run_id,
            "measured_posts": len(dataset),
            "analysis": analysis,
            "correlation": correlation,
            "findings_stored": stored,
            "tokens": result.total_tokens,
            "cost": result.estimated_cost,
            "trace_id": result.trace_id,
        }
    except Exception as exc:
        repos.runs.complete(run_id, "FAILED", str(exc)[:500])
        raise
