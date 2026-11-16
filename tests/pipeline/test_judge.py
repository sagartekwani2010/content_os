"""The judge step is mocked: no CLI process, no network."""

import json
import subprocess

import pytest

from content_os.pipeline import judge
from content_os.pipeline.reel import Reel, StageError, read_json, write_json


def take(tid, beat, eligible, reasons=()):
    return {"id": tid, "beat": beat, "text": "x", "duration": 2.0, "wpm": 160, "completeness": 1.0, "complete": eligible,
            "restart": False, "fillers": 0, "filler_words": [], "internal_pauses": [], "loudness_lufs": -18,
            "loudness_rel_beat_db": 0, "variation": {}, "face": {"measured": False}, "score": 0.9, "score_parts": {},
            "eligible": eligible, "ineligible_reasons": list(reasons), "flags": []}


@pytest.fixture
def reel(tmp_path):
    write_json(tmp_path / "beats.json", {"beats": [{"id": 1, "text": "Line one."}, {"id": 2, "text": "Line two."}]})
    write_json(tmp_path / "cue_sheet.json", {"beats": [{"beat": 1, "visual": {"type": "card", "text": "A"}}]})
    r = Reel.at(tmp_path)
    write_json(r.scores_file, {"takes": [take("b1_t1", 1, True), take("b1_t2", 1, True),
                                         take("b2_t1", 2, False, ["incomplete sentence"]), take("b2_t2", 2, True)]})
    write_json(r.selects_file, {"beats": [{"beat": 1, "take": "b1_t2", "status": "ok"},
                                          {"beat": 2, "take": "b2_t2", "status": "ok"}], "needs_rerecord": []})
    return r


def fake_cli(output, captured):
    def run(cmd, stdin, timeout):
        captured["cmd"] = cmd
        captured["stdin"] = json.loads(stdin)
        events = [{"type": "system", "subtype": "init"},
                  {"type": "result", "subtype": "success", "is_error": False, "structured_output": output,
                   "result": json.dumps(output), "total_cost_usd": 0.12, "session_id": "s"}]
        return subprocess.CompletedProcess(cmd, 0, "\n".join(json.dumps(e) for e in events), "")
    return run


def test_takes_phase_applies_only_eligible_choices(reel, cfg, monkeypatch):
    out = {"beats": [{"beat": 1, "take": "b1_t1", "reason": "steadier pace", "confidence": "medium"},
                     {"beat": 2, "take": "b2_t1", "reason": "more energy", "confidence": "low"}],
           "visual_timing": [{"beat": 1, "start_offset_s": 0.8, "anchor_word": "agents", "reason": "noun lands"}],
           "notes": ""}
    cap = {}
    monkeypatch.setattr(judge, "_run_cli", fake_cli(out, cap))
    cfg["judge"]["model"] = "claude-test-model"
    rec = judge.run(reel, cfg, "takes")
    cmd = cap["cmd"]
    assert cmd[cmd.index("--model") + 1] == "claude-test-model"
    assert "--json-schema" in cmd and cmd[cmd.index("--tools") + 1] == ""
    assert cap["stdin"]["message"]["content"][0]["type"] == "text"
    sel = read_json(reel.selects_file)
    b1, b2 = sel["beats"]
    assert b1["take"] == "b1_t1" and b1["picked_by"] == "judge:claude-test-model"
    assert b2["take"] == "b2_t2"  # ineligible choice refused, deterministic pick kept
    assert b2["judge"]["accepted"] is False and "hard checks" in b2["judge"]["rejected_because"]
    assert rec["cost_usd"] == 0.12
    sugg = read_json(reel.work / "cue_sheet.suggested.json")
    assert sugg["beats"][0]["start_offset"] == 0.8
    assert read_json(reel.cue_sheet_file)["beats"][0].get("start_offset") is None  # creator's file untouched


def test_cuts_phase_sends_images_and_records_rejections(reel, cfg, monkeypatch, tmp_path):
    import numpy as np
    cv2 = pytest.importorskip("cv2")
    png = reel.p("review", "contact_sheet.png")
    cv2.imwrite(str(png), np.zeros((8, 8, 3), np.uint8))
    write_json(reel.cuts_file, {"sha256": "x", "segments": [
        {"index": 0, "beat": 1, "take": "b1_t2", "out_start": 0, "duration": 2, "gain_db": 0, "lead_s": .04,
         "tail_s": .08, "crop_realigned": False, "text": "Line one.",
         "words": [{"text": "Line", "start": 0.04, "end": 0.3}]}]})
    write_json(reel.work / "review" / "review.json", {"joins": [], "contact_sheets": [reel.rel(png)]})
    out = {"reject_cuts": [{"cut": 1, "reason": "head jumps", "suggested_fix": "use b1_t1"}], "visual_timing": [],
           "notes": "ok"}
    cap = {}
    monkeypatch.setattr(judge, "_run_cli", fake_cli(out, cap))
    rec = judge.run(reel, cfg, "cuts")
    content = cap["stdin"]["message"]["content"]
    assert [c["type"] for c in content] == ["text", "image"]
    assert rec["result"]["reject_cuts"][0]["cut"] == 1


def test_judge_error_is_reported(reel, cfg, monkeypatch):
    def bad(cmd, stdin, timeout):
        return subprocess.CompletedProcess(cmd, 1, json.dumps({"type": "result", "is_error": True}), "boom")
    monkeypatch.setattr(judge, "_run_cli", bad)
    with pytest.raises(StageError, match="judge call failed"):
        judge.run(reel, cfg, "takes")
