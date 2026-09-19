"""Repositories.

Append-only repositories deliberately expose no update method. There is no
`ScoreRepository.update` to call by accident, which is the cheapest possible way
to guarantee that scoring history, performance snapshots, QA verdicts, and the
token ledger stay intact.

Mutation is confined to exactly three places: topic status, content item status
and publish metadata, and experiment/ad-test lifecycle fields.
"""

from __future__ import annotations

import sqlite3
from datetime import datetime
from typing import Any, Sequence

from content_os.ids import new_id, slugify
from content_os.models.ads import AdEligibility, AdTest
from content_os.models.brand import BrandMemory
from content_os.models.content import (
    ContentItem,
    ContentStatus,
    CreativeVariant,
    QAResult,
)
from content_os.models.experiments import AnalystFinding, Experiment
from content_os.models.performance import PostPerformance
from content_os.models.topics import (
    OpportunityScore,
    ScoredTopic,
    TopicCandidate,
    TopicStatus,
)
from content_os.storage.brief_repositories import (
    BriefRepository,
    ExecutionPlanRepository,
    HookRepository,
)
from content_os.storage.db import dumps, from_iso, loads, to_iso, utcnow


class _Base:
    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn

    def _exec(self, sql: str, params: Sequence[Any] = ()) -> sqlite3.Cursor:
        return self.conn.execute(sql, tuple(params))


# ------------------------------------------------------------------ runs


class RunRepository(_Base):
    def create(self, workflow: str, args: dict[str, Any] | None = None) -> str:
        run_id = new_id("run")
        self._exec(
            "INSERT INTO runs (id, workflow, started_at, status, args_json) "
            "VALUES (?, ?, ?, 'RUNNING', ?)",
            (run_id, workflow, to_iso(utcnow()), dumps(args or {})),
        )
        return run_id

    def complete(self, run_id: str, status: str = "COMPLETED", notes: str = "") -> None:
        self._exec(
            "UPDATE runs SET completed_at = ?, status = ?, notes = ? WHERE id = ?",
            (to_iso(utcnow()), status, notes, run_id),
        )

    def get(self, run_id: str) -> sqlite3.Row | None:
        return self._exec("SELECT * FROM runs WHERE id = ?", (run_id,)).fetchone()


class AgentRunRepository(_Base):
    """Append-only token and cost ledger. One row per agent invocation,
    including failures and retries."""

    def record(
        self,
        *,
        run_id: str | None,
        workflow_name: str,
        agent_name: str,
        model: str,
        prompt_version: str,
        started_at: datetime,
        completed_at: datetime,
        status: str,
        reasoning_effort: str | None = None,
        trace_id: str | None = None,
        topic_id: str | None = None,
        content_id: str | None = None,
        requests: int = 0,
        input_tokens: int = 0,
        cached_input_tokens: int = 0,
        cache_write_tokens: int = 0,
        output_tokens: int = 0,
        reasoning_tokens: int = 0,
        total_tokens: int = 0,
        uncached_input_cost: float = 0.0,
        cached_input_cost: float = 0.0,
        cache_write_cost: float = 0.0,
        output_cost: float = 0.0,
        estimated_cost: float = 0.0,
        pricing_known: bool = True,
        attempt: int = 1,
        error_type: str | None = None,
        error_message: str | None = None,
    ) -> str:
        agent_run_id = new_id("agent_run")
        duration_ms = int((completed_at - started_at).total_seconds() * 1000)
        self._exec(
            """
            INSERT INTO agent_runs (
                id, run_id, workflow_name, agent_name, trace_id,
                topic_id, content_id, model, prompt_version, reasoning_effort,
                started_at, completed_at, duration_ms, status,
                requests, input_tokens, cached_input_tokens, cache_write_tokens,
                output_tokens, reasoning_tokens, total_tokens,
                uncached_input_cost, cached_input_cost, cache_write_cost,
                output_cost, estimated_cost, pricing_known,
                attempt, error_type, error_message
            ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            """,
            (
                agent_run_id, run_id, workflow_name, agent_name, trace_id,
                topic_id, content_id, model, prompt_version, reasoning_effort,
                to_iso(started_at), to_iso(completed_at), duration_ms, status,
                requests, input_tokens, cached_input_tokens, cache_write_tokens,
                output_tokens, reasoning_tokens, total_tokens,
                uncached_input_cost, cached_input_cost, cache_write_cost,
                output_cost, estimated_cost, int(pricing_known),
                attempt, error_type, error_message,
            ),
        )
        return agent_run_id

    def usage_summary(self, run_id: str | None = None) -> list[sqlite3.Row]:
        sql = """
            SELECT agent_name, model,
                   MAX(reasoning_effort)      AS reasoning_effort,
                   COUNT(*)                   AS invocations,
                   SUM(requests)              AS requests,
                   SUM(input_tokens)          AS input_tokens,
                   SUM(cached_input_tokens)   AS cached_input_tokens,
                   SUM(cache_write_tokens)    AS cache_write_tokens,
                   SUM(output_tokens)         AS output_tokens,
                   SUM(reasoning_tokens)      AS reasoning_tokens,
                   SUM(total_tokens)          AS total_tokens,
                   SUM(uncached_input_cost)   AS uncached_input_cost,
                   SUM(cached_input_cost)     AS cached_input_cost,
                   SUM(cache_write_cost)      AS cache_write_cost,
                   SUM(output_cost)           AS output_cost,
                   SUM(estimated_cost)        AS estimated_cost,
                   MIN(pricing_known)         AS pricing_known,
                   SUM(CASE WHEN status != 'OK' THEN 1 ELSE 0 END) AS failures,
                   AVG(duration_ms)           AS avg_ms
            FROM agent_runs
        """
        params: tuple[Any, ...] = ()
        if run_id:
            sql += " WHERE run_id = ?"
            params = (run_id,)
        sql += " GROUP BY agent_name, model ORDER BY estimated_cost DESC"
        return self._exec(sql, params).fetchall()

    def cost_per_content(self, content_id: str) -> sqlite3.Row | None:
        return self._exec(
            "SELECT COUNT(*) AS invocations, SUM(total_tokens) AS total_tokens, "
            "SUM(estimated_cost) AS estimated_cost "
            "FROM agent_runs WHERE content_id = ?",
            (content_id,),
        ).fetchone()


