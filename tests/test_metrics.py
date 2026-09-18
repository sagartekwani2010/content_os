"""Derived metrics. Zero denominators must never crash an ingest."""

from __future__ import annotations

from datetime import datetime, timezone

import pytest

from content_os.ids import new_id
from content_os.models.performance import PostPerformance
from content_os.tools.metrics import (
    compute_derived,
    compute_performance_score,
    percentile_rank,
    safe_div,
)
from tests.conftest import make_performance


class TestSafeDivision:
    def test_zero_denominator_returns_zero(self):
        assert safe_div(10, 0) == 0.0

    def test_both_zero_returns_zero(self):
        assert safe_div(0, 0) == 0.0

    def test_none_denominator_returns_zero(self):
        assert safe_div(10, None) == 0.0

    def test_normal_division_is_exact(self):
        assert safe_div(1, 4) == 0.25

    def test_custom_default_is_respected(self):
        assert safe_div(1, 0, default=-1.0) == -1.0


class TestDerivedMetrics:
    def test_empty_snapshot_computes_without_raising(self):
        """A post measured the second it goes live has zero reach."""
        empty = PostPerformance(
            id=new_id("performance"),
            content_id="c1",
            snapshot_time=datetime.now(timezone.utc),
        )
        derived = compute_derived(empty)
        assert derived.like_rate == 0.0
        assert derived.share_rate == 0.0
        assert derived.watch_ratio == 0.0
        assert derived.profile_to_follow_conversion == 0.0
        assert derived.completion_rate == 0.0

    def test_rates_are_computed_against_reach(self):
        perf = make_performance("c1", reach=10_000, shares=100, saves=200, likes=400)
        derived = compute_derived(perf)
        assert derived.share_rate == pytest.approx(0.01)
        assert derived.save_rate == pytest.approx(0.02)
        assert derived.like_rate == pytest.approx(0.04)

    def test_amplification_combines_shares_and_sends(self):
        perf = make_performance("c1", reach=1000, shares=10)
        derived = compute_derived(perf)
        assert derived.amplification_rate == pytest.approx(
            (perf.shares + perf.sends) / 1000
        )

    def test_watch_ratio_uses_duration(self):
        perf = make_performance("c1")
        perf.avg_watch_time_seconds = 15.0
        perf.video_duration_seconds = 20.0
        assert compute_derived(perf).watch_ratio == pytest.approx(0.75)

    def test_zero_profile_visits_does_not_break_conversion(self):
        perf = make_performance("c1", profile_visits=0, new_followers=5)
        assert compute_derived(perf).profile_to_follow_conversion == 0.0

    def test_carousel_with_no_video_duration_survives(self):
        perf = make_performance("c1")
        perf.video_duration_seconds = 0.0
        perf.avg_watch_time_seconds = 0.0
        assert compute_derived(perf).watch_ratio == 0.0


class TestPercentileRank:
    def test_empty_population_is_neutral(self):
        assert percentile_rank(5.0, []) == 50.0

    def test_highest_value_ranks_high(self):
        assert percentile_rank(10, [1, 2, 3, 4]) == 100.0

    def test_lowest_value_ranks_low(self):
        assert percentile_rank(0, [1, 2, 3, 4]) == 0.0

    def test_identical_values_land_midway_not_at_the_top(self):
        """A flat history should not make every post look excellent."""
        assert percentile_rank(5, [5, 5, 5, 5]) == 50.0


class TestPerformanceScore:
    def test_score_with_no_history_uses_absolute_anchors(self, cfg):
        perf = make_performance("c1")
        score = compute_performance_score(perf, [], cfg)
        assert score.normalisation_method == "absolute_anchor"
        assert score.history_size == 0
        assert 0.0 <= score.performance_score <= 100.0

    def test_score_with_history_uses_percentiles(self, cfg):
        history = [make_performance(f"c{i}", reach=5000 + i * 500) for i in range(10)]
        target = make_performance("target", reach=10_000, shares=500)
        score = compute_performance_score(target, history, cfg)
        assert score.normalisation_method == "percentile"
        assert score.history_size == 10

    def test_a_post_is_excluded_from_its_own_population(self, cfg):
        history = [make_performance("target", reach=999)] + [
            make_performance(f"c{i}") for i in range(8)
        ]
        target = make_performance("target", reach=10_000, shares=900)
        score = compute_performance_score(target, history, cfg)
        assert score.history_size == 8

    def test_better_post_scores_above_worse_post(self, cfg):
        history = [make_performance(f"c{i}", shares=50, saves=100) for i in range(10)]
        strong = make_performance("strong", shares=900, saves=900,
                                  new_followers=300, profile_visits=900)
        weak = make_performance("weak", shares=1, saves=1,
                                new_followers=0, profile_visits=1)
        assert (
            compute_performance_score(strong, history, cfg).performance_score
            > compute_performance_score(weak, history, cfg).performance_score
        )

    def test_every_component_is_preserved_for_later_analysis(self, cfg):
        score = compute_performance_score(make_performance("c1"), [], cfg)
        for component in cfg.performance_score.weights:
            assert component in score.component_values
            assert component in score.component_percentiles
