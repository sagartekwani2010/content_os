# Food tracker: results

Run on 2026-11-16. Everything below was measured in this directory; raw model outputs are in `eval/runs/`,
metrics in `eval/results.json`, per-dish numbers in `eval/per_dish.csv`. Nothing here was run on the creator's own food yet.

## 1. What was built

`estimate.py` takes one meal photo and returns items (name, grams low/best/high, protein g, kcal, confidence),
totals with ranges, the scale cues used and the stated assumptions. Two conditions:

- **table (two-step)**: (A) a vision call names the foods and estimates grams only, plus a USDA-style description;
  (B) local BM25 search over 13,224 USDA FoodData Central rows (SR Legacy 2018-04 + FNDDS 2021-2023, `data/fdc_compact.csv`)
  returns 8 candidate rows per item; (C) a text-only call picks the best row (or none). kcal and protein = grams x row value.
  The model never states a nutrient value in this condition.
- **direct (baseline)**: one vision call with the same identification rules; the model states kcal and protein itself.
- **table_bm25 (free ablation)**: same step A output, top-1 retrieved row, no step C.

Model calls go through the Claude Code CLI in headless mode on the creator's login (no API key):
`claude -p <prompt> --system-prompt <prompt> --model <model> --output-format json --no-session-persistence --tools Read --allowedTools Read --add-dir <image dir>`
(step C uses `--tools ""`). Each call runs in an empty temporary directory so no project instructions leak in.

Models: **claude-fable-5-2** (primary, all 50 dishes), **claude-opus-5-5** (secondary, first 25 dishes of the same sample).
The CLI prints a warning `unrecognized_model` for claude-fable-5-2 and reports its cost basis as `unknown`; the calls succeed
and `modelUsage` confirms claude-fable-5-2 answered.

### Exact prompts (copied from `estimate.py` at run time)
Step A system prompt (table):

```
You are the vision step of a food-logging pipeline. Use the Read tool to open the image path you are given.
Identify every distinct food item visible, including sauces, dressings, cooking oil or butter you can see
or that the preparation clearly implies, garnishes and drinks. Merge tiny garnishes into one item only if they weigh under 5 g.
For each item estimate the edible mass on the plate in grams as a range (grams_low, grams_high) and a best estimate (grams_best).
Use visual scale cues (plate, bowl, cutlery, hand, packaging) and say which you used. Give a confidence from 0 to 1 that
the item identity AND its grams_best (within +/-25%) are right.
Do NOT estimate calories or protein: a separate step looks those up in the USDA FoodData Central table.
For each item write fdc_query: a description in USDA SR Legacy / FNDDS style, e.g.
"Chicken, broilers or fryers, breast, meat only, cooked, roasted" or "Rice, white, long-grain, regular, cooked" or "Lentils, mature seeds, cooked, boiled".
Reply with ONLY this JSON, no prose:
{"items":[{"name":str,"grams_low":num,"grams_best":num,"grams_high":num,"fdc_query":str,"preparation":str,"confidence":num}],
"scale_cues":str,"assumptions":[str]}
```

Direct baseline system prompt:

```
You are a food-logging assistant. Use the Read tool to open the image path you are given.
Identify every distinct food item visible, including sauces, dressings, cooking oil or butter you can see
or that the preparation clearly implies, garnishes and drinks. Merge tiny garnishes into one item only if they weigh under 5 g.
For each item estimate the edible mass on the plate in grams as a range (grams_low, grams_high) and a best estimate (grams_best).
Use visual scale cues (plate, bowl, cutlery, hand, packaging) and say which you used. Give a confidence from 0 to 1 that
the item identity AND its grams_best (within +/-25%) are right.
Then estimate, yourself, the calories (kcal) and protein (g) of each item at grams_best, and the totals.
Reply with ONLY this JSON, no prose:
{"items":[{"name":str,"grams_low":num,"grams_best":num,"grams_high":num,"kcal":num,"protein_g":num,"preparation":str,"confidence":num}],
"total_kcal":num,"total_protein_g":num,"scale_cues":str,"assumptions":[str]}
```

Step C system prompt (row picking, text only):

```
You match foods to rows of the USDA FoodData Central table. For each item you get its description and
numbered candidate rows (description, kcal and protein per 100 g). Pick the candidate that best matches the food as it
appears on the plate, including preparation (cooked vs raw, fried, with sauce). If no candidate is a reasonable match, use -1.
Reply with ONLY JSON: {"picks":[{"item":int,"candidate":int,"why":str}]}
```

