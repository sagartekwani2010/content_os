"""Generation workflow: topic to a QA-reviewed, persisted content package.

A QA failure never discards the artifact. The package is persisted with status
QA_FAILED and the full verdict is stored, because a rejected draft plus the
reason is evidence about what this system produces, and throwing it away would
defeat the tracking the whole design rests on.
"""

from __future__ import annotations

from typing import Any, Literal

from agents import trace

from content_os.agents import carousel_writer, qa_editor, reel_writer
from content_os.config import load_brand, load_models_config, load_scoring_config
from content_os.ids import new_id
from content_os.models.content import (
    ContentItem,
    ContentPlanItem,
    ContentStatus,
    CreativeVariant,
)
from content_os.models.topics import TopicStatus
from content_os.storage.db import dumps, loads, utcnow
from content_os.storage.repositories import Repositories
from content_os.tracking.run_logger import TrackedRunner

Format = Literal["reel", "carousel"]


def _plan_item_from_row(row: Any) -> ContentPlanItem | None:
    """Rebuild the strategist's brief from the planned content row."""
    if row is None:
        return None
    body = loads(row["body_json"], {}) or {}
    try:
        return ContentPlanItem(
            topic_id=row["topic_id"],
            proposed_title=row["title"],
            format=row["format"],
            pillar=row["pillar"],
            strategic_role=row["strategic_role"] or "authority",
            recommended_publish_window=body.get("recommended_publish_window"),
            urgency=row["urgency"] or "evergreen",
            reasoning=row["strategist_reasoning"] or "",
            primary_hook=row["hook"] or "",
            alternate_hooks=body.get("alternate_hooks", []),
            score=row["strategist_score"] or 0.0,
        )
    except Exception:
        return None


def _detect_production_modes(package: Any, fmt: str) -> dict[str, bool]:
    """Infer which production modes the package actually requires.

    Stored on the content row so that avatar-versus-human performance can be
    compared later without re-reading every script.
    """
    if fmt == "carousel":
        return {"avatar_used": False, "human_used": False, "screen_demo_used": False}

    modes = {s.production_mode.lower() for s in getattr(package, "scene_plan", [])}
    blob = " ".join(getattr(package, "b_roll_requirements", [])).lower()

    return {
        "avatar_used": any("avatar" in m for m in modes)
        or bool(getattr(package, "avatar_requirements", [])),
        "human_used": any("human" in m or "talking_head_human" in m for m in modes),
        "screen_demo_used": any("screen" in m for m in modes) or "screen record" in blob,
    }


def _store_variants(
    repos: Repositories, content_id: str, package: Any, fmt: str
) -> list[str]:
    """Persist each hook as a testable creative variant.

    One idea ships with several hooks and we need to know which one won, so the
    variants are rows rather than a JSON blob inside the content.
    """
    now = utcnow()
    variants: list[CreativeVariant] = []

    if fmt == "reel":
        primary, alternates = package.hook, list(package.hook_variants)
        script, duration = package.script, package.estimated_duration_seconds
        style = package.visual_hook
    else:
        primary, alternates = package.cover_hook, []
        script, duration, style = None, None, "carousel_cover"

    variants.append(
        CreativeVariant(
            id=new_id("creative"),
            content_id=content_id,
            variant_type="hook",
            label="control",
            hook=primary,
            script=script,
            visual_style=style,
            duration_seconds=duration,
            is_control=True,
            created_at=now,
        )
    )
    for index, alternate in enumerate(alternates[:4], start=1):
        variants.append(
            CreativeVariant(
                id=new_id("creative"),
                content_id=content_id,
                variant_type="hook",
                label=f"variant_{index}",
                hook=alternate,
                script=script,
                visual_style=style,
                duration_seconds=duration,
                is_control=False,
                created_at=now,
            )
        )

    return [repos.variants.insert(v) for v in variants]


