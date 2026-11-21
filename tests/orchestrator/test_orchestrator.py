"""Orchestrator tests: no network, no real model calls, no notifications, everything in tmp dirs."""

from __future__ import annotations

import json
import shutil
import subprocess
import wave
from pathlib import Path

import pytest

from content_os.config import load_models_config, load_prompt
from content_os.orchestrator import (av_review, moodboard, backtrack, engine, graph, jobs, memory, modelcall, runner,
                                     settings, stages, status_page)
from content_os.orchestrator.state import Reel, ReelError

ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture(autouse=True)
def sandbox(tmp_path, monkeypatch):
    for var, sub in [("CONTENT_OS_OUTPUTS_ROOT", "outputs"), ("CONTENT_OS_MEDIA_ROOT", "media"),
                     ("CONTENT_OS_ORCH_STATE_DIR", "state"), ("CONTENT_OS_MEMORY_DIR", "memory")]:
        monkeypatch.setenv(var, str(tmp_path / sub))
    monkeypatch.setenv("CONTENT_OS_STATUS_PAGE", str(tmp_path / "status.html"))
    monkeypatch.setenv("CONTENT_OS_NOTIFY", "0")
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    calls: list[tuple[str, str]] = []

    def fake(role, prompt, output_type):
        calls.append((role, prompt))
        if role == "brief":
            out = {"topic": "t", "core_thesis": "c", "learning_objective": "l", "format": "talking head",
                   "brand_pillar": "p", "sections": ["a", "b", "c"], "audience": "x", "promise": "pr",
                   "takeaway": "tk", "target_duration_s": 60}
        elif role == "script":
            n = sum(1 for r, _ in calls if r == "script")
            out = {"title": "T", "promise": "pr", "hook": f"Hook v{n}", "target_duration_s": 30,
                   "beats": [{"id": 1, "text": f"Hook line version {n}.", "section": "hook", "visual": "card"},
                             {"id": 2, "text": "Payoff line.", "section": "payoff", "visual": "card"}]}
        elif role == "moodboard":
            out = {"concept": "c", "palette": ["#FFD23F accent: numbers"], "typography": "Barlow", "texture": "line",
                   "music": "m", "sfx_palette": ["whoosh"], "pacing": "fast",
                   "keyframes": [{"id": "KF01", "time_s": 0, "beats": [1], "emotion": "surprise", "layout": "split",
                                  "shot": "creator punch-in", "on_screen_text": "HOOK"}],
                   "shot_list": ["screen-record the tool, 10 s"]}
        elif role == "story_check":
            out = {"phase": "script", "verdict": "pass",
                   "scores": {k: 8 for k in ("hook", "emotional_arc", "clarity", "retention", "sends", "saves",
                                             "comments", "continuity")},
                   "beats": [{"beat": 1, "intended": "surprise", "likely_felt": "surprise"}]}
        elif role == "feedback_classifier":
            out = {"stage": "script", "reason": "hook wording", "confidence": "high", "generalizable": True,
                   "lesson": {"category": "content", "rule": "Open with the concrete result before the method.",
                              "applies_to": ["script"]}}
        elif role == "post_package":
            out = {"caption": "c", "hashtags": ["#a"], "cover_text": "x", "cover_beat": 1}
        else:
            nonce = prompt.split("nonce: ")[-1]
            out = {"ok": True, "nonce": nonce}
        return out, {"backend": "fake", "served_model": "fake"}

    monkeypatch.setattr(modelcall, "CALLER", fake)
    monkeypatch.setattr(moodboard, "CHROME", str(tmp_path / "no-chrome"))
    return calls


def _make_food_copy() -> Reel:
    dest = settings.paths().outputs_root / "food-tracker-reel"
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(ROOT / "outputs/food-tracker-reel", dest)
    return engine.adopt("food-tracker-reel")


def _add_raw(reel: Reel, name: str = "IMG_1.MOV", data: bytes = b"x") -> None:
    raw = reel.media / "raw"
    raw.mkdir(parents=True, exist_ok=True)
    (raw / name).write_bytes(data)


# --------------------------------------------------------------------------- config and graph
def test_orchestrator_agents_are_config_routed():
    models = load_models_config()
    for role, key in settings.load()["agents"].items():
        cfg = models.resolved(key)
        assert cfg.model and load_prompt(cfg.prompt_version)
    assert "fable" in models.resolved(settings.load()["agents"]["feedback_classifier"]).model
    assert "haiku" in models.resolved(settings.load()["agents"]["heartbeat"]).model