User message in steps A and direct: `Image path: <absolute path>`. Step C user message: the item list with 8 numbered candidate rows each (description, source, kcal and protein per 100 g).

## 2. Eval setup

- **Data**: Nutrition5k (Thames et al., CVPR 2021, CC BY 4.0). Official split file `dish_ids/splits/depth_test_ids.txt`
  (507 test dishes that have overhead RealSense images). 50 dishes sampled with `random.Random(20261116)` after sorting the ids
  (`eval/fetch_nutrition5k.py`, list in `eval/sample.json`). Input: `imagery/realsense_overhead/<dish>/rgb.png` (640x480) only; no depth.
- **Ground truth**: the dataset's dish totals (measured mass; kcal and protein from per-ingredient mass x USDA FNDDS 4.1 values).
  Sample: mean 280 kcal (range 12 to 837), mean 214 g, mean 18.8 g protein.
- **Metrics** (`eval/analyze.py`): MAE; MAPE (mean of per-dish |error| / truth); MAE as % of mean truth (the metric in Nutrition5k Table 3);
  bias (mean signed error); share of dishes within 20%. 95% CIs: percentile bootstrap, 10,000 resamples, seed 0.
  Condition differences use a paired bootstrap on the same dishes.
- Per-dish MAPE is inflated by a few very small dishes (e.g. 12 kcal of fruit), so the median APE is also shown.

## 3. Results

### Calories (n = dishes)

| Condition | n | kcal MAE [95% CI] | MAPE [95% CI] | median APE | MAE % of mean | bias kcal [95% CI] | within 20% |
|---|---|---|---|---|---|---|---|
| Fable 5.2, two-step table | 50 | **83.6** [59.9, 109.9] | 38.8% [26.8, 55.6] | 25.7% | 29.9% | -1.2 [-35.5, 32.9] | 42% |
| Fable 5.2, direct guess | 50 | **77.3** [55.8, 102.6] | 34.2% [25.0, 46.5] | 26.8% | 27.7% | -1.4 [-33.6, 29.0] | 42% |
| Fable 5.2, table, top-1 row (ablation) | 50 | 84.0 [57.7, 116.6] | 47.0% [28.4, 71.4] | 26.2% | 30.1% | +19.7 [-15.2, 60.0] | 36% |
| Opus 5.5, two-step table | 25 | 83.0 [48.6, 125.8] | 44.2% [27.5, 64.0] | 29.4% | 30.8% | +14.1 [-32.8, 69.7] | 40% |
| Opus 5.5, direct guess | 25 | 81.2 [52.4, 115.5] | 44.1% [25.1, 72.5] | 28.8% | 30.2% | +15.6 [-28.6, 61.5] | 32% |

On the same 25 dishes Opus ran on, Fable 5.2 scored 81.2 kcal (table) and 74.4 kcal (direct).

### Protein and mass

| Condition | n | protein MAE g [95% CI] | protein MAPE | mass MAE g [95% CI] | mass MAE % of mean | mass bias g [95% CI] |
|---|---|---|---|---|---|---|
| Fable 5.2, table | 50 | 5.0 [3.2, 7.3] | 34.1% | 46.1 [34.3, 59.7] | 21.6% | +2.6 [-15.6, 21.2] |
| Fable 5.2, direct | 50 | 5.0 [3.0, 7.4] | 32.0% | 40.9 [30.8, 52.6] | 19.1% | +4.4 [-11.7, 19.8] |
| Opus 5.5, table | 25 | 6.1 [3.1, 9.8] | 42.7% | 57.2 [38.7, 81.8] | 27.1% | +28.0 [0.5, 59.3] |
| Opus 5.5, direct | 25 | 6.0 [3.4, 9.3] | 45.5% | 50.4 [31.9, 74.6] | 23.8% | +31.1 [6.5, 60.2] |

### Baseline comparison (paired, same dishes)

