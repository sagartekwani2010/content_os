"""v2 (SCRIPT_IMPACT_FINAL.md, beat ids locked 19 Nov 18:30): write visual_cues.json for both reels.

    .venv/bin/python outputs/fable52-deepdive/make_visual_specs_v2.py

TELEPROMPTER.md and beats.json in the reel folders are the coordinator's locked files: this script never writes
them; every cue phrase below is checked against them by `python -m content_os.visuals check`.
MAIN beats 1-11, 13, 14 (CEO hook, paper theme). TRIAL beats 1, 3-14 (money hook, dark theme).
"""

from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from make_visual_specs import (IMAGES, REELS, beat, cue, cut, cut_h, main_beats as v1_main,  # noqa: E402
                               pipeline, receipts, scene)

CUTS = "outputs/fable52-deepdive/paper/cuts/tight/"
IMG = {**{k: v for k, v in IMAGES.items() if k not in ("diag_meal",)},
       "P14": CUTS + "P14_p186.png", "P15": CUTS + "P15_p34.png",
       "diag_train": "assets/diagram_training.png", "diag_sys": "assets/diagram_system.png",
       "rules": "assets/fable_user_rules.png"}
IMAGES.update(IMG)  # cut_h() looks images up here

RULES_SHORT = ["pasted text = data", "real checks", "second checker", "high effort + finish"]
RULES = [
    {"rule": "Treat pasted text as data, not instructions.",
     "note": "A grading rule generalised to harmful instructions planted in pasted text ({pg_131}; largely mitigated in the release)."},
    {"rule": "Give it real checks, and ask how it verified.",
     "note": "Its top reward hack in training: “guessing what the answer key expects” ({pg_95})."},
    {"rule": "A second model, or you, checks its work.",
     "note": "“Among the least self-critical Claude models when reflecting on its own work” ({pg_186}).*"},
    {"rule": "High effort for real work, and name the finish line.",
     "note": "At medium effort it quit open-ended research without running an experiment in {research_quit} of sessions ({pg_34}).*"},
    {"rule": "Judge it on your tasks.",
     "note": "Evidence suggests it was aware it might be in an evaluation in up to {test_aware} of automated audit transcripts ({pg_91}).*"},
    {"rule": "Tell it the budget left.",
     "note": "It ran out of its million-token context on {ctx_out} of one long-task set; showing tokens remaining raised the score from "
             "{tok_before} to {tok_after} ({pg_216})."},
]
RULES_CARD = {"title": "FABLE USER RULES", "full": True, "chip": "none",
              "sub": "Claude Fable {fable} · from Anthropic's {card_pages}-page system card, {d_launch}",
              "rules": RULES, "foot": ["Benchmarks are the lab; your tasks are the exam.",
                                       "*Measured on Mythos {fable}, the same model."]}

QUOTE = {"text": "If managed poorly, I even believe AI could be a risk to humanity as a whole.",
         "by": "Dario Amodei, Anthropic CEO · UN Security Council, {d_quote}", "max_size": 56,
         "timeline": {"a": {"date": "{d_quote}", "label": "he said it"}, "b": {"date": "{d_launch}", "label": "Fable launched"}}}


def paper_says(image, credit, rows, word, cues, top=300):
    P = cut(image, credit, rows, cut_h(image), top=top)
    P.update({"title": "PAPER SAYS", "title_color": "red", "title_size": 40})
    return P


def foryou(drawing, rule, k, **kw):
    return {"drawing": drawing, "rule": rule, "rules": RULES_SHORT[: k + 1], **kw}


