"""Single self-contained status page (~/Movies/ContentOS/status.html): reels, stage states, pending
approvals with the exact command, last errors, the job queue and the runner heartbeat."""

from __future__ import annotations

import json
from html import escape
from pathlib import Path

from . import engine, jobs, settings
from .state import Reel, now

CSS = """
:root{--bg:#f7f6f3;--panel:#fff;--ink:#1d1d1f;--muted:#6b6b70;--line:#e3e1dc;--ok:#1f7a4d;--okbg:#e3f3ea;
--warn:#8a5a00;--warnbg:#fdf0d5;--bad:#a1262a;--badbg:#fbe4e4;--info:#1f4f8a;--infobg:#e3ecf8;--dim:#ececea}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){--bg:#151517;--panel:#1e1e21;--ink:#ececef;
--muted:#9a9aa2;--line:#2e2e33;--ok:#6fd39c;--okbg:#17321f;--warn:#f1c26b;--warnbg:#3a2c10;--bad:#f08a8d;
--badbg:#3d1a1b;--info:#8db8f0;--infobg:#172a42;--dim:#2a2a2e}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);
font:14px/1.45 -apple-system,BlinkMacSystemFont,"SF Pro Text",system-ui,sans-serif}
main{max-width:1100px;margin:0 auto;padding:20px 16px 48px}h1{font-size:20px;margin:0 0 4px}
h2{font-size:15px;margin:28px 0 10px}.muted{color:var(--muted)}.card{background:var(--panel);border:1px solid var(--line);
border-radius:10px;padding:14px 16px;margin:10px 0}.row{display:flex;flex-wrap:wrap;gap:6px;margin-top:8px}
.chip{font-size:12px;padding:2px 8px;border-radius:999px;background:var(--dim);color:var(--muted);white-space:nowrap}
.done,.skipped{background:var(--okbg);color:var(--ok)}.waiting{background:var(--warnbg);color:var(--warn);font-weight:600}
.failed{background:var(--badbg);color:var(--bad);font-weight:600}.ready{background:var(--infobg);color:var(--info)}
.stale{background:var(--warnbg);color:var(--warn);text-decoration:line-through}
code{font:12px ui-monospace,SFMono-Regular,Menlo,monospace;background:var(--dim);padding:1px 5px;border-radius:4px;
word-break:break-all}table{width:100%;border-collapse:collapse;font-size:13px}td,th{text-align:left;padding:5px 6px;
border-bottom:1px solid var(--line);vertical-align:top}.err{color:var(--bad)}.wrap{overflow-x:auto}
"""


def render() -> str:
    reels = Reel.all()
    hb = heartbeat()
    parts = [f"<main><h1>Content OS reels</h1><div class='muted'>Updated {escape(now())} · runner: "
             f"{escape(hb)}</div>"]
    pending = []
    for r in reels:
        f = engine.frontier(r)
        if f and f["state"] in ("waiting", "failed"):
            pending.append((r, f))
    parts.append("<h2>Needs you</h2>")
    if not pending:
        parts.append("<div class='card muted'>Nothing waiting on the creator.</div>")
    for r, f in pending:
        parts.append(f"<div class='card'><b>{escape(r.id)}</b> · <span class='chip {f['state']}'>{escape(f['name'])}"
                     f"</span><div style='margin-top:6px'>{escape(engine.next_action(r))}</div></div>")
    parts.append("<h2>Reels</h2>")
    for r in reels:
        states = engine.node_states(r)
        chips = "".join(f"<span class='chip {s['state']}' title='{escape(s['state'])} {escape(s['version'] or '')}'>"
                        f"{escape(s['name'])}</span>" for s in states)
        err = r.state.get("last_error")
        err_html = (f"<div class='err' style='margin-top:6px'>Last error ({escape(err['stage'])}, {escape(err['at'])}): "
                    f"{escape(err['error'][:400])}</div>") if err else ""
        fb = [f for f in r.state.get("feedback", []) if not f.get("resolved_in")]
        fb_html = ("<div class='muted' style='margin-top:6px'>Open feedback: " +
                   "; ".join(f"{escape(f['id'])} → {escape(f['stage'])}: {escape(f['text'][:80])}" for f in fb) +
                   "</div>") if fb else ""
        parts.append(f"<div class='card'><b>{escape(r.id)}</b> <span class='muted'>{escape(r.state.get('idea', '')[:120])}"
                     f"</span><div class='row'>{chips}</div>{fb_html}{err_html}</div>")
    try:
        rows = jobs.listing(15)
    except Exception as exc:  # noqa: BLE001
        rows = []
        parts.append(f"<div class='err'>queue unreadable: {escape(str(exc))}</div>")
    parts.append("<h2>Jobs</h2><div class='card wrap'><table><tr><th>#</th><th>kind</th><th>reel</th><th>status</th>"
                 "<th>created</th><th>finished</th><th>error</th></tr>")
    for j in rows:
        parts.append(f"<tr><td>{j['id']}</td><td>{escape(j['kind'])}</td><td>{escape(j['reel'] or '')}</td>"
                     f"<td><span class='chip {_job_class(j['status'])}'>{escape(j['status'])}</span></td>"
                     f"<td>{escape(j['created_at'] or '')}</td><td>{escape(j['finished_at'] or '')}</td>"
                     f"<td class='err'>{escape((j['error'] or '')[:160])}</td></tr>")
    parts.append("</table></div><p class='muted'>Commands: <code>python -m content_os.orchestrator next</code> · "
                 "<code>approve &lt;reel&gt; &lt;gate&gt;</code> · <code>feedback &lt;reel&gt; \"…\"</code> · "
                 "<code>runner-status</code></p></main>")
    return ("<!doctype html><html lang='en'><head><meta charset='utf-8'><meta name='viewport' "
            "content='width=device-width,initial-scale=1'><meta http-equiv='refresh' content='60'>"
            f"<title>Content OS status</title><style>{CSS}</style></head><body>{''.join(parts)}</body></html>")


def _job_class(status: str) -> str:
    return {"done": "done", "running": "ready", "queued": "ready", "paused": "waiting",
            "failed": "failed"}.get(status, "")


def heartbeat() -> str:
    p = settings.paths().state_dir / "runner_heartbeat.json"
    if not p.exists():
        return "never seen"
    try:
        hb = json.loads(p.read_text())
        return f"pid {hb.get('pid')} {hb.get('state')} at {hb.get('at')}"
    except (OSError, ValueError):
        return "unreadable"


def write() -> Path:
    path = settings.paths().status_page
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    tmp.write_text(render(), encoding="utf-8")
    tmp.replace(path)
    return path
