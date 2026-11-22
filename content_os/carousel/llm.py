"""One model call through the local `claude -p` (no tools), logged with its cost to a ledger.

Used by the carousel steps (real run, drafts, blind judge, fact check). The model id is passed in by the caller
(BRIEF/STATUS record which model did what); the reply text and the cost come from `--output-format json`.
"""
from __future__ import annotations

import json
import subprocess
import time
from pathlib import Path

PLAIN_SYSTEM = "You are a helpful assistant."


def ask(model: str, prompt: str, *, role: str, ledger: Path | None = None, system: str = PLAIN_SYSTEM,
        effort: str | None = None, timeout: int = 1200) -> str:
    cmd = ["claude", "-p", "--model", model, "--tools", "", "--system-prompt", system, "--output-format", "json"]
    if effort:
        cmd += ["--effort", effort]
    t0 = time.time()
    r = subprocess.run(cmd, input=prompt, capture_output=True, text=True, timeout=timeout)
    ok = r.returncode == 0
    try:
        data = json.loads(r.stdout)
    except json.JSONDecodeError:
        data, ok = {}, False
    text = (data.get("result") or "").strip()
    if ledger:
        rec = {"at": time.strftime("%Y-%m-%dT%H:%M:%S"), "role": role, "model": model,
               "seconds": round(time.time() - t0, 1), "chars_in": len(prompt), "chars_out": len(text),
               "cost_usd": round(float(data.get("total_cost_usd") or 0), 4), "ok": ok and bool(text)}
        with Path(ledger).open("a") as f:
            f.write(json.dumps(rec) + "\n")
    if not ok or not text:
        raise RuntimeError(f"{model} failed: {r.stderr[-400:]}")
    return text
