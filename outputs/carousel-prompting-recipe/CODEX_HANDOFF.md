# Codex handoff · Prompting techniques carousel (v3) · 22 Nov 2026

You are taking over an Instagram carousel for the creator's Content OS. Read `AGENTS.md` (repo rules) and
`.agents/skills/carousel-production/SKILL.md` (the carousel template) first. Claude built v1 and v2; the creator
rejected both. Your job is to build v3 yourself as an agent (signed in with ChatGPT). **Make no OpenAI API calls**:
reuse the existing real runs in `runs/` and write the slides yourself. Claude evaluates it (see "Evals").

## Goal
A save- and share-worthy carousel that teaches **real prompting techniques by their actual names**, each explained
through an easy **gym** example. Slot: the Playbook series (prompting → guardrails → evals). It was planned for
Mon 23 Nov 13:00 IST; check with the creator whether that slot still holds.

## The creator's rules (non-negotiable)
1. **Real technique names as headlines**: "Few-shot prompting", "Chain-of-thought", and so on. The gym analogy explains
   each one; it does not replace the name.
2. **Every concept gets an easy real-world example.** The context is **gym/fitness** (the creator's world). No random
   contexts (kitchen and head chef were rejected). Very popular contexts (cricket, Ramayan) are allowed only if gym
   genuinely doesn't fit a technique.
3. **Simple explanations and simple visuals**: light paper theme, hand-drawn doodles, short silent video slides. v2
   failed by becoming text cards. Aim for ≤ 25 words of body per slide and one gym doodle per technique.
4. **Creator photo on slide 1** (a gym photo). Use `~/Movies/ContentOS/_photos/` if the creator has added photos;
   otherwise use the current `photo/cover_gym.jpg`. Blur bystanders' faces.
5. **No API calls for production.** Reuse `runs/` (real Fable 5.2 outputs). If a technique truly needs a new run, ask
   the creator first. The official evaluation is Claude's (see below).
6. Real runs only: quote outputs verbatim (trimmed with "…"), never invent. Label test personas and scripted replies.
   Label nutrition and price numbers as the AI's estimates.
7. English only. Public repo: media, photos and secrets never go into Git. No keys are needed. Never write any key
   into a file. Do not post, commit or push without the creator's yes.

## Techniques: proposed scope for v3 ("Prompting basics")
Recommended: **6-8 of these, by name**. The rest become later carousels (reasoning techniques; workflows).

| Technique | Gym analogy (seed) | Existing real run |
|---|---|---|
| Context prompting | Tell a new trainer your age, job, timings | `runs/g1_context__*` |
| Constraint prompting | "No barbell, 30 min, knee-friendly" | `runs/g2_constraints__*` |
| Few-shot prompting | "Here are 2 workouts I liked, make one like these" | `runs/g3_examples__*` (weak difference; rerun or drop) |
| Structured output | "Give me 5 cues, not a lecture under the bar" | `runs/g4_format__*` |
| Iterative / check-in prompting | Plan 2 weeks, then check in | `runs/g5_chain__*` |
| Clarifying questions | A good trainer asks about injuries first | `runs/g6_questions__*` |
| Uncertainty prompting ("say I don't know") | A trainer measures you; he doesn't guess | `runs/g7_dontguess__*` |
| Chain-of-thought + self-critique | A gym bill, item by item, then check the total | `runs/g8_checkable__*` |
| Role / persona prompting (optional) | "You are a beginner strength coach": changes tone more than accuracy | needs a new run |

The existing runs were made on Claude Fable 5.2 (see `runs/tasks.json`). You may reuse them, naming that model on the
slide. Do not rerun them on another model unless the creator asks.

## Evals: Claude evaluates, Codex builds
Codex **runs** the official evaluation, but Claude's code does the judging: Fable 5.2 is the blind engagement judge
and Opus 5.5 does the visual and honesty review, through the creator's local `claude` login (no key needed). Codex must not touch
that code (`content_os/carousel_eval/`; see "Carousel ownership" in
`AGENTS.md`). Production needs no model calls: you write the slides and reuse the runs.

**When a version is ready, write `outputs/<id>/SUBMISSION.json`.** The schema is in
`content_os/carousel_eval/contract.py` (contract `carousel_submission@1`). It must include:
- upload-ordered `post_files` and a `contact_sheet`;
- per slide: `headline`, `body` and `visual`, plus every quoted model output in `quotes` with the run file it came from;
- the caption and pinned comment files, the keyword and `dm_kit_dir`, `runs_dir`, `facts_file`, `models_used`,
  `calls` and `cost_usd`.

Then tell the creator "v3 submitted for evaluation".

Before submitting, run the free deterministic gate yourself and fix everything it flags:
`.venv/bin/python -m content_os.carousel_eval check carousel-prompting-recipe`. It checks:
- JPEG or H.264 at 1080×1350, videos 3-60 s with an audio track, 2-20 items, at least 1 video in 3;
- headline ≤ 10 words and body ≤ 25 words;
- every quote verbatim in its run file;
- the caption, and a dm_kit if there is a keyword.

Then run `.venv/bin/python -m content_os.carousel_eval eval carousel-prompting-recipe` (2 Claude calls). It writes
`outputs/<id>/eval/<version>/EVAL.md` and `eval.json`. The verdict is
PASS / REVISE / FAIL. Gate: Fable weighted score ≥ 7, no blocking issue, and legible on a phone. On REVISE, fix what
EVAL.md lists, bump `version` and resubmit. Never edit `eval/`.

## Code you can use
- Renderer: `.venv/bin/python -m content_os.carousel render outputs/carousel-prompting-recipe [--only 1,4]`
  (`content_os/carousel/`: items.py, render.py, runs.py, judge.py, llm.py). It reads `slides.json`, writes media to
  `~/Movies/ContentOS/carousel-prompting-recipe/`, and builds POST/, PREVIEW.html, contact_sheet.jpg and qa.json.
  Layouts include `before_after`. The visual style comes from `content_os/visuals/` (palette, Kalam and Patrick Hand
  fonts, doodles).
- `content_os/carousel/llm.py` calls Claude via `claude -p`. Don't use it for v3 (no production model calls needed).
- `content_os/carousel/runs.py`: the before/after runner, which supports chained prompts.
- Tests: `tests/carousel/` (10) and `tests/visuals/`. Keep them passing.

## Assets already generated (v2 unless marked)
Repo text, in `outputs/carousel-prompting-recipe/`:
- `slides.json` (v2 spec, 12 slides) and `build/make_slides.py`
- `runs/`: 32 run files (8 techniques × before/after × 2), `tasks.json` (prompts and personas), `pilot/` (obsolete
  kitchen pilot)
- `brainstorm/`: the open round (all contexts, where kitchen and head chef lost) and the gym round (winner: "Day 1 with a
  new trainer", 8.4)
- `drafts/`: v2_A, v2_B, v2_B2 (the revision)
- `judge/`: `FACTS.md`, `RUNS_DIGEST.md`, `POST_JUDGE_EDITS.md`, round-1 prompt, reply and key (v2_B scored 6.7)
- `CAPTION.txt`, `PINNED_COMMENT.txt`, `STATUS.md`, `ledger.jsonl` (94 calls, $19.30 across v1 and v2)
- `dm_kit/`: `DM_REPLY.txt`, `DM_SHORT.txt`, `CHEAT_SHEET.txt`, `COMBINED_TEMPLATE.txt`, `README.txt` (keyword TRAINER)
- `v1/`: the rejected kitchen ("Maa's recipe") version

Media (outside Git), in `~/Movies/ContentOS/carousel-prompting-recipe/`:
- `POST/`: 12 files (01_cover.jpg, 02_casting.jpg, 03_t1.mp4, 04_t2.mp4, 05_t3.jpg, 06_t4.mp4, 07_t5.jpg, 08_t6.jpg,
  09_t7.mp4, 10_t8.jpg, 11_cheat_sheet.jpg, 12_cta.mp4), all 1080×1350
- `render/` (the same set plus `frames/`), `PREVIEW.html`, `contact_sheet.jpg`, `qa.json`
- `photo/`: `cover_gym.jpg` (a cable-fly frame from IMG_2781.MOV, bystander blurred), `cover_photo.jpg` (v1 talking
  head), `pick_1-4.jpg`, `cand/` and `gym/` (candidate frames)
- `dm_kit/cheat_sheet.jpg`
- `v1/` (the rejected v1 media)

## Why v1 and v2 were rejected (don't repeat these)
- v1: a random context (kitchen), one idea ("be specific") instead of named techniques, and the concept was picked
  without a brainstorm.
- v2: gym framing accepted, but too text-heavy, hand-drawn visuals turned into text cards, empty lower thirds,
  no real technique names, a weak Examples slide, blind score 6.7, and far too many model calls.

## Deliver to the creator
Only after Claude's evaluation says PASS: `PREVIEW.html` plus a five-line summary (the hook, Claude's scores, the
techniques covered, the risks, and the call count and cost). Then wait for an explicit yes before anything is posted.
