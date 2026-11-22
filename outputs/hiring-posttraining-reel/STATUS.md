# Salesforce hiring / post-training reel · STATUS (created 21 Nov 2026)

Read this first in a new chat. 22 Nov: gate 1 + 3 spines + script v1 in `GATE1_SPINES_SCRIPT_v1.md` (unscored). 22 Nov later: creator widened it to several companies; `SCRIPT_v2.md` = first script for review (Salesforce, Google Search Evals Bengaluru, OpenAI, Anthropic), evidence in `JOB_POSTINGS_EVIDENCE.md`. Blind judge not run yet. Later 22 Nov: creator wants the reel to SHOW how to write an eval (consulting). `consulting_eval/` built + run (10 so-what-slide cases, Fable 5.2 + Sonnet 5.5 students, Opus examiner): both 10/10, so the eval does not discriminate. `SCRIPT_v3.md` is built on that twist. Then creator asked for: case -> AI garbage answer -> call out issues -> evals (key, checks, fixed answer) -> Comment EVAL. Round 2 (`run_naive.py`, casual prompts, 4 models) found real failures; `SCRIPT_v4.md` uses case C7 (Fable 5.2's real 300-store slide, `consulting_eval/REEL_EXAMPLE_C7.md`). v4 = calmer fallback. Creator then asked for drama + consistency: round 3 (`run_ladder.py`, Fable 5.2, 4 prompt versions x 3 runs) = 20/30 -> 23/30 -> 30/30 -> 30/30. `SCRIPT_v5.md` built on that curve. Creator: case too weak/complex -> `SCRIPT_v6.md` = current: one simple case (C2 Pune vs Mumbai; casual 3/3 runs said 'all new stores in Pune', with the rule 3/3 correct), creator authority line (beat 3, creator must confirm wording/employer OK). Note: examiner leniently passed C2 v0 run1, strict v0 = 19/30. Then creator: dumb it down -> `SCRIPT_v7.md` (creator: too dumb): Indonesia case (C4, zero Indonesia data; casual 0/3, 'use only data' 0/3, one rule 3/3), beat 3 authority line confirmed by creator 22 Nov. -> `SCRIPT_v8.md` = CURRENT, in-between: store layout (C7) told simply (2 stores in Diwali +30%, normal stores +22%; casual 0/3, fix one 0/3 though it computed the Diwali effect, one rule 3/3). Then creator: case locked, but the eval must catch what viewer/AI miss -> Fable wrote v9 (3 drafts, blind judge, merge; `fable_v9/`), then v10 with the judge's 3 fixes. Blind: v9 6.2-6.5, v10 6.8 (mass 6.1). Two rewrite rounds used: below the 7 gate, creator decides. `SCRIPT_v10.md` = CURRENT. Direction (creator, 22 Nov): pay off the tease with EVALS and open a series "evals for every job", consulting first; reel first, carousels as the importable kit. Media and screenshots stay out of Git.

## Why this reel exists
Gym Jarvis Ep 3 (Workout Analyser) ends with the tease, spoken word for word:
"Next up: Salesforce is reportedly letting people go, but hiring people with AI experience." /
"How can you be that one? Follow along to know." This reel must pay that off. Calendar slot: Thursday = careers.

## What we have (verified)
- `SALESFORCE_LMTS_POSTTRAINING_JD.md`: the real posting, saved verbatim 20 Nov from Salesforce's Workday site.
  "LMTS - Lead AI/ML Engineer (LLM Post-Training)", JR368314, Bangalore + Hyderabad, posted 13 Nov 2026.
  Key quote: "This is a model-training role, not a wrapper around a hosted LLM and not a prompt-engineering-only role."
- `jd_card_top.png`, `news_headline.png`: cropped screenshots used in the Ep 3 ending (no names or photos).
- Cuts, sourced in `outputs/workout-analyser-reel/facts.md` ("SALESFORCE EXAMPLE" and "UPDATE 20 Nov"):
  - Benioff: support heads about 9,000 -> about 5,000 as AI agents handle about half the conversations (2025, on record).
  - India: staff reportedly put on garden leave until 1 Feb 2027, severance about 21 weeks (People Matters, DNA,
    19-20 Nov 2026; based on employee posts, NOT confirmed by Salesforce: always say "reportedly").
  - Feb 2026 "nearly 1,000 more cuts" was reported only: do not use.

## Process (gates from `.agents/skills/reel-script-writing/SKILL.md`)
1. Finding first: what does the creator uniquely add (the JD decoded skill by skill, his own path into post-training,
   what he would build to get hired)? Decide before any outline.
2. Reel profile: careers reel, not a build reel, so the Ep 2 system skeleton does not apply by default; decide per profile.
   SERIES ANCHOR applies only if it is framed as part of a series.
3. Fable writes 3 spines -> creator picks -> Fable script -> blind judge loop (3 parallel drafts, blind judge,
   Opus fact check; only blind scores count) -> paper animatic -> record -> visuals.
4. A trial variant is recorded only if it is drastically different (content or emotion), not a polish of the main.
5. Ship CAPTION.txt, pinned comment, cover.png, and dm_kit/ if there is a comment keyword.

## Decision 22 Nov (creator, in the calendar chat)
Tonight (Sun 22, about 19:30 IST) posts a **carousel only, no reel**: the evals series introduction and the consulting
eval kit in one piece (keyword EVAL; `dm_kit/` before posting). No separate kit carousel on Mon 23. Slide plan and
requirements: item 1 of `planning/content-calendar-2026-11-22.md`.


## 22 Nov (late): new premise, M2C diagnosis (`m2c_eval/`)
Creator moved to a Swiggy-like 'M2C dropped 31%' consulting case (simulated data, never Swiggy's numbers). Runs: clean tables Fable 30/30; raw export Fable 30/30, Haiku 29/30; hard mode (Slack pressure + cherry-picked table) Fable 30/30, Haiku 26/30; no model ever followed the boss (0/60). Hero case M1 (tracking bug, orders up): Haiku failed 2/3 (recommended app rollback without suspecting tracking). Creator: reduce evals (no more runs). `SCRIPT_v12.md` = CURRENT (consultant angle + eval mechanics shown with the checker's real verdicts). Optional: one small run (Haiku + one rule, M1, 3 runs) to restore the climb.

## 22 Nov (end of day): LOCKED for recording
- Script + beat sheet: `SCRIPT_v13_FINAL.md` (21 beats; Salesforce/Google open; consultant angle; eval mechanics; CTA comment EVAL for the framework).
- Teleprompter: `~/Movies/ContentOS/evals-ep1/teleprompter.html` (Chrome).
- Still assets A01-A21 (top-half panels): `~/Movies/ContentOS/evals-ep1/assets/`, built by `assets/build_assets.py` from m2c_eval results.
- Resume (after 9:30 pm if limits hit): animate the key panels (A11 checks building, A12 ticks, A15/A18 run marks), cover.png, CAPTION.txt + pinned comment, dm_kit (EVAL framework one-pager + the M1 case and checks), job title-block screenshots on the day, blind judge on the as-recorded transcript.

## 22 Nov (night): creator's narrative
`SCRIPT_v14.md` = CURRENT (creator's 13-point story, light vetting). Teleprompter rebuilt. Rule saved: career reels illustrate, never simulate. Old v13 assets A01-A06 still usable; A08-A21 need redoing for the funnel story.
