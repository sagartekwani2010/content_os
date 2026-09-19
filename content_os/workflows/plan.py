"""Planning workflow.

Produces a balanced weekly portfolio and persists each item as a PLANNED content
row, so generation later has a real target and the plan is auditable against
what actually got made.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

from agents import trace

from content_os.agents import strategist
from content_os.config import load_brand, load_models_config, load_scoring_config
from content_os.ids import new_id
from content_os.models.content import ContentItem, ContentStatus
from content_os.models.topics import TopicStatus
from content_os.storage.db import dumps, utcnow
from content_os.storage.repositories import Repositories
from content_os.tools.analytics import leaderboard
from content_os.tracking.run_logger import TrackedRunner


def _performance_summary(repos: Repositories) -> dict[str, Any] | None:
    try:
        board = leaderboard(repos, n=10)
    except Exception:
        return None
    if not board.get("measured_posts"):
        return None
    return {
        "measured_posts": board["measured_posts"],
        "by_pillar": board["by_pillar"],
        "by_format": board["by_format"],
        "by_hook_type": board["by_hook_type"],
        "by_delivery": board["by_delivery"],
        "top_titles": [t["title"] for t in board["top"][:5]],
    }


async def run_planning(
    repos: Repositories,
    *,
    target_posts: int = 7,
    horizon_days: int = 7,
    candidate_limit: int = 60,
) -> dict[str, Any]:
    brand = load_brand()
    cfg = load_scoring_config()
    models = load_models_config()

    # Vetoed topics are included in the context so the strategist can record why
    # it passed on them, but the agent is instructed not to select them and the
    # selection is filtered in Python regardless.
    candidates = repos.scores.ranked(include_vetoed=True, limit=candidate_limit)
    usable = [c for c in candidates if not c.score.vetoed]

    if not usable:
        return {
            "run_id": None,
            "error": "No scored, non-vetoed topics available. Run discover and score first.",
        }
    if len(usable) < target_posts:
        target_posts = len(usable)

    run_id = repos.runs.create(
        "plan", {"target_posts": target_posts, "horizon_days": horizon_days}
    )
    runner = TrackedRunner(repos, run_id, models)

    try:
        with trace(
            models.workflow_name("plan"),
            group_id=run_id,
            metadata={
                "run_id": run_id,
                "candidates": str(len(usable)),
                "target_posts": str(target_posts),
            },
        ):
            result, report = await strategist.build_plan(
                runner,
                brand,
                candidates,
                cfg,
                target_posts=target_posts,
                horizon_days=horizon_days,
                recent_content=repos.content.recent_for_context(20),
                performance_summary=_performance_summary(repos),
                models=models,
            )

        plan = result.output
        plan_id = repos.plans.insert(
            run_id=run_id,
            horizon_days=horizon_days,
            target_posts=target_posts,
            portfolio_rationale=plan.portfolio_rationale,
            composition=report.get("distribution", {}),
            balance_report=report,
        )

        by_topic = {c.topic.id: c for c in candidates}
        start = datetime.now(timezone.utc)
        created: list[dict[str, Any]] = []

        for position, item in enumerate(plan.items):
            scored = by_topic.get(item.topic_id)
            if scored is None:
                continue

            planned_date = start + timedelta(
                days=round(position * horizon_days / max(1, len(plan.items)))
            )
            now = utcnow()
            content = ContentItem(
                id=new_id("content"),
                topic_id=item.topic_id,
                run_id=run_id,
                format=item.format,
                pillar=item.pillar,
                strategic_role=item.strategic_role,
                title=item.proposed_title,
                hook=item.primary_hook,
                body_json=dumps(
                    {
                        "alternate_hooks": item.alternate_hooks,
                        "recommended_publish_window": item.recommended_publish_window,
                    }
                ),
                caption="",
                status=ContentStatus.PLANNED,
                planned_publish_date=planned_date,
                generator_agent=strategist.AGENT_KEY,
                generator_model=result.model,
                generator_prompt_version=result.prompt_version,
                created_at=now,
                updated_at=now,
            )
            repos.content.insert(
                content,
                plan_id=plan_id,
                urgency=item.urgency,
                strategist_reasoning=item.reasoning,
                strategist_score=item.score,
            )
            repos.topics.set_status(item.topic_id, TopicStatus.PLANNED)

            created.append(
                {
                    "content_id": content.id,
                    "topic_id": item.topic_id,
                    "title": item.proposed_title,
                    "format": item.format,
                    "pillar": item.pillar,
                    "strategic_role": item.strategic_role,
                    "urgency": item.urgency,
                    "hook": item.primary_hook,
                    "alternate_hooks": item.alternate_hooks,
                    "reasoning": item.reasoning,
                    "score": item.score,
                    "planned_date": planned_date.date().isoformat(),
                }
            )

        repos.runs.complete(run_id, "COMPLETED")
        return {
            "run_id": run_id,
            "plan_id": plan_id,
            "items": created,
            "balance_report": report,
            "portfolio_rationale": plan.portfolio_rationale,
            "deferred": list(zip(plan.deferred_topic_ids, plan.deferral_reasons)),
            "tokens": result.total_tokens,
            "cost": result.estimated_cost,
            "trace_id": result.trace_id,
        }
    except Exception as exc:
        repos.runs.complete(run_id, "FAILED", str(exc)[:500])
        raise
