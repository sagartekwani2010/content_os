# Regular demo series backlog — superseded discovery proposal

**Superseded by the follower-growth strategy:** [researcher-series-growth-experiment-2026-11-08.md](researcher-series-growth-experiment-2026-11-08.md) responds to the creator's request to prioritise qualified follower growth and visible research authority. The earlier topic slate below remains as planning history.

**Prepared:** 8 November 2026 (Asia/Kolkata)<br>
**Status:** discovery proposal for Sagar's approval. This is a catalogue, not approval to make production briefs, generate media, schedule, publish or spend credits.<br>
**Creator direction:** two Wardrobe Agent demos, one Agent Astra demo, one AI system design demo, and two or three research-led ideas. Aim to batch production in 2–3 days and have the first item release-ready on 12–13 November.

## Recommended first six

| Order | Working Reel idea | One visible demo | Viewer takeaway | Pillar / evidence gate |
| --- | --- | --- | --- | --- |
| 1 | **Wardrobe Agent 1 — Dress me from what I already own** | Real inventory photos + actual occasion, weather and comfort constraints → three ranked outfits → Sagar chooses one. | Good context is the information that changes a decision. | `ai_real_life`, `MEM-01`. Prototype until a real selection trace is captured. Reuse the earlier [Wardrobe Selector concept](reel-batch-recommendation-2026-10-02.md); check publication status before production. |
| 2 | **Wardrobe Agent 2 — I rejected the first outfit. What changes next?** | Reject an outfit for a concrete reason (e.g. too warm); the agent updates this run's state, reranks only owned items, and asks before treating the reason as a lasting preference. | Feedback for this outfit is different from a durable memory about the person. | `ai_real_life`, `MEM-02`/`MEM-04`. Needs a real before/after trace and a visible user decision; no invented wardrobe items. |
| 3 | **Agent Astra — make Qwen better at one bounded decision** | Astra in Codex prepares a local Qwen LoRA training and evaluation for a missing-order support router: `LOOK_UP_ONCE`, `ASK_CUSTOMER`, `ESCALATE`, or `DRAFT_EVIDENCE_SUMMARY`. Show base Qwen, adapter and held-out output. Preferred AI-avatar narration. | A model adaptation should earn its place against a prompt and a deterministic rule. | `ai_builder`, model adaptation and evaluation. No improvement claim until actual held-out results exist. Details remain in the [earlier implementation contract](six-reel-batch-backlog-2026-11-08.md#r2-implementation-contract-astra-adapts-qwen). |
| 4 | **AI system design — design an agent that can send a message safely** | On-screen architecture trace: user request → draft → recipient/permission check → human approval → send tool → receipt/idempotency record. Simulate a send failure and retry decision; do not send a real message. | The important design choice is where autonomous drafting ends and authorized action begins. | `ai_builder`, `ACT-04`/`REL-03`. Use a small runnable mock or recorded trace; a diagram alone is insufficient for a demo Reel. Distinct from the existing interview-failure-path script. |
| 5 | **Trend demo — a product page tries to instruct your agent** | A controlled, malicious catalogue or webpage snippet says to ignore the user's constraints. Show the agent's attempted action, then the same task with untrusted page text separated from instructions and the action tool scoped. | Reading an external page must not grant that page authority over the agent. | `ai_builder`, `ACT-04`. Local contained fixture only; show the guardrail's observed result, not a universal security claim. |
| 6 | **Trend demo — would you still choose this if AI had not recommended it?** | Two approval screens for the same illustrative choice: one shows an AI preference first; the other asks for the person's criteria before showing evidence and options. Explain the different decision boundary. | Human approval is useful when the person can form and record an independent criterion. | `ai_career`, `HUM-02`. The UI is a design demonstration; do not claim a causal effect from this Reel's mockup. |

**Suggested release sequence:** 1 → 4 → 2 → 3 → 5 → 6. This alternates everyday utility, system design, model building, security and leadership so consecutive posts do not repeat the same visual grammar. It is a proposed queue, not a schedule. A staged cadence across roughly two weeks would make the six a recurring series instead of six releases on one day.

## Seventh idea to keep warm

**Can your agent still remember the one relevant fact after 50 irrelevant chats?** Hold a travel-planning preference and the current request constant, add irrelevant prior sessions in steps, and show whether the next action remains correct within a fixed retrieval budget. This is a separate memory-evaluation demo, not a repeat of Wardrobe Agent 2's feedback-versus-memory decision. Use only measured local results; choose it as Reel 6 if the approval-design Reel feels too abstract or if the real memory test yields a striking trace. `REL-02`, `ai_builder`.

## Why these three trend candidates

These are **timely primary-source developments**, not a claim that their social-media engagement has been measured. The demo angle is our editorial inference from the evidence.

1. **Agent security and permissions:** Google Threat Intelligence Group and Mandiant reported observed use of agentic offensive frameworks in intrusions on [30 October 2026](https://cloud.google.com/blog/topics/threat-intelligence/artex-and-friends-enter-agentic-offensive-frameworks). The transfer to our audience is concrete: what an agent reads must not expand what it is allowed to do. [OpenAI's computer-use guidance](https://developers.openai.com/api/docs/guides/tools-computer-use-integration) explicitly treats third-party page and tool content as untrusted; that is the direct basis for the controlled product-page injection demo. The demo does not recreate the reported intrusions.
2. **Independent human approval:** An [Anthropic study published 27 October 2026](https://www.anthropic.com/research/agents-judgment-calls) reported that professional analysts frequently followed an agent's experimentally assigned preference in one analysis task. The Reel's opportunity is to make approval-interface design visible. The study's result is source-reported and task-specific.
3. **Memory under growth:** A [paper revised 29 October 2026](https://arxiv.org/abs/2605.07313) evaluates whether fixed relevant evidence remains usable while irrelevant history accumulates. The proposed Reel would reproduce the *test pattern* on our own small fixture; it would not present the paper's numbers as our result.

## Batch production dependencies

- **First:** confirm which Wardrobe concept, AI interview Reel or other related material has already been posted. Preserve the posted Diwali Reel as retrospective evidence only.
- **Capture once:** real wardrobe photos, one occasion, one rejection reason and the agent's complete action trace. Reuse the inventory and screen design for the two Wardrobe demos while giving each a separate claim and proof visual.
- **Build in parallel within the batch:** the Astra–Qwen local experiment is the critical path. Keep its title and result language conditional until the adapter and held-out comparison exist. The system-design and security demos can use contained mock tools.
- **Narration and visual production:** record or render one batch of approved narration; use the preferred approved avatar asset for the Astra Reel if available. Create only brief-approved keyframes in ChatGPT. Use Edits for assembly; inspect invideo/Magnific credit balances and action prices before any justified generation. fal.ai generations remain Sagar-run.
- **QA and learning:** each finished Reel gets a rendered-video check for exact hook promise, timed visuals, captions, audio and platform export. Log creator feedback and actual before/after evidence after each generation and final cut, then feed approved lessons into the next versioned prompt and brief.

## Choices for Sagar

1. Approve the first six as the series slate, or swap the memory test into slot 6.
2. Choose the real occasion and rejection reason for Wardrobe Agent 1 and 2, and identify the approved avatar/voice source for Agent Astra.
3. Confirm that “Agent Astra” means GPT-6 Astra in Codex driving the Qwen adaptation experiment discussed earlier.

This proposal supersedes the support-led [six-Reel draft](six-reel-batch-backlog-2026-11-08.md) without changing historical fixed queues or treating any unapproved topic as production-ready.
