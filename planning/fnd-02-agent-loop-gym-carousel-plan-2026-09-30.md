# FND-02 — The Agent Loop: Gym Assistant carousel plan

## Status

`STORY_FLOW_FOR_HUMAN_APPROVAL`

This is a planning artefact only. It does not yet approve final slide copy,
visual generation or publication.

## Roadmap mapping

- **Series:** Agent Series
- **Roadmap topic:** `FND-02 — The Agent Loop`
- **Teaching environment:** Biceps Progression Agent (Gym Assistant)
- **Format:** Instagram carousel, 6 slides at 4:5: five educational,
  image-led slides plus one dedicated contact slide
- **Evidence label:** `PROTOTYPE` until a real end-to-end run is captured
- **Single viewer question:** How did an agentic loop help Sagar run a repeatable
  weekly system for biceps progression?
- **Single takeaway:** An agent repeatedly observes the latest state, decides
  the next action, acts, and uses the result as its next observation.
- **Viewer learning payoff:** After viewing, a person can draw and explain a
  closed agent loop in an interview: define its goal, observation schema,
  decision policy, bounded action, environment transition and stopping
  condition, then determine whether a proposed system genuinely closes the
  loop.
- **Likely interview question:** What is an agent loop, and how would you design
  one for a real system?
- **Common interview mistake:** Describing `user prompt → model response` or
  `prompt → generated plan` as a complete agent loop without a new observation,
  bounded action or stop condition.
- **Adjacent topics, not taught here:** `FND-01`, `MEM-02`, `PLN-03`, `REL-02`

## Creative theme

### Working title

Creator-approved outcome theme:

> **How I ensured my biceps progressed every week using agentic principles.**

Use the exact claim only if the creator's weekly training/progression evidence
supports it. Otherwise publish the evidence-safe version:

> **How I used an agentic loop to drive my weekly biceps progression.**
>
> *Deep dive: the agent loop inside it.*

### Cover direction

Use a real before/current biceps comparison as the attention anchor with the
evidence-appropriate version of:

> **How I used agentic principles to progress my biceps every week.**
>
> `Learn how an agent uses feedback to choose its next action—and how to tell whether the loop is genuinely closed.`

This leads with the outcome, frames the carousel as a system-build story and
then narrows into one technical concept. The creator still did the training;
the prototype organised the feedback-and-decision loop. Do not imply that AI
directly caused muscle growth or guaranteed a physiological result.

### Narrative idea

Sagar first shows the biceps-specific operating contract passed into the
system: his verified objective, weekly training evidence, progression rule,
practical constraints, allowed next moves and safety boundary. Those same
guidelines remain visible while the system observes, decides, acts and observes
again. The carousel then reveals that repeated mechanism as the agent loop.

The guidelines are implementation context, not additional concepts to teach.
The deep dive remains `FND-02`.

### Gym operating contract to show

Use the creator's real versions of these fields; do not invent values or turn
them into general fitness advice:

1. **Goal `G`** — the creator's verified biceps-progression objective.
2. **Observation schema `O`** — the real weekly fields available to the system,
   such as completed sessions, the tracked progression signal, recovery input
   and current constraints.
3. **Decision policy `π`** — the rule/model boundary that maps the observation,
   goal and constraints to one next decision.
4. **Bounded action space `A`** — the real prototype contract, such as
   `PROGRESS`, `HOLD`, `ASK_FOR_DATA` or `ESCALATE`.
5. **Environment transition `E`** — the deterministic update and human training
   activity that produce the next week's state.
6. **Stop condition `τ`** — missing evidence, pain, injury or medical judgement
   stops the automated loop and transfers control to a human/professional.

Show a compact `LOOP CONTRACT` rail on slides 2–4. Translate every symbol into
plain language on first use; notation should compress the idea, not make it
look artificially complex.

Recommended formal trace:

> `oₜ + G + constraints → π → aₜ → E → oₜ₊₁`

Where `oₜ` is this week's observation, `π` selects one bounded action `aₜ`, the
environment/workflow `E` applies it, and `oₜ₊₁` is the next observation.

### Exact mapping to the current Gym Assistant setup

Use these concrete call-outs next to the technical terms everywhere they appear:

