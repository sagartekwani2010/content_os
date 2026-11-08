# Why AI demos fail in production — experiment-led carousel

## Brief fingerprint

- **Topic:** Why AI demos fail in production
- **Core thesis:** A prompt plus a fluent model proves a happy path; a production
  AI system must preserve state and protect the user when tools, policies or
  assumptions fail.
- **Learning objective:** The viewer can explain the difference between a demo
  and a production system, and name the minimum failure-path test to run.
- **Format:** 7-slide mixed-media Instagram carousel (4 image slides + 3 video
  slides)
- **Pillar:** AI Builder / Production AI
- **Illustrative scenario:** a fictional food-delivery support assistant

## Execution plan

The experiment changes exactly one variable across three clips: the same
customer question, then a working tool, then a tool timeout, then a guardrail.
The carousel does not claim this ran at a real company or achieved a measured
business result. It challenges the familiar “the demo worked” narrative by
making the failure visible.

Learning payoff: readers can run a minimum production test: **what does the
system do when the next tool call fails?**

Save reason: a compact checklist for reviewing an AI prototype before calling
it production-ready.

Share reason: it gives builders and interview candidates a crisp way to explain
why an impressive demo is not a reliable system.

## Hook options

1. **A working AI demo is not proof that you built a system.** ← selected
2. Your AI demo passed because nothing went wrong.
3. The question that separates an AI demo from production: “What fails next?”

## Content package

### Slide 1 — Static cover

**Copy**

> A working AI demo is not proof that you built a system.  
> Run this one failure test.

**Visual:** real photo of Sagar on a dark, clean background. One small amber
label: `EXPERIMENT: SAME REQUEST, 3 CONDITIONS`.

### Slide 2 — Video 1: Happy path

**On-screen intro:** `TEST 1 — Everything works`

Use the `Happy path` state from `assets/demo-vs-production/demo.html`.

**Overlay:** `Prompt + tool + fluent answer = impressive demo`

### Slide 3 — Static principle

**Copy**

> But the demo only tested the easiest version of reality.  
> The user asked. The tool worked. Nothing conflicted.

**Visual:** one horizontal condition rail, with all three conditions green:
`request understood` · `tool available` · `policy simple`.

### Slide 4 — Video 2: Tool failure

**On-screen intro:** `TEST 2 — Change one thing`

Use the `Tool fails` state from the prototype.

**Overlay:** `Same request. Same agent. Tool timeout.`

### Slide 5 — Static distinction

**Copy**

> A model can still sound helpful when the system has failed.  
> Fluency is not reliability.

**Visual:** two large columns only.

| A demo proves | Production must prove |
|---|---|
| The desired path can happen | The user is protected when it cannot |

### Slide 6 — Video 3: Guardrail

**On-screen intro:** `TEST 3 — Add the system`

Use the `Guardrail` state from the prototype.

**Overlay:** `retry → preserve state → human escalation`

### Slide 7 — Static outcome/checklist

**Copy**

> Before you call it production-ready, break one assumption.  
> Then check: did it preserve context, choose a safe next step, and protect the user?

**Visual:** three oversized checklist items:

- `Context survives`
- `Fallback is defined`
- `Human can take over`

Closing line: `That is the difference between a demo and a system.`

## Video-production plan

- **Ratio:** 4:5 (1080 × 1350) for all slides. Capture the prototype at 9:16,
  then crop its centre safely to 4:5. Keep all core text inside the central 80%.
- **Clip duration:** 2.5–4 seconds each; autoplay muted and looped in the
  carousel. Do not add a voiceover to the clips.
- **Transitions:** use a hard cut from green `PASS` → red `FAIL`, then an amber
  cut to `GUARDED`. The contrast is the experiment.
- **Type:** add only the stated overlay. Do not add animated code, sidebars,
  particle effects or fake dashboards.
- **Integrity label:** retain `Illustrative experiment` in a small corner on
  every video slide.

## Caption

Most AI demos only prove that the happy path is possible.

The production question is simpler: when the next tool call fails, does the
system preserve context and choose a safe next step?

Break one assumption before you call your prototype production-ready.

## Factual checks

- This is a fictional, simulated support-assistant scenario; do not imply a
  Zomato, Swiggy or any other company uses this architecture.
- Do not attach performance, cost, latency or resolution metrics unless they
  are measured for this experiment.

## QA report

| Dimension | Score | Rationale |
|---|---:|---|
| Learning value | 9.0 | One transferable failure-path test and a production checklist. |
| Execution against brief | 9.0 | Challenges demo narrative through an actual controlled visual sequence. |
| Hook strength | 8.5 | Clear, contrarian and defensible. |
| Clarity | 9.0 | One variable changes per clip; static slides interpret the result. |
| Technical accuracy | 8.5 | Distinguishes model fluency from system reliability without false claims. |
| Brand fit | 9.5 | Production-AI practitioner perspective. |
| Originality | 8.5 | The mixed-media failure experiment makes the claim concrete. |
| Visual potential | 9.0 | Video interruption inside a carousel creates a deliberate pattern break. |
| AI hype penalty | 0.5 | Explicit limitations and no inflated impact claims. |
| Generic-content penalty | 1.0 | Uses a built simulation and specific test rather than generic advice. |

**Verdict:** `READY_FOR_HUMAN_REVIEW`

## Sections covered

- Why a prompt-plus-model demo is insufficient
- The production failure path
- State preservation and safe fallback
- Human escalation
- A practical production-readiness test
