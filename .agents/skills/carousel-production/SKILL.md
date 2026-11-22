---
name: carousel-production
description: Produce an Instagram carousel end to end from the creator's theme and points. Covers the brief, a real run, a slide script, a blind judge loop, hand-drawn light-theme slides with short video slides, a creator photo cover, QA, packaging and the readout. Claude orchestrates and executes every step; the creator approves the brief points and the finished carousel. Use for every carousel (Playbooks, companions to reels, careers kits).
---

# Carousel production (template for every carousel)

The creator gives a **theme and the points to cover**. Everything else is Claude's job: execution, the real run,
evals, engagement judging, visuals and packaging. The creator sees the work twice: an optional glance at the brief,
then the finished carousel in `PREVIEW.html`. Nothing is posted without the creator's explicit yes.

Version 1, 22 Nov 2026, finalised through the first carousel (`outputs/carousel-prompting-recipe/`). Each later
carousel may change this file. Record what changed and why in "Changelog" at the bottom.

## Where things live

- Text (public repo): `outputs/<carousel-id>/`: `STATUS.md`, `BRIEF.md`, `runs/` (real prompts and outputs,
  verbatim), `drafts/`, `judge/`, `slides.json`, `CAPTION.txt`, `PINNED_COMMENT.txt`, `dm_kit/` (text only).
- Media (never in Git): `~/Movies/ContentOS/<carousel-id>/`: `photo/`, `render/`, `POST/` (numbered upload files),
  `PREVIEW.html`.
- Renderer: `python -m content_os.carousel render outputs/<carousel-id>` (built on `content_os.visuals`: skia,
  Kalam and Patrick Hand fonts, palette in `content_os/visuals/palette.py`).

## House style

- **Light theme.** Off-white paper background (`palette.PAPER`), ink outlines, bright saturated accents, a yellow
  highlighter band for the key words. Same family as the approved reel diagrams.
- **Hand-drawn look.** Wobbly line diagrams, sticky notes, arrows and circles. One idea per slide. No stock
  imagery and no dense cards.
- **Simple explanations.** Simple enough for a 15-year-old to follow. Headline ≤ 8 words, body ≤ 25 words. No jargon unless
  the slide defines it. English only.
- **Video slides.** Short (4-8 s), silent, calm draw-on animation of that slide's diagram. Frame 0 must already
  show the headline, because Instagram shows the first frame before playback. Aim for at least one video slide per
  three slides. Prefer video wherever motion explains something (a before → after, a flow, a growing bar).
- **Slide 1 = creator photo + hook.** A frame from the creator's own footage (camera-facing, eyes open, expressive,
  well lit), framed as a hand-drawn polaroid or cut-out on paper, with the hook handwritten beside it. Use a photo
  that has not appeared on a recent cover.
- **Format.** 1080×1350 (4:5) for every item. Stills are JPEG (the Graph API accepts only JPEG). Videos are H.264
  MP4, 30 fps, ≤ 60 s, with a silent AAC track. Up to 20 items, aiming for 7-10.
- **Two domains merged.** The AI concept is one domain, an everyday or cultural one (cooking, cricket, Ramayan,
  health) is the other. The analogy is the hook. The **real run** is the proof.

## Steps

### Roles (from 22 Nov 2026)
- **Codex builds** with OpenAI models: steps 0-3 and 5-7. It owns `content_os/carousel/`.
- **Claude evaluates** with Fable and Opus: step 4 and the gate before step 8, run by
  `python -m content_os.carousel_eval eval <id>` from the Codex-written `SUBMISSION.json`. Claude also monitors
  Codex: `python -m content_os.carousel_eval monitor`. See "Carousel ownership" in `AGENTS.md`.

### Call budget: lean by default (the creator's rule, 22 Nov 2026)
The creator's usage limit is finite, so keep model calls to a minimum by default:
- one Fable brainstorm call (framings, examples and its own pick);
- real runs once each, on a cheaper model named on the slide;
- one Fable draft;
- one blind Fable judge, plus one revision only if the score is < 7, with no re-judge;
- the fact check is done by the orchestrating session itself, with no extra model call.

That is roughly 10-15 calls per carousel. Use heavier loops (several drafts, repeated judges) only when the creator
asks for them. Report the number of calls in `STATUS.md`. The steps below describe the full loop; follow them with
these limits.

### 0. Fable brainstorm (always first; the creator's rule, 22 Nov 2026)
Fable 5.2 does the creative thinking. Claude (Opus) orchestrates and checks; it does not pick the concept on its own.
- Ask Fable for **at least 4 whole-carousel framings** and, **for every concept or technique, 3 real-world everyday
  examples** that a non-technical Indian Instagram viewer gets instantly. No jargon, no abstract AI-speak.
- **Every concept is explained through a real-world example that is easy to digest.** A carousel that only states
  principles ("be specific") fails this step.
- **Contexts allowed:** only **very popular** contexts (cricket, Ramayan, Bollywood) or **the creator's own
  interests**: gym and fitness first, then AI building and careers. Never a random context such as a kitchen or a
  head chef. Gym is the default: the creator's audience relates to it, and the creator has gym photos and footage.
  Constrain the brainstorm to the chosen context.
