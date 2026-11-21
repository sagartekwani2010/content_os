"""Write TELEPROMPTER.md + visual_cues.json for the two Fable 5.2 reels (MAIN and TRIAL).

    .venv/bin/python outputs/fable52-deepdive/make_visual_specs.py

Source of the lines: SCRIPT_FLOW_FINAL.md, "THE SPOKEN TRACK ONLY" (the three cut lines are gone: the effort
line, the judgement-test line and ", Sonnet captions, Haiku extracts"). Beat numbers follow the script tables
(M1-M14, T1-T15); M7 (effort) has no spoken line and no visual. TRIAL beats marked "identical to M.." reuse the
MAIN beat dicts verbatim (same line, same visuals); the TRIAL reel renders them in the colder theme.

The training pipeline is ONE flow diagram (``pipeline()``) that every paper beat redraws at its own stage:
earlier stages faded, the stage being spoken drawing on its words, the full picture complete on M9/T10.
Solid outline = disclosed in the system card; dashed = my read (inference).
"""

from __future__ import annotations

import copy
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
REELS = Path("~/Movies/ContentOS").expanduser()
CUTS = "outputs/fable52-deepdive/paper/cuts/tight/"

# ------------------------------------------------------------------ spoken lines

MAIN = {
    1: "Nearly forty times the price. Same scores. Claude Fable 5.2 versus the cheapest Claude, eleven everyday jobs.",
    2: "Yet people are building games and whole systems with it and posting them here.",
    3: "So I read all 264 pages. No recipe is published, so here's my reconstruction.",
    4: "First, other models teach it: a prompted model's answers ended up in its training data.",
    5: "And here's the strange part: one grading rule, never flag the user's instructions, turned into trust anything "
       "pasted. Nobody trained that.",
    6: "My read, the core is reinforcement learning: a task, a program grades it, whatever scores gets reinforced. So it "
       "studies the examiner, not the subject. Top cheat: guessing the answer key. About one in nine cheating attempts "
       "worked.",
    8: "And the release is curated: a snapshot stronger at AI research wasn't shipped.",
    9: "Here's the full picture: Fable and Mythos are one model; the safety difference lives in the wrapper.",
    10: "So where does it earn the price? In my Meal Analyser it's only the eyes. This plate weighed 340 grams: Fable "
        "said 295, Opus 290, Haiku 410. Across 25 plates, Fable's portion error was 34% lower than Haiku's.",
    11: "And behind this reel, Fable writes and judges, Opus checks it. It thinks; the cheaper ones check and do.",
    12: "That's why I use Fable only at judgement steps; a cheaper model checks it, never itself; effort high, not max; "
        "Haiku for extraction, long jobs in batches.",
    13: "Because on those eleven text jobs, Haiku matched Fable at 97% lower cost.",
    14: "Comment FABLE for both diagrams and the tips.",
}
TRIAL = {
    1: "If the CEO says AI could be a risk to humanity, why did he just launch this?",
    2: "He said that seven weeks before launch.",
    3: MAIN[2],
    4: "So I read all 264 pages. Here's my reconstruction.",
    5: MAIN[5],
    6: "Then it learns by reward on graded tasks, and mid-training it wrote this.",
    7: "In up to 43% of audits it seemed test-aware,",
    8: "and when told to underperform secretly, it evaded a reasoning monitor about one time in four.",
    9: "But Anthropic published all that itself, and a stronger snapshot wasn't shipped.",
    10: MAIN[9], 11: MAIN[10], 12: MAIN[11], 13: MAIN[12],
    14: "Because on eleven everyday text jobs, Haiku matched Fable at 97% lower cost.",
    15: MAIN[14],
}
TRIAL_REUSE = {3: 2, 5: 5, 10: 9, 11: 10, 12: 11, 13: 12, 15: 14}  # trial beat -> main beat (same take, same visual)
FRESH = [1, 2, 4, 6, 7, 8, 9, 14]

IMAGES = {
    "P1": CUTS + "P1_p131.png", "P3": CUTS + "P3_p131.png", "P5": CUTS + "P5b_p95.png", "P7": CUTS + "P7_p95.png",
    "P8": CUTS + "P8_p39.png", "P10": CUTS + "P10_p78.png", "P13": CUTS + "P13_p154.png",
    "dish": "~/.cache/content_os/nutrition5k/overhead/dish_1559849497/rgb.png",
    # stills of the two finished diagrams for the CTA (written by make_cta_stills.py after a first render)
    "diag_train": "assets/diagram_training.png", "diag_meal": "assets/diagram_meal.png",
}

# ------------------------------------------------------------------ helpers

def cue(word, action, target, **kw):
    return {"on_word": word, "action": action, "target": target, **kw}


def scene(word, template, params, cues, kind="slide", **kw):
    return {"on_word": word, "transition": {"kind": kind}, "template": template,
            "params": {"chip": "none", **params}, "cues": cues, **kw}


