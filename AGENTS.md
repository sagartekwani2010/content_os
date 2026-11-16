# Content OS: operating instructions

This repository is operated through Claude (Claude Code for interactive work).
The pipeline's model stages run on Claude through `content_os/llm_runtime.py`:
the Anthropic Messages API (`anthropic` SDK) when `ANTHROPIC_API_KEY`,
`ANTHROPIC_AUTH_TOKEN` or an `ant auth login` profile is available, otherwise
the Claude Agent SDK (`claude-agent-sdk`) on the creator's local Claude Code
login, with no API key. Models, effort and prompt versions are set per stage in
`config/models.yaml`; never hardcode a model name in code. Do not use Codex or
the OpenAI API for model stages. OpenAI may appear only as an optional
transcription provider under `content_os/pipeline/`.

## Source of truth

- Human-authored briefs in `briefs/` decide **what** and **why**.
- `config/brand.yaml` defines the brand voice and pillars.
- `config/brand.yaml` also contains the human-approved Content Learning Memory;
  apply it to every draft, visual plan and QA pass.
- `config/scoring.yaml` contains deterministic approval gates.
- Versioned files in `prompts/` are execution guidance; do not edit a version
  in place when changing its meaning.
- `HANDOFF.md` records the system's decisions and current operating state.

## Recovering a stalled chat

The repository cannot detect or resume a stuck agent session. To reduce
recovery work, run `python scripts/prepare_chat_handoff.py [path/to/focus-file]`
and paste its output into a fresh chat. Add `--note "..."` for decisions that
exist only in the conversation. The packet includes current project handoff,
Git state, and the selected file; it does not include chat transcripts or
attachments.

## When asked to produce content

1. Read `CLAUDE_WORKFLOW.md`, the requested brief, `config/brand.yaml`, and the
   relevant versioned prompt files.
2. Preserve the six immutable brief fields: topic, core thesis, learning
   objective, format, brand pillar, and high-level sections.
   Explain the idea through a familiar real-life setup before introducing
   technical vocabulary; see `communication_principles` in `config/brand.yaml`.
   Treat `content_learning_memory` as approved operating guidance, not optional
   style notes. Log future human revisions with `feedback/POST_REVIEW_TEMPLATE.md`.
   Apply `feedback/VIDEO_LEARNING_LOOP.md` after each generated video candidate
   and final export; preserve review evidence and version prompt changes.
3. Produce the execution plan, content package, visual plan, and QA report in
   one Markdown artifact under `outputs/`, or run the matching `cli.py`
   workflow when the result must be persisted in the local database.
4. Never publish, schedule, buy ads, or invent a human approval. The creator
   has authorized credit-limited invideo or Magnific runs for active, unposted
   videos after a live cost check; fal.ai generations stay with the creator.
   Flag factual gaps and thesis conflicts rather than silently changing the
   brief.
5. Run `python cli.py check <brief>` before handoff. This is a deterministic
   local validation command, not a model runner.

## When asked for discovery or planning

Use the supplied sources, brand guidance, and deterministic scoring rules as
evidence. Present recommendations for human approval; do not create production
content from an unapproved topic.

## When editing recorded video

Use `.agents/skills/reel-footage-edit/SKILL.md`.
Build a timecoded take log and complete narration cut before adding B-roll or
shortening for runtime. Remove dead air and distracting off-camera gaze by
default, then verify each join and the platform export. Keep media MCP
credentials out of the repository.
Use ChatGPT for keyframe images. The creator runs fal.ai generations. Check
live credit estimates before any authorized invideo or Magnific video run, and
do not regenerate a posted video merely to test a connection.

## Repository conventions

- Preserve append-only historical records and existing databases.
- Keep generated content human-readable in `outputs/`.
- Run `python -m pytest tests -q` after changing Python code.
- Never commit secrets, API keys, or credentials. Never write an
  `ANTHROPIC_API_KEY` or other credential into a file in this repository.
- Commit or push only when the creator asks. Any Git commit made with Claude
  ends its message with the Claude attribution trailer, for example
  `Co-Authored-By: Claude <noreply@anthropic.com>` (use the exact line your
  Claude Code session specifies, which names the model).
