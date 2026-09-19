"""Brief-driven production: the default workflow.

    ContentBrief (human, approved)
      -> Brief Strategist   plans how, never what
      -> Hook Expander      polishes human-approved hook points
      -> Writer             reel or carousel
      -> Visual Planner     shot plan
      -> QA                 hard gates on learning and brief execution
      -> human review

Only APPROVED briefs are processed. The brief's immutable fields are reasserted
after every agent rather than trusted, and drift is reported rather than
silently corrected.
"""

from __future__ import annotations

from typing import Any

from agents import trace

from content_os.agents import (
    brief_strategist,
    carousel_writer,
    hook_expander,
    qa_editor,
    reel_writer,
    visual_planner,
)
from content_os.config import load_brand, load_models_config, load_scoring_config
from content_os.ids import new_id, slugify
from content_os.models.brief import BriefStatus, ContentBrief
from content_os.models.content import ContentItem, ContentStatus, CreativeVariant
from content_os.models.topics import TopicCandidate, TopicStatus
from content_os.storage.db import dumps, utcnow
from content_os.storage.repositories import Repositories
from content_os.tracking.run_logger import TrackedRunner


def _detect_modes(package: Any, fmt: str) -> dict[str, bool]:
    if fmt == "carousel":
        return {"avatar_used": False, "human_used": False, "screen_demo_used": False}
    modes = {s.production_mode.lower() for s in getattr(package, "scene_plan", [])}
    return {
        "avatar_used": any("avatar" in m for m in modes)
        or bool(getattr(package, "avatar_segments", [])),
        "human_used": any("human" in m for m in modes),
        "screen_demo_used": any("screen" in m for m in modes)
        or bool(getattr(package, "screen_demo_segments", [])),
    }


def _topic_for_brief(repos: Repositories, brief: ContentBrief) -> str:
    """Give a brief a topic row so the existing tracking chain still holds.

    Content reaches production down two paths now: discovery, where a topic is
    found and scored, and a human brief, where the subject was chosen outright.
    The analytics layer joins content through topics, so a brief without one
    would silently drop out of every historical report.

    The row is marked with source type `content_brief`, so brief-originated and
    discovery-originated subjects stay distinguishable rather than merged.
    """
    candidate = TopicCandidate(
        id=new_id("topic"),
        title=brief.topic,
        canonical_topic=slugify(brief.topic),
        summary=brief.core_thesis,
        source_urls=list(brief.references),
        source_types=["content_brief"],
        discovered_at=utcnow(),
        target_audience=list(brief.target_audience),
        content_pillars=[brief.brand_pillar],
        potential_angles=list(brief.approved_hook_points),
        estimated_saturation=0.0,
        status=TopicStatus.IN_PRODUCTION,
        why_it_matters=brief.why_this_matters,
        discussion_angle=brief.hook_direction,
    )
    topic_id, _ = repos.topics.upsert(candidate)
    return topic_id