def test_graph_has_all_creator_gates_in_order():
    gates = [n.gate for n in graph.NODES if n.kind == "gate"]
    assert gates == list(graph.CREATOR_GATES)
    assert graph.index("script") < graph.index("record") < graph.index("ingest") < graph.index("qa")
    assert graph.index("qa") < graph.index("visuals") or graph.index("draft_render") < graph.index("visuals")
    assert graph.index("av_review") < graph.index("gate:final_listen") < graph.index("post_package")
    assert graph.downstream("render")[0] == "render" and "performance" in graph.downstream("render")


# --------------------------------------------------------------------------- lifecycle
def test_new_reel_runs_brief_then_waits_for_creator(sandbox):
    reel = engine.new("Why AI calorie counters miss portions", "cal-test")
    res = engine.advance(reel.id)
    assert res["ran"] == ["idea", "brief"] and res["stopped"] == "waiting" and res["node"] == "gate:brief"
    reel = Reel.load(reel.id)
    assert (reel.dir / "brief.md").exists()
    assert reel.stage("brief")["provenance"]["model"] == load_models_config().resolved("orchestrator_brief").model
    # nothing past the gate ran
    assert not reel.stage("script")
    engine.approve(reel.id, "brief", by="tester")
    res = engine.advance(reel.id)
    assert res["ran"] == ["script"] and res["node"] == "gate:script"


def test_gate_approval_is_bound_to_version_and_needs_footage():
    reel = engine.new("idea", "g-test")
    engine.advance(reel.id)
    engine.approve(reel.id, "brief", by="t")
    engine.advance(reel.id)
    engine.approve(reel.id, "script", by="t")
    res = engine.advance(reel.id)
    assert res["ran"] == ["moodboard"] and res["node"] == "gate:moodboard"
    r = Reel.load(reel.id)
    assert "KF01" in (r.dir / "MOODBOARD.html").read_text()
    engine.approve(reel.id, "moodboard", by="t")
    res = engine.advance(reel.id)
    assert res["ran"] == ["shoot_plan"] and res["node"] == "record"
    assert "screen-record the tool" in (r.dir / "SHOOT_PLAN.md").read_text()
    with pytest.raises(ReelError):
        engine.approve(reel.id, "recorded", by="t")       # no footage yet
    with pytest.raises(ReelError):
        engine.approve(reel.id, "cut_review", by="t")     # earlier stages not done
    r = Reel.load(reel.id)
    assert (r.dir / "TELEPROMPTER.md").read_text().count("**beat") == 2


def test_adopt_food_tracker_keeps_hand_written_plan_and_invents_no_approval():
    reel = _make_food_copy()
    assert reel.state["approvals"] == {}
    beats = json.loads((reel.dir / "beats.json").read_text())["beats"]
    assert len(beats) == 14 and beats[0]["section"] == "hook"
    original_plan = (reel.dir / "SHOOT_PLAN.md").read_text()
    res = engine.advance(reel.id)
    assert res["node"] == "gate:script"
    engine.approve(reel.id, "script", by="t")
    res = engine.advance(reel.id)
    assert res["ran"] == ["moodboard", "shoot_plan"]          # adopted reel: no mood board, gate skipped
    assert Reel.load(reel.id).stage("moodboard")["status"] == "skipped"
    assert (reel.dir / "SHOOT_PLAN.md").read_text() == original_plan


# --------------------------------------------------------------------------- backtracking
def _to_recorded(reel_id: str) -> None:
    engine.approve(reel_id, "script", by="t")
    engine.advance(reel_id)
    if engine.advance(reel_id).get("node") == "gate:moodboard":
        engine.approve(reel_id, "moodboard", by="t")
        engine.advance(reel_id)
    r = Reel.load(reel_id)
    _add_raw(r)
    engine.approve(reel_id, "recorded", by="t")


