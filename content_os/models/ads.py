"""Paid media data model and deterministic eligibility.

No LLM is ever in the path of a spending decision. The eligibility engine is
pure Python over measured percentiles, and every budget is capped.
"""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, Field


class AdTestStatus(StrEnum):
    PROPOSED = "PROPOSED"
    AWAITING_APPROVAL = "AWAITING_APPROVAL"
    APPROVED = "APPROVED"
    RUNNING = "RUNNING"
    PAUSED = "PAUSED"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


class AdTest(BaseModel):
    id: str
    content_id: str
    creative_id: str | None = None

    audience_name: str

    start_date: datetime | None = None
    end_date: datetime | None = None

    daily_budget: float = 0.0
    total_spend: float = 0.0

    objective: str = "profile_visits"
    status: AdTestStatus = AdTestStatus.PROPOSED

    paid_reach: int = 0
    paid_impressions: int = 0
    paid_profile_visits: int = 0
    paid_followers: int = 0

    cost_per_profile_visit: float | None = None
    cost_per_follower: float | None = None

    quality_adjusted_followers: float | None = None
    quality_adjusted_cpf: float | None = None

    approved_by: str | None = None
    approved_at: datetime | None = None

    created_at: datetime


class AdEligibility(BaseModel):
    content_id: str
    eligible: bool

    organic_performance_percentile: float = 0.0
    profile_visit_percentile: float = 0.0
    follow_conversion_percentile: float = 0.0
    share_percentile: float = 0.0

    reason_codes: list[str] = Field(default_factory=list)
    suggested_test_budget: float | None = None

    # Human approval is always required before any spend, regardless of this
    # object's contents. Present so downstream callers cannot forget.
    requires_human_approval: bool = True
    evaluated_at: datetime | None = None
