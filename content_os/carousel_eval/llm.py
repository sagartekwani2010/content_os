"""Model calls for evaluation, logged with cost. Two backends:

  api  the official Anthropic SDK; used when ANTHROPIC_API_KEY is set in the environment. Billed to the API account,
       not the creator's Claude Code limit. The key is read from the environment only and is never written to a file.
  cli  the local `claude -p` (the creator's Claude Code login); used otherwise.

Override with CAROUSEL_EVAL_BACKEND=api|cli. Deliberately independent of content_os.factory and content_os.carousel,
so production-side edits cannot alter it.
"""
from __future__ import annotations

import base64
import json
import os
import re
import subprocess
import time
from pathlib import Path

FABLE = "claude-fable-5-2"
OPUS = "claude-opus-5-5"
PRICE = {FABLE: (8.0, 40.0), OPUS: (4.0, 20.0)}          # $ per 1M input / output tokens
FALLBACK_BETA = "server-side-fallback-2026-07-01"


def backend() -> str:
    forced = os.environ.get("CAROUSEL_EVAL_BACKEND")
    if forced in ("api", "cli"):
        return forced
    return "api" if os.environ.get("ANTHROPIC_API_KEY") else "cli"


def _log(ledger: Path, row: dict) -> None:
    ledger.parent.mkdir(parents=True, exist_ok=True)
    with ledger.open("a") as f:
        f.write(json.dumps({"at": time.strftime("%Y-%m-%dT%H:%M:%S"), **row}) + "\n")


def _api(model: str, prompt: str, images: list[Path]) -> tuple[str, float | None]:
    import anthropic

    client = anthropic.Anthropic()                     # key from ANTHROPIC_API_KEY
    content: list[dict] = []
    for p in images:
        media = "image/png" if p.suffix.lower() == ".png" else "image/jpeg"
        content.append({"type": "image", "source": {"type": "base64", "media_type": media,
                                                     "data": base64.standard_b64encode(p.read_bytes()).decode()}})
    content.append({"type": "text", "text": prompt})
    with client.beta.messages.stream(
        model=model, max_tokens=32000, betas=[FALLBACK_BETA], fallbacks=[{"model": "claude-opus-4-8"}],
        output_config={"effort": "high"}, messages=[{"role": "user", "content": content}],
    ) as stream:
        msg = stream.get_final_message()
    if msg.stop_reason == "refusal":
        raise RuntimeError(f"{model} refused the evaluation request")
    text = "".join(b.text for b in msg.content if b.type == "text")
    pin, pout = PRICE.get(model, (0.0, 0.0))
    cost = (msg.usage.input_tokens * pin + msg.usage.output_tokens * pout) / 1e6
    return text, round(cost, 4)


def _cli(model: str, prompt: str, images: list[Path], cwd: Path | None, timeout: int) -> tuple[str, float | None]:
    tools = ""
    if images:
        tools = "Read"
        prompt = "Use the Read tool to look at these images first:\n" + "\n".join(map(str, images)) + "\n\n" + prompt
    cmd = ["claude", "-p", "--model", model, "--output-format", "json", "--tools", tools]
    r = subprocess.run(cmd, input=prompt, capture_output=True, text=True, timeout=timeout, cwd=cwd)
    if r.returncode != 0:
        raise RuntimeError(f"claude {model} failed: {r.stderr[-400:]}")
    try:
        data = json.loads(r.stdout)
        return data.get("result", ""), data.get("total_cost_usd")
    except json.JSONDecodeError:
        return r.stdout, None


def ask(model: str, prompt: str, *, role: str, ledger: Path, images: list[Path] | None = None,
        cwd: Path | None = None, timeout: int = 900) -> str:
    images = [p for p in (images or []) if p.exists()]
    be, t0 = backend(), time.time()
    try:
        text, cost = _api(model, prompt, images) if be == "api" else _cli(model, prompt, images, cwd, timeout)
    except Exception as e:
        _log(ledger, {"role": role, "model": model, "backend": be, "ok": False, "error": str(e)[:300],
                      "seconds": round(time.time() - t0, 1)})
        raise
    _log(ledger, {"role": role, "model": model, "backend": be, "ok": True, "cost_usd": cost,
                  "seconds": round(time.time() - t0, 1)})
    return text


def parse_json(text: str) -> dict:
    m = re.search(r"\{.*\}", text, re.S)
    if not m:
        raise ValueError(f"no JSON object in reply: {text[:200]!r}")
    return json.loads(m.group(0))
