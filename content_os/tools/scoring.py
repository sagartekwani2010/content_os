"""Deterministic opportunity scoring.

No LLM is in this module. Agents supply 0-10 judgements on six dimensions and an
estimated saturation; everything from there is arithmetic that can be unit
tested, replayed against historical rows, and audited when a number looks wrong.

Pipeline:
    ratings -> trend decay -> weighted base score
            -> originality-relieved saturation -> bounded penalty
            -> adjusted score -> brand-fit veto
"""

from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone

from content_os.config import ScoringConfig
from content_os.ids import new_id
from content_os.models.content import ContentPlanItem
from content_os.models.topics import OpportunityScore, TopicCandidate, TopicRating

DIMENSIONS = (
    "brand_fit",
    "audience_fit",
    "trend_velocity",
    "originality",
    "visual_potential",
    "production_fit",
)


def clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, value))


def age_hours(reference: datetime | None, now: datetime | None = None) -> float:
    """Hours since a topic's event or discovery. Never negative."""
    if reference is None:
        return 0.0
    now = now or datetime.now(timezone.utc)
    if reference.tzinfo is None:
        reference = reference.replace(tzinfo=timezone.utc)
    delta = (now - reference).total_seconds() / 3600.0
    return max(0.0, delta)


def apply_trend_decay(
    velocity: float, hours_old: float, cfg: ScoringConfig
) -> float:
    """Decay a trend velocity rating by age.

    A topic rated 9/10 for velocity three days ago is not a 9 today. Without
    this, stale news keeps winning the ranking forever.
    """
    decay_cfg = cfg.trend_decay
    if not decay_cfg.enabled or hours_old <= 0:
        return velocity

    retained = 0.5 ** (hours_old / decay_cfg.half_life_hours)
    retained = max(decay_cfg.floor_fraction, retained)
    return velocity * retained


def compute_base_score(ratings: dict[str, float], cfg: ScoringConfig) -> float:
    """Weighted sum of the six dimensions. Output is on the same 0-10 scale."""
    weights = cfg.opportunity_score.weights.as_dict()
    lo = cfg.opportunity_score.dimension_min
    hi = cfg.opportunity_score.dimension_max

    total = 0.0
    for dimension, weight in weights.items():
        value = clamp(float(ratings.get(dimension, 0.0)), lo, hi)
        total += value * weight
    return round(total, 4)


def compute_effective_saturation(
    saturation: float, originality: float, cfg: ScoringConfig
) -> float:
    """Relieve saturation where the brand can credibly own the topic.

    "5 ChatGPT prompts you need" is saturated and nobody owns it. "I built an AI
    clone of myself" may touch a saturated theme but the firsthand build is
    unique, so high originality buys the topic relief from the penalty.
    """
    sat_cfg = cfg.saturation
    effective = clamp(saturation)
    if sat_cfg.originality_offset:
        surplus = max(0.0, originality - sat_cfg.originality_pivot)
        effective = clamp(effective - surplus * sat_cfg.originality_relief_per_point)
    return round(effective, 4)


def compute_saturation_penalty(effective_saturation: float, cfg: ScoringConfig) -> float:
    """Bounded multiplicative penalty in [0, max_penalty].

    The curve exponent means mild saturation is barely punished while heavy
    saturation collapses the score, rather than penalising linearly and treating
    0.3 and 0.9 saturation as merely different by degree.
    """
    sat_cfg = cfg.saturation
    penalty = sat_cfg.max_penalty * (clamp(effective_saturation) ** sat_cfg.curve)
    return round(clamp(penalty, 0.0, sat_cfg.max_penalty), 4)


def check_brand_fit_veto(brand_fit: float, cfg: ScoringConfig) -> tuple[bool, str | None]:
    """A topic below the brand-fit floor cannot be auto-recommended.

    This is the rule that stops the account drifting into an AI-news aggregator
    the first time something enormous trends and scores 10 on velocity.
    """
    if brand_fit < cfg.brand_fit_veto.threshold:
        return True, cfg.brand_fit_veto.flag
    return False, None


