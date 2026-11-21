"""Playback speed, cold open, sound effects, music drops, clean stem and the SFX cue list.

Media is synthetic (numpy tones / ffmpeg lavfi) in tmp dirs; no network."""

import json

import numpy as np
import pytest

from content_os.pipeline import cue as cuelib
from content_os.pipeline import cutpoints, media, render, sfx
from content_os.pipeline.config import DEFAULTS, load_config
from content_os.pipeline.reel import Reel, StageError, write_json

from .conftest import needs_ffmpeg

FPS = 30
SR48 = 48000


# ------------------------------------------------------------------ pure helpers

def test_speed_for_defaults_and_overrides():
    cue = {"speed": 1.05, "beats": [{"beat": 15, "speed": 1.0}, {"beat": 2}]}
    assert cuelib.speed_for(cue, 2) == 1.05
    assert cuelib.speed_for(cue, 15) == 1.0
    assert cuelib.speed_for(cue, 9) == 1.05
    assert cuelib.speed_for(None, 1) == 1.0
    with pytest.raises(StageError):
        cuelib.speed_for({"speed": 3.0}, 1, DEFAULTS["speed"])


def test_out_frames_rounds_to_frame_grid():
    assert cuelib.out_frames(89, 1.0) == 89
    assert cuelib.out_frames(156, 1.05) == 149  # 148.57 -> 149
    assert cuelib.out_frames(1, 2.0) == 1


def test_trim_lead_starts_on_onset():
    env = np.full(300, -80.0)
    env[100:200] = -20.0           # speech from 1.00 s
    env[98:100] = -60.0            # soft consonant from 0.98 s (above the threshold)
    r = {"in": 0.8, "out": 2.1, "frames": 39, "lead_s": 0.2, "tail_s": 0.1, "notes": []}
    t = cutpoints.trim_lead(r, env, 0.01, first_word=1.05, threshold=-65.0, fps=FPS, max_lead=0.04)
    assert t["onset"] == pytest.approx(0.98)
    assert 0 <= t["lead_s"] <= 0.04
    assert t["in"] >= 0.8 and t["in"] <= 0.98
    assert abs(t["in"] * FPS - round(t["in"] * FPS)) < 0.01
    assert t["frames"] == round(2.1 * FPS) - round(t["in"] * FPS)
    assert t["out"] == 2.1
    # a decaying tail of earlier sound right at the in-point is not the onset
    env[80:84] = [-50.0, -58.0, -63.0, -70.0]
    t2 = cutpoints.trim_lead(r, env, 0.01, first_word=1.05, threshold=-65.0, fps=FPS, max_lead=0.04)
    assert t2["onset"] == pytest.approx(0.98) and t2["in"] == t["in"]


def _cuts(segments):
    return {"fps": FPS, "sha256": "abc", "segments": segments,
            "duration": round(sum(s["duration"] for s in segments), 4)}


def _seg(beat, start, dur, words, **kw):
    return {"beat": beat, "out_start": start, "duration": dur,
            "words": [{"text": w, "start": round(start + a, 3), "end": round(start + b, 3)} for w, a, b in words], **kw}


@pytest.fixture
def toy_cuts():
    return _cuts([
        _seg(0, 0.0, 2.0, [("500", 0.03, 0.5), ("became", 1.0, 1.4), ("94.", 1.5, 1.9)], source_beat=2, cold_open=True),
        _seg(1, 2.0, 3.0, [("Hello", 0.05, 0.5), ("calories", 1.0, 1.5), ("there.", 2.0, 2.8)]),
        _seg(2, 5.0, 2.0, [("500", 0.03, 0.5), ("became", 1.0, 1.4), ("94.", 1.5, 1.9)]),
    ])


