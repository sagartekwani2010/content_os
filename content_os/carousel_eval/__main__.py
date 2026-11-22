"""python -m content_os.carousel_eval check <id>     deterministic checks only (free)
   python -m content_os.carousel_eval eval <id>      checks + Fable engagement judge + Opus visual review (2 calls)
   python -m content_os.carousel_eval monitor        what Codex changed since the last look
   python -m content_os.carousel_eval monitor --scheduled   (launchd, every 2 days) report + Opus review
   python -m content_os.carousel_eval seal           record Claude-owned file hashes (after Claude edits them)
"""
from __future__ import annotations

import argparse
import json
import sys
import time

from . import checks, judge, monitor
from .contract import load


def _verdict(issues: list[dict], eng: dict | None, vis: dict | None) -> str:
    if any(i["level"] == "block" for i in issues):
        return "FAIL"
    if eng is None or vis is None:
        return "CHECKS-ONLY"
    vis_block = any(i.get("severity") == "block" for i in vis.get("issues", []))
    if eng["weighted"] >= judge.GATE and not vis_block and vis.get("legibility_ok", False):
        return "PASS"
    return "REVISE"


def _write(sub, issues, eng, vis) -> str:
    d = sub.eval_dir
    d.mkdir(parents=True, exist_ok=True)
    verdict = _verdict(issues, eng, vis)
    data = {"id": sub.id, "version": sub.version, "at": time.strftime("%Y-%m-%dT%H:%M:%S"), "verdict": verdict,
            "checks": issues, "engagement": eng, "visual": vis}
    (d / "eval.json").write_text(judge.to_json(data))
    md = [f"# Evaluation · {sub.id} · {sub.version} · {verdict}", ""]
    if eng:
        md += [f"**Fable engagement (blind): {eng['weighted']}/10** (gate {judge.GATE}). "
               f"Panel: {eng.get('stop')}/16 stop, {eng.get('swipe_to_end')}/16 swipe to end, {eng.get('save')}/16 save.",
               f"Verdict: {eng.get('one_line_verdict', '')}", "",
               "Scores: " + ", ".join(f"{k} {v}" for k, v in eng["scores"].items()), ""]
    if vis:
        md += [f"**Opus visual review: {vis.get('visual_score')}/10**, legible on phone: {vis.get('legibility_ok')}. "
               f"{vis.get('one_line_verdict', '')}", ""]
    fixes = [i for i in issues if i["level"] != "note"]
    md.append("## Must fix (deterministic checks)")
    md += [f"- [{i['level']}] {i['where']}: {i['msg']}" for i in fixes] or ["- none"]
    if eng:
        md.append("\n## Top fixes (Fable)")
        md += [f"{n}. {f}" for n, f in enumerate(eng.get("top_3_fixes", []), 1)]
        md += [f"- slide {w['n']}: {w['why']} → {w['fix']}" for w in eng.get("weakest_slides", [])]
        md += [f"- rule break: {r}" for r in eng.get("rule_breaks", [])]
    if vis:
        md.append("\n## Visual issues (Opus)")
        md += [f"- [{i.get('severity')}] slide {i.get('n')}: {i.get('issue')} → {i.get('fix')}"
               for i in vis.get("issues", [])] or ["- none"]
        md += [f"- honesty: {h}" for h in vis.get("honesty_flags", [])]
    md += ["", "Codex: fix the items above, bump `version` in SUBMISSION.json, and resubmit. "
           "Do not edit this folder."]
    (d / "EVAL.md").write_text("\n".join(md) + "\n")
    return verdict


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="content_os.carousel_eval")
    sp = ap.add_subparsers(dest="cmd", required=True)
    for c in ("check", "eval"):
        sp.add_parser(c).add_argument("carousel")
    mp = sp.add_parser("monitor")
    mp.add_argument("--scheduled", action="store_true", help="report + Opus review, saved to _monitor/, notify")
    sp.add_parser("seal")
    a = ap.parse_args(argv)

    if a.cmd == "monitor":
        print(monitor.run_scheduled() if a.scheduled else monitor.report())
        return 0
    if a.cmd == "seal":
        print(f"sealed {monitor.seal()} Claude-owned files")
        return 0

    sub, problems = load(a.carousel)
    if sub is None:
        print("FAIL: " + "; ".join(problems))
        return 2
    issues = checks.run_all(sub)
    eng = vis = None
    if a.cmd == "eval" and not any(i["level"] == "block" for i in issues):
        ledger = sub.eval_dir / "ledger.jsonl"
        eng = judge.engagement(sub, ledger)
        vis = judge.visual(sub, ledger)
    verdict = _write(sub, issues, eng, vis)
    print(f"{verdict}: {sub.eval_dir / 'EVAL.md'}")
    print(json.dumps([i for i in issues if i["level"] != "note"], indent=1, ensure_ascii=False))
    return 0 if verdict in ("PASS", "CHECKS-ONLY") else 1


if __name__ == "__main__":
    sys.exit(main())
