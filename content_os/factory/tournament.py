"""Overnight script tournament: many full drafts, three independent judges, automatic revision, one review page.

Round 0  : every configured variant (angle) is drafted in parallel - Fable 5.2 and GPT-6.2 Astra.
Scoring  : checker (Opus 5.5: facts, honesty, house rules), panel (GPT-6.2 Astra: 16 personas), critic
           (Fable 5.2 + the creator taste model: predicts the creator's verdict and change list).
Revision : the top variants are revised against all three, re-scored, and kept while they gain.
Output   : <out>/REVIEW.html + DECISIONS.md - the top two, scores, and only the decisions that need the creator.
Creator notes go back in with `revise`.
"""
from __future__ import annotations

import html
import json
import re
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any

from . import taste
from .llm import REPO, call, config, parse_json

MEMORY = Path.home() / ".claude/projects/-Users-sagartekwani/memory"

PANEL = ("Panel (Indian Instagram viewers scrolling at 10 pm, English only): 1 TCS support engineer Pune 24; "
         "2 CA Ahmedabad 31; 3 HR exec Bengaluru 28; 4 bank RM Lucknow 35; 5 school teacher Jaipur 38; "
         "6 BTech final-year Hyderabad 21; 7 FP&A analyst Gurgaon 25; 8 IB/equity research associate Mumbai 33; "
         "9 Big 4 consulting analyst Bengaluru 24; 10 strategy consulting manager Mumbai 32; 11 performance marketing "
         "exec Delhi 26; 12 FMCG brand manager Mumbai 34; 13 startup backend dev Bengaluru 27; 14 ML engineer "
         "Hyderabad 30; 15 gym trainer Delhi 29 (non-tech); 16 BCom student Kolkata 20. "
         "Groups: mass 2-5,12,15,16; fin-consult-mktg 7-12; builders 1,6,13,14.")

PACKAGE_FORMAT = """OUTPUT, in this order (Markdown):
# SCRIPT
Beat table: Beat | E/H | Time | Spoken (what the creator says) | Top-half visual (what draws on which word) |
Bottom half (face / footage / punch-in) | On-screen text | Viewer feels | Delivery (face/voice) | Sound.
Then: runtime estimate at 1.15x, save asset, honest comment trigger, the re-hooks at 1/3 and 2/3.
# VISUAL BOARD
Palette, type, music and SFX direction. One KEYFRAME per visual change: id | time | layout | on screen |
motion anchored to a word | data source (measured file or [SLOT]).
# HOOKS
3 beat-1 variants on different emotions, one line each, plus the MAIN vs TRIAL A/B hypothesis.
# CAPTION
Caption draft with the comment keyword and any credits.
# TELEPROMPTER
Just the spoken lines, one beat per line, as the creator will read them."""


def context(brief: str, facts: str) -> str:
    rules = "\n".join(f"- {p.stem}: {p.read_text().split('---')[-1].strip()[:600]}"
                      for p in sorted(MEMORY.glob("*.md")) if p.name != "MEMORY.md")
    docs = []
    for rel in (".agents/skills/reel-script-writing/SKILL.md", "production/REEL_DEFAULTS.md"):
        p = REPO / rel
        if p.exists():
            docs.append(f"## {rel}\n{p.read_text()}")
    return (f"# BRIEF\n{brief}\n\n# FACTS (the only allowed numbers and claims; unmeasured = [SLOT])\n{facts}\n\n"
            f"# CREATOR TASTE MODEL\n{taste.load()}\n\n# CREATOR RULES (memory)\n{rules}\n\n" + "\n\n".join(docs))


def write_prompt(ctx: str, angle: str) -> str:
    return (f"You are writing an Instagram reel package for this creator. Your assigned ANGLE: {angle}.\n"
            "Follow BRIEF, FACTS, the CREATOR TASTE MODEL and the house rules exactly; LOCKED creator decisions may "
            "not be reopened. Never invent numbers or results. English only.\n\n"
            f"{PACKAGE_FORMAT}\n\n{ctx}")


