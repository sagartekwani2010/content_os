import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEMO = ROOT / "demos" / "jev-decision-slots" / "run_demo.py"
FIXTURES = ROOT / "demos" / "jev-decision-slots" / "fixtures.json"


def test_five_fixture_ids_are_unique_and_typed() -> None:
    payload = json.loads(FIXTURES.read_text(encoding="utf-8"))
    cases = payload["cases"]
    assert [case["id"] for case in cases] == [
        "model-routing",
        "triage",
        "rag-filter",
        "tool-gate",
        "agent-eval",
    ]
    assert all(question["type"] in {"choice", "score", "noul"}
               for case in cases for question in case["questions"].values())


def test_dry_run_prints_request_and_never_invents_response() -> None:
    result = subprocess.run(
        [sys.executable, str(DEMO), "model-routing"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    assert "DRY RUN — request payload only" in result.stdout
    assert '"questions"' in result.stdout
    assert "LIVE CALL" not in result.stdout
