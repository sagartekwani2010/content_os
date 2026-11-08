"""Adversarial Reel story review before visual production.

The writer is rewarded for making a coherent package. This stage has a different
job: act like a first-time viewer and reject a script that explains twice,
never turns, or leaves no reason to continue watching.
"""

from __future__ import annotations

from typing import Any

from content_os.config import BrandMemory, ModelsConfig
from content_os.models.brief import ContentBrief
from content_os.models.content import ReelPackage, StoryVerdict
from content_os.tracking.run_logger import (
    TrackedResult,
    TrackedRunner,
    agent_instructions,
    build_agent,
)

AGENT_KEY = "story_judge"


def build_context(
    brand: BrandMemory,
    package: ReelPackage,
    *,
    topic_title: str,
    brief: ContentBrief | None = None,
) -> str:
    parts = [brand.as_prompt_context(), ""]
    if brief is not None:
        parts += [brief.as_prompt_context(), ""]
    parts += [
        "You are reviewing this as a first-time mobile viewer. Do not reward "
        "technical correctness if the story does not move.",
        f"UNDERLYING TOPIC: {topic_title}",
        "",
        "REEL PACKAGE:",
        package.model_dump_json(indent=2),
        "",
        "Return REWRITE when one revision could fix the issue. Return BLOCK "
        "only when the approved brief cannot be met without human direction.",
    ]
    return "\n".join(parts)


def failed_gates(verdict: StoryVerdict) -> list[str]:
    """Convert the judge's narrative review into explicit pipeline vetoes."""
    failed: list[str] = []
    if verdict.verdict != "PASS":
        failed.append(f"STORY_{verdict.verdict}")
    if not (verdict.viewer_question_by_second_five or "").strip():
        failed.append("STORY_NO_EARLY_VIEWER_QUESTION")
    if verdict.story_turn_scene_index is None:
        failed.append("STORY_NO_TURN")
    if not (verdict.reveal_or_proof_by_second_fifteen or "").strip():
        failed.append("STORY_NO_EARLY_PROOF")
    if verdict.repeated_claims:
        failed.append(f"STORY_REPEATED_CLAIMS:{len(verdict.repeated_claims)}")
    stalled = [s.scene_index for s in verdict.scene_assessments if not s.advances_story]
    if stalled:
        failed.append("STORY_STALLED_SCENES:" + ",".join(map(str, stalled)))
    return failed


async def review(
    runner: TrackedRunner,
    brand: BrandMemory,
    package: ReelPackage,
    *,
    topic_title: str,
    content_id: str | None = None,
    models: ModelsConfig | None = None,
    brief: ContentBrief | None = None,
) -> tuple[TrackedResult[StoryVerdict], list[str]]:
    agent, model, prompt_version = build_agent(
        AGENT_KEY,
        instructions=agent_instructions(AGENT_KEY, models),
        output_type=StoryVerdict,
        models=models,
        name="Reel Story Judge",
    )
    result = await runner.run(
        agent,
        build_context(brand, package, topic_title=topic_title, brief=brief),
        agent_key=AGENT_KEY,
        workflow_key="story_validation",
        model=model,
        prompt_version=prompt_version,
        content_id=content_id,
        extra_metadata={"format": "reel", "stage": "pre_visual"},
    )
    return result, failed_gates(result.output)