def check_prompt(ctx: str, draft: str) -> str:
    return (f"{ctx}\n\n# DRAFT (written by another model)\n{draft}\n\n"
            "You are the independent checker. Check the DRAFT against BRIEF, FACTS and the house rules: every number "
            "and claim supported or a marked [SLOT]; quotes verbatim; nothing overclaims; locked decisions kept; "
            "architecture explained where the brief calls for it; emotion/hook rhythm; payoff early; runtime.\n"
            'Reply with JSON only: {"must_fix":[str],"should_fix":[str],"facts_ok":bool}')


def panel_prompt(draft: str) -> str:
    return (f"You are an engagement panel. Another model wrote this Instagram reel package; you did not.\n{PANEL}\n"
            "Imagine each persona meeting this reel cold in their feed. For each persona give ENGAGEMENT 0-10 "
            "(10 = holds past 3 s, watches to the end, and would send, save or comment), a short reason, and the beat "
            "where they drop off (or \"none\"). Be strict: an ordinary good reel scores 5-6. Judge the visuals as "
            "described, as if built well.\n"
            'Reply with JSON only: {"personas":[{"id":int,"score":num,"drop_beat":str,"why":str}],'
            '"groups":{"mass":num,"fin_consult_mktg":num,"builders":num},"overall":num,'
            '"top_fixes":[str]}\n\n# DRAFT\n' + draft)


def critic_prompt(ctx: str, draft: str) -> str:
    return (f"{ctx}\n\n# DRAFT\n{draft}\n\n"
            "You are the CREATOR CRITIC. Using the CREATOR TASTE MODEL, predict exactly how this creator reacts to the "
            "DRAFT: the score they would give (0-10, where 8 = approve with tiny edits), whether they approve it, and "
            "the change list they would send, in their words. Run every checklist item of the taste model.\n"
            'Reply with JSON only: {"predicted_score":num,"would_approve":bool,"change_list":[str],'
            '"taste_violations":[str],"what_they_will_love":[str]}')


def revise_prompt(ctx: str, draft: str, fb: dict[str, Any], notes: str = "") -> str:
    creator = f"\n# CREATOR NOTES (highest priority; apply all of them)\n{notes}\n" if notes else ""
    return (f"{ctx}\n\n# CURRENT DRAFT\n{draft}\n{creator}\n# FEEDBACK\n{json.dumps(fb, indent=1)[:12000]}\n\n"
            "Revise the DRAFT. Fix every checker must_fix and every creator-critic change; use panel top_fixes and "
            "drop-off beats where they do not conflict with the creator. Keep what scored well. Return the complete "
            f"revised package.\n\n{PACKAGE_FORMAT}")


def decide_prompt(ctx: str, top: list[dict[str, Any]]) -> str:
    body = "\n\n".join(f"## Variant {v['id']} (score {v['score']:.2f})\n{v['draft']}\n\nSCORES: "
                       f"{json.dumps(v['summary'])}" for v in top)
    return (f"{ctx}\n\n{body}\n\nYou prepare the creator's ONLY review. Their time is the scarcest resource. Write "
            "Markdown:\n# Recommendation\nWhich variant to shoot as MAIN and which hook for the TRIAL, in 3 lines.\n"
            "# Decisions only you can make\nAt most 5 numbered taste questions, each answerable in a few words, with "
            "your recommended answer. Never ask anything a model could check.\n# Measurements still needed\n[SLOTS] "
            "that must be measured before the shoot.\n# What changed vs the brief\nOne line each.")


