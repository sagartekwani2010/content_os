"""Derived performance metrics and the composite performance score.

Pure functions over raw snapshots. Nothing here is stored as the only record of
a number: every rate is recomputed from the immutable snapshot on read, so
changing a formula retroactively improves every historical comparison instead of
invalidating it.

Every division goes through safe_div. Instagram routinely reports zero reach on
a fresh post, and a ZeroDivisionError during a nightly ingest would lose data.
"""

from __future__ import annotations

from statistics import median
from typing import Iterable, Sequence

from content_os.config import ScoringConfig
from content_os.models.performance import (
    DerivedMetrics,
    PerformanceScore,
    PostPerformance,
)

# Components of the composite score, in the order they appear in config.
SCORE_COMPONENTS = (
    "share_rate",
    "follow_per_reach",
    "profile_visit_rate",
    "save_rate",
    "watch_ratio",
    "like_rate",
)


def safe_div(numerator: float, denominator: float, default: float = 0.0) -> float:
    """Division that cannot crash an ingest.

    A zero denominator means "we have no evidence", which is 0.0, not an error
    and not infinity.
    """
    try:
        if denominator is None or denominator == 0:
            return default
        result = numerator / denominator
    except (TypeError, ZeroDivisionError):
        return default
    if result != result or result in (float("inf"), float("-inf")):  # NaN or inf
        return default
    return result


def compute_derived(perf: PostPerformance) -> DerivedMetrics:
    """All engagement rates for one snapshot."""
    reach = perf.reach

    return DerivedMetrics(
        content_id=perf.content_id,
        snapshot_time=perf.snapshot_time,
        like_rate=safe_div(perf.likes, reach),
        share_rate=safe_div(perf.shares, reach),
        send_rate=safe_div(perf.sends, reach),
        save_rate=safe_div(perf.saves, reach),
        comment_rate=safe_div(perf.comments, reach),
        profile_visit_rate=safe_div(perf.profile_visits, reach),
        follow_per_reach=safe_div(perf.new_followers, reach),
        profile_to_follow_conversion=safe_div(perf.new_followers, perf.profile_visits),
        watch_ratio=safe_div(perf.avg_watch_time_seconds, perf.video_duration_seconds),
        completion_rate=safe_div(
            perf.total_watch_time_seconds,
            perf.plays * perf.video_duration_seconds
            if perf.plays and perf.video_duration_seconds
            else 0,
        ),
        non_follower_ratio=safe_div(perf.non_follower_reach, reach),
        # Shares and sends together are the strongest distribution signal, and
        # Instagram splits them inconsistently across surfaces.
        amplification_rate=safe_div(perf.shares + perf.sends, reach),
    )


def percentile_rank(value: float, population: Sequence[float]) -> float:
    """Percentile of a value within a population, 0-100.

    Uses the midpoint convention so identical values do not all land at 100,
    which would make a flat history look uniformly excellent.
    """
    if not population:
        return 50.0
    below = sum(1 for v in population if v < value)
    equal = sum(1 for v in population if v == value)
    return round(100.0 * (below + 0.5 * equal) / len(population), 2)


def _normalise_component(
    name: str,
    value: float,
    population: Sequence[float],
    cfg: ScoringConfig,
) -> float:
    """Map a raw rate to 0-1.

    With enough history we use the percentile against recent posts, because an
    account's "good" share rate changes as it grows. Below that threshold we
    fall back to absolute anchors from config so early posts still get a
    meaningful score rather than everything scoring 50.
    """
    norm = cfg.performance_score.normalisation
    if len(population) >= norm.min_history_for_percentile:
        return percentile_rank(value, population) / 100.0

    anchor = norm.fallback_anchors.get(name, 0.0)
    if anchor <= 0:
        return 0.0
    return min(1.0, safe_div(value, anchor))


def compute_performance_score(
    perf: PostPerformance,
    history: Iterable[PostPerformance],
    cfg: ScoringConfig,
) -> PerformanceScore:
    """Composite score for one snapshot, normalised against recent history.

    History should be the most recent N snapshots for other posts. The post
    being scored is excluded from its own population so a single outlier does
    not normalise against itself.
    """
    norm = cfg.performance_score.normalisation
    weights = cfg.performance_score.weights

    history_list = [h for h in history if h.content_id != perf.content_id]
    history_list = sorted(history_list, key=lambda h: h.snapshot_time, reverse=True)
    history_list = history_list[: norm.lookback_posts]

    derived_history = [compute_derived(h) for h in history_list]
    derived = compute_derived(perf)

    component_values: dict[str, float] = {}
    component_percentiles: dict[str, float] = {}
    score = 0.0

    for component, weight in weights.items():
        value = float(getattr(derived, component, 0.0))
        population = [float(getattr(d, component, 0.0)) for d in derived_history]

        normalised = _normalise_component(component, value, population, cfg)
        component_values[component] = round(value, 6)
        component_percentiles[component] = round(normalised * 100.0, 2)
        score += weight * normalised

    score = round(score * 100.0, 2)

    # Percentile of this composite against the same history, scored identically.
    peer_scores: list[float] = []
    for peer, peer_derived in zip(history_list, derived_history):
        peer_total = 0.0
        for component, weight in weights.items():
            value = float(getattr(peer_derived, component, 0.0))
            population = [
                float(getattr(d, component, 0.0))
                for d in derived_history
                if d.content_id != peer_derived.content_id
            ]
            peer_total += weight * _normalise_component(component, value, population, cfg)
        peer_scores.append(round(peer_total * 100.0, 2))

    return PerformanceScore(
        content_id=perf.content_id,
        snapshot_time=perf.snapshot_time,
        performance_score=score,
        performance_percentile=percentile_rank(score, peer_scores),
        component_percentiles=component_percentiles,
        component_values=component_values,
        normalisation_method=(
            norm.method
            if len(derived_history) >= norm.min_history_for_percentile
            else "absolute_anchor"
        ),
        history_size=len(derived_history),
        scoring_config_version=cfg.version,
    )


def median_or_zero(values: Sequence[float]) -> float:
    return round(median(values), 6) if values else 0.0


def summarise(values: Sequence[float]) -> dict[str, float]:
    """Compact distribution summary used across the analytics functions."""
    if not values:
        return {"n": 0, "median": 0.0, "mean": 0.0, "min": 0.0, "max": 0.0}
    return {
        "n": len(values),
        "median": round(median(values), 6),
        "mean": round(sum(values) / len(values), 6),
        "min": round(min(values), 6),
        "max": round(max(values), 6),
    }
