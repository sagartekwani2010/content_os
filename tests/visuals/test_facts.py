"""Every number the visuals can draw is a fact quoted from the eval write-up; specs cannot add numbers."""

import json
from pathlib import Path

from content_os.visuals.facts import FACTS, bare_numbers, fill, number_problems, verify_sources
from content_os.visuals.scenes import number_errors

ROOT = Path(__file__).resolve().parents[2]


def test_every_fact_quote_is_in_its_source():
    assert verify_sources() == []


def test_key_numbers():
    assert FACTS["table_mae"].value == 83.6 and FACTS["table_ci"].value == (59.9, 109.9)
    assert FACTS["direct_mae"].value == 77.3 and FACTS["oracle_direct_mae"].value == 45.2
    assert (FACTS["caught"].value, FACTS["worst"].value, FACTS["flagged"].value) == (12, 15, 31)
    assert (FACTS["dish_true_kcal"].value, FACTS["dish_est_kcal"].value, FACTS["chicken_conf"].value) == (499, 94, 0.3)
    # script roundings shown on screen are the script's own
    assert (FACTS["table_mae_spoken"].value, FACTS["direct_mae_spoken"].value, FACTS["oracle_direct_spoken"].value) == (84, 77, 45)


def test_fill_and_bare_numbers():
    assert fill("Fable {fable} · {usda_foods} foods · CI {table_ci:lo}–{table_ci:hi}") == "Fable 5.2 · 13,224 foods · CI 59.9–109.9"
    assert bare_numbers("Nutrition5k Im2Calories {fable}") == []
    assert bare_numbers("missed by 90 kcal") == ["90"]
    assert number_problems("Fable 5.2", "on Fable 5.2 it") == []
    assert number_problems("one answer: +90 kcal", "One answer moved it") == ["90"]


def test_spec_number_guard():
    beat = {"line": "It missed by about 84 calories.", "params": {
        "number": {"value": 84}, "label": "≈84 kcal", "sub": "really 90", "ok": "{table_mae}", "n": "@nope"}}
    errs = number_errors(beat)
    assert any("number.value" in e for e in errs)  # raw number in a numeric slot
    assert any("'90'" in e for e in errs)          # unsourced digits in text
    assert any("unknown fact @nope" in e for e in errs)
    assert not any("label" in e for e in errs)      # 84 is spoken in the line


def test_food_tracker_spec_has_no_raw_numbers():
    from content_os.visuals.script import load_lines

    sheet = json.loads((ROOT / "outputs/food-tracker-reel/visual_cues.json").read_text())
    lines = load_lines(ROOT / "outputs/food-tracker-reel/TELEPROMPTER.md")
    for b in sheet["beats"]:
        errs = [e for e in number_errors({**b, "line": lines[b["beat"]]}) if "unknown fact @lunch" not in e]
        assert errs == [], (b["beat"], errs)