def score_topic(
    topic: TopicCandidate,
    rating: TopicRating,
    cfg: ScoringConfig,
    *,
    scoring_model: str,
    scoring_prompt_version: str,
    run_id: str | None = None,
    now: datetime | None = None,
) -> OpportunityScore:
    """Turn agent ratings into an immutable scoring record.

    Every raw rating is preserved alongside the derived numbers. When we later
    ask which dimension actually predicted Instagram performance, the answer has
    to come from stored components, not from a recomputed guess.
    """
    now = now or datetime.now(timezone.utc)

    reference = topic.event_date or topic.discovered_at
    hours_old = age_hours(reference, now)

    decayed_velocity = apply_trend_decay(rating.trend_velocity, hours_old, cfg)

    ratings = {
        "brand_fit": rating.brand_fit,
        "audience_fit": rating.audience_fit,
        "trend_velocity": decayed_velocity,
        "originality": rating.originality,
        "visual_potential": rating.visual_potential,
        "production_fit": rating.production_fit,
    }
    base = compute_base_score(ratings, cfg)

    effective_sat = compute_effective_saturation(
        rating.estimated_saturation, rating.originality, cfg
    )
    penalty = compute_saturation_penalty(effective_sat, cfg)
    adjusted = round(base * (1.0 - penalty), 4)

    vetoed, flag = check_brand_fit_veto(rating.brand_fit, cfg)

    rationale = " | ".join(
        part
        for part in (
            rating.overall_rationale,
            f"brand fit: {rating.brand_fit_rationale}",
            f"originality: {rating.originality_rationale}",
            f"saturation: {rating.saturation_rationale}",
        )
        if part
    )

    return OpportunityScore(
        id=new_id("score"),
        topic_id=topic.id,
        run_id=run_id,
        brand_fit=rating.brand_fit,
        audience_fit=rating.audience_fit,
        trend_velocity=rating.trend_velocity,
        originality=rating.originality,
        visual_potential=rating.visual_potential,
        production_fit=rating.production_fit,
        decayed_trend_velocity=round(decayed_velocity, 4),
        base_score=base,
        saturation=round(clamp(rating.estimated_saturation), 4),
        effective_saturation=effective_sat,
        saturation_penalty=penalty,
        adjusted_score=adjusted,
        vetoed=vetoed,
        veto_flag=flag,
        scoring_model=scoring_model,
        scoring_prompt_version=scoring_prompt_version,
        scoring_config_version=cfg.version,
        rationale=rationale,
        recommended_pillar=rating.recommended_pillar,
        recommended_format=rating.recommended_format,
        created_at=now,
    )


# --------------------------------------------------------------------------
# Portfolio composition
# --------------------------------------------------------------------------


def analyse_portfolio(
    items: list[ContentPlanItem], cfg: ScoringConfig
) -> dict[str, object]:
    """Measure a plan against the target portfolio.

    Deterministic, so the strategist's judgement can be checked rather than
    trusted. Returns the actual distribution, the deviation from target, and any
    guardrail violations.
    """
    portfolio = cfg.portfolio
    total = len(items)
    if total == 0:
        return {
            "total": 0,
            "distribution": {},
            "deviations": {},
            "violations": ["EMPTY_PLAN"],
            "balanced": False,
            "format_counts": {},
            "max_same_format_streak": 0,
        }

    pillar_counts = Counter(item.pillar for item in items)
    format_counts = Counter(item.format for item in items)

    distribution = {p: round(c / total, 4) for p, c in pillar_counts.items()}
    deviations = {
        pillar: round(distribution.get(pillar, 0.0) - target, 4)
        for pillar, target in portfolio.targets.items()
    }

    violations: list[str] = []

    for pillar, count in pillar_counts.items():
        if pillar not in portfolio.targets:
            violations.append(f"UNKNOWN_PILLAR:{pillar}")
        if count > portfolio.max_per_pillar:
            violations.append(f"PILLAR_OVER_CAP:{pillar}={count}")

    if len(pillar_counts) < min(portfolio.min_distinct_pillars, total):
        violations.append(
            f"TOO_FEW_PILLARS:{len(pillar_counts)}<{portfolio.min_distinct_pillars}"
        )

    for pillar, deviation in deviations.items():
        if abs(deviation) > portfolio.tolerance:
            violations.append(f"PILLAR_OFF_TARGET:{pillar}={deviation:+.2f}")

    streak = max_streak = 0
    previous: str | None = None
    for item in items:
        streak = streak + 1 if item.format == previous else 1
        previous = item.format
        max_streak = max(max_streak, streak)
    if max_streak > portfolio.max_same_format_streak:
        violations.append(f"FORMAT_STREAK:{max_streak}")

    topic_ids = [item.topic_id for item in items]
    duplicates = [t for t, c in Counter(topic_ids).items() if c > 1]
    if duplicates:
        violations.append(f"DUPLICATE_TOPICS:{','.join(duplicates)}")

    return {
        "total": total,
        "distribution": distribution,
        "deviations": deviations,
        "violations": violations,
        "balanced": not violations,
        "format_counts": dict(format_counts),
        "max_same_format_streak": max_streak,
        "distinct_pillars": len(pillar_counts),
    }


def portfolio_gap_brief(
    items: list[ContentPlanItem], cfg: ScoringConfig, target_posts: int
) -> str:
    """Human-readable description of what a plan is missing.

    Fed back to the strategist on a rebalance attempt, which works better than
    restating the abstract targets it already has.
    """
    report = analyse_portfolio(items, cfg)
    lines = [f"Current plan has {report['total']} of {target_posts} posts."]

    for pillar, target in cfg.portfolio.targets.items():
        actual = report["distribution"].get(pillar, 0.0)  # type: ignore[union-attr]
        want = round(target * target_posts, 1)
        have = round(actual * report["total"], 1)  # type: ignore[operator]
        lines.append(
            f"  {pillar}: {have} posts ({actual:.0%}), target {want} ({target:.0%})"
        )

    if report["violations"]:
        lines.append("Guardrail violations to fix:")
        lines += [f"  - {v}" for v in report["violations"]]  # type: ignore[union-attr]
    return "\n".join(lines)