def test_resolve_sfx_anchors(toy_cuts, tmp_path):
    cue = {"visual_clips": "vis", "beats": [
        {"beat": 0, "sfx": [{"path": "hit.wav", "word": "94", "level_db": -18}]},
        {"beat": 1, "sfx": [{"path": "whoosh.wav", "at": -0.12, "level_db": -24},
                            {"path": "pop.wav", "type": "pop", "visual_cue": {"target": "cal", "action": "cross",
                                                                              "edge": "end"},
                             "word": "calories", "offset": 0.3, "level_db": -22}]},
        {"beat": 2, "sfx": [{"path": "hit.wav", "word": "94", "gain_db": -10}]}]}
    got = cuelib.resolve_sfx(cue, toy_cuts, tmp_path)
    by = [(s["beat"], s["type"], s["at"]) for s in got]
    assert by == [(0, "hit", 1.5), (1, "whoosh", 1.88), (1, "pop", 3.3), (2, "hit", 6.5)]
    assert got[2]["anchor"].startswith("word")  # no manifest -> spoken-word fallback
    assert got[0]["level_db"] == -18 and got[3]["gain_db"] == -10
    # with a fresh visuals manifest the pop follows the visual cue's end
    (tmp_path / "vis").mkdir()
    write_json(tmp_path / "vis" / "visuals.json", {"cuts_sha256": "abc", "beats": [
        {"beat": 1, "cues": [{"target": "cal", "action": "write", "t": 0.2, "dur": 0.4},
                             {"target": "cal", "action": "cross", "t": 0.9, "dur": 0.7}]}]})
    pop = [s for s in cuelib.resolve_sfx(cue, toy_cuts, tmp_path) if s["type"] == "pop"][0]
    assert pop["at"] == pytest.approx(2.0 + 0.9 + 0.7 + 0.3) and pop["anchor"].startswith("visual")
    # a stale manifest (other cuts) is ignored
    write_json(tmp_path / "vis" / "visuals.json", {"cuts_sha256": "old", "beats": []})
    pop = [s for s in cuelib.resolve_sfx(cue, toy_cuts, tmp_path) if s["type"] == "pop"][0]
    assert pop["at"] == pytest.approx(3.3)


def test_resolve_sfx_missing_word_fails(toy_cuts):
    with pytest.raises(StageError):
        cuelib.resolve_sfx({"beats": [{"beat": 1, "sfx": [{"path": "x.wav", "word": "nope"}]}]}, toy_cuts)


def test_music_drops_envelope(toy_cuts):
    cue = {"music_drops": [{"from_beat": 1, "to_beat": 1, "level_db": -60},
                           {"before_beat": 1, "duration": 0.3, "level_db": -60, "fade_out": 0.05, "fade_in": 0.02}]}
    d = cuelib.resolve_music_drops(cue, toy_cuts)
    assert d[0] == {"fade_out_start": 2.0, "hold_start": 2.25, "hold_end": 5.0, "fade_in_end": 5.6, "level_db": -60}
    assert d[1]["hold_start"] == pytest.approx(1.7) and d[1]["hold_end"] == 2.0 and d[1]["fade_out_start"] == pytest.approx(1.65)
    g = lambda t: cuelib.drop_gain(d, t)  # noqa: E731
    assert g(1.0) == 1.0 and g(6.0) == 1.0
    assert g(1.8) < 0.002 and g(3.0) < 0.002          # reset before beat 1, silent through beat 1
    assert 0.4 < g(2.125) < 0.6 or g(2.125) < 0.002  # inside the fade (or still held by the reset)
    assert 0.45 < g(5.3) < 0.55                       # halfway back in


def test_timecode():
    assert sfx.timecode(0) == "00:00.00"
    assert sfx.timecode(65.237) == "01:05.24"
    assert sfx.timecode(3599.999) == "60:00.00"


# ------------------------------------------------------------------ media

def _write_wav(path, x, sr):
    raw = path.with_suffix(".f32")
    x.astype("<f4").tofile(raw)
    media.ffmpeg("-v", "error", "-f", "f32le", "-ar", str(sr), "-ac", "1", "-i", str(raw), "-c:a", "pcm_s24le", str(path))
    raw.unlink()


def _speech_like(sr, total, spans, freq=180.0):
    t = np.arange(int(sr * total)) / sr
    x = np.random.default_rng(1).normal(0, 1e-4, len(t))
    for a, b in spans:
        m = (t >= a) & (t < b)
        x[m] += 0.3 * np.sin(2 * np.pi * freq * t[m]) * (1 + 0.3 * np.sin(2 * np.pi * 4 * t[m]))
    return x


