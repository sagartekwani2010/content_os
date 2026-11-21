"""Script factory CLI.

  python -m content_os.factory taste                         # (re)build production/CREATOR_TASTE.md with Fable
  python -m content_os.factory run --brief B.md --facts F.md --out outputs/<reel>/factory [--only A,B]
  python -m content_os.factory revise outputs/<reel>/factory A "creator notes..."
  python -m content_os.factory usage [--days 7]              # model calls and time per model this week
"""
from __future__ import annotations

import argparse
import json
import subprocess
import time
from collections import defaultdict
from pathlib import Path

from . import taste, tournament
from .llm import REPO


def main() -> None:
    ap = argparse.ArgumentParser(prog="content_os.factory")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("taste")
    r = sub.add_parser("run")
    r.add_argument("--brief", type=Path, required=True)
    r.add_argument("--facts", type=Path)
    r.add_argument("--out", type=Path, required=True)
    r.add_argument("--only", default="")
    r.add_argument("--open", action="store_true")
    v = sub.add_parser("revise")
    v.add_argument("out", type=Path)
    v.add_argument("variant")
    v.add_argument("notes")
    v.add_argument("--open", action="store_true")
    u = sub.add_parser("usage")
    u.add_argument("--days", type=int, default=7)
    a = ap.parse_args()

    if a.cmd == "taste":
        print(taste.build(REPO / "outputs/_factory/ledger.jsonl"))
    elif a.cmd == "run":
        page = tournament.run(a.brief, a.facts, a.out, [x for x in a.only.split(",") if x])
        print(page)
        if a.open:
            subprocess.run(["open", str(page)])
    elif a.cmd == "revise":
        page = tournament.revise(a.out, a.variant, a.notes)
        print(page)
        if a.open:
            subprocess.run(["open", str(page)])
    elif a.cmd == "usage":
        cutoff = time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(time.time() - a.days * 86400))
        agg: dict[str, list[float]] = defaultdict(lambda: [0, 0.0, 0])
        for f in list(REPO.glob("outputs/*/factory/ledger.jsonl")) + [REPO / "outputs/_factory/ledger.jsonl"]:
            if not f.exists():
                continue
            for line in f.read_text().splitlines():
                d = json.loads(line)
                if "model" in d and d.get("at", "") >= cutoff:
                    x = agg[d["model"]]
                    x[0] += 1
                    x[1] += d["seconds"]
                    x[2] += d["chars_in"] + d["chars_out"]
        for m, (n, s, c) in sorted(agg.items()):
            print(f"{m:22s} {n:4d} calls  {s / 60:6.1f} min  ~{c / 4 / 1000:,.0f}k tokens")


if __name__ == "__main__":
    main()
