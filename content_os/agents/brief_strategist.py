"""Brief Strategist: plans how to execute a human-approved brief.

Replaces topic selection with execution planning. The immutable fields of the
brief are verified in Python after the agent responds, because a prompt
instruction not to change the thesis is a request, and this needs to be a
guarantee.
"""

from __future__ import annotations

from typing import Any

from content_os.config import BrandMemory, ModelsConfig
from content_os.models.brief import ContentBrief, ExecutionPlan
from content_os.tracking.run_logger import (
    TrackedResult,
    TrackedRunner,
    agent_instructions,
    build_agent,
)

AGENT_KEY = "brief_strategist"


def build_context(
    brand: BrandMemory, brief: ContentBrief, recent_content: list[dict[str, Any]]
) -> str:
    parts = [brief.as_prompt_context(), "", "=== BRAND CONTEXT ===", ""]
    parts.append(brand.as_prompt_context())

    if recent_content:
        parts += ["", "RECENTLY PUBLISHED OR PLANNED (avoid repeating these):"]
        for c in recent_content[:12]:
            parts.append(f"  - [{c.get('format', '?')}] {c.get('title', '')}")

    parts += [
        "",
        "Produce an execution plan for this brief. Plan the format you were "
        "given. Cover every mandatory section. Put disagreements in "
        "risks_or_gaps rather than acting on them.",
    ]
    return "\n".join(parts)


def verify_plan(plan: ExecutionPlan, brief: ContentBrief) -> list[str]:
    """Check the plan against the brief's immutable fields.

    Returns drift warnings. The agent is told not to change these; this is what
    catches it when the instruction is not followed.
    """
    problems: list[str] = []

    if plan.format != brief.content_format:
        problems.append(
            f"FORMAT_CHANGED: plan says '{plan.format}', brief says "
            f"'{brief.content_format}'. Brief wins."
        )

    covered = " ".join(plan.section_coverage_plan + plan.narrative_arc).lower()
    for section in brief.high_level_sections:
        key = section.lower().strip()
        # Match on the distinctive words of the section rather than the whole
        # phrase, since the planner is allowed to reword.
        words = [w for w in key.split() if len(w) > 3]
        if words and not any(w in covered for w in words):
            problems.append(f"SECTION_NOT_PLANNED: {section}")

    return problems


async def plan_execution(
    runner: TrackedRunner,
    brand: BrandMemory,
    brief: ContentBrief,
    *,
    recent_content: list[dict[str, Any]] | None = None,
    models: ModelsConfig | None = None,
) -> tuple[TrackedResult[ExecutionPlan], list[str]]:
    agent, model, prompt_version = build_agent(
        AGENT_KEY,
        instructions=agent_instructions(AGENT_KEY, models),
        output_type=ExecutionPlan,
        models=models,
        name="Brief Strategist",
    )
    result = await runner.run(
        agent,
        build_context(brand, brief, recent_content or []),
        agent_key=AGENT_KEY,
        workflow_key="produce",
        model=model,
        prompt_version=prompt_version,
        extra_metadata={"brief_id": brief.brief_id, "format": brief.content_format},
    )

    plan: ExecutionPlan = result.output
    # The brief is the source of truth. Reassert it rather than trusting the
    # agent to have preserved it.
    plan.brief_id = brief.brief_id
    plan.format = brief.content_format

    return result, verify_plan(plan, brief)