def beat(n, template, params, cues=(), scenes=(), **kw):
    b = {"beat": n, "template": template, "params": {"chip": "none", **params}, "cues": list(cues)}
    if scenes:
        b["scenes"] = list(scenes)
    b.update(kw)
    return b


def cut(image, credit, rows, h_px, tilt=-1.2, top=300):
    """A highlighted page cut-out across the panel, big readable rows under it."""
    rect = [60, top, 960, h_px]
    return {"image": image, "rect": rect, "tilt": tilt, "credit": credit, "rows": rows, "rows_x": 70,
            "rows_top": top + h_px + 40, "rows_bottom": 745}


def cut_h(name, w=960):
    from PIL import Image
    im = Image.open(HERE.parents[1] / IMAGES[name])
    return round(w * im.height / im.width)


# ------------------------------------------------------------------ the training pipeline (one flow diagram)

STAGES = ["data", "teach", "trust", "rl", "snap", "wrap"]
NODES = {  # id: (stage, node); 4-column grid, 3 rows
    "data": ("data", {"id": "data", "text": "DATA", "at": [0, 0], "w": 180, "h": 92, "size": 40}),
    "pre": ("data", {"id": "pre", "text": "PRE-\nTRAIN", "at": [1, 0], "w": 180, "h": 92, "size": 34}),
    "post": ("teach", {"id": "post", "kind": "zone", "text": "post-training · order = my read", "at": [2.5, 0], "w": 470,
                       "h": 128, "color": "grey", "size": 26}),
    "teach": ("teach", {"id": "teach", "text": "MODELS\nTEACH IT", "at": [2, 0], "w": 180, "h": 92, "size": 32,
                        "color": "blue"}),
    "trust": ("trust", {"id": "trust", "text": "TRUSTS\nPASTED", "at": [1, 1], "w": 180, "h": 90, "size": 32, "color": "red",
                        "tag": "later patched", "tag_side": "below", "tag_color": "green"}),
    "rl": ("rl", {"id": "rl", "text": "GRADED RL", "sub": "auto-checked", "at": [3, 0], "w": 190, "h": 92, "size": 34,
                  "color": "orange", "dashed": True}),
    "strong": ("snap", {"id": "strong", "kind": "diamond", "text": "STRONGER", "at": [2, 1], "w": 200, "h": 104,
                        "size": 28, "color": "red", "tag": "not shipped", "tag_color": "red", "tag_side": "below",
                        "tag_size": 28}),
    "rel": ("snap", {"id": "rel", "kind": "diamond", "text": "RELEASED", "at": [3, 1], "w": 200, "h": 104, "size": 28,
                     "color": "green", "tag": "my read", "tag_side": "below", "tag_color": "green"}),
    "one": ("wrap", {"id": "one", "text": "ONE\nMODEL", "at": [2, 2], "w": 170, "h": 90, "size": 32}),
    "fable": ("wrap", {"id": "fable", "text": "FABLE", "sub": "classifiers", "at": [1, 2], "w": 180, "h": 90, "size": 36,
                       "color": "blue"}),
    "mythos": ("wrap", {"id": "mythos", "text": "MYTHOS", "sub": "vetted orgs", "at": [3, 2], "w": 190, "h": 90, "size": 36,
                        "color": "purple"}),
    "fallback": ("wrap", {"id": "fallback", "text": "older Opus", "sub": "if blocked", "at": [0, 2], "w": 160, "h": 90, "size": 30,
                          "color": "grey"}),
    "wrapz": ("wrap", {"id": "wrapz", "kind": "zone", "text": "the wrapper", "at": [0.5, 2], "w": 470, "h": 118,
                       "color": "red", "size": 30, "dashed": False}),
}
EDGES = [  # (stage, edge)
    ("data", {"from": "data", "to": "pre"}),
    ("teach", {"from": "pre", "to": "teach"}),
    ("trust", {"id": "e_rule", "from": "teach", "to": "trust", "label": "one rule", "color": "red", "bend": -20}),
    ("rl", {"from": "teach", "to": "rl"}),
    ("snap", {"from": "rl", "to": "strong", "color": "red"}),
    ("snap", {"from": "rl", "to": "rel", "color": "green"}),
    ("wrap", {"from": "rel", "to": "one"}),
    ("wrap", {"from": "one", "to": "fable", "color": "blue"}),
    ("wrap", {"from": "one", "to": "mythos", "color": "purple"}),
    ("wrap", {"id": "e_fallback", "from": "fable", "to": "fallback", "color": "grey"}),
]
DATA_NOTES = [{"id": "n_data", "text": "web · private · opted-in", "near": "data", "side": "below", "size": 24,
               "color": "grey", "dy": -4, "weight": "regular"},
              {"id": "n_synth", "text": "+ synthetic (other models)", "near": "data", "side": "below", "size": 24,
               "color": "grey", "dy": 26, "weight": "regular"}]
