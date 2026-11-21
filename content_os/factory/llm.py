"""Model calls for the script factory: Claude through the local `claude -p`, OpenAI through the Responses API.

Every call is appended to <out>/ledger.jsonl (role, model, seconds, chars, ok) so weekly usage is visible.
"""
from __future__ import annotations

import getpass
import json
import os
import re
import subprocess
import threading
import time
from pathlib import Path
from typing import Any

import yaml

REPO = Path(__file__).resolve().parents[2]
_lock = threading.Lock()


def config() -> dict[str, Any]:
    return yaml.safe_load((REPO / "config" / "factory.yaml").read_text())


def _openai_key() -> str:
    if os.environ.get("OPENAI_API_KEY"):
        return os.environ["OPENAI_API_KEY"]
    return subprocess.run(["security", "find-generic-password", "-s", "content_os_openai", "-a", getpass.getuser(),
                           "-w"], capture_output=True, text=True, check=True).stdout.strip()


def _claude(model: str, prompt: str, effort: str | None, timeout: int) -> str:
    cmd = ["claude", "-p", "--model", model, "--tools", ""]
    if effort:
        cmd += ["--effort", effort]
    r = subprocess.run(cmd, input=prompt, capture_output=True, text=True, timeout=timeout)
    if r.returncode != 0 or not r.stdout.strip():
        raise RuntimeError(f"claude {model} failed: {r.stderr[-500:]}")
    return r.stdout.strip()


def _openai(model: str, prompt: str, effort: str | None, timeout: int) -> str:
    from openai import OpenAI
    client = OpenAI(api_key=_openai_key(), timeout=timeout)
    kw: dict[str, Any] = {"model": model, "input": prompt}
    if effort:
        kw["reasoning"] = {"effort": effort}
    return client.responses.create(**kw).output_text.strip()


def call(role: str, prompt: str, *, ledger: Path | None = None, retries: int = 1) -> str:
    """Run one prompt for a configured role and return the text reply."""
    cfg = config()
    spec = cfg["roles"][role]
    timeout = cfg["tournament"].get("timeout_seconds", 1200)
    fn = _claude if spec["provider"] == "claude" else _openai
    last: Exception | None = None
    for attempt in range(retries + 1):
        t0 = time.time()
        try:
            out = fn(spec["model"], prompt, spec.get("effort"), timeout)
            _log(ledger, role, spec["model"], time.time() - t0, len(prompt), len(out), True)
            return out
        except Exception as e:  # noqa: BLE001 - retried, then raised
            last = e
            _log(ledger, role, spec["model"], time.time() - t0, len(prompt), 0, False, str(e)[:300])
            time.sleep(5 * (attempt + 1))
    raise RuntimeError(f"{role} failed after retries: {last}")


def _log(ledger: Path | None, role: str, model: str, secs: float, cin: int, cout: int, ok: bool,
         err: str = "") -> None:
    if not ledger:
        return
    rec = {"at": time.strftime("%Y-%m-%dT%H:%M:%S"), "role": role, "model": model, "seconds": round(secs, 1),
           "chars_in": cin, "chars_out": cout, "ok": ok, **({"error": err} if err else {})}
    with _lock, ledger.open("a") as f:
        f.write(json.dumps(rec) + "\n")


def parse_json(text: str) -> dict[str, Any]:
    """Pull the first JSON object out of a model reply (tolerates code fences and prose around it)."""
    m = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.S)
    body = m.group(1) if m else text[text.find("{"): text.rfind("}") + 1]
    return json.loads(body)
