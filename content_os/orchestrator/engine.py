"""Advance a reel through the stage graph, compute status, record approvals, adopt existing reels."""

from __future__ import annotations

import getpass
import re
import subprocess
import sys
from typing import Any

from . import graph, notify, settings, stages
from .settings import tilde
from .state import Reel, ReelError, now, sha256_json, short


# --------------------------------------------------------------------------- status
def node_states(reel: Reel) -> list[dict[str, Any]]:
    """Per node: done | skipped | stale | waiting | ready | failed | pending."""
    out, frontier = [], None
    for name in graph.ORDER:
        n = graph.node(name)
        rec = reel.stage(name)
        if reel.is_fresh(name):
            st = "skipped" if rec.get("status") == "skipped" or (n.kind == "gate" and _gate_skipped(reel, n)) else "done"
        elif frontier is None:
            frontier = name
            if n.kind in ("gate", "creator"):
                st = "waiting"
            elif rec.get("last_failure") and (reel.state.get("last_error") or {}).get("stage") == name:
                st = "failed"
            else:
                st = "ready"
        else:
            st = "stale" if (rec.get("version") or (n.kind == "gate" and n.gate in reel.state.get("invalidated", {}))) else "pending"
        out.append({"name": name, "kind": n.kind, "title": n.title, "state": st,
                    "version": short(reel.version(name) or rec.get("version")),
                    "stale": rec.get("stale"), "gate": n.gate})
    return out


def _gate_skipped(reel: Reel, n: graph.Node) -> bool:
    return reel.stage(n.approves).get("status") == "skipped"


def frontier(reel: Reel) -> dict[str, Any] | None:
    return next((s for s in node_states(reel) if s["state"] not in ("done", "skipped")), None)


def next_action(reel: Reel) -> str:
    f = frontier(reel)
    if f is None:
        return "complete"
    n = graph.node(f["name"])
    rid = reel.id
    if n.kind == "gate":
        what = {"brief": f"read outputs/{rid}/brief.md",
                "script": f"read outputs/{rid}/SCRIPT.md (with SCRIPT_CHECK.md)",
                "moodboard": f"open outputs/{rid}/MOODBOARD.html (keyframes, palette, sound, shot list)",
                "cut_review": f"open {tilde(reel.media)}/work/cut_review.html and listen to every cut",
                "final_listen": f"listen to {tilde(stages.final_mp4(reel))} (and outputs/{rid}/av_review.md)",
                "posting": f"post by hand using outputs/{rid}/POST.md"}[n.gate]
        return f"CREATOR: {what}, then `approve {rid} {n.gate}` (or `feedback {rid} \"...\"`)"
    if n.kind == "creator":
        if n.gate == "recorded":
            return (f"CREATOR: record the beats from outputs/{rid}/TELEPROMPTER.md into {tilde(reel.media)}/raw/, "
                    f"then `approve {rid} recorded`")
        return f"CREATOR: after 48 h, `perf {rid} views=... saves=...` or `feedback {rid} \"...\"`"
    if f["state"] == "failed":
        return f"FIX: {f['name']} failed: {(reel.state.get('last_error') or {}).get('error', '')[:160]} ; then `run {rid}`"
    return f"RUNNER: `run {rid}` will run {f['name']} ({n.kind})"


