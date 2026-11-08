# Content OS

Content OS is a **Codex-native** workspace for producing thoughtful,
Instagram-first AI content from human-approved briefs. Open the folder in
Codex, ask for the requested work, and Codex uses the project instructions and
your ChatGPT authentication. No API key is required.

## Start here

1. Open `/Users/sagart/Desktop/content_os` in Codex (or VS Code with the Codex
   extension for an IDE file explorer).
2. Read `HANDOFF.md` for product context and current constraints.
3. Create or edit a human-authored brief under `briefs/`.
4. Ask Codex: `Produce the package for briefs/<name>.yaml`.
5. Review the generated package under `outputs/`: `caption.txt`, package JSON,
   thumbnail prompt, per-asset ChatGPT-UI prompts and an `assets/` folder.
   Publishing and scheduling require creator action. Media generation for an
   active, unposted video follows live credit checks and the creator's fal.ai
   boundary in `feedback/VIDEO_LEARNING_LOOP.md`.

Codex loads `AGENTS.md` before working. The detailed execution contract lives
in `CODEX_WORKFLOW.md`. When Codex runs a pipeline command, it uses the local
`openai-codex` SDK and your existing `codex login` session—never an API key.

## What stays deterministic

Python remains the coordinator and deterministic support layer. It validates
briefs, models durable data, and retains scoring, QA gates, append-only
history, and ad-eligibility logic. Each contextual stage runs in its own
read-only Codex SDK thread: planning, hooks, writing, visual direction, and QA.

```bash
python -m pip install -r requirements.txt
python cli.py check briefs/example_production_ai.yaml
python -m pytest tests -q
```

Run these commands from Codex's terminal or ask Codex to run them for you. They
preserve the original functionality, but every model stage is now Codex SDK
backed and uses ChatGPT-plan authentication:

| Command | Purpose |
|---|---|
| `python cli.py doctor` | Validate config, database, and the local Codex login. |
| `python cli.py produce <brief-id>` | Run brief strategist → hooks → writer → thumbnail + visual planner → QA, then export a complete package. |
| `python cli.py produce-approved` | Produce the approved brief backlog through Codex SDK. |
| `python cli.py attach-assets <package-dir> <source-dir>` | Copy completed ChatGPT-UI renders into the package’s `assets/` folder by filename. |
| `python cli.py simulate-validators` | Run the named adversarial story and asset-validation suite; compare expected versus observed verdicts. |
| `python cli.py discover`, `score`, `plan`, `weekly` | Run the original coordinated discovery and planning workflows through Codex SDK. |
| `python cli.py create-brief "Topic" --format carousel` | Create a human-editable brief template. |

## Content workflow

```text
human-approved brief
  -> Codex execution plan
  -> hooks + Reel/carousel package
  -> thumbnail + visual plan
  -> exported caption and asset handoff
  -> QA report against deterministic gates
  -> human review
```

The six immutable brief fields are topic, core thesis, learning objective,
format, brand pillar, and high-level sections. Codex may improve execution, but
must flag conflicts instead of silently changing the strategy.

## Project map

```text
AGENTS.md              Codex rules for this workspace
CODEX_WORKFLOW.md      Content-production procedure and output contract
briefs/                Human-authored source briefs
outputs/               Codex-generated, human-reviewable content packages
config/brand.yaml      Brand positioning, pillars, voice, audiences
config/scoring.yaml    Deterministic scores, QA gates, and approval thresholds
prompts/               Versioned execution reference material
content_os/            Pydantic models, storage, deterministic tools, legacy API code
tests/                 Deterministic safeguards
HANDOFF.md             Product decisions and current operating state
```

## How coordination works

The existing workflow code remains the orchestrator. For every named stage it:

1. Loads the stage's versioned prompt and model routing from `config/models.yaml`.
2. Starts a read-only, ephemeral Codex SDK thread with the active ChatGPT login.
3. Supplies the Pydantic model's JSON Schema as `output_schema`.
4. Validates the response in Python, records the Codex thread ID and token usage
   in `agent_runs`, then passes the validated object to the next stage.

That keeps the intentional sequence intact—for example, the writer receives the
approved brief and selected hooks, while the visual planner receives finished
copy. Codex threads can be resumed by the SDK if a future workflow needs a
multi-turn specialist; the current stages are isolated by default so one role
cannot overwrite another's context.

## SDK and legacy API code

`openai-codex` is the active runner and exposes Codex threads, turns, sandbox
selection, structured outputs, token usage, and resumable sessions. The
`openai-agents` dependency remains available for compatibility and optional
SDK functionality, but its API-key `Runner` is not invoked. `config/models.yaml`
routes Codex SDK stages to their selected Codex models and prompt versions; its
pricing block is historical only because ChatGPT-plan usage is not API-priced.
