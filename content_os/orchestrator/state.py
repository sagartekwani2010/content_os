"""Per-reel compact state, append-only ledger and content-hashed versions.

outputs/<reel-id>/
  state.json             current compact state (what a fresh session or the runner reads)
  ledger.jsonl           append-only decision trail: runs, approvals, invalidations, feedback, plans
  versions/<stage>/<v>/  immutable copies of every text output version (never deleted)
  idea.md brief.md SCRIPT.md beats.json SHOOT_PLAN.md TELEPROMPTER.md POST.md ...   current artifacts
Media (footage, audio, renders, pipeline work/) lives in <media_root>/<reel-id>/ outside the repo;
the ledger records only its hashes and paths.
"""

from __future__ import annotations

import fcntl
import hashlib
import json
import os
import shutil
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator

from . import graph
from .settings import paths, tilde

SCHEMA = "content_os.orchestrator/state@1"
TEXT_SUFFIXES = {".md", ".json", ".yaml", ".yml", ".txt", ".html", ".srt", ".ass", ".csv"}


def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for block in iter(lambda: fh.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def sha256_json(obj: Any) -> str:
    return sha256_bytes(json.dumps(obj, sort_keys=True, separators=(",", ":"), default=str).encode())


def short(h: str | None) -> str:
    return (h or "")[:12]


class ReelError(RuntimeError):
    pass


class Reel:
    def __init__(self, reel_id: str) -> None:
        self.id = reel_id
        p = paths()
        self.dir = p.reel_dir(reel_id)
        self.media = p.media_dir(reel_id)
        self.state_file = self.dir / "state.json"
        self.ledger_file = self.dir / "ledger.jsonl"
        self.versions_dir = self.dir / "versions"
        self._state: dict[str, Any] | None = None

    # ---------------------------------------------------------------- lifecycle
    @classmethod
    def create(cls, reel_id: str, idea: str) -> "Reel":
        reel = cls(reel_id)
        if reel.state_file.exists():
            raise ReelError(f"reel {reel_id} already exists at {reel.dir}")
        reel.dir.mkdir(parents=True, exist_ok=True)
        reel.media.mkdir(parents=True, exist_ok=True)
        reel._state = {"schema": SCHEMA, "reel_id": reel_id, "idea": idea, "created_at": now(),
                       "media_dir": tilde(reel.media), "stages": {}, "approvals": {},
                       "waiting": None, "last_error": None, "feedback_count": 0}
        reel.save()
        reel.log("created", idea=idea, media_dir=tilde(reel.media))
        return reel

    @classmethod
    def load(cls, reel_id: str) -> "Reel":
        reel = cls(reel_id)
        if not reel.state_file.exists():
            raise ReelError(f"no orchestrated reel {reel_id!r} (missing {reel.state_file}); "
                            "start one with `new` or `adopt`")
        return reel

    @classmethod
    def all(cls) -> list["Reel"]:
        root = paths().outputs_root
        if not root.is_dir():
            return []
        return [cls(p.parent.name) for p in sorted(root.glob("*/state.json"))]

    @property
    def state(self) -> dict[str, Any]:
        if self._state is None:
            self._state = json.loads(self.state_file.read_text(encoding="utf-8"))
        return self._state

    def reload(self) -> None:
        self._state = None

    def save(self) -> None:
        tmp = self.state_file.with_suffix(".json.tmp")
        tmp.write_text(json.dumps(self.state, indent=2, sort_keys=False) + "\n", encoding="utf-8")
        os.replace(tmp, self.state_file)

    @contextmanager
    def lock(self) -> Iterator[None]:
        """Exclusive per-reel lock so the runner and an interactive command never interleave."""
        p = paths().state_dir / "locks"
        p.mkdir(parents=True, exist_ok=True)
        with open(p / f"{self.id}.lock", "w") as fh:
            fcntl.flock(fh, fcntl.LOCK_EX)
            try:
                self.reload()
                yield
            finally:
                fcntl.flock(fh, fcntl.LOCK_UN)

    # ---------------------------------------------------------------- ledger
    def log(self, event: str, **data: Any) -> dict[str, Any]:
        rec = {"ts": now(), "event": event, **data}
        with open(self.ledger_file, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(rec, sort_keys=False, default=str) + "\n")
        return rec

    def ledger(self) -> list[dict[str, Any]]:
        if not self.ledger_file.exists():
            return []
        return [json.loads(l) for l in self.ledger_file.read_text(encoding="utf-8").splitlines() if l.strip()]

    # ---------------------------------------------------------------- stage records
    def stage(self, name: str) -> dict[str, Any]:
        return self.state["stages"].get(name) or {}

    def version(self, name: str) -> str | None:
        """Current version of a node. Gate nodes are versioned by the approval they hold."""
        n = graph.node(name)
        if n.kind == "gate":
            target = self.stage(n.approves)
            if target.get("status") == "skipped" and not target.get("stale") and self.is_fresh(n.approves):
                # Nothing to approve (e.g. an adopted reel that predates briefs): pass through.
                return sha256_json({"gate": n.gate, "skipped": target.get("version")})
            appr = self.state["approvals"].get(n.gate)
            if appr and appr.get("version") == self.version(n.approves) and appr.get("version"):
                return sha256_json({"gate": n.gate, "approved": appr["version"]})
            return None
        rec = self.stage(name)
        return rec.get("version") if rec.get("status") in ("done", "skipped") else None

    def current_inputs(self, name: str) -> dict[str, str | None]:
        return {d: self.version(d) for d in graph.deps(name)}

    def is_fresh(self, name: str) -> bool:
        n = graph.node(name)
        if n.kind == "gate":
            return self.version(name) is not None
        rec = self.stage(name)
        if rec.get("status") not in ("done", "skipped") or rec.get("stale"):
            return False
        return rec.get("inputs") == self.current_inputs(name)

    def snapshot_outputs(self, name: str, files: dict[str, Path]) -> dict[str, str]:
        """Hash output files; copy text outputs into versions/<stage>/<v>/ (immutable)."""
        hashes = {rel: sha256_file(p) for rel, p in sorted(files.items()) if p.exists()}
        return hashes

    def record_run(self, name: str, *, files: dict[str, Path], provenance: dict[str, Any],
                   status: str = "done", result: dict[str, Any] | None = None, note: str = "") -> str:
        outputs = self.snapshot_outputs(name, files)
        version = sha256_json({"stage": name, "outputs": outputs, "result": result or {}})
        vdir = self.versions_dir / name / short(version)
        if not vdir.exists():
            vdir.mkdir(parents=True)
            for rel, p in files.items():
                if p.exists() and p.suffix.lower() in TEXT_SUFFIXES and _inside(p, self.dir):
                    dest = vdir / rel
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(p, dest)
            (vdir / "provenance.json").write_text(json.dumps(
                {"stage": name, "version": version, "inputs": self.current_inputs(name),
                 "outputs": outputs, "provenance": provenance, "result": result or {}},
                indent=2, default=str) + "\n")
        prev = self.stage(name)
        history = list(prev.get("history", []))
        if prev.get("version") and prev.get("version") != version:
            history.append({"version": prev["version"], "ran_at": prev.get("ran_at"),
                            "stale": prev.get("stale")})
        self.state["stages"][name] = {
            "status": status, "version": version, "inputs": self.current_inputs(name),
            "outputs": {rel: short(h) for rel, h in outputs.items()},
            "ran_at": now(), "provenance": provenance, "result": result or {}, "note": note,
            "stale": None, "history": history[-20:],
        }
        if self.state.get("last_error", {}) and (self.state["last_error"] or {}).get("stage") == name:
            self.state["last_error"] = None
        self.save()
        self.log("stage_run", stage=name, status=status, version=short(version),
                 previous=short(prev.get("version")), changed=prev.get("version") != version,
                 inputs={k: short(v) for k, v in self.current_inputs(name).items()},
                 outputs={k: short(v) for k, v in outputs.items()},
                 model=provenance.get("model"), prompt_version=provenance.get("prompt_version"),
                 config=short(provenance.get("config_hash")), note=note)
        return version

    def record_failure(self, name: str, error: str) -> None:
        self.state["last_error"] = {"stage": name, "error": error[:2000], "at": now()}
        rec = self.state["stages"].setdefault(name, {})
        rec["last_failure"] = {"error": error[:500], "at": now()}
        self.save()
        self.log("stage_failed", stage=name, error=error[:1000])

    def set_waiting(self, waiting: dict[str, Any] | None) -> None:
        if self.state.get("waiting") != waiting:
            self.state["waiting"] = waiting
            self.save()


def _inside(p: Path, root: Path) -> bool:
    try:
        p.resolve().relative_to(root.resolve())
        return True
    except ValueError:
        return False
