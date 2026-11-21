"""``python -m content_os.orchestrator <command>``

Creator-facing:
  new "<idea>" [--id ID] [--now]      start a reel; the brief is drafted by the runner (or now)
  adopt <reel-id>                      bring an existing outputs/<reel-id>/ (SCRIPT.md ...) under orchestration
  status [<reel>] [--json]             stage states, versions, pending gates, last error
  next                                 what each reel needs next and who must act
  run [<reel>] [--until STAGE] [--bg]  advance now (foreground) or queue it for the runner
  approve <reel> <gate> [--note]       brief | script | recorded | cut_review | final_listen | posting | performance
  feedback <reel> "<text>"             classify -> mark stale -> invalidate gates -> re-run plan -> candidate lesson
  perf <reel> key=value ...            record post performance (then `approve <reel> performance`)
  log [<reel>] [-n N]                  decision trail from the ledger
  queue [list|cancel ID|add KIND [REEL]]
  memory [list|candidates|approve ID|reject ID|show STAGE]
  av-review <reel> | --file PATH       OpenAI audio/frames review (advisory)
  heartbeat [--bg]                     cheap model call (Haiku-routed) to prove model access
  status-page                          rewrite ~/Movies/ContentOS/status.html
Runner:
  install-runner | uninstall-runner | runner-status | runner [--once]
"""

from __future__ import annotations

import argparse
import getpass
import json
import sys
from pathlib import Path
from typing import Any

from . import backtrack, engine, graph, jobs, memory, runner, settings, status_page
from .state import Reel, ReelError, short


def _p(obj: Any) -> None:
    print(json.dumps(obj, indent=2, default=str))


def _reels(reel: str | None) -> list[Reel]:
    return [Reel.load(reel)] if reel else Reel.all()


def cmd_status(a: argparse.Namespace) -> int:
    for r in _reels(a.reel):
        states = engine.node_states(r)
        if a.json:
            _p({"reel": r.id, "states": states, "waiting": r.state.get("waiting"),
                "last_error": r.state.get("last_error"), "approvals": r.state.get("approvals")})
            continue
        print(f"\n{r.id}  ({r.state.get('idea', '')[:70]})")
        print(f"  text: {r.dir}\n  media: {r.media}")
        for s in states:
            mark = {"done": "✓", "skipped": "–", "waiting": "⏸", "failed": "✗", "ready": "▶",
                    "stale": "↺", "pending": "·"}[s["state"]]
            extra = f"  stale: {s['stale']['reason'][:60]}" if s.get("stale") and s["state"] == "stale" else ""
            print(f"  {mark} {s['name']:<18} {s['state']:<8} {s['version'] or '':<12}{extra}")
        print(f"  next: {engine.next_action(r)}")
        if r.state.get("last_error"):
            e = r.state["last_error"]
            print(f"  last error ({e['stage']}, {e['at']}): {e['error'][:200]}")
    return 0


def cmd_next(a: argparse.Namespace) -> int:
    reels = Reel.all()
    if not reels:
        print("no orchestrated reels; `new \"<idea>\"` or `adopt <reel-id>`")
    for r in reels:
        print(f"{r.id}: {engine.next_action(r)}")
    return 0


def cmd_new(a: argparse.Namespace) -> int:
    reel = engine.new(a.idea, a.id)
    print(f"created {reel.id}\n  text: {reel.dir}\n  media: {reel.media}")
    if a.now:
        _p(engine.advance(reel.id))
    else:
        jid = jobs.enqueue("advance", reel.id, requested_by=getpass.getuser(), reason="new reel")
        print(f"queued job {jid}: the runner drafts the brief and notifies you at the brief gate")
    return 0


def cmd_adopt(a: argparse.Namespace) -> int:
    reel = engine.adopt(a.reel)
    print(f"adopted {reel.id}; next: {engine.next_action(reel)}")
    return 0


def cmd_run(a: argparse.Namespace) -> int:
    targets = _reels(a.reel)
    for r in targets:
        if a.bg:
            jid = jobs.enqueue("advance", r.id, {"until": a.until} if a.until else {}, getpass.getuser(), "run --bg")
            print(f"{r.id}: queued job {jid}")
        else:
            res = engine.advance(r.id, until=a.until)
            print(f"{r.id}: ran {', '.join(res['ran']) or 'nothing'}; stopped: {res['stopped']} at {res.get('node')}")
            if res.get("error"):
                print(f"  error: {res['error'][:400]}")
            print(f"  next: {engine.next_action(Reel.load(r.id))}")
    _safe_page()
    return 0


def cmd_approve(a: argparse.Namespace) -> int:
    rec = engine.approve(a.reel, a.gate, a.by, a.note)
    print(f"approved {rec['gate']} ({rec['version']}) by {rec['by']}")
    if not a.no_queue and a.gate != "posting":
        jid = jobs.enqueue("advance", a.reel, requested_by=rec["by"], reason=f"approved {a.gate}")
        print(f"queued job {jid} to continue {a.reel} up to the next gate")
    _safe_page()
    return 0


