"""Render the reel visuals (1080x960 PNG, top half of a 9:16 split; key content inside the central 900x800).

Every number is read from eval/results.json, eval/runs/ and eval/sample.json at render time; nothing is typed in by hand
except paper facts (from REFERENCES.md) and the improvement list (from RESULTS.md).
Food photos are Nutrition5k overhead images (Thames et al., CVPR 2021, CC BY 4.0) and carry an attribution line.

  python visuals/make_visuals.py [--out ~/Movies/ContentOS/food-tracker/visuals]
"""
import argparse, json, subprocess
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent.parent
N5K = Path.home() / ".cache/content_os/nutrition5k/overhead"
W, H = 1080, 960
SAFE = (90, 80, 990, 880)
BG, INK, INK2, MUTED, LINE = "#FAFAF7", "#111111", "#45443F", "#7A7973", "#E3E2DC"
BLUE, ORANGE, RED, GREEN = "#2A78D6", "#EB6834", "#D63B3A", "#138A5E"
FONT = "/System/Library/Fonts/HelveticaNeue.ttc"
ATTR = "Photo: Nutrition5k (Google, CVPR 2021), CC BY 4.0"


def f(size, w="regular"):
    return ImageFont.truetype(FONT, size, index={"regular": 0, "bold": 1, "medium": 10, "light": 7}[w])


def canvas():
    im = Image.new("RGB", (W, H), BG)
    return im, ImageDraw.Draw(im)


def text(d, xy, s, size=40, w="regular", fill=INK, anchor="la"):
    d.text(xy, s, font=f(size, w), fill=fill, anchor=anchor)


def wrap(d, s, size, w, maxw):
    words, lines, cur = s.split(), [], ""
    for x in words:
        t = (cur + " " + x).strip()
        if d.textlength(t, font=f(size, w)) <= maxw:
            cur = t
        else:
            lines.append(cur); cur = x
    lines.append(cur)
    return lines


def para(d, xy, s, size=40, w="regular", fill=INK, maxw=900, lh=1.22):
    x, y = xy
    for ln in wrap(d, s, size, w, maxw):
        text(d, (x, y), ln, size, w, fill)
        y += int(size * lh)
    return y