def score(ctx: str, draft: str, ledger: Path, w: dict[str, Any]) -> dict[str, Any]:
    with ThreadPoolExecutor(3) as ex:
        fc = ex.submit(call, "checker", check_prompt(ctx, draft), ledger=ledger)
        fp = ex.submit(call, "panel", panel_prompt(draft), ledger=ledger)
        fr = ex.submit(call, "critic", critic_prompt(ctx, draft), ledger=ledger)
        out = {}
        for k, f in (("check", fc), ("panel", fp), ("critic", fr)):
            try:
                out[k] = parse_json(f.result())
            except Exception as e:  # noqa: BLE001 - a failed judge lowers confidence, not the run
                out[k] = {"error": str(e)[:300]}
    panel = float(out["panel"].get("overall", 0) or 0)
    critic = float(out["critic"].get("predicted_score", 0) or 0)
    musts = len(out["check"].get("must_fix", []) or [])
    pen = min(w["max_penalty"], w["must_fix_penalty"] * musts)
    out["score"] = w["weights"]["panel"] * panel + w["weights"]["critic"] * critic - pen
    out["summary"] = {"panel": panel, "critic": critic, "must_fix": musts,
                      "approve": out["critic"].get("would_approve"), "groups": out["panel"].get("groups")}
    return out


def _save(out: Path, rnd: int, vid: str, draft: str, sc: dict[str, Any]) -> dict[str, Any]:
    d = out / f"round_{rnd}"
    d.mkdir(parents=True, exist_ok=True)
    (d / f"{vid}_DRAFT.md").write_text(draft)
    (d / f"{vid}_SCORES.json").write_text(json.dumps(sc, indent=1))
    return {"id": vid, "round": rnd, "draft": draft, "score": sc["score"], "summary": sc["summary"], "fb": sc}


def run(brief: Path, facts: Path, out: Path, only: list[str] | None = None) -> Path:
    cfg = config()["tournament"]
    out.mkdir(parents=True, exist_ok=True)
    ledger = out / "ledger.jsonl"
    ctx = context(brief.read_text(), facts.read_text() if facts and facts.exists() else "(none)")
    (out / "CONTEXT.md").write_text(ctx)
    variants = [v for v in cfg["variants"] if not only or v["id"] in only]

    def first(v: dict[str, Any]) -> dict[str, Any]:
        draft = call(v["role"], write_prompt(ctx, v["angle"]), ledger=ledger)
        rec = _save(out, 0, v["id"], draft, score(ctx, draft, ledger, cfg))
        rec["angle"], rec["writer"] = v["angle"], config()["roles"][v["role"]]["model"]
        return rec

    with ThreadPoolExecutor(cfg["workers"]) as ex:
        results = [r for r in ex.map(_safe(first), variants) if r]
    best = {r["id"]: r for r in results}
    _leaderboard(out, list(best.values()))

    alive = sorted(best.values(), key=lambda r: -r["score"])[: cfg["keep_top"]]
    for rnd in range(1, cfg["max_revisions"] + 1):
        if not alive:
            break

        def rev(r: dict[str, Any], rnd: int = rnd) -> dict[str, Any]:
            draft = call("reviser", revise_prompt(ctx, r["draft"], _fb(r["fb"])), ledger=ledger)
            n = _save(out, rnd, r["id"], draft, score(ctx, draft, ledger, cfg))
            n["angle"], n["writer"] = r.get("angle"), r.get("writer")
            return n

        with ThreadPoolExecutor(cfg["workers"]) as ex:
            new = [n for n in ex.map(_safe(rev), alive) if n]
        nxt = []
        for n in new:
            gain = n["score"] - best[n["id"]]["score"]
            if gain > 0:
                best[n["id"]] = n
            if gain >= cfg["min_gain"]:
                nxt.append(n)
        alive = nxt
        _leaderboard(out, list(best.values()))
    return finish(out, ctx, list(best.values()), ledger)


def revise(out: Path, vid: str, notes: str) -> Path:
    """Apply the creator's notes to one variant, re-score it, and rebuild the review page."""
    cfg = config()["tournament"]
    ledger = out / "ledger.jsonl"
    ctx = (out / "CONTEXT.md").read_text()
    best = _load_best(out)
    r = best[vid]
    draft = call("reviser", revise_prompt(ctx, r["draft"], _fb(r["fb"]), notes), ledger=ledger)
    rnd = max(int(p.name.split("_")[1]) for p in out.glob("round_*")) + 1
    (out / f"round_{rnd}").mkdir(exist_ok=True)
    (out / f"round_{rnd}" / "CREATOR_NOTES.md").write_text(notes)
    n = _save(out, rnd, vid, draft, score(ctx, draft, ledger, cfg))
    n["angle"], n["writer"] = r.get("angle"), r.get("writer")
    best[vid] = n  # creator notes win even if the panel score dips
    _leaderboard(out, list(best.values()))
    return finish(out, ctx, list(best.values()), ledger)