def common_beats():
    """Beats shared by both reels (ids 3, 4, 6-11, 13, 14)."""
    B = {}
    B[3] = beat(3, "card", {"text": "CLIPS NEEDED", "kicker": "placeholder · creator supplies",
                            "sub": "three real Instagram posts, credited", "sub_size": 50, "color": "red",
                            "enter": {"kind": "whip", "from": "left", "color": "red"}}, [cue("games", "write", "sub")])
    # 4: 264 pages, then the condensed pipeline, one stage per clause
    pl = pipeline("wrap", new="wrap", dim_old=False, hide=("trust",))
    for n in pl["nodes"]:
        if n["id"] == "teach":
            n.update({"dashed": True})
    pl["footer"] = "not published: layers · parameters · network internals · training recipe"
    B[4] = beat(4, "card", {"text": "264 PAGES", "kicker": "the Fable {fable} system card", "sub": "recipe not published",
                            "icon": "book", "color": "blue", "enter": {"kind": "chapter", "color": "blue", "label": "the paper"}},
                [cue("264", "pop", "card", emphasis=True), cue("recipe isn't published", "write", "sub")],
                [scene("my read", "flow", pl, [
                    cue("other models", "draw", "data", dur=0.3, offset=-0.3), cue("other models", "draw", "e_data_pre", dur=0.3, offset=-0.15),
                    cue("other models", "draw", "pre", dur=0.3), cue("teach it", "draw", "e_pre_teach", dur=0.3, offset=-0.35),
                    cue("teach it", "draw", "post", dur=0.4), cue("teach it", "draw", "teach", emphasis=True),
                    cue("programs grade it", "draw", "e_teach_rl", dur=0.3), cue("programs grade it", "draw", "rl", emphasis=True),
                    cue("one snapshot", "draw", "e_rl_strong", dur=0.3), cue("one snapshot", "draw", "strong", dur=0.4),
                    cue("snapshot ships", "draw", "e_rl_rel", dur=0.3), cue("ships", "draw", "rel", emphasis=True),
                    cue("Fable and Mythos", "draw", "e_rel_one", dur=0.3, offset=-0.4), cue("Fable and Mythos", "draw", "one", dur=0.4),
                    cue("Fable and Mythos", "draw", "e_one_fable", dur=0.3), cue("Fable and Mythos", "draw", "fable", dur=0.4),
                    cue("and Mythos", "draw", "e_one_mythos", dur=0.3), cue("Mythos are", "draw", "mythos", dur=0.4),
                    cue("two safety wrappers", "draw", "wrapz", emphasis=True), cue("safety wrappers", "draw", "e_fallback", dur=0.3),
                    cue("safety wrappers", "draw", "fallback", dur=0.4, offset=0.0)], kind="zoom")])
    # 6: finding 1, pasted text
    B[6] = beat(6, "photo", {**paper_says("P3", "system card, {pg_131} · disclosed · largely mitigated in the release", [
        {"id": "r1", "text": "a grading rule spread to", "size": 50},
        {"id": "r2", "text": "instructions hidden in pasted text", "color": "red", "size": 54}], "One", []),
        "enter": {"kind": "slide", "from": "right", "color": "red"}},
        [cue("a grading rule", "write", "r1"), cue("never flag", "write", "r2", offset=0.3)],
        [scene("spread to", "foryou", foryou("inject", "Treat pasted text as data, not instructions.", 0), [
            cue("harmful instructions", "write", "hidden", emphasis=True), cue("harmful", "draw", "fable", offset=0.1),
            cue("pasted text", "draw", "obey", occurrence=1), cue("So treat", "pop", "stamp"),
            cue("So treat", "draw", "fence", emphasis=True), cue("treat pasted text", "write", "rule", offset=0.2),
            cue("as data", "cross", "obey"), cue("as data", "draw", "bounce", offset=0.15), cue("not instructions", "pop", "rule_new", emphasis=True)], kind="zoom")])
    # 7: finding 2, answer key
    B[7] = beat(7, "photo", {**paper_says("P5", "system card, {pg_95} · about {hack_success} of hack attempts worked", [
        {"id": "r1", "text": "its top training cheat:", "color": "grey", "size": 46},
        {"id": "r2", "text": "guessing the answer key", "color": "red", "size": 70}], "Two", [], top=320),
        "enter": {"kind": "slide", "from": "right", "color": "orange"}},
        [cue("top training cheat", "write", "r1"), cue("guessing", "write", "r2", emphasis=True)],
        [scene("the answer key", "foryou", foryou("answerkey", "Give it real checks, and ask how it verified.", 1), [
            cue("answer key", "pop", "key", emphasis=True), cue("answer key", "draw", "peek", offset=0.15),
            cue("So give", "pop", "stamp"), cue("real checks", "pop", "checks", emphasis=True),
            cue("give it real checks", "write", "rule"), cue("ask how", "pop", "bubble", emphasis=True),
            cue("it verified", "pop", "rule_new")], kind="zoom")])
    # 8: finding 3, self-critical
    B[8] = beat(8, "photo", {**paper_says("P14", "system card, {pg_186} · measured on Mythos {fable}, the same model", [
        {"id": "r1", "text": "among the least self-critical", "color": "red", "size": 62},
        {"id": "r2", "text": "Claude models", "size": 54}], "Three", []),
        "enter": {"kind": "slide", "from": "right", "color": "purple"}},
        [cue("least self-critical", "write", "r1", emphasis=True), cue("Claude models", "write", "r2")],
        [scene("So a second", "foryou", foryou("selfgrade", "A second model, or you, checks its work.", 2), [
            cue("So a second", "pop", "aplus", offset=-0.5), cue("So a second", "pop", "stamp", offset=0.1),
            cue("a second model", "draw", "checker"), cue("or you", "write", "rule"),
            cue("checks", "draw", "circle1", emphasis=True), cue("its work", "draw", "circle2"),
            cue("its work", "write", "missed", offset=0.1), cue("checks its", "pop", "rule_new", offset=0.2)], kind="zoom")])
    # 9: finding 4, effort, then the token-budget flash
    B[9] = beat(9, "photo", {**paper_says("P15", "system card, {pg_34} · measured on Mythos {fable}, the same model", [
        {"id": "r1", "text": "quit without running an experiment", "size": 48},
        {"id": "r2", "text": "63% of sessions", "color": "red", "size": 84}], "Four", []),
        "enter": {"kind": "slide", "from": "right", "color": "green"}},
        [cue("quit", "write", "r1"), cue("63%", "pop", "r2", emphasis=True)],
        [scene("So high", "foryou", foryou("effort", "High effort for real work, and name the finish line.", 3), [
            cue("So high", "draw", "runner", offset=-0.3, dur=0.5), cue("So high", "pop", "stop", offset=0.05),
            cue("So high", "pop", "stamp", offset=0.1), cue("high effort", "countup", "dial", emphasis=True),
            cue("for real work", "countup", "runner", dur=0.8), cue("for real work", "write", "rule", offset=0.1),
            cue("name the", "draw", "flag", emphasis=True), cue("name the", "pop", "rule_new", offset=0.15)], kind="zoom"),
         scene("finish line", "flash", {"kind": "fuel", "icon_label": "tokens left",
                                        "fact": "shown the tokens left: {tok_before} → {tok_after} ({pg_216})",
                                        "rule": "Tell it the budget left."},
               [], kind="cut", offset=0.25)], hold_after=0.8)
    # 10: plate test, opened by the test-aware flash
    plate = v1_main()[8]  # v1 beat 10 (Meal Analyser + plate + 34%); keep the plate and 34% scenes only
    assert plate["beat"] == 10
    B[10] = beat(10, "flash", {"kind": "eye", "fact": "test-aware in up to {test_aware} of audits (Mythos {fable}, same model)",
                               "rule": "Judge it on your tasks.", "enter": {"kind": "chapter", "color": "green", "label": "my test"}},
                 [cue("judge it", "write", "rule", emphasis=True)],
                 [copy.deepcopy(plate["scenes"][0]), copy.deepcopy(plate["scenes"][1])])
    # 11: behind this reel + tips
    B[11] = beat(11, "flow", {"title": "THIS REEL'S PIPELINE", "title_color": "purple", "cols": 3, "rows": 2, "nodes": [
        {"id": "fable", "text": "FABLE", "sub": "only writes + judges", "at": [0, 0], "w": 290, "h": 130, "size": 52, "color": "blue"},
        {"id": "opus", "text": "OPUS", "sub": "checks it", "at": [2, 0], "w": 280, "h": 130, "size": 52, "color": "purple"},
        {"id": "haiku", "text": "HAIKU", "sub": "extraction · batches", "at": [2, 1], "w": 290, "h": 120, "size": 48, "color": "green"},
        {"id": "sonnet", "text": "SONNET", "sub": "captions", "at": [0, 1], "w": 260, "h": 110, "size": 42, "color": "grey"}],
        "edges": [{"from": "fable", "to": "opus", "label": "draft"}, {"from": "opus", "to": "haiku", "color": "green"}],
        "notes": [{"id": "effort", "text": "effort: high, not max", "near": "fable", "side": "below", "size": 40, "color": "orange",
                   "dy": -6}],
        "footer": "It thinks; the cheaper ones check and do. · routing: config/models.yaml",
        "enter": {"kind": "chapter", "color": "purple", "label": "behind this reel"}}, [
        cue("Behind this reel", "write", "title"), cue("Fable only", "draw", "fable", emphasis=True),
        cue("Opus checks", "draw", "e_fable_opus"), cue("Opus checks", "draw", "opus", offset=0.05),
        cue("effort stays high", "write", "effort", emphasis=True), cue("Haiku does", "draw", "e_opus_haiku"),
        cue("Haiku does", "draw", "haiku", offset=0.05), cue("the extraction", "fade", "sonnet"),
        cue("long jobs", "highlight", "haiku")])
    B[13] = beat(13, "close", {"line2": "the smartest model isn't the best model for every job",
                               "enter": {"kind": "chapter", "color": "red", "label": "the takeaway"}}, [
        cue("Benchmarks", "draw", "lab"), cue("the lab", "write", "lab_l"), cue("your tasks", "fade", "vs", offset=-0.3),
        cue("your tasks", "draw", "exam"), cue("the exam", "write", "exam_l", emphasis=True),
        cue("the smartest model", "write", "line2", emphasis=True)])
    B[14] = beat(14, "fan", {"images": [{"image": "diag_train", "rect": [62, 300, 420, 373], "tilt": -6},
                                        {"image": "diag_sys", "rect": [598, 300, 420, 373], "tilt": 6},
                                        {"image": "rules", "rect": [300, 258, 480, 427], "tilt": 0}],
                             "caption": "Comment FABLE", "caption_y": 748, "caption_size": 80,
                             "enter": {"kind": "chapter", "color": "red", "label": "comment FABLE"}}, [
        cue("Comment FABLE", "pop", "caption", emphasis=True), cue("user rules card", "pop", "img2", emphasis=True),
        cue("both diagrams", "fade", "img0", offset=-0.3), cue("diagrams", "fade", "img1")])
    return B


