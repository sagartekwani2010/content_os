"""Full-frame section transition cards (cue sheet ``section_cards``). No network: the font must already
be in ~/.cache/content_os/fonts (``python -m content_os.pipeline setup``); font-dependent tests skip otherwise."""

import numpy as np
import pytest

from content_os.pipeline import cards, cutpoints, media, render
from content_os.pipeline.reel import Reel, StageError, write_json

from .conftest import needs_ffmpeg
from .test_speed_coldopen_sfx import _cfg, fake_reel  # noqa: F401  (fixture)

HAVE_FONT = (cards.FONT_DIR / cards.FONT_BOLD).exists() and (cards.FONT_DIR / cards.FONT_SEMI).exists()
needs_font = pytest.mark.skipif(not HAVE_FONT, reason="Barlow Condensed not installed (pipeline setup)")


def test_split_title():
    assert cards.split_title({"title": "THE RESEARCH"}) == ("THE", ["RESEARCH"])
    assert cards.split_title({"title": "Next up: workout analyser"}) == ("NEXT UP", ["WORKOUT", "ANALYSER"])
    assert cards.split_title({"title": "THE SECRET SAUCE"}) == ("THE", ["SECRET", "SAUCE"])
    assert cards.split_title({"title": "GYM JARVIS", "kicker": "meet my"}) == ("MEET MY", ["GYM", "JARVIS"])
    assert cards.split_title({"title": "THE"}) == ("", ["THE"])
    assert cards.split_title({"title": "A\nB C"}) == ("", ["A", "B C"])


def _cuts():
    segs = [{"beat": b, "out_start": a, "duration": d, "words": []} for b, a, d in [(1, 0.0, 2.0), (2, 2.0, 3.0), (3, 5.0, 2.0)]]
    return {"fps": 30, "duration": 7.0, "segments": segs}


def test_plan_is_frame_exact():
    p = cards.plan(_cuts(), {"section_cards": [{"beat": 3, "title": "B"}, {"beat": 2, "title": "A", "dur": 0.6}]})
    assert [c["beat"] for c in p] == [2, 3]
    assert p[0]["start_frame"] == round((2.0 - 0.05) * 30) and p[0]["frames"] == 18
    assert p[1]["start_frame"] == round((5.0 - 0.05) * 30) and p[1]["frames"] == 21
    assert cards.plan(_cuts(), None) == []
    with pytest.raises(StageError):
        cards.plan(_cuts(), {"section_cards": [{"beat": 9, "title": "X"}]})
    with pytest.raises(StageError):
        cards.plan(_cuts(), {"section_cards": [{"beat": 2, "title": "A", "dur": 3.5}, {"beat": 3, "title": "B"}]})


def test_motion_curves():
    assert cards.ease_scale(0) == pytest.approx(1.12)
    assert [cards.ease_scale(i) for i in range(6)] == sorted([cards.ease_scale(i) for i in range(6)], reverse=True)
    assert cards.ease_scale(5) == 1.0 and cards.ease_scale(15) == 1.0
    assert [round(cards.frame_alpha(i, 21), 2) for i in range(15, 21)] == [1.0, 1.0, 0.8, 0.6, 0.4, 0.2]


@needs_font
def test_render_frames_punch_and_fade(tmp_path):
    from PIL import Image

    paths = cards.render_frames({"title": "THE RESEARCH", "accent": "cyan"}, 21, 1080, 1920, tmp_path, "c")
    assert len(paths) == 21
    ims = [np.asarray(Image.open(p)) for p in paths]
    assert ims[0].shape == (1920, 1080, 4)

    def text_width(a):  # bright (white text) columns
        cols = np.where((a[..., :3].min(axis=2) > 200).any(axis=0))[0]
        return cols.max() - cols.min()

    assert text_width(ims[0]) > 1.08 * text_width(ims[10])        # punched in at frame 0
    assert text_width(ims[5]) == pytest.approx(text_width(ims[10]), abs=2)
    assert ims[10][..., 3].min() == 255 and ims[-1][..., 3].max() == 51  # opaque, then fading out
    # dark navy background, not pure black; enough bright ink that blackdetect never fires
    assert tuple(ims[10][5, 5, :3]) == cards.BG
    assert (ims[10][..., :3].max(axis=2) > 60).mean() > 0.03


@needs_ffmpeg
@needs_font
def test_draft_render_overlays_cards_full_frame(fake_reel):  # noqa: F811
    cue = {"section_cards": [{"beat": 2, "title": "THE TEST", "accent": "yellow", "dur": 0.7}]}
    write_json(fake_reel / "cue_sheet.json", cue)
    reel = Reel.at(fake_reel)
    cfg = _cfg()
    cfg["video"]["draft_preset"] = "ultrafast"
    cuts = cutpoints.run(reel, cfg)
    info = render.run(reel, cfg, draft=True)
    card = info["section_cards"][0]
    b2 = next(s for s in cuts["segments"] if s["beat"] == 2)
    assert card["start_frame"] == round((b2["out_start"] - 0.05) * 30) and card["frames"] == 21
    out = reel.resolve(info["output"])
    assert media.probe(out)["duration"] == pytest.approx(cuts["duration"], abs=0.05)
    frames = [a for _, a in media.sample_frames(out, 0, cuts["duration"], 30, 270, 480)]

    def card_like(f):  # navy everywhere, including the speaker half (bottom)
        return f is not None and f[300:470].mean() < 40 and f[:40].mean() < 40

    hold = frames[card["start_frame"] + 10]
    assert card_like(hold)
    assert not card_like(frames[card["start_frame"] - 3]) and not card_like(frames[card["start_frame"] + card["frames"] + 2])
    blacks = media.ffmpeg("-i", str(out), "-vf", "blackdetect=d=0.1:pix_th=0.10", "-an", "-f", "null", "-").stderr
    assert "black_start" not in blacks
