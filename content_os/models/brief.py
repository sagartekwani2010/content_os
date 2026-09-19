"""The ContentBrief: human strategy, authoritative.

This is the inversion point of the system. The human decides what to make and
why; agents decide how to execute it. Every field here is strategy, and agents
may improve execution against it but may not silently change it.

Six fields are immutable through the pipeline: topic, core_thesis,
learning_objective, content_format, brand_pillar, and high_level_sections. An
agent that disagrees with any of them raises a concern rather than acting on it,
because a system that quietly substitutes its own judgement for the operator's
is not a tool, it is a second opinion you cannot audit.
"""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, Field, field_validator

BriefFormat = Literal["reel", "carousel", "trial_reel"]
BriefUrgency = Literal["evergreen", "this_week", "24_48h"]

# Fields an agent must never alter. Enforced in code, not merely asked for in
# a prompt, because a prompt instruction is a request and this is a guarantee.
IMMUTABLE_FIELDS = (
    "topic",
    "core_thesis",
    "learning_objective",
    "content_format",
    "brand_pillar",
    "high_level_sections",
)


class BriefStatus(StrEnum):
    DRAFT = "DRAFT"
    HUMAN_REVIEW = "HUMAN_REVIEW"
    APPROVED = "APPROVED"
    IN_PRODUCTION = "IN_PRODUCTION"
    READY = "READY"
    PUBLISHED = "PUBLISHED"
    REJECTED = "REJECTED"
    ARCHIVED = "ARCHIVED"


class HookStrategy(StrEnum):
    """How a hook works, stored so hook approach can later be correlated with
    performance rather than guessed at."""

    CONTRARIAN = "contrarian"
    CURIOSITY = "curiosity"
    OUTCOME_FIRST = "outcome_first"
    MISTAKE = "mistake"
    FRAMEWORK = "framework"
    COMPARISON = "comparison"
    MYTH_BUSTING = "myth_busting"
    DEMONSTRATION = "demonstration"