def _fb(sc: dict[str, Any]) -> dict[str, Any]:
    return {"checker": sc.get("check"), "creator_critic": sc.get("critic"),
            "panel": {k: sc.get("panel", {}).get(k) for k in ("overall", "groups", "top_fixes")} |
            {"drop_offs": [(p.get("id"), p.get("drop_beat")) for p in sc.get("panel", {}).get("personas", [])]}}


def _safe(fn):
    def wrap(x):
        try:
            return fn(x)
        except Exception as e:  # noqa: BLE001 - one failed variant must not sink the night
            print(f"variant failed: {e}")
            return None
    return wrap


def _load_best(out: Path) -> dict[str, dict[str, Any]]:
    lb = json.loads((out / "leaderboard.json").read_text())
    best = {}
    for row in lb:
        d = out / f"round_{row['round']}"
        sc = json.loads((d / f"{row['id']}_SCORES.json").read_text())
        best[row["id"]] = {**row, "draft": (d / f"{row['id']}_DRAFT.md").read_text(), "fb": sc}
    return best


def _leaderboard(out: Path, rows: list[dict[str, Any]]) -> None:
    rows = sorted(rows, key=lambda r: -r["score"])
    keep = [{k: r.get(k) for k in ("id", "round", "score", "summary", "angle", "writer")} for r in rows]
    (out / "leaderboard.json").write_text(json.dumps(keep, indent=1))


def finish(out: Path, ctx: str, rows: list[dict[str, Any]], ledger: Path) -> Path:
    rows = sorted(rows, key=lambda r: -r["score"])
    top = rows[:2]
    try:
        decisions = call("decider", decide_prompt(ctx, top), ledger=ledger)
    except Exception as e:  # noqa: BLE001
        decisions = f"(decider failed: {e})"
    (out / "DECISIONS.md").write_text(decisions)
    page = review_html(out.name, rows, top, decisions, ledger)
    (out / "REVIEW.html").write_text(page)
    return out / "REVIEW.html"


# ---------- review page ----------