- A separate blind Fable judge scores the framings and examples on:
  - instant understanding (a 15-year-old gets it in one read);
  - real-world familiarity;
  - save/share pull;
  - how cleanly the analogy maps to the concept;
  - whether the real run will visibly show the difference.
- Keep the winners. Save everything in `brainstorm/`.
- When in doubt, spend more Fable calls here, not fewer. This is where a carousel is won.

### 1. Brief (from the creator's theme, points and the brainstorm winners)
Write `BRIEF.md`:
- the AI concept and the everyday domain;
- the one takeaway a viewer saves for;
- the creator's points, mapped to slides;
- the real run planned;
- the comment keyword, if any, and what the DM delivers;
- the posting slot (from `planning/content-calendar-*.md`).

Check it against the calendar rules: two domains, no "me too". If the creator only gave a theme, propose the points
in the brief and continue. The creator can correct them at the final gate.

### 2. Real run (proof, never invented)
Run the actual prompts, guardrail or eval against a real model, for example through `content_os.factory.llm.call`
or `claude -p --model …`. Save every prompt and output verbatim in `runs/` with the model id and date. Slides quote
these outputs, trimmed but never reworded. Mark anything shortened with "…". If the run does not show the point,
change the point, not the output.

### 3. Slide script: 3 drafts from Fable
Three independent drafts in `drafts/`, each with a different hook or angle, as JSON per slide: `n`, `kind`
(cover | still | video | cta), `headline`, `body`, `visual` (what is drawn and how it moves), plus `caption` and
`pinned_comment`. Structure:
- slide 1: hook;
- slide 2: why it matters (the stake);
- middle slides: one idea each, the analogy then the real run;
- second-to-last slide: a recap the viewer saves;
- last slide: CTA (keyword or save/share, plus follow for the series).

### 4. Blind judge loop (only blind scores count)
A fresh judge that did not write the drafts (Fable via a separate call, no author labels, drafts shuffled) scores
each draft from 1 to 10 on:
- hook stop power (slide 1 alone);
- swipe-through (does each slide make the next one necessary?);
- clarity (could a 15-year-old follow it?);
- save-worthiness;
- share/send-worthiness;
- two-domain merge;
- proof (the real run, used honestly);
- accuracy.

The judge also predicts, for the panel in `content_os/factory/tournament.py` (`PANEL`), who stops, who swipes to
the end, and who saves. The weighted total must be ≥ 7 blind. Otherwise revise the winner against the judge's notes and
re-judge (up to 3 rounds). If it still scores < 7, stop and ask the creator. Then run an Opus fact check on the winner
(facts, honesty, house rules, the cultural or religious respect rule) and fix every flag. Save everything in `judge/`.

### 5. Visuals and render
Write `slides.json` (the renderer spec) and render. Cover: pick 6-10 candidate frames from the newest talking-head
recording (`ffmpeg` at 1 fps), look at them, choose one, and record the choice and why in `STATUS.md`. Use the
`content_os.visuals` elements and templates for the diagrams. Video slides are animated versions of the same
diagram.

### 6. QA (look at every slide)
- Build a contact sheet and look at it. Check every still and the first and last frame of every video.
- Text ≥ 40 px at 1080 wide, with nothing within 60 px of the edges. Nothing important in the bottom 180 px, which the
  Instagram UI covers.
- Spelling. Every number traces to `runs/` or a cited source.
- File specs (`ffprobe`): size, codec, duration ≤ 60 s, JPEG stills.
- Frame 0 of every video is a meaningful still.

Record what was checked and what was not.

### 7. Package
- `POST/`: `01_cover.jpg`, `02_….mp4`, and so on, in upload order.
- `CAPTION.txt`: the Instagram post caption, not subtitles. Hook line, 3-5 short lines, keyword CTA, 3-5 hashtags.
- `PINNED_COMMENT.txt`.
- `dm_kit/` if there is a keyword: DM reply, short DM, the deliverable. Test it before posting.
- `PREVIEW.html`: a swipeable phone-width preview of the slides in order, with the caption below. This is what the
  creator reviews.

### 8. Creator gate
Show `PREVIEW.html` and a five-line summary: the hook, the blind score, the real-run result, the risks, and the post
time. Apply the creator's changes, re-run steps 4-6 for any slide that changed, and get an explicit yes.

### 9. Post and read out
The creator posts manually until the Graph API token exists. After that, use `instagram` skill `publish_carousel`
with the JPEG and MP4 URLs. At 24 h and 48 h, record reach, % non-follower reach, saves, sends, follows, profile
visits and keyword comments. Store them in `STATUS.md` and the calendar or catalogue. Compare them with the judge's
predictions: that comparison is how the judge gets calibrated.

### 10. Learn
Append any lesson that should change the next carousel to the "Changelog" below, with its evidence.

## Changelog
- v1 (22 Nov 2026): first version, written before the first run.
