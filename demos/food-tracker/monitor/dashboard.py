"""Render the monitoring log into one self-contained HTML file (no network, no JS libraries).

  python monitor/dashboard.py [--out ~/.cache/content_os/food-tracker/dashboard.html]

Shows ONLY what is in the log: every point is a logged run, labelled "eval" (Nutrition5k) or "real meal".
Panels: estimates over time, latency and CLI-reported cost per estimate, item confidence distribution,
error vs ground truth (eval labels, weighed meals, or user corrections), and the alert queue.
"""
import argparse, html, json, statistics as st, sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from monitor.log import LOG, KCAL_PLAUSIBLE, MIN_ITEM_CONF, MAX_RANGE_RATIO, read  # noqa: E402

W, H, PAD = 560, 260, 44
SRC = {"eval": "var(--series-1)", "sim": "var(--series-2)", "real": "var(--series-3)"}
SRC_LABEL = {"eval": "eval (Nutrition5k)", "sim": "simulated meal", "real": "real meal"}


def esc(x):
    return html.escape(str(x))


def axes(xmin, xmax, ymin, ymax, xlab, ylab, xfmt=lambda v: f"{v:.0f}", yfmt=lambda v: f"{v:.0f}"):
    sx = lambda v: PAD + (v - xmin) / ((xmax - xmin) or 1) * (W - PAD - 12)
    sy = lambda v: H - PAD + 10 - (v - ymin) / ((ymax - ymin) or 1) * (H - PAD - 10)
    g = []
    for k in range(5):
        yv = ymin + (ymax - ymin) * k / 4
        g.append(f'<line x1="{PAD}" x2="{W-12}" y1="{sy(yv):.1f}" y2="{sy(yv):.1f}" class="grid"/>'
                 f'<text x="{PAD-6}" y="{sy(yv)+4:.1f}" text-anchor="end" class="tick">{esc(yfmt(yv))}</text>')
    for k in range(5):
        xv = xmin + (xmax - xmin) * k / 4
        anchor = "start" if k == 0 else "end" if k == 4 else "middle"
        g.append(f'<text x="{sx(xv):.1f}" y="{H-PAD+28}" text-anchor="{anchor}" class="tick">{esc(xfmt(xv))}</text>')
    g.append(f'<text x="{W/2}" y="{H-4}" text-anchor="middle" class="lab">{esc(xlab)}</text>'
             f'<text x="12" y="{H/2}" transform="rotate(-90 12 {H/2})" text-anchor="middle" class="lab">{esc(ylab)}</text>')
    return sx, sy, "".join(g)


def svg(body):
    return f'<svg viewBox="0 0 {W} {H+6}" role="img">{body}</svg>'


def dot(x, y, src, tip, r=4.5):
    return (f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{SRC[src]}" stroke="var(--surface)" stroke-width="2">'
            f'<title>{esc(tip)}</title></circle>')


def legend(srcs):
    return "".join(f'<span class="key"><i style="background:{SRC[s]}"></i>{SRC_LABEL[s]}</span>' for s in srcs)


