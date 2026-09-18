"""The full weekly cycle: score, plan, and report in one command.

Generation is deliberately not included. A week's plan is reviewed before
anything is written, and writing seven packages unprompted would burn tokens on
content the human may reorder or drop.
"""

from __future__ import annotations

from typing import Any

from content_os.storage.repositories import Repositories
from content_os.workflows.plan import run_planning
from content_os.workflows.score import run_scoring


async def run_weekly(
    repos: Repositories, *, target_posts: int = 7, horizon_days: int = 7
) -> dict[str, Any]:
    scoring = await run_scoring(repos)
    planning = await run_planning(
        repos, target_posts=target_posts, horizon_days=horizon_days
    )
    return {"scoring": scoring, "planning": planning}