@pytest.fixture
def fake_reel(tmp_path):
    """Three beats in one 12 s source: speech bursts, a 1280x720 lavfi video, all JSON a run needs."""
    root = tmp_path / "reel"
    (root / "work" / "audio").mkdir(parents=True)
    spans = {1: (1.0, 2.6), 2: (4.0, 5.2), 3: (7.0, 9.0)}
    x16 = _speech_like(16000, 12.0, spans.values())
    x48 = _speech_like(SR48, 12.0, spans.values())
    _write_wav(root / "work" / "audio" / "s1_16k.wav", x16, 16000)
    _write_wav(root / "work" / "audio" / "s1_48k.wav", x48, SR48)
    media.ffmpeg("-v", "error", "-f", "lavfi", "-i", "testsrc2=s=1280x720:r=30:d=12", "-c:v", "libx264",
                 "-pix_fmt", "yuv420p", "-g", "15", str(root / "s1.mp4"))
    video = {"codec": "h264", "width": 1280, "height": 720, "display_width": 1280, "display_height": 720,
             "fps": 30, "pix_fmt": "yuv420p", "hdr": False, "color_transfer": "bt709"}
    write_json(root / "work" / "sources.json", {"sources": [
        {"id": "s1", "path": "s1.mp4", "duration": 12.0, "video": video, "wav16": "work/audio/s1_16k.wav",
         "wav48": "work/audio/s1_48k.wav"}]})
    write_json(root / "work" / "transcript.json", {"sources": {"s1": {
        "speech_regions": [list(v) for v in spans.values()]}}})
    takes = []
    for b, (a, e) in spans.items():
        n = 4
        ws = [{"text": f"w{b}{i}", "start": round(a + (e - a) * i / n, 3), "end": round(a + (e - a) * (i + 1) / n, 3)}
              for i in range(n)]
        ws[-1]["text"] = "94." if b == 2 else ws[-1]["text"]
        takes.append({"id": f"b{b}_t1", "beat": b, "source": "s1", "start": a, "end": e, "words": ws,
                      "text": " ".join(w["text"] for w in ws), "face": {"cx": 0.5, "cy": 0.45, "w": 0.2}})
    write_json(root / "work" / "scores.json", {"takes": takes})
    write_json(root / "work" / "selects.json", {"beats": [{"beat": t["beat"], "take": t["id"]} for t in takes],
                                                "needs_rerecord": []})
    write_json(root / "beats.json", {"beats": [{"id": b, "text": t["text"]} for b, t in zip(spans, takes)]})
    return root


def _cfg():
    return load_config(overrides={"judge": {"enabled": False}, "captions": {"enabled": False}})


@needs_ffmpeg
def test_cutpoints_speed_and_cold_open(fake_reel):
    write_json(fake_reel / "cue_sheet.json", {"speed": 1.25, "cold_open": {"beat": 2, "id": 0},
                                              "beats": [{"beat": 2, "speed": 1.0, "speaker_zoom": 1.2}]})
    reel = Reel.at(fake_reel)
    cuts = cutpoints.run(reel, _cfg())
    segs = cuts["segments"]
    assert [s["beat"] for s in segs] == [0, 1, 2, 3]
    co, b2 = segs[0], segs[2]
    assert co["take"] == b2["take"] == "b2_t1" and co["source_beat"] == 2 and co["cold_open"]
    assert co["speed"] == 1.0 and b2["speed"] == 1.0 and segs[1]["speed"] == 1.25 and segs[3]["speed"] == 1.25
    assert co["out"] == b2["out"] and co["in"] >= b2["in"]
    assert co["crop"] == b2["crop"]  # inherits beat 2's speaker_zoom
    # starts on the word: lead silence <= 40 ms; first word at the onset
    assert co["lead_s"] <= 0.04 and co["words"][0]["start"] <= 0.06
    frame_total = 0
    for s in segs:
        assert s["frames"] == cuelib.out_frames(s["src_frames"], s["speed"])
        assert s["src_frames"] == round((s["out"] - s["in"]) * FPS)
        assert s["out_start"] == pytest.approx(frame_total / FPS, abs=1e-4)
        assert s["duration"] == pytest.approx(s["frames"] / FPS, abs=1e-4)
        frame_total += s["frames"]
    assert cuts["duration"] == pytest.approx(frame_total / FPS, abs=1e-4)
    # sped-up word times: source offsets divided by the speed
    take3 = next(t for t in json.loads((fake_reel / "work" / "scores.json").read_text())["takes"] if t["beat"] == 3)
    s3 = segs[3]
    assert s3["words"][1]["start"] == pytest.approx(s3["out_start"] + (take3["words"][1]["start"] - s3["in"]) / 1.25, abs=2e-3)
    assert [j["time"] for j in cuts["joins"]] == [s["out_start"] for s in segs[1:]]


@needs_ffmpeg
def test_cutpoints_without_new_keys_is_unchanged(fake_reel):
    reel = Reel.at(fake_reel)
    cuts = cutpoints.run(reel, _cfg())
    assert [s["beat"] for s in cuts["segments"]] == [1, 2, 3]
    assert all(s["speed"] == 1.0 and s["frames"] == s["src_frames"] and "cold_open" not in s for s in cuts["segments"])


@needs_ffmpeg
def test_cold_open_id_collision(fake_reel):
    write_json(fake_reel / "cue_sheet.json", {"cold_open": {"beat": 2, "id": 3}})
    with pytest.raises(StageError):
        cutpoints.run(Reel.at(fake_reel), _cfg())


