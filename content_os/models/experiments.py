"""Structured experiment tracking.

The point of the system is not to publish content. It is to run experiments and
retain the results, so experiments are a first-class table rather than notes.
"""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, Field


class ExperimentStatus(StrEnum):
    DESIGNED = "DESIGNED"
    RUNNING = "RUNNING"
    CONCLUDED = "CONCLUDED"
    ABANDONED = "ABANDONED"


class Experiment(BaseModel):
    id: str
    name: str
    hypothesis: str

    variable: str
    control: str
    variant: str

    start_date: datetime | None = None
    end_date: datetime | None = None

    primary_metric: str
    secondary_metrics: list[str] = Field(default_factory=list)

    status: ExperimentStatus = ExperimentStatus.DESIGNED

    result: str | None = None
    confidence_notes: str | None = None

    # Content ids enrolled on each arm, so results trace back to real posts.
    control_content_ids: list[str] = Field(default_factory=list)
    variant_content_ids: list[str] = Field(default_factory=list)

    created_at: datetime


class AnalystFinding(BaseModel):
    """The performance analyst must separate what it saw from what it thinks.

    A weak correlation reported as a fact would poison future scoring, so the
    claim type is a required field rather than a matter of phrasing.
    """

    claim_type: str  # OBSERVATION | HYPOTHESIS | RECOMMENDATION
    statement: str
    supporting_metric: str
    sample_size: int
    confidence: str  # low | medium | high
    caveats: list[str]


class PerformanceAnalysis(BaseModel):
    observations: list[AnalystFinding]
    hypotheses: list[AnalystFinding]
    recommendations: list[AnalystFinding]
    proposed_experiments: list[str]
    summary: str