# --------------------------------------------------------------------------- advance
def advance(reel_id: str, until: str | None = None, *, notify_creator: bool = True) -> dict[str, Any]:
    """Run every runnable stage in order until a creator gate/action, a failure, or ``until``."""
    if until:
        graph.node(until)
    reel = Reel.load(reel_id)
    ran: list[str] = []
    with reel.lock():
        for name in graph.ORDER:
            if reel.is_fresh(name):
                if name == until:
                    break
                continue
            n = graph.node(name)
            if n.kind in ("gate", "creator"):
                waiting = {"node": name, "gate": n.gate, "since": now(), "action": next_action(reel)}
                if (reel.state.get("waiting") or {}).get("node") != name:
                    reel.log("waiting", node=name, gate=n.gate)
                    if notify_creator:
                        notify.send(f"{reel.id}: needs you", f"{n.title}. {next_action(reel)[:180]}")
                reel.set_waiting(waiting)
                return {"reel": reel.id, "ran": ran, "stopped": "waiting", "node": name}
            reel.set_waiting({"node": name, "running": True, "since": now()})
            try:
                res = stages.run_node(reel, name)
            except Exception as exc:  # noqa: BLE001 - every failure is recorded and surfaced
                msg = f"{type(exc).__name__}: {exc}"
                reel.record_failure(name, msg)
                reel.set_waiting(None)
                if notify_creator:
                    notify.send(f"{reel.id}: {name} failed", msg[:200])
                return {"reel": reel.id, "ran": ran, "stopped": "failed", "node": name, "error": msg}
            prov = {**res.provenance, "orchestrator_config": sha256_json(settings.load())[:12]}
            before = reel.stage(name).get("version")
            after = reel.record_run(name, files=res.files, provenance=prov, status=res.status,
                                    result=res.result, note=res.note)
            _resolve_feedback(reel, name, changed=before != after, notify_creator=notify_creator)
            ran.append(name)
            if name == until:
                break
        reel.set_waiting(None)
    return {"reel": reel.id, "ran": ran, "stopped": "until" if until else "complete", "node": until}


def _resolve_feedback(reel: Reel, name: str, *, changed: bool = True, notify_creator: bool = True) -> None:
    """Feedback routed to a stage is addressed only when the re-run changed its output. A deterministic
    stage (cutpoints, render) re-run with unchanged inputs gives the same version: the feedback stays
    open and the creator is told a manual change is needed (pipeline.yaml override, take select, edit)."""
    dirty = False
    for f in reel.state.get("feedback", []):
        if f.get("stage") != name or f.get("resolved_in"):
            continue
        if changed:
            f["resolved_in"] = short(reel.stage(name).get("version"))
            reel.log("feedback_addressed", feedback=f["id"], stage=name, version=f["resolved_in"])
        else:
            f["needs_manual_change"] = True
            reel.log("feedback_not_addressed", feedback=f["id"], stage=name,
                     reason="re-run produced identical output; change an input (pipeline.yaml override, "
                            "`content_os.pipeline select`, beats/cue sheet) and run again")
            if notify_creator:
                notify.send(f"{reel.id}: {name} unchanged", f"Feedback {f['id']} needs a manual change")
        dirty = True
    if dirty:
        reel.save()


# --------------------------------------------------------------------------- approvals
def approve(reel_id: str, gate: str, by: str | None = None, note: str = "") -> dict[str, Any]:
    by = by or getpass.getuser()
    if gate not in graph.GATE_NODES:
        raise ReelError(f"unknown gate {gate!r}; known: {', '.join(graph.GATE_NODES)}")
    reel = Reel.load(reel_id)
    name = graph.GATE_NODES[gate]
    n = graph.node(name)
    with reel.lock():
        idx = graph.index(name)
        blockers = [x for x in graph.ORDER[:idx] if not reel.is_fresh(x)]
        if blockers:
            raise ReelError(f"cannot approve {gate}: earlier stages are not done/fresh: {', '.join(blockers)}")
        if n.kind == "creator":
            return _record_creator(reel, n, by, note)
        version = reel.version(n.approves)
        if gate == "cut_review":
            _pipeline_approve(reel, by, note)
        prev = reel.state["approvals"].get(gate)
        if prev:
            reel.state.setdefault("approvals_history", []).append({**prev, "gate": gate, "superseded_at": now()})
        rec = {"version": version, "by": by, "note": note, "at": now()}
        reel.state["approvals"][gate] = rec
        reel.state.get("invalidated", {}).pop(gate, None)
        reel.save()
        reel.log("approval", gate=gate, version=short(version), by=by, note=note)
        if gate == "posting":
            reel.log("posted_by_creator", url=note)
    return {"gate": gate, "version": short(version), "by": by}