def build(recs):
    ests = [r for r in recs if r["kind"] == "estimate"]
    gts = {r["tag"]: r for r in recs if r["kind"] == "ground_truth"}
    corr = {r["estimate_id"]: r for r in recs if r["kind"] == "correction"}
    if not ests:
        return "<p>No estimates logged yet.</p>"
    for e in ests:
        e["_t"] = datetime.strptime(e["ts"], "%Y-%m-%dT%H:%M:%S%z")
        e["_src"] = "eval" if e["source"] == "eval" else ("sim" if e.get("simulated") else "real")
        e["_truth"] = None
        if e["id"] in corr and corr[e["id"]].get("kcal") is not None:
            e["_truth"], e["_truth_kind"] = corr[e["id"]]["kcal"], "user correction"
        elif e.get("tag") in gts:
            e["_truth"], e["_truth_kind"] = gts[e["tag"]]["kcal"], "Nutrition5k label" if e["_src"] == "eval" else "weighed"
    srcs = sorted({e["_src"] for e in ests})
    n_eval = sum(e["_src"] == "eval" for e in ests)
    n_sim = sum(e["_src"] == "sim" for e in ests)
    n_real = len(ests) - n_eval - n_sim
    n_alert = sum(e["needs_confirmation"] for e in ests)
    lat = [e["latency_s"] for e in ests]
    cost = [e["cost_usd_cli"] for e in ests]

    # 1. estimates over time
    t0 = min(e["_t"] for e in ests).timestamp()
    t1 = max(e["_t"] for e in ests).timestamp()
    kmax = max(max(e["totals"]["kcal"] for e in ests), KCAL_PLAUSIBLE[1] * 0.6)
    span_h = max((t1 - t0) / 3600, 1 / 60)
    tfmt = (lambda v: datetime.fromtimestamp(t0 + v * 3600).strftime("%d %b")) if span_h > 48 else \
           (lambda v: datetime.fromtimestamp(t0 + v * 3600).strftime("%H:%M"))
    sx, sy, g = axes(0, span_h, 0, kmax, "time logged", "kcal estimate", xfmt=tfmt)
    body = g + f'<line x1="{PAD}" x2="{W-12}" y1="{sy(KCAL_PLAUSIBLE[0]):.1f}" y2="{sy(KCAL_PLAUSIBLE[0]):.1f}" class="thr"/>'
    body += "".join(dot(sx((e["_t"].timestamp() - t0) / 3600), sy(e["totals"]["kcal"]), e["_src"],
                        f'{e["ts"]} | {SRC_LABEL[e["_src"]]} | {e["mode"]} | {e["model"]} | {e["totals"]["kcal"]:.0f} kcal'
                        + (" | ALERT" if e["needs_confirmation"] else "")) for e in ests)
    p1 = svg(body)

    # 2. latency vs cost
    cap = min(max(lat), 60)
    off = sum(l > cap for l in lat)
    sx, sy, g = axes(0, cap * 1.05, 0, max(cost) * 1.1,
                     "latency per estimate (s)" + (f"; {off} runs over {cap:.0f} s pinned at right edge" if off else ""),
                     "CLI-reported cost (USD)", yfmt=lambda v: f"{v:.2f}")
    p2 = svg(g + "".join(dot(sx(min(e["latency_s"], cap * 1.05)), sy(e["cost_usd_cli"]), e["_src"],
                             f'{e["mode"]} | {e["model"]} | {e["latency_s"]} s | ${e["cost_usd_cli"]:.3f} | {e["n_calls"]} calls')
                         for e in ests))

    # 3. confidence histogram (items)
    confs = [(i["confidence"], e["_src"]) for e in ests for i in e["items"] if i.get("confidence") is not None]
    bins = [k / 10 for k in range(11)]
    counts = {s: [0] * 10 for s in srcs}
    for c, s in confs:
        counts[s][min(int(c * 10), 9)] += 1
    cmax = max(sum(counts[s][b] for s in srcs) for b in range(10)) or 1
    sx, sy, g = axes(0, 1, 0, cmax, "model-stated item confidence", "items", xfmt=lambda v: f"{v:.2f}")
    body = g + f'<line x1="{sx(MIN_ITEM_CONF):.1f}" x2="{sx(MIN_ITEM_CONF):.1f}" y1="{sy(0):.1f}" y2="{sy(cmax):.1f}" class="thr"/>'
    bw = (sx(0.1) - sx(0)) - 2
    for b in range(10):
        base = 0
        for s in srcs:
            v = counts[s][b]
            if v:
                body += (f'<rect x="{sx(bins[b])+1:.1f}" y="{sy(base+v):.1f}" width="{bw:.1f}" height="{sy(base)-sy(base+v):.1f}" '
                         f'fill="{SRC[s]}" stroke="var(--surface)" stroke-width="2"><title>{SRC_LABEL[s]}: {v} items with confidence '
                         f'{bins[b]:.1f}-{bins[b+1]:.1f}</title></rect>')
                base += v
    p3 = svg(body)

    # 4. error vs truth
    wt = [e for e in ests if e["_truth"] is not None]
    if wt:
        m = max(max(e["_truth"] for e in wt), max(e["totals"]["kcal"] for e in wt)) * 1.05
        sx, sy, g = axes(0, m, 0, m, "ground truth kcal", "estimated kcal")
        body = g + f'<line x1="{sx(0):.1f}" y1="{sy(0):.1f}" x2="{sx(m):.1f}" y2="{sy(m):.1f}" class="ref"/>'
        body += "".join(dot(sx(e["_truth"]), sy(e["totals"]["kcal"]), e["_src"],
                            f'{e.get("tag")} | {e["mode"]} | {e["model"]} | est {e["totals"]["kcal"]:.0f} vs {e["_truth_kind"]} {e["_truth"]:.0f} kcal')
                        for e in wt)
        p4 = svg(body)
        errs = {}
        for e in wt:
            errs.setdefault((e["_src"], e["mode"], e["model"]), []).append(abs(e["totals"]["kcal"] - e["_truth"]))
        err_rows = "".join(f"<tr><td>{SRC_LABEL[s]}</td><td>{md}</td><td>{mo}</td><td>{len(v)}</td><td>{st.mean(v):.0f}</td></tr>"
                           for (s, md, mo), v in sorted(errs.items()))
    else:
        p4, err_rows = "<p class='muted'>No ground truth or corrections logged yet.</p>", ""

    # 5. alert queue
    al = sorted([e for e in ests if e["needs_confirmation"]], key=lambda e: e["ts"], reverse=True)
    alert_rows = "".join(f"<tr><td>{esc(e['ts'][:16])}</td><td>{SRC_LABEL[e['_src']]}</td><td>{esc(e.get('tag') or '')}</td>"
                         f"<td>{esc(e['mode'])}</td><td>{e['totals']['kcal']:.0f}</td><td>{esc('; '.join(e['alerts']))}</td></tr>"
                         for e in al[:40])

    tiles = "".join(f'<div class="tile"><div class="v">{v}</div><div class="k">{k}</div></div>' for k, v in [
        ("logged estimates", len(ests)), ("eval runs (Nutrition5k)", n_eval), ("simulated meals", n_sim), ("real meals", n_real),
        ("flagged: ask user to confirm", f"{n_alert} ({n_alert/len(ests)*100:.0f}%)"),
        ("median latency", f"{st.median(lat):.1f} s"), ("median CLI-reported cost", f"${st.median(cost):.3f}")])
    rule = (f"Alert rule: ask the user to confirm when total kcal is outside {KCAL_PLAUSIBLE[0]} to {KCAL_PLAUSIBLE[1]}, "
            f"any item confidence is below {MIN_ITEM_CONF}, a table match is weak, or the kcal range is wider than "
            f"{int(MAX_RANGE_RATIO*100)}% of the estimate.")
    return f"""
<div class="tiles">{tiles}</div>
<p class="muted">{esc(rule)} Every point below is a logged record. Eval runs are real model calls on Nutrition5k; points marked simulated are generated by monitor/simulate_usage.py, not real meals.
Cost is what the Claude Code CLI reports (total_cost_usd); for some models it marks the cost basis as unknown.</p>
<div class="legend">{legend(srcs)}</div>
<div class="grid2">
<section><h2>Estimates over time</h2>{p1}</section>
<section><h2>Latency and cost per estimate</h2>{p2}</section>
<section><h2>Item confidence distribution</h2>{p3}</section>
<section><h2>Estimate vs ground truth</h2>{p4}
<table><tr><th>source</th><th>mode</th><th>model</th><th>n</th><th>kcal MAE</th></tr>{err_rows}</table></section>
</div>
<section><h2>Alert queue (latest 40)</h2><table><tr><th>time</th><th>source</th><th>tag</th><th>mode</th><th>kcal</th><th>why</th></tr>{alert_rows}</table></section>
"""