| Technical term | Meaning in this carousel | Current implementation evidence |
|---|---|---|
| Goal `G` | Improve Sagar's biceps through repeatable weekly progression decisions. | Creator-approved goal. The exact outcome metric still needs to be supplied from the creator's real tracking. |
| Observation `oₜ` | The current normalised weekly check-in presented to the decision layer. | `check_in_complete`, `recovery_status`, `data_consistency`, `safety_signal`. |
| Decision policy `π` | The bounded decision layer chooses exactly one route from the validated state; deterministic code checks schema and safety boundaries before execution. | Complete + normal + consistent + no safety signal → `PROGRESS`; recovery concern → `HOLD`; missing or conflicting evidence → `ASK_FOR_DATA`; pain/injury → `ESCALATE`. |
| Bounded action `aₜ` | The only decisions the agent is allowed to return. | `PROGRESS`, `HOLD`, `ASK_FOR_DATA`, `ESCALATE`. |
| Environment transition `E` | A deterministic workflow converts the selected route into a constrained next-week proposal; Sagar performs the real training. | Existing workflow boundary from the Gym Assistant design; the agent does not perform the workout. |
| Next observation `oₜ₊₁` | The next weekly check-in after Sagar has followed—or not followed—the proposal. | Required to close the loop; use a real subsequent check-in or label the continuation as a prototype. |
| Stop condition `τ` | The loop must not automatically progress when evidence is missing, conflicting or crosses the pain/injury boundary. | `ASK_FOR_DATA` pauses for evidence; `ESCALATE` requires human review and blocks automated progression. |

Do not show a symbol without its concrete Gym Assistant meaning on the same
slide. The audience should learn the general term and see its instantiated value
in one glance.

### Evidence gap to close before production

The current saved fixture contract validates routing, abstention and escalation,
but it does not contain a direct biceps-progress measure. Before using “ensured
my biceps progressed every week,” add the real signal Sagar actually tracked to
the observation schema—for example the creator's real load/repetition,
measurement or other logged progression field. Do not choose or fabricate that
metric in planning.

Until that evidence is supplied, the truthful system claim is:

> **I used an agentic loop to manage my weekly biceps-progression decisions.**

### Domain recommendation layer

The existing saved contract stops at the route level: `PROGRESS`, `HOLD`,
`ASK_FOR_DATA` or `ESCALATE`. For the carousel to feel like a genuine biceps
system, a safe `PROGRESS` or `HOLD` route should expand into a concrete,
domain-specific recommendation drawn from Sagar's actual programme and logs.

Use a versioned recommendation object such as:

```text
route: PROGRESS
recommendations:
  - action: INCREASE_LOAD
    target: [real exercise from Sagar's programme]
    reason_code: TARGET_REPS_MET
    evidence_refs: [real logged fields]
  - action: REBALANCE_EXERCISE_FOCUS
    target: SHORT_HEAD
    exercise: [real short-head exercise used by Sagar]
    reason_code: BELOW_CONFIGURED_ALLOCATION
    evidence_refs: [real weekly allocation fields]
  - action: REBALANCE_EXERCISE_FOCUS
    target: LONG_HEAD
    exercise: [real long-head exercise used by Sagar]
    reason_code: BELOW_CONFIGURED_ALLOCATION
    evidence_refs: [real weekly allocation fields]
  - action: EMPHASISE_HAMMER_CURL
    reason_code: NEUTRAL_GRIP_WORK_BELOW_CONFIGURED_TARGET
    evidence_refs: [real weekly allocation fields]
needs_human_review: false
```

These are candidate action types based on the creator's direction, not generic
fitness prescriptions. Replace every placeholder with the actual exercise,
programme rule and logged evidence used by Sagar. Do not claim that a specific
exercise targets a particular anatomical outcome unless that rationale is part
of the creator's real programme and is factually supported.

If the route is `ASK_FOR_DATA` or `ESCALATE`, the system must not emit an
exercise-change recommendation. If the route is `HOLD`, any output should
explain what remains unchanged and which observed evidence caused the hold.

### What “reasoning” means on screen

Show an auditable recommendation trace, not private chain-of-thought:

> **observed evidence → route → domain recommendation → reason code → applied
> change → next observation**

Each reason must point back to visible input evidence. Good: “Increase load
because the configured rep target was met in the supplied log and recovery was
normal.” Weak: “The AI thinks heavier weight will work better.”

This distinction is interview-relevant: production agents should expose
structured decisions, evidence references and concise rationales without
depending on unverifiable free-form reasoning.

### Visual language

