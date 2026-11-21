import pytest

from content_os.pipeline.captions import chunk_words, write_ass
from content_os.pipeline.config import load_config
from content_os.pipeline.layouts import LAYOUTS, Rect, build_layout, speaker_crop
from content_os.pipeline.render import plan_visuals


def layout(**params):
    cfg = load_config()
    cfg["layout"]["params"].update(params)
    return build_layout(cfg), cfg


def test_split_50_50_geometry_and_safe_areas():
    lay, cfg = layout(caption_position="top_safe")
    v, s = lay.panels["visual"], lay.panels["speaker"]
    assert (v.h, s.h, s.y) == (960, 960, 960)
    box = lay.caption_box
    assert box.bottom <= 960 - cfg["captions"]["margin_above_seam"]  # inside the top panel, above the seam
    assert box.bottom <= 1920 - cfg["safe_area"]["bottom"] and box.right <= 1080 - cfg["safe_area"]["right"]
    assert not box.intersects(s)
    assert lay.compose({"visual": "[a]", "speaker": "[b]"}) == "[a][b]vstack=inputs=2[base]"


def test_split_40_60_and_seam_captions():
    lay, _ = layout(speaker_ratio=0.4)
    assert lay.panels["speaker"].h == 768 and lay.panels["visual"].h == 1152
    seam, _ = layout(caption_position="seam")
    assert seam.caption_box.y < 960 < seam.caption_box.bottom


def test_layout_registry_and_validation():
    assert "split_vertical" in LAYOUTS
    with pytest.raises(ValueError):
        layout(speaker_ratio=0.95)


def test_speaker_crop_centres_face_and_clamps():
    panel = Rect(0, 960, 1080, 960)
    c = speaker_crop(3840, 2160, panel, 0.5, 0.45)
    assert (c.w, c.h) == (2430, 2160) and abs((c.x + c.w / 2) - 1920) <= 2
    edge = speaker_crop(3840, 2160, panel, 0.02, 0.45)
    assert edge.x == 0
    tight = speaker_crop(3840, 2160, panel, 0.5, 0.45, zoom=1.5)
    assert tight.h == 1440 and tight.y >= 0


def test_caption_chunks_two_to_four_words(tmp_path):
    cfg = load_config()
    words = [{"text": w, "start": 0.3 * i, "end": 0.3 * i + 0.25} for i, w in
             enumerate("If the steps never change, write a script instead.".split())]
    chunks = chunk_words([{"index": 0, "words": words}], cfg["captions"])
    assert all(2 <= len(c["text"].split()) <= 4 for c in chunks)
    assert " ".join(c["text"] for c in chunks) == "If the steps never change, write a script instead."
    assert all(a["end"] <= b["start"] for a, b in zip(chunks, chunks[1:]))
    lay, _ = layout()
    p = tmp_path / "c.ass"
    write_ass(p, chunks, lay, cfg["captions"])
    text = p.read_text()
    assert "PlayResY: 1920" in text and text.count("Dialogue:") == len(chunks)


def test_visual_plan_supports_15_beats():
    segs, t = [], 0.0
    for b in range(1, 16):
        segs.append({"beat": b, "out_start": t, "duration": 7.0})
        t += 7.0
    cuts = {"fps": 30, "duration": t, "segments": segs}
    cue = {"beats": [{"beat": b, "visual": {"type": "card", "text": f"B{b}"}, "start_offset": 0.5 if b > 1 else 0}
                     for b in range(1, 16)]}
    plan = plan_visuals(cuts, cue, draft=False)
    assert [p["beat"] for p in plan] == list(range(1, 16))
    assert sum(p["frames"] for p in plan) == round(t * 30)
    assert plan[1]["start"] == 7.5
    draft = plan_visuals(cuts, cue, draft=True)
    assert all(p["visual"]["type"] == "placeholder" for p in draft)


def test_bottom_safe_captions_sit_low_below_the_face():
    lay, cfg = layout(caption_position="bottom_safe")
    box, spk = lay.caption_box, lay.panels["speaker"]
    assert box.bottom == 1920 - cfg["captions"]["bottom_px"]
    assert box.y > spk.y + spk.h * 0.6  # lower part of the speaker panel, under chest and hands
