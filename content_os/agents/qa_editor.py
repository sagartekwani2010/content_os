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
from content_os.models.brief import ContentBrief
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
        # Hard gates. Neither can be averaged away by scoring well elsewhere:
        # content that teaches nothing, or that executes a different brief, is
        # a rejection regardless of how good it is.
        ("LEARNING_VALUE_TOO_LOW", scores.learning_value,
         gates.min_learning_value, "min"),
        ("POOR_BRIEF_EXECUTION", scores.execution_against_brief,
         gates.min_execution_against_brief, "min"),
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
    brief: ContentBrief | None = None,
    preflight_failures: list[str] | None = None,
) -> QAResult:
    """Apply the gates. When a brief is supplied, coverage and thesis drift are
    checked in Python from the reported sections rather than being left to the
    composite score, because a missing mandatory section is a binary failure."""
    composite, failed = evaluate_gates(verdict.scores, cfg)

    sections_missing = list(verdict.sections_missing)
    if brief and brief.high_level_sections:
        covered = {s.lower().strip() for s in verdict.sections_covered}
        blob = " ".join(covered)
        for section in brief.high_level_sections:
            key = section.lower().strip()
            if key in covered:
                continue
            # Every distinctive word must appear, not merely one of them.
            # Matching on any word lets "demo architecture" mark "production
            # architecture" as covered, because they share a generic noun, and
            # a genuinely missing section then passes the gate silently.
            words = [w for w in key.split() if len(w) > 3]
            if words and all(w in blob for w in words):
                continue
            if section not in sections_missing:
                sections_missing.append(section)

        if sections_missing:
            failed.append(f"SECTIONS_MISSING:{len(sections_missing)}")

    if verdict.thesis_drift:
        failed.append("THESIS_DRIFT")

    for failure in preflight_failures or []:
        failed.append(f"PREFLIGHT:{failure}")

    return QAResult(
        approved=not failed,
        scores=verdict.scores.as_dict(),
        composite=composite,
        issues=list(verdict.issues),
        required_changes=list(verdict.required_changes),
        failed_gates=failed,
        agent_recommends_approval=verdict.agent_recommends_approval,
        verdict_rationale=verdict.verdict_rationale,
        sections_covered=list(verdict.sections_covered),
        sections_missing=sections_missing,
        thesis_drift=verdict.thesis_drift,
        thesis_drift_explanation=verdict.thesis_drift_explanation,
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
    brief: ContentBrief | None = None,
) -> str:
    parts: list[str] = []
    if brief is not None:
        parts += [
            brief.as_prompt_context(),
            "",
            "Judge the content against THIS brief, not against what you would "
            "have briefed. Report section coverage literally.",
            "",
        ]
    parts += [brand.as_prompt_context(), ""]
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
    brief: ContentBrief | None = None,
    preflight_failures: list[str] | None = None,
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
        brief=brief,
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
        brief=brief,
        preflight_failures=preflight_failures,
    )
    return result, qa_result
