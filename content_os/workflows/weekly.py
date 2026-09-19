"""The full weekly cycle: score, plan, and report in one command.

Generation is deliberately not included. A week's plan is reviewed before
anything is written, and writing seven packages unprompted would burn tokens on
content the human may reorder or drop.
"""

from __future__ import annotations

from typing import Any

from content_os.storage.repositories import Repositories
from content_os.workflows.mine import run_mining
from content_os.workflows.plan import run_planning
from content_os.workflows.score import run_scoring


async def run_weekly(
    repos: Repositories,
    *,
    target_posts: int = 7,
    horizon_days: int = 7,
    mine_brand: bool = True,
) -> dict[str, Any]:
    """Mine, score, and plan.

    Brand mining runs first so series episodes and identity content compete for
    slots alongside reactive topics. Without it a week is all commentary and no
    persona, which is the difference between a page and a feed.
    """
    mining = None
    if mine_brand:
        try:
            mining = await run_mining(repos, max_topics=8)
        except Exception as exc:  # noqa: BLE001
            mining = {"error": f"{type(exc).__name__}: {exc}"}

    scoring = await run_scoring(repos)
    planning = await run_planning(
        repos, target_posts=target_posts, horizon_days=horizon_days
    )
    return {"mining": mining, "scoring": scoring, "planning": planning}