# ------------------------------------------------------------------ topics


class TopicRepository(_Base):
    def upsert(self, topic: TopicCandidate) -> tuple[str, bool]:
        """Insert, or return the existing id if this canonical topic is known.

        Returns (topic_id, created). Deduplication is by canonical slug so the
        same story arriving from three sources does not become three topics.
        """
        canonical = slugify(topic.canonical_topic)
        existing = self._exec(
            "SELECT id FROM topics WHERE canonical_topic = ?", (canonical,)
        ).fetchone()
        if existing:
            return existing["id"], False

        now = to_iso(utcnow())
        self._exec(
            """
            INSERT INTO topics (
                id, canonical_topic, title, description,
                discovered_at, event_date, source_count,
                source_urls_json, source_types_json, trend_signals_json,
                target_audience_json, potential_angles_json, content_pillars_json,
                trend_velocity, saturation, why_it_matters, discussion_angle,
                status, run_id, created_at, updated_at
            ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            """,
            (
                topic.id, canonical, topic.title, topic.summary,
                to_iso(topic.discovered_at), to_iso(topic.event_date),
                len(topic.source_urls),
                dumps(topic.source_urls), dumps(topic.source_types),
                dumps(topic.trend_signals), dumps(topic.target_audience),
                dumps(topic.potential_angles), dumps(topic.content_pillars),
                None, topic.estimated_saturation,
                topic.why_it_matters, topic.discussion_angle,
                topic.status.value, topic.run_id, now, now,
            ),
        )
        return topic.id, True

    def set_status(self, topic_id: str, status: TopicStatus) -> None:
        self._exec(
            "UPDATE topics SET status = ?, updated_at = ? WHERE id = ?",
            (status.value, to_iso(utcnow()), topic_id),
        )

    def get(self, topic_id: str) -> TopicCandidate | None:
        row = self._exec("SELECT * FROM topics WHERE id = ?", (topic_id,)).fetchone()
        return self._hydrate(row) if row else None

    def find_by_prefix(self, prefix: str) -> TopicCandidate | None:
        """Allow short ids on the command line."""
        row = self._exec(
            "SELECT * FROM topics WHERE id LIKE ? ORDER BY created_at LIMIT 2",
            (f"{prefix}%",),
        ).fetchall()
        if len(row) == 1:
            return self._hydrate(row[0])
        return None

    def list(
        self, status: TopicStatus | None = None, limit: int = 200
    ) -> list[TopicCandidate]:
        if status:
            rows = self._exec(
                "SELECT * FROM topics WHERE status = ? ORDER BY discovered_at DESC LIMIT ?",
                (status.value, limit),
            ).fetchall()
        else:
            rows = self._exec(
                "SELECT * FROM topics ORDER BY discovered_at DESC LIMIT ?", (limit,)
            ).fetchall()
        return [self._hydrate(r) for r in rows]

    def unscored(self, limit: int = 200) -> list[TopicCandidate]:
        rows = self._exec(
            """
            SELECT t.* FROM topics t
            LEFT JOIN opportunity_scores s ON s.topic_id = t.id
            WHERE s.id IS NULL
            ORDER BY t.discovered_at DESC LIMIT ?
            """,
            (limit,),
        ).fetchall()
        return [self._hydrate(r) for r in rows]

    def recent_titles(self, limit: int = 40) -> list[str]:
        rows = self._exec(
            "SELECT title FROM topics ORDER BY discovered_at DESC LIMIT ?", (limit,)
        ).fetchall()
        return [r["title"] for r in rows]

    @staticmethod
    def _hydrate(row: sqlite3.Row) -> TopicCandidate:
        return TopicCandidate(
            id=row["id"],
            title=row["title"],
            canonical_topic=row["canonical_topic"],
            summary=row["description"] or "",
            source_urls=loads(row["source_urls_json"]),
            source_types=loads(row["source_types_json"]),
            discovered_at=from_iso(row["discovered_at"]),
            event_date=from_iso(row["event_date"]),
            trend_signals=loads(row["trend_signals_json"]),
            target_audience=loads(row["target_audience_json"]),
            potential_angles=loads(row["potential_angles_json"]),
            content_pillars=loads(row["content_pillars_json"]),
            estimated_saturation=row["saturation"] or 0.0,
            status=TopicStatus(row["status"]),
            run_id=row["run_id"],
            why_it_matters=row["why_it_matters"] or "",
            discussion_angle=row["discussion_angle"] or "",
        )


