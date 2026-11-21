"""One review page for the Fable 5.2 reels: spoken track, every beat with its animated clip, paper cuts,
the user-rules card, previews, mood boards, caption and cover. Writes ~/Movies/ContentOS/fable52-REVIEW.html."""
from __future__ import annotations

import html
import re
from pathlib import Path

HERE = Path(__file__).parent
MOV = Path.home() / "Movies/ContentOS"
OUT = MOV / "fable52-REVIEW.html"
SCRIPT = HERE / "V6_FINAL_SPOKEN.md"


def esc(s: str) -> str:
    s = html.escape(s)
    s = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", s)
    return re.sub(r"\[(DUMMY|MODEL|XX|CLIPS NEEDED|PAGE CUT NEEDED)([^\]]*)\]", r"<mark>[\1\2]</mark>", s)


def section(md: str, title: str) -> str:
    i = md.find(f"# {title}")
    if i < 0:
        return ""
    j = md.find("\n# ", i + 3)
    return md[i: j if j > 0 else None]


def md_to_html(md: str) -> str:
    out, rows = [], []

    def flush():
        nonlocal rows
        if rows:
            out.append("<table><tr>" + "".join(f"<th>{esc(c)}</th>" for c in rows[0]) + "</tr>" +
                       "".join("<tr>" + "".join(f"<td>{esc(c)}</td>" for c in r) + "</tr>" for r in rows[2:]) + "</table>")
            rows = []
    for line in md.splitlines():
        if line.startswith("|"):
            rows.append([c.strip() for c in line.strip().strip("|").split("|")])
            continue
        flush()
        if line.startswith("#"):
            n = min(len(line) - len(line.lstrip("#")) + 1, 4)
            out.append(f"<h{n}>{esc(line.lstrip('#').strip())}</h{n}>")
        elif line.strip().startswith(("- ", "* ")):
            out.append(f"<li>{esc(line.strip()[2:])}</li>")
        elif re.match(r"^\s*\d+\.\s", line):
            item = re.sub(r"^\s*\d+\.\s", "", line)
            out.append(f"<li>{esc(item)}</li>")
        elif line.strip():
            out.append(f"<p>{esc(line)}</p>")
    flush()
    return "\n".join(out)


def beats(reel: str) -> list[tuple[str, str, Path | None]]:
    d = MOV / f"fable52-{reel}"
    lines, cur = {}, None
    tp = d / "TELEPROMPTER.md"
    if tp.exists():
        for l in tp.read_text().splitlines():
            m = re.match(r"^\*\*beat (\d+)\*\*", l.strip())
            if m:
                cur = int(m.group(1)); lines[cur] = ""; continue
            if cur is not None and l.strip() and not l.startswith(("#", "(")):
                lines[cur] += " " + l.strip()
    clips = {int(p.stem.split("_")[1]): p for p in (d / "visuals").glob("beat_*.mp4")}
    keys = sorted(set(lines) | set(clips))
    return [(f"{n:02d}", lines.get(n, "").strip(), clips.get(n)) for n in keys]


def reel_block(reel: str, label: str) -> str:
    d = MOV / f"fable52-{reel}"
    prev = next(iter(sorted((d / "preview").glob("*.mp4"))), None)
    sheet = d / "visuals/contact_sheet.png"
    cards = []
    for n, line, clip in beats(reel):
        v = f"<video src='{clip.as_uri()}' controls muted loop preload='metadata'></video>" if clip else "<div class='none'>no clip</div>"
        cards.append(f"<div class='beat'><div class='bn'>beat {n}</div>{v}<p class='line'>{esc(line)}</p></div>")
    top = (f"<p><b>Full preview (synthetic voice):</b> <a href='{prev.as_uri()}'>{prev.name}</a></p>" if prev else "") + \
          (f"<p><a href='{sheet.as_uri()}'>contact sheet</a> · <a href='{(d / 'teleprompter.html').as_uri()}'>teleprompter</a> · "
           f"<a href='{(HERE / ('mb_' + reel) / 'MOODBOARD.html').as_uri()}'>mood board</a></p>")
    return f"<h2>{label}</h2>{top}<div class='grid'>{''.join(cards)}</div>"


