"""Historical learning.

Aggregations that answer the questions the system exists to answer: which
pillars, formats, hooks, durations and delivery modes actually work for this
account. All deterministic, all recomputed from immutable snapshots.

These functions are what make the system worth more after 100 posts than after
one. They are also the input to the performance analyst, which interprets them
but never produces the numbers itself.
"""

from __future__ import annotations

import re
import sqlite3
from typing import Any, Callable

from content_os.config import ScoringConfig, load_scoring_config
from content_os.storage.repositories import Repositories
from content_os.tools.metrics import (
    compute_derived,
    compute_performance_score,
    summarise,
)

# Deterministic hook classification. Order matters: the first pattern that
# matches wins, so the more specific categories are checked first.
HOOK_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("contrarian", re.compile(
        r"\b(don'?t|doesn'?t|isn'?t|aren'?t|never|stop|wrong|myth|not\s+a|"
        r"nobody|overrated|unpopular|actually)\b", re.I)),
    ("numeric", re.compile(
        r"(\d+\s*%|\b\d+x\b|^\s*\d+\b|\b\d+\s+(reasons|ways|things|mistakes|"
        r"lessons|times)\b)", re.I)),
    ("demo_reveal", re.compile(
        r"\b(i built|i made|i cloned|watch|this (video|clip|demo)|here'?s what|"
        r"look at|wasn'?t filmed|check this)\b", re.I)),
    # Educational is checked before question so "How to build an agent" is not
    # miscounted as a question hook purely because it opens with "how".
    ("educational", re.compile(
        r"\b(how to|explained|guide|understand|learn|basics|introduction|"
        r"the difference between|a guide)\b", re.I)),
    ("question", re.compile(r"\?\s*$|^\s*(why|what|how|when|should|can|do|does)\b", re.I)),
]


def classify_hook(hook: str | None) -> str:
    """Bucket a hook into a comparable type.

    Rule-based rather than model-based on purpose: hook classification feeds
    performance comparisons, and a classifier that drifts between runs would
    make historical buckets incomparable.
    """
    if not hook or not hook.strip():
        return "unknown"
    for label, pattern in HOOK_PATTERNS:
        if pattern.search(hook):
            return label
    return "statement"


def duration_bucket(seconds: float | None) -> str:
    if not seconds or seconds <= 0:
        return "unknown"
    if seconds <= 15:
        return "0-15s"
    if seconds <= 25:
        return "16-25s"
    if seconds <= 35:
        return "26-35s"
    if seconds <= 60:
        return "36-60s"
    return "60s+"


def _delivery_mode(row: sqlite3.Row) -> str:
    if row["avatar_used"]:
        return "ai_avatar"
    if row["screen_demo_used"]:
        return "screen_demo"
    if row["human_used"]:
        return "human"
    return "unspecified"


def build_dataset(
    repos: Repositories, cfg: ScoringConfig | None = None
) -> list[dict[str, Any]]:
    """Join published content to its latest performance snapshot.

    One row per content item that has at least one measurement. Content with no
    performance data is excluded rather than counted as zero, which would drag
    every average toward nothing.
    """
    cfg = cfg or load_scoring_config()
    history = repos.performance.latest_per_content(limit=500)
    by_content = {p.content_id: p for p in history}

    dataset: list[dict[str, Any]] = []
    for content in repos.content.list(limit=500):
        perf = by_content.get(content["id"])
        if perf is None:
            continue

        derived = compute_derived(perf)
        score = compute_performance_score(perf, history, cfg)
        variants = repos.variants.for_content(content["id"])

        dataset.append(
            {
                "content_id": content["id"],
                "topic_id": content["topic_id"],
                "title": content["title"],
                "hook": content["hook"],
                "hook_type": classify_hook(content["hook"]),
                "format": content["format"],
                "pillar": content["pillar"],
                "strategic_role": content["strategic_role"],
                "delivery_mode": _delivery_mode(content),
                "avatar_used": bool(content["avatar_used"]),
                "duration_seconds": perf.video_duration_seconds,
                "duration_bucket": duration_bucket(perf.video_duration_seconds),
                "qa_composite": content["qa_composite"],
                "performance_score": score.performance_score,
                "performance_percentile": score.performance_percentile,
                "reach": perf.reach,
                "derived": derived,
                "metrics": {
                    "share_rate": derived.share_rate,
                    "save_rate": derived.save_rate,
                    "like_rate": derived.like_rate,
                    "comment_rate": derived.comment_rate,
                    "amplification_rate": derived.amplification_rate,
                    "profile_visit_rate": derived.profile_visit_rate,
                    "follow_per_reach": derived.follow_per_reach,
                    "profile_to_follow_conversion": derived.profile_to_follow_conversion,
                    "watch_ratio": derived.watch_ratio,
                    "non_follower_ratio": derived.non_follower_ratio,
                },
            }
        )
    return dataset


