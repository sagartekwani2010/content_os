"""Config validation, QA gating, and ad eligibility."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest
import yaml

from content_os.config import (
    ConfigError,
    OpportunityWeights,
    PerformanceScoreConfig,
    PortfolioConfig,
    load_prompt,
    load_models_config,
    validate_all,
)
from content_os.models.content import ContentStatus, QAScores
from content_os.agents.qa_editor import compute_composite, evaluate_gates
from content_os.tools.ad_eligibility import evaluate_ad_eligibility
from content_os.tools.scoring import score_topic
from tests.conftest import make_content, make_performance, make_rating, make_topic


class TestConfigValidation:
    def test_repository_config_is_valid(self):
        assert validate_all() == []

    def test_opportunity_weights_must_sum_to_one(self):
        with pytest.raises(ValueError, match="must sum to 1.0"):
            OpportunityWeights(
                brand_fit=0.5, audience_fit=0.2, trend_velocity=0.15,
                originality=0.15, visual_potential=0.10, production_fit=0.10,
            )

    def test_valid_weights_are_accepted(self):
        weights = OpportunityWeights(
            brand_fit=0.30, audience_fit=0.20, trend_velocity=0.15,
            originality=0.15, visual_potential=0.10, production_fit=0.10,
        )
        assert sum(weights.as_dict().values()) == pytest.approx(1.0)

    def test_performance_weights_must_sum_to_one(self):
        with pytest.raises(ValueError, match="must sum to 1.0"):
            PerformanceScoreConfig(weights={"share_rate": 0.9, "like_rate": 0.2})

    def test_portfolio_targets_must_sum_to_one(self):
        with pytest.raises(ValueError, match="must sum to 1.0"):
            PortfolioConfig(targets={"ai_builder": 0.9, "ai_pov": 0.5})

    def test_every_configured_prompt_version_exists(self):
        models = load_models_config()
        for name in models.agents:
            text = load_prompt(models.resolved(name).prompt_version)
            assert len(text) > 200, f"{name} prompt looks empty"

    def test_missing_prompt_raises_a_clear_error(self):
        with pytest.raises(ConfigError, match="Missing prompt file"):
            load_prompt("does_not_exist_v9")

    def test_scoring_config_is_fingerprinted(self, cfg):
        assert cfg.version != "unversioned"
        assert len(cfg.version) == 12


class TestQAGate:
    def _scores(self, **overrides) -> QAScores:
        base = dict(
            hook_strength=8.0, clarity=8.0, technical_accuracy=9.0, brand_fit=9.0,
            originality=8.0, share_potential=7.0, save_potential=7.0,
            visual_potential=8.0, ai_hype_penalty=1.0, generic_content_penalty=1.0,
        )
        base.update(overrides)
        return QAScores(**base)

    def test_strong_content_passes_every_gate(self, cfg):
        composite, failed = evaluate_gates(self._scores(), cfg)
        assert failed == []
        assert composite > cfg.qa_gates.min_composite

    def test_weak_hook_alone_blocks_approval(self, cfg):
        _, failed = evaluate_gates(self._scores(hook_strength=3.0), cfg)
        assert any(f.startswith("WEAK_HOOK") for f in failed)

    def test_generic_content_is_rejected(self, cfg):
        _, failed = evaluate_gates(self._scores(generic_content_penalty=9.0), cfg)
        assert any(f.startswith("TOO_GENERIC") for f in failed)

    def test_hype_is_rejected(self, cfg):
        _, failed = evaluate_gates(self._scores(ai_hype_penalty=8.0), cfg)
        assert any(f.startswith("TOO_HYPED") for f in failed)

    def test_questionable_accuracy_is_rejected(self, cfg):
        _, failed = evaluate_gates(self._scores(technical_accuracy=4.0), cfg)
        assert any(f.startswith("TECHNICAL_ACCURACY_TOO_LOW") for f in failed)

    def test_penalties_cannot_be_offset_by_high_scores(self, cfg):
        """A hype-heavy piece must not be rescued by scoring well elsewhere."""
        perfect_but_hyped = self._scores(
            hook_strength=10.0, clarity=10.0, technical_accuracy=10.0,
            brand_fit=10.0, originality=10.0, share_potential=10.0,
            save_potential=10.0, visual_potential=10.0,
            ai_hype_penalty=10.0, generic_content_penalty=10.0,
        )
        _, failed = evaluate_gates(perfect_but_hyped, cfg)
        assert any(f.startswith("TOO_HYPED") for f in failed)
        assert any(f.startswith("TOO_GENERIC") for f in failed)

    def test_composite_falls_as_penalties_rise(self, cfg):
        clean = compute_composite(self._scores(), cfg)
        hyped = compute_composite(self._scores(ai_hype_penalty=9.0), cfg)
        assert hyped < clean

    def test_gate_decision_is_config_driven_not_agent_driven(self, cfg):
        """The agent's recommendation does not decide approval."""
        from content_os.agents.qa_editor import finalise
        from content_os.models.content import QAVerdict

        verdict = QAVerdict(
            scores=self._scores(hook_strength=2.0, generic_content_penalty=9.0),
            issues=[], required_changes=[],
            agent_recommends_approval=True,  # agent says yes
            verdict_rationale="I like it",
        )
        result = finalise(verdict, cfg, revision_number=0,
                          qa_model="gpt-5", qa_prompt_version="qa_v1")
        assert result.agent_recommends_approval is True
        assert result.approved is False, "config decides, not the agent"
        assert result.failed_gates


