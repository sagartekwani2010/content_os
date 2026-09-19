"""SQLite connection handling and schema bootstrap.

Plain sqlite3 rather than an ORM. The schema is roughly ten tables, mostly
insert-only, with one real ranking query. An ORM would add a mapping layer and
migration machinery without buying anything the append-only design needs.
"""

from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator

from content_os.config import db_path

SCHEMA_PATH = Path(__file__).resolve().parent / "schema.sql"


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def to_iso(value: datetime | None) -> str | None:
    if value is None:
        return None
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc).isoformat()


def from_iso(value: str | None) -> datetime | None:
    if not value:
        return None
    dt = datetime.fromisoformat(value)
    return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)


def dumps(value: Any) -> str:
    return json.dumps(value, default=str, ensure_ascii=False)


def loads(value: str | None, default: Any = None) -> Any:
    if not value:
        return default if default is not None else []
    try:
        return json.loads(value)
    except (TypeError, ValueError):
        return default if default is not None else []


def connect(path: str | Path | None = None) -> sqlite3.Connection:
    target = Path(path) if path else db_path()
    if str(target) != ":memory:":
        target.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(target), isolation_level=None)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = WAL")
    return conn


# Columns added after the first release. CREATE TABLE IF NOT EXISTS will not
# add a column to a table that already exists, so an existing database needs
# these applied explicitly.
_MIGRATIONS: dict[str, list[tuple[str, str]]] = {
    "agent_runs": [
        ("reasoning_effort", "TEXT"),
        ("cached_input_tokens", "INTEGER DEFAULT 0"),
        ("cache_write_tokens", "INTEGER DEFAULT 0"),
        ("reasoning_tokens", "INTEGER DEFAULT 0"),
        ("uncached_input_cost", "REAL DEFAULT 0.0"),
        ("cached_input_cost", "REAL DEFAULT 0.0"),
        ("cache_write_cost", "REAL DEFAULT 0.0"),
        ("output_cost", "REAL DEFAULT 0.0"),
        ("pricing_known", "INTEGER DEFAULT 1"),
    ],
    # Human strategy carried from the brief into the published record, so that
    # performance can be correlated with the decisions behind it.
    "content_items": [
        ("brief_id", "TEXT"),
        ("core_thesis", "TEXT"),
        ("learning_objective", "TEXT"),
        ("hook_direction", "TEXT"),
        ("approved_hook_points_json", "TEXT"),
        ("high_level_sections_json", "TEXT"),
        ("preferred_pov", "TEXT"),
        ("visual_direction", "TEXT"),
        ("hook_strategy", "TEXT"),
        ("hook_source", "TEXT"),
        ("hook_variant_id", "TEXT"),
        ("learning_payoff", "TEXT"),
        ("save_reason", "TEXT"),
        ("share_reason", "TEXT"),
        ("sections_covered_json", "TEXT"),
    ],
}


def migrate(conn: sqlite3.Connection) -> list[str]:
    """Add any missing columns. Additive only, never destructive.

    Historical rows keep whatever they recorded; new columns arrive as NULL or
    their default rather than being backfilled with a guess.
    """
    applied: list[str] = []
    for table, columns in _MIGRATIONS.items():
        existing = {
            row["name"] for row in conn.execute(f"PRAGMA table_info({table})")
        }
        if not existing:
            continue
        for name, spec in columns:
            if name not in existing:
                conn.execute(f"ALTER TABLE {table} ADD COLUMN {name} {spec}")
                applied.append(f"{table}.{name}")
    return applied


def init_db(conn: sqlite3.Connection) -> None:
    conn.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))
    migrate(conn)


def get_db(path: str | Path | None = None) -> sqlite3.Connection:
    """Open a connection with the schema applied. Safe to call repeatedly."""
    conn = connect(path)
    init_db(conn)
    return conn


@contextmanager
def transaction(conn: sqlite3.Connection) -> Iterator[sqlite3.Connection]:
    conn.execute("BEGIN")
    try:
        yield conn
    except Exception:
        conn.execute("ROLLBACK")
        raise
    else:
        conn.execute("COMMIT")
