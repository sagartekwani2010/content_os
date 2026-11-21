# v5 (locked, ids 1-6, 8-12): CURRENT

- Clips `~/Movies/ContentOS/fable52-{main,trial}/visuals/beat_NN.mp4` (beat_07 deleted; beat_02 = the creator's clip, untouched),
  `visuals/INDEX.md`, `visuals/contact_sheet.png`. Assets: `assets/fable_user_rules.png` (3 rules), `tips_card.png` (MY THREE FABLE
  TIPS, no attribution), `how_i_use_fable.png`. Generator: `make_visual_specs_v5.py` (`--assets` for the cards).
- Recurring HOW I USE FABLE sticky after rules 1-3 (beats 4-6) and at the end of beat 8; full card in beat 9 and in the CTA fan.
  The stickies pop late in their beats (after the rule tick), so they are on screen ~0.5-1 s at the default timing.
- v1-v4 notes below are history.

---

# v4 (locked TELEPROMPTER.md, beats 1-12, 19 Nov evening): CURRENT

- Clips: `~/Movies/ContentOS/fable52-{main,trial}/visuals/beat_01..12.mp4`, listed with their lines in `visuals/INDEX.md`; contact
  sheets `visuals/contact_sheet.png`. CTA assets: `<reel>/assets/fable_user_rules.png` (4 rules, in spoken order) and `tips_card.png`.
- Generator: `make_visual_specs_v3.py` (writes visual_cues.json only; `--assets` renders the two cards). MAIN = paper, TRIAL = dark.
- Timing is proportional (no takes yet); no synthetic previews were built for v4.
- Deviation: beat 6 opens on the WhatsApp-forward drawing (the line starts with the analogy), then the p.131 cut on "A grading
  rule", then the DATA fence. Beats 4, 5 and 7 are paper cut first, then drawing.
- New facts: 14% / 49.3 g / 57.2 g (creator_changes_v3.md), $0.14 vs $0.08 and about ₹5 per plate (computed from RESULTS.md token
  counts at list price; worked in visual_facts.md). Beat 2 is still the CLIPS NEEDED card (coordinator replaces beat_02).
- The v1-v3 notes below are history.

---

# v2 (SCRIPT_IMPACT_FINAL.md, locked beat ids, 19 Nov 18:30): what to review NOW

- Clips: `~/Movies/ContentOS/fable52-main/visuals/beat_NN.mp4` (1-11, 13, 14) and `~/Movies/ContentOS/fable52-trial/visuals/beat_NN.mp4`
  (1, 3-14), each listed with its line in `visuals/INDEX.md`. Contact sheets: `visuals/contact_sheet.png`. Old-numbering clips deleted.
- Timing: default length per line, proportional cue times (no recording yet). Re-time to real takes with
  `python -m content_os.visuals render <reel>` after work/cuts.json exists. Synthetic-voice previews for v2: NOT rebuilt yet
  (`python -m content_os.visuals preview <reel>`, ~5 min each); the preview/ files below are the v1 script.
- Themes: MAIN = paper (light, like Ep 2); TRIAL = dark.
- Spec generator: `outputs/fable52-deepdive/make_visual_specs_v2.py` (writes only visual_cues.json; TELEPROMPTER.md/beats.json are the
  coordinator's locked files). CTA assets: `make_cta_assets_v2.py` -> `<reel>/assets/fable_user_rules.png` (the "Comment FABLE"
  screenshot card), `diagram_training.png`, `diagram_system.png`.
- New page cuts from the PDF (`make_page_cuts.py` -> `paper/cuts/tight/`): P14 p.186 (least self-critical), P15 p.34 (63%),
  P16 p.91 (43%), P17 p.216 (85.6% -> 91.6%). These replace the [PAGE CUT NEEDED] gaps for finding 3 and the 43% flash (the flash
  shows the number with its page; the P16/P17 strips are made but the 1 s flashes are drawn cards, not the strips).
- Findings 1-4 (beats 6-9): PAPER SAYS cut + big line, then a hand-drawn FOR YOU scene (pasted email with a hidden line ->
  Fable obeys, crossed -> DATA fence, bounce; Fable peeking at the ANSWER KEY -> REAL CHECKS sheet + "how did you verify?";
  Fable's self-graded A+ -> second figure circles mistakes; runner stops early at MED -> dial to HIGH, crosses the FINISH LINE flag),
  rule caption, running MY RULES list. Flashes: token fuel gauge (end of beat 9, "Tell it the budget left", 85.6% -> 91.6%) and
  test-aware eye (start of beat 10, "Judge it on your tasks", up to 43%).
- Approximate / to know: the beat-9 flash sits on the last ~1 s; in the edit leave about 1 s after "name the finish line" or it
  is very short. Beat 4 condenses the pipeline (teach is dashed = my read; the "trusts pasted" branch is left out, finding 1
  covers it). Plate beat no longer shows the Meal Analyser flow (the script dropped it). CLIPS NEEDED and the Workout Analyser
  glimpse are still placeholders. Not checked by ear or on a phone.

---

# Fable 5.2 reels: top-half visuals, ready for review (19 Nov 2026)

## Watch these first
| Reel | Synthetic-voice preview (visuals + macOS voice + burned captions) | Contact sheet (one keyframe per beat) |
|---|---|---|
| MAIN (money hook, dark board) | `~/Movies/ContentOS/fable52-main/preview/fable52_main_preview.mp4` | `~/Movies/ContentOS/fable52-main/preview/beats/contact_sheet.png` |
| TRIAL (fear hook, colder board, red accents) | `~/Movies/ContentOS/fable52-trial/preview/fable52_trial_preview.mp4` | `~/Movies/ContentOS/fable52-trial/preview/beats/contact_sheet.png` |

Measured preview lengths are 106.8 s (MAIN) and 99.0 s (TRIAL, including the 1 s hold after T6). The script estimates about 89 s for each, but that assumes your pace at 1.1x; the synthetic voice is slower and plays at 1.0x. Cue sync on the synthetic track: 106 of 107 MAIN cues and 105 of 105 TRIAL cues landed on their exact transcribed word. The one interpolated cue is "Comment FABLE", because whisper misheard "FABLE".

Per-beat clips sit next to each contact sheet (`beat_NN.mp4`). The voice is the macOS "Samantha" voice at 175 wpm, so timings will shift once you record. The visuals re-time themselves to your real takes: `python -m content_os.visuals render <reel>` after the pipeline has made `work/cuts.json`.

## What was built
- `TELEPROMPTER.md` in each reel folder, taken from "THE SPOKEN TRACK ONLY". Beat numbers follow the script tables: MAIN is M1-M14 with M7 (effort) dropped because it has no line; TRIAL is T1-T15. The three cut lines are gone, and so are their visuals: the effort dial, the D7 judgement-test bars, and the Sonnet/Haiku lanes.
- `visual_cues.json` in each reel folder. Both are generated by `outputs/fable52-deepdive/make_visual_specs.py`, so edit that script and re-run it rather than hand-editing the JSON. TRIAL beats marked "identical" reuse the MAIN beat visuals exactly.
- The centrepiece is one `flow` diagram of the training and deployment pipeline. Paper beats redraw it at their own stage: earlier stages stay, and the new stage draws on its words. It is complete on "Here's the full picture" and holds on "wrapper".
  - Stages: data (web, private, opted-in, synthetic from other models) -> pre-train -> post-training zone (models teach it -> graded RL, auto-checked) -> "trusts pasted" side branch (later patched) -> snapshots (STRONGER: not shipped; RELEASED) -> one model -> Fable (classifiers, fallback to an older Opus, inside "the wrapper") / Mythos (vetted orgs).
  - Solid = disclosed. Dashed = my read: the post-training order, the auto-checked RL loop, and "picked" on the release. A legend sits in the bottom strip.
- Paper cut-outs P1, P3, P5, P7, P8, P10 and P13 are shown with the `photo` template as each step is spoken, with large readable text under each one. The highlights were re-cropped tighter into `paper/cuts/tight/` (P5b is just the highlighted phrase).
- Other beats:
  - Hook receipts: ₹22 vs ₹0.60, ≈40×, "same scores", 11 everyday jobs.
  - Big-first cards: 264 PAGES, ONE GRADING RULE, THE EXAMINER, 34% LOWER, TEST-AWARE.
  - The RL loop shown big: task -> program grades it -> reward -> model.
  - Meal Analyser flow, then Nutrition5k dish 1559849497 (weighed 340 g; Fable 295, Opus 290, Haiku 410, checked against the eval run files), then the 34% card.
  - Content OS routing: "it thinks; the cheaper ones check and do".
  - Tips card with four ticks.
  - Payoff receipts with 97% lower cost.
  - CTA "Comment FABLE" showing stills of both diagrams (`assets/diagram_*.png`, regenerated by `make_cta_stills.py`).
- TRIAL only: the Amodei quote card with a 23 Sep -> 9 Nov 2026 timeline ("7 weeks · 47 days"); the model's own words (P13) with a 1 s silent hold in the preview; the test-aware card (up to 43%); monitor evasion (three caught, one evaded, about 1 in 4); "they published it" leading into the snapshot step.

## Placeholders (need you)
- **M2 / T3 "CLIPS NEEDED":** a red placeholder card. Supply three real Instagram posts, with handles credited. Nothing was invented.
- **Workout Analyser glimpse (last ~1 s, both reels):** not built. Your clip and the "Saturday" on-screen line go over it at assembly; the CTA footer marks the spot.

## Not done / approximate (honest list)
- **Dark board is new.** The approved food-tracker look was off-white paper. I added a spec-level `"theme"` (`dark` for MAIN, `cold` for TRIAL). Change one line (`"theme": "paper"`, set in `make_visual_specs.py`) to go back. In `cold`, orange maps to periwinkle, so the RL box is not orange in TRIAL.
- **Paper cut-outs are thin strips.** Card lines are long, so the page text is small at phone size. The large hand-lettered line under each cut-out carries the message. Check this on a phone.
- **Not drawn:**
  - The effort dial (M7 was cut, and in T10 the table says "draws silently"; I left it out).
  - The probe -> classifier -> classifier gate detail (Fable's box just says "classifiers").
  - The rubric-card-to-clipboard morph (a red side branch instead).
  - The page-stack flip in M3 (a "264 PAGES" card instead).
  - The trial's "quote ghosts back" (a footer line instead).
- **T7 / T8 page cuts:** marked [PAGE CUT NEEDED] in the script, and still missing. The numbers come from `arch_facts.md` with a "measured on Mythos 5.2, same model" footer.
- **Sync has not been heard.** Previews are synthetic voice. Check the sync by ear, and check legibility on a phone.

## Engine changes (repo, uncommitted)
- `rough.py`: `set_theme()` (every colour goes through `color()`). Glyph fallback, because Patrick Hand has no ₹ and no hand font has →.
- `palette.py`: `THEMES` (paper, dark, cold).
- `templates.py`:
  - `flow` gains dashed nodes, multi-line text, `tag`, `zone`, `legend`, and `top`/`bottom`.
  - `photo` gains `rows_x`/`rows_top`/`rows_bottom`, `cover` and `tilt`.
  - New `receipts` and `quote` templates.
- `preview.py`: per-beat `hold_after`. `cli.py`: `preview --name`; the default output is now `<reel>/preview`.
- `facts.py`: about 35 fable52 facts sourced from `facts.md`, `creator_inputs.md`, `arch_facts.md`, `results_tonight.md` and the new `visual_facts.md` (page references, the 11% excerpt, and 47 days computed). All quotes are verified by the tests.
- New tests: `tests/visuals/test_themes_templates.py`.
