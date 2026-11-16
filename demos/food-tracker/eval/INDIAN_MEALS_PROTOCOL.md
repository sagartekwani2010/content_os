# Weigh-it-yourself protocol: 10 home meals (Indian food)

Nutrition5k is US cafeteria food. Our eval says nothing yet about dal, roti, rice, paneer or sabzi.
This protocol creates a small ground truth for the creator's own meals. Ten meals is a sanity check, not a
benchmark: report every meal individually and do not quote a percentage error with a confidence interval from n=10
as if it were general.

Photos are personal: keep them in `demos/workout-hud/app/media/food/` (gitignored) or outside the repo.
The results CSV holds only numbers and the photo's SHA-256, never the photo.

## Equipment

- [ ] Kitchen scale with 1 g resolution and a tare button. Check it with a known packet (e.g. a sealed 500 g pack) first.
- [ ] One reference object you will put in every photo: a standard credit/ID card (85.6 x 54 mm) or a 1-rupee coin.
- [ ] The packet labels (nutrition per 100 g) for every packaged ingredient you use: atta, dal, rice, paneer, oil/ghee, curd, whey.

## Per meal (10 meals; aim for a mix: 3 dal + rice/roti, 2 paneer, 2 sabzi + roti, 1 rajma/chole, 1 egg/chicken, 1 breakfast)

- [ ] 1. Cooking: weigh raw ingredients that go into the pot, including oil/ghee (weigh the bottle before and after, or measure with a spoon and weigh the spoonful once). Note the recipe in `item_recipe_notes`.
- [ ] 2. Cooked yield: weigh the empty pot, then the pot with the finished dish. Cooked weight = difference. This gives kcal per 100 g of the cooked dish = sum of raw-ingredient kcal / cooked weight x 100.
- [ ] 3. Plate: tare the empty plate, add each item one at a time and write down the grams for each item (`weighed_grams`).
- [ ] 4. Photo: overhead (straight down) from about 40-50 cm, daylight or bright light, reference card beside the plate, nothing covering the food. Optionally a second photo at about 45 degrees (for the improvement experiment).
- [ ] 5. Compute ground truth per item: grams x kcal_per_100g / 100 (and protein). Sources in order of preference: packet label (what you actually bought) > recipe calculation from step 2 > IFCT 2017 raw values (Longvah et al., NIN 2017; per its terms, use for personal reference with acknowledgement, do not bundle its data into the app).
- [ ] 6. Run the estimator on the photo BEFORE looking at your numbers again: `python demos/food-tracker/estimate.py <photo> --mode table` and also `--mode direct`. Copy `log_id`, totals and grams into the CSV.
- [ ] 7. Log the truth into the monitor so the dashboard shows error on real meals:
      `python -c "from monitor.log import append_correction as c; c('<log_id>', kcal=..., protein_g=..., mass_g=..., note='weighed')"` (run from `demos/food-tracker`).
- [ ] 8. Eat. Leftovers: weigh what is left and subtract, if any.

## What to report afterwards

- Per meal: true vs estimated kcal, protein and grams for both modes, with the photo (only if the creator wants to show it).
- Which items were missed (ghee, tadka oil, chutney) and which were mistaken (paneer vs tofu, dal type).
- Whether the US table (FoodData Central) has a sensible row for each item: chapati yes; many sabzis no.
- Do not claim accuracy on Indian food from fewer than about 30-50 meals.
