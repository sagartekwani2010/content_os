"""Performance snapshots and deterministically derived metrics.

Snapshots are append-only. A post measured at 24h and again at 7d produces two
rows, never an update. Derived metrics are pure functions of a snapshot and are
recomputed on read rather than trusted from storage, so that changing a formula
retroactively improves every historical analysis.
"""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class PostPerformance(BaseModel):
    """A raw metrics snapshot. Never mutated."""

    id: str
    content_id: str
    creative_id: str | None = None
    platform_post_id: str | None = None

    snapshot_time: datetime
    followers_at_post_time: int | None = None

    impressions: int = 0
    reach: int = 0
    follower_reach: int = 0
    non_follower_reach: int = 0

    plays: int = 0
    avg_watch_time_seconds: float = 0.0
    total_watch_time_seconds: float = 0.0
    video_duration_seconds: float = 0.0

    likes: int = 0
    comments: int = 0
    shares: int = 0
    sends: int = 0
    saves: int = 0

    profile_visits: int = 0
    new_followers: int = 0
    website_clicks: int = 0

    organic_impressions: int = 0
    paid_impressions: int = 0

    created_at: datetime | None = None


class DerivedMetrics(BaseModel):
    """Pure function of a snapshot. Zero denominators yield 0.0, never a crash."""

    content_id: str
    snapshot_time: datetime

    like_rate: float = 0.0
    share_rate: float = 0.0
    send_rate: float = 0.0
    save_rate: float = 0.0
    comment_rate: float = 0.0

    profile_visit_rate: float = 0.0
    follow_per_reach: float = 0.0
    profile_to_follow_conversion: float = 0.0

    watch_ratio: float = 0.0
    completion_rate: float = 0.0
    non_follower_ratio: float = 0.0

    # shares and sends combined, the strongest distribution signal on Instagram
    amplification_rate: float = 0.0


class PerformanceScore(BaseModel):
    """Composite score, normalised against recent account history."""

    content_id: str
    snapshot_time: datetime

    performance_score: float
    performance_percentile: float

    component_percentiles: dict[str, float] = Field(default_factory=dict)
    component_values: dict[str, float] = Field(default_factory=dict)

    normalisation_method: str = "percentile"
    history_size: int = 0
    scoring_config_version: str = ""
