"""Still panels for Evals Ep 1 (SCRIPT_v13_FINAL.md), 1080x960 top-half visuals, bottom 100 px kept clear for captions.

Every number and quote is read from m2c_eval/ result files or JOB_POSTINGS_EVIDENCE.md facts.
python build_assets.py  ->  ~/Movies/ContentOS/evals-ep1/assets/A??.png (media stays out of Git)
"""
import html
import json
import subprocess
import tempfile
from pathlib import Path

HERE = Path(__file__).parent
EVAL = HERE.parent / "m2c_eval"
OUT = Path.home() / "Movies/ContentOS/evals-ep1/assets"
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
E = html.escape

CSS = """
@import url('https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@500;700;800&family=Inter:wght@400;600;700&display=swap');
:root{--bg:#0B0F17;--panel:#131A26;--ink:#F2F5FA;--mute:#8A97AD;--cyan:#35E0FF;--green:#3DDC84;--red:#FF4D5E;--amber:#FFB547}
*{box-sizing:border-box;margin:0;padding:0}
body{width:1080px;height:960px;background:var(--bg);color:var(--ink);font-family:Inter,sans-serif;overflow:hidden}
.safe{position:absolute;left:60px;right:60px;top:56px;bottom:156px;display:flex;flex-direction:column;justify-content:center;gap:26px}
.kicker{font-family:'Barlow Condensed';font-weight:700;letter-spacing:.08em;color:var(--cyan);font-size:34px;text-transform:uppercase}
.big{font-family:'Barlow Condensed';font-weight:800;font-size:120px;line-height:.95;text-transform:uppercase}
.h{font-family:'Barlow Condensed';font-weight:800;font-size:64px;line-height:1.02;text-transform:uppercase}
.card{background:var(--panel);border:2px solid #22304A;border-radius:22px;padding:28px 32px}
.small{color:var(--mute);font-size:22px}
.msg{display:flex;gap:18px;align-items:flex-start;font-size:30px;line-height:1.3}
.av{width:58px;height:58px;border-radius:12px;flex:none;display:flex;align-items:center;justify-content:center;font-weight:700;font-size:24px}
.who{font-weight:700}
table{border-collapse:collapse;width:100%;font-size:26px}
td,th{padding:9px 12px;text-align:left;border-bottom:1px solid #22304A}
th{color:var(--mute);font-weight:600;font-size:21px}
.red{color:var(--red)}.green{color:var(--green)}.cyan{color:var(--cyan)}.amber{color:var(--amber)}
.row{display:flex;gap:22px;align-items:center}
.check{display:flex;gap:20px;align-items:center;font-size:32px;padding:12px 0;border-bottom:1px solid #22304A}
.box{width:52px;height:52px;border-radius:10px;border:3px solid var(--mute);flex:none;display:flex;align-items:center;justify-content:center;font-size:36px;font-weight:800}
.ok{border-color:var(--green);color:var(--green)}.no{border-color:var(--red);color:var(--red)}
.stamp{position:absolute;right:70px;bottom:190px;transform:rotate(-12deg);border:8px solid var(--red);color:var(--red);font-family:'Barlow Condensed';font-weight:800;font-size:110px;padding:0 26px;border-radius:14px}
.pill{display:inline-block;padding:8px 18px;border-radius:999px;background:#1C2738;font-size:24px;color:var(--mute)}
"""


def page(body: str) -> str:
    return f"<!doctype html><html><head><meta charset='utf-8'><style>{CSS}</style></head><body>{body}</body></html>"


def render(name: str, body: str) -> None:
    with tempfile.NamedTemporaryFile("w", suffix=".html", delete=False) as f:
        f.write(page(body))
    subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars", f"--screenshot={OUT / (name + '.png')}",
                    "--window-size=1080,960", "--virtual-time-budget=4000", f"file://{f.name}"],
                   check=True, capture_output=True)


def load():
    case = next(c for c in json.loads((EVAL / "cases.json").read_text())["cases"] if c["id"] == "M1")
    rows = json.loads((EVAL / "results_hard.json").read_text())["rows"]
    pick = lambda v, r: next(x for x in rows if x["version"] == v and x["case"] == "M1" and x["run"] == r)
    return case, rows, pick


