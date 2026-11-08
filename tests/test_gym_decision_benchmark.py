import json
from pathlib import Path

import pytest

from content_os.tools.gym_decision_benchmark import BenchmarkError, load_fixtures, summarise


FIXTURES = Path("assets/jev-gpt-gym-benchmark/fixtures-v1.json")


def _recorded_runs() -> list[dict]:
    payload = load_fixtures(FIXTURES)
    rows = []
    for model, latency, cost in (("gpt", 420.0, 0.002), ("jev", 180.0, 0.001)):
        for fixture in payload["fixtures"]:
            for run_index in range(1, 3):
                rows.append(
                    {
                        "model": model,
                        "fixture_id": fixture["id"],
                        "fixture_version": payload["fixture_version"],
                        "contract_version": payload["contract_version"],
                        "run_index": run_index,
                        "route": fixture["expected_route"],
                        "needs_human_review": fixture["expected_human_review"],
                        "schema_valid": True,
                        "latency_ms": latency + run_index,
                        "cost_usd": cost,
                    }
                )
    return rows


def test_fixture_suite_is_valid_and_summary_keeps_quality_gates():
    payload = load_fixtures(FIXTURES)
    result = summarise(payload, _recorded_runs(), expected_runs_per_fixture=2)

    assert result["models"]["gpt"]["valid_safe_rate"] == 1.0
    assert result["models"]["jev"]["hard_boundary_violations"] == 0
    assert result["models"]["jev"]["latency_ms"]["p50"] < result["models"]["gpt"]["latency_ms"]["p50"]


def test_summary_rejects_incomplete_evidence():
    payload = load_fixtures(FIXTURES)
    with pytest.raises(BenchmarkError, match="expected 2"):
        summarise(payload, _recorded_runs()[:-1], expected_runs_per_fixture=2)
