"""Unattended runner: a per-user launchd LaunchAgent that drains the job queue.

* ``runner`` loop: recover orphaned jobs, claim the oldest queued job, run it in a child process
  wrapped in ``caffeinate -i -s`` (no idle sleep, no system sleep on AC power, only while a job runs),
  record the result, notify, refresh the status page; idle -> poll and refresh periodically.
* ``install-runner`` writes ~/Library/LaunchAgents/com.contentos.runner.plist (RunAtLoad, KeepAlive)
  and bootstraps it into the gui/<uid> domain; logs go to ~/Library/Logs/content_os/.
"""

from __future__ import annotations

import json
import os
import plistlib
import signal
import subprocess
import sys
import time
import uuid
from pathlib import Path
from typing import Any

from . import engine, jobs, notify, settings, status_page
from .state import now

_STOP = False


def _label() -> str:
    return settings.load()["runner"]["label"]


def plist_path() -> Path:
    return Path.home() / "Library" / "LaunchAgents" / f"{_label()}.plist"


def _heartbeat(state: str, job: int | None = None) -> None:
    p = settings.paths().state_dir / "runner_heartbeat.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps({"pid": os.getpid(), "state": state, "job": job, "at": now()}))


def _log(msg: str) -> None:
    print(f"{now()} {msg}", flush=True)


# --------------------------------------------------------------------------- job execution (child)
def exec_job(job_id: int) -> int:
    job = jobs.get(job_id)
    if job is None:
        print(f"no job {job_id}", file=sys.stderr)
        return 1
    args = json.loads(job["args"] or "{}")
    kind, reel = job["kind"], job["reel"]
    try:
        if kind == "advance":
            res = engine.advance(reel, until=args.get("until"))
            status = {"waiting": "paused", "failed": "failed"}.get(res["stopped"], "done")
            jobs.finish(job_id, status, res, res.get("error"))
            if status == "done":
                notify.send(f"{reel}: done", f"ran {', '.join(res['ran']) or 'nothing new'}")
        elif kind == "status_refresh":
            path = status_page.write()
            jobs.finish(job_id, "done", {"status_page": str(path)})
        elif kind == "heartbeat":
            from . import modelcall

            nonce = uuid.uuid4().hex[:8]
            out, prov = modelcall.call("heartbeat", f"nonce: {nonce}", modelcall.HeartbeatOut)
            ok = out.ok and out.nonce == nonce
            result = {"ok": ok, "nonce": nonce, "echo": out.nonce, **{k: prov.get(k) for k in (
                "backend", "model", "served_model", "prompt_version", "cost_usd", "seconds", "trace_id")}}
            jobs.finish(job_id, "done" if ok else "failed", result, None if ok else "nonce mismatch")
            notify.send("Runner heartbeat", f"model call {'ok' if ok else 'FAILED'} via {prov.get('backend')}")
        elif kind == "av_review":
            from . import av_review
            from .state import Reel

            if args.get("file"):
                res = av_review.review(Path(args["file"]), Path(args.get("out") or settings.paths().state_dir / "av_review"))
            else:
                r = Reel.load(reel)
                from .stages import final_mp4
                res = av_review.review(final_mp4(r), r.dir)
            st = "done" if not str(res.get("status", "")).startswith("error") else "failed"
            jobs.finish(job_id, st, {k: v for k, v in res.items() if k != "raw"}, res.get("error"))
            notify.send("A/V review", f"{reel or args.get('file')}: {res.get('status')}")
        elif kind == "pipeline_steps":
            import subprocess

            done = []
            for st in jobs.validate_steps(args.get("steps")):
                p = subprocess.run([sys.executable, "-m", *st], cwd=str(settings.PROJECT_ROOT),
                                   capture_output=True, text=True)
                tail = (p.stdout + p.stderr).strip().splitlines()[-6:]
                done.append({"step": st, "rc": p.returncode, "tail": tail})
                if p.returncode != 0:
                    jobs.finish(job_id, "failed", {"steps": done}, f"step failed: {' '.join(st[:2])}")
                    notify.send(f"Job {job_id} failed", f"{' '.join(st[:2])}: {tail[-1] if tail else ''}"[:200])
                    return 1
            jobs.finish(job_id, "done", {"steps": done})
            notify.send(f"Job {job_id} done", f"{len(done)} pipeline steps finished")
        else:
            jobs.finish(job_id, "failed", error=f"unknown kind {kind}")
            return 1
    except Exception as exc:  # noqa: BLE001
        jobs.finish(job_id, "failed", error=f"{type(exc).__name__}: {exc}")
        notify.send(f"Job {job_id} failed", f"{kind} {reel or ''}: {exc}"[:200])
        return 1
    return 0


# --------------------------------------------------------------------------- loop (parent)
def _child_cmd(job_id: int) -> list[str]:
    cmd = [sys.executable, "-m", "content_os.orchestrator", "_exec-job", str(job_id)]
    flags = settings.load()["runner"].get("caffeinate_flags", ["-i", "-s"])
    if Path("/usr/bin/caffeinate").exists():
        return ["/usr/bin/caffeinate", *flags, *cmd]
    return cmd