class ScoreRepository(_Base):
    """Append-only. No update method exists by design."""

    def insert(self, score: OpportunityScore) -> str:
        self._exec(
            """
            INSERT INTO opportunity_scores (
                id, topic_id, run_id,
                brand_fit, audience_fit, trend_velocity, originality,
                visual_potential, production_fit,
                decayed_trend_velocity, base_score, saturation,
                effective_saturation, saturation_penalty, adjusted_score,
                vetoed, veto_flag,
                scoring_model, scoring_prompt_version, scoring_config_version,
                rationale, recommended_pillar, recommended_format, created_at
            ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            """,
            (
                score.id, score.topic_id, score.run_id,
                score.brand_fit, score.audience_fit, score.trend_velocity,
                score.originality, score.visual_potential, score.production_fit,
                score.decayed_trend_velocity, score.base_score, score.saturation,
                score.effective_saturation, score.saturation_penalty,
                score.adjusted_score,
                int(score.vetoed), score.veto_flag,
                score.scoring_model, score.scoring_prompt_version,
                score.scoring_config_version,
                score.rationale, score.recommended_pillar, score.recommended_format,
                to_iso(score.created_at),
            ),
        )
        return score.id

    def latest_for_topic(self, topic_id: str) -> OpportunityScore | None:
        row = self._exec(
            "SELECT * FROM opportunity_scores WHERE topic_id = ? "
            "ORDER BY created_at DESC, rowid DESC LIMIT 1",
            (topic_id,),
        ).fetchone()
        return self._hydrate(row) if row else None

    def history_for_topic(self, topic_id: str) -> list[OpportunityScore]:
        rows = self._exec(
            "SELECT * FROM opportunity_scores WHERE topic_id = ? ORDER BY created_at",
            (topic_id,),
        ).fetchall()
        return [self._hydrate(r) for r in rows]

    def ranked(
        self, include_vetoed: bool = False, limit: int = 100
    ) -> list[ScoredTopic]:
        """Topics joined to their most recent score, ranked by adjusted score."""
        sql = """
            SELECT t.*, s.id AS score_id
            FROM topics t
            JOIN opportunity_scores s ON s.id = (
                SELECT id FROM opportunity_scores
                WHERE topic_id = t.id
                ORDER BY created_at DESC, rowid DESC LIMIT 1
            )
            WHERE (? = 1 OR s.vetoed = 0)
              AND t.status NOT IN ('PUBLISHED', 'REJECTED', 'EXPIRED')
            ORDER BY s.adjusted_score DESC
            LIMIT ?
        """
        rows = self._exec(sql, (1 if include_vetoed else 0, limit)).fetchall()
        out: list[ScoredTopic] = []
        for row in rows:
            topic = TopicRepository._hydrate(row)
            score = self.latest_for_topic(topic.id)
            if score:
                out.append(ScoredTopic(topic=topic, score=score))
        return out

    @staticmethod
    def _hydrate(row: sqlite3.Row) -> OpportunityScore:
        return OpportunityScore(
            id=row["id"],
            topic_id=row["topic_id"],
            run_id=row["run_id"],
            brand_fit=row["brand_fit"],
            audience_fit=row["audience_fit"],
            trend_velocity=row["trend_velocity"],
            originality=row["originality"],
            visual_potential=row["visual_potential"],
            production_fit=row["production_fit"],
            decayed_trend_velocity=row["decayed_trend_velocity"],
            base_score=row["base_score"],
            saturation=row["saturation"],
            effective_saturation=row["effective_saturation"],
            saturation_penalty=row["saturation_penalty"],
            adjusted_score=row["adjusted_score"],
            vetoed=bool(row["vetoed"]),
            veto_flag=row["veto_flag"],
            scoring_model=row["scoring_model"],
            scoring_prompt_version=row["scoring_prompt_version"],
            scoring_config_version=row["scoring_config_version"],
            rationale=row["rationale"] or "",
            recommended_pillar=row["recommended_pillar"] or "",
            recommended_format=row["recommended_format"] or "",
            created_at=from_iso(row["created_at"]),
        )