def main():
    md = SCRIPT.read_text() if SCRIPT.exists() else ""
    spoken = section(md, "THE SPOKEN TRACK ONLY") or md
    rules = section(md, "FABLE USER RULES CARD")
    deliver = MOV / "fable52-deliver"
    cuts = sorted((HERE / "paper/cuts").glob("P*.png"), key=lambda p: int(re.findall(r"\d+", p.stem)[0]))
    cut_html = "".join(f"<figure><img src='{c.as_uri()}'><figcaption>{c.stem}</figcaption></figure>" for c in cuts)
    cover = deliver / "cover_DRAFT.png"
    caption = (deliver / "CAPTION.txt").read_text() if (deliver / "CAPTION.txt").exists() else ""
    css = """
:root{--bg:#0f1115;--ink:#ece9e1;--mut:#9aa0ab;--line:#2a2f3a;--acc:#FFD23F}
body{margin:0;background:var(--bg);color:var(--ink);font:16px/1.55 -apple-system,Inter,sans-serif}
main{max-width:1300px;margin:auto;padding:20px 16px 80px}h1{color:var(--acc)}h2{color:#6ee7f9;border-bottom:1px solid var(--line);padding-bottom:4px;margin-top:40px}
nav a{color:var(--acc);margin-right:14px}a{color:#6ee7f9}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:16px}
.beat{background:#171a21;border:1px solid var(--line);border-radius:10px;padding:10px}.bn{color:var(--mut);font-size:12px}
.beat video{width:100%;border-radius:6px;background:#000}.line{font-weight:600;color:#fff}.none{color:var(--mut);padding:30px;text-align:center}
.spoken p{font-size:18px;max-width:900px}table{border-collapse:collapse;width:100%;font-size:14px}th,td{border:1px solid var(--line);padding:8px;vertical-align:top}
th{background:#171a21;color:var(--mut)}figure{margin:0;background:#fff;border-radius:6px;padding:4px}figure img{width:100%}figcaption{color:#333;font-size:12px}
.cuts{display:grid;grid-template-columns:repeat(auto-fill,minmax(380px,1fr));gap:12px}mark{background:#ff5a5f33;color:#ff9a9d}
pre{white-space:pre-wrap;background:#171a21;padding:12px;border-radius:8px}.row{display:flex;gap:20px;flex-wrap:wrap}.row img{width:270px;border-radius:8px}"""
    page = f"""<!doctype html><html><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'>
<title>Fable 5.2 review</title><style>{css}</style></head><body><main>
<h1>Fable 5.2 deep-dive: everything in one place</h1>
<nav><a href='#spoken'>Spoken script</a><a href='#main'>Main reel visuals</a><a href='#trial'>Trial reel visuals</a><a href='#rules'>User rules card</a><a href='#cuts'>Paper cuts</a><a href='#post'>Caption + cover</a><a href='#table'>Full beat tables</a></nav>
<p style='color:var(--mut)'>Main = CEO hook · Trial = money hook · clips are timed to a synthetic voice and re-time to your real takes after recording · red = still needed from you</p>
<section id='spoken' class='spoken'>{md_to_html(spoken)}</section>
<section id='main'>{reel_block('main', 'Main reel (CEO hook): every beat and its visual')}</section>
<section id='trial'>{reel_block('trial', 'Trial reel (money hook): every beat and its visual')}</section>
<section id='rules'>{md_to_html(rules)}</section>
<section id='cuts'><h2>Paper cuts (highlighted, from the 264-page system card)</h2><div class='cuts'>{cut_html}</div></section>
<section id='post'><h2>Caption + cover</h2><div class='row'><img src='{cover.as_uri()}'><pre>{html.escape(caption)}</pre></div></section>
<section id='table'><h2>Full beat tables</h2>{md_to_html(section(md, 'MAIN REEL'))}{md_to_html(section(md, 'TRIAL REEL'))}</section>
</main></body></html>"""
    OUT.write_text(page)
    print(OUT)


if __name__ == "__main__":
    main()
