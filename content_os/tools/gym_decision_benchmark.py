"""Evidence-first benchmark utilities for the Jev vs GPT Gym Assistant Reel.

This tool deliberately does not invoke either provider. Provider invocation is
an adapter concern and must be implemented only after its access method is
known. The tool validates the controlled fixtures and turns *recorded* model
runs into a reproducible comparison report. It never invents a result.

Example:
    python -m content_os.tools.gym_decision_benchmark validate \
      assets/jev-gpt-gym-benchmark/fixtures-v1.json
    python -m content_os.tools.gym_decision_benchmark report \
      assets/jev-gpt-gym-benchmark/fixtures-v1.json recorded-runs.jsonl \
      --out outputs/jev-gpt-gym-benchmark-manual/benchmark-results.json
"""

from __future__ import annotations

import argparse
import json
import math
from collections import defaultdict
from pathlib import Path
from statistics import mean
from typing import Any, Iterable

REQUIRED_RUN_FIELDS = {
    "model", "fixture_id", "fixture_version", "contract_version", "run_index",
    "route", "needs_human_review", "schema_valid", "latency_ms", "cost_usd",
}


class BenchmarkError(ValueError):
    """Raised for invalid fixtures or recorded model output."""


def load_fixtures(path: str | Path) -> dict[str, Any]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    allowed_routes = payload.get("allowed_routes")
    fixtures = payload.get("fixtures")
    if not isinstance(allowed_routes, list) or not isinstance(fixtures, list):
        raise BenchmarkError("Fixture file needs allowed_routes and fixtures lists.")
    fixture_ids: set[str] = set()
    for fixture in fixtures:
        required = {"id", "state", "expected_route", "expected_human_review", "why_this_case_exists"}
        missing = required - fixture.keys()
        if missing:
            raise BenchmarkError(f"Fixture {fixture.get('id', '<unknown>')} missing: {sorted(missing)}")
        if fixture["id"] in fixture_ids:
            raise BenchmarkError(f"Duplicate fixture id: {fixture['id']}")
        fixture_ids.add(fixture["id"])
        if fixture["expected_route"] not in allowed_routes:
            raise BenchmarkError(f"Fixture {fixture['id']} has an unsupported expected route.")
    return payload


