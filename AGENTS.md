# Content OS: Codex-native operating instructions

This repository is operated through Codex under the user's ChatGPT sign-in.
Do not call the OpenAI API or use `OPENAI_API_KEY`. The active pipeline uses
the `openai-codex` SDK; `openai-agents` remains installed for compatibility
with historical schemas and optional local SDK utilities, not as the runner.

## Source of truth

- Human-authored briefs in `briefs/` decide **what** and **why**.
- `config/brand.yaml` defines the brand voice and pillars.
- `config/brand.yaml` also contains the human-approved Content Learning Memory;
  apply it to every draft, visual plan and QA pass.
- `config/scoring.yaml` contains deterministic approval gates.
- Versioned files in `prompts/` are execution guidance; do not edit a version
  in place when changing its meaning.
- `HANDOFF.md` records the system's decisions and current operating state.

## When asked to produce content

1. Read `CODEX_WORKFLOW.md`, the requested brief, `config/brand.yaml`, and the
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
   one Markdown artifact under `outputs/`, or ask Codex to run the matching
   `cli.py` workflow when the result must be persisted in the local database.
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
- Never commit secrets, API keys, or credentials.