def _group(
    dataset: list[dict[str, Any]],
    key: Callable[[dict[str, Any]], str],
    metrics: tuple[str, ...] = (
        "performance_score",
        "share_rate",
        "save_rate",
        "follow_per_reach",
        "profile_visit_rate",
        "watch_ratio",
    ),
) -> dict[str, dict[str, Any]]:
    buckets: dict[str, list[dict[str, Any]]] = {}
    for row in dataset:
        buckets.setdefault(key(row), []).append(row)

    out: dict[str, dict[str, Any]] = {}
    for bucket, rows in sorted(buckets.items()):
        entry: dict[str, Any] = {"count": len(rows)}
        for metric in metrics:
            if metric == "performance_score":
                values = [r["performance_score"] for r in rows]
            else:
                values = [r["metrics"].get(metric, 0.0) for r in rows]
            entry[metric] = summarise(values)
        entry["avg_reach"] = round(
            sum(r["reach"] for r in rows) / len(rows), 1
        )
        out[bucket] = entry
    return out


def get_performance_by_pillar(repos: Repositories) -> dict[str, dict[str, Any]]:
    return _group(build_dataset(repos), lambda r: r["pillar"])


def get_performance_by_format(repos: Repositories) -> dict[str, dict[str, Any]]:
    return _group(build_dataset(repos), lambda r: r["format"])


def get_performance_by_hook_type(repos: Repositories) -> dict[str, dict[str, Any]]:
    return _group(build_dataset(repos), lambda r: r["hook_type"])


def get_performance_by_avatar_usage(repos: Repositories) -> dict[str, dict[str, Any]]:
    return _group(build_dataset(repos), lambda r: r["delivery_mode"])


def get_performance_by_duration_bucket(repos: Repositories) -> dict[str, dict[str, Any]]:
    return _group(build_dataset(repos), lambda r: r["duration_bucket"])


def get_performance_by_strategic_role(repos: Repositories) -> dict[str, dict[str, Any]]:
    return _group(build_dataset(repos), lambda r: r["strategic_role"] or "unset")


def get_top_content(repos: Repositories, n: int = 20) -> list[dict[str, Any]]:
    data = build_dataset(repos)
    return sorted(data, key=lambda r: r["performance_score"], reverse=True)[:n]


def get_bottom_content(repos: Repositories, n: int = 20) -> list[dict[str, Any]]:
    data = build_dataset(repos)
    return sorted(data, key=lambda r: r["performance_score"])[:n]


def scoring_dimension_correlation(repos: Repositories) -> dict[str, Any]:
    """Which opportunity dimension actually predicted performance.

    This is the long-term payoff of storing every component score rather than
    just the total. With enough posts it tells us whether our weights are right.
    """
    dataset = build_dataset(repos)
    if len(dataset) < 3:
        return {
            "sufficient_data": False,
            "n": len(dataset),
            "note": "Need at least 3 measured posts before correlating dimensions.",
        }

    dimensions = (
        "brand_fit", "audience_fit", "trend_velocity",
        "originality", "visual_potential", "production_fit",
    )
    pairs: dict[str, list[tuple[float, float]]] = {d: [] for d in dimensions}

    for row in dataset:
        score = repos.scores.latest_for_topic(row["topic_id"])
        if not score:
            continue
        for dimension in dimensions:
            pairs[dimension].append(
                (float(getattr(score, dimension)), row["performance_score"])
            )

    out: dict[str, Any] = {"sufficient_data": True, "n": len(dataset), "correlations": {}}
    for dimension, points in pairs.items():
        out["correlations"][dimension] = {
            "n": len(points),
            "pearson_r": _pearson(points),
        }
    return out


def _pearson(points: list[tuple[float, float]]) -> float | None:
    """Pearson correlation. Returns None rather than a number when the sample is
    too small or has no variance, so a meaningless value is never reported."""
    n = len(points)
    if n < 3:
        return None
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    mx, my = sum(xs) / n, sum(ys) / n
    num = sum((x - mx) * (y - my) for x, y in points)
    dx = sum((x - mx) ** 2 for x in xs) ** 0.5
    dy = sum((y - my) ** 2 for y in ys) ** 0.5
    if dx == 0 or dy == 0:
        return None
    return round(num / (dx * dy), 4)


def leaderboard(repos: Repositories, n: int = 20) -> dict[str, Any]:
    """Everything the `leaderboard` command prints, in one call."""
    dataset = build_dataset(repos)
    return {
        "measured_posts": len(dataset),
        "top": get_top_content(repos, n),
        "bottom": get_bottom_content(repos, min(n, 10)),
        "by_pillar": _group(dataset, lambda r: r["pillar"]),
        "by_format": _group(dataset, lambda r: r["format"]),
        "by_hook_type": _group(dataset, lambda r: r["hook_type"]),
        "by_delivery": _group(dataset, lambda r: r["delivery_mode"]),
        "by_duration": _group(dataset, lambda r: r["duration_bucket"]),
    }
