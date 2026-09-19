"""Repositories for human strategy: briefs, execution plans, hook variants.

Briefs are the one thing in this system a human edits repeatedly, so unlike the
evidence tables they do support update. What does not change is the record of
what was approved: approval stamps a time and a name, and the full brief JSON is
stored so the exact object that entered production stays recoverable.
"""

from __future__ import annotations

import sqlite3
from datetime import datetime
from typing import Any

from content_os.ids import new_id
from content_os.models.brief import (
    BriefStatus,
    ContentBrief,
    ExecutionPlan,
    HookSet,
)
from content_os.storage.db import dumps, from_iso, loads, to_iso, utcnow

# Only APPROVED briefs may enter production. Nothing else is processed.
PRODUCIBLE = (BriefStatus.APPROVED,)


class BriefRepository:
    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn

    def upsert(self, brief: ContentBrief) -> str:
        now = to_iso(brief.created_at or utcnow())
        self.conn.execute(
            """
            INSERT INTO content_briefs (
                brief_id, topic, core_thesis, why_this_matters, audience_takeaway,
                learning_objective, target_audience_json, brand_pillar,
                content_format, hook_direction, approved_hook_points_json,
                high_level_sections_json, core_examples_json, preferred_pov,
                desired_tone, visual_direction, desired_duration_seconds,
                desired_slide_count, references_json, factual_claims_json,
                must_include_json, must_avoid_json, cta_direction, urgency, notes,
                status, priority, scheduled_date, created_at, approved_at,
                approved_by, published_at, brief_json
            ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            ON CONFLICT(brief_id) DO UPDATE SET
                topic=excluded.topic,
                core_thesis=excluded.core_thesis,
                why_this_matters=excluded.why_this_matters,
                audience_takeaway=excluded.audience_takeaway,
                learning_objective=excluded.learning_objective,
                target_audience_json=excluded.target_audience_json,
                brand_pillar=excluded.brand_pillar,
                content_format=excluded.content_format,
                hook_direction=excluded.hook_direction,
                approved_hook_points_json=excluded.approved_hook_points_json,
                high_level_sections_json=excluded.high_level_sections_json,
                core_examples_json=excluded.core_examples_json,
                preferred_pov=excluded.preferred_pov,
                desired_tone=excluded.desired_tone,
                visual_direction=excluded.visual_direction,
                desired_duration_seconds=excluded.desired_duration_seconds,
                desired_slide_count=excluded.desired_slide_count,
                references_json=excluded.references_json,
                factual_claims_json=excluded.factual_claims_json,
                must_include_json=excluded.must_include_json,
                must_avoid_json=excluded.must_avoid_json,
                cta_direction=excluded.cta_direction,
                urgency=excluded.urgency,
                notes=excluded.notes,
                priority=excluded.priority,
                scheduled_date=excluded.scheduled_date,
                brief_json=excluded.brief_json
            """,
            (
                brief.brief_id, brief.topic, brief.core_thesis,
                brief.why_this_matters, brief.audience_takeaway,
                brief.learning_objective, dumps(brief.target_audience),
                brief.brand_pillar, brief.content_format, brief.hook_direction,
                dumps(brief.approved_hook_points),
                dumps(brief.high_level_sections), dumps(brief.core_examples),
                brief.preferred_pov, brief.desired_tone, brief.visual_direction,
                brief.desired_duration_seconds, brief.desired_slide_count,
                dumps(brief.references), dumps(brief.factual_claims_to_verify),
                dumps(brief.must_include), dumps(brief.must_avoid),
                brief.cta_direction, brief.urgency, brief.notes,
                brief.status.value, brief.priority, to_iso(brief.scheduled_date),
                now, to_iso(brief.approved_at), brief.approved_by,
                to_iso(brief.published_at), brief.model_dump_json(),
            ),
        )
        return brief.brief_id

    def get(self, brief_id: str) -> ContentBrief | None:
        row = self.conn.execute(
            "SELECT * FROM content_briefs WHERE brief_id = ?", (brief_id,)
        ).fetchone()
        if row is None:
            row = self.conn.execute(
                "SELECT * FROM content_briefs WHERE brief_id LIKE ? LIMIT 2",
                (f"{brief_id}%",),
            ).fetchall()
            if len(row) != 1:
                return None
            row = row[0]
        return self._hydrate(row)

    def approve(self, brief_id: str, approved_by: str, note: str = "") -> bool:
        brief = self.get(brief_id)
        if brief is None:
            return False
        self.conn.execute(
            "UPDATE content_briefs SET status = ?, approved_at = ?, approved_by = ? "
            "WHERE brief_id = ?",
            (BriefStatus.APPROVED.value, to_iso(utcnow()), approved_by, brief.brief_id),
        )
        return True

    def set_status(self, brief_id: str, status: BriefStatus) -> None:
        self.conn.execute(
            "UPDATE content_briefs SET status = ? WHERE brief_id = ?",
            (status.value, brief_id),
        )

    def approved(self, limit: int = 100) -> list[ContentBrief]:
        """Production reads only this. Nothing else is eligible."""
        rows = self.conn.execute(
            "SELECT * FROM content_briefs WHERE status = ? "
            "ORDER BY priority ASC, COALESCE(scheduled_date, created_at) ASC LIMIT ?",
            (BriefStatus.APPROVED.value, limit),
        ).fetchall()
        return [self._hydrate(r) for r in rows]

    def backlog(self, status: str | None = None, limit: int = 200) -> list[dict[str, Any]]:
        """The backlog view: the workflow-facing columns of every brief."""
        sql = (
            "SELECT brief_id, topic, content_format, brand_pillar, status, priority, "
            "urgency, scheduled_date, created_at, approved_at, published_at "
            "FROM content_briefs"
        )
        params: tuple[Any, ...] = ()
        if status:
            sql += " WHERE status = ?"
            params = (status,)
        sql += " ORDER BY priority ASC, created_at DESC LIMIT ?"
        return [dict(r) for r in self.conn.execute(sql, params + (limit,))]

    def counts_by_status(self) -> dict[str, int]:
        return {
            r["status"]: r["n"]
            for r in self.conn.execute(
                "SELECT status, COUNT(*) AS n FROM content_briefs GROUP BY status"
            )
        }

    @staticmethod
    def _hydrate(row: sqlite3.Row) -> ContentBrief:
        # brief_json is the approved object verbatim; the columns exist for
        # querying. Reading back from JSON means a schema addition never
        # silently drops a field a brief was approved with.
        data = loads(row["brief_json"], {}) or {}
        if data:
            brief = ContentBrief(**data)
            brief.status = BriefStatus(row["status"])
            brief.approved_at = from_iso(row["approved_at"])
            brief.approved_by = row["approved_by"]
            brief.published_at = from_iso(row["published_at"])
            brief.priority = row["priority"] or 3
            return brief
        raise ValueError(f"Brief {row['brief_id']} has no stored JSON.")


