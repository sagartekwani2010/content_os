# Reel orchestrator (`content_os.orchestrator`)

Takes a reel from an idea to a post-ready package. It stops at every creator gate, keeps a versioned
provenance ledger, routes feedback back to the stage it concerns, distils lessons into a small memory,
and runs approved work unattended under launchd.

```
python -m content_os.orchestrator new "<idea>" [--id slug] [--now]
python -m content_os.orchestrator adopt <reel-id>              # existing outputs/<id>/SCRIPT.md
python -m content_os.orchestrator status [<reel>] | next | log [<reel>] | queue
python -m content_os.orchestrator run [<reel>] [--until STAGE] [--bg]
python -m content_os.orchestrator approve <reel> brief|script|recorded|cut_review|final_listen|posting|performance [--note ...]
python -m content_os.orchestrator feedback <reel> "<text>" [--dry-run] [--no-model] [--stage S]
python -m content_os.orchestrator perf <reel> views=... saves=...
python -m content_os.orchestrator memory [list|candidates|approve ID|reject ID|show STAGE]
python -m content_os.orchestrator av-review <reel> | --file PATH [--out DIR]
python -m content_os.orchestrator heartbeat [--bg] | status-page
python -m content_os.orchestrator install-runner | uninstall-runner | runner-status
```

Settings: `config/orchestrator.yaml`. Claude models: the `orchestrator_*` agents in `config/models.yaml`
(prompts `prompts/orchestrator_*_v1.md`). Claude Code: `.claude/agents/reel-orchestrator.md` and
`.claude/skills/reel-orchestrator/SKILL.md`.

## Stage graph

```
idea → brief* → [gate brief] → script* → [gate script] → shoot_plan → [creator: recorded]
  → ingest → transcribe → segment → score(+judge) → cutpoints → cut_review(+judge) → [gate cut_review]
  → draft_render(+draft qa) → visuals → render → qa → av_review → [gate final_listen]
  → post_package* → [gate posting: the creator posts] → [creator: performance]
```
`*` = Claude stage through `content_os/llm_runtime.py`. The steps from ingest through qa run
`python -m content_os.pipeline` on the media dir. visuals runs `python -m content_os.visuals check|render`
when the reel has a `visual_cues.json`, and is skipped otherwise. av_review calls OpenAI. Each node depends
on the one before it plus its declared data inputs (for example ingest also hashes the script), and
everything after a node counts as downstream of it.

## Files

| Where | What |
|---|---|
| `outputs/<id>/state.json` | Compact current state: stage records, approvals, open feedback, waiting gate, last error |
| `outputs/<id>/ledger.jsonl` | Append-only trail: stage runs, approvals, invalidations, feedback, plans, lessons |
| `outputs/<id>/versions/<stage>/<hash>/` | Immutable copy of each text output version and its `provenance.json` |
| `outputs/<id>/*.md, beats.json, …` | Current artifacts |
| `~/Movies/ContentOS/<id>/` | Footage (`raw/`), the pipeline `work/` dir and renders. Outside the repo |
| `~/Movies/ContentOS/.orchestrator/` | `queue.sqlite`, runner heartbeat, notification log, locks |
| `~/Movies/ContentOS/status.html` | Status page |
| `feedback/orchestrator/` | Dated feedback records, `lesson_candidates.yaml`, `reel_memory.yaml`, `lesson_archive.yaml` |

## Provenance and backtracking

Each stage run records:
- a version: the sha256 of its outputs and result;
- the versions of its inputs;
- the model, prompt version, prompt sha and config hash;
- the lessons it was given;
- the cost.

A stage is fresh when it has not been flagged stale and its recorded inputs equal the current
versions of its dependencies. An approval is bound to the version it approved.

`feedback` works in five steps:
1. The Fable classifier (`orchestrator_feedback_classifier`) routes the text to the earliest stage that
   fixes it. If the model call fails, a keyword fallback routes it instead.
