"""Real before/after runs for a carousel: every prompt runs N times on the same model, verbatim to runs/.

``runs/tasks.json``::

    {"model": "claude-fable-5-2", "repeats": 2,
     "tasks": [{"id": "t1_context", "technique": "...",
                "before": ["prompt"], "after": ["step 1 prompt", "step 2 uses {prev}"]}]}

A variant is a list of prompts. More than one = a prompt chain: each later prompt is sent as a fresh single-turn
call with ``{prev}`` replaced by the previous step's output (verbatim). Outputs land in
``runs/<task>__<variant>__run<k>.md`` with a header naming the model, date and the exact prompts.
"""
from __future__ import annotations

import json
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from .llm import PLAIN_SYSTEM, ask


def _one(folder: Path, model: str, task: dict, variant: str, k: int, ledger: Path) -> str:
    prompts, prev, steps = task[variant], "", []
    for i, p in enumerate(prompts):
        text = p.replace("{prev}", prev)
        prev = ask(model, text, role=f"run_{task['id']}_{variant}_{k}_s{i + 1}", ledger=ledger)
        steps.append((text, prev))
    out = folder / f"{task['id']}__{variant}__run{k}.md"
    head = (f"<!-- model: {model} via `claude -p --tools \"\" --system-prompt \"{PLAIN_SYSTEM}\"`, "
            f"{time.strftime('%Y-%m-%d %H:%M')} IST, single-turn call per step, default effort. Verbatim. -->\n")
    body = "".join(f"\n## Step {i + 1} prompt\n\n{p}\n\n## Step {i + 1} output\n\n{o}\n" for i, (p, o) in enumerate(steps))
    out.write_text(head + f"# {task['id']} · {variant} · run {k}\n" + body)
    return out.name


def run_all(folder: Path, only: list[str] | None = None, workers: int = 8) -> list[str]:
    folder = Path(folder)
    spec = json.loads((folder / "tasks.json").read_text())
    ledger = folder.parent / "ledger.jsonl"
    jobs = [(t, v, k) for t in spec["tasks"] if not only or t["id"] in only
            for v in ("before", "after") for k in range(1, spec.get("repeats", 2) + 1)]
    with ThreadPoolExecutor(workers) as ex:
        return list(ex.map(lambda j: _one(folder, spec["model"], j[0], j[1], j[2], ledger), jobs))


def final_output(path: Path) -> str:
    """The last step's output from a run file."""
    return Path(path).read_text().rsplit("output\n\n", 1)[-1].strip()