@needs_ffmpeg
def test_voice_and_speaker_lengths_at_speed(fake_reel):
    write_json(fake_reel / "cue_sheet.json", {"speed": 1.25, "cold_open": {"beat": 2, "id": 0},
                                              "beats": [{"beat": 3, "voice_ramp_db": [0, 2]}]})
    reel = Reel.at(fake_reel)
    cfg = _cfg()
    cuts = cutpoints.run(reel, cfg)
    sources = {"s1": json.loads((fake_reel / "work" / "sources.json").read_text())["sources"][0]}
    out = fake_reel / "work" / "voice.wav"
    render.build_voice(reel, cuts, sources, out, json.loads((fake_reel / "cue_sheet.json").read_text()))
    x, _ = media.read_wav(out, SR48)
    assert len(x) == pytest.approx(cuts["duration"] * SR48, abs=2)
    # speech lands where cuts.json says the words are (sped-up timeline)
    env = 20 * np.log10(np.sqrt(np.convolve(x ** 2, np.ones(480) / 480, "same")) + 1e-9)
    for s in cuts["segments"]:
        w = s["words"][1]
        mid = int((w["start"] + w["end"]) / 2 * SR48)
        assert env[mid] > -30, (s["beat"], w)
    # picture: exact output frame count per segment
    layout = render.build_layout(cfg, None)
    rdir = fake_reel / "work" / "r"
    rdir.mkdir()
    spk = render.render_speaker(reel, cfg, cuts, sources, layout, rdir)
    for s in cuts["segments"]:
        info = media.run([media.tool("ffprobe"), "-v", "error", "-count_frames", "-select_streams", "v:0", "-show_entries",
                          "stream=nb_read_frames", "-of", "csv=p=0", str(rdir / f"spk_{s['index']:03d}.mp4")]).stdout
        assert int(info.strip()) == s["frames"]
    assert media.probe(spk)["duration"] == pytest.approx(cuts["duration"], abs=0.05)


@needs_ffmpeg
def test_sfx_generate_deterministic_and_clean(tmp_path):
    a = sfx.generate(tmp_path / "a")
    b = sfx.generate(tmp_path / "b")
    assert set(a["files"]) == {"whoosh", "pop", "hit", "tick"}
    for name, f in a["files"].items():
        assert f["sha256"] == b["files"][name]["sha256"]
        assert f["true_peak_db"] <= -1.0 and f["peak_dbfs"] == pytest.approx(-6.0, abs=0.1)
        assert f["duration"] == pytest.approx(sfx.SPECS[name][0], abs=0.002)
        x, _ = media.read_wav(f["path"], SR48)
        assert abs(x[0]) < 0.02 and abs(x[-1]) < 0.01  # faded at both ends: no clicks


