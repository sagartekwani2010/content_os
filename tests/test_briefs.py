"""The human-led production path.

The guarantee under test: agents improve execution and never change strategy.
"""

from __future__ import annotations

import pytest

from content_os.models.brief import (
    IMMUTABLE_FIELDS,
    BriefStatus,
    ContentBrief,
    ExecutionPlan,
    HookSet,
    HookVariant,
)
from content_os.tools.brief_loader import BriefError, load_brief_file, parse_brief


def make_plan(brief: ContentBrief, **overrides) -> ExecutionPlan:
    base = dict(
        brief_id=brief.brief_id,
        format=brief.content_format,
        narrative_arc=["open", "explain", "land"],
        opening_strategy="Lead with the claim.",
        key_learning_points=["point"],
        supporting_examples=["example"],
        visual_beats=["diagram"],
        closing_strategy="Reframe.",
        section_coverage_plan=[f"{s}: covered" for s in brief.high_level_sections],
        risks_or_gaps=[],
        factual_items_to_verify=[],
        alternate_format_recommendation=None,
        alternate_format_reason=None,
    )
    base.update(overrides)
    return ExecutionPlan(**base)


class TestBriefLoading:
    def test_example_brief_loads(self):
        briefs = load_brief_file("briefs/example_production_ai.yaml")
        assert len(briefs) == 1
        brief = briefs[0]
        assert brief.content_format == "carousel"
        assert len(brief.high_level_sections) == 10

    def test_block_scalars_are_collapsed(self):
        brief = load_brief_file("briefs/example_production_ai.yaml")[0]
        assert "\n" not in brief.core_thesis

    def test_missing_required_field_is_rejected(self):
        with pytest.raises(BriefError, match="missing required fields"):
            parse_brief({"topic": "x", "content_format": "reel"})

    def test_unknown_pillar_is_rejected(self):
        with pytest.raises(BriefError, match="Unknown brand_pillar"):
            parse_brief({
                "topic": "x", "core_thesis": "t", "learning_objective": "l",
                "content_format": "reel", "brand_pillar": "crypto",
                "hook_direction": "h",
            })

    def test_field_aliases_are_accepted(self):
        brief = parse_brief({
            "topic": "x", "core_thesis": "t", "learning_objective": "l",
            "format": "reel", "pillar": "ai_builder", "hook_direction": "h",
            "sections": ["a", "b"], "hook_points": ["p"], "slides": 7,
        })
        assert brief.content_format == "reel"
        assert brief.brand_pillar == "ai_builder"
        assert brief.high_level_sections == ["a", "b"]

    def test_briefs_import_as_draft_not_approved(self):
        """Importing is not approving. Production reads APPROVED only."""
        brief = load_brief_file("briefs/example_production_ai.yaml")[0]
        assert brief.status == BriefStatus.DRAFT

    def test_string_where_a_list_is_expected_is_tolerated(self):
        brief = parse_brief({
            "topic": "x", "core_thesis": "t", "learning_objective": "l",
            "content_format": "reel", "brand_pillar": "ai_builder",
            "hook_direction": "h", "high_level_sections": "only one",
        })
        assert brief.high_level_sections == ["only one"]


class TestBriefAuthority:
    def test_immutable_fields_are_declared(self):
        for field in IMMUTABLE_FIELDS:
            assert field in ContentBrief.model_fields

    def test_fingerprint_captures_every_immutable_field(self, sample_brief):
        fingerprint = sample_brief.fingerprint()
        assert set(fingerprint) == set(IMMUTABLE_FIELDS)

    def test_prompt_context_marks_fields_as_unchangeable(self, sample_brief):
        context = sample_brief.as_prompt_context()
        assert "do not alter" in context.lower()
        assert "do not change" in context.lower()
        assert sample_brief.core_thesis in context
        assert sample_brief.learning_objective in context

    def test_every_mandatory_section_reaches_the_prompt(self, sample_brief):
        context = sample_brief.as_prompt_context()
        for section in sample_brief.high_level_sections:
            assert section in context

    def test_approved_hook_points_reach_the_prompt(self, sample_brief):
        context = sample_brief.as_prompt_context()
        for point in sample_brief.approved_hook_points:
            assert point in context


