"""Deterministic ad eligibility.

No LLM is ever in the path of a spending decision. This module reads measured
percentiles, applies config thresholds, and caps the suggested budget. It can
recommend; it cannot spend. Every returned object carries
requires_human_approval=True and there is no code path that clears it.
"""

from __future__ import annotations

from datetime import datetime, timezone

from content_os.config import ScoringConfig, load_scoring_config
from content_os.models.ads import AdEligibility
from content_os.storage.db import from_iso
from content_os.storage.repositories import Repositories
from content_os.tools.metrics import (
    compute_derived,
    compute_performance_score,
    percentile_rank,
)


def evaluate_ad_eligibility(
    content_id: str,
    repos: Repositories,
    cfg: ScoringConfig | None = None,
    *,
    now: datetime | None = None,
) -> AdEligibility:
    """Decide whether a post has earned paid amplification.

    The gates exist because boosting a post that organically failed buys reach
    for content the audience already rejected. We only amplify what is already
    working, and only within a capped budget.
    """
    cfg = cfg or load_scoring_config()
    gates = cfg.ad_eligibility
    now = now or datetime.now(timezone.utc)

    result = AdEligibility(content_id=content_id, eligible=False, evaluated_at=now)

    content = repos.content.get(content_id)
    if content is None:
        result.reason_codes.append("CONTENT_NOT_FOUND")
        return result

    perf = repos.performance.latest_for_content(content_id)
    if perf is None:
        result.reason_codes.append("NO_PERFORMANCE_DATA")
        return result

    history = repos.performance.latest_per_content(limit=500)
    peers = [p for p in history if p.content_id != content_id]

    if len(peers) < cfg.performance_score.normalisation.min_history_for_percentile:
        result.reason_codes.append(
            f"INSUFFICIENT_HISTORY:{len(peers)}<"
            f"{cfg.performance_score.normalisation.min_history_for_percentile}"
        )
        return result

    score = compute_performance_score(perf, history, cfg)
    derived = compute_derived(perf)
    peer_derived = [compute_derived(p) for p in peers]

    result.organic_performance_percentile = score.performance_percentile
    result.profile_visit_percentile = percentile_rank(
        derived.profile_visit_rate, [d.profile_visit_rate for d in peer_derived]
    )
    result.follow_conversion_percentile = percentile_rank(
        derived.profile_to_follow_conversion,
        [d.profile_to_follow_conversion for d in peer_derived],
    )
    result.share_percentile = percentile_rank(
        derived.amplification_rate, [d.amplification_rate for d in peer_derived]
    )

    # --- gates -----------------------------------------------------------
    failures: list[str] = []

    if result.organic_performance_percentile < gates.min_performance_percentile:
        failures.append(
            f"ORGANIC_BELOW_THRESHOLD:{result.organic_performance_percentile:.0f}"
            f"<{gates.min_performance_percentile:.0f}"
        )
    if result.profile_visit_percentile < gates.min_profile_visit_percentile:
        failures.append(
            f"PROFILE_VISIT_BELOW_THRESHOLD:{result.profile_visit_percentile:.0f}"
            f"<{gates.min_profile_visit_percentile:.0f}"
        )
    if result.follow_conversion_percentile < gates.min_follow_conversion_percentile:
        failures.append(
            f"FOLLOW_CONVERSION_BELOW_THRESHOLD:"
            f"{result.follow_conversion_percentile:.0f}"
            f"<{gates.min_follow_conversion_percentile:.0f}"
        )
    if result.share_percentile < gates.min_share_percentile:
        failures.append(
            f"SHARE_BELOW_THRESHOLD:{result.share_percentile:.0f}"
            f"<{gates.min_share_percentile:.0f}"
        )

    # Brand alignment: never pay to amplify something that was off-brand.
    score_row = repos.scores.latest_for_topic(content["topic_id"])
    if score_row is None:
        failures.append("NO_OPPORTUNITY_SCORE")
    else:
        if score_row.vetoed:
            failures.append(f"BRAND_VETO:{score_row.veto_flag}")
        if score_row.brand_fit < gates.min_brand_fit:
            failures.append(
                f"BRAND_FIT_BELOW_THRESHOLD:{score_row.brand_fit:.1f}"
                f"<{gates.min_brand_fit:.1f}"
            )

    if content["qa_approved"] is not None and not content["qa_approved"]:
        failures.append("QA_NOT_APPROVED")

    published = from_iso(content["actual_publish_date"])
    if published is None:
        failures.append("NOT_PUBLISHED")
    else:
        days = (now - published).total_seconds() / 86400.0
        if days < gates.min_days_since_publish:
            failures.append(f"TOO_EARLY:{days:.1f}d<{gates.min_days_since_publish}d")
        if days > gates.max_days_since_publish:
            failures.append(f"TOO_OLD:{days:.1f}d>{gates.max_days_since_publish}d")

    if failures:
        result.reason_codes = failures
        return result

    # --- passed: suggest a capped budget ---------------------------------
    budget_cfg = gates.budget
    surplus = result.organic_performance_percentile - gates.min_performance_percentile
    suggested = budget_cfg.base_daily + surplus * budget_cfg.scale_per_percentile_point
    suggested = min(suggested, budget_cfg.max_daily)

    result.eligible = True
    result.suggested_test_budget = round(suggested, 2)
    result.reason_codes = [
        "PASSED_ALL_GATES",
        f"ORGANIC_P{result.organic_performance_percentile:.0f}",
        f"PROFILE_VISIT_P{result.profile_visit_percentile:.0f}",
        f"FOLLOW_CONV_P{result.follow_conversion_percentile:.0f}",
        f"SHARE_P{result.share_percentile:.0f}",
        f"DAILY_BUDGET_CAPPED_AT_{budget_cfg.max_daily:.0f}",
        f"TOTAL_SPEND_CAPPED_AT_{budget_cfg.max_total:.0f}",
        "REQUIRES_HUMAN_APPROVAL",
    ]
    return result


def rank_ad_candidates(
    repos: Repositories, cfg: ScoringConfig | None = None, limit: int = 20
) -> list[AdEligibility]:
    """Evaluate every published post and return the eligible ones, best first."""
    cfg = cfg or load_scoring_config()
    results = [
        evaluate_ad_eligibility(row["id"], repos, cfg)
        for row in repos.content.list(limit=500)
    ]
    eligible = [r for r in results if r.eligible]
    eligible.sort(key=lambda r: r.organic_performance_percentile, reverse=True)
    return eligible[:limit]
