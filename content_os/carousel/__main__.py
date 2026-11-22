"""python -m content_os.carousel render outputs/<id> [--only 2,5]"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .render import render


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="python -m content_os.carousel")
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("render", help="render slides.json to JPEG/MP4, POST/, contact sheet and PREVIEW.html")
    r.add_argument("folder", type=Path)
    r.add_argument("--only", help="comma-separated slide numbers to re-render (others are reused)")
    a = ap.parse_args(argv)
    only = [int(x) for x in a.only.split(",")] if a.only else None
    rep = render(a.folder, only)
    for s in rep["slides"]:
        print(f"{s['name']}: {s.get('file')}")
    for i in rep["issues"]:
        print("QA:", i)
    print(json.dumps({"slides": len(rep["slides"]), "issues": len(rep["issues"])}))
    return 1 if rep["issues"] else 0


if __name__ == "__main__":
    sys.exit(main())
