"""Hook Expander: turns approved hook points into polished variants.

Every variant must trace back to a human-approved hook point. Anything outside
that territory is reported separately rather than being used, because a hook
promising something the human never approved is a contract the script cannot
honour.
"""

from __future__ import annotations

from content_os.config import BrandMemory, ModelsConfig
from content_os.models.brief import ContentBrief, ExecutionPlan, HookSet
from content_os.tracking.run_logger import (
    TrackedResult,
    TrackedRunner,
    agent_instructions,
    build_agent,
)

AGENT_KEY = "hook_expander"

VALID_STRATEGIES = {
    "contrarian", "curiosity", "outcome_first", "mistake",
    "framework", "comparison", "myth_busting", "demonstration",
}


def build_context(
    brand: BrandMemory, brief: ContentBrief, plan: ExecutionPlan
) -> str:
    parts = [brief.as_prompt_context(), ""]
    parts.append("=== EXECUTION PLAN ===")
    parts.append(f"Opening strategy: {plan.opening_strategy}")
    parts.append(f"Narrative arc: {' -> '.join(plan.narrative_arc)}")
    parts.append(f"Closing: {plan.closing_strategy}")
    parts.append("")
    parts.append("Key learning points the hook must be consistent with:")
    parts += [f"  - {p}" for p in plan.key_learning_points]
    parts.append("")

    if brand.losing_hook_patterns:
        parts.append("HOOK PATTERNS THAT FAIL ON THIS ACCOUNT (never use):")
        parts += [f"  - {h}" for h in brand.losing_hook_patterns]
        parts.append("")

    parts.append(
        f"Write 3-5 variants for a {brief.content_format}. Every variant must "
        f"come from an approved hook point. Anything outside that territory "
        f"goes in out_of_scope_ideas."
    )
    return "\n".join(parts)


def verify_hooks(hook_set: HookSet, brief: ContentBrief) -> list[str]:
    """Check variants stayed inside the approved territory."""
    problems: list[str] = []

    if not hook_set.variants:
        problems.append("NO_VARIANTS_PRODUCED")
        return problems

    for variant in hook_set.variants:
        if variant.hook_strategy not in VALID_STRATEGIES:
            problems.append(
                f"UNKNOWN_STRATEGY:{variant.variant_id}={variant.hook_strategy}"
            )
        if not variant.derived_from_point:
            problems.append(f"UNTRACEABLE_HOOK:{variant.variant_id}")

    ids = {v.variant_id for v in hook_set.variants}
    if hook_set.recommended_variant_id not in ids:
        problems.append(
            f"RECOMMENDED_NOT_IN_SET:{hook_set.recommended_variant_id}"
        )

    return problems


def select(hook_set: HookSet) -> tuple[str, str, str]:
    """Return (text, strategy, variant_id) for the recommended hook."""
    chosen = next(
        (v for v in hook_set.variants if v.variant_id == hook_set.recommended_variant_id),
        None,
    )
    if chosen is None and hook_set.variants:
        chosen = hook_set.variants[0]
    if chosen is None:
        return "", "", ""
    return chosen.text, chosen.hook_strategy, chosen.variant_id


async def expand(
    runner: TrackedRunner,
    brand: BrandMemory,
    brief: ContentBrief,
    plan: ExecutionPlan,
    *,
    models: ModelsConfig | None = None,
) -> tuple[TrackedResult[HookSet], list[str]]:
    agent, model, prompt_version = build_agent(
        AGENT_KEY,
        instructions=agent_instructions(AGENT_KEY, models),
        output_type=HookSet,
        models=models,
        name="Hook Expander",
    )
    result = await runner.run(
        agent,
        build_context(brand, brief, plan),
        agent_key=AGENT_KEY,
        workflow_key="produce",
        model=model,
        prompt_version=prompt_version,
        extra_metadata={"brief_id": brief.brief_id},
    )
    hook_set: HookSet = result.output
    hook_set.brief_id = brief.brief_id
    return result, verify_hooks(hook_set, brief)
