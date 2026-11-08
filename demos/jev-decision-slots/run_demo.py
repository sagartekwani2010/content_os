#!/usr/bin/env python3
"""Show or execute five Jev-style decision contracts.

This demo has no hidden fallback and never invents a model response. By default
it prints the exact JSON payload a live decision endpoint would receive. Add
--live only when a valid server-side API key and endpoint are configured.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parent
FIXTURES = ROOT / "fixtures.json"
DEFAULT_ENDPOINT = "https://api.typesafe.ai/v1/systemone"


def load_cases() -> tuple[dict[str, object], dict[str, dict[str, object]]]:
    payload = json.loads(FIXTURES.read_text(encoding="utf-8"))
    cases = {case["id"]: case for case in payload["cases"]}
    return payload, cases


def request_payload(case: dict[str, object], model: str) -> dict[str, object]:
    return {"model": model, "state": case["state"], "questions": case["questions"]}


def call_live(endpoint: str, api_key: str, payload: dict[str, object]) -> object:
    body = json.dumps(payload).encode("utf-8")
    request = Request(
        endpoint,
        data=body,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
        method="POST",
    )
    try:
        with urlopen(request, timeout=30) as response:
            return json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Live API returned HTTP {exc.code}: {detail}") from exc
    except URLError as exc:
        raise RuntimeError(f"Could not reach the configured Jev endpoint: {exc.reason}") from exc


def print_case(case: dict[str, object], model: str, *, live: bool) -> None:
    print(f"\n=== {case['id']}: {case['title']} ===")
    print(f"Why this is a decision slot: {case['why']}")
    payload = request_payload(case, model)
    if not live:
        print("\nDRY RUN — request payload only; no model result is being claimed.")
        print(json.dumps(payload, indent=2))
        return

    api_key = os.environ.get("TYPESAFE_API_KEY") or os.environ.get("JEV_API_KEY")
    if not api_key:
        raise RuntimeError(
            "--live requires TYPESAFE_API_KEY or JEV_API_KEY in the environment. "
            "Do not put keys in fixtures, source code, screenshots, or Git."
        )
    endpoint = os.environ.get("JEV_API_URL", DEFAULT_ENDPOINT)
    print(f"\nLIVE CALL — endpoint: {endpoint}")
    print(json.dumps(call_live(endpoint, api_key, payload), indent=2))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("case", nargs="?", help="Case id to show or execute.")
    parser.add_argument("--list", action="store_true", help="List the five decision slots.")
    parser.add_argument("--all", action="store_true", help="Run every case (dry run unless --live is set).")
    parser.add_argument("--live", action="store_true", help="Call the configured live endpoint; requires a key.")
    parser.add_argument("--model", help="Override the pinned fixture model.")
    args = parser.parse_args(argv)
    fixture, cases = load_cases()

    if args.list:
        for case in cases.values():
            print(f"{case['id']}: {case['title']}")
        return 0

    if args.all:
        selected = list(cases.values())
    elif args.case:
        if args.case not in cases:
            parser.error(f"Unknown case: {args.case}. Use --list to see available cases.")
        selected = [cases[args.case]]
    else:
        parser.error("Choose a case, --all, or --list.")

    model = args.model or str(fixture["model"])
    try:
        for case in selected:
            print_case(case, model, live=args.live)
    except RuntimeError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
