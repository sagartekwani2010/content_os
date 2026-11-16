"""SQLite job queue (<state_dir>/queue.sqlite, outside the repo).

A job only exists because the creator asked for it (new/run --bg/approve/heartbeat); the runner still
re-checks gates before every stage, so a queued job can never run past a missing approval.
Kinds: advance (reel [, until]), status_refresh, heartbeat (cheap model call), av_review (reel).
"""

from __future__ import annotations

import json
import os
import sqlite3
from contextlib import contextmanager
from typing import Any, Iterator

from . import settings
from .state import now

KINDS = ("advance", "status_refresh", "heartbeat", "av_review")
SCHEMA = """
CREATE TABLE IF NOT EXISTS jobs (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  kind TEXT NOT NULL, reel TEXT, args TEXT NOT NULL DEFAULT '{}',
  status TEXT NOT NULL DEFAULT 'queued',      -- queued | running | done | paused | failed | cancelled
  requested_by TEXT, reason TEXT,
  created_at TEXT NOT NULL, started_at TEXT, finished_at TEXT,
  attempts INTEGER NOT NULL DEFAULT 0, runner_pid INTEGER, result TEXT, error TEXT
);
CREATE INDEX IF NOT EXISTS jobs_status ON jobs(status, id);
"""


@contextmanager
def connect() -> Iterator[sqlite3.Connection]:
    db = settings.paths().queue_db
    db.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(db, timeout=30, isolation_level=None)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA journal_mode=WAL")
    con.executescript(SCHEMA)
    try:
        yield con
    finally:
        con.close()


def enqueue(kind: str, reel: str | None = None, args: dict[str, Any] | None = None,
            requested_by: str | None = None, reason: str = "") -> int:
    if kind not in KINDS:
        raise ValueError(f"unknown job kind {kind}; known: {', '.join(KINDS)}")
    with connect() as con:
        row = con.execute("SELECT id FROM jobs WHERE kind=? AND IFNULL(reel,'')=IFNULL(?, '') AND status='queued'",
                          (kind, reel)).fetchone()
        if row:
            return int(row["id"])
        cur = con.execute("INSERT INTO jobs(kind, reel, args, requested_by, reason, created_at) VALUES (?,?,?,?,?,?)",
                          (kind, reel, json.dumps(args or {}), requested_by, reason, now()))
        return int(cur.lastrowid)


def claim(pid: int | None = None) -> dict[str, Any] | None:
    with connect() as con:
        con.execute("BEGIN IMMEDIATE")
        row = con.execute("SELECT * FROM jobs WHERE status='queued' ORDER BY id LIMIT 1").fetchone()
        if row is None:
            con.execute("COMMIT")
            return None
        con.execute("UPDATE jobs SET status='running', started_at=?, attempts=attempts+1, runner_pid=? WHERE id=?",
                    (now(), pid or os.getpid(), row["id"]))
        con.execute("COMMIT")
        return dict(row) | {"status": "running"}


def claim_id(job_id: int) -> bool:
    """Claim one specific queued job (foreground execution)."""
    with connect() as con:
        cur = con.execute("UPDATE jobs SET status='running', started_at=?, attempts=attempts+1, runner_pid=? "
                          "WHERE id=? AND status='queued'", (now(), os.getpid(), job_id))
        return cur.rowcount == 1


def finish(job_id: int, status: str, result: Any = None, error: str | None = None) -> None:
    with connect() as con:
        con.execute("UPDATE jobs SET status=?, finished_at=?, result=?, error=? WHERE id=?",
                    (status, now(), json.dumps(result, default=str) if result is not None else None,
                     (error or "")[:2000] or None, job_id))


def cancel(job_id: int) -> None:
    with connect() as con:
        con.execute("UPDATE jobs SET status='cancelled', finished_at=? WHERE id=? AND status='queued'",
                    (now(), job_id))


def get(job_id: int) -> dict[str, Any] | None:
    with connect() as con:
        row = con.execute("SELECT * FROM jobs WHERE id=?", (job_id,)).fetchone()
        return dict(row) if row else None


def recover_orphans(max_attempts: int = 3) -> int:
    """Jobs left 'running' by a dead runner go back to the queue (or fail after max_attempts)."""
    n = 0
    with connect() as con:
        for row in con.execute("SELECT id, runner_pid, attempts FROM jobs WHERE status='running'").fetchall():
            if row["runner_pid"] and _alive(row["runner_pid"]):
                continue
            new = "queued" if row["attempts"] < max_attempts else "failed"
            con.execute("UPDATE jobs SET status=?, error=IFNULL(error,'') || ? WHERE id=?",
                        (new, " [runner died mid-job; requeued]" if new == "queued" else " [gave up]", row["id"]))
            n += 1
    return n


def _alive(pid: int) -> bool:
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False


def listing(limit: int = 30, statuses: tuple[str, ...] | None = None) -> list[dict[str, Any]]:
    with connect() as con:
        if statuses:
            q = f"SELECT * FROM jobs WHERE status IN ({','.join('?' * len(statuses))}) ORDER BY id DESC LIMIT ?"
            rows = con.execute(q, (*statuses, limit)).fetchall()
        else:
            rows = con.execute("SELECT * FROM jobs ORDER BY id DESC LIMIT ?", (limit,)).fetchall()
        return [dict(r) for r in rows]


def counts() -> dict[str, int]:
    with connect() as con:
        return {r["status"]: r["n"] for r in con.execute("SELECT status, COUNT(*) n FROM jobs GROUP BY status")}
