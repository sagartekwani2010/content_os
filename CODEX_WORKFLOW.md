# Content production workflow

Use this workflow when the user asks Codex to produce a Reel, carousel, or
trial Reel from a brief. Codex is the creative executor; no API-backed agent
workflow is involved.

## Inputs

Read these before drafting:

1. The requested file in `briefs/`.
2. `config/brand.yaml` for voice, pillars, and audience.
3. `config/scoring.yaml` for the non-negotiable QA gates.
4. The matching files in `prompts/`:
   `brief_strategist_v1.md`, `hook_expander_v2.md`, the current format writer,
   `story_judge_v1.md`, `visual_planner_v4.md`, and `qa_v4.md`.

Treat the brief as authoritative. The following are immutable: `topic`,
`core_thesis`, `learning_objective`, `content_format`, `brand_pillar`, and
every item in `high_level_sections`.

When teaching an architecture, use a concrete, relatable request and trace it
through specialist responsibilities, tool calls, deterministic workflows, and
the final user outcome. Do not present an illustrative brand scenario as a
claim about that company's actual internal implementation.

Apply the approved Content Learning Memory in `config/brand.yaml`. In practice,
this means teaching a usable decision rule, compressing setup, using one idea
per visual, making orchestration and execution visible, including the relevant
guardrail or failure path, and connecting the design to an outcome. Avoid
generic AI visuals, dense simulated dashboards and unsupported metrics.

## Deliverable

Create `outputs/<title>-<content-id>/` containing, in order:

1. **Brief fingerprint** — repeat the immutable fields verbatim.
2. **Execution plan** — opening, narrative arc, learning points, examples,
   visual beats, closing, coverage map, risks, and factual checks.
3. **Hook options** — three to five options inside the approved hook territory;
   identify the selected hook and why it is the strongest.
4. **Content package** — the complete carousel or Reel, matching the requested
   format and size. A carousel must specify each slide; a Reel must specify the
   spoken script, on-screen copy, timing and a paste-ready caption.
5. **Thumbnail + visual plan** — a separate, complete thumbnail prompt and an
   executable visual/shot direction for every slide or scene. Every asset has a
   filename, ChatGPT-UI-ready prompt and a slot in `assets/`.
6. **QA report** — score each configured dimension from 0–10, calculate the
   configured weighted composite, list every failed hard gate, check section
   coverage, and give an explicit `READY_FOR_HUMAN_REVIEW` or `REVISE` verdict.

If a factual claim cannot be supported by the brief's references or supplied
source material, put it under **Factual checks** and avoid presenting it as
established fact. If the brief is incomplete or internally contradictory, stop
and request human direction instead of inventing strategy.

## Human control boundaries

- Do not publish, schedule, buy ads, or imply that content is approved.
- Do not substitute a better-sounding thesis or different format.
- Do not convert optional discovery suggestions into production work without a
  human-approved brief.
- Preserve all rejected drafts and their QA findings in the output artifact.
- After a human revises a published piece, capture the before/after and the
  reason with `feedback/POST_REVIEW_TEMPLATE.md`. Do not promote a speculative
  preference to long-term memory without repeated evidence or explicit approval.

## Package files

Every production run exports `caption.txt`, `package.json`,
`asset-manifest.json`, `ASSET_PROMPTS.md`, individual prompts under
`asset-prompts/`, and an `assets/` folder. Render each prompt in the ChatGPT UI
when that is the creator's preferred quality surface, save it with its assigned
manifest filename, then run:

```bash
python cli.py attach-assets outputs/<package-dir> <downloads-directory>
```

This copies the completed thumbnail and media into the package without changing
the source downloads.

## Recorded-footage edit

After the creator records, follow `.agents/skills/reel-footage-edit/SKILL.md`.
The production package is a guide, while the creator's current instructions
and recorded speech determine the actual cut. Keep a source-timecode map,
take-selection rationale, and editable project alongside the finished export.
Place B-roll only after the narration cut is stable. Verify subtitles, mix,
and platform encoding on the rendered file before handoff.

After each video generation and final export, run
`feedback/VIDEO_LEARNING_LOOP.md`: record the actual result and creator
feedback, keep rejected generations, and promote only evidenced rules into
brand memory and new prompt versions. Use a posted video as retrospective
evidence without spending credits to remake it.