- Fable 5.2, table minus direct, kcal absolute error: **+6.2 kcal [-5.1, +20.3]**, n=50. **No measurable difference**; the point estimate slightly favours direct guessing.
- Protein: +0.0 g [-0.9, +1.0]. Mass: +5.2 g [+0.3, +10.7] (the two conditions are separate model calls, so grams differ between them).
- Opus 5.5, table minus direct: +1.8 kcal [-13.1, +17.6], n=25. No difference.
- Step C (model picks the row) vs top-1 retrieval: kcal error -0.5 [-29.1, +21.3] for Fable (no difference); MAPE drops from 47.0% to 38.8% and the
  +19.7 kcal bias disappears, driven by a few bad top-1 rows. Opus: -6.9 [-17.5, +1.7].
- Opus 5.5 vs Fable 5.2 (table, same 25 dishes): +1.7 kcal [-14.5, +20.1]. No difference.

### Where the error comes from (decomposition, uses the label, not deployable)

Rescaling each prediction to the dish's true mass (keeps identification and nutrient density, removes portion error):

| Condition | kcal MAE as run | kcal MAE if true mass were known |
|---|---|---|
| Fable 5.2 direct | 77.3 | 45.2 [30.5, 63.1] |
| Fable 5.2 table | 83.6 | 58.1 [39.8, 78.9] |
| Fable 5.2 table, top-1 row | 84.0 | 71.9 [41.5, 111.1] |
| Opus 5.5 direct | 81.2 | 40.0 [23.7, 59.1] |

Portion size is the largest single source of error. With mass fixed, the table rows are *worse* than the model's own calorie density
(58 vs 45 kcal): table lookups add errors from wrong rows (raw vs cooked, dry vs prepared) that direct guessing avoids.

### Repeatability

The same 20 photos were run twice through the Fable table pipeline. Mean absolute change in the kcal total: **18.2 kcal [11.4, 25.8]**
(median 12.7, max 57.1; 9.0% of the estimate on average); grams changed by 7.7 g on average. Accuracy on the repeat (80.8 kcal MAE, n=20) was in line.

### Ranges and confidence

- The stated kcal range (sum of item lows to highs) contained the true value for **68%** of dishes (Fable table, n=50); Opus 48% (n=25). The ranges are too narrow.
- Model-stated item confidence is weakly related to error: Spearman between the lowest item confidence on a plate and its absolute % error = -0.35 (Fable table, n=50).
  Flagging plates with any item below 0.45 flags 31 of 50 and catches 12 of the 15 plates with errors over 40%; mean error is 49% on flagged plates vs 22% on the rest.
  This is the alert rule in the monitor (threshold 0.5 gives the same split here). It asks for confirmation on most plates, which costs the user effort.

### Context from published work (not a head-to-head: different subsets, image types and models)

- Nutrition5k paper, Table 3 (test set): 2D direct prediction 70.6 kcal / 26.1%, mass 40.4 g / 18.8%, protein 5.5 g / 29.5%; depth as 4th channel 47.6 kcal / 18.8%;
  volume scalar 41.3 kcal / 16.5%; mean-value baseline 150.8 kcal / 60.2%. Their models were trained on Nutrition5k; ours is zero-shot. Their 2D numbers use side-angle video frames; ours use the single overhead RGB image.
- Nutrition5k paper, Sec. 4.6 (10 dishes): people estimating mass from images: 53% average error (16 non-nutritionists), 41% (4 nutritionists).
- Tanabe & Yanai 2025, zero-shot on 506 Nutrition5k test dishes: GPT-4o 82.7 kcal MAE, GPT-4V 80.7 kcal.
- Mu et al. 2025, 505 Nutrition5k images: calorie MAPE GPT-4.1 34.6%, Gemini 2.5 Flash 42.9%.

Our Fable 5.2 numbers (77 to 84 kcal MAE, 27.7 to 29.9% of mean) are in the same range as those published zero-shot LLM results.

## 4. Failure cases (Fable 5.2, table)

Top absolute errors were inspected against the photo and the per-ingredient labels.