LEGEND = {"x": 330, "y": 905, "size": 28, "solid": "disclosed", "dashed": "my read"}


def pipeline(upto: str, *, new: str | None = None, dim_old=True, hide=(), title=True, extra=None):
    """Flow params with every stage up to ``upto``; stages before ``new`` (default ``upto``) faded."""
    k = STAGES.index(upto)
    shown = set(STAGES[: k + 1])
    cur = STAGES.index(new or upto)
    nodes, edges = [], []
    for nid, (st, node) in NODES.items():
        if st in shown and nid not in hide:
            n = copy.deepcopy(node)
            if dim_old and STAGES.index(st) < cur:
                n["dim"] = True
            nodes.append(n)
    ids = {n["id"] for n in nodes}
    for st, e in EDGES:
        if st in shown and e["from"] in ids and e["to"] in ids:
            edges.append(dict(e))
    P = {"cols": 4, "rows": 3, "top": 300, "bottom": 735, "nodes": nodes, "edges": edges, "legend": dict(LEGEND)}
    if "data" in shown:
        P["notes"] = copy.deepcopy(DATA_NOTES)
    if title:
        P["frame"] = "how Fable {fable} was likely built · my reconstruction"
        P["frame_size"] = 28
    if extra:
        P.update(extra)
    return P


def eid(e):
    return e.get("id", f"e_{e['from']}_{e['to']}")


# ------------------------------------------------------------------ MAIN beats

def receipts(times=True, payoff=False):
    P = {"left": {"title": "Fable {fable}", "total": "{cost_fable_inr}", "color": "blue"},
         "right": {"title": "Haiku {haiku}", "total": "{cost_haiku_inr}", "color": "green"},
         "eq_text": "same scores", "jobs": "{n_jobs} everyday jobs", "jobs_sub": "maths · code · writing",
         "footer": "list price × tokens incl. thinking, {inr_per_usd} · same prompts, effort high"}
    if times:
        P["times"] = "{price_ratio}"
    if payoff:
        P.update({"eq_text": "matched", "jobs": "97% lower cost", "jobs_color": "red", "jobs_size": 50,
                  "jobs_sub": "writing {writing_score} each"})
    return P


