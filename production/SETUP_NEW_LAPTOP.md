# Moving Content OS to another Mac

For the current work-to-home migration, read `WORKSTATION_MIGRATION_HANDOFF.md`
first. It lists the personal media and transcripts still needing a verified
private backup. The steps below describe the software setup after that backup.

Edits is a Mac app, so this assumes a Mac. Git carries the code, briefs, feedback and plans. It does
**not** carry the files listed under "Bring across by hand".

## Install

| Tool | Why | How |
|---|---|---|
| Git and GitHub CLI | This repository | `brew install git gh`, then `gh auth login` |
| Claude Code and/or Codex | The agents that run the system | Sign in with the creator's own accounts |
| Python 3 | `cli.py`, tests, scripts | `brew install python`; `python3 -m venv .venv && .venv/bin/pip install -r requirements.txt` |
| Edits (Mac) | The editor | Mac App Store; sign in with the Instagram account that posts |
| ffmpeg | Checks and mastering | `brew install ffmpeg` |
| whisper.cpp | Independent transcript check | `brew install whisper-cpp`, plus the `ggml-small.en.bin` model |
| Google Chrome | Page screenshots and cover rendering | Standard install |

Optional, for a later comparison: DaVinci Resolve.

## Bring across by hand (ignored by Git)

Copy these from the old machine by AirDrop or a drive. Do not put them in the repository.

- `content_os.db`, `content_os_v2.db`, `content_os_v3.db` in the repository root. `AGENTS.md` asks for
  existing databases to be preserved; a fresh clone has none.
- `.env`, only if a workflow still needs it.
- `sites/sagar-agent-authority/` and `demos/workout-hud/app/media/`.
- Raw footage and final exports you want to keep, and any Edits projects (export them from Edits or
  re-create; they live inside the app's library).
- Downloaded music, into `music/`, with a line per track in `music/LICENSES.md`.

## Connect the agent to Edits

1. Open Edits, go to **Settings > Automation**, copy the access token.
2. `launchctl setenv METAPILOT_TOKEN <token>`, and add `export METAPILOT_TOKEN=<token>` to `~/.zshrc`.
   Never commit it.
3. Claude Code:
   `claude mcp add --scope user --transport http edits http://127.0.0.1:19501/mcp --header 'Authorization: Bearer ${METAPILOT_TOKEN}'`
   (single quotes, so the config stores the variable name and not the token). Codex: the
   `metapilot-native` server entry with `bearer_token_env_var = "METAPILOT_TOKEN"`.
4. Start the agent with Edits already open. If the tools are missing, `scripts/edits/mcp.py` reaches
   the same server directly.

Edits reads media only from a few places: `~/Movies` and its own container
(`~/Library/Containers/com.burbn.basel.mac/Data/Documents/`). See
`.agents/skills/reel-footage-edit/references/edits-automation.md`.

## Check

```bash
.venv/bin/python -m pytest tests -q
python3 scripts/edits/mcp.py list | head     # prints Edits tools if the app and token are right
python3 scripts/edits/mcp.py appState
ffmpeg -version | head -1
whisper-cli -h | head -1
```

Then open the agent in this folder and say: "Read CURRENT_REEL_CONTEXT.md and
planning/reel-production-system-blueprint-2026-11-15.md, then continue with the build order."
