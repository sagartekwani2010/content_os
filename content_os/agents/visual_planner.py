"""Visual Planner: turns a written package into an executable shot plan.

Runs after the writer, so it can see the actual words rather than planning
visuals for a script that does not exist yet. It refines the scene plan and
production requirements; it never rewrites the copy.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel

from content_os.config import BrandMemory, ModelsConfig
from content_os.models.brief import ContentBrief
from content_os.models.content import Scene
from content_os.tracking.run_logger import (
    TrackedResult,
    TrackedRunner,
    agent_instructions,
    build_agent,
)

AGENT_KEY = "visual_planner"


class VisualPlan(BaseModel):
    scene_plan: list[Scene]
    visual_hook: str
    on_screen_text: list[str]
    avatar_segments: list[str]
    screen_demo_segments: list[str]
    b_roll_requirements: list[str]
    avatar_requirements: list[str]
    production_notes: list[str]
    estimated_production_minutes: int


class CarouselVisualPlan(BaseModel):
    visual_structure: list[str]
    slide_visual_directions: list[str]
    production_notes: list[str]
    estimated_production_minutes: int


def build_context(
    brand: BrandMemory, brief: ContentBrief, package: Any, fmt: str
) -> str:
    parts = [
        f"FORMAT: {fmt}",
        "",
        "PRODUCTION MODES AVAILABLE: "
        + ", ".join(brand.production.available_modes),
        f"About {int(brand.production.avatar_share_target * 100)}% of Reels are "
        f"avatar-delivered.",
        "",
    ]
    parts += [f"  - {c}" for c in brand.production.constraints]

    if brief.visual_direction:
        parts += ["", f"HUMAN VISUAL DIRECTION (respect this): {brief.visual_direction}"]

    parts += ["", "CONTENT TO PLAN VISUALS FOR:", package.model_dump_json(indent=2)]
    parts += [
        "",
        "Produce an executable shot plan. Do not rewrite the copy. Every second "
        "must be accounted for, and on-screen text must reinforce rather than "
        "repeat the voiceover.",
    ]
    return "\n".join(parts)


async def plan_visuals(
    runner: TrackedRunner,
    brand: BrandMemory,
    brief: ContentBrief,
    package: Any,
    *,
    fmt: str,
    content_id: str | None = None,
    models: ModelsConfig | None = None,
) -> TrackedResult[Any]:
    output_type = VisualPlan if fmt != "carousel" else CarouselVisualPlan
    agent, model, prompt_version = build_agent(
        AGENT_KEY,
        instructions=agent_instructions(AGENT_KEY, models),
        output_type=output_type,
        models=models,
        name="Visual Planner",
    )
    return await runner.run(
        agent,
        build_context(brand, brief, package, fmt),
        agent_key=AGENT_KEY,
        workflow_key="produce",
        model=model,
        prompt_version=prompt_version,
        content_id=content_id,
        extra_metadata={"brief_id": brief.brief_id, "format": fmt},
    )


def apply_to_reel(package: Any, visual: VisualPlan) -> Any:
    """Merge the visual plan into the reel package.

    The writer owns words, the planner owns pictures. Only visual fields are
    replaced, so a planner that drifts cannot silently rewrite the script.
    """
    package.scene_plan = visual.scene_plan
    package.visual_hook = visual.visual_hook or package.visual_hook
    package.on_screen_text = visual.on_screen_text or package.on_screen_text
    package.avatar_segments = visual.avatar_segments
    package.screen_demo_segments = visual.screen_demo_segments
    package.b_roll_requirements = visual.b_roll_requirements
    package.avatar_requirements = visual.avatar_requirements
    return package


def apply_to_carousel(package: Any, visual: CarouselVisualPlan) -> Any:
    package.visual_structure = visual.visual_structure or package.visual_structure
    for slide, direction in zip(package.slides, visual.slide_visual_directions):
        if direction:
            slide.visual_direction = direction
    return package
