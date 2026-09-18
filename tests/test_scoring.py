"""Deterministic scoring: the arithmetic no LLM is allowed to touch."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from content_os.tools.scoring import (
    analyse_portfolio,
    apply_trend_decay,
    check_brand_fit_veto,
    compute_base_score,
    compute_effective_saturation,
    compute_saturation_penalty,
    score_topic,
)
from tests.conftest import make_rating, make_topic


class TestWeightedScore:
    def test_known_dimensions_produce_exact_weighted_total(self, cfg):
        # 10*0.30 + 10*0.20 + 10*0.15 + 10*0.15 + 10*0.10 + 10*0.10 = 10.0
        perfect = dict.fromkeys(
            ("brand_fit", "audience_fit", "trend_velocity",
             "originality", "visual_potential", "production_fit"), 10.0
        )
        assert compute_base_score(perfect, cfg) == pytest.approx(10.0)

    def test_hand_computed_mixed_score(self, cfg):
        ratings = {
            "brand_fit": 9.0,        # 0.30 -> 2.70
            "audience_fit": 8.0,     # 0.20 -> 1.60
            "trend_velocity": 6.0,   # 0.15 -> 0.90
            "originality": 7.0,      # 0.15 -> 1.05
            "visual_potential": 5.0, # 0.10 -> 0.50
            "production_fit": 10.0,  # 0.10 -> 1.00
        }
        assert compute_base_score(ratings, cfg) == pytest.approx(7.75)

    def test_brand_fit_dominates_as_the_heaviest_weight(self, cfg):
        high_brand = {"brand_fit": 10.0, "audience_fit": 0.0, "trend_velocity": 0.0,
                      "originality": 0.0, "visual_potential": 0.0, "production_fit": 0.0}
        high_visual = {"brand_fit": 0.0, "audience_fit": 0.0, "trend_velocity": 0.0,
                       "originality": 0.0, "visual_potential": 10.0, "production_fit": 0.0}
        assert compute_base_score(high_brand, cfg) > compute_base_score(high_visual, cfg)

    def test_out_of_range_ratings_are_clamped(self, cfg):
        absurd = dict.fromkeys(
            ("brand_fit", "audience_fit", "trend_velocity",
             "originality", "visual_potential", "production_fit"), 500.0
        )
        assert compute_base_score(absurd, cfg) == pytest.approx(10.0)

    def test_missing_dimension_scores_zero_rather_than_raising(self, cfg):
        assert compute_base_score({"brand_fit": 10.0}, cfg) == pytest.approx(3.0)


class TestSaturationPenalty:
    def test_higher_saturation_lowers_the_adjusted_score(self, cfg):
        low = score_topic(
            make_topic(canonical="low-sat"), make_rating(saturation=0.1), cfg,
            scoring_model="test", scoring_prompt_version="v1",
        )
        high = score_topic(
            make_topic(canonical="high-sat"), make_rating(saturation=0.95), cfg,
            scoring_model="test", scoring_prompt_version="v1",
        )
        assert low.base_score == high.base_score, "base score must be unaffected"
        assert high.adjusted_score < low.adjusted_score

    def test_penalty_is_monotonic_in_saturation(self, cfg):
        penalties = [
            compute_saturation_penalty(s, cfg) for s in (0.0, 0.25, 0.5, 0.75, 1.0)
        ]
        assert penalties == sorted(penalties)

    def test_penalty_is_bounded_by_config(self, cfg):
        assert compute_saturation_penalty(0.0, cfg) == 0.0
        assert compute_saturation_penalty(1.0, cfg) <= cfg.saturation.max_penalty
        assert compute_saturation_penalty(5.0, cfg) <= cfg.saturation.max_penalty

    def test_generic_framing_is_punished_hard(self, cfg):
        """'5 ChatGPT prompts you need' should collapse."""
        generic = score_topic(
            make_topic("5 ChatGPT prompts you need", canonical="generic"),
            make_rating(originality=2.0, saturation=0.97),
            cfg, scoring_model="test", scoring_prompt_version="v1",
        )
        assert generic.saturation_penalty > 0.4

    def test_ownable_topic_keeps_most_of_its_score(self, cfg):
        """'I built an AI clone of myself' touches a crowded theme but the
        firsthand build is unique, so originality relieves the penalty."""
        ownable = score_topic(
            make_topic("I built an AI clone of myself", canonical="ownable"),
            make_rating(originality=9.5, saturation=0.55),
            cfg, scoring_model="test", scoring_prompt_version="v1",
        )
        generic = score_topic(
            make_topic("Top 10 AI tools", canonical="generic2"),
            make_rating(originality=2.0, saturation=0.55),
            cfg, scoring_model="test", scoring_prompt_version="v1",
        )
        assert ownable.effective_saturation < generic.effective_saturation
        assert ownable.saturation_penalty < generic.saturation_penalty

    def test_originality_relief_cannot_go_negative(self, cfg):
        assert compute_effective_saturation(0.05, 10.0, cfg) >= 0.0

    def test_raw_dimensions_are_never_overwritten(self, cfg):
        rating = make_rating(trend_velocity=9.0, saturation=0.9)
        topic = make_topic(
            event_date=datetime.now(timezone.utc) - timedelta(hours=200),
            canonical="raw-preserved",
        )
        score = score_topic(
            topic, rating, cfg, scoring_model="test", scoring_prompt_version="v1"
        )
        assert score.trend_velocity == 9.0, "raw rating must survive"
        assert score.decayed_trend_velocity < 9.0, "decayed value stored separately"
        assert score.saturation == pytest.approx(0.9)


class TestTrendDecay:
    def test_velocity_halves_at_the_half_life(self, cfg):
        decayed = apply_trend_decay(10.0, cfg.trend_decay.half_life_hours, cfg)
        assert decayed == pytest.approx(5.0, abs=0.01)

    def test_decay_is_monotonic_with_age(self, cfg):
        values = [apply_trend_decay(10.0, h, cfg) for h in (0, 24, 72, 168, 500)]
        assert values == sorted(values, reverse=True)

    def test_decay_respects_the_floor(self, cfg):
        ancient = apply_trend_decay(10.0, 100_000, cfg)
        assert ancient == pytest.approx(10.0 * cfg.trend_decay.floor_fraction)

    def test_fresh_topic_is_not_decayed(self, cfg):
        assert apply_trend_decay(8.0, 0.0, cfg) == 8.0

    def test_stale_topic_ranks_below_identical_fresh_topic(self, cfg):
        rating = make_rating(trend_velocity=10.0)
        fresh = score_topic(
            make_topic(event_date=datetime.now(timezone.utc), canonical="fresh"),
            rating, cfg, scoring_model="t", scoring_prompt_version="v1",
        )
        stale = score_topic(
            make_topic(
                event_date=datetime.now(timezone.utc) - timedelta(days=14),
                canonical="stale",
            ),
            rating, cfg, scoring_model="t", scoring_prompt_version="v1",
        )
        assert stale.adjusted_score < fresh.adjusted_score


class TestBrandFitVeto:
    def test_veto_fires_below_threshold(self, cfg):
        vetoed, flag = check_brand_fit_veto(cfg.brand_fit_veto.threshold - 0.1, cfg)
        assert vetoed is True
        assert flag == "TRENDING_BUT_OFF_BRAND"

    def test_no_veto_at_or_above_threshold(self, cfg):
        assert check_brand_fit_veto(cfg.brand_fit_veto.threshold, cfg) == (False, None)

    def test_maximum_trend_velocity_cannot_override_the_veto(self, cfg):
        """The rule that stops the account becoming an AI-news aggregator."""
        score = score_topic(
            make_topic("Huge AI funding round", canonical="offbrand"),
            make_rating(brand_fit=2.0, audience_fit=10.0, trend_velocity=10.0,
                        originality=10.0, visual_potential=10.0, production_fit=10.0),
            cfg, scoring_model="t", scoring_prompt_version="v1",
        )
        assert score.vetoed is True
        assert score.veto_flag == "TRENDING_BUT_OFF_BRAND"
        assert score.adjusted_score > 5.0, "still scored, just not recommendable"

    def test_vetoed_topics_are_excluded_from_the_candidate_pool(self, repos, cfg):
        for title, brand_fit in (("On brand", 9.0), ("Off brand", 2.0)):
            topic = make_topic(title, canonical=title)
            repos.topics.upsert(topic)
            repos.scores.insert(
                score_topic(topic, make_rating(brand_fit=brand_fit), cfg,
                            scoring_model="t", scoring_prompt_version="v1")
            )

        usable = repos.scores.ranked(include_vetoed=False)
        assert [s.topic.title for s in usable] == ["On brand"]

        everything = repos.scores.ranked(include_vetoed=True)
        assert len(everything) == 2, "vetoed topics are still stored and visible"
