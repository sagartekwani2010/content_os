---
name: reel-orchestrator
description: Run the creator's reel production through the Content OS orchestrator (python -m content_os.orchestrator) - start a reel from an idea, show what is waiting, present creator gates (brief, script, recorded, cut_review, final_listen, posting) for approval, route feedback back to the right stage, queue work for the unattended runner, and check the runner. Use when the creator asks to make a new reel/script/video, asks what is pending, approves something, gives feedback on a reel, or asks whether background jobs are running.
---

# Reel orchestrator

Everything goes through the CLI from the repo root with `.venv/bin/python -m content_os.orchestrator`.
Work from the reel's state, never from chat history: `status <reel>` and `log <reel>` are the memory.

## Start of every session

1. `next` - one line per reel: who must act and how.
2. `runner-status` - is the launchd runner loaded, its heartbeat, queue counts, log tail.
3. If something failed: `status <reel>` shows the last error. Fix the cause, then `run <reel> --bg`.

## Creator asks for a new reel

`new "<idea>"` (add `--id <slug>` if they name it). The runner drafts the brief and notifies them at the
brief gate. An existing hand-written reel (outputs/<id>/SCRIPT.md) is brought in with `adopt <id>`.

## Presenting a gate

Show the artifact, not a summary of it:
- brief -> `outputs/<id>/brief.md`; script -> `outputs/<id>/SCRIPT.md` (point out open questions/placeholders);
- recorded -> the creator puts footage in `~/Movies/ContentOS/<id>/raw/`;
- cut_review -> `~/Movies/ContentOS/<id>/work/cut_review.html` (they must listen to every cut);
- final_listen -> the final MP4 and `outputs/<id>/av_review.md` (advisory; Claude cannot hear);
- posting -> `outputs/<id>/POST.md`. Content OS never posts; the creator posts by hand.

Then ask: approve, or what should change? Only run `approve <id> <gate> --note "..."` after the creator
says yes in this conversation. Never approve on their behalf, never infer approval from silence.
Approving queues a runner job that continues to the next gate.

## Feedback

`feedback <id> "<their words verbatim>"`. Report: the stage it was routed to and why, what was
invalidated, the re-run plan. If the routing looks wrong, re-run with `--stage <stage>`.
Then ask whether to start the re-run: `run <id> --bg` (runner) or `run <id>` (now).
If `log` shows `feedback_not_addressed`, the re-run gave identical output: a manual change is needed
(pipeline `select`, a `pipeline.yaml` override, or a script edit).

## Lessons

`memory candidates` / `memory` (promoted). A candidate seen in two independent feedback events is
promoted automatically; `memory approve <id>` promotes on the creator's say-so; `memory reject <id>`
retires one. Promoted lessons are fed only to the stages they apply to.

## Unattended work

`run <id> --bg`, `heartbeat --bg`, `queue`. The runner only runs stages whose gates are approved and
stops (notifies) at the next gate. Status page: `~/Movies/ContentOS/status.html`.
