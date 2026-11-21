"""The only numbers a visual may draw.

Each fact carries the exact quote it comes from (``source_quote`` must occur verbatim in
``source_file``; the tests check this), so a spec can never introduce a number of its own: templates
take numbers as ``"@key"`` references and labels embed them as ``{key}``. Digits that a label shows
outside those placeholders must be spoken in the beat's line (e.g. "Fable 5.2").
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
RESULTS = "demos/food-tracker/RESULTS.md"
FAILURES = "demos/food-tracker/visuals/failures.json"
REFERENCES = "demos/food-tracker/REFERENCES.md"
SCRIPT = "outputs/food-tracker-reel/SCRIPT.md"
HUD_DAY = "demos/workout-hud/app/day.js"
F52 = "outputs/fable52-deepdive/"
F52_FACTS, F52_CREATOR, F52_ARCH, F52_VIS = (F52 + n for n in ("facts.md", "creator_inputs.md", "arch_facts.md", "visual_facts.md"))


@dataclass(frozen=True)
class Fact:
    value: float | int | tuple
    display: str
    meaning: str
    source_file: str
    source_quote: str


def _f(v, d, m, f, q):
    return Fact(v, d, m, f, q)


FACTS: dict[str, Fact] = {
    "usda_foods": _f(13224, "13,224", "USDA FoodData Central rows the retrieval tool searches", RESULTS, "13,224 USDA FoodData Central rows"),
    "candidates": _f(8, "8", "candidate rows returned per item", RESULTS, "returns 8 candidate rows per item"),
    "n_dishes": _f(50, "50", "Nutrition5k test dishes in the eval (Fable)", RESULTS, "| Fable 5.2, two-step table | 50 |"),
    "fable": _f(5.2, "5.2", "Claude Fable version", RESULTS, "claude-fable-5-2"),
    "table_mae": _f(83.6, "83.6", "kcal MAE, two-agent table pipeline", RESULTS, "**83.6** [59.9, 109.9]"),
    "table_mae_spoken": _f(84, "84", "83.6 as the script says it ('about 84')", SCRIPT, "about 84 calories"),
    "table_ci": _f((59.9, 109.9), "59.9 – 109.9", "95% CI of the table MAE", RESULTS, "**83.6** [59.9, 109.9]"),
    "direct_mae": _f(77.3, "77.3", "kcal MAE, one-prompt direct guess", RESULTS, "**77.3** [55.8, 102.6]"),
    "direct_mae_spoken": _f(77, "77", "77.3 as the script says it", SCRIPT, "calories: 77."),
    "direct_ci": _f((55.8, 102.6), "55.8 – 102.6", "95% CI of the direct MAE", RESULTS, "**77.3** [55.8, 102.6]"),
    "diff_table_direct": _f(6.2, "+6.2", "paired difference table minus direct (kcal)", RESULTS, "**+6.2 kcal [-5.1, +20.3]**"),
    "oracle_direct_mae": _f(45.2, "45.2", "direct MAE if the true mass were known", RESULTS, "45.2 [30.5, 63.1]"),
    "oracle_direct_spoken": _f(45, "45", "45.2 as the script says it", SCRIPT, "from 77 to 45"),
    "oracle_direct_ci": _f((30.5, 63.1), "30.5 – 63.1", "95% CI of the oracle MAE", RESULTS, "45.2 [30.5, 63.1]"),
    "oracle_table_mae": _f(58.1, "58.1", "table MAE if the true mass were known", RESULTS, "58.1 [39.8, 78.9]"),
    "chicken_true_g": _f(194, "194", "grams of chicken hidden under carrots", FAILURES, "194 g of grilled chicken"),
    "chicken_seen_g": _f(35, "35", "grams the model saw", FAILURES, "The AI saw only 35 g"),
    "chicken_conf": _f(0.3, "0.3", "model confidence on that plate", FAILURES, "confidence 0.3"),
    "dish_true_kcal": _f(499, "499", "true kcal of the hidden-chicken dish", RESULTS, "True 499 kcal, estimated 94"),
    "dish_est_kcal": _f(94, "94", "estimated kcal of that dish", RESULTS, "True 499 kcal, estimated 94"),
    "protein_true_g": _f(45, "45", "protein g weighed on that dish", FAILURES, "Protein: 45 g weighed"),
    "protein_est_g": _f(12, "12", "protein g estimated on that dish", FAILURES, "12 g estimated"),
    "flagged": _f(31, "31", "plates flagged by the confidence rule", RESULTS, "flags 31 of 50"),
    "caught": _f(12, "12", "of the worst misses caught by flagging", RESULTS, "catches 12 of the 15 plates"),
    "worst": _f(15, "15", "plates with errors over 40%", RESULTS, "catches 12 of the 15 plates with errors over 40%"),
    "flag_threshold": _f(0.45, "0.45", "confidence threshold of the flag rule", RESULTS, "any item below 0.45"),
    "flagged_err": _f(49, "49%", "mean error on flagged plates", RESULTS, "mean error is 49% on flagged plates vs 22%"),
    "unflagged_err": _f(22, "22%", "mean error on the other plates", RESULTS, "mean error is 49% on flagged plates vs 22%"),
    "range_coverage": _f(68, "68%", "stated kcal range contained the truth", RESULTS, "contained the true value for **68%**"),
    "repeat_change": _f(18.2, "18.2", "kcal change, same photo run twice", RESULTS, "**18.2 kcal [11.4, 25.8]**"),
    "within20": _f(42, "42%", "dishes within 20% (both conditions)", RESULTS, "| 42% |"),
    "oil_share": _f(8.2, "8.2%", "share of true calories from oils/dressings", RESULTS, "8.2% of true calories"),
    "n5k_dishes_spoken": _f(5000, "5,000", "dishes Nutrition5k weighed, as the script says it", SCRIPT,
                            "Nutrition5k weighed five thousand dishes"),
    "n5k_year": _f(2021, "2021", "Nutrition5k paper year (CVPR)", REFERENCES, "CVPR 2021"),
    "cvprw_year": _f(2025, "2025", "two-step multimodal LLM paper year (CVPR Workshops)", REFERENCES, "CVPR Workshops 2025"),
    "im2cal_year": _f(2015, "2015", "Im2Calories paper year (ICCV)", REFERENCES, "ICCV 2015"),
    "paper_n5k_2d": _f(70.6, "70.6", "Nutrition5k paper 2D direct kcal MAE (their trained model)", RESULTS, "2D direct prediction 70.6 kcal"),
    "gpt4o_n5k": _f(82.7, "82.7", "GPT-4o zero-shot kcal MAE on Nutrition5k (Tanabe & Yanai 2025)", RESULTS, "GPT-4o 82.7 kcal"),
    "ci_level": _f(95, "95%", "confidence level of every interval shown", RESULTS, "95% CIs: percentile bootstrap"),
    "cc_by": _f(4.0, "CC BY 4.0", "Nutrition5k licence", REFERENCES, "CC BY 4.0"),
    "meals_day": _f("12 Nov", "12 Nov", "the day the creator's five meal photos are from (Gym Jarvis HUD day)", HUD_DAY,
                    'date: "Thu 12 Nov"'),
    "latency_table": _f(13.7, "13.7 s", "median latency, table pipeline", RESULTS, "| 13.7 s |"),
    # ---- Fable 5.2 deep-dive reels (19 Nov 2026)
    "opus": _f(5.5, "5.5", "Claude Opus version", F52_CREATOR, "Opus 5.5"),
    "haiku": _f(5.5, "5.5", "Claude Haiku version", F52_CREATOR, "Haiku 5.5"),
    "sonnet": _f(5.5, "5.5", "Claude Sonnet version", F52_CREATOR, "Sonnet 5.5"),
    "cost_fable_inr": _f(22, "₹22", "Fable 5.2 cost for the 11 everyday text jobs", F52_CREATOR, "Fable ₹22"),
    "cost_haiku_inr": _f(0.60, "₹0.60", "Haiku 5.5 cost for the same 11 jobs", F52_CREATOR, "Haiku ₹0.60"),
    "price_ratio": _f(40, "≈40×", "Fable vs Haiku cost on those jobs", F52_CREATOR, "(Fable ~40x Haiku)"),
    "inr_per_usd": _f(88, "₹88/$", "exchange rate used for every ₹ cost", F52 + "results_tonight.md", "1 USD = ~₹88"),
    "n_jobs": _f(11, "11", "everyday text jobs in the cost test", F52_CREATOR, "Cost for these 11 tasks"),
    "writing_score": _f((16, 17), "16/17", "writing checklist score, Fable and Haiku", F52_CREATOR,
                        "writing 16/17 for Fable, Opus, Haiku"),
    "plate_weighed": _f(340, "340", "example plate, weighed grams", F52_CREATOR, "weighed 340 g; Fable 5.2 said 295 g"),
    "plate_fable": _f(295, "295", "example plate, Fable 5.2 grams", F52_CREATOR, "Fable 5.2 said 295 g"),
    "plate_opus": _f(290, "290", "example plate, Opus 5.5 grams", F52_CREATOR, "Opus 5.5 290 g"),
    "plate_haiku": _f(410, "410", "example plate, Haiku 5.5 grams", F52_CREATOR, "Haiku 5.5 410 g"),
    "portion_gain": _f(34, "34%", "Fable's portion error lower than Haiku's, 25 plates", F52_CREATOR,
                       "Fable's portion error was 34% lower than Haiku's"),
    "n_plates": _f(25, "25", "weighed Nutrition5k plates in the portion test", F52_CREATOR, "across all 25 weighed plates"),
    "personas": _f(16, "16", "viewer personas in the Opus panel", F52_CREATOR, "a 16-persona viewer panel"),
    "card_pages": _f(264, "264", "pages in the system card", F52_ARCH, "264-PAGE SYSTEM CARD"),
    "fallback_opus": _f(4.8, "4.8", "older Opus that blocked cyber requests fall back to", F52_ARCH, "Opus 4.8 for cyber"),
    "test_aware": _f(43, "43%", "audit transcripts where it seemed eval-aware (up to)", F52_ARCH,
                     "up to 43% of automated audit transcripts"),
    "monitor_evade": _f(0.25, "1 in 4", "told to sandbag secretly, evaded the reasoning monitor", F52_ARCH, "about 1 in 4 times"),
    "d_quote": _f("2026-09-23", "23 Sep 2026", "Amodei at the UN Security Council", F52_FACTS,
                  "23 September: at a special UN Security Council meeting"),
    "d_launch": _f("2026-11-09", "9 Nov 2026", "Fable 5.2 launch", F52_FACTS, "9 November: Fable 5.2 launched."),
    "gap_weeks": _f(7, "7 weeks", "quote to launch", F52_FACTS, "he said it ~7 weeks before"),
    "gap_days": _f(47, "47 days", "quote to launch, exact", F52_VIS, "23 Sep 2026 to 9 Nov 2026: 47 days"),
    "fable_g25": _f(49.3, "49.3", "Fable 5.2 portion error g, same 25 plates", F52 + "creator_changes_v3.md",
                    "Fable 49.3 g vs Opus 57.2 g -> 14% lower"),
    "opus_g25": _f(57.2, "57.2", "Opus 5.5 portion error g, same 25 plates", F52 + "creator_changes_v3.md",
                   "Fable 49.3 g vs Opus 57.2 g -> 14% lower"),
    "portion_vs_opus": _f(14, "14%", "Fable's portion error lower than Opus's (not conclusive)", F52 + "creator_changes_v3.md",
                          "Fable 49.3 g vs Opus 57.2 g -> 14% lower"),
    "plate_cost_fable": _f(0.14, "$0.14", "Fable 5.2 cost per plate at list price", F52_VIS, "about $0.14 per plate"),
    "plate_cost_opus": _f(0.08, "$0.08", "Opus 5.5 cost per plate at list price", F52_VIS, "about $0.08 per plate"),
    "plate_inr_more": _f(5, "₹5", "extra cost per plate, Fable vs Opus", F52_VIS, "about ₹5 more per plate"),
    "max_low_ratio": _f(21, "21x", "FrontierCode cost per task, max vs low effort ($44.70 / $2.10)", F52_VIS, "max cost about 21x low"),
    "n_tips": _f(3, "3", "tips on the tips card", F52_VIS, "The tips card lists 3 tips"),
    "cc_by2": _f(2.0, "CC BY 2.0", "licence of the Dario Amodei photo", F52_VIS, "Licence: CC BY 2.0"),
    "portion_more_acc": _f(14, "14% more accurate", "14% lower portion error than Opus, as the script says it", F52 + "creator_changes_v3.md",
                           "Fable 49.3 g vs Opus 57.2 g -> 14% lower"),
    "research_quit": _f(63, "63%", "open-ended research sessions it quit without an experiment, medium effort", F52_FACTS,
                        "quit open-ended research without running an experiment in 63% of sessions at medium effort"),
    "ctx_out": _f(68, "68%", "long-task set where it ran out of its 1M context", F52_FACTS,
                  "ran out of its 1M context on 68% of ProgramBench tasks"),
    "tok_before": _f(85.6, "85.6%", "score without being shown tokens remaining", F52_FACTS,
                     "showing remaining tokens raised score 85.6% -> 91.6%"),
    "tok_after": _f(91.6, "91.6%", "score when shown tokens remaining", F52_FACTS, "showing remaining tokens raised score 85.6% -> 91.6%"),
    "hack_success": _f(11, "11%", "share of reward-hack attempts that succeeded (card p.95)", F52_VIS,
                       "About 11% of its attempts succeeded"),
    "hack_spoken": _f(1 / 9, "1 in 9", "11% as the script says it", F52_VIS, 'spoken as "about one in nine"'),
    **{f"pg_{n}": _f(n, f"p.{n}", f"system card page {n}", F52_VIS, f"card page {n}") for n in (131, 95, 39, 13, 78, 154, 186, 34, 91, 216, 209)},
}

_PLACE = re.compile(r"\{([a-z0-9_]+)(?::(lo|hi))?\}")


def fact(ref: str) -> Fact:
    key = ref[1:] if ref.startswith("@") else ref
    if key not in FACTS:
        raise KeyError(f"unknown fact {ref!r}")
    return FACTS[key]


def value(ref):
    """``"@key"`` -> the fact's value; anything else is returned unchanged (layout numbers etc.)."""
    if isinstance(ref, str) and ref.startswith("@"):
        return fact(ref).value
    return ref


