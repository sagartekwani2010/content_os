"""v6 (V6_FINAL_SPOKEN.md, ids 1-11 contiguous): visual_cues.json for both reels + the three CTA cards.

    .venv/bin/python outputs/fable52-deepdive/make_visual_specs_v6.py
    PYTHONPATH=. .venv/bin/python outputs/fable52-deepdive/make_visual_specs_v6.py --assets

Same visuals as v5, renumbered (v5 9 -> 7, 10 -> 9, 11 -> 10, 12 -> 11; v5 8 stays 8) with the new tips card. Never writes the
teleprompter / beats / cue / edits files; beat_02.mp4 is the creator's clip (not rendered here).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import make_visual_specs_v3 as v3  # noqa: E402
import make_visual_specs_v5 as v5  # noqa: E402
from make_visual_specs import REELS, beat, cue, scene  # noqa: E402
from make_visual_specs_v2 import QUOTE  # noqa: E402

TIPS = [
    {"rule": "Fable plans, a cheaper model builds.", "note": "Fable plans as the architect; Opus or Sonnet implements."},
    {"rule": "Run it on high, not max.",
     "note": "On one coding benchmark, max cost {max_low_ratio} more than low and still didn't score best ({pg_209})."},
    {"rule": "On long jobs, tell it how much budget is left.",
     "note": "In Anthropic's tests that raised its score from {tok_before} to {tok_after} ({pg_216})."},
]
v5.TIPS[:] = TIPS
v5.TIPS_CARD.update({"title": "MY {n_tips} FABLE TIPS", "rules": TIPS, "rule_size": 44})
v5.TIPS_PANEL.update({"title": "MY {n_tips} FABLE TIPS", "rules": TIPS})
RENUMBER = {1: 1, 2: 2, 3: 3, 4: 4, 5: 5, 6: 6, 9: 7, 8: 8, 10: 9, 11: 10, 12: 11}


def renumber(beats):
    out = []
    for b in beats:
        b["beat"] = RENUMBER[int(b["beat"])]
        out.append(b)
    return sorted(out, key=lambda b: b["beat"])


def v61(beats, main_reel: bool):
    """v6.1: MAIN beat 1 = Dario's photo + quote only; beat 7 opens on a big HOW I USE FABLE heading; beat 8 new line,
    no stickies, no "small test" callout."""
    by = {b["beat"]: b for b in beats}
    if main_reel:
        by[1] = beat(1, "quote", {"text": QUOTE["text"], "max_size": 46, "quote_bottom": 600, "top": 290,
                                  "by": "Dario Amodei, Anthropic CEO\nUN Security Council, {d_quote}", "by_size": 30,
                                  "image": "dario", "image_rect": [60, 262, 370, 478],
                                  "credit": "Photo: Kimberly White/Getty Images for TechCrunch · {cc_by2}",
                                  "enter": {"kind": "zoom", "scale": 1.12, "blur": 10, "frames": 7}}, [
            cue("Anthropic's own CEO", "pop", "marks"), cue("warned the UN", "write", "q0"), cue("that AI", "write", "q1"),
            cue("a risk", "write", "q2", emphasis=True), cue("all of humanity", "write", "q3"),
            cue("a risk", "write", "by", offset=0.6)])
    b7 = by[7]
    flow = {k: v for k, v in b7.items() if k in ("template", "params", "cues")}
    flow["params"] = {**flow["params"], "title": ""}
    flow["params"].pop("enter", None)
    flow["cues"] = [c for c in flow["cues"] if c["target"] != "title"]
    by[7] = beat(7, "card", {"text": "HOW I USE FABLE", "color": "purple", "size": 100,
                             "enter": {"kind": "zoom", "scale": 1.12, "blur": 8, "frames": 7}},
                 [cue("Even this reel", "pop", "card", emphasis=True, offset=-0.4)],
                 [scene("Fable wrote it", flow["template"], flow["params"], flow["cues"], kind="zoom")] + b7.get("scenes", []))
    b8 = by[8]
    ph = dict(b8["params"])
    ph["rows"] = [{"id": "r0", "text": "MY NUTRITION AGENT", "color": "green", "size": 52},
                  {"id": "r1", "text": "{n_plates} weighed plates", "size": 52}]
    ph["rows_bottom"] = 520
    bars = dict(b8["scenes"][0]["params"])
    bars.pop("note", None)
    bars["callout"] = [{"id": "c1", "text": "{portion_more_acc}", "color": "blue", "y": 400, "size": 62},
                       {"id": "c2", "text": "\u2248{plate_inr_more} more / plate", "y": 490, "size": 48},
                       {"id": "c4", "text": "{plate_cost_fable} vs {plate_cost_opus} at list price", "y": 540, "size": 28,
                        "color": "grey", "weight": "regular"}]
    bars["footer"] = "{n_plates} weighed plates · portion error {fable_g25} g vs {opus_g25} g"
    bars["y_label"] = "portion error, g (same {n_plates} plates)"
    by[8] = beat(8, "photo", ph, [cue("nutrition agent", "write", "r0"), cue("nutrition agent", "write", "r1", offset=0.3)],
                 [scene("Fable was", "bars", bars, [
                     cue("Fable was", "draw", "axis", dur=0.3), cue("Fable was", "draw", "fable", offset=0.1),
                     cue("14% more accurate", "pop", "c1", emphasis=True), cue("than Opus", "draw", "opus"),
                     cue("five rupees", "pop", "c2"), cue("per plate", "fade", "c4")], kind="slide")])
    return [by[k] for k in sorted(by)]


def main():
    v3.RULES_CARD.update(v5.RULES_CARD)
    for d, theme, beats in ((REELS / "fable52-main", "paper", v5.main_spec()), (REELS / "fable52-trial", "dark", v5.trial_spec())):
        if "--assets" in sys.argv:
            v3.RULES_CARD, v3.TIPS_CARD = v5.RULES_CARD, v5.TIPS_CARD
            v3.assets(d)
            v5.how_asset(d)
            continue
        spec = v3.spec(d.name, theme, v61(renumber(beats), d.name == "fable52-main"))
        spec["params"]["images"]["how"] = "assets/how_i_use_fable.png"
        spec["params"]["images"]["dario"] = "assets/dl/dario_cc_by_2.jpg"
        spec["notes"] = "v6 (V6_FINAL_SPOKEN.md, ids 1-11) generated by outputs/fable52-deepdive/make_visual_specs_v6.py."
        (d / "visual_cues.json").write_text(json.dumps(spec, indent=1, ensure_ascii=False) + "\n")
        print("wrote", d / "visual_cues.json")


if __name__ == "__main__":
    main()
