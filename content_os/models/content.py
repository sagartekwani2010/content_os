"""Content planning, generation, and QA models."""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, Field

ContentFormat = Literal["reel", "carousel", "trial_reel"]
StrategicRole = Literal[
    "reach", "authority", "shareability", "brand_building", "experiment", "conversion"
]
Urgency = Literal["evergreen", "publish_this_week", "publish_24_48h"]


class ContentStatus(StrEnum):
    IDEA = "IDEA"
    PLANNED = "PLANNED"
    GENERATED = "GENERATED"
    QA_FAILED = "QA_FAILED"
    READY_FOR_REVIEW = "READY_FOR_REVIEW"
    APPROVED = "APPROVED"
    PUBLISHED = "PUBLISHED"
    ARCHIVED = "ARCHIVED"


# --------------------------------------------------------------------------
# Strategist
# --------------------------------------------------------------------------


class ContentPlanItem(BaseModel):
    topic_id: str

    proposed_title: str
    format: ContentFormat
    pillar: str
    strategic_role: StrategicRole

    recommended_publish_window: str | None
    urgency: Urgency

    reasoning: str
    primary_hook: str
    alternate_hooks: list[str]

    score: float


class ContentPlan(BaseModel):
    """Strategist output. Portfolio composition is validated in Python."""

    items: list[ContentPlanItem]
    portfolio_rationale: str
    deferred_topic_ids: list[str]
    deferral_reasons: list[str]


# --------------------------------------------------------------------------
# Reel
# --------------------------------------------------------------------------


class Scene(BaseModel):
    index: int
    start_second: float
    end_second: float
    visual: str
    voiceover: str
    on_screen_text: str
    production_mode: str


class ReelPackage(BaseModel):
    title: str

    hook: str
    hook_variants: list[str]

    script: str
    estimated_duration_seconds: int

    scene_plan: list[Scene]

    b_roll_requirements: list[str]
    avatar_requirements: list[str]
    on_screen_text: list[str]
    visual_hook: str

    caption: str
    cta: str | None
    hashtags_or_keywords: list[str]

    factual_claims_to_verify: list[str]
    references: list[str]


# --------------------------------------------------------------------------
# Carousel
# --------------------------------------------------------------------------


class CarouselSlide(BaseModel):
    index: int
    role: str
    headline: str
    body: str
    visual_direction: str


class CarouselPackage(BaseModel):
    title: str
    cover_hook: str

    slides: list[CarouselSlide]

    caption: str
    cta: str | None

    save_reason: str
    share_reason: str

    factual_claims_to_verify: list[str]
    references: list[str]


# --------------------------------------------------------------------------
# QA
# --------------------------------------------------------------------------


class QAScores(BaseModel):
    """Fixed fields rather than dict[str, float].

    Strict structured output does not permit open-ended objects, and named
    fields make the scores queryable later without JSON parsing.
    """

    hook_strength: float = Field(ge=0.0, le=10.0)
    clarity: float = Field(ge=0.0, le=10.0)
    technical_accuracy: float = Field(ge=0.0, le=10.0)
    brand_fit: float = Field(ge=0.0, le=10.0)
    originality: float = Field(ge=0.0, le=10.0)
    share_potential: float = Field(ge=0.0, le=10.0)
    save_potential: float = Field(ge=0.0, le=10.0)
    visual_potential: float = Field(ge=0.0, le=10.0)

    # Penalties: higher means worse.
    ai_hype_penalty: float = Field(ge=0.0, le=10.0)
    generic_content_penalty: float = Field(ge=0.0, le=10.0)

    def as_dict(self) -> dict[str, float]:
        return self.model_dump()


class QAVerdict(BaseModel):
    """Raw QA agent output. The approve/reject decision is recomputed in Python
    against config thresholds so that the gate cannot drift with the prompt."""

    scores: QAScores
    issues: list[str]
    required_changes: list[str]
    agent_recommends_approval: bool
    verdict_rationale: str


class QAResult(BaseModel):
    """Final QA record, after deterministic gating."""

    approved: bool
    scores: dict[str, float]
    composite: float
    issues: list[str]
    required_changes: list[str]
    failed_gates: list[str]
    agent_recommends_approval: bool
    verdict_rationale: str
    revision_number: int = 0
    qa_model: str = ""
    qa_prompt_version: str = ""


# --------------------------------------------------------------------------
# Persisted content
# --------------------------------------------------------------------------


class ContentItem(BaseModel):
    id: str
    topic_id: str
    run_id: str | None = None

    format: ContentFormat
    pillar: str
    strategic_role: str

    title: str
    hook: str
    body_json: str
    caption: str
    cta: str | None = None

    avatar_used: bool = False
    human_used: bool = False
    screen_demo_used: bool = False

    status: ContentStatus = ContentStatus.IDEA

    planned_publish_date: datetime | None = None
    actual_publish_date: datetime | None = None

    # Provenance. Never overwritten.
    generator_agent: str = ""
    generator_model: str = ""
    generator_prompt_version: str = ""

    qa_approved: bool | None = None
    qa_composite: float | None = None
    qa_json: str | None = None

    created_at: datetime
    updated_at: datetime


class CreativeVariant(BaseModel):
    """One testable variant of a content item.

    A single idea may ship with three different hooks. We need to know which one
    actually won, so variants are first-class and link back to the content id.
    """

    id: str
    content_id: str

    variant_type: str
    label: str

    hook: str
    script: str | None = None
    visual_style: str | None = None
    duration_seconds: int | None = None

    is_control: bool = False
    created_at: datetime