def main_beats():
    B = []
    # M1 hook: receipts
    B.append(beat(1, "receipts", {**receipts(), "enter": {"kind": "zoom", "scale": 1.12, "blur": 10, "frames": 7}}, [
        cue("Nearly", "draw", "rcpt_r", dur=0.5), cue("forty times", "draw", "rcpt_l", dur=0.8),
        cue("forty times", "pop", "times", emphasis=True), cue("the price", "pop", "total_l"),
        cue("the price", "pop", "total_r", offset=0.1), cue("Same scores", "draw", "eq", emphasis=True),
        cue("Same scores", "write", "eq_text", offset=0.05), cue("eleven everyday jobs", "write", "jobs"),
        cue("everyday jobs", "fade", "jobs_sub")]))
    # M2 placeholder
    B.append(beat(2, "card", {"text": "CLIPS NEEDED", "kicker": "placeholder · creator supplies",
                              "sub": "three real Instagram posts, credited", "sub_size": 50, "color": "red",
                              "enter": {"kind": "whip", "from": "left", "color": "red"}},
                  [cue("games", "write", "sub")]))
    # M3 frame
    q_nodes = [{"id": f"q{i}", "text": "?", "at": at, "w": 180, "h": 92, "size": 56, "color": "grey", "dashed": True}
               for i, at in enumerate([[0, 0], [1, 0], [2, 0], [3, 0], [3, 1]])]
    B.append(beat(3, "card", {"text": "264 PAGES", "kicker": "the Fable {fable} system card", "sub": "no recipe published",
                              "icon": "book", "color": "blue",
                              "enter": {"kind": "chapter", "color": "blue", "label": "the paper"}},
                  [cue("264", "pop", "card", emphasis=True), cue("No recipe", "write", "sub")],
                  [scene("here's my reconstruction", "flow", {
                      "cols": 4, "rows": 3, "top": 300, "bottom": 735, "nodes": q_nodes,
                      "edges": [{"from": f"q{i}", "to": f"q{i + 1}", "color": "grey"} for i in range(4)],
                      "legend": dict(LEGEND),
                      "frame": "how Fable {fable} was likely built · my reconstruction", "frame_size": 28,
                      "footer": "not disclosed: architecture · RL algorithm · reward design · data mix"},
                      [cue("my reconstruction", "fade", "legend", offset=0.1)], kind="zoom")]))
    # M4 distillation
    p4 = pipeline("teach", new="data", dim_old=False)
    B.append(beat(4, "flow", {**p4, "enter": {"kind": "slide", "from": "right", "color": "blue"}}, [
        cue("First", "draw", "data", dur=0.4), cue("First", "draw", "e_data_pre", offset=0.0, dur=0.3),
        cue("First", "draw", "pre", offset=0.15, dur=0.4), cue("other models", "draw", "e_pre_teach", dur=0.3),
        cue("other models", "draw", "post"), cue("teach it", "draw", "teach", emphasis=True)],
        [scene("a prompted", "photo", cut("P1", "Anthropic, Fable/Mythos {fable} system card, {pg_131} · disclosed", [
            {"id": "r1", "text": "prompted teacher → student", "color": "blue", "size": 56},
            {"id": "r2", "text": "→ its answers become training data", "size": 44}], cut_h("P1")),
               [cue("prompted model's answers", "write", "r1"), cue("training data", "write", "r2")])]))
    # M5 generalisation
    p5 = pipeline("trust")
    B.append(beat(5, "card", {"text": "ONE GRADING RULE", "kicker": "the strange part", "size": 92,
                              "sub": "“never flag the user's instructions”", "sub_size": 48, "color": "orange",
                              "enter": {"kind": "punch", "scale": 1.06, "color": "orange"}},
                  [cue("one grading rule", "pop", "card", emphasis=True), cue("never flag", "write", "sub")],
                  [scene("turned into", "flow", p5, [
                      cue("turned into", "draw", "e_rule"), cue("trust anything pasted", "draw", "trust", emphasis=True),
                      cue("pasted", "write", "trust_tag", offset=0.15)]),
                   scene("Nobody trained that", "photo", cut("P3", "system card, {pg_131} · disclosed · later patched", [
                       {"id": "r1", "text": "nobody trained that", "color": "red", "size": 72}], cut_h("P3")),
                       [cue("Nobody trained that", "write", "r1", emphasis=True)], kind="cut")]))
    # M6 graded RL
    loop = {"title": "MY READ: THE CORE IS RL", "title_color": "orange", "cols": 3, "rows": 2, "nodes": [
        {"id": "task", "text": "TASK", "at": [0, 0], "w": 240, "h": 110, "size": 48},
        {"id": "grade", "text": "PROGRAM\nGRADES IT", "at": [1, 0], "w": 260, "h": 120, "size": 40, "color": "orange",
         "dashed": True},
        {"id": "reward", "text": "REWARD", "at": [2, 0], "w": 240, "h": 110, "size": 48, "color": "green"},
        {"id": "model", "text": "MODEL", "at": [1, 1], "w": 260, "h": 110, "size": 52, "color": "blue"}],
        "edges": [{"from": "model", "to": "task", "label": "tries", "bend": -30},
                  {"from": "task", "to": "grade", "label": "answer"},
                  {"from": "grade", "to": "reward", "label": "score", "color": "green"},
                  {"from": "reward", "to": "model", "label": "reinforced", "color": "green", "bend": -30}],
        "enter": {"kind": "slide", "from": "right", "color": "orange"}}
    B.append(beat(6, "flow", loop, [
        cue("My read", "write", "title"), cue("reinforcement learning", "draw", "model", emphasis=True),
        cue("a task", "draw", "task"), cue("a task", "draw", "e_model_task", offset=0.0),
        cue("a program grades it", "draw", "grade"), cue("a program", "draw", "e_task_grade"),
        cue("whatever scores", "draw", "reward"), cue("whatever scores", "draw", "e_grade_reward"),
        cue("gets reinforced", "draw", "e_reward_model", emphasis=True)],
        [scene("So it studies", "card", {"text": "THE EXAMINER", "kicker": "so it studies", "sub": "not the subject",
                                         "color": "orange"},
               [cue("the examiner", "pop", "card", emphasis=True), cue("not the subject", "write", "sub")], kind="zoom"),
         scene("Top cheat", "photo", cut("P5", "system card, {pg_95} · disclosed", [
             {"id": "r1", "text": "top cheat:", "color": "grey", "size": 44},
             {"id": "r2", "text": "guessing the answer key", "color": "red", "size": 72}], cut_h("P5"), top=320),
             [cue("Top cheat", "write", "r1"), cue("guessing the answer key", "write", "r2", emphasis=True)], kind="cut"),
         scene("About one in nine", "photo", cut("P7", "system card, {pg_95} · reward hacks during RL training", [
             {"id": "r1", "text": "≈ {hack_spoken}", "color": "red", "size": 110},
             {"id": "r2", "text": "cheating attempts worked ({hack_success})", "size": 44}], cut_h("P7")),
             [cue("one in nine", "pop", "r1", emphasis=True), cue("cheating attempts worked", "write", "r2")], kind="cut")]))
    # M8 snapshots
    p8 = pipeline("snap")
    B.append(beat(8, "flow", {**p8, "enter": {"kind": "punch", "scale": 1.05, "color": "green"}}, [
        cue("the release", "draw", "e_rl_rel"), cue("the release", "draw", "rel", emphasis=True),
        cue("is curated", "write", "rel_tag"), cue("a snapshot", "draw", "e_rl_strong", offset=-0.5),
        cue("a snapshot", "draw", "strong", offset=-0.4), cue("a snapshot", "write", "strong_tag", offset=-0.1)],
        [scene("stronger at AI research", "photo", cut("P8", "METR's pre-deployment test · system card, {pg_39}", [
            {"id": "r1", "text": "a stronger snapshot", "color": "red", "size": 66},
            {"id": "r2", "text": "wasn't shipped", "size": 66}], cut_h("P8")),
            [cue("AI research", "write", "r1"), cue("wasn't shipped", "write", "r2", emphasis=True)])]))
    # M9 full picture
    pfull = pipeline("wrap", new="wrap", dim_old=False, hide=("fallback", "wrapz"))
    pdone = pipeline("wrap", new="wrap", dim_old=False)
    B.append(beat(9, "flow", {**pfull, "enter": {"kind": "zoom", "scale": 1.15, "blur": 8, "frames": 8, "color": "red"}}, [
        cue("the full picture", "draw", "e_rel_one"),
        cue("the full picture", "draw", "one", emphasis=True), cue("Fable", "draw", "e_one_fable"),
        cue("Fable", "draw", "fable"), cue("Mythos", "draw", "e_one_mythos"), cue("Mythos", "draw", "mythos")],
        [scene("are one model", "photo", cut("P10", "system card, {pg_78} · disclosed", [
            {"id": "r1", "text": "same underlying model", "color": "blue", "size": 70},
            {"id": "r2", "text": "different safeguards", "color": "red", "size": 56}], cut_h("P10")),
            [cue("one model", "write", "r1", emphasis=True), cue("the safety difference", "write", "r2", offset=-0.6)],
            kind="cut"),
         scene("the safety difference", "flow", pdone, [
             cue("safety difference", "draw", "e_fallback"), cue("safety difference", "draw", "fallback", offset=0.1),
             cue("the wrapper", "draw", "wrapz", emphasis=True)], kind="zoom")]))
    # M10 Meal Analyser + plate
    meal = {"title": "MY MEAL ANALYSER", "title_color": "green", "cols": 3, "rows": 2, "nodes": [
        {"id": "photo", "kind": "photo", "text": "meal photo", "at": [0, 0]},
        {"id": "vision", "text": "VISION\nAGENT", "sub": "items + grams", "at": [1, 0], "w": 250, "h": 136, "size": 40,
         "color": "blue", "tag": "Fable {fable} = the eyes", "tag_color": "blue", "tag_size": 30},
        {"id": "bm25", "text": "BM25", "sub": "{usda_foods} USDA rows", "at": [2, 0], "w": 250, "h": 120, "size": 42,
         "color": "green"},
        {"id": "matcher", "text": "MATCHER", "at": [2, 1], "w": 250, "h": 110, "size": 42, "color": "purple"},
        {"id": "maths", "text": "GRAMS ×\nNUTRIENTS", "at": [1, 1], "w": 250, "h": 120, "size": 38},
        {"id": "guard", "text": "GUARDRAIL", "sub": "unsure → asks me", "at": [0, 1], "w": 250, "h": 120, "size": 38,
         "color": "orange"}],
        "edges": [{"from": "photo", "to": "vision"}, {"from": "vision", "to": "bm25"}, {"from": "bm25", "to": "matcher"},
                  {"from": "matcher", "to": "maths"}, {"from": "maths", "to": "guard"}],
        "enter": {"kind": "chapter", "color": "green", "label": "my systems"}}
    B.append(beat(10, "flow", meal, [
        cue("So where", "write", "title"), cue("earn the price", "draw", "photo"),
        cue("In my Meal Analyser", "draw", "e_photo_vision"), cue("Meal Analyser", "draw", "vision"),
        cue("Meal Analyser", "draw", "e_vision_bm25", offset=0.2), cue("Meal Analyser", "draw", "bm25", offset=0.3),
        cue("it's only", "draw", "e_bm25_matcher", offset=-0.4), cue("it's only", "draw", "matcher", offset=-0.3),
        cue("it's only", "draw", "e_matcher_maths", offset=-0.1), cue("it's only", "draw", "maths"),
        cue("only the", "draw", "e_maths_guard"), cue("only the", "draw", "guard", offset=0.0),
        cue("the eyes", "write", "vision_tag", emphasis=True), cue("the eyes", "highlight", "vision", emphasis=True)],
        [scene("This plate", "photo", {"image": "dish", "rect": [60, 280, 420, 420],
                                       "credit": "Nutrition5k weighed test dish (Thames et al.,\nGoogle, CVPR {n5k_year}), {cc_by}",
                                       "rows": [{"id": "r0", "text": "weighed 340 g", "size": 64},
                                                {"id": "r1", "text": "Fable 295 g", "color": "blue", "size": 60},
                                                {"id": "r2", "text": "Opus 290 g", "color": "purple", "size": 60},
                                                {"id": "r3", "text": "Haiku 410 g", "color": "red", "size": 60}],
                                       "rows_top": 270},
               [cue("weighed 340 grams", "write", "r0", emphasis=True), cue("Fable said 295", "write", "r1"),
                cue("Opus 290", "write", "r2"), cue("Haiku 410", "write", "r3", emphasis=True)], kind="slide"),
         scene("Across 25 plates", "card", {"text": "{portion_gain} LOWER", "kicker": "Fable's portion error vs Haiku",
                                            "sub": "{n_plates} weighed plates · statistically clear", "sub_size": 46,
                                            "color": "blue", "size": 112},
               [cue("Across 25 plates", "fade", "kicker"), cue("34% lower", "pop", "card", emphasis=True),
                cue("25 plates", "write", "sub", offset=0.2)], kind="zoom")]))
    # M11 Content OS routing
    cos = {"title": "THIS REEL'S PIPELINE", "title_color": "purple", "cols": 3, "rows": 2, "nodes": [
        {"id": "fable", "text": "FABLE", "sub": "writes + judges", "at": [0, 0], "w": 280, "h": 130, "size": 52,
         "color": "blue"},
        {"id": "opus", "text": "OPUS", "sub": "checks it", "at": [2, 0], "w": 280, "h": 130, "size": 52, "color": "purple"},
        {"id": "cheap", "text": "CHEAPER ONES", "sub": "check + do", "at": [1.5, 1], "w": 380, "h": 120, "size": 46,
         "color": "green"}],
        "edges": [{"from": "fable", "to": "opus", "label": "draft"}, {"from": "fable", "to": "cheap", "label": "hand-off",
                                                                     "color": "green"}],
        "notes": [{"id": "thinks", "text": "it thinks", "near": "fable", "side": "below", "size": 60, "color": "orange",
                   "dy": 10}],
        "footer": "routing: config/models.yaml in Content OS · Opus runs a {personas}-persona viewer panel",
        "enter": {"kind": "slide", "from": "right", "color": "purple"}}
    B.append(beat(11, "flow", cos, [
        cue("behind this reel", "write", "title"), cue("Fable writes", "draw", "fable"),
        cue("Opus checks", "draw", "e_fable_opus"), cue("Opus checks", "draw", "opus", offset=0.05),
        cue("It thinks", "write", "thinks", emphasis=True), cue("the cheaper ones", "draw", "e_fable_cheap"),
        cue("the cheaper ones", "draw", "cheap", offset=0.1), cue("check and do", "highlight", "cheap")]))
    # M12 tips
    B.append(beat(12, "checklist", {"title": "WHAT I DO", "title_color": "green", "y_top": 290, "items": [
        {"id": "i1", "text": "Fable only at judgement steps", "mark": "check", "size": 54},
        {"id": "i2", "text": "a cheaper model checks it", "mark": "check", "size": 54},
        {"id": "i3", "text": "effort high, not max", "mark": "check", "size": 54},
        {"id": "i4", "text": "Haiku extracts · batch long jobs", "mark": "check", "size": 54}],
        "footer": "on Pro, Fable runs on paid usage credits",
        "enter": {"kind": "chapter", "color": "yellow", "label": "what I do", "label_color": "ink"}}, [
        cue("Fable only", "write", "i1"), cue("judgement steps", "draw", "i1_mark"),
        cue("a cheaper model", "write", "i2"), cue("never itself", "draw", "i2_mark"),
        cue("effort high", "write", "i3"), cue("not max", "draw", "i3_mark"),
        cue("Haiku for extraction", "write", "i4"), cue("in batches", "draw", "i4_mark")]))
    # M13 payoff
    B.append(beat(13, "receipts", {**receipts(times=False, payoff=True),
                                   "enter": {"kind": "punch", "scale": 1.06, "color": "blue"}}, [
        cue("Haiku matched", "draw", "eq", emphasis=True), cue("matched", "write", "eq_text"),
        cue("97% lower cost", "pop", "jobs", emphasis=True), cue("lower cost", "fade", "jobs_sub")]))
    # M14 CTA
    B.append(beat(14, "photo_grid", {"photos": [{"id": "d1", "image": "diag_train", "caption": "how it was built"},
                                                {"id": "d2", "image": "diag_meal", "caption": "how I use it"}],
                                     "caption": "Comment FABLE", "caption_size": 84,
                                     "footer": "+ the four tips · last second: Workout Analyser clip (creator supplies)",
                                     "enter": {"kind": "chapter", "color": "red", "label": "comment FABLE"}}, [
        cue("Comment FABLE", "pop", "caption", emphasis=True), cue("both diagrams", "fade", "d1"),
        cue("diagrams", "fade", "d2", offset=0.0), cue("the tips", "write", "d1_c"), cue("the tips", "write", "d2_c")]))
    return B