def md_to_html(md: str) -> str:
    out, table, lst = [], [], False

    def inline(s: str) -> str:
        s = html.escape(s)
        s = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", s)
        return re.sub(r"`(.+?)`", r"<code>\1</code>", s)

    def flush_table():
        if table:
            rows = [r for r in table if not re.match(r"^\|?\s*:?-{2,}", r.replace(" ", ""))]
            cells = [[c.strip() for c in r.strip().strip("|").split("|")] for r in rows]
            h = "".join(f"<th>{inline(c)}</th>" for c in cells[0])
            b = "".join("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in r) + "</tr>" for r in cells[1:])
            out.append(f"<div class=tw><table><tr>{h}</tr>{b}</table></div>")
            table.clear()

    for line in md.splitlines():
        if line.strip().startswith("|"):
            table.append(line)
            continue
        flush_table()
        m = re.match(r"^(#{1,4})\s+(.*)", line)
        if lst and not re.match(r"^\s*([-*]|\d+\.)\s", line):
            out.append("</ul>")
            lst = False
        if m:
            n = len(m.group(1)) + 1
            out.append(f"<h{n}>{inline(m.group(2))}</h{n}>")
        elif re.match(r"^\s*([-*]|\d+\.)\s", line):
            if not lst:
                out.append("<ul>")
                lst = True
            out.append(f"<li>{inline(re.sub(r'^\s*([-*]|\d+\.)\s', '', line))}</li>")
        elif line.strip():
            out.append(f"<p>{inline(line)}</p>")
    flush_table()
    if lst:
        out.append("</ul>")
    return "\n".join(out)


def review_html(name: str, rows: list[dict[str, Any]], top: list[dict[str, Any]], decisions: str,
                ledger: Path) -> str:
    calls = [json.loads(x) for x in ledger.read_text().splitlines()] if ledger.exists() else []
    board = "".join(
        f"<tr><td><b>{r['id']}</b></td><td>{html.escape(str(r.get('angle', '')))}</td><td>{r.get('writer', '')}</td>"
        f"<td>{r['round']}</td><td><b>{r['score']:.2f}</b></td><td>{r['summary']['panel']}</td>"
        f"<td>{r['summary']['critic']}</td><td>{r['summary']['must_fix']}</td><td>{r['summary']['approve']}</td></tr>"
        for r in rows)
    cols = ""
    for r in top:
        crit = r["fb"].get("critic", {})
        changes = "".join(f"<li>{html.escape(c)}</li>" for c in crit.get("change_list", [])[:8])
        musts = "".join(f"<li>{html.escape(c)}</li>" for c in r["fb"].get("check", {}).get("must_fix", [])[:8])
        cols += (f"<section class=col><h2>Variant {r['id']} · {r['score']:.2f}</h2>"
                 f"<p class=meta>{html.escape(str(r.get('angle', '')))} · {r.get('writer', '')} · round {r['round']}</p>"
                 f"<details><summary>Predicted creator changes ({len(crit.get('change_list', []))})</summary>"
                 f"<ul>{changes}</ul></details><details><summary>Checker must-fix "
                 f"({len(r['fb'].get('check', {}).get('must_fix', []))})</summary><ul>{musts}</ul></details>"
                 f"{md_to_html(r['draft'])}</section>")
    return f"""<!doctype html><html><head><meta charset=utf-8><meta name=viewport content="width=device-width,initial-scale=1">
<title>Script review: {html.escape(name)}</title><style>
:root{{--bg:#fbfaf7;--fg:#1d1d1f;--mut:#6b6b70;--line:#e3e1dc;--acc:#e8590c;--card:#fff}}
@media (prefers-color-scheme:dark){{:root{{--bg:#151517;--fg:#ececee;--mut:#9a9aa2;--line:#2c2c30;--acc:#ff8a3d;--card:#1d1d20}}}}
body{{background:var(--bg);color:var(--fg);font:15px/1.5 -apple-system,system-ui,sans-serif;margin:0;padding:16px}}
h1{{font-size:22px;margin:4px 0 12px}} h2{{font-size:18px;margin:16px 0 6px}} h3,h4,h5{{font-size:15px;margin:14px 0 4px;color:var(--acc)}}
.dec{{background:var(--card);border:1px solid var(--line);border-left:4px solid var(--acc);border-radius:8px;padding:8px 16px;max-width:900px}}
.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,560px),1fr));gap:16px;margin-top:16px}}
.col{{background:var(--card);border:1px solid var(--line);border-radius:8px;padding:8px 16px;min-width:0}}
.tw{{overflow-x:auto}} table{{border-collapse:collapse;font-size:13px;margin:8px 0}} td,th{{border:1px solid var(--line);padding:4px 6px;vertical-align:top;text-align:left}}
.meta{{color:var(--mut);font-size:13px}} details{{margin:6px 0}} summary{{cursor:pointer;color:var(--acc)}}
code{{font-size:13px}}
</style></head><body>
<h1>Script review · {html.escape(name)}</h1>
<p class=meta>{len(calls)} model calls · reply with notes, e.g. <code>python -m content_os.factory revise {html.escape(name)} A "notes"</code></p>
<div class=dec>{md_to_html(decisions)}</div>
<h2>Leaderboard</h2><div class=tw><table><tr><th>Variant</th><th>Angle</th><th>Writer</th><th>Round</th><th>Score</th>
<th>Panel (Astra)</th><th>Creator critic (Fable)</th><th>Must-fix (Opus)</th><th>Critic approves</th></tr>{board}</table></div>
<div class=grid>{cols}</div></body></html>"""
