"""The reel pipeline's render stage picks up per-beat clips through cue_sheet.visual_clips."""

import json

import pytest

from content_os.pipeline.reel import Reel, StageError
from content_os.pipeline.render import check_visual_clips, plan_visuals
from content_os.visuals.build import words_from_cuts

CUTS = {"fps": 30, "duration": 6.0, "sha256": "abc",
        "segments": [{"beat": 1, "out_start": 0.0, "duration": 2.0, "words": [{"text": "Hi", "start": 0.04, "end": 0.3}]},
                     {"beat": 2, "out_start": 2.0, "duration": 2.5, "words": [{"text": "Two", "start": 2.1, "end": 2.4}]},
                     {"beat": 3, "out_start": 4.5, "duration": 1.5, "words": [{"text": "Three", "start": 4.6, "end": 5.0}]}]}


def test_clips_fill_beats_without_visuals(tmp_path):
    d = tmp_path / "work" / "visuals"
    d.mkdir(parents=True)
    for n in (1, 2):
        (d / f"beat_{n:02d}.mp4").write_bytes(b"")
    cue = {"visual_clips": "work/visuals",
           "beats": [{"beat": 2, "visual": {"type": "card", "text": "X"}, "start_offset": 0.4}]}
    plan = plan_visuals(CUTS, cue, False, tmp_path)
    by_beat = {p["beat"]: p for p in plan}
    assert by_beat[1]["visual"] == {"type": "clip", "path": "work/visuals/beat_01.mp4"}
    assert by_beat[1]["start_frame"] == 0
    assert by_beat[2]["visual"]["type"] == "card"  # explicit visual wins
    assert by_beat[3]["visual"]["type"] == "placeholder"  # no clip file
    # draft never uses clips; without root the old behaviour is unchanged
    assert all(p["visual"]["type"] == "placeholder" for p in plan_visuals(CUTS, cue, True, tmp_path))
    assert plan_visuals(CUTS, {"beats": []}, False) == plan_visuals(CUTS, None, False)


def test_stale_clips_are_refused(tmp_path):
    reel = Reel.at(tmp_path)
    d = tmp_path / "work" / "visuals"
    d.mkdir(parents=True)
    (d / "visuals.json").write_text(json.dumps({"cuts_sha256": "old"}))
    with pytest.raises(StageError):
        check_visual_clips(reel, {"visual_clips": "work/visuals"}, CUTS)
    (d / "visuals.json").write_text(json.dumps({"cuts_sha256": "abc"}))
    check_visual_clips(reel, {"visual_clips": "work/visuals"}, CUTS)
    check_visual_clips(reel, None, CUTS)


def test_words_from_cuts_are_relative_to_beat_start():
    t = words_from_cuts(CUTS)
    assert t[2]["duration"] == 2.5
    assert t[2]["words"][0]["start"] == pytest.approx(0.1)
    assert t[3]["words"][0]["end"] == pytest.approx(0.5)


def test_render_visual_accepts_clip(tmp_path):
    from content_os.pipeline import media
    from content_os.pipeline.config import load_config
    from content_os.pipeline.layouts import Rect
    from content_os.pipeline.render import render_visual

    if not media.have_tool("ffmpeg"):
        pytest.skip("ffmpeg missing")
    reel = Reel.at(tmp_path)
    clip = tmp_path / "work" / "visuals" / "beat_01.mp4"
    clip.parent.mkdir(parents=True)
    media.ffmpeg("-v", "error", "-f", "lavfi", "-i", "testsrc2=s=1080x960:r=30:d=0.5", "-pix_fmt", "yuv420p", str(clip))
    cfg = load_config(tmp_path, {})
    item = {"visual": {"type": "clip", "path": "work/visuals/beat_01.mp4"}, "frames": 24}  # longer: holds last frame
    out = render_visual(reel, cfg, item, Rect(0, 0, 1080, 960), 30, tmp_path / "v.mp4", tmp_path)
    v = media.probe(out)["video"]
    assert (v["width"], v["height"]) == (1080, 960)
    assert abs(float(media.probe(out)["duration"]) - 0.8) < 0.05