# ------------------------------------------------------------------ content


class PlanRepository(_Base):
    def insert(
        self,
        *,
        run_id: str | None,
        horizon_days: int,
        target_posts: int,
        portfolio_rationale: str,
        composition: dict[str, Any],
        balance_report: dict[str, Any],
    ) -> str:
        plan_id = new_id("plan")
        self._exec(
            "INSERT INTO content_plans (id, run_id, created_at, horizon_days, "
            "target_posts, portfolio_rationale, composition_json, balance_report_json) "
            "VALUES (?,?,?,?,?,?,?,?)",
            (
                plan_id, run_id, to_iso(utcnow()), horizon_days, target_posts,
                portfolio_rationale, dumps(composition), dumps(balance_report),
            ),
        )
        return plan_id

    def get(self, plan_id: str) -> sqlite3.Row | None:
        return self._exec(
            "SELECT * FROM content_plans WHERE id = ?", (plan_id,)
        ).fetchone()

    def latest(self) -> sqlite3.Row | None:
        return self._exec(
            "SELECT * FROM content_plans ORDER BY created_at DESC LIMIT 1"
        ).fetchone()


class ContentRepository(_Base):
    def insert(
        self,
        item: ContentItem,
        *,
        plan_id: str | None = None,
        urgency: str | None = None,
        strategist_reasoning: str | None = None,
        strategist_score: float | None = None,
    ) -> str:
        self._exec(
            """
            INSERT INTO content_items (
                id, topic_id, plan_id, run_id, format, pillar, strategic_role,
                title, hook, body_json, caption, cta,
                avatar_used, human_used, screen_demo_used, status,
                planned_publish_date, actual_publish_date,
                urgency, strategist_reasoning, strategist_score,
                generator_agent, generator_model, generator_prompt_version,
                qa_approved, qa_composite, qa_json, created_at, updated_at
            ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            """,
            (
                item.id, item.topic_id, plan_id, item.run_id, item.format,
                item.pillar, item.strategic_role,
                item.title, item.hook, item.body_json, item.caption, item.cta,
                int(item.avatar_used), int(item.human_used),
                int(item.screen_demo_used), item.status.value,
                to_iso(item.planned_publish_date), to_iso(item.actual_publish_date),
                urgency, strategist_reasoning, strategist_score,
                item.generator_agent, item.generator_model,
                item.generator_prompt_version,
                None if item.qa_approved is None else int(item.qa_approved),
                item.qa_composite, item.qa_json,
                to_iso(item.created_at), to_iso(item.updated_at),
            ),
        )
        return item.id

    def insert_with_strategy(
        self, item: ContentItem, sections_covered: list[str] | None = None
    ) -> str:
        """Insert a content item carrying its human strategy fields.

        These columns are what make it possible to later ask which learning
        objectives drove saves, or which hook strategies drove shares, rather
        than only which finished copy happened to perform.
        """
        content_id = self.insert(item)
        self._exec(
            "UPDATE content_items SET brief_id = ?, core_thesis = ?, "
            "learning_objective = ?, hook_direction = ?, "
            "approved_hook_points_json = ?, high_level_sections_json = ?, "
            "preferred_pov = ?, visual_direction = ?, hook_strategy = ?, "
            "hook_source = ?, hook_variant_id = ?, learning_payoff = ?, "
            "save_reason = ?, share_reason = ?, sections_covered_json = ? "
            "WHERE id = ?",
            (
                item.brief_id, item.core_thesis, item.learning_objective,
                item.hook_direction, dumps(item.approved_hook_points),
                dumps(item.high_level_sections), item.preferred_pov,
                item.visual_direction, item.hook_strategy, item.hook_source,
                item.hook_variant_id, item.learning_payoff, item.save_reason,
                item.share_reason, dumps(sections_covered or []), content_id,
            ),
        )
        return content_id

    def attach_qa(
        self, content_id: str, *, approved: bool, composite: float, qa_json: str
    ) -> None:
        """Record the QA outcome on the content item.

        The full QA history lives in qa_results; this is the denormalised latest
        verdict so listing content does not need a join.
        """
        status = (
            ContentStatus.READY_FOR_REVIEW.value
            if approved
            else ContentStatus.QA_FAILED.value
        )
        self._exec(
            "UPDATE content_items SET qa_approved = ?, qa_composite = ?, "
            "qa_json = ?, status = ?, updated_at = ? WHERE id = ?",
            (int(approved), composite, qa_json, status, to_iso(utcnow()), content_id),
        )

    def set_status(self, content_id: str, status: ContentStatus) -> None:
        self._exec(
            "UPDATE content_items SET status = ?, updated_at = ? WHERE id = ?",
            (status.value, to_iso(utcnow()), content_id),
        )

    def mark_published(
        self, content_id: str, platform_post_id: str, published_at: datetime
    ) -> None:
        self._exec(
            "UPDATE content_items SET status = ?, platform_post_id = ?, "
            "actual_publish_date = ?, updated_at = ? WHERE id = ?",
            (
                ContentStatus.PUBLISHED.value, platform_post_id,
                to_iso(published_at), to_iso(utcnow()), content_id,
            ),
        )

    def get(self, content_id: str) -> sqlite3.Row | None:
        return self._exec(
            "SELECT * FROM content_items WHERE id = ?", (content_id,)
        ).fetchone()

    def find_by_prefix(self, prefix: str) -> sqlite3.Row | None:
        rows = self._exec(
            "SELECT * FROM content_items WHERE id LIKE ? LIMIT 2", (f"{prefix}%",)
        ).fetchall()
        return rows[0] if len(rows) == 1 else None

    def list(
        self, status: ContentStatus | None = None, limit: int = 100
    ) -> list[sqlite3.Row]:
        if status:
            return self._exec(
                "SELECT * FROM content_items WHERE status = ? "
                "ORDER BY created_at DESC LIMIT ?",
                (status.value, limit),
            ).fetchall()
        return self._exec(
            "SELECT * FROM content_items ORDER BY created_at DESC LIMIT ?", (limit,)
        ).fetchall()

    def recent_for_context(
        self, limit: int = 20, exclude_id: str | None = None
    ) -> list[dict[str, Any]]:
        """Compact recent-history view handed to agents so they can avoid
        repeating pillars, formats, and hooks.

        exclude_id drops one item from the list. Generation fills in a row that
        the planner already created, so without this the writer and QA both see
        the item they are working on as prior art and call it a duplicate of
        itself.
        """
        rows = self._exec(
            "SELECT id, title, format, pillar, hook, status, planned_publish_date, "
            "actual_publish_date FROM content_items "
            "WHERE (? IS NULL OR id != ?) "
            "ORDER BY COALESCE(actual_publish_date, planned_publish_date, created_at) "
            "DESC LIMIT ?",
            (exclude_id, exclude_id, limit),
        ).fetchall()
        return [dict(r) for r in rows]

    def by_plan(self, plan_id: str) -> list[sqlite3.Row]:
        return self._exec(
            "SELECT * FROM content_items WHERE plan_id = ? ORDER BY created_at",
            (plan_id,),
        ).fetchall()


