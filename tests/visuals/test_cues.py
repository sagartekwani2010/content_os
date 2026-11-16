"""Anchored cue resolution (pure Python, no media)."""

import json
from pathlib import Path

import pytest

from content_os.visuals.cues import default_duration, expand, proportional_words, resolve_beat, spoken_tokens

ROOT = Path(__file__).resolve().parents[2]
LINE = "The lazy version, one prompt asking for calories: 77. Statistically, a tie."


def words_for(texts, t0=0.3, step=0.4):
    return [{"text": w, "start": round(t0 + i * step, 3), "end": round(t0 + i * step + 0.3, 3)} for i, w in enumerate(texts)]


def test_expand_numbers_and_words():
    assert expand("77.") == ["seventy", "seven"]
    assert expand("seventy-seven") == ["seventy", "seven"]
    assert expand("13,224") == ["thirteen", "thousand", "two", "hundred", "twenty", "four"]
    assert expand("0.3") == ["zero", "point", "three"]
    assert expand(".3") == ["point", "three"]
    assert expand("5.2") == ["five", "point", "two"]
    assert expand("what's") == ["what's"]
    assert spoken_tokens(["Its", "194"])[1] == [0, 1, 1, 1, 1]


def test_exact_match_on_digits_vs_words():
    ws = words_for("The lazy version, one prompt asking for calories: seventy-seven. Statistically, a tie.".split())
    cues = [{"on_word": "77", "action": "countup", "target": "v", "emphasis": True},
            {"on_word": "tie", "action": "pop", "target": "t", "offset": 0.0}]
    res, rep = resolve_beat(LINE, cues, ws, 6.0)
    assert [r.method for r in res] == ["exact", "exact"]
    assert res[0].t == pytest.approx(0.3 + 8 * 0.4 - 0.1)
    assert res[0].dur == pytest.approx(0.7)  # emphasis default
    assert res[1].t == pytest.approx(0.3 + 11 * 0.4)
    assert rep["fallbacks"] == []


def test_misrecognised_word_is_interpolated_and_reported():
    texts = LINE.split()
    texts[-1] = "tight."  # ASR error on the anchor word
    texts[-2] = "uh"
    res, rep = resolve_beat(LINE, [{"on_word": "tie", "action": "pop", "target": "t", "offset": 0}],
                            words_for(texts), 6.0)
    assert res[0].method == "interpolated"
    assert rep["fallbacks"] and rep["fallbacks"][0]["on_word"] == "tie"
    assert 0.3 + 9 * 0.4 < res[0].t <= 6.0


def test_no_transcript_falls_back_to_proportional():
    res, rep = resolve_beat(LINE, [{"on_word": "tie", "action": "pop", "target": "t", "offset": 0}], [], 6.0)
    assert res[0].method == "proportional"
    assert 4.0 < res[0].t < 6.0
    assert rep["methods"]["proportional"] == 1


def test_word_index_anchor_end_occurrence_and_clamps():
    line = "The lazy version matched it. The lazy version."
    ws = words_for(line.split())
    res, _ = resolve_beat(line, [
        {"on_word": 0, "action": "fade", "target": "a", "offset": -5},
        {"on_word": "lazy version", "occurrence": 2, "anchor": "end", "action": "write", "target": "b", "offset": 0,
         "dur": 5}], ws, 6.0)
    assert res[0].t == 0.0  # clamped to clip start
    assert res[1].t == pytest.approx(ws[7]["end"])
    assert res[1].dur == 0.8  # clamped to the 0.3-0.8 s motion range


def test_bad_cues_raise():
    with pytest.raises(ValueError):
        resolve_beat(LINE, [{"on_word": "banana", "action": "pop", "target": "x"}], [], 5)
    with pytest.raises(ValueError):
        resolve_beat(LINE, [{"on_word": "tie", "action": "explode", "target": "x"}], [], 5)
    with pytest.raises(ValueError):
        resolve_beat(LINE, [{"on_word": 99, "action": "pop", "target": "x"}], [], 5)


def test_food_tracker_cues_resolve_against_teleprompter_lines():
    from content_os.visuals.script import load_lines

    sheet = json.loads((ROOT / "outputs/food-tracker-reel/visual_cues.json").read_text())
    lines = load_lines(ROOT / "outputs/food-tracker-reel/TELEPROMPTER.md")
    assert sorted(lines) == [b["beat"] for b in sheet["beats"]]
    for b in sheet["beats"]:
        resolve_beat(lines[b["beat"]], b["cues"], [], 8.0)  # raises if a phrase is not in the line


def test_default_duration_and_proportional_words():
    d = default_duration(LINE)
    assert 4 < d < 8
    ws = proportional_words(LINE, d)
    assert len(ws) == len(LINE.split()) and ws[-1]["end"] <= d


def test_last_word_motion_is_moved_to_finish_before_the_cut():
    ws = words_for(LINE.split())
    dur = ws[-1]["end"] + 0.08  # tight cut, like the pipeline's 80 ms tail
    res, rep = resolve_beat(LINE, [{"on_word": "tie", "action": "pop", "target": "t", "emphasis": True}], ws, dur)
    assert res[0].t + res[0].dur <= dur - 2 / 30 + 1e-9
    assert rep["fit_shifts"] and rep["fit_shifts"][0]["shift_s"] < 0
