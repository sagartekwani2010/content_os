# carousel-prompting-recipe · STATUS v2 (22 Nov 2026, 15:15 IST)

**State:** v2 rendered and packaged; waiting for the creator's review of PREVIEW.html. Nothing posted, nothing committed.
**Slot:** Mon 23 Nov 2026, 13:00 IST. **Keyword:** TRAINER. v1 (family recipe) is archived in `v1/` and
`~/Movies/ContentOS/carousel-prompting-recipe/v1/`.

## Concept
"Your AI trainer met you 10 seconds ago": you = the gym member who briefs; AI = a brilliant new trainer who only
knows what you tell him. 8 techniques, one per slide, each = gym line + copy-ready line + real lazy ask -> sharp ask.
Slides: 1 cover (gym photo), 2 casting, 3-10 techniques (who you are, format, limits, ask first, don't guess,
examples, check-in, show the maths), 11 cheat sheet (save), 12 CTA TRAINER. Videos: 3, 4, 6, 9, 12.

## Files
- Repo text: brainstorm/ (open_round/ = pre-gym round, gym_*), runs/ (tasks.json, g*.md = the runs used, pilot/ = first
  pilot), drafts/ (v2_A, v2_B, v2_B2), judge/ (FACTS.md, RUNS_DIGEST.md, v2_round1_*, POST_JUDGE_EDITS.md),
  build/make_slides.py, slides.json, CAPTION.txt, PINNED_COMMENT.txt, dm_kit/, ledger.jsonl.
- Media: ~/Movies/ContentOS/carousel-prompting-recipe/ PREVIEW.html, POST/ (12), contact_sheet.jpg, render/ (+frames),
  photo/cover_gym.jpg (cover, single path `cover_photo` in slides.json), dm_kit/cheat_sheet.jpg, qa.json.
- Render: `.venv/bin/python outputs/carousel-prompting-recipe/build/make_slides.py && .venv/bin/python -m content_os.carousel render outputs/carousel-prompting-recipe`

## Real runs (claude-fable-5-2, each lazy and sharp ask twice; personas and 2nd-step replies are scripted tests)
1 Who you are: generic deficit diet (eggs, chicken, fish) -> canteen lunch, 5 pm snack, 9:30 pm dinner.
2 Format: 344 / 415-word deadlift guide -> 5 bullets (36 / 33 words).
3 Limits: chicken and paneer bowl -> one-pot soya + moong dal khichdi (~Rs 60-70, AI's estimate).
4 Ask first: barbell gym split -> 3 questions, then a dumbbell plan with "Box squat to a chair (pain-free depth only)".
5 Don't guess: "Start at about 2,000 kcal… assuming…" -> "Calories: [ASK ME]".
6 Examples: generic names -> names copying the examples' tone and time stamp (moderate; said on the slide).
7 Check-in: fixed 12-week table -> weeks 1-2, check-in, "rest until the shin is pain-free" for week 3.
8 Show the maths: stated total doesn't match its own meals (105 g vs 109 g) -> per-item list whose totals add up.

## Scores
- Brainstorm judge (gym framings, blind Fable): F1 new trainer 8.4 · F4 online coach 8.2 · F5 floor trainer 7.6 ·
  F2 you're the coach 5.8 · F3 spotter 4.0. Earlier open round (before the gym rule): exam paper 8.2 won; kitchen/head
  chef 5.8-6.8.
- Script judge (blind, round 1): B (lazy vs sharp) 6.7, A (warm) 6.5. Panel for B: stop 8/16, end 5, save 6.
  B revised once (B2); not re-judged (lean plan). Post-judge edits: judge/POST_JUDGE_EDITS.md.

## Cover
IMG_2781.MOV (cable fly, 28 Aug, red T-shirt) at about 0.9 s: camera-facing, mid-lift, well lit. Chosen from about 80
frames (sheets in photo/gym/). A bystander (likely a trainer) stands behind him: his face and two far-background faces
are blurred. ~/Movies/ContentOS/_photos/ did not exist when checked.

## QA (done)
- qa.json: 0 issues (text >= 40 px, quotes >= 44 px, margins, bottom 180 px, lower third used, video frame 0 shows the
  sticky and the LAZY card, animation ends >= 0.8 s before the end).
- Viewed: contact sheet (all stills, first/last frames), slides 1, 9, 11 at half size, a mid-animation frame of slide 6.
- Every quote on slides 3-10 checked by hand against runs/g*.md; word counts and slide-10 sums measured by script.
- ffprobe: 7 JPEG + 5 MP4 (H.264, AAC silent, 30 fps, 6-7 s), all 1080x1350.
- Tests: tests/carousel (10) + tests/visuals pass.

## Not checked
Phone legibility; Instagram's 3:4 grid crop of the cover; MP4 playback in the app; nutrition values (AI estimates);
the combined template as a whole; DM sending; silent audio by ear; no Opus/independent fact-check call (lean plan).

## For the creator
Hook "Your AI trainer met you 10 seconds ago." The script scored 6.7 blind before revision (below the 7 bar; the
revision was not re-scored). Check: the blurred bystander on the cover, the TRAINER keyword, slide 8 honestly says
"the smallest change". The brand guide lists "prompt packs" as avoided; this is framed as 8 tested techniques.
