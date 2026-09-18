"""Topic discovery and opportunity scoring models.

Split between what an LLM produces (judgement) and what Python produces
(identity, timestamps, arithmetic). Agent-facing models are suffixed Draft or
Rating and never carry ids, timestamps, or computed scores.
"""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, Field


class TopicStatus(StrEnum):
    CANDIDATE = "CANDIDATE"
    SCORED = "SCORED"
    VETOED = "VETOED"
    PLANNED = "PLANNED"
    IN_PRODUCTION = "IN_PRODUCTION"
    PUBLISHED = "PUBLISHED"
    REJECTED = "REJECTED"
    EXPIRED = "EXPIRED"


# --------------------------------------------------------------------------
# Agent-facing (strict-JSON-schema safe: no dicts, no datetimes, no defaults)
# --------------------------------------------------------------------------


class TopicDraft(BaseModel):
    """What the Trend Scout returns. Python assigns id and discovered_at."""

    title: str
    canonical_topic: str
    summary: str

    source_urls: list[str]
    source_types: list[str]

    event_date_iso: str | None

    trend_signals: list[str]
    target_audience: list[str]
    potential_angles: list[str]
    content_pillars: list[str]

    estimated_saturation: float = Field(ge=0.0, le=1.0)

    why_it_matters: str
    discussion_angle: str
    brand_fit_rationale: str


class TopicDiscoveryResult(BaseModel):
    topics: list[TopicDraft]
    discarded_reasons: list[str]


class TopicRating(BaseModel):
    """What the Opportunity Scorer returns.

    Ratings only. The scorer never computes the weighted total; that is done in
    deterministic Python so the arithmetic is testable and auditable.
    """

    brand_fit: float = Field(ge=0.0, le=10.0)
    audience_fit: float = Field(ge=0.0, le=10.0)
    trend_velocity: float = Field(ge=0.0, le=10.0)
    originality: float = Field(ge=0.0, le=10.0)
    visual_potential: float = Field(ge=0.0, le=10.0)
    production_fit: float = Field(ge=0.0, le=10.0)

    estimated_saturation: float = Field(ge=0.0, le=1.0)

    brand_fit_rationale: str
    originality_rationale: str
    saturation_rationale: str
    overall_rationale: str

    recommended_pillar: str
    recommended_format: str


# --------------------------------------------------------------------------
# Persisted
# --------------------------------------------------------------------------


class TopicCandidate(BaseModel):
    """A stored candidate topic. Identity and time are owned by Python."""

    id: str
    title: str
    canonical_topic: str
    summary: str

    source_urls: list[str] = Field(default_factory=list)
    source_types: list[str] = Field(default_factory=list)

    discovered_at: datetime
    event_date: datetime | None = None

    trend_signals: list[str] = Field(default_factory=list)
    target_audience: list[str] = Field(default_factory=list)
    potential_angles: list[str] = Field(default_factory=list)
    content_pillars: list[str] = Field(default_factory=list)

    estimated_saturation: float = 0.0
    freshness_hours: float | None = None

    status: TopicStatus = TopicStatus.CANDIDATE
    run_id: str | None = None

    why_it_matters: str = ""
    discussion_angle: str = ""


class OpportunityScore(BaseModel):
    """An immutable scoring record.

    Every component rating is preserved alongside the computed totals so that we
    can later correlate individual dimensions against real Instagram outcomes.
    Never updated in place; a rescore writes a new row.
    """

    id: str
    topic_id: str
    run_id: str | None = None

    # Raw agent ratings, never overwritten.
    brand_fit: float
    audience_fit: float
    trend_velocity: float
    originality: float
    visual_potential: float
    production_fit: float

    # Deterministic derivations.
    decayed_trend_velocity: float
    base_score: float
    saturation: float
    effective_saturation: float
    saturation_penalty: float
    adjusted_score: float

    vetoed: bool = False
    veto_flag: str | None = None

    scoring_model: str
    scoring_prompt_version: str
    scoring_config_version: str

    rationale: str = ""
    recommended_pillar: str = ""
    recommended_format: str = ""

    created_at: datetime


class ScoredTopic(BaseModel):
    """Join of a topic and its most recent score. Used by the strategist."""

    topic: TopicCandidate
    score: OpportunityScore

    @property
    def rank_key(self) -> float:
        return self.score.adjusted_score