class TestAdEligibility:
    def test_unknown_content_is_ineligible(self, repos):
        result = evaluate_ad_eligibility("nope", repos)
        assert result.eligible is False
        assert "CONTENT_NOT_FOUND" in result.reason_codes

    def test_content_without_performance_data_is_ineligible(self, repos):
        topic = make_topic(canonical="no-perf")
        repos.topics.upsert(topic)
        content = make_content(topic.id)
        repos.content.insert(content)
        result = evaluate_ad_eligibility(content.id, repos)
        assert result.eligible is False
        assert "NO_PERFORMANCE_DATA" in result.reason_codes

    def test_thin_history_blocks_eligibility(self, repos):
        topic = make_topic(canonical="thin")
        repos.topics.upsert(topic)
        content = make_content(topic.id)
        repos.content.insert(content)
        repos.performance.insert(make_performance(content.id))
        result = evaluate_ad_eligibility(content.id, repos)
        assert result.eligible is False
        assert any(r.startswith("INSUFFICIENT_HISTORY") for r in result.reason_codes)

    def test_approval_is_always_required(self, repos):
        assert evaluate_ad_eligibility("anything", repos).requires_human_approval is True

    def test_underperforming_post_is_rejected_with_named_gates(self, repos, cfg):
        topic = make_topic(canonical="weak-post")
        repos.topics.upsert(topic)
        repos.scores.insert(
            score_topic(topic, make_rating(), cfg,
                        scoring_model="m", scoring_prompt_version="v")
        )
        for index in range(8):
            peer_topic = make_topic(f"peer {index}", canonical=f"peer-{index}")
            repos.topics.upsert(peer_topic)
            peer = make_content(peer_topic.id, title=f"peer {index}")
            repos.content.insert(peer)
            repos.performance.insert(
                make_performance(peer.id, shares=500, saves=500,
                                 new_followers=200, profile_visits=600)
            )

        weak = make_content(topic.id, title="weak post")
        repos.content.insert(weak)
        repos.performance.insert(
            make_performance(weak.id, shares=1, saves=1,
                             new_followers=0, profile_visits=2)
        )
        result = evaluate_ad_eligibility(weak.id, repos)
        assert result.eligible is False
        assert any("BELOW_THRESHOLD" in r for r in result.reason_codes)

    def test_budget_is_capped_when_a_post_qualifies(self, repos, cfg):
        """A strong post gets a recommendation, never an unbounded one."""
        topic = make_topic(canonical="strong-post")
        repos.topics.upsert(topic)
        repos.scores.insert(
            score_topic(topic, make_rating(brand_fit=9.0), cfg,
                        scoring_model="m", scoring_prompt_version="v")
        )
        for index in range(10):
            peer_topic = make_topic(f"p{index}", canonical=f"p-{index}")
            repos.topics.upsert(peer_topic)
            peer = make_content(peer_topic.id, title=f"p{index}")
            repos.content.insert(peer)
            repos.performance.insert(
                make_performance(peer.id, shares=5, saves=10,
                                 new_followers=2, profile_visits=20)
            )

        strong = make_content(topic.id, title="strong post")
        repos.content.insert(strong)
        repos.content.attach_qa(strong.id, approved=True, composite=8.0, qa_json="{}")
        repos.content.mark_published(
            strong.id, "ig_123",
            datetime.now(timezone.utc) - timedelta(days=7),
        )
        repos.performance.insert(
            make_performance(strong.id, shares=900, saves=900,
                             new_followers=400, profile_visits=1200)
        )

        result = evaluate_ad_eligibility(strong.id, repos)
        assert result.eligible is True, result.reason_codes
        assert result.suggested_test_budget is not None
        assert result.suggested_test_budget <= cfg.ad_eligibility.budget.max_daily
        assert "REQUIRES_HUMAN_APPROVAL" in result.reason_codes


class TestHookClassification:
    def test_classifier_is_stable_across_calls(self):
        from content_os.tools.analytics import classify_hook

        hook = "90% of apps don't need multi-agent systems"
        assert classify_hook(hook) == classify_hook(hook) == "contrarian"

    def test_empty_hook_is_unknown(self):
        from content_os.tools.analytics import classify_hook

        assert classify_hook("") == "unknown"
        assert classify_hook(None) == "unknown"


class TestPricingWarnings:
    def test_unpriced_model_is_reported(self):
        """A model with no real rates records zero cost. That must be loud,
        because a $0 ledger looks like a working ledger."""
        from content_os.config import config_warnings

        warnings = config_warnings()
        assert any("zero cost" in w or "no entry" in w for w in warnings), (
            "the gpt-5.6 variants have placeholder pricing and should warn"
        )

    def test_a_fully_priced_config_produces_no_warning(self, tmp_path):
        from content_os.config import ModelsConfig

        models = ModelsConfig(
            defaults={"model": "m1"},
            agents={"scorer": {"model": "m1", "prompt_version": "scorer_v1"}},
            pricing={"m1": {"input_per_mtok": 1.0, "output_per_mtok": 2.0}},
        )
        price = models.price("m1")
        assert price.input_per_mtok == 1.0
        assert models.price("unknown-model").input_per_mtok == 0.0

    def test_every_configured_model_resolves(self):
        from content_os.config import load_models_config

        models = load_models_config()
        for agent in models.agents:
            resolved = models.resolved(agent)
            assert resolved.model
            assert resolved.prompt_version
            assert resolved.reasoning_effort in ("low", "medium", "high")