def fill(text: str) -> str:
    """Replace ``{key}`` (or ``{key:lo}`` / ``{key:hi}`` for intervals) by the fact's display text."""
    def sub(m):
        f = fact(m.group(1))
        if m.group(2):
            lo, hi = f.value
            return f"{lo if m.group(2) == 'lo' else hi}"
        return f.display
    return _PLACE.sub(sub, text)


def bare_numbers(text: str) -> list[str]:
    """Digit groups in ``text`` outside {placeholders} and not glued to letters (Nutrition5k, Im2Calories)."""
    stripped = _PLACE.sub(" ", text)
    return [m.group(0) for m in re.finditer(r"(?<![A-Za-z\d.,])\d[\d,.]*(?![A-Za-z\d])", stripped)
            if m.group(0).rstrip(".,")]


def number_problems(text: str, spoken_line: str) -> list[str]:
    """Numbers drawn but not sourced: not a fact placeholder and not spoken in the line."""
    spoken = {n.rstrip(".,") for n in re.findall(r"\d[\d,.]*", spoken_line)}
    out = []
    for n in bare_numbers(text):
        n = n.rstrip(".,")
        if n not in spoken:
            out.append(n)
    return out


def catalogue() -> str:
    return "\n".join(f"- {k}: {f.display}  ({f.meaning})" for k, f in FACTS.items())


