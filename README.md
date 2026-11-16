# Content OS

Content OS is a **Claude-native** workspace for producing thoughtful,
Instagram-first AI content from human-approved briefs. Open the folder in
Claude Code, ask for the requested work, and Claude uses the project
instructions in `CLAUDE.md` and `AGENTS.md`. No API key is required: pipeline
commands fall back to your local Claude Code login.

## Start here

1. Open the repository in Claude Code (terminal, desktop app, or the VS Code
   extension for an IDE file explorer).
2. Read `HANDOFF.md` for product context and current constraints.
3. Create or edit a human-authored brief under `briefs/`.
4. Ask Claude: `Produce the package for briefs/<name>.yaml`.
5. Review the generated package under `outputs/`: `caption.txt`, package JSON,
   thumbnail prompt, per-asset ChatGPT-UI prompts and an `assets/` folder.
   Publishing and scheduling require creator action. Media generation for an
   active, unposted video follows live credit checks and the creator's fal.ai
   boundary in `feedback/VIDEO_LEARNING_LOOP.md`.

Claude Code loads `CLAUDE.md`, which points to `AGENTS.md`. The detailed
execution contract lives in `CLAUDE_WORKFLOW.md`.

## What stays deterministic

Python remains the coordinator and deterministic support layer. It validates
briefs, models durable data, and retains scoring, QA gates, append-only
history, and ad-eligibility logic. Each contextual stage is its own isolated,
tool-less Claude call: planning, hooks, writing, visual direction, and QA.

```bash
python -m pip install -r requirements.txt
python cli.py check briefs/example_production_ai.yaml
python -m pytest tests -q
```

Run these commands from a terminal or ask Claude Code to run them for you.
Every model stage runs on Claude (see "How coordination works" for how the
backend is chosen):

| Command | Purpose |
|---|---|
| `python cli.py doctor` | Validate config, database, and the Claude runtime. |
| `python cli.py produce <brief-id>` | Run brief strategist → hooks → writer → thumbnail + visual planner → QA, then export a complete package. |
| `python cli.py produce-approved` | Produce the approved brief backlog. |
| `python cli.py attach-assets <package-dir> <source-dir>` | Copy completed ChatGPT-UI renders into the package’s `assets/` folder by filename. |
| `python cli.py simulate-validators` | Run the named adversarial story and asset-validation suite; compare expected versus observed verdicts. |
| `python cli.py discover`, `score`, `plan`, `weekly` | Run the original coordinated discovery and planning workflows. |
| `python cli.py create-brief "Topic" --format carousel` | Create a human-editable brief template. |

## Content workflow

```text
human-approved brief
  -> Claude execution plan
  -> hooks + Reel/carousel package
  -> thumbnail + visual plan
  -> exported caption and asset handoff
  -> QA report against deterministic gates
  -> human review
```

The six immutable brief fields are topic, core thesis, learning objective,
format, brand pillar, and high-level sections. Claude may improve execution, but
must flag conflicts instead of silently changing the strategy.

## Project map

```text
CLAUDE.md              Claude Code entry point
AGENTS.md              Agent rules for this workspace
CLAUDE_WORKFLOW.md     Content-production procedure and output contract
briefs/                Human-authored source briefs
outputs/               Claude-generated, human-reviewable content packages
config/brand.yaml      Brand positioning, pillars, voice, audiences
config/scoring.yaml    Deterministic scores, QA gates, and approval thresholds
prompts/               Versioned execution reference material
content_os/            Pydantic models, storage, deterministic tools, Claude runtime
tests/                 Deterministic safeguards
HANDOFF.md             Product decisions and current operating state
```

## How coordination works

The existing workflow code remains the orchestrator. For every named stage it:

1. Loads the stage's versioned prompt, model, and effort from `config/models.yaml`.
2. Sends one Claude call with the prompt as the system prompt and the
   Pydantic model's JSON Schema as the required output structure. The stage
   has no tools, so it cannot read or change the repository.
3. Validates the response in Python (retrying once with the validation error
   fed back), records the request or session ID, token usage, and cost in
   `agent_runs`, then passes the validated object to the next stage.

That keeps the intentional sequence intact: for example, the writer receives the
approved brief and selected hooks, while the visual planner receives finished
copy. Stages are isolated so one role cannot overwrite another's context.

## Claude runtime

`content_os/llm_runtime.py` picks the backend automatically:

- **Anthropic Messages API** (`anthropic` SDK) when `ANTHROPIC_API_KEY`,
  `ANTHROPIC_AUTH_TOKEN`, or an `ant auth login` profile is available.
  Structured outputs via `messages.parse`, adaptive thinking, per-stage effort,
  and server-side refusal fallbacks. Cost is priced from the `pricing` block in
  `config/models.yaml`.
- **Claude Agent SDK** (`claude-agent-sdk`) otherwise. It drives the bundled
  Claude Code CLI with your local Claude Code login, so no API key is read.
  Built-in tools and local settings are disabled for each stage. The ledger
  records the cost the SDK reports.

Set `CONTENT_OS_LLM_BACKEND=anthropic_api` or `claude_agent_sdk` to force one.
`config/models.yaml` routes Claude Fable to the quality-critical stages (briefs,
hooks, scripts, story judgement, visual planning), Claude Opus as the default,
and Claude Sonnet or Haiku to the high-volume stages. No model name is
hardcoded in Python.