- Use a light editorial system throughout: warm off-white or very pale stone
  background, charcoal typography, restrained electric-blue system lines and
  one muted lime highlight for the selected decision.
- Avoid dark dashboard styling, neon, gradients, glossy fitness-ad treatment or
  dense technical UI.
- Use five real progress images across the five educational slides—one
  image-led composition per slide—not five separate photos crowded onto each
  slide. Slide 6 is a dedicated light contact card and does not need another
  progress photo.
- Slide 1 uses the strongest before/current comparison.
- Slides 2–3 use older or earlier-stage biceps imagery while explaining the
  system definition and initial loop stages.
- Slides 4–5 use newer imagery while showing the closed loop and outcome.
- Preserve chronological truth; do not reorder photos to exaggerate progress.
- Real human photos only; no generated physique, AI avatar, robot or generic
  fitness-ad aesthetic.
- Large labels: `OBSERVE + DECIDE` and `ACT + OBSERVE AGAIN`.
- Two paired steps per mechanism slide, with one left-to-right visual path.
- A compact `LOOP CONTRACT` rail remains visually consistent on slides 2–4.
- No dense app screens or multi-agent diagram.
- A single line should physically continue across slides and close into a loop
  on slide 4.

## Recommended story flow

The lines below are directional, not final publish copy.

| Slide | Job in the story | What the viewer sees | Information added |
|---|---|---|---|
| 1 | Lead with outcome + learning promise | Real before/current biceps comparison. Call out `Goal G = improve my biceps through weekly progression decisions`, use the evidence-safe hook, promise `Learn how feedback becomes the next agent action`, and add a small `AGENT SERIES / FND-02` marker. | The personal outcome earns attention; the audience immediately sees the general goal term and its concrete use-case value. |
| 2 | Replace the common interview mistake with the instantiated system contract | Older biceps image. First show `prompt → plan → stop`; then reveal `oₜ + G + constraints → π → aₜ → E → oₜ₊₁`. Under every symbol, render the concrete mapping: weekly check-in, biceps goal, bounded router, four permitted decisions, deterministic update + human training, next check-in. | A closed loop is a set of explicit contracts, and each abstract component has a real responsibility in this system. |
| 3 | Show two steps: `OBSERVE + DECIDE` | Earlier-stage image plus the actual current observation schema: `check_in_complete`, `recovery_status`, `data_consistency`, `safety_signal`, the real progression metric and exercise-allocation fields once supplied. Label `Decision policy π` with the route table. Show `Bounded action aₜ = PROGRESS`, followed by one or more structured domain recommendations such as increase load, emphasise the configured short-head or long-head exercise, or emphasise hammer curls. Each recommendation shows a reason code and evidence reference. | The viewer sees exactly what the policy received, which route it selected, what that route meant in the biceps domain and why the recommendation followed from the supplied evidence. |
| 4 | Show two steps: `ACT + OBSERVE AGAIN` | Newer biceps image. Continue the same agent trace: `approved recommendation → deterministic next-week proposal update → Sagar performs training → next check-in oₜ₊₁`. Display the human-readable rationale beside the applied change. Show `Stop τ`: missing/conflicting evidence emits no exercise change; pain/injury escalates to human review. | The recommendation becomes a real domain action, its rationale remains auditable, and new evidence returns or the loop stops safely. |
| 5 | Deliver the mapped interview-answer sequence | Current biceps image plus a seven-step answer structure: goal → observation → policy → actions → execution → feedback → stop. End with the full notation and `Then prove it with one real trace.` No CTA. | The viewer can structure a strong agent system-design answer and ground every abstract component in one demonstrated system. |
| 6 | Invite contact | Clean light-background contact card with generous whitespace and the website URL; optional small current portrait, but no new technical content | People who want to share learnings or need help building agents know where to reach Sagar. |

## Interview-ready technical depth

The carousel must be useful immediately before an agent-system interview. It
should make these implementation details visible without introducing a second
concept:

- **Goal `G`:** the outcome the loop is trying to advance.
- **Observation `oₜ`:** the exact evidence available for the current decision.
- **Decision policy `π`:** the model/rule boundary selecting the next action.
- **Action `aₜ`:** one structured output from the bounded action space.
- **Environment `E`:** the workflow and human activity that change reality.
- **Next observation `oₜ₊₁`:** evidence of what happened after the action.
- **Stop condition `τ`:** when the loop must stop or escalate instead of guess.

Recommended interview formulation for slide 5:

