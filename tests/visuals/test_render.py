"""Every beat of the food-tracker spec builds and animates; determinism; encoding.
No personal photos or logs: images are absent (placeholders) and the lunch facts are stand-ins."""

import json
from pathlib import Path

import numpy as np
import pytest

from content_os.visuals import facts, rough
from content_os.visuals.script import load_lines

ROOT = Path(__file__).resolve().parents[2]
fonts_missing = any(not (rough.FONT_DIR / f[0]).exists() for f in rough.FONTS.values())
pytestmark = pytest.mark.skipif(fonts_missing, reason="fonts not cached; run python -m content_os.visuals setup")


@pytest.fixture
def sheet(monkeypatch):
    stand_ins = {"lunch_kcal": 600, "lunch_lo": 400, "lunch_hi": 900, "lunch_least_conf": 0.35}
    for i in range(8):
        stand_ins.update({f"lunch_i{i}_g": 100 + i, f"lunch_i{i}_kcal": 50 + i, f"lunch_i{i}_protein": 1.5})
    for k, v in stand_ins.items():
        monkeypatch.setitem(facts.FACTS, k, facts.Fact(v, str(v), "test stand-in", "-", "-"))
    s = json.loads((ROOT / "outputs/food-tracker-reel/visual_cues.json").read_text())
    lines = load_lines(ROOT / "outputs/food-tracker-reel/TELEPROMPTER.md")
    for b in s["beats"]:
        b["line"] = lines[b["beat"]]
    return s


CTX = {"images": {}, "simulated_log": None}


def renderer(sheet, beat_no, words=None, duration=None):
    from content_os.visuals.cues import default_duration
    from content_os.visuals.render import BeatRenderer

    b = next(b for b in sheet["beats"] if b["beat"] == beat_no)
    return BeatRenderer(b, CTX, words or [], duration or default_duration(b["line"]))


def test_spec_validates(sheet):
    from content_os.visuals.scenes import validate_spec

    assert validate_spec(sheet, CTX) == []


@pytest.mark.parametrize("beat", range(1, 15))
def test_every_beat_builds_and_animates(sheet, beat):
    r = renderer(sheet, beat)
    first, key = r.frame(0.0), r.frame(r.key_time())
    assert key.shape == (960, 1080, 4)
    assert np.abs(key.astype(int) - first.astype(int)).sum() > 0


def test_frames_are_deterministic(sheet):
    assert np.array_equal(renderer(sheet, 8).frame(3.0), renderer(sheet, 8).frame(3.0))


def test_animation_follows_word_times(sheet):
    """Beat 19's "Workout Analyser" is absent before those words are spoken and present after."""
    line = next(b["line"] for b in sheet["beats"] if b["beat"] == 19)
    words = [{"text": w, "start": 0.3 + 0.4 * i, "end": 0.6 + 0.4 * i} for i, w in enumerate(line.split())]
    r = renderer(sheet, 19, words, words[-1]["end"] + 1.5)
    cue = next(c for c in r.resolved if c.target == "workout")
    wi = line.split().index("Workout")
    assert cue.method == "exact" and cue.t == pytest.approx(words[wi]["start"] - 0.1)
    x, y, w, h = next(e for e in r.elements if e.id == "workout").bounds()
    box = (int(x), int(y), int(x + w), int(y + h))

    def ink(t):
        f = r.frame(t)[box[1]:box[3], box[0]:box[2], :3].astype(int)
        return int((np.abs(f - f[0, 0]).sum(axis=2) > 120).sum())
    assert ink(cue.t - 0.2) < 50
    assert ink(cue.t + cue.dur + 0.1) > 500


def test_table_search_uses_real_usda_rows():
    from content_os.visuals.templates import usda_rows

    rows = usda_rows("Soup, lentil")
    assert len(rows) == 8 and "Soup, lentil" in rows


def test_encode_clip(sheet, tmp_path):
    from content_os.pipeline import media
    from content_os.visuals.render import encode

    if not media.have_tool("ffmpeg"):
        pytest.skip("ffmpeg missing")
    info = encode(renderer(sheet, 14, duration=0.5), tmp_path / "b.mp4")
    v = media.probe(tmp_path / "b.mp4")["video"]
    assert info["frames"] == 15 and (v["width"], v["height"]) == (1080, 960) and "709" in json.dumps(v)


@pytest.mark.parametrize("tight", [False, True])
def test_every_countup_lands_and_holds_before_the_cut(sheet, tight):
    """Each counted number shows exactly its final value for >= 0.6 s before the beat ends
    (also when the take is cut tight: last word + 80 ms)."""
    from content_os.visuals.cues import COUNTUP_HOLD, default_duration, proportional_words
    from content_os.visuals.elements import Number, ease_out

    for b in sheet["beats"]:
        dur = default_duration(b["line"])
        words = proportional_words(b["line"], dur)
        if tight:
            dur = words[-1]["end"] + 0.08
        r = renderer(sheet, b["beat"], words, dur)
        by_id = {e.id: e for e in r.elements}
        last_hold = dur - COUNTUP_HOLD
        for cue in r.resolved:
            if cue.action != "countup":
                continue
            assert cue.t + cue.dur <= last_hold + 1e-6, (b["beat"], cue.target, cue.t, cue.dur, dur)
            el = by_id[cue.target]
            if isinstance(el, Number):
                c = next(x for x in el.cues if x.action == "countup")
                for t in (last_hold, dur - 1 / 30):
                    assert el.text_at(ease_out(c.progress(t))) == el.text_at(1.0), (b["beat"], cue.target, t)