def run_one(job: dict[str, Any]) -> str:
    timeout = settings.load()["runner"]["job_timeout_seconds"]
    cmd = _child_cmd(job["id"])
    _log(f"job {job['id']} {job['kind']} {job['reel'] or ''}: {' '.join(cmd[:4])} ...")
    _heartbeat("running", job["id"])
    try:
        proc = subprocess.run(cmd, cwd=settings.PROJECT_ROOT, timeout=timeout, capture_output=True, text=True)
        if proc.stdout.strip():
            _log(proc.stdout.strip()[-2000:])
        if proc.stderr.strip():
            _log("stderr: " + proc.stderr.strip()[-2000:])
    except subprocess.TimeoutExpired:
        jobs.finish(job["id"], "failed", error=f"timed out after {timeout}s")
        notify.send(f"Job {job['id']} timed out", f"{job['kind']} {job['reel'] or ''}")
    final = jobs.get(job["id"]) or {}
    if final.get("status") == "running":  # child died without recording
        jobs.finish(job["id"], "failed", error="job process exited without a result")
        final = jobs.get(job["id"]) or {}
    _log(f"job {job['id']} -> {final.get('status')} {final.get('error') or ''}")
    return final.get("status", "?")


def loop(once: bool = False) -> int:
    def _stop(*_: Any) -> None:
        global _STOP
        _STOP = True

    signal.signal(signal.SIGTERM, _stop)
    signal.signal(signal.SIGINT, _stop)
    cfg = settings.load()["runner"]
    n = jobs.recover_orphans()
    _log(f"runner started pid={os.getpid()} python={sys.executable} cwd={os.getcwd()} recovered={n}")
    last_page = 0.0
    while not _STOP:
        job = jobs.claim()
        if job:
            run_one(job)
            _safe_page()
            last_page = time.time()
            continue
        _heartbeat("idle")
        if time.time() - last_page > cfg["status_refresh_seconds"]:
            _safe_page()
            last_page = time.time()
        if once:
            break
        for _ in range(int(cfg["poll_seconds"])):
            if _STOP:
                break
            time.sleep(1)
    _heartbeat("stopped")
    _log("runner stopped")
    return 0


def _safe_page() -> None:
    try:
        status_page.write()
    except Exception as exc:  # noqa: BLE001
        _log(f"status page failed: {exc}")


# --------------------------------------------------------------------------- launchd
def plist_dict() -> dict[str, Any]:
    p = settings.paths()
    path_env = os.pathsep.join([*settings.tool_path(), "/usr/bin", "/bin", "/usr/sbin", "/sbin"])
    return {
        "Label": _label(),
        "ProgramArguments": [sys.executable, "-m", "content_os.orchestrator", "runner"],
        "WorkingDirectory": str(settings.PROJECT_ROOT),
        "RunAtLoad": True,
        "KeepAlive": True,
        "ThrottleInterval": 30,
        "ProcessType": "Background",
        "StandardOutPath": str(p.logs_dir / "runner.log"),
        "StandardErrorPath": str(p.logs_dir / "runner.err.log"),
        "EnvironmentVariables": {"PATH": path_env, "PYTHONUNBUFFERED": "1", "HOME": str(Path.home()),
                                 "LANG": "en_US.UTF-8"},
    }


def _domain() -> str:
    return f"gui/{os.getuid()}"


def install() -> dict[str, Any]:
    p = settings.paths()
    p.logs_dir.mkdir(parents=True, exist_ok=True)
    p.state_dir.mkdir(parents=True, exist_ok=True)
    dest = plist_path()
    dest.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(["launchctl", "bootout", f"{_domain()}/{_label()}"], capture_output=True)
    with open(dest, "wb") as fh:
        plistlib.dump(plist_dict(), fh)
    boot = subprocess.run(["launchctl", "bootstrap", _domain(), str(dest)], capture_output=True, text=True)
    subprocess.run(["launchctl", "enable", f"{_domain()}/{_label()}"], capture_output=True)
    return {"plist": str(dest), "bootstrap_rc": boot.returncode, "bootstrap_err": boot.stderr.strip(),
            "status": status()}


def uninstall() -> dict[str, Any]:
    out = subprocess.run(["launchctl", "bootout", f"{_domain()}/{_label()}"], capture_output=True, text=True)
    existed = plist_path().exists()
    if existed:
        plist_path().unlink()
    return {"bootout_rc": out.returncode, "removed_plist": existed}


def status() -> dict[str, Any]:
    out = subprocess.run(["launchctl", "print", f"{_domain()}/{_label()}"], capture_output=True, text=True)
    info: dict[str, Any] = {"loaded": out.returncode == 0, "plist": str(plist_path()),
                            "plist_exists": plist_path().exists()}
    for line in out.stdout.splitlines():
        line = line.strip()
        for key in ("state", "pid", "last exit code", "runs"):
            if line.startswith(f"{key} ="):
                info[key.replace(" ", "_")] = line.split("=", 1)[1].strip()
    info["heartbeat"] = status_page.heartbeat()
    try:
        info["queue"] = jobs.counts()
    except Exception as exc:  # noqa: BLE001
        info["queue"] = f"error: {exc}"
    log = settings.paths().logs_dir / "runner.log"
    if log.exists():
        info["log_tail"] = log.read_text(errors="replace").splitlines()[-8:]
    err = settings.paths().logs_dir / "runner.err.log"
    if err.exists() and err.stat().st_size:
        info["err_tail"] = err.read_text(errors="replace").splitlines()[-5:]
    return info
