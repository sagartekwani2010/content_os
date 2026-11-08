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

    # Story contracts make every scene earn its time. Empty defaults preserve
    # compatibility with older stored packages while new writers must fill them.
    viewer_question: str = ""
    new_information: str = ""
    belief_shift: str = ""
    visual_proof: str = ""
    cut_rationale: str = ""


class AssetBrief(BaseModel):
    """One production-ready media asset belonging to a content package.

    Image and video quality varies substantially by surface. This deliberately
    captures the complete creative direction needed to regenerate an asset in
    the creator's preferred ChatGPT UI, plus the canonical filename it should
    have in the exported package.
    """

    scene_index: int
    content_unit: Literal["scene", "slide", "cover", "caption_card"] = "scene"
    asset_id: str = ""
    source_type: Literal[
        "real_capture", "screen_recording", "reference_edit", "generated_image",
        "generated_video", "not_needed",
    ]
    rendering_tool: Literal["gpt_2_5", "h3", "not_applicable"] = "not_applicable"
    source_materials: list[str] = Field(default_factory=list)
    purpose: str
    prompt: str = ""
    composition: str = ""
    motion_beats: list[str] = Field(default_factory=list)
    duration_seconds: float | None = None
    on_screen_copy: list[str] = Field(default_factory=list)
    negative_constraints: list[str] = Field(default_factory=list)
    output_filename: str = ""
    asset_path: str | None = None
    alt_text: str = ""


class ReelPackage(BaseModel):
    brief_id: str
    title: str

    hook: str
    hook_variants: list[str]

    script: str
    estimated_duration_seconds: int

    # Required, not optional. A reel that cannot state what the viewer learned
    # is entertainment, and this account is not an entertainment account.
    learning_payoff: str
    save_reason: str
    share_reason: str

    scene_plan: list[Scene]

    avatar_segments: list[str]
    screen_demo_segments: list[str]
    b_roll_requirements: list[str]
    avatar_requirements: list[str]
    on_screen_text: list[str]
    visual_hook: str
    asset_briefs: list[AssetBrief] = Field(default_factory=list)
    thumbnail_asset: AssetBrief | None = None

    caption: str
    cta: str | None
    hashtags_or_keywords: list[str]

    sections_covered: list[str]
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
    brief_id: str
    title: str
    cover_hook: str

    slides: list[CarouselSlide]

    learning_payoff: str
    save_reason: str
    share_reason: str

    visual_structure: list[str]
    asset_briefs: list[AssetBrief] = Field(default_factory=list)
    thumbnail_asset: AssetBrief | None = None

    caption: str
    cta: str | None

    sections_covered: list[str]
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

    # Did the viewer actually learn something substantial, and did the piece
    # execute the brief it was given? Both are hard gates rather than
    # contributions to an average, so neither can be traded away.
    learning_value: float = Field(ge=0.0, le=10.0)
    execution_against_brief: float = Field(ge=0.0, le=10.0)

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

    # Brief compliance, reported explicitly rather than folded into a score.
    sections_covered: list[str]
    sections_missing: list[str]
    thesis_drift: bool
    thesis_drift_explanation: str | None


class StorySceneAssessment(BaseModel):
    scene_index: int
    advances_story: bool
    repeated_scene_indices: list[int] = Field(default_factory=list)
    issue: str | None = None


class StoryVerdict(BaseModel):
    """Cross-model narrative review before visual asset generation."""

    verdict: Literal["PASS", "REWRITE", "BLOCK"]
    narrative_spine: str
    viewer_question_by_second_five: str | None
    story_turn_scene_index: int | None
    reveal_or_proof_by_second_fifteen: str | None
    scene_assessments: list[StorySceneAssessment]
    repeated_claims: list[str] = Field(default_factory=list)
    issues: list[str] = Field(default_factory=list)
    required_changes: list[str] = Field(default_factory=list)
    rationale: str


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
    sections_covered: list[str] = Field(default_factory=list)
    sections_missing: list[str] = Field(default_factory=list)
    thesis_drift: bool = False
    thesis_drift_explanation: str | None = None
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

    # Human strategy, carried from the brief through to the published record so
    # that performance can later be correlated with the decisions that produced
    # it rather than only with the output.
    brief_id: str | None = None
    core_thesis: str = ""
    learning_objective: str = ""
    hook_direction: str = ""
    approved_hook_points: list[str] = Field(default_factory=list)
    high_level_sections: list[str] = Field(default_factory=list)
    preferred_pov: str | None = None
    visual_direction: str | None = None

    hook_strategy: str = ""
    hook_source: str = ""
    hook_variant_id: str = ""

    learning_payoff: str = ""
    save_reason: str = ""
    share_reason: str = ""

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