async def run_generation(
    repos: Repositories,
    topic_id: str,
    fmt: Format,
    *,
    content_id: str | None = None,
    run_id: str | None = None,
) -> dict[str, Any]:
    brand = load_brand()
    cfg = load_scoring_config()
    models = load_models_config()

    topic = repos.topics.get(topic_id) or repos.topics.find_by_prefix(topic_id)
    if topic is None:
        return {"error": f"Topic not found: {topic_id}"}

    owns_run = run_id is None
    if owns_run:
        run_id = repos.runs.create(f"create_{fmt}", {"topic_id": topic.id})
    runner = TrackedRunner(repos, run_id, models)

    workflow_key = "reel" if fmt == "reel" else "carousel"
    existing_row = repos.content.get(content_id) if content_id else None
    plan_item = _plan_item_from_row(existing_row)
    recent = repos.content.recent_for_context(20)

    try:
        with trace(
            models.workflow_name(workflow_key),
            group_id=run_id,
            metadata={
                "run_id": run_id or "",
                "topic_id": topic.id,
                "format": fmt,
                "content_id": content_id or "",
            },
        ):
            if fmt == "reel":
                gen = await reel_writer.write_reel(
                    runner, brand, topic,
                    plan_item=plan_item, content_id=content_id,
                    recent_content=recent, models=models,
                )
            else:
                gen = await carousel_writer.write_carousel(
                    runner, brand, topic,
                    plan_item=plan_item, content_id=content_id,
                    recent_content=recent, models=models,
                )

            package = gen.output

            qa_raw, qa_result = await qa_editor.review(
                runner, brand, cfg, package,
                content_format=fmt,
                topic_title=topic.title,
                topic_id=topic.id,
                content_id=content_id,
                revision_number=(
                    repos.qa.next_revision(content_id) if content_id else 0
                ),
                recent_content=recent,
                models=models,
            )

        # --- persist ------------------------------------------------------
        modes = _detect_production_modes(package, fmt)
        now = utcnow()
        title = package.title
        hook = package.hook if fmt == "reel" else package.cover_hook

        if existing_row is not None:
            final_content_id = existing_row["id"]
            repos.conn.execute(
                "UPDATE content_items SET title = ?, hook = ?, body_json = ?, "
                "caption = ?, cta = ?, avatar_used = ?, human_used = ?, "
                "screen_demo_used = ?, status = ?, generator_agent = ?, "
                "generator_model = ?, generator_prompt_version = ?, updated_at = ? "
                "WHERE id = ?",
                (
                    title, hook, package.model_dump_json(), package.caption,
                    package.cta, int(modes["avatar_used"]), int(modes["human_used"]),
                    int(modes["screen_demo_used"]), ContentStatus.GENERATED.value,
                    gen.agent_name, gen.model, gen.prompt_version,
                    now.isoformat(), final_content_id,
                ),
            )
        else:
            score = repos.scores.latest_for_topic(topic.id)
            item = ContentItem(
                id=new_id("content"),
                topic_id=topic.id,
                run_id=run_id,
                format=fmt,
                pillar=(score.recommended_pillar if score else "")
                or (topic.content_pillars[0] if topic.content_pillars else "ai_builder"),
                strategic_role="authority",
                title=title,
                hook=hook,
                body_json=package.model_dump_json(),
                caption=package.caption,
                cta=package.cta,
                avatar_used=modes["avatar_used"],
                human_used=modes["human_used"],
                screen_demo_used=modes["screen_demo_used"],
                status=ContentStatus.GENERATED,
                generator_agent=gen.agent_name,
                generator_model=gen.model,
                generator_prompt_version=gen.prompt_version,
                created_at=now,
                updated_at=now,
            )
            final_content_id = repos.content.insert(item)

        variant_ids = _store_variants(repos, final_content_id, package, fmt)
        repos.qa.insert(final_content_id, qa_result, run_id)
        repos.content.attach_qa(
            final_content_id,
            approved=qa_result.approved,
            composite=qa_result.composite,
            qa_json=dumps(qa_result.model_dump()),
        )
        repos.topics.set_status(topic.id, TopicStatus.IN_PRODUCTION)

        if owns_run:
            repos.runs.complete(run_id, "COMPLETED")

        cost = repos.agent_runs.cost_per_content(final_content_id)
        return {
            "run_id": run_id,
            "content_id": final_content_id,
            "topic_id": topic.id,
            "format": fmt,
            "title": title,
            "hook": hook,
            "package": package,
            "qa": qa_result,
            "variant_ids": variant_ids,
            "status": (
                ContentStatus.READY_FOR_REVIEW.value
                if qa_result.approved
                else ContentStatus.QA_FAILED.value
            ),
            "tokens": gen.total_tokens + qa_raw.total_tokens,
            "cost": round(
                (cost["estimated_cost"] or 0.0) if cost else 0.0, 6
            ),
            "trace_id": gen.trace_id,
        }
    except Exception as exc:
        if owns_run and run_id:
            repos.runs.complete(run_id, "FAILED", str(exc)[:500])
        raise