def test_feedback_marks_stale_invalidates_gates_and_plans(sandbox):
    reel = _make_food_copy()
    engine.advance(reel.id)
    _to_recorded(reel.id)
    old_script = Reel.load(reel.id).stage("script")["version"]
    res = backtrack.feedback(reel.id, "the hook is weak")
    assert res["classification"]["stage"] == "script"
    assert "gate:script" in res["invalidated"] and "record" in res["invalidated"]
    assert res["plan"][0].startswith("script") and "[creator] approve script" in res["plan"]
    r = Reel.load(reel.id)
    assert "script" not in r.state["approvals"]
    hist = r.state["approvals_history"][-1]
    assert hist["gate"] == "script" and "hook is weak" in hist["invalidated_reason"]
    states = {s["name"]: s["state"] for s in engine.node_states(r)}
    assert states["script"] == "ready" and states["record"] == "stale"
    # re-run: the script stage receives the feedback, makes a new version, keeps the old one
    engine.advance(reel.id)
    r = Reel.load(reel.id)
    assert r.stage("script")["version"] != old_script
    assert any("the hook is weak" in p for role, p in sandbox if role == "script")
    assert (r.versions_dir / "script" / old_script[:12] / "SCRIPT.md").exists()
    assert r.state["feedback"][0]["resolved_in"]
    events = [e["event"] for e in r.ledger()]
    for ev in ("feedback", "approval_invalidated", "marked_stale", "rerun_plan", "feedback_addressed"):
        assert ev in events


@pytest.mark.parametrize("text,stage", [
    ("the hook is weak", "script"),
    ("cut at 0:14 is abrupt", "cutpoints"),
    ("voice too quiet", "render"),
    ("music too loud under beat 3", "render"),
    ("I look tired in beat 5, re-record it", "record"),
    ("wrong chart on beat 7", "visuals"),
    ("caption needs the source", "post_package"),
])
def test_keyword_fallback_routes_feedback(text, stage):
    assert backtrack.heuristic(text)["stage"] == stage


def test_classifier_failure_falls_back(monkeypatch):
    reel = _make_food_copy()

    def boom(*_a):
        raise RuntimeError("no login")

    monkeypatch.setattr(modelcall, "CALLER", boom)
    c = backtrack.classify(reel, "cut at 0:14 is abrupt")
    assert c["stage"] == "cutpoints" and c["timestamp_s"] == 14 and "model failed" in c["classified_by"]


# --------------------------------------------------------------------------- memory
def test_lesson_promoted_after_two_independent_feedbacks_and_deduped():
    rec = settings.paths().memory_dir / "r.md"
    lesson = {"category": "content", "rule": "Open with the concrete result before the method.",
              "applies_to": ["script"]}
    assert memory.add_candidate(lesson, reel_id="a", feedback_id="a/F001", record=rec)["action"] == "new_candidate"
    # same feedback again does not count twice
    assert memory.add_candidate(lesson, reel_id="a", feedback_id="a/F001", record=rec)["action"] == "merged"
    similar = {**lesson, "rule": "Open with the concrete result, before the method!"}
    out = memory.add_candidate(similar, reel_id="b", feedback_id="b/F001", record=rec)
    assert out["action"] == "promoted_on_repeat"
    mem = memory.load_memory()
    assert len(mem["lessons"]) == 1 and mem["lessons"][0]["confidence"] == "medium"
    assert len(mem["lessons"][0]["sources"]) == 2
    # a third similar one reinforces the memory lesson instead of adding a duplicate
    assert memory.add_candidate(similar, reel_id="c", feedback_id="c/F001", record=rec)["action"] == "reinforced_memory"
    block, ids = memory.prompt_block("script")
    assert ids == [mem["lessons"][0]["id"]] and "concrete result" in block
    assert memory.prompt_block("render")[1] == []   # not relevant to render


def test_memory_is_capped_and_evictions_archived(monkeypatch):
    cfg = settings.load()
    cfg["memory"]["max_lessons"] = 3
    monkeypatch.setattr(settings, "load", lambda: cfg)
    rec = settings.paths().memory_dir / "r.md"
    words = ["alpha", "bravo", "charlie", "delta", "echo"]
    for i, w in enumerate(words):
        memory.add_candidate({"category": "edit", "rule": f"{w} {w}x rule number {i} unique{i}",
                              "applies_to": ["edit"]}, reel_id="r", feedback_id=f"r/F{i}", record=rec)
        memory.promote(f"L{i + 1:04d}", by="creator" if i == 0 else "repeat")
    mem = memory.load_memory()
    assert len(mem["lessons"]) == 3 and "L0001" in {l["id"] for l in mem["lessons"]}
    arch = memory._read(memory._files()["archive"], {"lessons": []})
    assert len(arch["lessons"]) == 2


def test_feedback_writes_dated_record_and_candidate():
    reel = _make_food_copy()
    res = backtrack.feedback(reel.id, "the hook is weak")
    text = Path(res["record"]).read_text()
    assert "the hook is weak" in text and "Routed to stage:** `script`" in text
    assert res["lesson"]["action"] == "new_candidate"