@needs_ffmpeg
def test_master_audio_sfx_drops_and_clean(fake_reel, tmp_path):
    lib = sfx.generate(tmp_path / "sfx")["files"]
    music = tmp_path / "music.wav"
    _write_wav(music, 0.2 * np.sin(2 * np.pi * 440 * np.arange(SR48 * 20) / SR48), SR48)
    cue = {"speed": 1.25, "cold_open": {"beat": 2, "id": 0},
           "music": {"path": str(music), "gain_db": -6, "fade_in": 0.05, "fade_out": 0.05},
           "music_drops": [{"from_beat": 2, "to_beat": 2, "level_db": -60},
                           {"before_beat": 1, "duration": 0.3, "level_db": -60, "fade_out": 0.03, "fade_in": 0.02}],
           "beats": [{"beat": 1, "sfx": [{"path": lib["whoosh"]["path"], "type": "whoosh", "at": -0.12, "level_db": -24}]},
                     {"beat": 0, "sfx": [{"path": lib["hit"]["path"], "type": "hit", "word": "94", "level_db": -18}]}]}
    write_json(fake_reel / "cue_sheet.json", cue)
    reel = Reel.at(fake_reel)
    cfg = _cfg()
    cuts = cutpoints.run(reel, cfg)
    sources = {"s1": json.loads((fake_reel / "work" / "sources.json").read_text())["sources"][0]}
    voice = render.build_voice(reel, cuts, sources, fake_reel / "work" / "voice.wav", cue)
    rep = render.master_audio(reel, cfg, voice, cue, cuts, fake_reel / "work" / "mix.wav", False)
    assert rep["sfx"] == 2 and rep["music"] and len(rep["music_drops"]) == 2
    assert rep["true_peak_db"] <= -1.0
    whoosh = next(s for s in rep["sfx_plan"] if s["type"] == "whoosh")
    assert whoosh["at"] == pytest.approx(cuts["segments"][1]["out_start"] - 0.12, abs=1e-3)
    assert whoosh["applied_gain_db"] == pytest.approx(cfg["master"]["target_lufs"] - 24 - lib["whoosh"]["momentary_max_lufs"], abs=0.2)
    # music is gone inside the beat-2 drop
    x, _ = media.read_wav(fake_reel / "work" / "mix.wav", SR48)
    b2 = cuts["segments"][2]
    a = int((b2["out_start"] + 0.3) * SR48)
    clean = render.master_audio(reel, cfg, voice, cue, cuts, fake_reel / "work" / "mix_clean.wav", False, clean=True)
    assert clean["sfx"] == 0 and not clean["music"] and clean["clean"]
    # music audible before the drop, inaudible inside it (compare full mix with the clean voice-only mix)
    y, _ = media.read_wav(fake_reel / "work" / "mix_clean.wav", SR48)
    n = min(len(x), len(y))
    resid = x[:n] - y[:n] * (10 ** ((rep["iterations"][-1]["voice_gain_db"] - clean["iterations"][-1]["voice_gain_db"]) / 20))
    rms = lambda s, e: float(np.sqrt(np.mean(resid[s:e] ** 2)))  # noqa: E731
    pre = cuts["segments"][1]
    before = rms(int((pre["out_start"] + 0.5) * SR48), int((pre["out_start"] + 1.0) * SR48))
    inside = rms(a, min(a + int(0.4 * SR48), int((b2["out_start"] + b2["duration"]) * SR48)))
    assert before > 10 * inside


@needs_ffmpeg
def test_sfx_cue_list(fake_reel, tmp_path):
    lib = sfx.generate(tmp_path / "sfx")["files"]
    write_json(fake_reel / "cue_sheet.json", {"speed": 1.25, "cold_open": {"beat": 2, "id": 0}, "beats": [
        {"beat": 0, "sfx": [{"path": lib["hit"]["path"], "type": "hit", "word": "94", "level_db": -18}]},
        {"beat": 1, "sfx": [{"path": lib["whoosh"]["path"], "at": -0.12, "level_db": -24, "label": "section"}]}],
        "music_drops": [{"from_beat": 2, "to_beat": 2}]})
    reel = Reel.at(fake_reel)
    cuts = cutpoints.run(reel, _cfg())
    out = sfx.cue_list(reel, _cfg())
    text = out.read_text()
    assert out == fake_reel / "deliver" / "SFX_CUES.md"
    hit_t = next(w["start"] for w in cuts["segments"][0]["words"] if w["text"] == "94.")
    assert f"| 1 | {sfx.timecode(hit_t)} | {int(round(hit_t * FPS))} | hit | 0 |" in text
    assert "| whoosh | 1 |" in text and "-24 dB vs voice" in text and "## Music drops" in text
    assert f"({cuts['duration']:.3f} s, 30 fps)" in text


@needs_ffmpeg
def test_final_render_writes_clean_stem(fake_reel, tmp_path):
    lib = sfx.generate(tmp_path / "sfx")["files"]
    write_json(fake_reel / "cue_sheet.json", {"speed": 1.25, "cold_open": {"beat": 2, "id": 0}, "beats": [
        {"beat": 1, "sfx": [{"path": lib["whoosh"]["path"], "at": -0.12, "level_db": -24}]}]})
    reel = Reel.at(fake_reel)
    cfg = load_config(overrides={"judge": {"enabled": False}, "captions": {"enabled": False},
                                 "video": {"preset": "ultrafast"}, "master": {"voice_chain": ""}})
    cuts = cutpoints.run(reel, cfg)
    write_json(reel.approvals_file, {"cut_review": {"sha256": cuts["sha256"], "by": "test"}})
    info = render.run(reel, cfg)
    full, clean = reel.resolve(info["output"]), reel.resolve(info["clean_output"])
    assert clean.name == "final_clean.mp4" and info["audio"]["sfx"] == 1 and info["audio"]["clean"]["sfx"] == 0
    pf, pc = media.probe(full), media.probe(clean)
    assert pf["duration"] == pytest.approx(cuts["duration"], abs=0.05)
    assert pc["duration"] == pytest.approx(pf["duration"], abs=0.03)
    assert pc["video"]["width"] == 1080 and pc["audio"]["codec"] == "aac"
    assert info["audio"]["clean"]["true_peak_db"] <= -1.0
