"""Shared fixtures. Every test runs against an in-memory database."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from content_os.config import load_brand, load_scoring_config
from content_os.ids import new_id
from content_os.models.content import ContentItem, ContentStatus
from content_os.models.performance import PostPerformance
from content_os.models.topics import TopicCandidate, TopicRating, TopicStatus
from content_os.storage.db import get_db, utcnow
from content_os.storage.repositories import Repositories


@pytest.fixture
def repos() -> Repositories:
    return Repositories(get_db(":memory:"))


@pytest.fixture
def cfg():
    return load_scoring_config()


@pytest.fixture
def brand():
    return load_brand()


def make_topic(
    title: str = "Agent vs tool vs workflow",
    *,
    saturation: float = 0.2,
    event_date: datetime | None = None,
    canonical: str | None = None,
) -> TopicCandidate:
    return TopicCandidate(
        id=new_id("topic"),
        title=title,
        canonical_topic=canonical or title.lower(),
        summary=f"Summary of {title}",
        source_urls=["https://example.com/a"],
        source_types=["personal_note"],
        discovered_at=datetime.now(timezone.utc),
        event_date=event_date,
        content_pillars=["ai_builder"],
        estimated_saturation=saturation,
        status=TopicStatus.CANDIDATE,
    )


def make_rating(
    *,
    brand_fit: float = 9.0,
    audience_fit: float = 8.0,
    trend_velocity: float = 7.0,
    originality: float = 8.0,
    visual_potential: float = 7.0,
    production_fit: float = 8.0,
    saturation: float = 0.2,
) -> TopicRating:
    return TopicRating(
        brand_fit=brand_fit,
        audience_fit=audience_fit,
        trend_velocity=trend_velocity,
        originality=originality,
        visual_potential=visual_potential,
        production_fit=production_fit,
        estimated_saturation=saturation,
        brand_fit_rationale="r1",
        originality_rationale="r2",
        saturation_rationale="r3",
        overall_rationale="r4",
        recommended_pillar="ai_builder",
        recommended_format="reel",
    )


def make_content(
    topic_id: str,
    *,
    fmt: str = "reel",
    pillar: str = "ai_builder",
    title: str = "Test content",
    hook: str = "Most agents are workflows wearing a costume.",
    avatar: bool = True,
    model: str = "gpt-5",
    prompt_version: str = "reel_writer_v1",
) -> ContentItem:
    now = utcnow()
    return ContentItem(
        id=new_id("content"),
        topic_id=topic_id,
        format=fmt,
        pillar=pillar,
        strategic_role="authority",
        title=title,
        hook=hook,
        body_json="{}",
        caption="caption",
        avatar_used=avatar,
        status=ContentStatus.GENERATED,
        generator_agent="reel_writer",
        generator_model=model,
        generator_prompt_version=prompt_version,
        created_at=now,
        updated_at=now,
    )


def make_performance(
    content_id: str,
    *,
    hours_ago: int = 0,
    reach: int = 10000,
    shares: int = 100,
    saves: int = 200,
    likes: int = 400,
    new_followers: int = 40,
    profile_visits: int = 300,
) -> PostPerformance:
    return PostPerformance(
        id=new_id("performance"),
        content_id=content_id,
        snapshot_time=datetime.now(timezone.utc) - timedelta(hours=hours_ago),
        reach=reach,
        impressions=int(reach * 1.3),
        follower_reach=int(reach * 0.3),
        non_follower_reach=int(reach * 0.7),
        plays=int(reach * 1.2),
        avg_watch_time_seconds=12.0,
        total_watch_time_seconds=12.0 * reach,
        video_duration_seconds=20.0,
        likes=likes,
        comments=30,
        shares=shares,
        sends=int(shares * 0.7),
        saves=saves,
        profile_visits=profile_visits,
        new_followers=new_followers,
    )


@pytest.fixture
def sample_brief():
    """A minimal human-approved brief for testing the brief-driven path."""
    from content_os.ids import new_id
    from content_os.models.brief import BriefStatus, ContentBrief

    return ContentBrief(
        brief_id=new_id("brief"),
        topic="Why AI demos fail in production",
        core_thesis=(
            "Production AI fails because the engineering problem is not the "
            "model. State, latency, evaluation and observability matter equally."
        ),
        why_this_matters="Most public AI examples stop at prototype quality.",
        audience_takeaway="The model is often the easiest part.",
        learning_objective=(
            "Viewer can name the layers production adds to an AI demo."
        ),
        target_audience=["AI engineers", "Technical founders"],
        brand_pillar="ai_builder",
        content_format="carousel",
        hook_direction="Challenge the assumption that the model is the hard part.",
        approved_hook_points=[
            "The model is often the easiest part.",
            "AI demos are easy. Production AI is not.",
        ],
        high_level_sections=[
            "demo architecture",
            "production architecture",
            "evaluation",
            "observability",
        ],
        desired_slide_count=8,
        status=BriefStatus.APPROVED,
        created_at=utcnow(),
    )