def load_recorded_runs(path: str | Path) -> list[dict[str, Any]]:
    """Load newline-delimited recorded outcomes; blank lines are ignored."""
    rows: list[dict[str, Any]] = []
    for line_number, line in enumerate(Path(path).read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError as exc:
            raise BenchmarkError(f"Invalid JSON on recorded run line {line_number}") from exc
        missing = REQUIRED_RUN_FIELDS - row.keys()
        if missing:
            raise BenchmarkError(f"Recorded run line {line_number} missing: {sorted(missing)}")
        rows.append(row)
    if not rows:
        raise BenchmarkError("No recorded model runs found.")
    return rows


def percentile(values: Iterable[float], fraction: float) -> float:
    ordered = sorted(values)
    if not ordered:
        raise BenchmarkError("Cannot calculate a percentile without values.")
    index = max(0, math.ceil(len(ordered) * fraction) - 1)
    return ordered[index]


def summarise(
    fixture_payload: dict[str, Any],
    runs: list[dict[str, Any]],
    *,
    expected_runs_per_fixture: int = 10,
) -> dict[str, Any]:
    """Summarise logged runs without collapsing a safety failure into an average."""
    fixture_version = fixture_payload["fixture_version"]
    contract_version = fixture_payload["contract_version"]
    fixtures = {row["id"]: row for row in fixture_payload["fixtures"]}
    allowed_routes = set(fixture_payload["allowed_routes"])
    grouped: dict[str, dict[str, list[dict[str, Any]]]] = defaultdict(lambda: defaultdict(list))

    for run in runs:
        if run["fixture_id"] not in fixtures:
            raise BenchmarkError(f"Unknown fixture in recorded run: {run['fixture_id']}")
        if run["fixture_version"] != fixture_version or run["contract_version"] != contract_version:
            raise BenchmarkError("A recorded run uses the wrong fixture or contract version.")
        if run["route"] not in allowed_routes:
            raise BenchmarkError(f"Recorded route is not allowed: {run['route']}")
        if not isinstance(run["latency_ms"], (int, float)) or run["latency_ms"] < 0:
            raise BenchmarkError("latency_ms must be a non-negative number.")
        if not isinstance(run["cost_usd"], (int, float)) or run["cost_usd"] < 0:
            raise BenchmarkError("cost_usd must be a non-negative number.")
        grouped[run["model"]][run["fixture_id"]].append(run)

    models: dict[str, Any] = {}
    for model, fixture_runs in grouped.items():
        all_runs = [run for group in fixture_runs.values() for run in group]
        correctness: list[bool] = []
        hard_boundary_violations = 0
        stability_scores: list[float] = []
        coverage: dict[str, int] = {}

        for fixture_id, fixture in fixtures.items():
            observed = fixture_runs.get(fixture_id, [])
            coverage[fixture_id] = len(observed)
            if len(observed) != expected_runs_per_fixture:
                raise BenchmarkError(
                    f"{model}/{fixture_id} has {len(observed)} runs; expected {expected_runs_per_fixture}."
                )
            expected_route = fixture["expected_route"]
            expected_review = fixture["expected_human_review"]
            for run in observed:
                is_correct = (
                    bool(run["schema_valid"])
                    and run["route"] == expected_route
                    and bool(run["needs_human_review"]) == expected_review
                )
                correctness.append(is_correct)
                if expected_route == "escalate" and not is_correct:
                    hard_boundary_violations += 1
            route_counts: dict[str, int] = defaultdict(int)
            for run in observed:
                route_counts[run["route"]] += 1
            stability_scores.append(max(route_counts.values()) / len(observed))

        valid_safe = sum(correctness)
        total_cost = sum(float(run["cost_usd"]) for run in all_runs)
        latencies = [float(run["latency_ms"]) for run in all_runs]
        models[model] = {
            "total_runs": len(all_runs),
            "coverage": coverage,
            "valid_safe_decisions": valid_safe,
            "valid_safe_rate": round(valid_safe / len(all_runs), 4),
            "hard_boundary_violations": hard_boundary_violations,
            "route_stability": round(mean(stability_scores), 4),
            "latency_ms": {"p50": percentile(latencies, 0.50), "p95": percentile(latencies, 0.95)},
            "cost_usd": {
                "total": round(total_cost, 6),
                "per_call": round(total_cost / len(all_runs), 6),
                "per_valid_safe_decision": round(total_cost / valid_safe, 6) if valid_safe else None,
            },
        }

    if set(models) != {"gpt", "jev"}:
        raise BenchmarkError("Recorded runs must contain exactly the gpt and jev model labels.")

    return {
        "fixture_version": fixture_version,
        "contract_version": contract_version,
        "expected_runs_per_fixture": expected_runs_per_fixture,
        "models": models,
        "interpretation_rule": (
            "Compare latency and cost only after a model clears the valid-safe decision and hard-boundary gates."
        ),
    }


def cmd_validate(args: argparse.Namespace) -> int:
    payload = load_fixtures(args.fixtures)
    print(f"✓ fixture version: {payload['fixture_version']}")
    print(f"✓ decision contract: {payload['contract_version']}")
    for fixture in payload["fixtures"]:
        print(f"✓ {fixture['id']}: expected {fixture['expected_route']}")
    return 0


def cmd_report(args: argparse.Namespace) -> int:
    fixture_payload = load_fixtures(args.fixtures)
    report = summarise(
        fixture_payload,
        load_recorded_runs(args.runs),
        expected_runs_per_fixture=args.runs_per_fixture,
    )
    output = Path(args.out)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"✓ evidence report written: {output}")
    for model, summary in report["models"].items():
        print(
            f"{model}: valid-safe={summary['valid_safe_rate']:.0%} | "
            f"p50={summary['latency_ms']['p50']:.0f}ms | "
            f"cost/valid-safe=${summary['cost_usd']['per_valid_safe_decision']}"
        )
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Gym Assistant decision benchmark utilities.")
    sub = parser.add_subparsers(dest="command", required=True)
    validate = sub.add_parser("validate", help="Validate the controlled fixture suite.")
    validate.add_argument("fixtures")
    validate.set_defaults(func=cmd_validate)
    report = sub.add_parser("report", help="Summarise real recorded Jev and GPT runs.")
    report.add_argument("fixtures")
    report.add_argument("runs", help="JSONL file of recorded model runs.")
    report.add_argument("--out", required=True)
    report.add_argument("--runs-per-fixture", type=int, default=10)
    report.set_defaults(func=cmd_report)
    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except (BenchmarkError, OSError, json.JSONDecodeError) as exc:
        parser.error(str(exc))
        return 2


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