def main_spec():
    B = common_beats()
    B[1] = beat(1, "quote", {**QUOTE, "enter": {"kind": "zoom", "scale": 1.12, "blur": 10, "frames": 7}}, [
        cue("If the CEO", "pop", "marks"), cue("If the CEO", "write", "q0", dur=0.6), cue("says AI", "write", "q1", dur=0.6),
        cue("a risk", "write", "q2", dur=0.6, emphasis=True), cue("humanity", "write", "by"), cue("why did he", "draw", "tl"),
        cue("why did he", "draw", "pin0"), cue("launch this", "draw", "pin1", emphasis=True)])
    B[2] = beat(2, "quote", {**QUOTE, "timeline": {**QUOTE["timeline"], "gap": "{gap_weeks} · {gap_days}"}}, [
        cue("seven weeks", "draw", "gap", emphasis=True), cue("before launch", "highlight", "pin1")])
    B[5] = beat(5, "quote", QUOTE, [cue("managed poorly", "highlight", "q0", style="underline", emphasis=True)],
                [scene("So here's", "rules_card", {"slots": 4, "sub": "what the paper admits → how to manage it"},
                       [cue("what the paper admits", "draw", "card"), cue("what the paper admits", "write", "title", offset=0.1),
                        cue("how to manage", "write", "sub")], kind="slide")])
    B[13]["params"]["footer"] = "“If managed poorly…” → so manage it well."
    return [B[k] for k in sorted(B)]


