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
            PortfolioConfig(targets={"ai_builder": 0.9, "ai_career": 0.5})

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
            visual_potential=8.0, learning_value=8.5,
            execution_against_brief=9.0,
            ai_hype_penalty=1.0, generic_content_penalty=1.0,
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
            learning_value=10.0, execution_against_brief=10.0,
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
            sections_covered=[], sections_missing=[],
            thesis_drift=False, thesis_drift_explanation=None,
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
    def test_repository_config_is_fully_priced(self):
        """Every model in use has real rates, so no warning should fire."""
        from content_os.config import config_warnings

        assert config_warnings() == []

    def test_unpriced_model_is_reported(self):
        """A model with no real rates records zero cost. That must be loud,
        because a $0 ledger looks exactly like a working ledger."""
        from content_os.config import ModelsConfig

        models = ModelsConfig(
            agents={"scorer": {"model": "unpriced-m", "prompt_version": "scorer_v1"}},
            pricing={},
        )
        assert models.price("unpriced-m").is_priced is False
        cost = models.compute_cost("unpriced-m", input_tokens=1000, output_tokens=500)
        assert cost.total_cost == 0.0
        assert cost.priced is False

    def test_every_configured_model_resolves(self):
        from content_os.config import load_models_config

        models = load_models_config()
        for agent in models.agents:
            resolved = models.resolved(agent)
            assert resolved.model
            assert resolved.prompt_version
            assert resolved.reasoning_effort in ("low", "medium", "high")


class TestBrandContextCompleteness:
    """Brand config that never reaches a prompt is config that does nothing.

    signature_series shipped declared-but-unused, which is exactly the failure
    these assertions exist to catch.
    """

    def test_signature_series_reaches_the_prompt(self, brand):
        context = brand.as_prompt_context()
        assert brand.signature_series, "brand.yaml should declare series"
        for series in brand.signature_series:
            assert series.name in context, f"series '{series.name}' never reaches agents"

    def test_identity_themes_reach_the_prompt(self, brand):
        context = brand.as_prompt_context()
        assert brand.identity_themes
        for theme in brand.identity_themes:
            assert theme[:40] in context

    def test_signature_opinions_reach_the_prompt(self, brand):
        context = brand.as_prompt_context()
        for opinion in brand.signature_opinions:
            assert opinion in context

    def test_avoided_topics_reach_the_prompt(self, brand):
        context = brand.as_prompt_context()
        for topic in brand.avoided_topics:
            assert topic in context

    def test_communication_principles_reach_the_prompt(self, brand):
        context = brand.as_prompt_context()
        assert brand.communication_principles
        for principle in brand.communication_principles:
            assert principle[:40] in context

    def test_content_learning_memory_reaches_the_prompt(self, brand):
        context = brand.as_prompt_context()
        assert brand.content_learning_memory
        for learning in brand.content_learning_memory:
            assert learning.rule[:40] in context
            assert learning.source in context

    def test_every_declared_list_field_is_surfaced(self, brand):
        """Guard against adding a field to brand.yaml and forgetting to render it."""
        context = brand.as_prompt_context()
        for field in (
            "target_audiences", "preferred_topics", "avoided_topics",
            "signature_opinions", "winning_hook_patterns", "losing_hook_patterns",
            "identity_themes", "communication_principles",
        ):
            values = getattr(brand, field)
            if values:
                assert str(values[0])[:30] in context, f"{field} not rendered"


class TestPromptVersioning:
    def test_changed_prompts_became_new_versions(self):
        """Editing a prompt in place would silently rewrite the meaning of every
        historical row pointing at that version."""
        from pathlib import Path

        for stem in ("trend_scout", "scorer", "strategist", "reel_writer",
                     "carousel_writer"):
            assert Path(f"prompts/{stem}_v1.md").exists(), f"{stem} v1 must survive"
            assert Path(f"prompts/{stem}_v2.md").exists(), f"{stem} v2 must exist"

    def test_v2_prompts_differ_from_v1(self):
        from pathlib import Path

        for stem in ("trend_scout", "scorer", "strategist"):
            v1 = Path(f"prompts/{stem}_v1.md").read_text()
            v2 = Path(f"prompts/{stem}_v2.md").read_text()
            assert v1 != v2
            assert len(v2) > len(v1), f"{stem}_v2 should add guidance"

    def test_config_points_at_the_new_versions(self):
        from content_os.config import load_models_config

        models = load_models_config()
        assert models.resolved("strategist").prompt_version == "strategist_v2"
        assert models.resolved("scorer").prompt_version == "scorer_v2"
        assert models.resolved("brand_miner").prompt_version == "brand_miner_v1"


