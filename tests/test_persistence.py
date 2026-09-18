"""Persistence guarantees.

These tests defend the property the whole system rests on: history survives.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from content_os.ids import new_id
from content_os.models.content import ContentStatus, CreativeVariant, QAResult
from content_os.models.topics import TopicStatus
from content_os.storage.db import utcnow
from content_os.tools.scoring import score_topic
from tests.conftest import make_content, make_performance, make_rating, make_topic


class TestTopicDeduplication:
    def test_same_canonical_topic_is_not_duplicated(self, repos):
        first = make_topic("Agent vs tool", canonical="agent-vs-tool")
        second = make_topic("Agents versus tools", canonical="agent-vs-tool")

        first_id, created_first = repos.topics.upsert(first)
        second_id, created_second = repos.topics.upsert(second)

        assert created_first is True
        assert created_second is False
        assert first_id == second_id

    def test_different_topics_both_persist(self, repos):
        repos.topics.upsert(make_topic("A", canonical="a"))
        repos.topics.upsert(make_topic("B", canonical="b"))
        assert len(repos.topics.list()) == 2


class TestAppendOnlyScoring:
    def test_rescoring_appends_rather_than_overwrites(self, repos, cfg):
        topic = make_topic(canonical="rescore-me")
        repos.topics.upsert(topic)

        first = score_topic(topic, make_rating(brand_fit=6.0), cfg,
                            scoring_model="gpt-5-mini", scoring_prompt_version="scorer_v1")
        repos.scores.insert(first)

        second = score_topic(topic, make_rating(brand_fit=9.0), cfg,
                             scoring_model="gpt-5", scoring_prompt_version="scorer_v2")
        repos.scores.insert(second)

        history = repos.scores.history_for_topic(topic.id)
        assert len(history) == 2, "the earlier verdict must survive"
        assert {h.brand_fit for h in history} == {6.0, 9.0}
        assert repos.scores.latest_for_topic(topic.id).brand_fit == 9.0

    def test_score_repository_exposes_no_update_method(self):
        """Append-only is enforced by absence, not by discipline."""
        from content_os.storage.repositories import ScoreRepository

        assert not hasattr(ScoreRepository, "update")
        assert not hasattr(ScoreRepository, "set")

    def test_every_component_score_is_stored(self, repos, cfg):
        topic = make_topic(canonical="components")
        repos.topics.upsert(topic)
        repos.scores.insert(
            score_topic(topic, make_rating(), cfg,
                        scoring_model="m", scoring_prompt_version="v")
        )
        stored = repos.scores.latest_for_topic(topic.id)

        for dimension in ("brand_fit", "audience_fit", "trend_velocity",
                          "originality", "visual_potential", "production_fit"):
            assert getattr(stored, dimension) is not None
        assert stored.base_score is not None
        assert stored.adjusted_score is not None
        assert stored.saturation_penalty is not None


class TestProvenanceMetadata:
    def test_content_retains_agent_model_and_prompt_version(self, repos, cfg):
        topic = make_topic(canonical="provenance")
        repos.topics.upsert(topic)
        content = make_content(topic.id, model="gpt-5", prompt_version="reel_writer_v1")
        repos.content.insert(content)

        row = repos.content.get(content.id)
        assert row["generator_agent"] == "reel_writer"
        assert row["generator_model"] == "gpt-5"
        assert row["generator_prompt_version"] == "reel_writer_v1"

    def test_score_retains_model_prompt_and_config_version(self, repos, cfg):
        topic = make_topic(canonical="score-provenance")
        repos.topics.upsert(topic)
        repos.scores.insert(
            score_topic(topic, make_rating(), cfg,
                        scoring_model="gpt-5-mini", scoring_prompt_version="scorer_v1")
        )
        stored = repos.scores.latest_for_topic(topic.id)
        assert stored.scoring_model == "gpt-5-mini"
        assert stored.scoring_prompt_version == "scorer_v1"
        assert stored.scoring_config_version == cfg.version
        assert stored.scoring_config_version != "unversioned"

    def test_qa_result_retains_model_and_prompt_version(self, repos, cfg):
        topic = make_topic(canonical="qa-provenance")
        repos.topics.upsert(topic)
        content = make_content(topic.id)
        repos.content.insert(content)

        repos.qa.insert(
            content.id,
            QAResult(
                approved=True, scores={"hook_strength": 8.0}, composite=7.5,
                issues=[], required_changes=[], failed_gates=[],
                agent_recommends_approval=True, verdict_rationale="fine",
                qa_model="gpt-5", qa_prompt_version="qa_v1",
            ),
            run_id=None,
        )
        row = repos.qa.history(content.id)[0]
        assert row["qa_model"] == "gpt-5"
        assert row["qa_prompt_version"] == "qa_v1"


class TestCreativeVariantLinkage:
    def test_variants_link_back_to_their_content(self, repos):
        topic = make_topic(canonical="variants")
        repos.topics.upsert(topic)
        content = make_content(topic.id)
        repos.content.insert(content)

        hooks = ["Hook A", "Hook B", "Hook C"]
        for index, hook in enumerate(hooks):
            repos.variants.insert(
                CreativeVariant(
                    id=new_id("creative"), content_id=content.id,
                    variant_type="hook", label="control" if index == 0 else f"v{index}",
                    hook=hook, is_control=index == 0, created_at=utcnow(),
                )
            )

        stored = repos.variants.for_content(content.id)
        assert len(stored) == 3
        assert [v.hook for v in stored] == hooks
        assert all(v.content_id == content.id for v in stored)
        assert sum(1 for v in stored if v.is_control) == 1

    def test_variants_trace_through_to_the_topic(self, repos):
        """source -> topic -> content -> creative must be walkable."""
        topic = make_topic(canonical="traceable")
        repos.topics.upsert(topic)
        content = make_content(topic.id)
        repos.content.insert(content)
        repos.variants.insert(
            CreativeVariant(id=new_id("creative"), content_id=content.id,
                            variant_type="hook", label="control", hook="h",
                            is_control=True, created_at=utcnow())
        )

        variant = repos.variants.for_content(content.id)[0]
        content_row = repos.content.get(variant.content_id)
        topic_row = repos.topics.get(content_row["topic_id"])
        assert topic_row.id == topic.id


class TestPerformanceSnapshots:
    def test_multiple_snapshots_for_one_post_all_persist(self, repos):
        topic = make_topic(canonical="snapshots")
        repos.topics.upsert(topic)
        content = make_content(topic.id)
        repos.content.insert(content)

        for hours, reach in ((72, 4000), (48, 7000), (24, 9500)):
            repos.performance.insert(
                make_performance(content.id, hours_ago=hours, reach=reach)
            )

        snapshots = repos.performance.for_content(content.id)
        assert len(snapshots) == 3
        assert [s.reach for s in snapshots] == [4000, 7000, 9500], "ordered by time"
        assert repos.performance.latest_for_content(content.id).reach == 9500

    def test_duplicate_snapshot_is_rejected_not_silently_updated(self, repos):
        import sqlite3

        topic = make_topic(canonical="dupe-snapshot")
        repos.topics.upsert(topic)
        content = make_content(topic.id)
        repos.content.insert(content)

        perf = make_performance(content.id, hours_ago=24)
        repos.performance.insert(perf)

        duplicate = make_performance(content.id, hours_ago=24, reach=99999)
        duplicate.snapshot_time = perf.snapshot_time
        with pytest.raises(sqlite3.IntegrityError):
            repos.performance.insert(duplicate)

        assert repos.performance.latest_for_content(content.id).reach == perf.reach

    def test_latest_per_content_returns_one_row_each(self, repos):
        topic = make_topic(canonical="latest-each")
        repos.topics.upsert(topic)
        for index in range(3):
            content = make_content(topic.id, title=f"post {index}")
            repos.content.insert(content)
            for hours in (48, 24):
                repos.performance.insert(
                    make_performance(content.id, hours_ago=hours, reach=1000 * hours)
                )

        latest = repos.performance.latest_per_content()
        assert len(latest) == 3
        assert all(p.reach == 24000 for p in latest)


class TestAgentRunLedger:
    def test_successful_and_failed_calls_are_both_recorded(self, repos):
        now = datetime.now(timezone.utc)
        repos.agent_runs.record(
            run_id=None, workflow_name="reel_generation", agent_name="reel_writer",
            model="gpt-5", prompt_version="reel_writer_v1",
            started_at=now, completed_at=now + timedelta(seconds=4), status="OK",
            input_tokens=1000, output_tokens=500, total_tokens=1500,
            estimated_cost=0.00625, requests=1,
        )
        repos.agent_runs.record(
            run_id=None, workflow_name="reel_generation", agent_name="reel_writer",
            model="gpt-5", prompt_version="reel_writer_v1",
            started_at=now, completed_at=now + timedelta(seconds=1), status="ERROR",
            error_type="ValidationError", error_message="bad schema",
        )
        summary = repos.agent_runs.usage_summary()
        assert len(summary) == 1
        assert summary[0]["invocations"] == 2
        assert summary[0]["failures"] == 1
        assert summary[0]["total_tokens"] == 1500

    def test_cost_per_content_aggregates_every_call(self, repos):
        topic = make_topic(canonical="cost")
        repos.topics.upsert(topic)
        content = make_content(topic.id)
        repos.content.insert(content)

        now = datetime.now(timezone.utc)
        for agent, cost in (("reel_writer", 0.02), ("qa", 0.01)):
            repos.agent_runs.record(
                run_id=None, workflow_name="reel_generation", agent_name=agent,
                model="gpt-5", prompt_version="v1", started_at=now,
                completed_at=now, status="OK", content_id=content.id,
                total_tokens=1000, estimated_cost=cost,
            )
        row = repos.agent_runs.cost_per_content(content.id)
        assert row["invocations"] == 2
        assert row["estimated_cost"] == pytest.approx(0.03)


class TestHumanApprovalGate:
    def test_content_is_not_approved_by_default(self, repos):
        topic = make_topic(canonical="approval")
        repos.topics.upsert(topic)
        content = make_content(topic.id)
        repos.content.insert(content)
        assert repos.approvals.is_approved("content", content.id, "publish") is False

    def test_approval_is_recorded_with_a_named_human(self, repos):
        topic = make_topic(canonical="approval2")
        repos.topics.upsert(topic)
        content = make_content(topic.id)
        repos.content.insert(content)

        repos.approvals.record(
            subject_type="content", subject_id=content.id, action="publish",
            decision="APPROVED", approved_by="sagar", notes="looks good",
        )
        assert repos.approvals.is_approved("content", content.id, "publish") is True
        assert repos.approvals.latest("content", content.id, "publish")["approved_by"] == "sagar"
