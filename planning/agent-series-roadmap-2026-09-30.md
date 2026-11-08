# Agent Series canonical roadmap — 30 September 2026

## Status

Proposed curriculum for creator approval. This is a planning artefact, not
approval to produce or publish every topic below.

## Operating model

The public series is **Agent Series**. It has three independent layers:

1. **Canonical topic** — the durable concept being taught. Every post or Reel
   maps to exactly one topic ID in this document.
2. **Teaching environment** — the relatable system used to explain it. Examples
   include the Gym Assistant, Wardrobe Agent, Content Agent, Travel Agent or a
   work/enterprise agent.
3. **Evidence object** — the real trace, demo, architecture decision, paper,
   benchmark or source that earns the lesson.

A weekly theme changes the teaching environment, not the curriculum. This
prevents the catalogue from becoming either a fitness account or a stream of
disconnected AI news.

## Publishing contract

Before production, every item must declare:

- `roadmap_topic_id`: exactly one canonical ID below;
- `viewer_question`: one question the piece resolves;
- `viewer_learning_payoff`: one checkable sentence stating what the viewer will
  be able to identify, explain, decide or design afterwards;
- `single_takeaway`: one transferable sentence;
- `interview_question`: the realistic agent-system question this piece helps
  the viewer answer;
- `interview_answer_structure`: the concise reasoning structure the viewer can
  reuse without memorising a script;
- `common_interview_mistake`: the specific shallow or incorrect answer this
  piece helps the viewer avoid;
- `teaching_environment`: the current weekly theme;
- `evidence_state`: demonstrated, prototype or informed hypothesis;
- `evidence_object`: what the audience will actually see;
- `adjacent_topic_ids`: prerequisite and follow-up topics, mentioned only as
  links to later episodes rather than taught in the current piece.

Define `viewer_learning_payoff` first. Hooks, outcomes, technical depth, story
structure and visuals must all earn that learning result rather than compete
with it. The published opening should make the learning promise clear without
using generic “today you will learn” language.

Every item must also contain one applied trace or concrete architecture example
that makes its interview answer defensible. The catalogue should become a
one-stop agent interview-preparation system through accumulated concepts,
answer structures, design tests, failure modes and trade-offs—not through
memorised definitions.

If a new model, paper or tool cannot be mapped to a canonical topic and a
changed system decision, it does not become Agent Series content.

## Priority model — frontier first, foundations on demand

The canonical roadmap below is ordered for comprehension, but it is **not the
publishing order**. The active publishing queue is refreshed weekly and gives
priority to the newest consequential agent developments.

Use this order when choosing content:

1. **New this week** — an important paper, model, capability, protocol or
   production result from the previous seven days that changes an agent-system
   decision.
2. **Prerequisite concept** — the single older concept the audience needs in
   order to understand why that development matters.
3. **Production implication** — the evaluation, security, architecture or
   economics decision exposed by the development.
4. **Evergreen gap** — an important canonical topic not yet covered, used when
   no stronger frontier item earns priority.

This is latest-first, not news-first. Recency earns attention only when the
development changes what an agent can do or how one should be built, evaluated
or operated. Vendor announcements without a transferable decision do not enter
the queue.

### Dynamic frontier queue — refreshed weekly

Within each priority tier, order items by source publication/release date when
known. Never invent a date; use `date not stated — verified YYYY-MM-DD` when the
primary source does not expose one.

**Last refreshed:** 2026-11-02  
**Review window:** 2026-10-26 through 2026-11-02

The 2026-10-26 refresh was interrupted before a verified update was saved.
The entries below cover the current seven-day window; earlier records remain
in the historical table. Design recommendations are editorial implications of
the cited evidence, rather than independently validated production results.