CSS = """
:root{--surface:#fcfcfb;--bg:#f4f3ef;--ink:#0b0b0b;--ink2:#52514e;--muted:#8a8984;--grid:#e4e3de;
--series-1:#2a78d6;--series-2:#eb6834;--series-3:#1baf7a;--thr:#e34948}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--surface:#1a1a19;--bg:#111110;--ink:#f0efec;--ink2:#c3c2b7;
--muted:#8f8e86;--grid:#2e2e2c;--series-1:#3987e5;--series-2:#d95926;--series-3:#199e70;--thr:#e66767}}
:root[data-theme="dark"]{--surface:#1a1a19;--bg:#111110;--ink:#f0efec;--ink2:#c3c2b7;--muted:#8f8e86;--grid:#2e2e2c;
--series-1:#3987e5;--series-2:#d95926;--series-3:#199e70;--thr:#e66767}
.simtag{position:fixed;top:10px;right:12px;background:var(--surface);color:var(--ink2);border:1px solid var(--grid);
border-radius:999px;padding:3px 10px;font-size:12px;letter-spacing:.02em}
body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.45 -apple-system,system-ui,sans-serif}
main{max-width:1200px;margin:0 auto;padding:24px 16px}
h1{font-size:26px;margin:0 0 4px}h2{font-size:16px;margin:0 0 8px;color:var(--ink2)}
.tiles{display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:12px;margin:16px 0}
.tile,section{background:var(--surface);border-radius:10px;padding:14px}
.tile .v{font-size:26px;font-weight:650}.tile .k{color:var(--ink2);font-size:13px}
.grid2{display:grid;grid-template-columns:repeat(auto-fit,minmax(420px,1fr));gap:12px;margin-bottom:12px}
svg{width:100%;height:auto}.grid{stroke:var(--grid);stroke-width:1}.tick{fill:var(--muted);font-size:11px}
.lab{fill:var(--ink2);font-size:12px}.thr{stroke:var(--thr);stroke-dasharray:4 4;stroke-width:1.5}.ref{stroke:var(--muted);stroke-width:1.5;stroke-dasharray:2 3}
.muted{color:var(--ink2)}.legend{margin:8px 0}.key{margin-right:16px;color:var(--ink2)}
.key i{display:inline-block;width:10px;height:10px;border-radius:5px;margin-right:6px}
table{border-collapse:collapse;width:100%;font-size:13px;margin-top:8px}td,th{text-align:left;padding:4px 6px;border-bottom:1px solid var(--grid)}
@media (max-width:520px){.grid2{grid-template-columns:1fr}}
"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(LOG.parent / "dashboard.html"))
    ap.add_argument("--logs", nargs="+", default=[str(LOG)], help="JSONL logs to combine (e.g. add simulated_usage.jsonl)")
    ap.add_argument("--theme", choices=["auto", "light", "dark"], default="auto")
    a = ap.parse_args()
    recs = [json.loads(l) for f in a.logs if Path(f).exists() for l in open(f) if l.strip()]
    sim = any(r.get("simulated") for r in recs)
    theme = "" if a.theme == "auto" else f' data-theme="{a.theme}"'
    page = (f"<!doctype html><html{theme}><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'>"
            f"<title>Food Tracker Monitor</title><style>{CSS}</style></head><body><main><h1>Food tracker monitor</h1>"
            f"<p class='muted'>Rendered {datetime.now():%Y-%m-%d %H:%M} from: {esc(', '.join(Path(f).name for f in a.logs))}.</p>"
            + (f"<div class='simtag'>simulated usage data</div>" if sim else "") + f"{build(recs)}</main></body></html>")
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    Path(a.out).write_text(page)
    print(a.out)


if __name__ == "__main__":
    main()