> **An agent loop is a state-transition cycle where the system observes the
> current environment, selects a bounded action, executes it, and uses the
> resulting state as evidence for the next decision.**

This is technical depth in service of `FND-02`; do not expand into separate
lessons on memory, evals, tool design or guardrail architecture.

Add this production-level interview distinction:

> **The route is the bounded agent decision. The exercise recommendation is the
> domain payload. The reason codes and evidence references make the trace
> auditable. A deterministic workflow applies the approved change.**

### Seven-step interview-answer sequence for slide 5

1. **Goal** — what outcome should change?
2. **Observation** — what evidence enters?
3. **Policy** — what chooses the next step?
4. **Actions** — what is the system allowed to do?
5. **Execution** — what changes reality?
6. **Feedback** — what returns as new evidence?
7. **Stop** — when should the loop pause or escalate?

Then prove the answer with one real trace. If a candidate cannot walk through
this sequence, the proposed “agent” is probably still a prompt-and-response demo
rather than a designed closed loop.

## Why this sequence teaches better

1. **Outcome before abstraction:** the biceps progression earns attention and
   gives the formal loop a concrete purpose.
2. **Whole before parts:** slide 2 shows the complete contract before slides 3
   and 4 unpack the two paired transitions.
3. **One real trace:** the audience sees data become a structured decision,
   then an action and a new observation.
4. **System boundaries stay visible:** the agent selects the action; a
   deterministic workflow applies it; the human performs the training.
5. **Transfer is tested:** slide 5 asks questions the viewer can reuse in an
   interview or architecture review.

## Execution trace to capture

Use one genuine prototype run compressed across slides 3 and 4:

1. a redacted weekly check-in enters with the real system guidelines;
2. the system chooses one allowed route;
3. a domain recommendation names the actual exercise adjustment and cites the
   observed evidence that caused it;
4. the deterministic workflow updates the next-week proposal;
5. the following check-in becomes the next observation under the same
   guidelines.

The trace proves the loop. It should not branch into separate explanations of
state, memory, tools, replanning, evaluation or guardrails.

Use the saved Gym Assistant contract as the source of truth for the route names
and normalised fields. Do not silently add a progress metric until the creator
provides the real one used during the biceps progression period.

## Closing and response channel

Slide 5 closes the lesson:

> **If your system cannot observe after acting, it doesn't yet have a closed agent loop.**

Slide 6 is the only CTA:
>
> **Want to share your learnings—or need help building agents for yourself?**  
> **Reach out below:**  
> **sagar-agents.saggy-2010.chatgpt.site**

Do not add a DM keyword, comment prompt, follow request or second CTA.

## Caption direction

Keep the caption short because the carousel carries the teaching:

1. clarify that this is a personal Gym Assistant prototype, not fitness advice;
2. restate that a generated plan is an output, while an agent loop uses outcomes
   as new observations;
3. direct collaboration interest to the website.

Do not claim that the assistant built the physique, improved health, prevented
injury or caused an unverified fitness result.

## Assets required before production

- a truthful before/current pair and three additional chronological biceps
  images suitable for the five educational slides;
- the actual goal, evidence fields, constraints, allowed moves and safety
  boundary used in the prototype;
- the exact biceps-progress signal actually tracked, including its real field
  name and one redacted weekly value pair if the outcome claim will be used;
- one real, redacted weekly check-in;
- one real decision/output from the prototype;
- the real exercise recommendation attached to that decision, its concise
  rationale/reason code and the log fields that support it;
- one subsequent check-in or clearly labelled prototype continuation that
  demonstrates the return path;
- confirmation that `PROTOTYPE` is the correct evidence label.

## Test hypothesis and measures

### Hypothesis

An evidenced biceps-progression outcome can earn attention, while an
interview-ready closed-loop explanation converts that attention into
agent-learning interest.

### Primary signals

- carousel completion or final-slide reach;
- evidence that viewers can restate or correctly apply the four-part loop;
- saves per reach;
- qualified collaboration enquiries;
- profile visits and bio-link activity from the post.

Fitness-only likes without saves, completion or agent-related responses do not
validate the teaching format.

## Scope protection

Reject any draft that attempts to additionally teach:

- agent versus workflow as a full comparison;
- state versus memory;
- planning or replanning;
- tool contracts;
- evaluation methodology;
- guardrails or human escalation.

Those remain linked future episodes. This carousel teaches only the closed
observe → decide → act → observe-again loop.