1. **Hidden food (occlusion)**: dish_1563389626. True 499 kcal, estimated 94 (-81%). 194 g of grilled chicken lies under shredded carrot; the model saw 35 g of "pale chunks" (confidence 0.3). Protein 45.3 g true vs 12 g estimated. Direct guess: 63 kcal.
2. **Wrong table row**: dish_1563898084. True 419, estimated 723 (+72%). "Chia seed pudding" (80 g) was matched to *dry* chia seeds (486 kcal/100 g), adding 389 kcal; the plate held 11 g of chia (in milk and yogurt). Direct guess 457, so this is the largest table-vs-direct gap in the sample (266 kcal).
3. **Calorie-dense food, small gram miss**: dish_1559844272. 80 g almonds = 462 kcal; model saw 60 g, estimated 347 (-25%). A 20 g miss cost 115 kcal.
4. **Likely label error**: dish_1562009934. Label: quinoa, brown rice, greens, goat cheese, olive oil (435 kcal, 12.7 g protein), no meat. The photo shows what looks like two pieces of roast chicken; the model added 140 g chicken (335 kcal) and estimated 678 kcal, 46 g protein. Our reading of the photo, not confirmed with the dataset authors. A similar photo/label mismatch appears in dish_1568305257 (photo shows greens; label lists cucumber, radish, peppers).
5. **Big plate under-estimated / extra items invented**: dish_1568305257 (837 true, 574 est.: eggs 276 g true vs 185 g est., 82 g turkey bacon vs 48 g) and dish_1560975601 (234 true, 576 est.: 10 items listed, broccoli counted twice, 485 g estimated vs 253 g true).

**Oil**: in this sample, oils, butter and dressings are 8.2% of true calories (1,144 kcal over 25 dishes that contain them). The model's oil and dressing items add up to 1,422 kcal,
so on Nutrition5k it *over*-counts added fat in aggregate. Under-counted oil is not a measured failure mode here (one exception: dish_1568305257, 12 g oil true vs 6 g est.).
Indian home cooking uses more oil and ghee; that is untested.

## 5. Cost and latency per image

| Condition | calls/image | median latency | p90 latency | CLI-reported cost/image (median) | tokens in / out per image |
|---|---|---|---|---|---|
| Fable 5.2 table | 2 | 13.7 s | 19.6 s | $0.081 | 12,180 / 1,041 |
| Fable 5.2 direct | 1 | 9.1 s | 11.7 s | $0.054 | 8,783 / 720 |
| Opus 5.5 table | 2 | 17.2 s | (outliers) | $0.095 | 14,066 / 1,228 |
| Opus 5.5 direct | 1 | 13.7 s | (outliers) | $0.062 | 11,301 / 1,116 |

- Cost is the CLI's `total_cost_usd`. For Opus 5.5 the basis is `list` (API list-price equivalent); for Fable 5.2 the CLI says `unknown`, so treat the Fable dollar figures as indicative only.
  The calls ran on the Claude Code subscription login, so these are not amounts billed. Total CLI-reported for all 170 eval estimates: about $12.5 (plus about $0.6 of smoke tests).
- Latency includes CLI start-up. 11 runs took 430 to 3,403 s; all happened while the Opus run and the repeat run were going in parallel (7 concurrent CLI calls). Cause not diagnosed (likely queueing or rate limiting); the medians above are the representative numbers. The first Fable run (4 concurrent) had no run over 26 s.

## 6. Monitoring

- `monitor/log.py`: every estimate is appended to `~/.cache/content_os/food-tracker/estimates.jsonl` (outside the repo): timestamp, source (eval or real), model, mode,
  image SHA-256 (never the image), latency, CLI cost, tokens, per-item grams/kcal/protein/confidence/table row, totals, alerts. Ground truth and user corrections
  are separate records linked by tag or estimate id (`python -m monitor.correct <id> --kcal ...`).
- Alert rule (`monitor/log.alerts`): ask the user to confirm if total kcal is outside 30 to 1,800, any item confidence is below 0.5, a table match is weak, or the kcal range is wider than 80% of the estimate.
- `monitor/dashboard.py` renders one self-contained HTML file: estimates over time, latency vs cost, confidence histogram, estimate vs truth with MAE table, alert queue.
- `monitor/simulate_usage.py` writes a **simulated** 18-day usage log (52 meals, 13 corrections, seed 7) to a separate file, every record `"simulated": true`.
  Latency, cost and confidence values are resampled from the real eval runs; meals are built from `data/indian_reference.csv`. The dashboard shows a "simulated usage data" tag and labels those points "simulated meal". **The simulated meals are not real usage.**

## 7. Improvements, ranked by the measured failures

