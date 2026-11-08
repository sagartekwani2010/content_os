# Content OS media production structure

| Stage | Source | Deliverable | Primary tool |
|---|---|---|---|
| Strategy | Approved brief, brand guidance, creator feedback | Script and beat checklist | Content OS workflow |
| Footage selection | Original takes | Timecoded take log with chosen and rejected reasons | Edits MCP inspection |
| Narration edit | Selected takes | Complete 1× cut, then approved pace version | Edits MCP timeline |
| Visual edit | Locked speech, approved assets | Timed 9:16 B-roll, charts, and labels | Edits MCP; InVideo MCP for needed generated shots |
| Finish | Final visual timeline | Captions, music mix, editable project | Edits MCP |
| Delivery | Rendered export | Compatible video and QA report | Edits export and `content_os.tools.video_delivery` metadata/decode check |

## Repo layout and boundaries

- `AGENTS.md` routes recorded-footage requests to `.agents/skills/reel-footage-edit/SKILL.md`.
- `CODEX_WORKFLOW.md` handles the package-to-filming handoff.
- The skill holds the reusable method; its `references/media-tools.md` holds tool routing and export requirements.
- `feedback/` holds verified creator corrections. Operational defaults, such as removing dead air and distracting gaze, belong in the edit skill. An experimental aesthetic choice does not enter `config/brand.yaml` without approval or repeated evidence.
- `planning/` records tool decisions. Media credentials stay in the host's secret store, never in this repo.

## Connected MCP services

- **Edits:** local Automation Server at `127.0.0.1:19501/mcp`. Primary for transcription, pause and quiet-point detection, frame review, timeline editing, captions, audio, preview, and export.
- **InVideo:** official remote MCP with OAuth. Use for specific generated B-roll or browser NLE work. State the exact narrated beat, vertical aspect, shot duration, and visual constraints.
- **Magnific:** official remote MCP with OAuth. Use selectively for covers or visuals whose detail matters. Check balance and action price first; MCP generation/upscaling consumes credits even when a web plan has unlimited operations.

Keep an exact source map and editable project so later comments produce small, precise revisions. Do not spend generation credits merely to exhaust an allowance; first choose assets that improve comprehension.