# --------------------------------------------------------------------------- queue, runner, page
def test_queue_dedupes_and_recovers_orphans():
    a = jobs.enqueue("advance", "r1")
    assert jobs.enqueue("advance", "r1") == a
    job = jobs.claim(pid=999999)
    assert job["id"] == a
    assert jobs.recover_orphans() == 1
    assert jobs.get(a)["status"] == "queued"


def test_exec_job_heartbeat_and_advance_pause(sandbox):
    jid = jobs.enqueue("heartbeat")
    assert runner.exec_job(jid) == 0
    j = jobs.get(jid)
    assert j["status"] == "done" and json.loads(j["result"])["ok"] is True
    reel = engine.new("idea", "q-test")
    jid = jobs.enqueue("advance", reel.id)
    runner.exec_job(jid)
    assert jobs.get(jid)["status"] == "paused"     # stopped at the brief gate


def test_runner_wraps_jobs_in_caffeinate_and_plist_is_keepalive():
    cmd = runner._child_cmd(7)
    assert cmd[0] == "/usr/bin/caffeinate" and "-i" in cmd and "-s" in cmd and cmd[-1] == "7"
    p = runner.plist_dict()
    assert p["RunAtLoad"] and p["KeepAlive"] and p["Label"] == "com.contentos.runner"
    assert p["StandardOutPath"].endswith("Library/Logs/content_os/runner.log")


def test_status_page_lists_pending_gate():
    reel = _make_food_copy()
    engine.advance(reel.id)
    html = Path(status_page.write()).read_text()
    assert "food-tracker-reel" in html and "approve food-tracker-reel script" in html


# --------------------------------------------------------------------------- av review
def _wav(path: Path, seconds: float = 1.0) -> Path:
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(16000)
        w.writeframes(b"\x00\x00" * int(16000 * seconds))
    return path


def test_av_review_skips_without_key(tmp_path, monkeypatch):
    monkeypatch.setattr(av_review, "get_key", lambda: None)
    res = av_review.review(_wav(tmp_path / "a.wav"), tmp_path / "out")
    assert res["status"] == "skipped: no key"
    assert (tmp_path / "out/av_review.md").exists()


def test_av_review_sends_audio_with_mocked_client(tmp_path, monkeypatch):
    sent = {}

    class Msg:
        content = json.dumps({"energy": {"score": 4, "notes": "good"}, "clarity": {"score": 5, "notes": ""},
                              "pacing": {"score": 3, "notes": "fast"}, "music_balance": {"score": 4, "notes": ""},
                              "issues": [{"at_s": 3, "issue": "breath", "severity": "low"}], "overall": "ok"})

    class Resp:
        choices = [type("C", (), {"message": Msg()})()]
        usage = None
        model = "fake"

    class Client:
        class chat:  # noqa: N801
            class completions:  # noqa: N801
                @staticmethod
                def create(**kw):
                    sent.update(kw)
                    return Resp()

    monkeypatch.setattr(av_review, "CLIENT_FACTORY", lambda key: Client())
    monkeypatch.setattr(av_review, "_ffmpeg", lambda: None)
    monkeypatch.setattr(av_review, "extract_audio",
                        lambda src, dest: (shutil.copy(src, dest), {"tool": "copy", "source_duration_s": 1.0,
                                                                    "sent_seconds": 1.0})[1])
    res = av_review.review(_wav(tmp_path / "a.wav"), tmp_path / "out", key="sk-test")
    assert res["status"] == "done" and res["audio_review"]["energy"]["score"] == 4
    assert sent["model"] == settings.load()["av_review"]["audio_model"]
    part = sent["messages"][0]["content"][1]
    assert part["type"] == "input_audio" and part["input_audio"]["format"] == "wav"
    assert "sk-test" not in (tmp_path / "out/av_review.json").read_text()


def test_unchanged_rerun_keeps_feedback_open():
    reel = _make_food_copy()
    engine.advance(reel.id)
    _to_recorded(reel.id)
    # shoot_plan is deterministic: re-running it with the same script gives the same version
    backtrack.feedback(reel.id, "teleprompter lines too long", use_model=False, stage_override="shoot_plan")
    engine.advance(reel.id)
    r = Reel.load(reel.id)
    fb = r.state["feedback"][-1]
    assert fb["resolved_in"] is None and fb["needs_manual_change"]
    assert "feedback_not_addressed" in [e["event"] for e in r.ledger()]