class TestPlanVerification:
    def test_format_change_is_detected(self, sample_brief):
        from content_os.agents.brief_strategist import verify_plan

        plan = make_plan(sample_brief, format="reel")
        problems = verify_plan(plan, sample_brief)
        assert any(p.startswith("FORMAT_CHANGED") for p in problems)

    def test_dropped_section_is_detected(self, sample_brief):
        from content_os.agents.brief_strategist import verify_plan

        plan = make_plan(sample_brief, section_coverage_plan=["demo architecture only"])
        problems = verify_plan(plan, sample_brief)
        assert any(p.startswith("SECTION_NOT_PLANNED") for p in problems)

    def test_complete_plan_has_no_problems(self, sample_brief):
        from content_os.agents.brief_strategist import verify_plan

        assert verify_plan(make_plan(sample_brief), sample_brief) == []

    def test_reworded_section_still_counts_as_planned(self, sample_brief):
        from content_os.agents.brief_strategist import verify_plan

        plan = make_plan(
            sample_brief,
            section_coverage_plan=[
                f"Slide covering {s.upper()}" for s in sample_brief.high_level_sections
            ],
        )
        assert verify_plan(plan, sample_brief) == []


class TestHookScope:
    def _hook_set(self, brief, **overrides):
        base = dict(
            brief_id=brief.brief_id,
            recommended_variant_id="h1",
            variants=[
                HookVariant(
                    variant_id="h1", text="The model is the easy part.",
                    hook_strategy="contrarian",
                    derived_from_point=brief.approved_hook_points[0],
                    rationale="Direct contradiction.",
                )
            ],
            out_of_scope_ideas=[],
        )
        base.update(overrides)
        return HookSet(**base)

    def test_untraceable_hook_is_flagged(self, sample_brief):
        from content_os.agents.hook_expander import verify_hooks

        hook_set = self._hook_set(
            sample_brief,
            variants=[HookVariant(
                variant_id="h1", text="Unrelated clickbait",
                hook_strategy="curiosity", derived_from_point="",
                rationale="",
            )],
        )
        problems = verify_hooks(hook_set, sample_brief)
        assert any(p.startswith("UNTRACEABLE_HOOK") for p in problems)

    def test_unknown_strategy_is_flagged(self, sample_brief):
        from content_os.agents.hook_expander import verify_hooks

        hook_set = self._hook_set(
            sample_brief,
            variants=[HookVariant(
                variant_id="h1", text="x", hook_strategy="vibes",
                derived_from_point="p", rationale="r",
            )],
        )
        assert any(
            p.startswith("UNKNOWN_STRATEGY")
            for p in verify_hooks(hook_set, sample_brief)
        )

    def test_recommended_must_exist_in_the_set(self, sample_brief):
        from content_os.agents.hook_expander import verify_hooks

        hook_set = self._hook_set(sample_brief, recommended_variant_id="h9")
        assert any(
            p.startswith("RECOMMENDED_NOT_IN_SET")
            for p in verify_hooks(hook_set, sample_brief)
        )

    def test_valid_set_passes(self, sample_brief):
        from content_os.agents.hook_expander import verify_hooks

        assert verify_hooks(self._hook_set(sample_brief), sample_brief) == []

    def test_selection_returns_the_recommended_variant(self, sample_brief):
        from content_os.agents.hook_expander import select

        text, strategy, variant_id = select(self._hook_set(sample_brief))
        assert variant_id == "h1"
        assert strategy == "contrarian"
        assert text


class TestBacklogGating:
    def test_only_approved_briefs_are_returned_for_production(self, repos, sample_brief):
        for status in (
            BriefStatus.DRAFT, BriefStatus.HUMAN_REVIEW, BriefStatus.REJECTED,
        ):
            brief = sample_brief.model_copy(
                update={"brief_id": f"b_{status.value}", "status": status}
            )
            repos.briefs.upsert(brief)
        repos.briefs.upsert(
            sample_brief.model_copy(
                update={"brief_id": "b_ok", "status": BriefStatus.APPROVED}
            )
        )

        approved = repos.briefs.approved()
        assert [b.brief_id for b in approved] == ["b_ok"]

    def test_approval_records_a_named_human_and_a_time(self, repos, sample_brief):
        brief = sample_brief.model_copy(update={"status": BriefStatus.DRAFT})
        repos.briefs.upsert(brief)
        assert repos.briefs.approve(brief.brief_id, "sagar") is True

        stored = repos.briefs.get(brief.brief_id)
        assert stored.status == BriefStatus.APPROVED
        assert stored.approved_by == "sagar"
        assert stored.approved_at is not None

    def test_brief_round_trips_through_storage(self, repos, sample_brief):
        repos.briefs.upsert(sample_brief)
        stored = repos.briefs.get(sample_brief.brief_id)
        assert stored.fingerprint() == sample_brief.fingerprint()
        assert stored.approved_hook_points == sample_brief.approved_hook_points

    def test_backlog_view_exposes_workflow_columns(self, repos, sample_brief):
        repos.briefs.upsert(sample_brief)
        row = repos.briefs.backlog()[0]
        for field in ("brief_id", "topic", "content_format", "brand_pillar",
                      "status", "priority", "urgency", "scheduled_date",
                      "created_at", "approved_at", "published_at"):
            assert field in row

    def test_priority_orders_the_production_queue(self, repos, sample_brief):
        for priority, brief_id in ((3, "low"), (1, "high"), (2, "mid")):
            repos.briefs.upsert(sample_brief.model_copy(update={
                "brief_id": brief_id, "priority": priority,
                "status": BriefStatus.APPROVED,
            }))
        assert [b.brief_id for b in repos.briefs.approved()] == ["high", "mid", "low"]


