"""Performance ingestion from CSV.

Every row becomes a new immutable snapshot. Re-ingesting the same file is safe:
a snapshot already recorded for that content and timestamp is skipped rather
than updated, so a repeated nightly job cannot corrupt history.
"""

from __future__ import annotations

import csv
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from content_os.ids import new_id
from content_os.models.performance import PostPerformance
from content_os.storage.repositories import Repositories

# Accepts either our own field names or the labels Instagram exports.
ALIASES: dict[str, str] = {
    "content_id": "content_id",
    "creative_id": "creative_id",
    "platform_post_id": "platform_post_id",
    "post_id": "platform_post_id",
    "snapshot_time": "snapshot_time",
    "date": "snapshot_time",
    "followers_at_post_time": "followers_at_post_time",
    "impressions": "impressions",
    "views": "impressions",
    "reach": "reach",
    "accounts_reached": "reach",
    "follower_reach": "follower_reach",
    "non_follower_reach": "non_follower_reach",
    "plays": "plays",
    "avg_watch_time_seconds": "avg_watch_time_seconds",
    "average_watch_time": "avg_watch_time_seconds",
    "total_watch_time_seconds": "total_watch_time_seconds",
    "watch_time": "total_watch_time_seconds",
    "video_duration_seconds": "video_duration_seconds",
    "duration": "video_duration_seconds",
    "likes": "likes",
    "comments": "comments",
    "shares": "shares",
    "sends": "sends",
    "saves": "saves",
    "profile_visits": "profile_visits",
    "new_followers": "new_followers",
    "follows": "new_followers",
    "website_clicks": "website_clicks",
    "organic_impressions": "organic_impressions",
    "paid_impressions": "paid_impressions",
}

INT_FIELDS = {
    "followers_at_post_time", "impressions", "reach", "follower_reach",
    "non_follower_reach", "plays", "likes", "comments", "shares", "sends",
    "saves", "profile_visits", "new_followers", "website_clicks",
    "organic_impressions", "paid_impressions",
}
FLOAT_FIELDS = {
    "avg_watch_time_seconds", "total_watch_time_seconds", "video_duration_seconds",
}


def _parse_time(value: str | None) -> datetime:
    if not value or not value.strip():
        return datetime.now(timezone.utc)
    text = value.strip().replace("Z", "+00:00")
    for parser in (
        lambda v: datetime.fromisoformat(v),
        lambda v: datetime.strptime(v, "%Y-%m-%d"),
        lambda v: datetime.strptime(v, "%d/%m/%Y"),
        lambda v: datetime.strptime(v, "%m/%d/%Y"),
    ):
        try:
            parsed = parser(text)
            return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)
        except ValueError:
            continue
    return datetime.now(timezone.utc)


def _coerce(field: str, value: str | None) -> Any:
    if value is None or str(value).strip() == "":
        return 0 if field in INT_FIELDS else (0.0 if field in FLOAT_FIELDS else None)
    text = str(value).strip().replace(",", "").replace("%", "")
    try:
        if field in INT_FIELDS:
            return int(float(text))
        if field in FLOAT_FIELDS:
            return float(text)
    except ValueError:
        return 0 if field in INT_FIELDS else 0.0
    return text


def ingest_csv(repos: Repositories, path: str | Path) -> dict[str, Any]:
    file_path = Path(path)
    if not file_path.exists():
        return {"error": f"File not found: {file_path}"}

    inserted: list[str] = []
    skipped: list[str] = []
    errors: list[str] = []

    with file_path.open("r", encoding="utf-8-sig", newline="") as fh:
        for line_number, raw in enumerate(csv.DictReader(fh), start=2):
            mapped: dict[str, Any] = {}
            for key, value in raw.items():
                if key is None:
                    continue
                field = ALIASES.get(key.strip().lower().replace(" ", "_"))
                if field:
                    mapped[field] = _coerce(field, value)

            content_id = mapped.get("content_id")
            if not content_id:
                errors.append(f"line {line_number}: missing content_id")
                continue

            row = repos.content.get(str(content_id)) or repos.content.find_by_prefix(
                str(content_id)
            )
            if row is None:
                errors.append(f"line {line_number}: unknown content_id {content_id}")
                continue

            perf = PostPerformance(
                id=new_id("performance"),
                content_id=row["id"],
                creative_id=mapped.get("creative_id") or None,
                platform_post_id=mapped.get("platform_post_id") or row["platform_post_id"],
                snapshot_time=_parse_time(mapped.get("snapshot_time")),
                followers_at_post_time=mapped.get("followers_at_post_time") or None,
                **{
                    k: mapped.get(k, 0)
                    for k in INT_FIELDS | FLOAT_FIELDS
                    if k != "followers_at_post_time"
                },
            )

            try:
                repos.performance.insert(perf)
                inserted.append(perf.id)
            except sqlite3.IntegrityError:
                # Unique index on (content_id, snapshot_time, creative_id).
                # Re-running the same export is a no-op rather than a duplicate.
                skipped.append(f"{row['id']}@{perf.snapshot_time.isoformat()}")

    return {
        "inserted": len(inserted),
        "skipped_duplicates": len(skipped),
        "errors": errors,
        "file": str(file_path),
    }