def cmd_feedback(a: argparse.Namespace) -> int:
    res = backtrack.feedback(a.reel, a.text, use_model=not a.no_model, dry_run=a.dry_run, stage_override=a.stage)
    c = res["classification"]
    print(f"routed to: {c['stage']} (by {c.get('classified_by')}, confidence {c.get('confidence')})")
    print(f"why: {c.get('reason')}")
    if c.get("model_error"):
        print(f"note: model classifier failed ({c['model_error']}); used keywords")
    if not res.get("dry_run"):
        print(f"feedback id: {res['feedback_id']}; invalidated: {', '.join(res['invalidated']) or 'nothing'}")
        print(f"record: {res['record']}; lesson: {res['lesson']}")
    print("re-run plan: " + " -> ".join(res["plan"]))
    if not res.get("dry_run"):
        print(f"start it with `run {a.reel}` (now) or `run {a.reel} --bg` (runner)")
    _safe_page()
    return 0


def cmd_perf(a: argparse.Namespace) -> int:
    r = Reel.load(a.reel)
    data = {}
    for kv in a.metrics:
        k, _, v = kv.partition("=")
        try:
            data[k] = float(v) if "." in v else int(v)
        except ValueError:
            data[k] = v
    path = r.dir / "performance.json"
    old = json.loads(path.read_text()) if path.exists() else {"snapshots": []}
    from .state import now
    old["snapshots"].append({"at": now(), **data})
    path.write_text(json.dumps(old, indent=2) + "\n")
    r.log("performance", metrics=data)
    print(f"recorded {data}; then `approve {r.id} performance` and `feedback {r.id} \"...\"` for lessons")
    return 0


def cmd_log(a: argparse.Namespace) -> int:
    for r in _reels(a.reel):
        print(f"\n== {r.id}")
        for e in r.ledger()[-a.n:]:
            ev = e["event"]
            body = {k: v for k, v in e.items() if k not in ("ts", "event")}
            if ev == "stage_run":
                s = (f"{body['stage']} -> {body['version']} ({'changed' if body.get('changed') else 'same'}) "
                     f"model={body.get('model')} prompt={body.get('prompt_version')} inputs={body.get('inputs')}")
            elif ev == "feedback":
                c = body.get("classification", {})
                s = f"{body['id']} \"{body['text'][:80]}\" -> {c.get('stage')} ({c.get('classified_by')})"
            else:
                s = json.dumps(body, default=str)[:220]
            print(f"{e['ts']}  {ev:<20} {s}")
    return 0


def cmd_queue(a: argparse.Namespace) -> int:
    if a.action == "cancel":
        jobs.cancel(int(a.args[0]))
        print(f"cancelled {a.args[0]}")
    elif a.action == "add":
        kind = a.args[0]
        reel = a.args[1] if len(a.args) > 1 else None
        print(f"queued job {jobs.enqueue(kind, reel, requested_by=getpass.getuser(), reason='queue add')}")
    else:
        for j in jobs.listing(a.n):
            print(f"#{j['id']:<4} {j['status']:<9} {j['kind']:<14} {j['reel'] or '':<28} "
                  f"{j['created_at']}  {(j['error'] or '')[:80]}")
    return 0


def cmd_memory(a: argparse.Namespace) -> int:
    if a.action == "approve":
        _p(memory.promote(a.arg, by="creator"))
    elif a.action == "reject":
        memory.reject(a.arg, "creator rejected")
        print(f"rejected {a.arg}")
    elif a.action == "candidates":
        for c in memory.load_candidates()["candidates"]:
            print(f"{c['id']} [{c['status']}; seen {c['count']}] ({', '.join(c['applies_to'])}) {c['rule']}")
    elif a.action == "show":
        block, ids = memory.prompt_block(a.arg, "")
        print(block or "(no lessons for this stage)")
    else:
        m = memory.load_memory()
        print(f"memory v{m.get('version')} ({len(m['lessons'])}/{settings.load()['memory']['max_lessons']} lessons)")
        for l in m["lessons"]:
            print(f"{l['id']} [{l['category']}; {l['confidence']}; {l['promoted_by']}] "
                  f"({', '.join(l['applies_to'])}) {l['rule']}")
    return 0


def cmd_av(a: argparse.Namespace) -> int:
    from . import av_review

    if a.file:
        out = Path(a.out) if a.out else settings.paths().state_dir / "av_review" / Path(a.file).stem
        res = av_review.review(Path(a.file), out)
    else:
        from .stages import final_mp4

        r = Reel.load(a.reel)
        res = av_review.review(final_mp4(r), r.dir)
    print(f"status: {res.get('status')}")
    print(f"report: {res.get('files', {}).get('av_review.md')}")
    return 0 if not str(res.get("status")).startswith("error") else 1