async def produce_brief(
    repos: Repositories,
    brief: ContentBrief,
    *,
    run_id: str | None = None,
    skip_visual_planner: bool = False,
) -> dict[str, Any]:
    """Execute one approved brief end to end."""
    brand = load_brand()
    cfg = load_scoring_config()
    models = load_models_config()

    if brief.status != BriefStatus.APPROVED:
        return {
            "brief_id": brief.brief_id,
            "error": (
                f"Brief status is {brief.status.value}. Only APPROVED briefs "
                f"are produced. Run: cli.py approve-brief {brief.brief_id}"
            ),
        }

    owns_run = run_id is None
    if owns_run:
        run_id = repos.runs.create(
            "produce", {"brief_id": brief.brief_id, "format": brief.content_format}
        )
    runner = TrackedRunner(repos, run_id, models)

    fmt = "carousel" if brief.content_format == "carousel" else "reel"
    warnings: list[str] = []
    recent = repos.content.recent_for_context(20)

    try:
        repos.briefs.set_status(brief.brief_id, BriefStatus.IN_PRODUCTION)

        with trace(
            models.workflow_name("produce"),
            group_id=run_id,
            metadata={
                "run_id": run_id or "",
                "brief_id": brief.brief_id,
                "format": brief.content_format,
                "pillar": brief.brand_pillar,
            },
        ):
            # 1. plan how to execute what the human decided
            plan_result, plan_warnings = await brief_strategist.plan_execution(
                runner, brand, brief, recent_content=recent, models=models
            )
            plan = plan_result.output
            warnings += plan_warnings
            repos.execution_plans.insert(
                plan, run_id=run_id,
                model=plan_result.model, prompt_version=plan_result.prompt_version,
            )

            # 2. expand the human-approved hook points
            hook_result, hook_warnings = await hook_expander.expand(
                runner, brand, brief, plan, models=models
            )
            hook_set = hook_result.output
            warnings += hook_warnings
            selected_hook, hook_strategy, hook_variant_id = hook_expander.select(hook_set)
            alternates = [
                v.text for v in hook_set.variants if v.variant_id != hook_variant_id
            ]

            # 3. write
            writer = (
                carousel_writer.write_carousel_from_brief
                if fmt == "carousel"
                else reel_writer.write_reel_from_brief
            )
            gen = await writer(
                runner, brand, brief, plan,
                selected_hook=selected_hook, alternate_hooks=alternates,
                recent_content=recent, models=models,
            )
            package = gen.output

            # 4. visual plan
            if not skip_visual_planner:
                try:
                    visual = await visual_planner.plan_visuals(
                        runner, brand, brief, package, fmt=fmt, models=models
                    )
                    package = (
                        visual_planner.apply_to_carousel(package, visual.output)
                        if fmt == "carousel"
                        else visual_planner.apply_to_reel(package, visual.output)
                    )
                except Exception as exc:  # noqa: BLE001
                    # The writer already produced a usable plan. Losing the
                    # refinement costs polish, not the run.
                    warnings.append(f"VISUAL_PLANNER_FAILED:{type(exc).__name__}")

            # 5. QA against the brief
            qa_raw, qa_result = await qa_editor.review(
                runner, brand, cfg, package,
                content_format=fmt, topic_title=brief.topic,
                recent_content=recent, models=models, brief=brief,
            )

        # --- persist ------------------------------------------------------
        modes = _detect_modes(package, fmt)
        now = utcnow()
        hook_text = package.hook if fmt == "reel" else package.cover_hook

        item = ContentItem(
            id=new_id("content"),
            topic_id=_topic_for_brief(repos, brief),
            run_id=run_id,
            format=brief.content_format,
            pillar=brief.brand_pillar,
            strategic_role="authority",
            title=package.title,
            hook=hook_text,
            body_json=package.model_dump_json(),
            caption=package.caption,
            cta=package.cta,
            avatar_used=modes["avatar_used"],
            human_used=modes["human_used"],
            screen_demo_used=modes["screen_demo_used"],
            status=ContentStatus.GENERATED,
            brief_id=brief.brief_id,
            core_thesis=brief.core_thesis,
            learning_objective=brief.learning_objective,
            hook_direction=brief.hook_direction,
            approved_hook_points=list(brief.approved_hook_points),
            high_level_sections=list(brief.high_level_sections),
            preferred_pov=brief.preferred_pov,
            visual_direction=brief.visual_direction,
            hook_strategy=hook_strategy,
            hook_source="agent_expanded",
            hook_variant_id=hook_variant_id,
            learning_payoff=package.learning_payoff,
            save_reason=package.save_reason,
            share_reason=package.share_reason,
            generator_agent=gen.agent_name,
            generator_model=gen.model,
            generator_prompt_version=gen.prompt_version,
            created_at=now,
            updated_at=now,
        )
        content_id = repos.content.insert_with_strategy(item, package.sections_covered)

        repos.hooks.record_set(
            hook_set, brief=brief, content_id=content_id,
            model=hook_result.model, prompt_version=hook_result.prompt_version,
            selected_variant_id=hook_variant_id,
        )

        # Creative variants stay the unit of performance comparison.
        for index, variant in enumerate(hook_set.variants):
            repos.variants.insert(
                CreativeVariant(
                    id=new_id("creative"), content_id=content_id,
                    variant_type="hook", label=variant.hook_strategy,
                    hook=variant.text,
                    script=getattr(package, "script", None),
                    visual_style=getattr(package, "visual_hook", None),
                    duration_seconds=getattr(
                        package, "estimated_duration_seconds", None
                    ),
                    is_control=variant.variant_id == hook_variant_id,
                    created_at=now,
                )
            )

        repos.qa.insert(content_id, qa_result, run_id)
        repos.content.attach_qa(
            content_id, approved=qa_result.approved,
            composite=qa_result.composite, qa_json=dumps(qa_result.model_dump()),
        )
        repos.briefs.set_status(
            brief.brief_id,
            BriefStatus.READY if qa_result.approved else BriefStatus.APPROVED,
        )

        if owns_run:
            repos.runs.complete(run_id, "COMPLETED")

        cost = repos.agent_runs.cost_per_content(content_id)
        return {
            "run_id": run_id,
            "brief_id": brief.brief_id,
            "content_id": content_id,
            "format": fmt,
            "title": package.title,
            "hook": hook_text,
            "hook_strategy": hook_strategy,
            "hook_variant_id": hook_variant_id,
            "package": package,
            "plan": plan,
            "hook_set": hook_set,
            "qa": qa_result,
            "warnings": warnings,
            "status": (
                ContentStatus.READY_FOR_REVIEW.value
                if qa_result.approved
                else ContentStatus.QA_FAILED.value
            ),
            "cost": round((cost["estimated_cost"] or 0.0) if cost else 0.0, 6),
            "tokens": (cost["total_tokens"] or 0) if cost else 0,
            "trace_id": gen.trace_id,
        }
    except Exception as exc:
        repos.briefs.set_status(brief.brief_id, BriefStatus.APPROVED)
        if owns_run and run_id:
            repos.runs.complete(run_id, "FAILED", str(exc)[:500])
        raise


async def produce_approved(
    repos: Repositories, *, limit: int = 0
) -> dict[str, Any]:
    """Batch-produce every approved brief.

    One failure does not stop the batch; ten briefs producing nine pieces plus
    one clear error is better than an empty run.
    """
    briefs = repos.briefs.approved(limit=limit or 100)
    if limit:
        briefs = briefs[:limit]
    if not briefs:
        return {"produced": [], "message": "No APPROVED briefs in the backlog."}

    run_id = repos.runs.create("produce_approved", {"count": len(briefs)})
    produced: list[dict[str, Any]] = []
    failed: list[dict[str, str]] = []

    for brief in briefs:
        try:
            result = await produce_brief(repos, brief, run_id=run_id)
            if result.get("error"):
                failed.append({"brief_id": brief.brief_id, "error": result["error"]})
            else:
                produced.append(result)
        except Exception as exc:  # noqa: BLE001
            failed.append(
                {"brief_id": brief.brief_id, "error": f"{type(exc).__name__}: {exc}"}
            )

    repos.runs.complete(run_id, "COMPLETED")
    return {"run_id": run_id, "produced": produced, "failed": failed}
