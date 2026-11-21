"""Locked factory draft -> shoot pack for MAIN and TRIAL: TELEPROMPTER.md, beats.json, teleprompter.html (Chrome).

Reads the '## MAIN' and '## TRIAL' beat tables of a factory draft (columns: Beat | E/H | Time | Spoken | ... |
Viewer feels | Delivery | Sound). Beats with no spoken line (e.g. a countdown) are skipped. TRIAL records only
the lines that differ from MAIN; shared beats reuse MAIN takes.

Usage: python scripts/shoot/make_shoot_pack.py <draft.md> <reel-slug> [--target-s 46]
Writes ~/Movies/ContentOS/<slug>-main/ and <slug>-trial/.
"""
import argparse, html, json, re
from pathlib import Path

POSE = "Base pose: sit back, hands resting together. Reset before every take; hold 1 s on the lens before and after."


def table(md, section, cues=None):
    m = re.search(rf"^## {section}\b.*?\n(\|.*?)(?:\n\n|\n#|\Z)", md, re.S | re.M)
    if not m:
        return []
    rows = [r for r in m.group(1).splitlines() if r.startswith("|")]
    head = [c.strip().lower() for c in rows[0].strip("|").split("|")]
    col = lambda *names: next(i for i, h in enumerate(head) if any(n in h for n in names))
    def opt(*n):
        try:
            return col(*n)
        except StopIteration:
            return None
    ib, ie, isp, ife, ide = col("beat"), col("e/h"), col("spoken"), opt("feels"), opt("delivery")
    cues = (cues or {}).get(section, {})
    out = []
    for r in rows[2:]:
        c = [x.strip() for x in r.strip("|").split("|")]
        if len(c) < len(head):
            continue
        spoken = re.sub(r"\*\*|`", "", c[isp]).strip().strip('"')
        if not spoken or spoken.lower() in ("—", "-", "(none)", "none") or spoken.startswith("("):
            continue
        cu = cues.get(c[ib].split()[0], {})
        out.append({"beat": c[ib], "eh": c[ie], "text": spoken,
                    "feel": re.sub(r"\*\*", "", c[ife]).strip('" ') if ife is not None else cu.get("feel", ""),
                    "delivery": re.sub(r"\*\*", "", c[ide]) if ide is not None else cu.get("delivery", "")})
    return out


def write_pack(d, slug, beats, target, title):
    d.mkdir(parents=True, exist_ok=True)
    md = [f"# Teleprompter: {title}", ""]
    for i, b in enumerate(beats, 1):
        md += [f"**beat {i}**", b["text"], f"(FEEL: {b['feel']} · FACE/VOICE: {b['delivery']} · POSE: {POSE})", ""]
    (d / "TELEPROMPTER.md").write_text("\n".join(md))
    (d / "beats.json").write_text(json.dumps({"reel_id": d.name, "target_duration_s": target, "beats": [
        {"id": i, "text": b["text"], "section": b["beat"], "eh": b["eh"], "emotion": b["feel"], "delivery": b["delivery"],
         "continuity": POSE} for i, b in enumerate(beats, 1)]}, indent=1))
    data = json.dumps([{"n": i, "t": b["text"], "feel": b["feel"], "dv": b["delivery"], "sec": b["beat"]} for i, b in enumerate(beats, 1)])
    (d / "teleprompter.html").write_text(f'''<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1"><title>Teleprompter: {html.escape(title)}</title>
<style>
:root{{--bg:#000;--fg:#f5f5f0;--dim:#8a8a8a;--accent:#ffcc33;--cue:#35e0ff}}
html,body{{margin:0;height:100%;background:var(--bg);color:var(--fg);font-family:-apple-system,"Helvetica Neue",Arial,sans-serif;cursor:none}}
.wrap{{height:100%;display:flex;flex-direction:column;justify-content:center;padding:0 6vw;box-sizing:border-box}}
.cue{{color:var(--accent);font-size:4.6vw;font-weight:700;margin-bottom:2vh}}
.line{{font-size:6.8vw;line-height:1.25;font-weight:600}}
.dir{{margin-top:4vh;color:var(--cue);font-size:2.1vw;line-height:1.45;max-width:88vw}}
.dir b{{color:var(--fg)}}
.next{{position:fixed;bottom:4vh;left:6vw;right:6vw;color:var(--dim);font-size:2.4vw;line-height:1.3}}
.count{{position:fixed;top:3vh;right:4vw;color:var(--dim);font-size:2.2vw}}
.help{{position:fixed;top:3vh;left:4vw;color:#444;font-size:1.6vw}}
</style></head><body>
<div class="help">→ / space: next · ←: back · F: full screen · D: hide directions</div>
<div class="count" id="count"></div>
<div class="wrap"><div class="cue" id="cue"></div><div class="line" id="line"></div><div class="dir" id="dir"></div></div>
<div class="next" id="next"></div>
<script>
const beats = {data};
const POSE = {json.dumps(POSE)};
let i = 0, showDir = true;
function show() {{
  const b = beats[i];
  document.getElementById("cue").textContent = "Say: beat " + b.n + "  ·  " + b.sec;
  document.getElementById("line").textContent = b.t;
  document.getElementById("dir").innerHTML = showDir ? "<b>FEEL</b> " + b.feel + "<br><b>FACE / VOICE</b> " + b.dv + "<br><b>POSE</b> " + POSE : "";
  document.getElementById("next").textContent = i + 1 < beats.length ? "Next: " + beats[i + 1].t : "Last line. Say \\"final\\" after the take you want.";
  document.getElementById("count").textContent = (i + 1) + " / " + beats.length;
}}
document.addEventListener("keydown", e => {{
  if (e.key === "ArrowRight" || e.key === " ") {{ i = Math.min(beats.length - 1, i + 1); show(); e.preventDefault(); }}
  if (e.key === "ArrowLeft") {{ i = Math.max(0, i - 1); show(); }}
  if (e.key.toLowerCase() === "f") document.documentElement.requestFullscreen();
  if (e.key.toLowerCase() === "d") {{ showDir = !showDir; show(); }}
}});
document.addEventListener("click", () => {{ i = Math.min(beats.length - 1, i + 1); show(); }});
show();
</script></body></html>''')


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("draft"); ap.add_argument("slug"); ap.add_argument("--target-s", type=float, default=46)
    ap.add_argument("--cues", help="JSON {MAIN:{beat:{feel,delivery}},TRIAL:{...}} when the script table has no feel/delivery columns")
    a = ap.parse_args(); md = Path(a.draft).read_text(); root = Path.home() / "Movies" / "ContentOS"
    cues = json.loads(Path(a.cues).read_text()) if a.cues else None
    main, trial = table(md, "MAIN", cues), table(md, "TRIAL", cues)
    write_pack(root / f"{a.slug}-main", a.slug, main, a.target_s, f"{a.slug} MAIN")
    shared = {b["text"] for b in main}
    fresh = [b for b in trial if b["text"] not in shared]
    write_pack(root / f"{a.slug}-trial", a.slug, fresh, a.target_s, f"{a.slug} TRIAL (record only these; the rest reuse MAIN takes)")
    print(json.dumps({"main_lines": len(main), "trial_lines_total": len(trial), "trial_lines_to_record": len(fresh),
                      "main_words": sum(len(b["text"].split()) for b in main)}))
