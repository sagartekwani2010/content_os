"""Spec-level themes, glyph fallback, and the receipts / quote templates (fable52 reels, 19 Nov 2026)."""

from content_os.visuals import rough as R
from content_os.visuals import templates as T
from content_os.visuals.scenes import validate_spec


def test_theme_remaps_and_resets():
    try:
        R.set_theme("dark")
        dark_ink = R.color(R.INK)
        R.set_theme("paper")
        assert R.color(R.INK) != dark_ink
        R.set_theme({"#16150F": "#FF0000"})
        assert R.color(R.INK) == R.color("#FF0000")
    finally:
        R.set_theme(None)


def test_glyph_fallback_runs():
    runs = R.runs("₹22 → x", "bold")
    assert ("₹", "bold") in runs  # Patrick Hand (digits) has no rupee sign
    assert any(w == "sym" for _, w in runs)  # no hand font has an arrow
    assert R.text_width("₹22 → x", 40) > 0


def _beat(template, params, cues, line):
    return {"beat": 1, "template": template, "params": {"chip": "none", **params}, "cues": cues, "line": line}


def test_receipts_and_quote_build_and_validate():
    line = "Nearly forty times the price. Same scores."
    rc = _beat("receipts", {"left": {"title": "Fable {fable}", "total": "{cost_fable_inr}"},
                            "right": {"title": "Haiku {haiku}", "total": "{cost_haiku_inr}"},
                            "times": "{price_ratio}", "eq_text": "same scores"},
               [{"on_word": "forty times", "action": "draw", "target": "rcpt_l"},
                {"on_word": "Same scores", "action": "draw", "target": "eq"}], line)
    q = _beat("quote", {"text": "If managed poorly, AI could be a risk.", "by": "someone",
                        "timeline": {"a": {"date": "{d_quote}"}, "b": {"date": "{d_launch}"}, "gap": "{gap_weeks}"}},
              [{"on_word": "Nearly", "action": "write", "target": "q0"},
               {"on_word": "Same", "action": "draw", "target": "gap"}], line)
    assert validate_spec({"beats": [rc, q]}, {"images": {}}) == []


def test_unsourced_number_in_receipts_is_rejected():
    rc = _beat("receipts", {"left": {"title": "Fable", "total": "₹99"}, "right": {"title": "Haiku", "total": "x"}},
               [], "Nearly forty times the price.")
    assert any("99" in e for e in validate_spec({"beats": [rc]}, {"images": {}}))


def test_flow_dashed_zone_tag_legend():
    P = {"cols": 3, "rows": 2, "legend": {"solid": "disclosed"}, "nodes": [
        {"id": "a", "text": "A\nB", "dashed": True, "tag": "my read", "at": [0, 0]},
        {"id": "z", "kind": "zone", "text": "zone", "at": [1, 0], "w": 300, "h": 120},
        {"id": "d", "kind": "diamond", "text": "X\nY", "at": [2, 1]}], "edges": [{"from": "a", "to": "d"}]}
    ids = {e.id for e in T.build("flow", P, {"images": {}})}
    assert {"a", "a_tag", "z", "d", "e_a_d", "legend"} <= ids
