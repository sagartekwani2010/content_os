# content_os.visuals: status (16 Nov 2026, 18:58 IST)

## Done
- Hand-drawn, word-anchored beat visuals, built from a spec: skia frames piped to ffmpeg (H.264, 1080x960, 30 fps, BT.709).
- Spec: `outputs/food-tracker-reel/visual_cues.json` (`content_os.visuals/spec@2`).
  - Beat lines are read from `TELEPROMPTER.md`.
  - Each beat has one template, its params, and word-anchored cues.
- 10 templates in `templates.py`: flow, table_search, bars, ticker, photo, line_chart, checklist, gauge, paper, versus.
  - Motion is calm, per the creator: lines and arrows draw on, bars grow, numbers tick, everything else writes or fades in. No decorative effects.
- Brighter palette per the creator. Every colour, the outline weight, hatch strength and how faded past steps are live in `palette.py` (one place to tune).
- Numbers come only from `facts.py`. Each fact's quote is checked against RESULTS.md, failures.json, REFERENCES.md or SCRIPT.md.
  - Lunch facts are read from `~/.cache/content_os/food-tracker/estimates.jsonl`, id `63e6ca37729b`.
- `draft-spec` drafts the spec with claude-fable-5-2 through `claude -p`, then validates and repairs it. Tested once for real on beats 8 and 12 ($0.13).
- Pipeline: set `cue_sheet.json` → `"visual_clips": "work/visuals"`. The final render refuses clips rendered for other cuts.
- Tests: `tests/visuals` (39). The full suite passes (307).
- Fonts (Kalam and Patrick Hand, SIL OFL) are in `~/.cache/content_os/fonts`. Run `python -m content_os.visuals setup` if they are missing.

## Script v7 (19 one-sentence beats): hand-polished spec, rendered
- `visual_cues.json` is hand-polished from the Fable draft. The draft is kept at `visual_cues.draft.json`.
- The voice carries the story and the diagram carries the detail:
  - Beat 7: the lunch items with their grams, from the estimate log.
  - Beat 9: real USDA rows.
  - Beat 10: item, then its USDA row, then kcal and protein.
  - Beat 13: breakfast, lunch and dinner photos.
  - Beats 15 and 16: the chicken circled where it actually shows under the carrots.
- The "653 kcal" chip shows on the beats with the lunch plate (1, 2, 13).
- New templates: table, papers, photo_grid. Flow takes a `cols` setting.
- Countup rule: every counted number lands on its final value at least 0.6 s before the cut. If there is no room, the final value is shown at once. A test checks the last frames.
- Preview: `~/Movies/ContentOS/food-tracker/preview/food_tracker_preview.mp4` (69 s, synthetic voice).
  - Contact sheet: `~/Movies/ContentOS/food-tracker/preview/beats/contact_sheet.png`. Checked by eye: legible.
- Flag for the creator: beats 13 and 14 say it was "tested on many meals I had" with "reasonable accuracy across all kinds of food".
  - RESULTS.md has no accuracy measured on the creator's meals or on Indian food.
  - Beat 14 therefore shows the measured lab result (≈84 kcal per plate on 50 weighed Nutrition5k dishes) with its source line, not an accuracy on his meals.

## Next
1. If the script changes again, draft and check the spec:
   `.venv/bin/python -m content_os.visuals draft-spec outputs/food-tracker-reel --write`
   `.venv/bin/python -m content_os.visuals check outputs/food-tracker-reel`
   - Place the photo annotations (x and y as fractions of the photo) by hand; the model can't see the photos.
2. Render the preview again (about 1–2 min):
   `.venv/bin/python -m content_os.visuals preview outputs/food-tracker-reel`
   - Look at the contact sheet.
3. After the shoot, render the real clips:
   `python -m content_os.pipeline run <reel> --until cutpoints`
   `python -m content_os.visuals render <reel>`
   - Add `visual_clips` to the cue sheet, then run the pipeline render.

## Not verified
- Sync by ear.
- A real pipeline render with clips.
- Legibility on an actual phone.
- Whisper heard "Claude skill" as "clotheskill" (that cue was interpolated).

## Beats 1-2: clips from the Gym Jarvis reel (added 16 Nov, 19:10)

- `~/Movies/ContentOS/food-tracker/visuals/beat01_gym_jarvis_intro.mp4`: main reel 4.4-8.0 s
  (system loading, MEAL SCAN ONLINE, "MEET MY GYM JARVIS"), crop y=520, no audio.
- `~/Movies/ContentOS/food-tracker/visuals/beat02_food_agent_circle.mp4`: main reel 8.0-12.0 s
  (meal HUD), crop y=485, hand-drawn orange circle drawn on at 0.5 s, "food agent" label and
  "from my last video · demo data" note. Generator: `make_intro_clips.py` in the same folder.
- At final assembly, set beats 1 and 2 in visual_cues.json / cue_sheet.json to these clips
  (`{"type": "clip"}` / `{"type": "video", "fit": "cover"}`), trimmed to each beat's length.

## Standing policy (creator, 17 Nov), encoded in the engine

- **Land early.** Every element appears on, or 0.2-0.3 s before, the word that names it: `cues.DEFAULT_OFFSET`
  is -0.25 s. A beat's main visual is on screen from its first frame (no appear cue = visible from frame 0).
- **Big first, then detail.** When a concept is named, show it large and alone (template `card`), then switch to
  the detailed diagram.
- **Several scenes per beat.** `"scenes": [{"on_word", "transition": {"kind": "slide|zoom|wipe|cut"}, "template",
  "params", "cues"}]` on a beat: each scene takes over the panel on its word, with a 6-8 frame in-beat transition
  (`render.SceneTransition`). Scene 0 is the beat's own template/params/cues.
- **Results are dashboards:** KPI tiles plus one chart (`meals`, `monitor`).
- **No more than about 2 s without a new visual event** (checked by eye from the resolved cue times).
- Entrances: `params.enter` (slide, whip, zoom, punch, wipe, chapter) over a beat's first frames; section changes
  (0, 3, 6, 11, 13, 17, 19) use chapter cards.

## v9 (17 Nov)

- Cold open beat 0 replays beat 16 (`"line_from": 16`; cuts.json segment `source_beat` 16).
- Beat 14: the creator's own day (five logged meals, 12 Nov), facts `meal_*` / `day_*` read from
  `estimates.jsonl` by id (`facts.load_meals`). No accuracy numbers: these meals have no weighed truth.
  The day total is the sum of the logged totals (2,217.2 → 2,217 kcal); summing the rounded per-meal values gives 2,218.
- Beats 7 and 9: big agent card, then the detailed scene. Beat 17: plate + "?", then the confidence meter.
  Beat 18: monitoring log (simulated, tagged) with a "my review" tray.