class TestStrategyPersistence:
    def test_strategy_fields_survive_onto_the_content_record(self, repos, sample_brief):
        """These columns are what let us later ask which learning objectives
        drove saves, rather than only which copy performed."""
        from content_os.models.content import ContentItem, ContentStatus
        from content_os.workflows.produce import _topic_for_brief
        from content_os.ids import new_id
        from content_os.storage.db import utcnow

        # Brief-driven content still gets a topic row so it stays visible to
        # the analytics layer, which joins content through topics.
        topic_id = _topic_for_brief(repos, sample_brief)
        now = utcnow()
        item = ContentItem(
            id=new_id("content"), topic_id=topic_id,
            format="carousel", pillar=sample_brief.brand_pillar,
            strategic_role="authority", title="t", hook="h", body_json="{}",
            caption="c", status=ContentStatus.GENERATED,
            brief_id=sample_brief.brief_id,
            core_thesis=sample_brief.core_thesis,
            learning_objective=sample_brief.learning_objective,
            hook_direction=sample_brief.hook_direction,
            approved_hook_points=sample_brief.approved_hook_points,
            high_level_sections=sample_brief.high_level_sections,
            hook_strategy="contrarian", hook_source="agent_expanded",
            hook_variant_id="h1", learning_payoff="They can audit a prototype.",
            save_reason="reference", share_reason="settles an argument",
            created_at=now, updated_at=now,
        )
        content_id = repos.content.insert_with_strategy(
            item, sample_brief.high_level_sections
        )

        row = repos.content.get(content_id)
        assert row["brief_id"] == sample_brief.brief_id
        assert row["core_thesis"] == sample_brief.core_thesis
        assert row["learning_objective"] == sample_brief.learning_objective
        assert row["hook_strategy"] == "contrarian"
        assert row["hook_variant_id"] == "h1"
        assert row["learning_payoff"]

    def test_human_and_agent_hooks_are_both_stored(self, repos, sample_brief):
        """Correlating hook strategy with performance needs the losers too."""
        repos.briefs.upsert(sample_brief)
        hook_set = HookSet(
            brief_id=sample_brief.brief_id,
            recommended_variant_id="h1",
            variants=[
                HookVariant(variant_id="h1", text="A", hook_strategy="contrarian",
                            derived_from_point="p", rationale="r"),
                HookVariant(variant_id="h2", text="B", hook_strategy="comparison",
                            derived_from_point="p", rationale="r"),
            ],
            out_of_scope_ideas=[],
        )
        repos.hooks.record_set(
            hook_set, brief=sample_brief, content_id=None,
            model="m", prompt_version="hook_expander_v1",
        )

        rows = repos.hooks.for_brief(sample_brief.brief_id)
        sources = {r["hook_source"] for r in rows}
        assert sources == {"human", "agent_expanded"}
        assert len(rows) == len(sample_brief.approved_hook_points) + 2

        selected = repos.hooks.selected(sample_brief.brief_id)
        assert selected["variant_id"] == "h1"


class TestBriefTopicLinkage:
    def test_brief_gets_a_topic_row_so_analytics_still_sees_it(
        self, repos, sample_brief
    ):
        """Content arrives from discovery or from a brief. Both must appear in
        historical reporting, which joins through topics."""
        from content_os.workflows.produce import _topic_for_brief

        topic_id = _topic_for_brief(repos, sample_brief)
        topic = repos.topics.get(topic_id)
        assert topic is not None
        assert topic.title == sample_brief.topic
        assert topic.source_types == ["content_brief"]

    def test_producing_the_same_brief_twice_reuses_one_topic(
        self, repos, sample_brief
    ):
        from content_os.workflows.produce import _topic_for_brief

        first = _topic_for_brief(repos, sample_brief)
        second = _topic_for_brief(repos, sample_brief)
        assert first == second, "canonical dedup should prevent duplicate topics"