def first_heading(text: str) -> str:
    """The slide's own headline: the first markdown heading, else the first long line."""
    for line in text.splitlines():
        s = line.strip()
        if s.startswith("#"):
            s = s.lstrip("#").strip().replace("**", "")
            s = s[6:].strip() if s.lower().startswith("slide:") else s
            if len(s) > 25:
                return s
    for line in text.splitlines():
        s = line.strip().lstrip("#").strip().replace("**", "")
        if s.lower().startswith("slide:"):
            s = s[6:].strip()
        if len(s) > 25 and not s.lower().startswith(("recommendation", "here")):
            return s
    return ""


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    case, rows, pick = load()
    h1, f3 = pick("hard_v0_haiku", 1), pick("hard_v0_fable", 3)
    hero_hk = [pick("hard_v0_haiku", r)["exam"]["pass"] for r in (1, 2, 3)]
    hero_fb = [pick("hard_v0_fable", r)["exam"]["pass"] for r in (1, 2, 3)]
    tot = lambda v: sum(bool(x["exam"]["pass"]) for x in rows if x["version"] == v)
    city = case["data_hard"].split("PRICING HEAD'S ANALYSIS (attached)")[1].split("\n\n")[0].strip().splitlines()[2:]
    marks = lambda xs: " ".join(f"<span class='{'green' if p else 'red'}'>{'✔' if p else '✘'}</span>" for p in xs)

    render("A01", """<div class='safe'><div class='kicker'>Cutting jobs</div>
      <div class='card'><div class='row'><div class='h'>Salesforce</div><div class='small'>Marc Benioff, 2025</div></div>
      <div class='big' style='font-size:96px'>support <span class='red'>~9,000 → ~5,000</span></div></div>
      <div class='card'><div class='row'><div class='h'>Google</div><div class='small'>2026 cuts, as reported</div></div></div>
      <div class='kicker'>…and still hiring</div>
      <div class='card' style='font-size:30px'><b>LMTS - Lead AI/ML Engineer (LLM Post-Training)</b> <span class='small'>· Salesforce · Bangalore</span><br><br>
      <b>Staff Software Engineer, Search Evals</b> <span class='small'>· Google · Bengaluru</span></div></div>""")
    render("A02", """<div class='safe'><div class='kicker'>Frontier labs, hiring in India</div>
      <div class='card' style='font-size:32px'><b>Applied AI Engineer</b> <span class='small'>· OpenAI · Delhi</span><br><br>
      <b>Applied AI Architect</b> <span class='small'>· Anthropic · Bangalore</span></div>
      <div class='card' style='border-color:var(--cyan);font-size:38px;line-height:1.35'>“Help customers develop <span class='cyan'><b>evaluation frameworks</b></span>
      to measure Claude's performance for their specific use cases”<div class='small' style='margin-top:14px'>Anthropic job posting, Applied AI Architect, Bangalore</div></div></div>""")
    render("A03", "<div class='safe' style='align-items:center;text-align:center'><div class='kicker'>Evals for every job · Ep 1</div><div class='big'>What is<br>an eval?</div><div class='pill'>one consulting problem</div></div>")
    render("A04", f"""<div class='safe'><div class='small'># leadership · Friday, 9:40 pm</div>
      <div class='big'>M2C <span class='red'>{case['headline_change']:+.0%}</span></div>
      <div class='h' style='font-size:44px;color:var(--mute)'>menu → add-to-cart conversion</div>
      <div class='pill'>a food-delivery app like Swiggy · simulated data</div></div>""")
    render("A05", """<div class='safe' style='align-items:center'><div class='row' style='gap:60px'>
      <div class='card h' style='font-size:56px'>📖 Menu</div><div class='big red' style='font-size:90px'>→</div><div class='card h' style='font-size:56px'>🛒 Cart</div></div>
      <div class='h' style='font-size:46px;color:var(--mute)'>far fewer people add anything</div></div>""")
    rows_html = "".join("<tr>" + "".join(f"<td>{E(c.strip())}</td>" for i, c in enumerate(r.strip('|').split('|')) if i in (0, 5, 6, 7)) + "</tr>" for r in city)
    render("A06", f"""<div class='safe' style='gap:18px'>
      <div class='card msg'><div class='av' style='background:#2B6CB0'>PH</div><div><span class='who'>Pricing head</span><br>It's the new delivery fee. Users see Rs 39 on the menu and leave.</div></div>
      <div class='card' style='padding:16px 26px'><table><tr><th>City</th><th>M2C LW</th><th>M2C TW</th><th>Change</th></tr>{rows_html}</table></div>
      <div class='card msg'><div class='av' style='background:#9B2C2C'>CEO</div><div><span class='who'>CEO</span><br>Agreed. I want the fix live by <span class='red'><b>Monday</b></span>.</div></div></div>""")
    render("A08", f"""<div class='safe'><div class='kicker'>The usual move</div>
      <div class='card' style='font-size:36px;line-height:1.4'><span class='small'>Prompt</span><br>{E(case['ask_hard'])}<span class='cyan'>▍</span></div>
      <div class='small'>+ the Slack thread, the analysis and the raw data export</div></div>""")
    render("A10", "<div class='safe' style='align-items:center;text-align:center'><div class='big'>Eval <span class='cyan'>on</span></div><div class='h' style='font-size:44px;color:var(--mute)'>before I trust any slide</div></div>")
    checks = ["Did it check whether orders actually fell?", "Did it call it a tracking problem?", "Did it fix tracking before any business action?",
              "Never: roll back the delivery fee", "Never: call it a loss of customers"]
    render("A11", "<div class='safe' style='gap:6px'><div class='kicker'>Yes / no checks · written before any run</div>" + "".join(
        f"<div class='check'><div class='box'></div><span class='{'red' if c.startswith('Never') else ''}'>{E(c)}</span></div>" for c in checks) + "</div>")
    ex = {k["id"]: k["ok"] for k in h1["exam"]["checks"]}
    order = ["I1", "I2", "I3", "N1", "N2"]
    title = first_heading(h1["answer"])
    render("A12", f"<div class='safe' style='gap:6px'><div class='card' style='font-size:26px;margin-bottom:14px'><span class='small'>The AI's slide · Claude Haiku 5.5 · run 1</span><br><b>{E(title)}</b></div>"
           + "".join(f"<div class='check'><div class='box {'ok' if ex[i] else 'no'}'>{'✔' if ex[i] else '✘'}</div><span>{E(c)}</span></div>" for i, c in zip(order, checks))
           + f"<div class='stamp'>{'PASS' if h1['exam']['pass'] else 'FAIL'}</div><div class='small' style='margin-top:10px'>Checker: Claude Opus 5.5, blind, quoting the slide</div></div>")
    render("A13", """<div class='safe'><div class='kicker'>Answer key · written before the AI runs</div>
      <div class='card h' style='font-size:58px'>Android v8.4 broke add-to-cart <span class='cyan'>tracking</span></div>
      <div class='card'><div class='row'><div class='h' style='font-size:52px'>Orders</div><div class='big green' style='font-size:100px'>6.9 → 7.1 lakh ↑</div></div></div>
      <div class='pill'>simulated data</div></div>""")
    render("A14", "<div class='safe' style='align-items:center;text-align:center'><div class='big'>× 3 runs</div><div class='h' style='font-size:44px;color:var(--mute)'>one good answer can be luck</div></div>")
    render("A15", f"""<div class='safe' style='align-items:center;text-align:center'><div class='kicker'>The cheaper AI most companies deploy</div>
      <div class='h'>Claude Haiku 5.5</div><div class='big' style='font-size:180px;letter-spacing:.12em'>{marks(hero_hk)}</div>
      <div class='h' style='font-size:44px;color:var(--mute)'>failed {hero_hk.count(False)} runs out of 3</div></div>""")
    render("A16", """<div class='safe'><div class='kicker'>Its leadership ask (run 1, verbatim)</div>
      <div class='card' style='font-size:46px;line-height:1.3;border-color:var(--red)'>“Approve the Android v8.4 hotfix or rollback as the Monday fix.”</div>
      <div class='h' style='font-size:42px;color:var(--mute)'>skipped: is this just broken tracking?</div></div>""")
    render("A18", f"""<div class='safe' style='align-items:center;text-align:center'><div class='kicker'>The premium AI</div><div class='h'>Claude Fable 5.2</div>
      <div class='big' style='font-size:180px;letter-spacing:.12em'>{marks(hero_fb)}</div>
      <div class='card' style='font-size:34px'>All 10 cases × 3 runs: <b class='green'>Fable {tot('hard_v0_fable')}/30</b> · <b class='amber'>Haiku {tot('hard_v0_haiku')}/30</b></div></div>""")
    render("A19", """<div class='safe'><div class='kicker'>How to put an eval on any AI</div>""" + "".join(
        f"<div class='card h' style='font-size:52px'><span class='cyan'>{i}</span> &nbsp;{t}</div>" for i, t in
        [(1, "Answer key, written first"), (2, "Yes / no checks"), (3, "A separate AI checker"), (4, "Every answer × 3 runs")]) + "</div>")
    render("A20", f"""<div class='safe'><div class='kicker'>The slide you can trust</div>
      <div class='card' style='font-size:40px;line-height:1.3;border-color:var(--green)'><b>{E(first_heading(f3['answer']))}</b></div>
      <div class='big green' style='font-size:110px'>✔ ✔ ✔ ✔ ✔</div><div class='small'>Claude Fable 5.2 · run 3 · all checks passed</div></div>""")
    render("A21", "<div class='safe' style='align-items:center;text-align:center'><div class='h' style='font-size:50px;color:var(--mute)'>My framework for writing good evals</div><div class='big'>Comment<br><span class='cyan'>EVAL</span></div></div>")
    print("rendered to", OUT)


if __name__ == "__main__":
    main()