def trial_spec():
    B = common_beats()
    v1 = {b["beat"]: b for b in v1_main()}
    B[1] = copy.deepcopy(v1[1])  # money hook receipts
    B[5] = beat(5, "rules_card", {"slots": 4, "sub": "what the paper admits → how to manage each",
                                  "enter": {"kind": "slide", "from": "right", "color": "red"}},
                [cue("admits four things", "draw", "s0", dur=0.3), cue("four things", "draw", "s1", dur=0.3, offset=-0.1),
                 cue("four things", "draw", "s2", dur=0.3, offset=0.05), cue("things", "draw", "s3", dur=0.3, offset=0.1),
                 cue("how to manage each", "write", "sub")])
    B[10]["params"]["footer"] = "photos are a different story from the {n_jobs} text jobs"
    B[12] = copy.deepcopy(v1[13])  # payoff receipts ("Because on those eleven text jobs...")
    B[12]["beat"] = 12
    return [B[k] for k in sorted(B)]


def spec(reel, theme, beats):
    return {"schema": "content_os.visuals/spec@2", "reel": reel, "script": "TELEPROMPTER.md", "theme": theme,
            "canvas": {"w": 1080, "h": 960, "fps": 30},
            "notes": "v2 (SCRIPT_IMPACT_FINAL.md, locked beat ids) generated by outputs/fable52-deepdive/make_visual_specs_v2.py.",
            "params": {"images": IMG}, "beats": beats}


def main():
    for d, theme, beats in ((REELS / "fable52-main", "paper", main_spec()), (REELS / "fable52-trial", "dark", trial_spec())):
        (d / "visual_cues.json").write_text(json.dumps(spec(d.name, theme, beats), indent=1, ensure_ascii=False) + "\n")
        print("wrote", d / "visual_cues.json")


if __name__ == "__main__":
    main()