2. The orchestrator records the feedback.
3. It flags that stage and everything after it as stale, and moves approvals downstream into
   `approvals_history` with the reason. Nothing is deleted.
4. It writes the re-run plan.
5. It drafts a candidate lesson.

On the next run, the target stage receives the feedback verbatim. If a re-run produces identical output
(for example, a deterministic cutpoints run with unchanged inputs), the feedback stays open as
`feedback_not_addressed`. Fixing it then needs a manual change: `content_os.pipeline select`, a
`pipeline.yaml` override, or an edit to the script or cue sheet.

## Memory

1. Each piece of feedback produces a candidate lesson (category, rule of at most 280 characters,
   `applies_to` stages, source links).
2. A candidate that matches one already seen (Jaccard similarity of 0.6 or more on its tokens) is merged
   into it.
3. A candidate is promoted to `reel_memory.yaml` once it has been seen in 2 independent feedback events,
   or when the creator runs `memory approve`.
4. The memory holds at most 40 lessons. Lessons evicted to stay under that cap move to
   `lesson_archive.yaml`.
5. A stage reads at most 8 lessons whose scope matches it. It also reads the most relevant
   `content_learning_memory` entries from `config/brand.yaml`, filtered by category and ranked by word
   overlap.
6. `config/brand.yaml` is still edited only by hand.

## Runner

`install-runner` writes `~/Library/LaunchAgents/com.contentos.runner.plist`, with these settings:
- RunAtLoad and KeepAlive, with ThrottleInterval 30;
- logs in `~/Library/Logs/content_os/`;
- PATH includes the conda env bin that holds ffmpeg and whisper-cli.

It then bootstraps the agent into `gui/<uid>`.

How it runs jobs:
- It claims queued jobs one at a time.
- Each job runs as `caffeinate -i -s python -m content_os.orchestrator _exec-job <id>`, so the Mac stays
  awake only while a job runs.
- An `advance` job stops at the next gate with status `paused` and sends a notification.
- Jobs orphaned by a crash are requeued, up to 3 attempts.

Jobs are created by `new`, `approve`, `run --bg`, `heartbeat --bg` and `queue add`.

Requirements and limits:
- Desktop access: the repo is on the Desktop, so macOS asks once whether the env's `python3.12` may
  access the Desktop folder. Click Allow, or grant Full Disk Access to
  `~/.conda-envs/content-os-tools/bin/python3.12`. Until then, the runner blocks at startup.
- Sleep: `caffeinate -s` prevents system sleep only on AC power. On battery only idle sleep is prevented.
  Closing the lid sleeps the Mac in every case, unless it is in clamshell mode with power and a display
  connected.
- Keychain: the Claude Code login and the OpenAI key come from the login keychain, which stays unlocked
  while the user is logged in, including with the screen locked. After a reboot, nothing runs until the
  user logs in, because LaunchAgents are per-user.

## av_review (OpenAI)

What it sends:
- the final MP4's audio (mono 16 kHz WAV, at most 180 s) to `gpt-audio-mini`, through Chat Completions
  `input_audio`;
- 6 sampled frames to `gpt-5.4-mini`.

Both models are set in `config/orchestrator.yaml`. The API key is read from the Keychain
(`security find-generic-password -s content_os_openai -a $USER -w`) or from `OPENAI_API_KEY`. It is never
logged or written.

Outcomes:
- No key: the result is `skipped: no key`.
- An API error is recorded in `av_review.md`.

The review is advisory either way. The final-listen gate always stays with the creator.

## Optional editor integration (not built)

InVideo has a remote MCP server at `https://mcp.invideo.io/mcp`. It could be added to Claude Code as an
optional editor for generated B-roll. If it is added, follow AGENTS.md: check live credits first, use
`dry_run`/`max_credits`, and keep credentials out of the repo. The orchestrator does not call it.