def verify_sources(root: Path = REPO) -> list[str]:
    errs = []
    cache: dict[str, str] = {}
    for k, f in FACTS.items():
        txt = cache.setdefault(f.source_file, (root / f.source_file).read_text())
        if f.source_quote not in txt:
            errs.append(f"{k}: quote {f.source_quote!r} not in {f.source_file}")
    return errs


def load_lunch(log_path: str | Path, log_id: str) -> dict[str, Fact]:
    """Register the creator's lunch estimate (a real logged run of the tracker) as facts.

    Read from the estimates log outside the repo; nothing personal is copied into the repo."""
    p = Path(log_path).expanduser()
    rec = None
    for line in p.read_text().splitlines():
        if log_id in line:
            r = json.loads(line)
            if r.get("id") == log_id and r.get("kind") == "estimate":
                rec = r
    if rec is None:
        raise KeyError(f"estimate {log_id} not in {p}")
    src = f"{p}#{log_id}"
    tot = rec["totals"]
    least = min(rec["items"], key=lambda i: i.get("confidence", 1))
    new = {
        "lunch_kcal": Fact(round(tot["kcal"]), f"{round(tot['kcal'])}", "lunch total kcal (Fable 5.2 estimate)", src,
                           f"kcal {tot['kcal']}"),
        "lunch_lo": Fact(tot["kcal_range"][0], f"{tot['kcal_range'][0]}", "lunch kcal range low", src, "kcal_range"),
        "lunch_hi": Fact(tot["kcal_range"][1], f"{tot['kcal_range'][1]}", "lunch kcal range high", src, "kcal_range"),
        "lunch_protein": Fact(tot["protein_g"], f"{tot['protein_g']}", "lunch protein g", src, "protein_g"),
        "lunch_least_conf": Fact(least["confidence"], f"{least['confidence']}",
                                 f"lowest item confidence on the lunch ({least['name']})", src, least["name"]),
    }
    for k, it in enumerate(rec["items"]):  # per item, in log order: lunch_i0_g, lunch_i0_kcal, lunch_i0_protein
        new[f"lunch_i{k}_g"] = Fact(it["grams"], f"{it['grams']:g}", f"grams: {it['name']}", src, it["name"])
        new[f"lunch_i{k}_kcal"] = Fact(it["kcal"], f"{it['kcal']:g}", f"kcal: {it['name']} ({it.get('fdc')})", src, it["name"])
        new[f"lunch_i{k}_protein"] = Fact(it["protein_g"], f"{it['protein_g']:g}", f"protein g: {it['name']}", src, it["name"])
    FACTS.update(new)
    return new