def _record_creator(reel: Reel, n: graph.Node, by: str, note: str) -> dict[str, Any]:
    if n.gate == "recorded":
        manifest = stages.raw_manifest(reel)
        if not manifest:
            raise ReelError(f"no footage in {tilde(reel.media)}/raw/ (*.MOV, *.mp4); record first")
        version = reel.record_run("record", files={}, provenance={"kind": "creator", "by": by},
                                  result={"raw": manifest}, note=note)
    else:
        perf = reel.dir / "performance.json"
        files = {"performance.json": perf} if perf.exists() else {}
        version = reel.record_run(n.name, files=files, provenance={"kind": "creator", "by": by}, note=note)
    reel.log("approval", gate=n.gate, version=short(version), by=by, note=note)
    return {"gate": n.gate, "version": short(version), "by": by}


def _pipeline_approve(reel: Reel, by: str, note: str) -> None:
    proc = subprocess.run([sys.executable, "-m", "content_os.pipeline", "approve", str(reel.media),
                           "cut_review", "--by", by, "--note", note], cwd=settings.PROJECT_ROOT,
                          env=stages.pipeline_env(), capture_output=True, text=True)
    if proc.returncode != 0:
        raise ReelError(f"pipeline approve failed: {(proc.stderr or proc.stdout).strip()[-400:]}")


# --------------------------------------------------------------------------- new / adopt
def slugify(text: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return "-".join(s.split("-")[:6]) or "reel"


def new(idea: str, reel_id: str | None = None) -> Reel:
    reel_id = reel_id or slugify(idea)
    reel = Reel.create(reel_id, idea)
    return reel


def adopt(reel_id: str) -> Reel:
    """Bring an existing outputs/<reel-id>/ (SCRIPT.md, SHOOT_PLAN.md, TELEPROMPTER.md) under the
    orchestrator without inventing approvals: brief is marked skipped (it predates briefs), the script
    is recorded as the current version and still needs the creator's approval."""
    reel = Reel(reel_id)
    script_md = reel.dir / "SCRIPT.md"
    if not script_md.exists():
        raise ReelError(f"{script_md} not found")
    if reel.state_file.exists():
        raise ReelError(f"{reel_id} is already orchestrated")
    parsed = stages.parse_script_md(script_md.read_text(encoding="utf-8"))
    existing = sorted(p.name for p in reel.dir.iterdir() if p.is_file())
    reel = Reel.create(reel_id, parsed["promise"] or parsed["title"] or reel_id)
    reel.log("adopted", from_files=existing)
    reel.record_run("idea", files={"idea.md": stages.run_idea(reel).files["idea.md"]},
                    provenance={"kind": "adopted"})
    reel.record_run("brief", files={}, provenance={"kind": "adopted"}, status="skipped",
                    note="reel predates orchestrator briefs")
    beats = [{"id": x["id"], "text": x["text"], "section": x["section"]} for x in parsed["beats"]]
    files = {"SCRIPT.md": script_md,
             "beats.json": stages._json(reel.dir / "beats.json", {"reel_id": reel_id,
                                                                   "target_duration_s": parsed["target_duration_s"],
                                                                   "beats": beats}),
             "beat_visuals.json": stages._json(reel.dir / "beat_visuals.json",
                                               {"beats": [{"beat": x["id"], "visual": x["visual"]} for x in parsed["beats"]]})}
    reel.record_run("script", files=files, provenance={"kind": "adopted", "source": "SCRIPT.md"},
                    result={"beats": len(beats)})
    if all((reel.dir / k).exists() for k in ("SHOOT_PLAN.md", "TELEPROMPTER.md")):
        # Keep the hand-written shoot plan while the script is unchanged (see stages.run_shoot_plan).
        reel.state["adopted"] = {"shoot_plan_for_script": reel.stage("script")["version"]}
        reel.save()
    return reel