def cmd_check(a: argparse.Namespace) -> int:
    """Run the independent emotion + hook checker on a reel's current script or visual plan."""
    import json as _json

    from . import stages, story_check
    reel = Reel.load(a.reel)
    if a.phase == "visuals":
        check = stages.run_visuals_check(reel)
        print(f"{reel.dir / 'VISUALS_CHECK.md'}: {check['verdict']}")
        return 0
    s = stages.parse_script_md((reel.dir / "SCRIPT.md").read_text(encoding="utf-8"))
    bj = reel.dir / "beats.json"
    if bj.exists():  # keep emotion/delivery/continuity from beats.json
        extra = {b["id"]: b for b in _json.loads(bj.read_text(encoding="utf-8"))["beats"]}
        for b in s["beats"]:
            b.update({k: v for k, v in extra.get(b["id"], {}).items() if k in stages.BEAT_EXTRA})
    brief = reel.dir / "brief.json"
    check, prov = story_check.check_script(s, brief.read_text(encoding="utf-8") if brief.exists() else "")
    story_check.write_report(reel.dir, "SCRIPT_CHECK", f"{s.get('title') or reel.id}: emotion + hook check", check,
                             None, prov.get("model", ""))
    print(f"{reel.dir / 'SCRIPT_CHECK.md'}: {check['verdict']} (hook {check['scores']['hook']}/10)")
    return 0


def cmd_heartbeat(a: argparse.Namespace) -> int:
    if a.bg:
        print(f"queued job {jobs.enqueue('heartbeat', requested_by=getpass.getuser(), reason='heartbeat')}")
        return 0
    jid = jobs.enqueue("heartbeat", requested_by=getpass.getuser(), reason="heartbeat (foreground)")
    rc = runner.exec_job(jid) if jobs.claim_id(jid) else 1
    _p(jobs.get(jid))
    return rc


def _safe_page() -> None:
    try:
        status_page.write()
    except Exception as exc:  # noqa: BLE001
        print(f"(status page not updated: {exc})", file=sys.stderr)


def build() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(prog="python -m content_os.orchestrator", description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("new"); p.add_argument("idea"); p.add_argument("--id"); p.add_argument("--now", action="store_true")
    p = sub.add_parser("adopt"); p.add_argument("reel")
    p = sub.add_parser("status"); p.add_argument("reel", nargs="?"); p.add_argument("--json", action="store_true")
    sub.add_parser("next")
    p = sub.add_parser("run"); p.add_argument("reel", nargs="?"); p.add_argument("--until", choices=graph.ORDER)
    p.add_argument("--bg", action="store_true", help="queue for the runner instead of running now")
    p = sub.add_parser("approve"); p.add_argument("reel"); p.add_argument("gate", choices=list(graph.GATE_NODES))
    p.add_argument("--by"); p.add_argument("--note", default=""); p.add_argument("--no-queue", action="store_true")
    p = sub.add_parser("feedback"); p.add_argument("reel"); p.add_argument("text")
    p.add_argument("--no-model", action="store_true"); p.add_argument("--dry-run", action="store_true")
    p.add_argument("--stage", choices=graph.FEEDBACK_TARGETS, help="override the classifier")
    p = sub.add_parser("perf"); p.add_argument("reel"); p.add_argument("metrics", nargs="+")
    p = sub.add_parser("log"); p.add_argument("reel", nargs="?"); p.add_argument("-n", type=int, default=40)
    p = sub.add_parser("queue"); p.add_argument("action", nargs="?", default="list", choices=["list", "cancel", "add"])
    p.add_argument("args", nargs="*"); p.add_argument("-n", type=int, default=25)
    p = sub.add_parser("memory"); p.add_argument("action", nargs="?", default="list",
                                                 choices=["list", "candidates", "approve", "reject", "show"])
    p.add_argument("arg", nargs="?")
    p = sub.add_parser("av-review"); p.add_argument("reel", nargs="?"); p.add_argument("--file"); p.add_argument("--out")
    p = sub.add_parser("check"); p.add_argument("reel"); p.add_argument("--phase", choices=["script", "visuals"], default="script")
    p = sub.add_parser("heartbeat"); p.add_argument("--bg", action="store_true")
    sub.add_parser("status-page")
    sub.add_parser("install-runner"); sub.add_parser("uninstall-runner"); sub.add_parser("runner-status")
    p = sub.add_parser("runner"); p.add_argument("--once", action="store_true")
    p = sub.add_parser("_exec-job"); p.add_argument("job_id", type=int)
    return ap


def main(argv: list[str] | None = None) -> int:
    a = build().parse_args(argv)
    try:
        handlers = {"status": cmd_status, "next": cmd_next, "new": cmd_new, "adopt": cmd_adopt, "run": cmd_run,
                    "approve": cmd_approve, "feedback": cmd_feedback, "perf": cmd_perf, "log": cmd_log,
                    "queue": cmd_queue, "memory": cmd_memory, "av-review": cmd_av, "check": cmd_check, "heartbeat": cmd_heartbeat}
        if a.cmd in handlers:
            return handlers[a.cmd](a)
        if a.cmd == "status-page":
            print(status_page.write())
            return 0
        if a.cmd == "install-runner":
            _p(runner.install())
            return 0
        if a.cmd == "uninstall-runner":
            _p(runner.uninstall())
            return 0
        if a.cmd == "runner-status":
            _p(runner.status())
            return 0
        if a.cmd == "runner":
            return runner.loop(once=a.once)
        if a.cmd == "_exec-job":
            return runner.exec_job(a.job_id)
    except (ReelError, KeyError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    return 0
