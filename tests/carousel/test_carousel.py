import json
import subprocess

import pytest

from content_os.carousel import items as I
from content_os.carousel import render as CR


def _spec(tmp_path, slides):
    return {"spec": CR.SPEC, "id": "t", "media_dir": str(tmp_path / "media"), "slides": slides}


def test_wrap_respects_width():
    lines = I.wrap("Serves who it is for and what they need for dinner tonight", 44, 300)
    assert len(lines) > 1
    from content_os.visuals import rough as R
    assert all(R.text_width(ln, 44, "bold") <= 300 or " " not in ln for ln in lines)


def test_marker_stays_inside_word():
    st = I.marker(100, 300, 200, 72, "k")
    xs = [p[0] for p in st.passes[0]]
    half = st.width / 2
    assert min(xs) - half >= 100 - 12 and max(xs) + half <= 300 + 12


def test_layout_flags_small_text_and_ui_zone(tmp_path):
    spec = _spec(tmp_path, [])
    sd = {"n": 1, "kind": "still", "headline": "Hi", "items": [
        {"type": "text", "x": 70, "y": 700, "w": 900, "text": "tiny", "size": 30},
        {"type": "sticky", "x": 70, "y": 1100, "w": 400, "lines": ["low note"]}]}
    issues = CR.layout_issues(CR.Slide(sd, spec, 1))
    assert any("< 40px" in i for i in issues)
    assert any("UI zone" in i for i in issues)


def test_clean_slide_has_no_issues(tmp_path):
    sd = {"n": 1, "kind": "still", "headline": "A clean slide", "body": "Short body.",
          "items": [{"type": "quote", "x": 70, "y": 900, "w": 900, "lines": ["“a quote”"], "tag": "real run"}]}
    assert CR.layout_issues(CR.Slide(sd, _spec(tmp_path, []), 1)) == []


def test_render_still_and_video(tmp_path):
    folder = tmp_path / "out"
    folder.mkdir()
    slides = [
        {"n": 1, "name": "a", "kind": "still", "headline": "Still slide", "hl": ["Still"],
         "items": [{"type": "icon", "name": "bowl", "cx": 540, "cy": 950}]},
        {"n": 2, "name": "b", "kind": "video", "duration": 2, "headline": "Video slide",
         "items": [{"type": "icon", "name": "oven", "cx": 300, "cy": 950},
                   {"type": "arrow", "from": [450, 950], "to": [800, 950], "at": 0.2, "dur": 0.5}]},
    ]
    (folder / "slides.json").write_text(json.dumps(_spec(tmp_path, slides)))
    (folder / "CAPTION.txt").write_text("caption <b>")
    rep = CR.render(folder)
    assert rep["issues"] == []
    post = sorted((tmp_path / "media" / "POST").iterdir())
    assert [p.name for p in post] == ["01_a.jpg", "02_b.mp4"]
    v = CR.probe(post[1])
    kinds = {s["codec_type"]: s for s in v["streams"]}
    assert kinds["video"]["codec_name"] == "h264" and kinds["video"]["width"] == 1080
    assert kinds["video"]["height"] == 1350 and kinds["video"]["r_frame_rate"] == "30/1"
    assert kinds["audio"]["codec_name"] == "aac"
    assert abs(float(v["format"]["duration"]) - 2.0) < 0.1
    s = CR.probe(post[0])["streams"][0]
    assert s["codec_name"] == "mjpeg" and (s["width"], s["height"]) == (1080, 1350)
    html = (tmp_path / "media" / "PREVIEW.html").read_text()
    assert "POST/02_b.mp4" in html and "caption &lt;b&gt;" in html
    assert (tmp_path / "media" / "contact_sheet.jpg").exists()


def test_frame0_shows_headline_before_cues(tmp_path):
    sd = {"n": 1, "kind": "video", "duration": 2, "headline": "Frame zero",
          "items": [{"type": "icon", "name": "oven", "cx": 540, "cy": 800, "at": 1.0}]}
    sl = CR.Slide(sd, _spec(tmp_path, []), 1)
    bg = CR.R.paper_background(CR.W, CR.H)
    f0, fend = sl.frame(0.0, bg), sl.frame(1.9, bg)
    top, mid = slice(60, 200), slice(650, 950)
    assert (f0[top] != bg.toarray()[top]).any()      # headline drawn at frame 0
    assert (f0[mid] == bg.toarray()[mid]).all()      # the oven is not there yet
    assert (fend[mid] != bg.toarray()[mid]).any()    # and it has drawn on by the end


def test_unknown_spec_rejected(tmp_path):
    (tmp_path / "slides.json").write_text(json.dumps({"spec": "x", "id": "t", "slides": []}))
    with pytest.raises(ValueError):
        CR.render(tmp_path)


def test_new_rules_flag_empty_frame0_small_quotes_and_empty_lower_third(tmp_path):
    sd = {"n": 1, "kind": "video", "duration": 3, "headline": "Hi", "items": [
        {"type": "quote", "x": 70, "y": 500, "w": 900, "lines": ["“small”"], "size": 40, "at": 0.5}]}
    issues = " | ".join(CR.layout_issues(CR.Slide(sd, _spec(tmp_path, []), 1)))
    assert "frame 0" in issues and "phone reading" in issues and "lower third" in issues


def test_cover_photo_comes_from_one_spec_key(tmp_path):
    from PIL import Image
    p = tmp_path / "me.jpg"
    Image.new("RGB", (40, 50), "red").save(p)
    spec = {**_spec(tmp_path, []), "cover_photo": str(p)}
    sd = {"n": 1, "kind": "still", "headline": "Hi", "items": [{"type": "photo", "rect": [70, 400, 400, 500]}]}
    CR.Slide(sd, spec, 1)  # builds without a per-item path


def test_before_after_layout_frame0_shows_before_and_after_writes_on(tmp_path):
    sd = {"n": 3, "kind": "video", "duration": 4, "layout": "before_after", "headline": "Tell him who you are.",
          "body": "Day 1, you'd tell a trainer your job.", "copy": "Add: This is for me: [age].",
          "before": {"lines": ["“Suggest a diet.”", "→ “generic”"]},
          "after": {"lines": ["+ the line above", "→ “specific”"]}, "after_at": 1.0}
    sl = CR.Slide(sd, _spec(tmp_path, []), 12)
    ids = [e.id for e in sl.elements]
    assert {"copy", "before", "after"} <= set(ids)
    after = next(e for e in sl.elements if e.id == "after")
    before = next(e for e in sl.elements if e.id == "before")
    assert before.appear_cue() is None and after.appear_cue().t == 1.0
    assert not any("frame 0" in i for i in CR.layout_issues(sl))