class CreativeVariantRepository(_Base):
    def insert(self, variant: CreativeVariant, experiment_id: str | None = None) -> str:
        self._exec(
            "INSERT INTO creative_variants (id, content_id, variant_type, label, "
            "hook, script, visual_style, duration_seconds, is_control, "
            "experiment_id, created_at) VALUES (?,?,?,?,?,?,?,?,?,?,?)",
            (
                variant.id, variant.content_id, variant.variant_type, variant.label,
                variant.hook, variant.script, variant.visual_style,
                variant.duration_seconds, int(variant.is_control), experiment_id,
                to_iso(variant.created_at),
            ),
        )
        return variant.id

    def for_content(self, content_id: str) -> list[CreativeVariant]:
        rows = self._exec(
            "SELECT * FROM creative_variants WHERE content_id = ? ORDER BY created_at",
            (content_id,),
        ).fetchall()
        return [
            CreativeVariant(
                id=r["id"],
                content_id=r["content_id"],
                variant_type=r["variant_type"],
                label=r["label"] or "",
                hook=r["hook"] or "",
                script=r["script"],
                visual_style=r["visual_style"],
                duration_seconds=r["duration_seconds"],
                is_control=bool(r["is_control"]),
                created_at=from_iso(r["created_at"]),
            )
            for r in rows
        ]


