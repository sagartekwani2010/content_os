# Jev decision slots — reasoning for the carousel

## First principle

Put Jev in a system only when the software needs a **bounded judgment** it can
act on. The output should be a defined choice, an ordered score, or a yes/no
signal—not an explanation, plan, email or conversation.

The practical test is:

> **Does the product need a paragraph, or does it need code to choose a path?**

Generative LLMs are for the paragraph. Jev is a candidate for the path.

## The four jobs

Many industry examples reduce to four reusable decision slots.

| Decision job | Where it sits | Example question | Why Jev can fit | What must remain outside Jev |
| --- | --- | --- | --- | --- |
| **1. Route** | Before the expensive model or handler | “Does this need a fast model, reasoning model, vision model, specialist workflow, or human?” | Output is a small, known menu. A code path follows the choice. | Capability constraints, model availability, confidence floor and fallback route. |
| **2. Score / filter** | Before generation or in a batch process | “Is this RAG passage useful?”, “How urgent is this ticket?”, “Which context is worth keeping?” | The state can be judged against an explicit relevance, risk or quality rubric. | Exact arithmetic, retrieval itself, ranking policy and the final generated answer. |
| **3. Gate / escalate** | Before a tool call, automatic action, or handoff | “Allow, ask, review, or block this action?”, “Does this need a human?” | The system needs a bounded safety/operations decision, not prose. | Deterministic policy enforcement, permissions, audit logs and human authority for high-stakes cases. |
| **4. Evaluate** | After an agent or model run | “Did the output meet the rubric?”, “Did the agent finish?”, “Does this claim have support?” | A closed evaluation criterion can be turned into a score, choice or review route. | Ground truth, the test harness, release threshold and final production approval. |

## Concrete uses inside an LLM system

### 1. Intent or model routing

`user message → Jev chooses handler/model class → chosen LLM or code path`

Use it when one request may need a different handler: billing, product help,
vision, complex reasoning or human support. Jev picks the route; it does not
write the response. Low confidence should fail toward a safer model or a human.

### 2. Support / lead / incident triage

`ticket or record → Jev: route + urgency + human-needed → queue`

The same mechanism works across domains. The reusable job is triage, not a
specific industry. This is strongest when teams have named queues, a review
path and historical examples to evaluate against.

### 3. Retrieval quality before generation

`query + retrieved passages → Jev: relevant / weak / contradictory → LLM sees selected context`

Jev can filter or score retrieved passages before a generative model writes an
answer. It should not be presented as proof that a claim is true; it is a
decision signal about supplied evidence and must be validated on real queries.

### 4. Tool or workflow gating

`agent proposes tool/action → Jev: allow / ask / review / block → policy code → tool`

Examples: send an email, issue a refund, change customer data, start a deploy.
Jev is a decision signal, not an authorization system. Code must check identity,
permissions, hard rules and audit requirements. High-consequence action still
needs an appropriate human-review policy.

### 5. Agent evaluation

`agent trace/output + rubric → Jev: pass / fail / review or scored reasons → eval report`

This is especially relevant to the content series. A Jev-style judge can answer
whether an agent respected a decision contract, asked for missing information,
or reached an allowed outcome. It cannot replace a labelled eval set; its own
thresholds and disagreements must be evaluated.

### 6. Context pruning or ranking

`large candidate context → Jev score/filter → compact context for the writer`

This is the same **score/filter** job applied to context. It is useful when the
writer is being given a lot of noisy history, retrieved documents or tool
outputs. Do not call it summarisation: the job is deciding what survives, not
rewriting it.

### 7. The Gym Assistant (worked example)

`messy weekly message → GPT makes structured state → Jev chooses progress / hold / ask / review → policy code validates → template or GPT explains`

The important boundary: GPT remains because the person wrote messy language.
Jev earns a place only at the repeated decision slot after state is usable.

## When Jev should not be used

- The product needs a user-facing explanation, creative draft, open-ended plan
  or conversation.
- A deterministic rule can solve the job more reliably and cheaply.
- The answer space or success criterion cannot be described clearly.
- The job is rare or one-off, so the integration and evaluation overhead does
  not pay back.
- One generative model already meets observed quality, latency and cost needs.
- The decision is high stakes and no appropriate policy, threshold, audit or
  human-review design exists.

## What this means for the carousel

Use **five slides for the five most intuitive slots**:

1. Route models or handlers.
2. Triage and hand off to humans.
3. Filter RAG/context before the writer sees it.
4. Gate tool calls and automated actions.
5. Evaluate whether an agent run met a rubric.

Then use Gym Assistant as one worked architecture, followed by the non-use
slide. Context pruning is a memorable optional example inside the RAG/filter
slide, not a separate slide.

## Claim discipline

The TypeSafe primitive framing is Choice (defined option), Score (defined
ordered rubric) and Noul (a calibrated yes/no probability). The design rule is
to combine typed judgments in application code, including thresholds and
fallbacks—not to treat a confidence value as permission to act. [Primitive
guide](https://www.typesafeai.org/guides/choice-score-noul)

The widely repeated `up to 200× faster / 400× cheaper` headline is TypeSafe's
vendor claim for selected structured-decision workloads. It is not a full-system
or general-chat result. If mentioned in the carousel, label it exactly as a
vendor claim and direct viewers to measure their own path. [Claim
analysis](https://explainx.ai/blog/jev-speed-cost-claims-fact-check-2026)
