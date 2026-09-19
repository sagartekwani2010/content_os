"""Content Strategist agent.

The manager of the system. Receives scored topics and builds a balanced weekly
portfolio rather than taking the top N by score.

Composition is measured deterministically after the agent responds. When the
plan violates a guardrail, the concrete gap is fed back and the agent gets one
rebalance attempt. This keeps judgement with the agent and verification with
Python instead of trusting the model to check its own arithmetic.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any

from content_os.config import BrandMemory, ModelsConfig, ScoringConfig
from content_os.models.content import ContentPlan
from content_os.models.topics import ScoredTopic
from content_os.tools.scoring import analyse_portfolio, portfolio_gap_brief
from content_os.tracking.run_logger import (
    TrackedResult,
    TrackedRunner,
    agent_instructions,
    build_agent,
)

AGENT_KEY = "strategist"


def _topic_payload(scored: ScoredTopic) -> dict[str, Any]:
    topic, score = scored.topic, scored.score
    return {
        "topic_id": topic.id,
        "title": topic.title,
        "summary": topic.summary,
        "discussion_angle": topic.discussion_angle,
        "potential_angles": topic.potential_angles,
        "pillars": topic.content_pillars,
        "recommended_pillar": score.recommended_pillar,
        "recommended_format": score.recommended_format,
        "event_date": topic.event_date.isoformat() if topic.event_date else None,
        "scores": {
            "adjusted": score.adjusted_score,
            "base": score.base_score,
            "brand_fit": score.brand_fit,
            "audience_fit": score.audience_fit,
            "trend_velocity_raw": score.trend_velocity,
            "trend_velocity_decayed": score.decayed_trend_velocity,
            "originality": score.originality,
            "visual_potential": score.visual_potential,
            "production_fit": score.production_fit,
            "saturation_penalty": score.saturation_penalty,
        },
        "vetoed": score.vetoed,
        "veto_flag": score.veto_flag,
        "rationale": score.rationale,
    }


def build_context(
    brand: BrandMemory,
    candidates: list[ScoredTopic],
    cfg: ScoringConfig,
    *,
    target_posts: int,
    horizon_days: int,
    recent_content: list[dict[str, Any]],
    performance_summary: dict[str, Any] | None,
) -> str:
    parts = [brand.as_prompt_context(), ""]

    parts.append(
        f"TASK: Build a {horizon_days}-day content plan containing exactly "
        f"{target_posts} items."
    )
    parts.append(f"TODAY: {datetime.now(timezone.utc).date().isoformat()}")
    parts.append("")

    parts.append("TARGET PORTFOLIO MIX (directional, deviate only with a reason):")
    for pillar, target in cfg.portfolio.targets.items():
        parts.append(
            f"  {pillar}: {target:.0%} (about "
            f"{round(target * target_posts, 1)} of {target_posts} posts)"
        )
    parts.append("")
    parts.append("GUARDRAILS (a plan violating these is rejected and returned to you):")
    parts.append(
        f"  - At most {cfg.portfolio.pillar_cap(target_posts)} posts per pillar"
    )
    parts.append(f"  - At least {cfg.portfolio.min_distinct_pillars} distinct pillars")
    parts.append(
        f"  - No more than {cfg.portfolio.max_same_format_streak} consecutive "
        f"posts in the same format"
    )
    parts.append("  - No topic used twice")
    parts.append("  - No vetoed topic included")
    parts.append("")

    if recent_content:
        parts.append("RECENTLY PUBLISHED OR PLANNED (audience fatigue check):")
        for c in recent_content[:15]:
            parts.append(
                f"  - [{c.get('format', '?')}/{c.get('pillar', '?')}] "
                f"{c.get('title', '')} | hook: {c.get('hook') or 'n/a'}"
            )
        parts.append("")

    if performance_summary and performance_summary.get("measured_posts"):
        parts.append("HISTORICAL PERFORMANCE FOR THIS ACCOUNT (weight this heavily):")
        parts.append(json.dumps(performance_summary, indent=2, default=str)[:4000])
        parts.append("")
    else:
        parts.append(
            "HISTORICAL PERFORMANCE: none yet. Rely on brand judgement, and favour "
            "a spread that will generate useful signal rather than concentrating "
            "the week on one bet."
        )
        parts.append("")

    vetoed = [c for c in candidates if c.score.vetoed]
    usable = [c for c in candidates if not c.score.vetoed]

    parts.append(f"CANDIDATE TOPICS ({len(usable)} available, ranked by adjusted score):")
    parts.append(json.dumps([_topic_payload(c) for c in usable], indent=2, default=str))

    if vetoed:
        parts.append("")
        parts.append(
            f"VETOED TOPICS ({len(vetoed)}) - DO NOT INCLUDE THESE. Listed so you "
            f"can record them in deferred_topic_ids with a reason:"
        )
        for c in vetoed:
            parts.append(
                f"  - {c.topic.id}: {c.topic.title} "
                f"(brand_fit {c.score.brand_fit}, flag {c.score.veto_flag})"
            )

    return "\n".join(parts)


async def build_plan(
    runner: TrackedRunner,
    brand: BrandMemory,
    candidates: list[ScoredTopic],
    cfg: ScoringConfig,
    *,
    target_posts: int = 7,
    horizon_days: int = 7,
    recent_content: list[dict[str, Any]] | None = None,
    performance_summary: dict[str, Any] | None = None,
    models: ModelsConfig | None = None,
    allow_rebalance: bool = True,
) -> tuple[TrackedResult[ContentPlan], dict[str, Any]]:
    """Produce a plan and its measured composition.

    Returns (result, balance_report). The report is stored with the plan so a
    later review can see not just what was chosen but how balanced it was.
    """
    agent, model, prompt_version = build_agent(
        AGENT_KEY,
        instructions=agent_instructions(AGENT_KEY, models),
        output_type=ContentPlan,
        models=models,
        name="Content Strategist",
    )

    prompt = build_context(
        brand,
        candidates,
        cfg,
        target_posts=target_posts,
        horizon_days=horizon_days,
        recent_content=recent_content or [],
        performance_summary=performance_summary,
    )

    result = await runner.run(
        agent,
        prompt,
        agent_key=AGENT_KEY,
        workflow_key="plan",
        model=model,
        prompt_version=prompt_version,
    )

    plan: ContentPlan = result.output
    valid_ids = {c.topic.id for c in candidates if not c.score.vetoed}
    plan.items = [i for i in plan.items if i.topic_id in valid_ids]

    report = analyse_portfolio(plan.items, cfg)

    if allow_rebalance and report["violations"]:
        # One corrective pass. Feeding back the concrete gap works better than
        # restating the targets the agent already had.
        gap = portfolio_gap_brief(plan.items, cfg, target_posts)
        retry_prompt = (
            f"{prompt}\n\n---\n"
            f"YOUR PREVIOUS PLAN VIOLATED THE GUARDRAILS.\n\n{gap}\n\n"
            f"Produce a corrected plan of exactly {target_posts} items that "
            f"resolves every violation above. Keep the strong choices; change "
            f"only what has to change."
        )
        retry = await runner.run(
            agent,
            retry_prompt,
            agent_key=AGENT_KEY,
            workflow_key="plan",
            model=model,
            prompt_version=prompt_version,
            extra_metadata={"rebalance": "1"},
        )
        retry_plan: ContentPlan = retry.output
        retry_plan.items = [i for i in retry_plan.items if i.topic_id in valid_ids]
        retry_report = analyse_portfolio(retry_plan.items, cfg)

        # Keep the rebalanced plan only when it is genuinely better.
        if len(retry_report["violations"]) < len(report["violations"]):
            retry.output = retry_plan
            return retry, retry_report

    result.output = plan
    return result, report