class QARepository(_Base):
    """Append-only. Each revision writes a new row."""

    def insert(self, content_id: str, result: QAResult, run_id: str | None) -> str:
        qa_id = new_id("qa")
        self._exec(
            "INSERT INTO qa_results (id, content_id, run_id, revision_number, "
            "approved, composite, scores_json, issues_json, required_changes_json, "
            "failed_gates_json, agent_recommends_approval, verdict_rationale, "
            "qa_model, qa_prompt_version, created_at) "
            "VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (
                qa_id, content_id, run_id, result.revision_number,
                int(result.approved), result.composite, dumps(result.scores),
                dumps(result.issues), dumps(result.required_changes),
                dumps(result.failed_gates), int(result.agent_recommends_approval),
                result.verdict_rationale, result.qa_model, result.qa_prompt_version,
                to_iso(utcnow()),
            ),
        )
        return qa_id

    def next_revision(self, content_id: str) -> int:
        row = self._exec(
            "SELECT COALESCE(MAX(revision_number), -1) AS n FROM qa_results "
            "WHERE content_id = ?",
            (content_id,),
        ).fetchone()
        return int(row["n"]) + 1

    def history(self, content_id: str) -> list[sqlite3.Row]:
        return self._exec(
            "SELECT * FROM qa_results WHERE content_id = ? ORDER BY revision_number",
            (content_id,),
        ).fetchall()


# ------------------------------------------------------------------ performance