| Priority | Development | Source date | Canonical topic | Single transferable concept | Agent-system decision that changes | Evidence state | Primary source |
|---|---|---|---|---|---|---|---|
| 1 | ARTEX and Friends: agentic offensive frameworks observed in intrusions | 2026-10-30 report; observations since late August | `ACT-04` | Automated attack chains amplify the consequences of credentials and execution permissions that span multiple systems. | Isolate agent control planes, use short-lived scoped credentials, segment execution environments and detect suspicious sequences of actions across tools. | **Demonstrated** — GTIG/Mandiant reports observations from incident response and telemetry; underlying incidents are not independently verified here. | [Google threat intelligence report](https://cloud.google.com/blog/topics/threat-intelligence/artex-and-friends-enter-agentic-offensive-frameworks) |
| 2 | When Stored Evidence Stops Being Usable — camera-ready revision | 2026-10-29 v2; original 2026-05-08 | `REL-02` | Test memory with fixed relevant evidence while irrelevant history grows, so usable scale is measured under an explicit interaction budget. | Add growth fixtures and report budget-compliant reliability, tail memory-call burden and the scale at which reliability misses its target for each model/interface pair. | **Prototype** — revised paper evaluation on LongMemEval and LoCoMo; author-reported results, not reproduced here. | [arXiv 2605.07313v2](https://arxiv.org/abs/2605.07313v2) |
| 3 | How AI agents shape experts' judgment calls | 2026-10-27 | `HUM-02` | Human sign-off does not automatically provide an independent judgment when the agent frames the available choices. | For consequential judgment calls, elicit the person's criteria before offering a recommendation and present the strongest alternatives with explicit trade-offs; evaluate whether approval remains independent. | **Demonstrated** — randomized agent-lean study with 50 professional analysts in one task and one model; generalization and proposed interface mitigations remain unproven. | [Anthropic study](https://www.anthropic.com/research/agents-judgment-calls) |
| 4 | Agent Memory as Recommendation | 2026-10-26 | `MEM-06` | Memory selection is a budgeted set-selection problem: the selected context must jointly contain the evidence needed to answer. | Evaluate candidate generation, ranking and final context construction separately; compare complete-evidence coverage and serving cost against direct retrieval before adding LLM-based memory processing. | **Prototype** — AgentMemRec paper results on LongMemEval and LoCoMo; author-reported gains, not independently reproduced here. | [arXiv 2610.34673](https://arxiv.org/abs/2610.34673) |

#### Previous frontier entries retained for continuity

These items remain part of the historical frontier record but are below the
current seven-day queue.

| Development | Source date | Canonical topic | Single transferable concept | Agent-system decision that changes | Evidence state | Primary source |
|---|---|---|---|---|---|---|
| Language Is a Security Surface for Agent Guards | 2026-10-15 | `REL-07` | A guardrail can change its verdict when only the user's language changes, even though the action and trajectory are identical. | Add meaning-preserving multilingual fixtures to guard evaluations, measure verdict flips against the guard's own run-to-run noise and avoid assuming English safety performance transfers across languages. | **Prototype** — paper benchmark covering 1,220 labelled steps and 19 guards; results are author-reported and not independently reproduced here. | [arXiv 2610.22244](https://arxiv.org/abs/2610.22244) |
| GraphACM: action consistency as agent uncertainty | 2026-10-15 | `LLM-06` | Compare actions only at equivalent decision states: disagreement across repeated rollouts can expose uncertainty that verbal confidence misses. | Run repeated fixtures, align equivalent states and use state-conditioned action divergence as an escalation or review signal rather than trusting one trajectory's stated confidence. | **Prototype** — paper experiments across three models and three agent environments; results are author-reported and not independently reproduced here. | [arXiv 2610.22031](https://arxiv.org/abs/2610.22031) |
| OntoAct: hypothesis-based learning through ontological abstraction | 2026-10-15 | `LRN-03` | A reusable lesson needs explicit entity, relation and applicability conditions—not a compressed anecdote from one successful run. | Distil validated experience into typed rules, verify their preconditions against the current observation and update the hypothesis when intervention outcomes contradict it. | **Prototype** — preprint framework and benchmark results; findings are author-reported and not independently reproduced here. | [arXiv 2610.21983](https://arxiv.org/abs/2610.21983) |
| BizBench: long-horizon agents in real-world business procedures | 2026-10-14 | `REL-03` | Final task completion can conceal invalid intermediate actions, policy violations and excessive tool use. | Score goal attainment and every consequential trajectory constraint separately with deterministic checks, including temporal dependencies, prior commitments and conflicting guidance. | **Prototype** — paper benchmark with 50 tasks, 789 knowledge documents and 601 tools; results are author-reported and not independently reproduced here. | [arXiv 2610.20424](https://arxiv.org/abs/2610.20424) |
| CyberArena: live symmetric attack-and-defense agents | 2026-10-13 | `REL-05` | Static, isolated security tests can miss behaviour that emerges when an adversary changes the environment in response to the agent. | Add contained multi-round adversarial fixtures with evolving state, symmetric rules and separate offensive, defensive and domain scores before trusting an agent in contested environments. | **Prototype** — paper benchmark spanning 12 agents, 40 challenges and 466 matches; results are author-reported and not independently reproduced here. | [arXiv 2610.19005](https://arxiv.org/abs/2610.19005) |
| Anthropic report on unintended agent actions in evaluations and internal use | 2026-10-09 | `ACT-04` | Instructions are not a security boundary: tool capabilities must be constrained by infrastructure even when the task says what is out of scope. | Default to contained execution, minimal network access, explicit target and action scopes, automatic blocking and transcript monitoring; require stronger controls before enabling live external actions. | **Demonstrated** — vendor incident report covering observed actions with minimal reported impact; causal intent remains unresolved. | [Anthropic report](https://www.anthropic.com/research/investigating-unintended-model-actions) |
| What to Admit and How to Present: Governing Persistent Memory in LLM Agents | 2026-10-08 | `MEM-06` | Memory relevance is not enough: separately decide whether a recalled item may enter working context and how it is rendered. | Add a deterministic admissibility gate after retrieval, evaluate selection separately from presentation and measure both leakage and loss of useful personalization. | **Prototype** — paper evaluation across four backbones and an external benchmark; results are author-reported and not independently reproduced here. | [arXiv 2610.11188](https://arxiv.org/abs/2610.11188) |
| CheckerBench: long-horizon agents synthesizing static-analysis checkers | 2026-10-06 | `REL-01` | Evaluate an agent's executable artifact in a clean environment instead of trusting its text or self-reported success. | Independently rebuild the output and score functional contrast, localization, false positives and tool use across repeated runs. | **Prototype** — paper benchmark with 300 executable tasks and reported results across 21 model-harness configurations; not independently reproduced here. | [arXiv 2610.07557](https://arxiv.org/abs/2610.07557) |
| Decisions API beta | 2026-10-06 | `PLN-04` | Constrain a routing decision to a finite, predefined action space when open-ended generation is unnecessary. | Use a bounded, typed decision contract for classification, routing or next-action selection; validate quality and latency on the target workflow before replacing a general agent call. | **Vendor claim** — documented beta capability; reported speed and quality are not independently validated here. | [OpenAI API changelog](https://developers.openai.com/api/docs/changelog) |
| Judged Useless, Queried Anyway | 2026-10-05 | `FND-06` | An agent's evidence judgment will not reliably change its behaviour unless the harness binds that judgment to a stopping action. | Enforce a stop, switch or escalation rule after a defined run of low-utility tool results instead of relying on a prompt-only budget or request to stop. | **Prototype** — controlled paper experiments and a preregistered replication; findings are author-reported and not independently reproduced here. | [arXiv 2610.06191](https://arxiv.org/abs/2610.06191) |
| Agents Are Systems, Not Models | 2026-10-01 | `REL-01` | Evaluate the complete agent configuration—not only the backbone model. | Define an evaluation matrix across task information, reasoning setup, verification mechanism, time budget and model; repeat identical configurations to measure run-to-run variance. | **Prototype** — paper benchmark and released trajectory dataset; findings are author-reported and not independently reproduced here. | [arXiv 2610.01618](https://arxiv.org/abs/2610.01618) |
| MCP Events for plugin automations | Date not stated — announced 2026-09-29 | `INT-02` | A signed, schema-bound external event can become an agent observation without becoming an instruction. | Prefer authenticated subscriptions over polling when the source supports events; validate authorization, filters, signatures and payload schemas, treat event text as untrusted data and make downstream writes idempotent. | **Prototype** — proposed MCP Events capability with an official implementation guide. | [OpenAI MCP Events guide](https://developers.openai.com/plugins/build/mcp-events) |
| Agents API computer use | 2026-09-29 | `MMD-05` | Computer use is a stateful action surface with approval and recovery requirements, not a generic tool call. | Use UI automation only with network allowlists, origin and authentication approvals, private screenshot handling, session recovery and explicit cleanup. | **Vendor claim** — documented API capability; a chosen workflow still requires first-hand validation. | [OpenAI API changelog](https://developers.openai.com/api/docs/changelog) |
| Decisions API limited preview | 2026-09-29 | `PLN-04` | Constrain a routing decision to a finite, predefined action space when open-ended generation is unnecessary. | Use a bounded decision contract for classification, routing or next-action selection instead of asking a general agent to emit unrestricted prose. | **Vendor claim** — limited-preview capability; quality and failure behaviour are not independently validated here. | [OpenAI DevDay 2026 recap](https://openai.com/index/devday-2026-recap/) |
| Agents API sandboxes on AWS Lambda MicroVMs | 2026-09-29 | `ACT-04` | The agent harness and its tool-execution environment should have separate trust and lifecycle boundaries. | Run tools in a per-session isolated environment with a least-privilege execution identity, separate application and executor secrets, explicit suspend/resume semantics and deterministic cleanup. | **Demonstrated** — official reference implementation and verification flow; not reproduced in this repository. | [OpenAI cookbook](https://developers.openai.com/cookbook/examples/agents_api/sandboxes/aws/readme) |
| SkillRL | 2026-09-24 repository update | `LRN-03` | Successful trajectories can be compressed into reusable agent skills. | Add a validated skill-distillation layer only when experience should change future policy; do not confuse raw log storage with learning. | **Repository claim** — paper and code claims require source-led explanation or reproduction before presenting results as fact. | [SkillRL repository](https://github.com/aiming-lab/SkillRL) |
| LTX Dub-It beta | Date not stated — verified 2026-09-30 | `MMD-04` | Generative video can become a bounded action inside an agent workflow. | Put media generation behind explicit review criteria instead of treating a generated asset as an automatically publishable outcome. | **Vendor claim** — documented beta capability; validate the selected example before presenting a result. | [LTX Dub-It beta guide](https://docs.ltx.io/open-source-model/feature-guides/audio/dub-it-beta) |
| MemOS DeepSeek Harness integration | 2026-08-17 repository announcement | `MEM-04` | Persistent memory can be attached around an agent runtime without becoming the agent itself. | Keep the memory service separate from decision policy and define an explicit persistence boundary. | **Repository claim** — architecture and performance have not been independently reproduced here. | [MemOS repository](https://github.com/MemTensor/MemOS) |

#### Latest-first candidate queue for the next Agent Series week

This is a recommendation for Sagar's approval, not a change to any approved
publishing queue.

1. **`ACT-04` — Permissions across an attack chain (October 30):** explain how
   credential scope and execution isolation limit an automated sequence's reach.
2. **`REL-02` — Memory growth fixtures (October 29 revision):** show whether the
   same evidence remains usable as irrelevant history grows under a fixed budget.
3. **`HUM-02` — Independent approval (October 27):** examine what a person must
   decide before an agent's recommendation can frame the choice.

**Refresh note (2026-11-02):** No new canonical topic is proposed. This week's
official OpenAI documentation review found model launches and subscription API
credits; these were excluded because the announcements alone did not establish
a new transferable agent-system decision. The memory revision is explicitly
dated as a revision, not presented as a newly introduced idea.

**Historical refresh notes retained:** On 2026-10-19, native Decisions
integration in GPT-Live and prompt-to-voice were screened out because the
bounded-decision principle was already represented. On 2026-10-12, the Decisions
API record advanced from limited preview to beta; no new canonical topic was
proposed. Previous candidate recommendations were ACT-04 → MEM-06 → REL-01
(October 12) and REL-07 → LLM-06 → REL-03 (October 19).

The next weekly refresh must retain still-relevant items, insert stronger new
developments above them, lower stale items and record the primary source used.
It must not silently delete canonical topics or convert a repository's own
benchmark claim into an independently verified fact.

## Roadmap

### 1. Foundations — what makes a system agentic?

| ID | One concept | Decision the viewer should be able to make |
|---|---|---|
| FND-01 | Agent versus workflow | Decide whether the next step genuinely requires judgement or can be predetermined. |
| FND-02 | The agent loop | Trace observe → decide → act → observe without treating one model call as a complete agent. |
| FND-03 | Goals | Define what the agent is trying to achieve before choosing tools or architecture. |
| FND-04 | Success criteria | Express a finish condition the system can test instead of an open-ended instruction. |
| FND-05 | Autonomy levels | Choose how much the agent may decide without approval. |
| FND-06 | Stopping conditions | Prevent loops that continue after success, uncertainty or budget exhaustion. |

### 2. LLMs inside agents — model behaviour as a system component

| ID | One concept | Decision the viewer should be able to make |
|---|---|---|
| LLM-01 | Instructions | Separate durable system rules from the current user request. |
| LLM-02 | Structured output | Use a machine-checkable decision contract instead of parsing conversational prose. |
| LLM-03 | Context windows | Decide what must be present now rather than assuming the model remembers everything. |
| LLM-04 | Model selection | Match model capability to the reasoning role it must perform. |
| LLM-05 | Model routing | Send different decisions to different models without letting routing become decorative complexity. |
| LLM-06 | Uncertainty and abstention | Design an allowed `I do not know` action before the model encounters ambiguity. |

### 3. Tools and execution — turning decisions into bounded action

| ID | One concept | Decision the viewer should be able to make |
|---|---|---|
| ACT-01 | Tool contracts | Define inputs, outputs and failure semantics for one action. |
| ACT-02 | Tool selection | Decide which available action best advances the goal. |
| ACT-03 | Result validation | Check a tool result before using it as new truth. |
| ACT-04 | Permissions | Restrict which actions the agent is allowed to attempt. |
| ACT-05 | Deterministic sub-workflows | Keep repeatable execution in code after the agent has made the judgement call. |
| ACT-06 | Idempotency | Make retries safe when an action may already have succeeded. |
| ACT-07 | Retry policy | Distinguish a transient failure worth retrying from a decision that needs a different plan. |

### 4. Context, state and memory — what the agent knows and retains

| ID | One concept | Decision the viewer should be able to make |
|---|---|---|
| MEM-01 | Context engineering | Assemble only the information needed for the current decision. |
| MEM-02 | Working state | Represent what is true during the current run. |
| MEM-03 | Checkpointing | Resume a long task without replaying or inventing completed work. |
| MEM-04 | Long-term memory | Decide what deserves to persist across runs. |
| MEM-05 | Memory write policy | Control what may be saved, by whom and after which validation. |
| MEM-06 | Memory retrieval | Retrieve useful memories for a decision rather than dumping history into context. |
| MEM-07 | Memory correction | Update or invalidate remembered information when the user or evidence contradicts it. |
| MEM-08 | Multimodal memory | Store and retrieve text, images and action traces without flattening their meaning. |
| MEM-09 | Shared versus isolated memory | Decide what multiple agents may share and what must remain scoped to a user or role. |

**Frontier attachment:** MemOS maps here. A post must select one memory concept
above—for example `MEM-07`—rather than trying to explain the entire platform.
Its repository describes a unified memory API, multimodal memory, correction
and controlled composition across users, projects and agents.

Source: <https://github.com/MemTensor/MemOS>

### 5. Planning and orchestration — deciding how work progresses

| ID | One concept | Decision the viewer should be able to make |
|---|---|---|
| PLN-01 | Task decomposition | Split a goal only where the parts can be executed or verified independently. |
| PLN-02 | Planning | Produce an actionable sequence without pretending the initial plan will remain correct. |
| PLN-03 | Replanning | Change the next step when observations contradict the current plan. |
| PLN-04 | Routing | Send a task to the correct specialist, tool or deterministic path. |
| PLN-05 | Handoffs | Transfer responsibility with explicit context and completion criteria. |
| PLN-06 | Single-agent versus multi-agent | Add another agent only when a separate role, context or control boundary earns it. |
| PLN-07 | Parallel execution | Run independent work concurrently without creating shared-state races. |

### 6. Protocols and integration — connecting agents to real systems

| ID | One concept | Decision the viewer should be able to make |
|---|---|---|
| INT-01 | API integration | Wrap an external system as a bounded capability. |
| INT-02 | MCP | Understand what a standard tool/context interface changes—and what it does not. |
| INT-03 | Capability discovery | Let an agent discover available actions without granting all of them by default. |
| INT-04 | Agent-to-agent communication | Define a message contract between independently operating agents. |
| INT-05 | Agent identity | Authenticate which agent or user is requesting an action. |

### 7. Reliability, evaluation and security — knowing when to trust the system

| ID | One concept | Decision the viewer should be able to make |
|---|---|---|
| REL-01 | Evaluation contract | Define valid outputs and failure conditions before comparing models or prompts. |
| REL-02 | Evaluation fixtures | Test normal, missing, conflicting and boundary inputs deliberately. |
| REL-03 | Trajectory evaluation | Judge the path of decisions and actions, not only the final answer. |
| REL-04 | Tool-call evaluation | Verify action choice, arguments and result handling separately from language quality. |
| REL-05 | Adversarial evaluation | Test how the agent behaves when input tries to redirect or exploit it. |
| REL-06 | Observability | Record enough state, decisions and tool results to explain a failure. |
| REL-07 | Guardrails | Put deterministic constraints around actions with unacceptable downside. |
| REL-08 | Human escalation | Specify when and how control transfers to a person. |
| REL-09 | Prompt injection | Treat external content as untrusted data rather than executable instruction. |
| REL-10 | Recovery and rollback | Restore a known safe state after partial or incorrect action. |

### 8. Production economics — making agency worth its cost

| ID | One concept | Decision the viewer should be able to make |
|---|---|---|
| OPS-01 | Latency budgets | Allocate time across reasoning, tools and retries based on the user experience. |
| OPS-02 | Cost accounting | Attribute spend to model calls, tools, retries and memory operations. |
| OPS-03 | Caching | Reuse stable work without caching personalised or stale decisions incorrectly. |
| OPS-04 | Quality-cost trade-offs | Reduce cost only after defining the quality and safety floor. |
| OPS-05 | Scaling | Identify which stateful component becomes the bottleneck as usage grows. |
| OPS-06 | Reliability targets | Define availability and completion expectations for an agentic task. |
| OPS-07 | Complexity budget | Remove agentic components whose value does not exceed their operational overhead. |

### 9. Learning and evolving agents — improving from experience

| ID | One concept | Decision the viewer should be able to make |
|---|---|---|
| LRN-01 | Reflection | Use a completed trajectory to identify a specific improvement, not to generate vague self-critique. |
| LRN-02 | Experience memory | Preserve useful lessons from trajectories without replaying every raw token. |
| LRN-03 | Skill abstraction | Convert repeated successful behaviour into a reusable higher-level skill. |
| LRN-04 | Skill retrieval | Select the relevant learned skill for a new task. |
| LRN-05 | Skill evolution | Update a skill library when validation failures reveal a better strategy. |
| LRN-06 | Reinforcement learning for agents | Understand when reward-driven policy improvement is different from runtime prompting. |
| LRN-07 | Learning from failure | Distil a failure into a bounded lesson without teaching the agent an unsafe shortcut. |

**Frontier attachment:** SkillRL maps primarily to `LRN-03`, `LRN-05` and
`LRN-06`. Its stated mechanism distils successful trajectories and failure
lessons into a hierarchical skill library that evolves during reinforcement
learning. Each post should isolate one of those ideas.

Source: <https://github.com/aiming-lab/SkillRL>

### 10. Multimodal and interface agents — perceiving and acting beyond text

| ID | One concept | Decision the viewer should be able to make |
|---|---|---|
| MMD-01 | Vision as input | Convert visual evidence into a decision without treating image description as ground truth. |
| MMD-02 | Audio as input | Use speech or ambient audio as evidence while handling transcription uncertainty. |
| MMD-03 | Voice as output | Decide when spoken interaction improves the task rather than merely adding personality. |
| MMD-04 | Generative media as an agent action | Treat image, video or audio generation as a bounded tool call with review criteria. |
| MMD-05 | Computer use | Let an agent operate interfaces while constraining credentials, confirmation and recovery. |
| MMD-06 | Physical-world action | Separate perception, decision and actuation when mistakes can affect the real world. |

**Frontier attachment:** LTX Dub-It maps to `MMD-04`. It is a video-to-video
dubbing capability that can replace dialogue while attempting to preserve
appearance, voice and delivery. It should be taught as one possible media tool
inside a larger agent workflow, with its beta limitations and review boundary
visible—not as proof that the media pipeline is autonomous.

Source: <https://docs.ltx.io/open-source-model/feature-guides/audio/dub-it-beta>

### 11. Human-agent systems — responsibility around the technology

| ID | One concept | Decision the viewer should be able to make |
|---|---|---|
| HUM-01 | Delegation | Decide which responsibility may be handed to the agent. |
| HUM-02 | Approval design | Place approval before the irreversible action rather than after it. |
| HUM-03 | Explanation | Expose the evidence and decision needed for a person to review the action. |
| HUM-04 | Accountability | Keep one human or organisational owner for the final outcome. |
| HUM-05 | Trust calibration | Help users rely on the agent in proportion to demonstrated capability. |

## Frontier intake lane

New papers, repositories, models and releases are reviewed continuously, but
they do not create random standalone topics. Each candidate must pass this
intake:

1. What canonical topic ID does it deepen or challenge?
2. What system-design, evaluation or operating decision changes?
3. What evidence is available: source, paper, code, trace or reproducible demo?
4. Is the claim demonstrated, a prototype or an informed hypothesis?
5. Can one post teach one concept without becoming a product recap?

If it passes, add it as a dated **frontier attachment** to the relevant topic.
If it introduces a genuinely new durable concept, propose a new canonical ID
for human approval instead of silently expanding the list.

## Active teaching environment: Biceps Progression Agent

The recurring Agent Series demonstration environment is the Biceps Progression
Agent inside the Gym Assistant. Stories should stay anchored to how Sagar built
a repeatable biceps-progression system, while each post still selects exactly
one canonical roadmap concept. Lead with the personal outcome, then provide
enough implementation depth to help someone preparing for an agent-system
interview.

Recommended starting candidates:

| Priority | Topic ID | Single Gym Assistant lesson | Suitable format |
|---|---|---|---|
| 1 | FND-02 | A useful agent repeatedly observes, decides and acts; it is not one generated biceps plan. | Six-slide carousel: five chronological, image-led teaching slides plus one dedicated contact slide. |
| 2 | MEM-02 | The current week's check-in is working state, not permanent memory. | Short Reel with one check-in card. |
| 3 | PLN-03 | When the week changes, the system should replan instead of repeating the original plan. | Face-led Reel plus before/after plan visual. |
| 4 | REL-02 | Normal, missing, conflicting and boundary check-ins are separate evaluation fixtures. | Carousel or recorded evaluation Reel. |
| 5 | REL-08 | A risk signal should transfer the decision to a human rather than produce a more confident recommendation. | Short Reel with one escalation trace. |

### Recommended first post

- `roadmap_topic_id`: `FND-02`
- `viewer_question`: How did an agentic loop help Sagar run a repeatable weekly
  system for biceps progression?
- `single_takeaway`: An agent repeatedly observes the latest state, decides the
  next action and uses the result as the next observation.
- `viewer_learning_payoff`: The viewer can identify observation, decision,
  action and next observation in another system and judge whether its agent
  loop is closed.
- `interview_question`: What is an agent loop, and how would you design one for
  a real system?
- `interview_answer_structure`: goal → observation schema → decision policy →
  bounded action → environment transition → next observation → stop condition.
- `common_interview_mistake`: calling a prompt-to-plan response an agent loop
  even though no result returns as the next observation.
- `teaching_environment`: Biceps Progression Agent (Gym Assistant)
- `evidence_state`: prototype or demonstrated, depending on the available build
  and real check-in trace
- `evidence_object`: creator gym image → one real weekly input → one system
  decision → next check-in
- `adjacent_topic_ids`: `FND-01`, `MEM-02`, `PLN-03`

Do not teach tools, memory, evaluation or guardrails inside this first post.
Those are linked episodes with their own topic IDs.

## Theme rotation examples

The roadmap stays fixed while the teaching environment changes:

- **Gym Assistant:** changing personal state, replanning, bounded decisions and
  evaluation fixtures;
- **Content Agent:** multimodal tools, approval design, cost and media review;
- **Travel Agent:** tools, permissions, changing state, rollback and human
  approval;
- **Work/enterprise agent:** handoffs, observability, shared memory, security and
  accountability;
- **Research agent:** retrieval, source trust, planning, trajectory evaluation
  and learning from failure.

Repeated concepts are allowed when a new environment, failure mode or evidence
object teaches a materially different decision. Repeated explanations with only
new decoration are not.
