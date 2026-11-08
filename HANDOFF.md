# Handoff: Content OS

## Current operating model

Content OS is now operated through **Codex with ChatGPT authentication**. It is
not a standalone API-backed agent application and does not require
`OPENAI_API_KEY`. Codex reads `AGENTS.md` and follows `CODEX_WORKFLOW.md` to
turn a human-approved brief into a reviewable Markdown package in `outputs/`.

The Python workflows remain the coordinator. Their stage runner now uses the
`openai-codex` SDK, which starts read-only Codex threads with the user's saved
ChatGPT login, validates Pydantic structured output, and records each thread ID
and token usage locally. `openai-agents` remains installed but its API-key
`Runner` is not used.

## Product principle

**Human decides WHAT and WHY. Codex decides HOW. Python remains deterministic.**

## Strategic direction approved 30 September 2026

The public brand now has two strategic initiatives:

1. **Agents, End to End** is the dominant initiative and intended one-stop
   learning system for agents. It covers LLM foundations through the agentic
   lens, tools, workflows, context, state, memory, retrieval, planning,
   orchestration, protocols, evaluations, guardrails, observability, security,
   deployment and production economics through demos, videos, traces, papers
   and recorded results.
2. **Become AI-Native: Career & Leadership** is the differentiated career-
   coaching and leadership initiative covering judgement, human-agent teams,
   workflow redesign, hiring, portfolios, careers and organisational adoption.

On 3 October 2026, the creator approved **Your Role, Rebuilt** as the recurring
practitioner playbook inside Become AI-Native. Layoff anxiety is the acquisition
hook, not the long-term editorial product. Each functional episode uses the
same action-oriented **CRISP** mitigation contract: Compress commodity work,
Reskill into adjacent capabilities, Integrate around an outcome end to end,
Safeguard the system and Prove
outcomes.
CRISP is a resilience and evidence-building framework, never a job-security
guarantee. Every episode begins with the same broad layoff-anxiety
beat and then moves immediately into Sagar's personal or role-specific story.
The current Microsoft/PayPal/20%-by-2027 opener remains `NEEDS VALIDATION` until
the creator approves the source. Test
one function at a time; the creator-approved follower-acquisition scan is Data
Science, Product, SDE and Marketing. MLE remains a specialist extension of the
Data Science lane rather than a separate first-cycle candidate. The controlled
plan and scale gates are in
`planning/ai-native-role-rebuilt-experimentation-plan-2026-10-03.md`.

`ai_real_life` remains an internal planning pillar for compatibility, but its
builds are demonstration environments inside the agents initiative rather than
a third public promise. The operating mix is 50% core agents, 30% AI-native
career and leadership, and 20% real-life agent demos. Be agentic-forward:
interpret new models, papers and LLM concepts through plausible future agent use
cases, but label demonstrated evidence, prototypes and informed hypotheses
separately. The catalogue should quietly build reusable intellectual property
and demand for a future agents course, community, coaching, workshops and
advisory without implying that any offering is currently available. The
detailed operating model is in
`planning/two-theme-agent-authority-strategy-2026-09-30.md`.

Every post or Reel now teaches exactly one primary transferable concept. A gym
build, personal image, demo or story may make that concept concrete, but it must
not introduce a second lesson. Related ideas become linked follow-up episodes in
the series.

The canonical topic system for this work is
`planning/agent-series-roadmap-2026-09-30.md`. Every Agent Series post must map
to exactly one roadmap topic ID. Weekly themes change the teaching environment,
not the curriculum; the current requested environment is the Gym Assistant.
New papers, repositories and capabilities enter as frontier attachments to the
durable concept and system decision they change.

Publishing priority is frontier-first. The stable roadmap remains ordered for
learning, while its dynamic priority queue is refreshed weekly from primary
sources: newest consequential development first, then the prerequisite older
concept, then its production implication. Recency does not override brand fit,
evidence labels or the one-concept-per-post rule.

For the current recurring Agent Series format, use the **Biceps Progression
Agent** as the default demonstration environment. Lead with an evidenced,
outcome-driven biceps-building story, then go technically deep on exactly one
roadmap concept. The content should be useful before an agent-system interview:
show the relevant objective, input/state contract, structured decision,
execution boundary and stop/failure condition. Biceps carousels use five
image-led teaching slides with truthful chronological personal imagery—
before/current on the cover, older images for system setup and earlier stages,
newer images for the closed loop and outcome—followed by a sixth dedicated CTA
slide when needed.
Claims that AI ensured weekly physical progress require the creator's supporting
logs or measurements; otherwise use evidence-safe wording.

Start every future Agent Series Reel or carousel plan by defining a checkable
viewer learning payoff—what the audience can identify, explain, decide or design
after watching—before choosing hooks, story flow or visuals. Make that promise
clear in the opening. Use a light editorial visual system for the Biceps
Progression Agent: warm off-white/pale stone, charcoal type, restrained blue
lines and one muted lime highlight. The FND-02 sixth slide uses only: “Want to
share your learnings—or need help building agents for yourself? Reach out
below,” followed by the website URL.