class PerformanceRepository(_Base):
    """Append-only. Two measurements of the same post are two rows."""

    def insert(self, perf: PostPerformance) -> str:
        self._exec(
            """
            INSERT INTO post_performance (
                id, content_id, creative_id, platform_post_id, snapshot_time,
                followers_at_post_time, impressions, reach, follower_reach,
                non_follower_reach, plays, avg_watch_time_seconds,
                total_watch_time_seconds, video_duration_seconds,
                likes, comments, shares, sends, saves,
                profile_visits, new_followers, website_clicks,
                organic_impressions, paid_impressions, created_at
            ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            """,
            (
                perf.id, perf.content_id, perf.creative_id, perf.platform_post_id,
                to_iso(perf.snapshot_time), perf.followers_at_post_time,
                perf.impressions, perf.reach, perf.follower_reach,
                perf.non_follower_reach, perf.plays, perf.avg_watch_time_seconds,
                perf.total_watch_time_seconds, perf.video_duration_seconds,
                perf.likes, perf.comments, perf.shares, perf.sends, perf.saves,
                perf.profile_visits, perf.new_followers, perf.website_clicks,
                perf.organic_impressions, perf.paid_impressions, to_iso(utcnow()),
            ),
        )
        return perf.id

    def latest_per_content(self, limit: int = 200) -> list[PostPerformance]:
        """Most recent snapshot for each content item."""
        rows = self._exec(
            """
            SELECT p.* FROM post_performance p
            JOIN (
                SELECT content_id, MAX(snapshot_time) AS mx
                FROM post_performance GROUP BY content_id
            ) m ON m.content_id = p.content_id AND m.mx = p.snapshot_time
            ORDER BY p.snapshot_time DESC LIMIT ?
            """,
            (limit,),
        ).fetchall()
        return [self._hydrate(r) for r in rows]

    def for_content(self, content_id: str) -> list[PostPerformance]:
        rows = self._exec(
            "SELECT * FROM post_performance WHERE content_id = ? ORDER BY snapshot_time",
            (content_id,),
        ).fetchall()
        return [self._hydrate(r) for r in rows]

    def latest_for_content(self, content_id: str) -> PostPerformance | None:
        row = self._exec(
            "SELECT * FROM post_performance WHERE content_id = ? "
            "ORDER BY snapshot_time DESC LIMIT 1",
            (content_id,),
        ).fetchone()
        return self._hydrate(row) if row else None

    @staticmethod
    def _hydrate(row: sqlite3.Row) -> PostPerformance:
        return PostPerformance(
            id=row["id"],
            content_id=row["content_id"],
            creative_id=row["creative_id"],
            platform_post_id=row["platform_post_id"],
            snapshot_time=from_iso(row["snapshot_time"]),
            followers_at_post_time=row["followers_at_post_time"],
            impressions=row["impressions"] or 0,
            reach=row["reach"] or 0,
            follower_reach=row["follower_reach"] or 0,
            non_follower_reach=row["non_follower_reach"] or 0,
            plays=row["plays"] or 0,
            avg_watch_time_seconds=row["avg_watch_time_seconds"] or 0.0,
            total_watch_time_seconds=row["total_watch_time_seconds"] or 0.0,
            video_duration_seconds=row["video_duration_seconds"] or 0.0,
            likes=row["likes"] or 0,
            comments=row["comments"] or 0,
            shares=row["shares"] or 0,
            sends=row["sends"] or 0,
            saves=row["saves"] or 0,
            profile_visits=row["profile_visits"] or 0,
            new_followers=row["new_followers"] or 0,
            website_clicks=row["website_clicks"] or 0,
            organic_impressions=row["organic_impressions"] or 0,
            paid_impressions=row["paid_impressions"] or 0,
            created_at=from_iso(row["created_at"]),
        )


# ------------------------------------------------------------ experiments/ads


class ExperimentRepository(_Base):
    def upsert(self, exp: Experiment) -> tuple[str, bool]:
        existing = self._exec(
            "SELECT id FROM experiments WHERE name = ?", (exp.name,)
        ).fetchone()
        if existing:
            return existing["id"], False
        self._exec(
            "INSERT INTO experiments (id, name, hypothesis, variable, control, "
            "variant, start_date, end_date, primary_metric, secondary_metrics_json, "
            "status, result, confidence_notes, created_at) "
            "VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (
                exp.id, exp.name, exp.hypothesis, exp.variable, exp.control,
                exp.variant, to_iso(exp.start_date), to_iso(exp.end_date),
                exp.primary_metric, dumps(exp.secondary_metrics), exp.status.value,
                exp.result, exp.confidence_notes, to_iso(exp.created_at),
            ),
        )
        return exp.id, True

    def list(self) -> list[sqlite3.Row]:
        return self._exec("SELECT * FROM experiments ORDER BY created_at").fetchall()

    def conclude(self, experiment_id: str, result: str, confidence_notes: str) -> None:
        self._exec(
            "UPDATE experiments SET status = 'CONCLUDED', result = ?, "
            "confidence_notes = ?, end_date = ? WHERE id = ?",
            (result, confidence_notes, to_iso(utcnow()), experiment_id),
        )


class AdTestRepository(_Base):
    """Schema is live; nothing writes here automatically in v1.

    Creating a test always records it as PROPOSED. Moving it to APPROVED
    requires an explicit approval row naming a human.
    """

    def propose(self, test: AdTest) -> str:
        self._exec(
            "INSERT INTO ad_tests (id, content_id, creative_id, audience_name, "
            "start_date, end_date, daily_budget, total_spend, objective, status, "
            "paid_reach, paid_impressions, paid_profile_visits, paid_followers, "
            "created_at) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (
                test.id, test.content_id, test.creative_id, test.audience_name,
                to_iso(test.start_date), to_iso(test.end_date), test.daily_budget,
                0.0, test.objective, "PROPOSED", 0, 0, 0, 0,
                to_iso(test.created_at),
            ),
        )
        return test.id

    def list(self) -> list[sqlite3.Row]:
        return self._exec("SELECT * FROM ad_tests ORDER BY created_at DESC").fetchall()