def pill(d, xy, s, size=30, fill=BLUE, fg="white"):
    x, y = xy
    tw = d.textlength(s, font=f(size, "bold"))
    d.rounded_rectangle((x, y, x + tw + 36, y + size + 22), radius=(size + 22) // 2, fill=fill)
    text(d, (x + 18, y + 10), s, size, "bold", fg)
    return x + tw + 36


def photo(d_im, dish, box, crop=None):
    im = Image.open(N5K / dish / "rgb.png").convert("RGB")
    if crop:
        im = im.crop(crop)
    x0, y0, x1, y1 = box
    im.thumbnail((x1 - x0, y1 - y0))
    m = Image.new("L", im.size, 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, *im.size), radius=18, fill=255)
    d_im.paste(im, (x0 + (x1 - x0 - im.size[0]) // 2, y0), m)
    return im.size


def load():
    res = json.load(open(HERE / "eval/results.json"))
    truth = {x["dish_id"]: x for x in json.load(open(HERE / "eval/sample.json"))["dishes"]}
    run = lambda m, mode, dish: json.load(open(HERE / f"eval/runs/{m}/{mode}/{dish}.json"))
    return res, truth, run


# ---------------- cards ----------------

PAPERS = [
    ("01_paper_nutrition5k", "Nutrition5k", "Thames et al. · Google", "CVPR 2021",
     "5,006 real cafeteria plates, each weighed ingredient by ingredient.",
     "We used: their test split as our exam."),
    ("02_paper_im2calories", "Im2Calories", "Myers et al. · Google", "ICCV 2015",
     "Find the food, estimate its size, then look up calories in a nutrition database.",
     "We used: the two-step design."),
    ("03_paper_two_step_mllm", "Decomposing Food Images: a two-step multimodal LLM approach",
     "Khlaisamniang et al.", "CVPR Workshops 2025",
     "Ask the AI to list ingredients and portions first, then work out nutrients.",
     "We used: step 1 for the AI, a USDA table for step 2."),
]


def paper_card(out, name, title, authors, venue, idea, used):
    im, d = canvas()
    x = SAFE[0]
    pill(d, (x, 110), "RESEARCH PAPER", 28, INK2)
    y = para(d, (x, 190), title, 62, "bold", INK, 900, 1.12)
    text(d, (x, y + 14), f"{authors}  ·  {venue}", 40, "regular", INK2)
    d.line((x, y + 90, SAFE[2], y + 90), fill=LINE, width=3)
    y = para(d, (x, y + 120), idea, 44, "regular", INK, 900)
    para(d, (x, y + 30), used, 44, "bold", BLUE, 900)
    im.save(out / f"{name}.png")


def pipeline(out):
    im, d = canvas()
    text(d, (W // 2, 100), "How it estimates a meal", 56, "bold", INK, "ma")
    boxes = [("Photo", "one overhead shot", INK2),
             ("1  AI looks", "names each food\n+ grams (a range)", BLUE),
             ("2  Look it up", "USDA food table\nkcal, protein /100 g", GREEN),
             ("Totals", "grams × per-100 g\n+ confidence", INK2)]
    y = 200
    for k, (h, sub, col) in enumerate(boxes):
        d.rounded_rectangle((150, y, 930, y + 140), radius=24, outline=col, width=5, fill="white")
        text(d, (190, y + 22), h, 46, "bold", col)
        for j, ln in enumerate(sub.split("\n")):
            text(d, (520, y + 26 + j * 46), ln, 38, "regular", INK2)
        if k < 3:
            d.polygon([(530, y + 150), (550, y + 150), (540, y + 172)], fill=MUTED)
            d.line((540, y + 140, 540, y + 160), fill=MUTED, width=5)
        y += 175
    im.save(out / "04_pipeline_two_step.png")


def worked_example(out, truth, run, model, dish="dish_1559844366"):
    t = truth[dish]
    r = run(model, "table", dish)
    im, d = canvas()
    text(d, (SAFE[0], 70), "One real plate, start to finish", 50, "bold")
    photo(im, dish, (SAFE[0], 145, 420, 400), crop=(110, 0, 590, 480))
    text(d, (SAFE[0], 412), ATTR, 20, "regular", MUTED)
    # item rows
    tmap = {i["name"]: i for i in t["ingredients"]}
    alias = {"Almonds": "almonds", "grapes": "grapes", "Broccoli": "broccoli"}
    x0 = 450
    text(d, (x0, 150), "AI sees", 34, "bold", BLUE)
    text(d, (x0 + 330, 150), "table says", 34, "bold", GREEN)
    y = 205
    for it in r["items"]:
        nm = it["name"].split("(")[0].replace("florets", "").replace("Red ", "").strip().split(",")[0]
        text(d, (x0, y), f"{nm[:10]}", 40, "regular")
        text(d, (x0 + 300, y), f"{it['grams_best']:.0f} g", 40, "bold", BLUE, "ra")
        text(d, (SAFE[2], y), f"{it['kcal']:.0f} kcal", 40, "bold", GREEN, "ra")
        y += 62
    d.line((SAFE[0], 470, SAFE[2], 470), fill=LINE, width=3)
    # totals vs truth
    rows = [("Calories", f"{r['totals']['kcal']:.0f} kcal", f"{t['kcal']:.0f} kcal"),
            ("Protein", f"{r['totals']['protein_g']:.1f} g", f"{t['protein_g']:.1f} g"),
            ("Weight", f"{r['totals']['grams']:.0f} g", f"{t['mass_g']:.0f} g")]
    text(d, (440, 500), "AI + table", 38, "bold", BLUE, "ma")
    text(d, (780, 500), "weighed truth", 38, "bold", INK, "ma")
    y = 565
    for lab, a, b in rows:
        text(d, (SAFE[0], y), lab, 46, "regular", INK2)
        text(d, (440, y), a, 52, "bold", BLUE, "ma")
        text(d, (780, y), b, 52, "bold", INK, "ma")
        y += 80
    err = (r["totals"]["kcal"] - t["kcal"]) / t["kcal"] * 100
    text(d, (W // 2, 820), f"Off by {err:+.0f}% on calories. Almonds are {tmap['almonds']['kcal']/t['kcal']*100:.0f}% of them.", 38, "medium", INK2, "ma")
    im.save(out / "05_worked_example.png")


def eval_card(out, res, model):
    c = res["conditions"]
    tb, dr = c[f"{model}/table"], c[f"{model}/direct"]
    im, d = canvas()
    text(d, (SAFE[0], 90), "The exam: 50 weighed plates", 54, "bold")
    text(d, (SAFE[0], 160), "Nutrition5k test set · random sample · seed fixed", 34, "regular", INK2)
    y = 250
    for lab, m, col in [("AI + table lookup", tb, BLUE), ("AI guesses directly", dr, ORANGE)]:
        text(d, (SAFE[0], y), lab, 42, "bold", col)
        text(d, (SAFE[0], y + 60), f"{m['kcal']['MAE']:.0f} kcal", 84, "bold", INK)
        text(d, (SAFE[0] + 400, y + 72), "average miss per plate", 36, "regular", INK2)
        text(d, (SAFE[0] + 400, y + 118), f"95% CI {m['kcal']['MAE_CI'][0]:.0f}–{m['kcal']['MAE_CI'][1]:.0f} · "
             f"{m['kcal']['MAE_pct_of_mean']:.0f}% of avg plate", 34, "regular", INK2)
        y += 230
    pd = res["paired"][f"{model}: table minus direct (kcal abs err)"]
    para(d, (SAFE[0], y + 10), f"Difference: {pd['mean_diff_abs_err']:+.0f} kcal (95% CI {pd['CI'][0]:+.0f} to {pd['CI'][1]:+.0f}). "
         "Not a real difference with 50 plates.", 38, "medium", INK, 900)
    para(d, (SAFE[0], 840), f"Model {model}. For context, Nutrition5k's own trained model: 70.6 kcal on their full test set (Table 3, 2D direct prediction).", 24, "regular", MUTED, 900)
    im.save(out / "06_eval_result_card.png")


def bars(out, res, models):
    c = res["conditions"]
    im, d = canvas()
    text(d, (SAFE[0], 80), "Average calorie miss per plate", 52, "bold")
    text(d, (SAFE[0], 148), "lower is better · whiskers = 95% CI", 34, "regular", INK2)
    groups = []
    for m in models:
        for mode, col, lab in [("table", BLUE, "AI + table"), ("direct", ORANGE, "AI guess")]:
            k = f"{m}/{mode}"
            if k in c:
                groups.append((m.replace("claude-", "").replace("-", " ").title(), lab, col, c[k]["kcal"], c[k]["n"]))
    vmax = max(g[3]["MAE_CI"][1] for g in groups) * 1.1
    x, bw, gap = 200, 150, 40
    base = 800
    sc = lambda v: base - v / vmax * 520
    for k in range(0, int(vmax) + 1, 50):
        d.line((170, sc(k), 990, sc(k)), fill=LINE, width=2)
        text(d, (160, sc(k)), f"{k}", 28, "regular", MUTED, "rm")
    for i, (mn, lab, col, m, n) in enumerate(groups):
        xx = x + i * (bw + gap) + (i // 2) * 40
        d.rounded_rectangle((xx, sc(m["MAE"]), xx + bw, base), radius=8, fill=col)
        d.rectangle((xx, base - 8, xx + bw, base), fill=col)
        cx = xx + bw / 2
        d.line((cx, sc(m["MAE_CI"][0]), cx, sc(m["MAE_CI"][1])), fill=INK, width=4)
        for v in m["MAE_CI"]:
            d.line((cx - 16, sc(v), cx + 16, sc(v)), fill=INK, width=4)
        text(d, (cx, sc(m["MAE_CI"][1]) - 12), f"{m['MAE']:.0f}", 40, "bold", INK, "md")
        text(d, (cx, base + 14), lab, 30, "medium", INK2, "ma")
        if i % 2 == 0:
            text(d, (xx + bw + gap / 2, base + 56), f"{mn} · n={n}", 32, "bold", INK, "ma")
    im.save(out / "07_two_step_vs_direct.png")


def failure(out, idx, dish, title, lines, truth, run, model, note=None):
    t = truth[dish]
    r = run(model, "table", dish)
    im, d = canvas()
    pill(d, (SAFE[0], 70), f"FAILURE {idx}", 28, RED)
    text(d, (SAFE[0], 135), title, 50, "bold")
    photo(im, dish, (SAFE[0], 215, 470, 595), crop=(80, 0, 560, 480))
    text(d, (SAFE[0], 600), ATTR, 20, "regular", MUTED)
    text(d, (500, 225), "Weighed", 34, "bold", INK)
    text(d, (500, 268), f"{t['kcal']:.0f} kcal", 64, "bold", INK)
    text(d, (500, 360), "AI + table", 34, "bold", BLUE)
    text(d, (500, 403), f"{r['totals']['kcal']:.0f} kcal", 64, "bold", BLUE)
    err = (r["totals"]["kcal"] - t["kcal"]) / t["kcal"] * 100
    text(d, (500, 500), f"{err:+.0f}%", 56, "bold", RED)
    y = 650
    for ln in lines:
        y = para(d, (SAFE[0], y), ln, 38, "regular", INK, 900) + 8
    if note:
        text(d, (SAFE[0], 880), note, 24, "regular", MUTED)
    im.save(out / f"{7 + idx:02d}_failure_{idx}.png")


def moment_retest(out, res):
    t = res["test_retest"]
    im, d = canvas()
    pill(d, (SAFE[0], 90), "SAME PHOTO, TWICE", 28, INK2)
    text(d, (SAFE[0], 170), "Ask again, get a", 58, "bold")
    text(d, (SAFE[0], 240), "different answer", 58, "bold")
    text(d, (SAFE[0], 360), f"{t['mean_abs_kcal_diff']:.0f} kcal", 110, "bold", BLUE)
    para(d, (SAFE[0], 500), f"average change when the same {t['n']} photos were run a second time "
         f"(up to {t['max_abs_kcal_diff']:.0f} kcal on one plate).", 40, "regular", INK2, 900)
    im.save(out / "12_moment_same_photo_twice.png")


def moment_portion(out, res, model):
    c = res["conditions"]
    dr = c[f"{model}/direct"]
    im, d = canvas()
    pill(d, (SAFE[0], 90), "WHERE THE ERROR COMES FROM", 28, INK2)
    text(d, (SAFE[0], 170), "Size is the hard part", 58, "bold")
    text(d, (SAFE[0], 290), f"{dr['kcal']['MAE']:.0f}", 120, "bold", ORANGE)
    text(d, (SAFE[0] + 250, 330), "kcal miss as it is", 42, "regular", INK2)
    text(d, (SAFE[0], 460), f"{dr['kcal_if_true_mass_known']['MAE']:.0f}", 120, "bold", BLUE)
    text(d, (SAFE[0] + 250, 500), "if the AI knew the weight", 42, "regular", INK2)
    para(d, (SAFE[0], 650), "Same 50 plates, AI guessing directly. The second number rescales its answer to the "
         "plate's true weight: a lab test, not something the app can do.", 34, "regular", INK2, 900)
    im.save(out / "13_moment_size_is_the_hard_part.png")


def roadmap(out):
    im, d = canvas()
    text(d, (SAFE[0], 80), "What we fix next", 56, "bold")
    items = [("Card in the photo", "fixes portion size: the #1 error"),
             ("Ask one question", "“Anything under the top layer?”"),
             ("Indian food table", "dal, roti, sabzi as cooked at home"),
             ("Learn from my fixes", "my corrections tune my portions"),
             ("Second photo at 45°", "sees height, not just area")]
    y = 180
    for k, (h, s) in enumerate(items, 1):
        d.ellipse((SAFE[0], y, SAFE[0] + 70, y + 70), fill=BLUE)
        text(d, (SAFE[0] + 35, y + 35), str(k), 40, "bold", "white", "mm")
        text(d, (SAFE[0] + 100, y - 2), h, 46, "bold")
        text(d, (SAFE[0] + 100, y + 52), s, 36, "regular", INK2)
        y += 140
    im.save(out / "15_improvements_roadmap.png")


def dashboard(out):
    html = Path.home() / ".cache/content_os/food-tracker/dashboard_with_simulated.html"
    chrome = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
    raw = out / "14_monitoring_dashboard_fullpage.png"
    subprocess.run([chrome, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--window-size=1200,1500",
                    f"--screenshot={raw}", f"file://{html}"], capture_output=True)
    shot = Image.open(raw).convert("RGB").crop((0, 430, 1200, 1290))  # the four chart panels
    im, d = canvas()
    text(d, (SAFE[0], 50), "Monitoring every estimate", 50, "bold")
    text(d, (SAFE[0], 115), "blue = real eval runs · orange = simulated meals", 30, "regular", INK2)
    shot.thumbnail((900, 700))
    im.paste(shot, ((W - shot.size[0]) // 2, 175))
    pill(d, (SAFE[2] - 210, 30), "simulated data", 22, MUTED)
    im.save(out / "14_monitoring_dashboard.png")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(Path.home() / "Movies/ContentOS/food-tracker/visuals"))
    ap.add_argument("--model", default="claude-fable-5-2")
    a = ap.parse_args()
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    res, truth, run = load()
    for p in PAPERS:
        paper_card(out, *p)
    pipeline(out)
    worked_example(out, truth, run, a.model)
    eval_card(out, res, a.model)
    bars(out, res, [a.model] + [m for m in ["claude-opus-5-5"] if f"{m}/table" in res["conditions"]])
    FAIL = json.load(open(HERE / "visuals/failures.json"))
    for k, fc in enumerate(FAIL, 1):
        failure(out, k, fc["dish"], fc["title"], fc["lines"], truth, run, a.model, fc.get("note"))
    moment_retest(out, res)
    moment_portion(out, res, a.model)
    dashboard(out)
    roadmap(out)
    print("\n".join(sorted(str(p) for p in out.glob("*.png"))))


if __name__ == "__main__":
    main()