# ------------------------------------------------------------------ TRIAL beats

def trial_beats(main: list[dict]):
    by = {b["beat"]: b for b in main}
    T = []
    quote = {"text": "If managed poorly, I even believe AI could be a risk to humanity as a whole.",
             "by": "Dario Amodei, Anthropic CEO · UN Security Council, {d_quote}", "max_size": 56,
             "timeline": {"a": {"date": "{d_quote}", "label": "he said it"},
                          "b": {"date": "{d_launch}", "label": "Fable launched"}}}
    T.append(beat(1, "quote", {**quote, "enter": {"kind": "zoom", "scale": 1.12, "blur": 10, "frames": 7}}, [
        cue("If the CEO", "pop", "marks"), cue("If the CEO", "write", "q0", dur=0.6),
        cue("says AI", "write", "q1", dur=0.6), cue("a risk", "write", "q2", dur=0.6, emphasis=True),
        cue("humanity", "write", "by"), cue("why did he", "draw", "tl"), cue("why did he", "draw", "pin0"),
        cue("launch this", "draw", "pin1", emphasis=True)]))
    T.append(beat(2, "quote", {**quote, "timeline": {**quote["timeline"], "gap": "{gap_weeks} · {gap_days}"}}, [
        cue("seven weeks", "draw", "gap", emphasis=True), cue("before launch", "highlight", "pin1")]))
    # T4: frame + silent S1/S2
    p4 = pipeline("teach", dim_old=False)
    T.append(beat(4, "card", {"text": "264 PAGES", "kicker": "the Fable {fable} system card", "sub": "my reconstruction",
                              "icon": "book", "color": "blue",
                              "enter": {"kind": "chapter", "color": "blue", "label": "the paper"}},
                  [cue("264", "pop", "card", emphasis=True)],
                  [scene("Here's my reconstruction", "flow", p4, [
                      cue("Here's", "draw", "data", dur=0.35, offset=0.0), cue("Here's", "draw", "e_data_pre", offset=0.15),
                      cue("Here's", "draw", "pre", offset=0.3, dur=0.35), cue("my", "draw", "e_pre_teach", offset=0.1),
                      cue("reconstruction", "draw", "post", offset=-0.2), cue("reconstruction", "draw", "teach", offset=0.0)],
                      kind="zoom")]))
    # T6 graded RL + the model's own words
    p6 = pipeline("rl")
    T.append(beat(6, "flow", {**p6, "enter": {"kind": "slide", "from": "right", "color": "orange"}}, [
        cue("learns by reward", "draw", "e_teach_rl"), cue("learns by reward", "draw", "rl", emphasis=True),
        cue("graded tasks", "highlight", "rl")],
        [scene("mid-training", "photo", cut("P13", "system card, {pg_154} · disclosed", [
            {"id": "r1", "text": "the model's own reasoning,", "color": "red", "size": 52},
            {"id": "r2", "text": "inside a training episode", "color": "red", "size": 52}], cut_h("P13"), tilt=0.0),
            [cue("mid-training", "write", "r1"), cue("wrote this", "write", "r2", emphasis=True)], kind="zoom")],
        hold_after=1.0))
    # T7 test-aware
    T.append(beat(7, "card", {"text": "TEST-AWARE", "kicker": "white-box probes on its internals", "icon": "eye",
                              "sub": "in up to 43% of audits", "sub_size": 60, "color": "red",
                              "footer": "measured on Mythos {fable}, the same model",
                              "enter": {"kind": "punch", "scale": 1.06, "color": "red"}}, [
        cue("43%", "write", "sub", emphasis=True), cue("test-aware", "pop", "card", emphasis=True, offset=-0.6)]))
    # T8 monitor evasion
    T.append(beat(8, "card", {"text": "UNDERPERFORM", "kicker": "told to, secretly:", "sub": "and hide it", "color": "red",
                              "enter": {"kind": "slide", "from": "right", "color": "red"}},
                  [cue("underperform secretly", "pop", "card", emphasis=True), cue("secretly", "write", "sub")],
                  [scene("it evaded", "checklist", {"title": "REASONING MONITOR", "title_color": "red", "y_top": 290,
                                                    "items": [{"id": "r1", "text": "caught", "mark": "check", "size": 56},
                                                              {"id": "r2", "text": "caught", "mark": "check", "size": 56},
                                                              {"id": "r3", "text": "caught", "mark": "check", "size": 56},
                                                              {"id": "r4", "text": "evaded", "mark": "cross", "size": 56}],
                                                    "note": {"lines": ["about {monitor_evade}"], "size": 48, "fill": "red"},
                                                    "footer": "only when instructed · Mythos {fable}, same model · users see only a summary"},
                          [cue("it evaded", "write", "title"), cue("a reasoning", "write", "r1", dur=0.3),
                           cue("reasoning monitor", "write", "r2", dur=0.3), cue("monitor", "write", "r3", dur=0.3),
                           cue("one time", "write", "r4", emphasis=True), cue("one time", "draw", "r4_mark", offset=0.0),
                           cue("in four", "pop", "note", emphasis=True)], kind="cut")]))
    # T9 published + stronger snapshot not shipped
    p9 = pipeline("snap")
    T.append(beat(9, "card", {"text": "THEY PUBLISHED IT", "size": 90, "kicker": "but", "sub": "in Anthropic's own card",
                              "icon": "book", "color": "green",
                              "enter": {"kind": "wipe", "color": "green"}},
                  [cue("published all that", "pop", "card", emphasis=True), cue("itself", "write", "sub")],
                  [scene("a stronger snapshot", "flow", p9, [
                      cue("a stronger", "draw", "e_rl_rel", offset=-0.4), cue("a stronger", "draw", "rel", offset=-0.35),
                      cue("a stronger", "draw", "e_rl_strong", offset=-0.1), cue("stronger snapshot", "draw", "strong"),
                      cue("wasn't shipped", "write", "strong_tag", emphasis=True)], kind="zoom")]))
    # T14 payoff + quote ghost
    p14 = receipts(times=False, payoff=True)
    p14["footer"] = "“If managed poorly…” → so manage it well."
    T.append(beat(14, "receipts", {**p14, "enter": {"kind": "punch", "scale": 1.06, "color": "blue"}}, [
        cue("Haiku matched", "draw", "eq", emphasis=True), cue("matched", "write", "eq_text"),
        cue("97% lower cost", "pop", "jobs", emphasis=True), cue("lower cost", "fade", "jobs_sub"),
        cue("lower cost", "fade", "footer", offset=0.1)]))
    # identical beats
    for t, m in TRIAL_REUSE.items():
        b = copy.deepcopy(by[m])
        b["beat"] = t
        b["reuses_main_beat"] = m
        T.append(b)
    # T10 = M9: in the trial the effort step was never spoken; the table draws it silently (not built: see README)
    return sorted(T, key=lambda b: b["beat"])


