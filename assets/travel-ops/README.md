# Travel-operations visual kit — v1

First-pass generated assets for the illustrative multi-agent travel-assistant
carousel. These represent a fictional system with simulated data; do not imply
that any airline or travel company uses this exact architecture.

Exact prompts and the rejection rationale are in [prompts-v1.md](prompts-v1.md).

| Asset | Intended slide/use | Generation brief |
|---|---|---|
| `01-cancelled-flight-cover-v1.png` | Cover / title slide | Cinematic airport disruption; traveller, red cancelled-flight state, phone-based travel assistant, empty left-side space for copy. |
| `02-agent-trace-console-v1.png` | “How agents and tools work” slide / screen-recording backdrop | Dark travel-operations console showing a passenger case, staged agent trace, tool calls, workflow rail, and human-escalation branch. |
| `03-multi-agent-architecture-v1.png` | Full-architecture slide | Visual hierarchy: cancellation → orchestrator → three specialist agents → tools → workflow → success or human escalation. |

## Production notes

- Add all carousel labels and title copy in Figma/Canva; the images intentionally
  contain icons and structure rather than AI-rendered text.
- Keep the dark-navy base, cyan orchestration, violet specialist agents, teal
  tools, amber workflow, and red escalation colour language consistent.
- Use `02` as the visual reference for a later screen recording or clickable
  prototype. Show synthetic data and label the demo clearly.
- Regenerate as a new `v2` sibling; do not overwrite this first pass.
