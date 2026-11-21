"""Live review page: every round's takes (spoken lines, on-screen text) with panel scores + checker notes.
Usage: python make_review_live.py rounds_notes  -> REVIEW_LIVE.html (rerun after each round)."""
import html, json, re, sys
from pathlib import Path
R = Path(sys.argv[1]); e = html.escape
def rows(md, sec="MAIN"):
    m = re.search(r"^## " + sec + r"\b.*?\n(\|.*?)(?:\n\n|\n#|\Z)", md, re.S | re.M)
    if not m: return []
    out = []
    for r in [r for r in m.group(1).splitlines() if r.startswith("|")][2:]:
        c = [x.strip() for x in r.strip("|").split("|")]
        if len(c) >= 6: out.append((c[0], c[1], c[3].strip('"'), c[5]))
    return out
log = json.loads((R / "log.json").read_text()) if (R / "log.json").exists() else []
parts = []
for n in sorted({int(p.name[1:].split("_")[0]) for p in R.glob("r*_*.md") if p.name[1].isdigit()}, reverse=True):
    sc = json.loads((R / f"r{n}_scores.json").read_text()) if (R / f"r{n}_scores.json").exists() else {}
    parts.append(f"<h2>Round {n}</h2><div class='grid'>")
    for k in "ABC":
        f = R / f"r{n}_{k}.md"
        if not f.exists(): continue
        md = f.read_text(); s = sc.get(k, {})
        chk = R / f"r{n}_{k}_CHECK.md"
        g = s.get("groups", {})
        body = "".join(f"<tr><td>{e(a)}</td><td>{e(b)}</td><td class=sp>{e(c)}</td><td class=os>{e(d)}</td></tr>" for a, b, c, d in rows(md))
        changed = md.split("## WHAT CHANGED")[-1] if "## WHAT CHANGED" in md else ""
        parts.append(f"<div class=card><h3>Take {k} · score {s.get('overall','…')}</h3><p class=g>mass {g.get('mass','')} · fin/consult/mktg {g.get('fin_consult_mktg','')} · builders {g.get('builders','')}</p>"
                     f"<table><tr><th>#</th><th>E/H</th><th>Spoken</th><th>On screen</th></tr>{body}</table>"
                     + (f"<details><summary>Checker</summary><pre>{e(chk.read_text())}</pre></details>" if chk.exists() else "")
                     + (f"<details><summary>What changed</summary><pre>{e(changed.strip())}</pre></details>" if changed else "") + "</div>")
    parts.append("</div>")
page = f"""<!doctype html><html lang=en><head><meta charset=utf-8><meta name=viewport content="width=device-width,initial-scale=1"><title>Script Review Live</title>
<meta http-equiv=refresh content=60><style>body{{margin:0;background:#03121c;color:#ebfaff;font-family:Inter,system-ui,sans-serif}}main{{max-width:1500px;margin:0 auto;padding:24px 16px}}
h1{{margin:0 0 6px}}h2{{color:#35e0ff;border-left:4px solid #35e0ff;padding-left:10px;margin-top:36px}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(420px,1fr));gap:16px}}
.card{{background:#062233;border:1px solid #1f4a5e;padding:14px}}h3{{margin:0}}.g{{color:#7fa3b3;margin:4px 0 10px}}table{{width:100%;border-collapse:collapse;font-size:14px}}
td,th{{border-bottom:1px solid #12384a;padding:6px;vertical-align:top;text-align:left}}.sp{{font-weight:600}}.os{{color:#7fa3b3;font-size:12px}}pre{{white-space:pre-wrap;font-size:12px;color:#cfe7f0}}</style></head>
<body><main><h1>Script review · live</h1><p class=g>Refreshes every 60 s. Send feedback in chat; it goes into creator_feedback.md and the next round uses it. Rounds so far: {e(json.dumps([{'round':r['round'],'best':r['winner'],'score':r['overall']} for r in log]))}</p>{''.join(parts)}</main></body></html>"""
(R.parent / "REVIEW_LIVE.html").write_text(page); print(R.parent / "REVIEW_LIVE.html")
