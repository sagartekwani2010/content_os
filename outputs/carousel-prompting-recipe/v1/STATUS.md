# carousel-prompting-recipe · STATUS (22 Nov 2026, 14:35 IST)

**State:** rendered and packaged, waiting for the creator's review of PREVIEW.html (creator gate, step 8). Nothing posted.
**Post slot:** Mon 23 Nov 2026, 13:00 IST (calendar item 2). Keyword: RECIPE.

## Files
- Text (repo): BRIEF.md, runs/ (verbatim prompts + outputs), drafts/, judge/ (prompts, replies, keys, FACTS.md,
  Opus fact check, POST_JUDGE_EDITS.md), slides.json, CAPTION.txt, PINNED_COMMENT.txt, dm_kit/, ledger.jsonl.
- Media (not in Git): ~/Movies/ContentOS/carousel-prompting-recipe/ → PREVIEW.html, POST/ (10 files), contact_sheet.jpg,
  render/ (+ frames/ first/last of each video), photo/ (cover frame + candidates), dm_kit/recipe_card.jpg, qa.json.
- Render: `.venv/bin/python -m content_os.carousel render outputs/carousel-prompting-recipe` (about 1 min).

## Real run (runs/, claude-fable-5-2, plain system prompt, single turn, each prompt twice)
- "Give me a healthy dinner recipe" → both runs: lemon chicken + quinoa, oven at 220°C (swaps listed at the end).
- Six-line recipe-card prompt → both runs: palak paneer moong dal, ~25-27 min, no oven, grams + minutes, "about 34 g
  per serving" (the AI's estimate, not verified), ends with one question.

## Scores
- Round 1 (blind, 3 drafts): A 6.95 · C 6.35 · B 6.2 (B's "I'm vegetarian" cover = false personal claim, accuracy 2).
- Round 2 (blind, revised A2/B2): A2 7.4 · B2 6.75. Panel prediction for A2: stop 10/16, swipe to end 7, save 6.
- Round 3 (blind, A3 = A2 + round-2 fixes): 7.2. Panel: stop 9/16, end 6, save 5.
- Opus fact check on A3: ok=true, 3 "should" flags (swaps omitted, a paraphrase styled as a quote, DM kit must exist), all fixed.
- Post-judge edits listed in judge/POST_JUDGE_EDITS.md (not re-scored).

## Cover
Frame IMG_3518.MOV @ 979.33 s (workout-analyser talking head, 20 Nov), cropped 800x960. Chosen from ~80 frames
(sheets in photo/cand/): camera-facing, eyes open, mid-smile while explaining, well lit, mic only partly visible.
Rejected: hand-on-chin frames (most of the recording), looking off-camera, mid-blink, the wide-open laugh at 979.67 s.
This frame has not been used as a cover before (the Ep 3 cover used reel footage, not this raw file; not verified
against every past cover).

## QA (done)
- Contact sheet viewed; every still and first/last frame of each video viewed; slides 1, 4, 5, 9 viewed at full size;
  mid-animation frames of slides 2 and 10 viewed.
- Automated layout check (render qa.json): all text ≥ 40 px (page counter exempt, 30 px), nothing within 60 px of the
  edges, nothing in the bottom 180 px, items below the headline/body block, video animations end ≥ 0.8 s before the end. 0 issues.
- Every quote checked by hand against runs/ (verbatim, trimmed with "…", markdown bold removed).
- ffprobe: stills JPEG 1080x1350; videos H.264 yuv420p 1080x1350 30 fps + AAC (silent), 6-8 s.
- DM kit: the filled example in DM_REPLY.txt and RECIPE_CARD_PROMPT.txt matches runs/prompt_recipe_card.txt line for line.
- Tests: tests/carousel (7) pass; full suite 367 passed, 3 failed in tests/pipeline (pre-existing: local ffmpeg has no
  drawtext filter; e2e needs a cut_review approval). No shared code was changed.

## Not checked
- Legibility on a real phone and how Instagram crops the 4:5 cover in the profile grid (3:4).
- Playback of the MP4s inside the Instagram app; upload of 4:4:4 JPEGs (Instagram normally accepts them).
- Nutrition: the 34 g protein figure is the model's claim (shown as such), not verified.
- The work-example lines on slide 9 and in the DM kit are template suggestions, not tested.
- The DM kit has not been sent through Instagram (no Graph API token).
- The silent audio track was checked by ffprobe only (no listening).

## For the creator (gate)
Hook: "You prompt AI like Maa gives recipes". Blind 7.2 (round 3; 7.4 in round 2). Risks: brand guide lists "prompt
hacks and prompt packs" as avoided topics, so the copy frames this as a principle, not a pack; "Maa" framing is warm,
check it reads that way to you; the account name in PREVIEW.html is a placeholder. Decide: keep 10 slides or fold
slide 3 into slide 2 (judge r3 suggestion).

## Readout (to fill)
24 h / 48 h: reach, % non-follower reach, saves, sends, follows, profile visits, RECIPE comments. Compare with the
panel prediction (stop 9-10/16, save 5-6/16).