The Agent Series should compound into a one-stop agent interview-preparation
system. Every future piece names one realistic interview question, provides a
concise reusable answer structure, proves it with one applied trace or
architecture example, and identifies the shallow mistake or missing trade-off
that the lesson prevents. These are four treatments of one roadmap concept, not
four separate topics or a memorised-answer script.

Map every technical term to the demonstrated system on the same slide or scene;
do not leave interview vocabulary abstract. For FND-02, use the saved Gym
Assistant contract: the current observation fields are `check_in_complete`,
`recovery_status`, `data_consistency` and `safety_signal`; the bounded actions
are `PROGRESS`, `HOLD`, `ASK_FOR_DATA` and `ESCALATE`. The environment is the
deterministic proposal workflow plus Sagar's real training, and the next weekly
check-in closes the loop. The current fixture does not contain a direct biceps-
progress metric, so that real field and supporting evidence are required before
claiming the system ensured weekly physical progress.

Make every agent trace domain-realistic. For the Biceps Progression Agent, a
route such as `PROGRESS` is insufficient on its own: pair it with the actual
exercise recommendation used by Sagar (for example a real load progression or
programme-specific short-head, long-head or hammer-curl emphasis), a concise
reason code and references to the input fields that caused it. Present this as
an auditable trace—evidence → bounded route → domain payload → rationale →
deterministic update → next observation—not as hidden chain-of-thought or
generic fitness advice. The saved v1 contract contains only the four routes;
the richer recommendation payload must be validated against Sagar's real logs
before being presented as an implemented result.

Never weaken these constraints:

1. `ContentBrief` is authoritative. Its immutable fields are topic,
   `core_thesis`, `learning_objective`, `content_format`, `brand_pillar`, and
   `high_level_sections`.
2. Deterministic scoring and QA gates live in `config/scoring.yaml`; content
   cannot self-approve by prompt alone.
3. Historical repositories are append-only. Preserve old data and database
   files, including the existing `content_os_v3.db` brief data.
4. Do not publish, schedule, spend, or imply approval without a human action.
5. Prompt files are versioned. Copy a version before materially changing it.

## How to work

After every video generation and final export, apply
`feedback/VIDEO_LEARNING_LOOP.md`. The Diwali retrospective is the first
evidence-backed case: its exact hook, complete narration, synchronized tier
graphics and verified delivery now inform brand memory v9 and the versioned
hook, writer, visual and QA prompts. ChatGPT makes still keyframes; Edits owns
the creator-footage cut; invideo or Magnific animate a justified shot after a
credit check. The creator handles fal.ai generations. Do not rerun a posted
video to exercise these tools.

```bash
python -m pip install -r requirements.txt
python cli.py check briefs/example_production_ai.yaml
python -m pytest tests -q
```

Then ask Codex to run the desired `cli.py` workflow or produce a package in the
chat. The coordinated pipeline retains the stage sequence—brief strategist,
hook expander, writer, visual planner, and QA—and passes Pydantic-validated
results between isolated Codex SDK threads. The output must include a brief
fingerprint, execution plan, hook options, complete content, visual plan,
factual checks, and a QA report with an explicit human-review verdict.

## Important context retained from the prior build

- The active execution plan is `planning/release-sprint-to-10-2026-09-28.md`:
  publish at least ten Reels by Sunday 4 October before drawing performance
  conclusions. It changes post timing, not the approved topic order. Treat the
  face-led-plus-proof-stills format as a working hypothesis only; do not name a
  winner or re-plan from individual post performance before the ten-Reel review.

- The fixed, creator-approved Reel execution queue is in
  `planning/fixed-reel-lineup-2026-09-26.md`. Treat it as the source of truth:
  do not rescore, reorder, replace, or auto-schedule its entries without
  explicit creator direction. Blank post dates and outcome fields are `TBD`,
  not missing values to infer.

- On 2 October 2026, the creator explicitly replaced the Netflix GenRec and
  earlier candidate-interview slots. The active three-Reel sequence is now:
  real-life Wardrobe Selector, SkillRL paper deep-dive and an evidence-led tech
  job-loss/readiness Reel for SDE, data and product roles. SkillRL and the career
  Reel have production packages under `outputs/`; Wardrobe remains a real-demo
  build to be completed separately before its proposed Sunday launch. The
  proposed launch sequence and timing hypotheses are in
  `planning/launch-plan-2026-10-04-to-2026-10-08.md` and do not authorize
  publication or scheduling.

- The approved brief in `content_os_v3.db` was never run through the old live
  API path; do not try to revive that path. Export or recreate the brief as YAML
  and run it through Codex instead.
- The old system's strongest safeguards are still valuable: section coverage
  must use strict matching, recently generated content must not compare against
  itself, and brief-derived content needs a linked topic record for analytics.
- Carousel work needs structural variety. Prefer a deliberate structure such as
  a framework breakdown, comparison table, annotated failure, decision tree, or
  before-and-after rather than defaulting to eight uniform slides.
- Factual claims need supplied references or must be flagged for verification;
  do not present unsourced personal measurements as general facts.

## Files to read before changing behavior

- `AGENTS.md`
- `CODEX_WORKFLOW.md`
- `config/brand.yaml`
- `config/scoring.yaml`
- `briefs/example_production_ai.yaml`
- the relevant versioned files in `prompts/`