| # | Change | Failure it targets | Expected effect | How we would measure it |
|---|---|---|---|---|
| 1 | Reference object (card or coin) in every photo, passed to step A as the scale | Portion error, the biggest share (77 to 45 kcal if mass were known) | Up to roughly 40% lower kcal MAE if portion error were removed entirely; a card will do less | A/B on the same weighed meals, with and without card; mass MAE and kcal MAE with paired CIs |
| 2 | One clarifying question when an item is low-confidence ("anything under the carrots?", "how much oil/ghee?") | Occlusion (failure 1), added fat in Indian cooking | Fixes the largest single misses | Error on flagged plates before and after the answer |
| 3 | Better table rows: prefer prepared/cooked rows, block dry ingredients for prepared dishes, add a cooked Indian dish table (needs a licence for IFCT-derived data) | Wrong row (failure 2); US-only table | Bring the table condition at least level with direct (now 58 vs 45 kcal at fixed mass) | The fixed-mass decomposition above, on Nutrition5k and on Indian meals |
| 4 | Per-user portion priors from corrections (e.g. "my katori is 180 g") | Repeated portion bias on the creator's own dishes | Lower bias on repeat meals | Bias and MAE on the creator's meals over weeks, with the logged corrections |
| 5 | Second photo at about 45 degrees | Height and depth of piles (failure 5) | Better volume; Dehais et al. 2017 report under 10% volume error from two views | Mass MAE with one vs two photos |
| 6 | Calibrate the ranges (widen them until they contain the truth about 80% of the time) | Ranges cover the truth only 68% of the time | Honest uncertainty | Coverage on a held-out set |

## 8. Indian food

- Not evaluated yet. No weighed Indian meals exist. `eval/INDIAN_MEALS_PROTOCOL.md` and `eval/indian_meals_template.csv` define a 10-meal weigh-it-yourself protocol.
- `data/indian_reference.csv` holds per-100 g kcal and protein for 21 common items with a source and URL per row (USDA FDC SR Legacy / FNDDS, and INDB values cited with attribution).
  Sources disagree a lot: dal is 145 kcal/100 g in FNDDS but 50 to 62 in INDB home recipes; roti is 297 (USDA, commercial) vs 202 (INDB, homemade).
- `eval/indian_reference_eval.py` will compare the estimator on the creator's own photos against a **reference estimate (portion assumed), not weighed**. It has not been run: the photos were not on this machine when this was written.

## 9. What is NOT shown

- No accuracy on Indian food, home cooking, or the creator's meals. Nutrition5k is US cafeteria food photographed from directly above in a fixed rig.
- No real-world usage: the monitoring time series beyond the eval runs is simulated.
- Not a significant difference between the two-step table and direct guessing: we **cannot** say the table makes it more accurate. Its measured benefit is traceability (each number points to a USDA row), not accuracy.
- n=50 (Fable) and n=25 (Opus) dishes; CIs are wide (about +/-25 kcal on the MAE).
- Ground truth has errors: at least two sampled dishes appear not to match their labels.
- Fable 5.2 dollar costs are CLI estimates with an unknown basis.
- Not medical or nutrition advice.

## How to reproduce

```
.venv/bin/pip install -r demos/food-tracker/requirements.txt
.venv/bin/python demos/food-tracker/tools/build_table.py            # USDA table (downloads to ~/.cache/content_os/fdc)
.venv/bin/python demos/food-tracker/eval/fetch_nutrition5k.py --n 50  # sample + images to ~/.cache/content_os/nutrition5k
.venv/bin/python demos/food-tracker/eval/run_eval.py --model claude-fable-5-2 --n 50 --workers 4
.venv/bin/python demos/food-tracker/eval/run_eval.py --model claude-opus-5-5 --n 25 --workers 4
.venv/bin/python demos/food-tracker/eval/run_eval.py --model claude-fable-5-2 --modes table --n 20 --suffix _repeat --workers 3
.venv/bin/python demos/food-tracker/eval/analyze.py
.venv/bin/python demos/food-tracker/monitor/simulate_usage.py
.venv/bin/python demos/food-tracker/monitor/dashboard.py --logs ~/.cache/content_os/food-tracker/estimates.jsonl ~/.cache/content_os/food-tracker/simulated_usage.jsonl --theme light --out ~/.cache/content_os/food-tracker/dashboard_with_simulated.html
.venv/bin/python demos/food-tracker/visuals/make_visuals.py         # PNGs to ~/Movies/ContentOS/food-tracker/visuals
```
One photo: `.venv/bin/python demos/food-tracker/estimate.py meal.jpg --mode table`.