class ExecutionPlanRepository:
    """Append-only. Replanning writes a new row so the plan that actually
    produced a piece of content stays recoverable."""

    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn

    def insert(
        self,
        plan: ExecutionPlan,
        *,
        run_id: str | None,
        model: str,
        prompt_version: str,
    ) -> str:
        plan_id = new_id("plan")
        self.conn.execute(
            "INSERT INTO execution_plans (id, brief_id, run_id, format, plan_json, "
            "alternate_format_recommendation, alternate_format_reason, risks_json, "
            "model, prompt_version, created_at) VALUES (?,?,?,?,?,?,?,?,?,?,?)",
            (
                plan_id, plan.brief_id, run_id, plan.format, plan.model_dump_json(),
                plan.alternate_format_recommendation, plan.alternate_format_reason,
                dumps(plan.risks_or_gaps), model, prompt_version, to_iso(utcnow()),
            ),
        )
        return plan_id

    def latest_for_brief(self, brief_id: str) -> ExecutionPlan | None:
        row = self.conn.execute(
            "SELECT plan_json FROM execution_plans WHERE brief_id = ? "
            "ORDER BY created_at DESC LIMIT 1",
            (brief_id,),
        ).fetchone()
        return ExecutionPlan(**loads(row["plan_json"], {})) if row else None


class HookRepository:
    """Every hook considered, human-supplied and agent-generated alike.

    Keeping the rejected variants is the point: correlating hook strategy with
    performance is impossible if only winners survive.
    """

    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn

    def record_set(
        self,
        hook_set: HookSet,
        *,
        brief: ContentBrief,
        content_id: str | None,
        model: str,
        prompt_version: str,
        selected_variant_id: str | None = None,
    ) -> list[str]:
        now = to_iso(utcnow())
        ids: list[str] = []
        selected = selected_variant_id or hook_set.recommended_variant_id

        # The human's own hook points are stored as variants too, so a human
        # hook and an agent hook can be compared on equal terms later.
        for index, point in enumerate(brief.approved_hook_points):
            row_id = new_id("creative")
            self.conn.execute(
                "INSERT INTO hook_variants (id, brief_id, content_id, variant_id, "
                "text, hook_strategy, hook_source, derived_from_point, rationale, "
                "is_selected, model, prompt_version, created_at) "
                "VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
                (
                    row_id, brief.brief_id, content_id, f"human_{index}", point,
                    "human_supplied", "human", None,
                    "Human-approved hook point from the brief.", 0, None, None, now,
                ),
            )
            ids.append(row_id)

        for variant in hook_set.variants:
            row_id = new_id("creative")
            self.conn.execute(
                "INSERT INTO hook_variants (id, brief_id, content_id, variant_id, "
                "text, hook_strategy, hook_source, derived_from_point, rationale, "
                "is_selected, model, prompt_version, created_at) "
                "VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
                (
                    row_id, brief.brief_id, content_id, variant.variant_id,
                    variant.text, variant.hook_strategy, "agent_expanded",
                    variant.derived_from_point, variant.rationale,
                    int(variant.variant_id == selected), model, prompt_version, now,
                ),
            )
            ids.append(row_id)
        return ids

    def attach_content(self, brief_id: str, content_id: str) -> None:
        self.conn.execute(
            "UPDATE hook_variants SET content_id = ? WHERE brief_id = ? "
            "AND content_id IS NULL",
            (content_id, brief_id),
        )

    def for_brief(self, brief_id: str) -> list[sqlite3.Row]:
        return self.conn.execute(
            "SELECT * FROM hook_variants WHERE brief_id = ? ORDER BY hook_source, "
            "variant_id",
            (brief_id,),
        ).fetchall()

    def selected(self, brief_id: str) -> sqlite3.Row | None:
        return self.conn.execute(
            "SELECT * FROM hook_variants WHERE brief_id = ? AND is_selected = 1 LIMIT 1",
            (brief_id,),
        ).fetchone()