class ApprovalRepository(_Base):
    """Audit trail for every human gate.

    Publishing, ad spend, and brand-positioning changes all require a row here.
    Nothing in v1 can take those actions without one.
    """

    def record(
        self,
        *,
        subject_type: str,
        subject_id: str,
        action: str,
        decision: str,
        approved_by: str,
        notes: str = "",
    ) -> str:
        approval_id = new_id("approval")
        self._exec(
            "INSERT INTO approvals (id, subject_type, subject_id, action, decision, "
            "approved_by, notes, created_at) VALUES (?,?,?,?,?,?,?,?)",
            (
                approval_id, subject_type, subject_id, action, decision,
                approved_by, notes, to_iso(utcnow()),
            ),
        )
        return approval_id

    def latest(self, subject_type: str, subject_id: str, action: str):
        return self._exec(
            "SELECT * FROM approvals WHERE subject_type = ? AND subject_id = ? "
            "AND action = ? ORDER BY created_at DESC LIMIT 1",
            (subject_type, subject_id, action),
        ).fetchone()

    def is_approved(self, subject_type: str, subject_id: str, action: str) -> bool:
        row = self.latest(subject_type, subject_id, action)
        return bool(row and row["decision"] == "APPROVED")


class BrandSnapshotRepository(_Base):
    """Append-only brand memory history.

    Lets us reconstruct the positioning that was in force when any given piece
    of content was generated.
    """

    def snapshot(
        self, memory: BrandMemory, source: str, change_note: str = ""
    ) -> str:
        snap_id = new_id("brand_snapshot")
        self._exec(
            "INSERT INTO brand_memory_snapshots (id, version, memory_json, source, "
            "change_note, created_at) VALUES (?,?,?,?,?,?)",
            (
                snap_id, memory.version, memory.model_dump_json(), source,
                change_note, to_iso(utcnow()),
            ),
        )
        return snap_id

    def latest(self) -> sqlite3.Row | None:
        return self._exec(
            "SELECT * FROM brand_memory_snapshots ORDER BY created_at DESC LIMIT 1"
        ).fetchone()


class FindingRepository(_Base):
    """Typed analyst findings. An observation and a hypothesis are stored
    differently so a guess never feeds back into scoring as a fact."""

    def insert(self, finding: AnalystFinding, run_id: str | None) -> str:
        finding_id = new_id("finding")
        self._exec(
            "INSERT INTO analyst_findings (id, run_id, claim_type, statement, "
            "supporting_metric, sample_size, confidence, caveats_json, created_at) "
            "VALUES (?,?,?,?,?,?,?,?,?)",
            (
                finding_id, run_id, finding.claim_type, finding.statement,
                finding.supporting_metric, finding.sample_size, finding.confidence,
                dumps(finding.caveats), to_iso(utcnow()),
            ),
        )
        return finding_id

    def list(self, claim_type: str | None = None, limit: int = 50) -> list[sqlite3.Row]:
        if claim_type:
            return self._exec(
                "SELECT * FROM analyst_findings WHERE claim_type = ? "
                "ORDER BY created_at DESC LIMIT ?",
                (claim_type, limit),
            ).fetchall()
        return self._exec(
            "SELECT * FROM analyst_findings ORDER BY created_at DESC LIMIT ?", (limit,)
        ).fetchall()


class Repositories:
    """One handle carrying every repository, so workflows take a single object."""

    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn
        self.runs = RunRepository(conn)
        self.agent_runs = AgentRunRepository(conn)
        self.topics = TopicRepository(conn)
        self.scores = ScoreRepository(conn)
        self.plans = PlanRepository(conn)
        self.content = ContentRepository(conn)
        self.variants = CreativeVariantRepository(conn)
        self.qa = QARepository(conn)
        self.performance = PerformanceRepository(conn)
        self.experiments = ExperimentRepository(conn)
        self.ads = AdTestRepository(conn)
        self.approvals = ApprovalRepository(conn)
        self.brand_snapshots = BrandSnapshotRepository(conn)
        self.findings = FindingRepository(conn)
        self.briefs = BriefRepository(conn)
        self.execution_plans = ExecutionPlanRepository(conn)
        self.hooks = HookRepository(conn)