class ContentBrief(BaseModel):
    """Human-authored strategy. The source of truth for generation."""

    brief_id: str

    topic: str
    core_thesis: str
    why_this_matters: str
    audience_takeaway: str
    learning_objective: str

    target_audience: list[str] = Field(default_factory=list)
    brand_pillar: str
    content_format: BriefFormat

    hook_direction: str
    approved_hook_points: list[str] = Field(default_factory=list)

    high_level_sections: list[str] = Field(default_factory=list)
    core_examples: list[str] = Field(default_factory=list)

    preferred_pov: str | None = None
    desired_tone: str = "Clear, confident, practitioner-led, useful, non-hype."
    visual_direction: str | None = None

    desired_duration_seconds: int | None = None
    desired_slide_count: int | None = None

    references: list[str] = Field(default_factory=list)
    factual_claims_to_verify: list[str] = Field(default_factory=list)

    must_include: list[str] = Field(default_factory=list)
    must_avoid: list[str] = Field(default_factory=list)

    cta_direction: str | None = None
    urgency: BriefUrgency = "evergreen"
    notes: str | None = None

    # Workflow state.
    status: BriefStatus = BriefStatus.DRAFT
    priority: int = 3
    scheduled_date: datetime | None = None
    created_at: datetime | None = None
    approved_at: datetime | None = None
    published_at: datetime | None = None
    approved_by: str | None = None

    @field_validator("approved_hook_points")
    @classmethod
    def _hook_points_bounded(cls, value: list[str]) -> list[str]:
        if len(value) > 8:
            raise ValueError(
                "approved_hook_points should be 2-5 concepts. More than eight "
                "stops being a direction and becomes a list of unrelated ideas."
            )
        return value

    def fingerprint(self) -> dict[str, object]:
        """The immutable fields, for verifying nothing drifted in generation."""
        return {field: getattr(self, field) for field in IMMUTABLE_FIELDS}

    def as_prompt_context(self) -> str:
        """Render the brief for an agent. Mandatory items are marked as such."""
        lines = [
            "=== HUMAN-APPROVED CONTENT BRIEF ===",
            "This brief is authoritative. You may improve how it is executed.",
            "You may not change what it is about.",
            "",
            f"TOPIC: {self.topic}",
            "",
            f"CORE THESIS (do not alter): {self.core_thesis}",
            "",
            f"WHY THIS MATTERS NOW: {self.why_this_matters}",
            "",
            f"LEARNING OBJECTIVE (do not alter): {self.learning_objective}",
            f"AUDIENCE TAKEAWAY: {self.audience_takeaway}",
            "",
            f"FORMAT (do not change): {self.content_format}",
            f"BRAND PILLAR (do not change): {self.brand_pillar}",
            f"URGENCY: {self.urgency}",
        ]

        if self.target_audience:
            lines.append(f"TARGET AUDIENCE: {', '.join(self.target_audience)}")

        lines += ["", f"HOOK DIRECTION: {self.hook_direction}"]
        if self.approved_hook_points:
            lines.append("APPROVED HOOK POINTS (stay inside this territory):")
            lines += [f"  - {p}" for p in self.approved_hook_points]

        if self.high_level_sections:
            lines += [
                "",
                "MANDATORY SECTIONS. Every one of these must be covered. You may "
                "reorder and reword them; you may not drop one:",
            ]
            lines += [
                f"  {i}. {s}" for i, s in enumerate(self.high_level_sections, 1)
            ]

        if self.core_examples:
            lines += ["", "CORE EXAMPLES TO USE:"]
            lines += [f"  - {e}" for e in self.core_examples]

        if self.preferred_pov:
            lines += ["", f"POINT OF VIEW: {self.preferred_pov}"]
        lines += ["", f"TONE: {self.desired_tone}"]

        if self.visual_direction:
            lines.append(f"VISUAL DIRECTION: {self.visual_direction}")
        if self.desired_duration_seconds:
            lines.append(f"TARGET DURATION: {self.desired_duration_seconds} seconds")
        if self.desired_slide_count:
            lines.append(f"TARGET SLIDE COUNT: {self.desired_slide_count}")

        if self.must_include:
            lines += ["", "MUST INCLUDE:"]
            lines += [f"  - {m}" for m in self.must_include]
        if self.must_avoid:
            lines += ["", "MUST AVOID:"]
            lines += [f"  - {m}" for m in self.must_avoid]

        if self.cta_direction:
            lines += ["", f"CTA DIRECTION: {self.cta_direction}"]
        if self.references:
            lines += ["", "REFERENCES:"] + [f"  - {r}" for r in self.references]
        if self.factual_claims_to_verify:
            lines += ["", "CLAIMS THE HUMAN HAS ALREADY FLAGGED FOR VERIFICATION:"]
            lines += [f"  - {c}" for c in self.factual_claims_to_verify]
        if self.notes:
            lines += ["", f"NOTES: {self.notes}"]

        return "\n".join(lines)


class ExecutionPlan(BaseModel):
    """The strategist's output under the new role.

    It plans how to execute a brief. It does not choose what to make. Concerns
    about the brief go in risks_or_gaps and the alternate-format fields, where a
    human can see them, rather than being silently acted upon.
    """

    brief_id: str
    format: str

    narrative_arc: list[str]
    opening_strategy: str

    key_learning_points: list[str]
    supporting_examples: list[str]
    visual_beats: list[str]
    closing_strategy: str

    section_coverage_plan: list[str]

    risks_or_gaps: list[str]
    factual_items_to_verify: list[str]

    # The agent may recommend a different format. It may not apply one.
    alternate_format_recommendation: str | None
    alternate_format_reason: str | None


class HookVariant(BaseModel):
    variant_id: str
    text: str
    hook_strategy: str
    derived_from_point: str
    rationale: str


class HookSet(BaseModel):
    """Expanded hooks, traceable back to the human-approved points they came
    from, so hook approach can later be correlated with performance."""

    brief_id: str
    recommended_variant_id: str
    variants: list[HookVariant]
    out_of_scope_ideas: list[str]