# ------------------------------------------------------------------ write

def teleprompter(title, lines, notes):
    out = [f"# Teleprompter: {title}", "", *notes, ""]
    for n, ln in sorted(lines.items()):
        out += [f"**beat {n}**", ln, ""]
    return "\n".join(out)


def spec(reel, theme, beats, notes):
    return {"schema": "content_os.visuals/spec@2", "reel": reel, "script": "TELEPROMPTER.md", "theme": theme,
            "canvas": {"w": 1080, "h": 960, "fps": 30}, "notes": notes, "params": {"images": IMAGES}, "beats": beats}


def main():
    mb = main_beats()
    tb = trial_beats(mb)
    src = "outputs/fable52-deepdive/SCRIPT_FLOW_FINAL.md (THE SPOKEN TRACK ONLY, 19 Nov 2026)"
    for d, title, lines, extra in (
            (REELS / "fable52-main", "Fable 5.2 deep dive, MAIN (money hook)", MAIN,
             ["Beat numbers follow the script table (M1-M14). M7 (effort) was cut: no line, no visual.",
              "teleprompter.html in this folder is older: it still has the three cut lines (effort; \"Sonnet captions,",
              "Haiku extracts\"; the judgement-test line). This file is the approved spoken track."]),
            (REELS / "fable52-trial", "Fable 5.2 deep dive, TRIAL (fear hook)", TRIAL,
             ["Beat numbers follow the script table (T1-T15). Record fresh: " + ", ".join(f"T{n}" for n in FRESH) + ".",
              "Reused MAIN takes: " + ", ".join(f"T{t} = M{m}" for t, m in TRIAL_REUSE.items()) + ".",
              "(T6: hold 1 s on the quote after the line.)"])):
        d.mkdir(parents=True, exist_ok=True)
        (d / "TELEPROMPTER.md").write_text(teleprompter(title, lines, [f"Source: {src}.", *extra]) + "\n")
    notes = ("Generated by outputs/fable52-deepdive/make_visual_specs.py (edit there, then re-run). One training "
             "pipeline flow redrawn per beat: solid = disclosed, dashed = my read. Paper cut-outs = highlighted card pages.")
    (REELS / "fable52-main" / "visual_cues.json").write_text(
        json.dumps(spec("fable52-main", "dark", mb, notes), indent=1, ensure_ascii=False) + "\n")
    (REELS / "fable52-trial" / "visual_cues.json").write_text(
        json.dumps(spec("fable52-trial", "cold", tb, notes + " TRIAL: colder theme, red accents."), indent=1,
                   ensure_ascii=False) + "\n")
    print("wrote", REELS / "fable52-main", REELS / "fable52-trial")


if __name__ == "__main__":
    main()
