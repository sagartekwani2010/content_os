import json

from content_os.factory import tournament


def fake_call(role, prompt, ledger=None, retries=1):
    if ledger:
        with ledger.open("a") as f:
            f.write(json.dumps({"at": "2026-11-19T00:00:00", "role": role, "model": "m", "seconds": 1,
                                "chars_in": 1, "chars_out": 1, "ok": True}) + "\n")
    if role in ("writer", "writer_alt"):
        return "# SCRIPT\n| Beat | Spoken |\n|---|---|\n| 1 | hi |\n# HOOKS\n- one"
    if role == "reviser":
        return "# SCRIPT\nrevised **better**"
    if role == "checker":
        return '```json\n{"must_fix":["x"],"should_fix":[],"facts_ok":true}\n```'
    if role == "panel":
        score = 7 if "revised" in prompt else 5
        return json.dumps({"personas": [{"id": 1, "score": score, "drop_beat": "none", "why": "ok"}],
                           "groups": {}, "overall": score, "top_fixes": []})
    if role == "critic":
        return json.dumps({"predicted_score": 6, "would_approve": False, "change_list": ["shorter"],
                           "taste_violations": [], "what_they_will_love": []})
    if role == "decider":
        return "# Recommendation\nShoot A."
    raise AssertionError(role)


def test_run_and_revise(tmp_path, monkeypatch):
    monkeypatch.setattr(tournament, "call", fake_call)
    monkeypatch.setattr(tournament.taste, "load", lambda: "taste")
    brief = tmp_path / "b.md"
    brief.write_text("brief")
    out = tmp_path / "f"
    page = tournament.run(brief, None, out, ["A", "E"])
    lb = json.loads((out / "leaderboard.json").read_text())
    assert {r["id"] for r in lb} == {"A", "E"}
    assert lb[0]["round"] >= 1 and lb[0]["score"] > 5.5  # revision gained and was kept
    text = page.read_text()
    assert "Shoot A." in text and "<table>" in text and "Leaderboard" in text
    page2 = tournament.revise(out, "A", "make it punchier")
    assert page2.exists()
    assert any((p / "CREATOR_NOTES.md").exists() for p in out.glob("round_*"))


def test_score_survives_bad_judge(monkeypatch):
    def bad(role, prompt, ledger=None, retries=1):
        return "not json" if role == "panel" else fake_call(role, prompt)
    monkeypatch.setattr(tournament, "call", bad)
    cfg = tournament.config()["tournament"]
    sc = tournament.score("ctx", "draft", None, cfg)
    assert "error" in sc["panel"] and sc["summary"]["panel"] == 0
