# Carousel system · final handover (22 Nov 2026)

For the creator and for Codex. It covers how carousels are made from now on, who does what, how to run it, and
where everything is.

## 1. How it works

```
Creator ──theme + points──▶ Codex (OpenAI models) builds the carousel
                              │  writes outputs/<id>/SUBMISSION.json
                              ▼
               Codex runs:  python -m content_os.carousel_eval eval <id>
                              │  (Claude's code: Fable 5.2 blind judge + Opus 5.5 visual/honesty review)
                              ▼
               outputs/<id>/eval/<version>/EVAL.md ── PASS ─▶ creator reviews PREVIEW.html ─▶ yes ─▶ post
                              │
                              └─ REVISE/FAIL ─▶ Codex fixes, bumps version, re-runs eval
Every 2 days: launchd job → Claude monitor report + Opus review → ~/Movies/ContentOS/_monitor/ + notification
```

## 2. Who owns what

| | Codex | Claude |
|---|---|---|
| Role | Builds carousels: brainstorm, real runs, slides, render, package | Evaluates and monitors; owns the template |
| Code | `content_os/carousel/`, `tests/carousel/` | `content_os/carousel_eval/`, `tests/carousel_eval/` |
| Files | `outputs/carousel-*/` (except `eval/`), `~/Movies/ContentOS/carousel-*/` | `outputs/carousel-*/eval/`, `.agents/skills/carousel-production/SKILL.md` |
| Models | OpenAI (`OPENAI_API_KEY`) | Fable 5.2 + Opus 5.5 (`ANTHROPIC_API_KEY`, or the local `claude` login) |

**Isolation.** The evaluator never imports Codex's code. It reads only `SUBMISSION.json` (contract
`carousel_submission@1`, in `content_os/carousel_eval/contract.py`) and the files that file lists. A test fails if
this ever changes. Codex may run the evaluator but must not edit it. The monitor flags any edit to Claude-owned files
(by hash, against `seal`).

## 3. One-time setup on the creator's Mac (keys never go into files)

Add the keys to `~/.zshrc`, **not** to any repo file. The repo is public.
```
export OPENAI_API_KEY=...        # Codex production calls
export ANTHROPIC_API_KEY=...     # evaluation calls (billed to the API account, not your Claude Code limit)
```
Then `source ~/.zshrc`. Without `ANTHROPIC_API_KEY`, the evaluation falls back to the local `claude` login.

The every-2-days monitor is **already installed** (`scripts/install_carousel_monitor.sh`, launchd label
`com.contentos.carousel-monitor`). It uses the local `claude` login, so no key is stored in the plist.
- Re-install: `./scripts/install_carousel_monitor.sh`
- Stop: `launchctl unload ~/Library/LaunchAgents/com.contentos.carousel-monitor.plist`

## 4. Commands

| Command | Who runs it | Model calls |
|---|---|---|
| `.venv/bin/python -m content_os.carousel render outputs/<id>` | Codex | 0 |
| `.venv/bin/python -m content_os.carousel_eval check <id>` (specs, word limits, verbatim quotes, dm kit) | Codex, before submitting | 0 |
| `.venv/bin/python -m content_os.carousel_eval eval <id>` (check + Fable judge + Opus review) | Codex, after submitting | 2 |
| `.venv/bin/python -m content_os.carousel_eval monitor` | Claude or the creator, on demand | 0 |
| `.venv/bin/python -m content_os.carousel_eval monitor --scheduled` (report + Opus review) | launchd, every 2 days | 0-1 |
| `.venv/bin/python -m content_os.carousel_eval seal` (after Claude edits its own files) | Claude | 0 |

**Gate for PASS:**
- no blocking check;
- Fable weighted score ≥ 7, with weights hook 0.15, swipe 0.15, clarity 0.10, save 0.15, share 0.10, merge 0.10,
  proof 0.10, accuracy 0.15;
- Opus finds no blocking visual issue and confirms the slides are legible on a phone.

## 5. The creator's rules every carousel follows (from SKILL.md and memory)

- Every concept is explained through an easy real-world example. Contexts come only from very popular worlds
  (cricket, Ramayan) or the creator's own: **gym first**, then AI building and careers. No random contexts.
- Real names for techniques and concepts. Simple words: headline ≤ 8-10 words, body ≤ 25 words. Light hand-drawn
  style, short video slides, the creator's (gym) photo on slide 1.
- Real runs only, quoted verbatim. Label test personas and model estimates.
- **Lean model use:** about 10 production calls, 2 evaluation calls per version, revisions only as needed.
- Nothing is posted without the creator's explicit yes. Keyword CTAs ship with a tested `dm_kit/`.

## 6. Current state

- **Carousel in progress:** `carousel-prompting-recipe` (prompting techniques, gym framing). v1 (kitchen) and v2 (gym,
  text-heavy, Claude score 6.7) were rejected. **v3 is Codex's first job.** Brief:
  `outputs/carousel-prompting-recipe/CODEX_HANDOFF.md`. Full technique list: basics first (context, constraints,
  few-shot, structured output, clarifying questions, uncertainty, iterative, chain-of-thought + self-critique).
  Reasoning and workflow techniques are later carousels.
- **Assets ready:** 32 real runs (Fable 5.2), brainstorm (gym winner "Day 1 with a new trainer"), FACTS, DM kit
  (TRAINER), the v2 render (12 slides in `~/Movies/ContentOS/carousel-prompting-recipe/POST/`), gym cover photo
  (bystander blurred). Full list in CODEX_HANDOFF.md.
- **Calendar:** `planning/content-calendar-2026-11-22.md` (Mon/Wed/Fri carousels; Thu paper, Sat build, Sun careers reels).
  Next carousel: Lakshman Rekha guardrails (Wed 25).
- **Spend so far on this carousel:** 94 Claude calls, $19.30 (v1 + v2, before the lean rules).

## 7. Not done or not verified

- Codex has not yet run against this setup. The first `eval` on a real submission is the end-to-end test.
- The API backend (`ANTHROPIC_API_KEY`) is written from the SDK docs but **not yet run with a real key**. The `claude`
  CLI backend is what has been used so far.
- Instagram Graph API token (posting, readouts, DMs): not set up. Posting stays manual.
- Legibility on a real phone and playback inside Instagram: never checked on a device.