def load_meals(log_path: str | Path, ids: dict[str, str], flag_below: float | None = None) -> dict[str, Fact]:
    """Register the creator's logged meals (real Meal Analyser runs, Fable 5.2) as facts, read by log id.

    Per meal ``meal_<key>_kcal|lo|hi|protein|conf|flag`` and day totals ``day_meals``, ``day_kcal`` (sum of the
    logged totals, rounded once), ``day_protein``, ``day_flagged`` (meals the guardrail sent for review:
    ``needs_confirmation`` in the log). No accuracy is registered: these meals have no weighed ground truth."""
    p = Path(log_path).expanduser()
    recs = {}
    for line in p.read_text().splitlines():
        if any(i in line for i in ids.values()):
            r = json.loads(line)
            if r.get("kind") == "estimate" and r.get("id") in ids.values():
                recs[r["id"]] = r
    new: dict[str, Fact] = {}
    tot_k = tot_p = 0.0
    flagged = 0
    for key, rid in ids.items():
        if rid not in recs:
            raise KeyError(f"estimate {rid} ({key}) not in {p}")
        r = recs[rid]
        src = f"{p}#{rid}"
        t = r["totals"]
        conf = min(i.get("confidence", 1) for i in r["items"])
        flag = bool(r.get("needs_confirmation"))
        tot_k += t["kcal"]
        tot_p += t["protein_g"]
        flagged += flag
        new.update({
            f"meal_{key}_kcal": Fact(round(t["kcal"]), f"{round(t['kcal']):,}", f"{key}: kcal (Fable 5.2 estimate)", src, "kcal"),
            f"meal_{key}_lo": Fact(t["kcal_range"][0], f"{t['kcal_range'][0]:,}", f"{key}: kcal range low", src, "kcal_range"),
            f"meal_{key}_hi": Fact(t["kcal_range"][1], f"{t['kcal_range'][1]:,}", f"{key}: kcal range high", src, "kcal_range"),
            f"meal_{key}_protein": Fact(t["protein_g"], f"{t['protein_g']:g}", f"{key}: protein g", src, "protein_g"),
            f"meal_{key}_conf": Fact(conf, f"{conf:g}", f"{key}: lowest item confidence", src, "confidence"),
            f"meal_{key}_flag": Fact(flag, "review" if flag else "ok", f"{key}: sent for review", src, "needs_confirmation"),
        })
    src = f"{p}#" + ",".join(ids.values())
    new.update({
        "day_meals": Fact(len(ids), f"{len(ids)}", "meals logged that day", src, "estimate"),
        "day_kcal": Fact(round(tot_k), f"{round(tot_k):,}", "sum of the day's logged kcal", src, "totals.kcal"),
        "day_protein": Fact(round(tot_p), f"{round(tot_p)}", "sum of the day's logged protein g", src, "totals.protein_g"),
        "day_flagged": Fact(flagged, f"{flagged}", "meals sent for review that day", src, "needs_confirmation"),
    })
    FACTS.update(new)
    return new