class TestBriefGates:
    """Learning value and brief execution are hard gates, not contributions."""

    def _scores(self, **overrides):
        from content_os.models.content import QAScores

        base = dict(
            hook_strength=9.0, clarity=9.0, technical_accuracy=9.0, brand_fit=9.0,
            originality=9.0, share_potential=9.0, save_potential=9.0,
            visual_potential=9.0, learning_value=9.0, execution_against_brief=9.0,
            ai_hype_penalty=0.0, generic_content_penalty=0.0,
        )
        base.update(overrides)
        return QAScores(**base)

    def test_weak_learning_value_rejects_otherwise_perfect_content(self, cfg):
        """Content that teaches nothing fails however good it is."""
        from content_os.agents.qa_editor import evaluate_gates

        _, failed = evaluate_gates(self._scores(learning_value=3.0), cfg)
        assert any(f.startswith("LEARNING_VALUE_TOO_LOW") for f in failed)

    def test_poor_brief_execution_rejects_otherwise_perfect_content(self, cfg):
        from content_os.agents.qa_editor import evaluate_gates

        _, failed = evaluate_gates(self._scores(execution_against_brief=4.0), cfg)
        assert any(f.startswith("POOR_BRIEF_EXECUTION") for f in failed)

    def test_missing_mandatory_section_is_a_rejection(self, cfg, sample_brief):
        """A missing section is binary. It cannot be averaged away."""
        from content_os.agents.qa_editor import finalise
        from content_os.models.content import QAVerdict

        verdict = QAVerdict(
            scores=self._scores(),
            issues=[], required_changes=[],
            agent_recommends_approval=True,
            verdict_rationale="looks good",
            sections_covered=[sample_brief.high_level_sections[0]],
            sections_missing=[],
            thesis_drift=False, thesis_drift_explanation=None,
        )
        result = finalise(
            verdict, cfg, revision_number=0, qa_model="m",
            qa_prompt_version="qa_v2", brief=sample_brief,
        )
        assert result.approved is False
        assert any(f.startswith("SECTIONS_MISSING") for f in result.failed_gates)
        assert len(result.sections_missing) == len(sample_brief.high_level_sections) - 1

    def test_full_coverage_passes(self, cfg, sample_brief):
        from content_os.agents.qa_editor import finalise
        from content_os.models.content import QAVerdict

        verdict = QAVerdict(
            scores=self._scores(),
            issues=[], required_changes=[],
            agent_recommends_approval=True,
            verdict_rationale="complete",
            sections_covered=list(sample_brief.high_level_sections),
            sections_missing=[],
            thesis_drift=False, thesis_drift_explanation=None,
        )
        result = finalise(
            verdict, cfg, revision_number=0, qa_model="m",
            qa_prompt_version="qa_v2", brief=sample_brief,
        )
        assert result.approved is True, result.failed_gates

    def test_thesis_drift_is_a_rejection(self, cfg, sample_brief):
        """Drift is not improvement. The human decided the argument."""
        from content_os.agents.qa_editor import finalise
        from content_os.models.content import QAVerdict

        verdict = QAVerdict(
            scores=self._scores(),
            issues=[], required_changes=[],
            agent_recommends_approval=True,
            verdict_rationale="better argument honestly",
            sections_covered=list(sample_brief.high_level_sections),
            sections_missing=[],
            thesis_drift=True,
            thesis_drift_explanation="Argued the opposite conclusion.",
        )
        result = finalise(
            verdict, cfg, revision_number=0, qa_model="m",
            qa_prompt_version="qa_v2", brief=sample_brief,
        )
        assert result.approved is False
        assert "THESIS_DRIFT" in result.failed_gates

    def test_reworded_section_still_counts_as_covered(self, cfg, sample_brief):
        """The writer may reword. Coverage matching is on distinctive words."""
        from content_os.agents.qa_editor import finalise
        from content_os.models.content import QAVerdict

        reworded = [f"{s} (expanded)" for s in sample_brief.high_level_sections]
        verdict = QAVerdict(
            scores=self._scores(),
            issues=[], required_changes=[],
            agent_recommends_approval=True,
            verdict_rationale="covered with different wording",
            sections_covered=reworded, sections_missing=[],
            thesis_drift=False, thesis_drift_explanation=None,
        )
        result = finalise(
            verdict, cfg, revision_number=0, qa_model="m",
            qa_prompt_version="qa_v2", brief=sample_brief,
        )
        assert result.sections_missing == []


class TestQAWeightValidation:
    def test_composite_weights_must_sum_to_one(self):
        from content_os.config import QAGatesConfig

        with pytest.raises(ValueError, match="must sum to 1.0"):
            QAGatesConfig(composite_weights={"hook_strength": 0.5, "clarity": 0.9})

    def test_unknown_score_field_is_rejected(self):
        """A typo would silently contribute zero and lower every composite."""
        from content_os.config import QAGatesConfig

        with pytest.raises(ValueError, match="unknown score fields"):
            QAGatesConfig(composite_weights={"hook_strenght": 1.0})

    def test_repository_weights_are_valid(self, cfg):
        assert sum(cfg.qa_gates.composite_weights.values()) == pytest.approx(1.0)
