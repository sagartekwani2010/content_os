"""QA Editor agent plus the deterministic approval gate.

The agent scores and recommends. Python decides. Keeping the approval threshold
in config rather than in the prompt means the publishing bar cannot drift every
time someone edits the QA instructions, and a rejection can always be explained
by naming the gate that failed.
"""

from __future__ import annotations

import json
from typing import Any

from content_os.config import BrandMemory, ModelsConfig, ScoringConfig
from content_os.models.content import QAResult, QAScores, QAVerdict
from content_os.tracking.run_logger import (
    TrackedResult,
    TrackedRunner,
    agent_instructions,
    build_agent,
)

AGENT_KEY = "qa"


def compute_composite(scores: QAScores, cfg: ScoringConfig) -> float:
    """Weighted quality score, reduced by the two penalties.

    Penalties subtract rather than scale so a hype-heavy piece cannot be rescued
    by scoring well everywhere else.
    """
    gates = cfg.qa_gates
    positive = sum(
        getattr(scores, name) * weight
        for name, weight in gates.composite_weights.items()
    )
    penalty = (
        (scores.ai_hype_penalty + scores.generic_content_penalty)
        / 2.0
        * gates.penalty_weight
    )
    return round(max(0.0, positive - penalty), 3)


def evaluate_gates(scores: QAScores, cfg: ScoringConfig) -> tuple[float, list[str]]:
    """Apply configured thresholds. Returns (composite, failed_gate_names)."""
    gates = cfg.qa_gates
    composite = compute_composite(scores, cfg)
    failed: list[str] = []

    checks = (
        ("COMPOSITE_TOO_LOW", composite, gates.min_composite, "min"),
        ("WEAK_HOOK", scores.hook_strength, gates.min_hook_strength, "min"),
        (
            "TECHNICAL_ACCURACY_TOO_LOW",
            scores.technical_accuracy,
            gates.min_technical_accuracy,
            "min",
        ),
        ("OFF_BRAND", scores.brand_fit, gates.min_brand_fit, "min"),
        ("NOT_ORIGINAL_ENOUGH", scores.originality, gates.min_originality, "min"),
        ("TOO_HYPED", scores.ai_hype_penalty, gates.max_ai_hype_penalty, "max"),
        (
            "TOO_GENERIC",
            scores.generic_content_penalty,
            gates.max_generic_content_penalty,
            "max",
        ),
    )

    for name, value, threshold, direction in checks:
        if direction == "min" and value < threshold:
            failed.append(f"{name}:{value:.1f}<{threshold:.1f}")
        elif direction == "max" and value > threshold:
            failed.append(f"{name}:{value:.1f}>{threshold:.1f}")

    return composite, failed


def finalise(
    verdict: QAVerdict,
    cfg: ScoringConfig,
    *,
    revision_number: int,
    qa_model: str,
    qa_prompt_version: str,
) -> QAResult:
    composite, failed = evaluate_gates(verdict.scores, cfg)
    return QAResult(
        approved=not failed,
        scores=verdict.scores.as_dict(),
        composite=composite,
        issues=list(verdict.issues),
        required_changes=list(verdict.required_changes),
        failed_gates=failed,
        agent_recommends_approval=verdict.agent_recommends_approval,
        verdict_rationale=verdict.verdict_rationale,
        revision_number=revision_number,
        qa_model=qa_model,
        qa_prompt_version=qa_prompt_version,
    )


def build_context(
    brand: BrandMemory,
    content_format: str,
    package: Any,
    *,
    topic_title: str,
    recent_content: list[dict[str, Any]],
) -> str:
    parts = [brand.as_prompt_context(), ""]
    parts.append(f"CONTENT FORMAT: {content_format}")
    parts.append(f"UNDERLYING TOPIC: {topic_title}")
    parts.append("")
    parts.append("CONTENT TO REVIEW:")
    parts.append(package.model_dump_json(indent=2))
    parts.append("")

    if recent_content:
        parts.append(
            "RECENTLY PUBLISHED OR PLANNED CONTENT. Flag anything too similar "
            "to these:"
        )
        for c in recent_content[:15]:
            parts.append(
                f"  - [{c.get('format', '?')}] {c.get('title', '')} "
                f"| hook: {c.get('hook') or 'n/a'}"
            )

    return "\n".join(parts)


async def review(
    runner: TrackedRunner,
    brand: BrandMemory,
    cfg: ScoringConfig,
    package: Any,
    *,
    content_format: str,
    topic_title: str,
    topic_id: str | None = None,
    content_id: str | None = None,
    revision_number: int = 0,
    recent_content: list[dict[str, Any]] | None = None,
    models: ModelsConfig | None = None,
) -> tuple[TrackedResult[QAVerdict], QAResult]:
    agent, model, prompt_version = build_agent(
        AGENT_KEY,
        instructions=agent_instructions(AGENT_KEY, models),
        output_type=QAVerdict,
        models=models,
        name="QA Editor",
    )
    prompt = build_context(
        brand,
        content_format,
        package,
        topic_title=topic_title,
        recent_content=recent_content or [],
    )
    result = await runner.run(
        agent,
        prompt,
        agent_key=AGENT_KEY,
        workflow_key="qa",
        model=model,
        prompt_version=prompt_version,
        topic_id=topic_id,
        content_id=content_id,
        extra_metadata={"format": content_format, "revision": str(revision_number)},
    )
    qa_result = finalise(
        result.output,
        cfg,
        revision_number=revision_number,
        qa_model=model,
        qa_prompt_version=prompt_version,
    )
    return result, qa_result
