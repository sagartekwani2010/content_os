# Carousel concept — Where Jev actually belongs in an LLM system

## Recommendation

Make **one carousel**, not two more Jev Reels. The two published Reels have
already established the comparison and the hybrid. This carousel is the useful
consolidation: it answers the viewer's natural question, "Where would I put it
in a real system?"

It is a companion piece; it **does not count toward the ten-Reel sample** and
should not displace the next scheduled Reel, Gym Assistant Evals.

## Title / hook

**Jev is not your ChatGPT replacement.**

**It is the decision layer around it.**

## Slide map

| Slide | Headline | What the viewer learns |
| ---: | --- | --- |
| 1 | `JEV IS NOT YOUR CHATGPT REPLACEMENT.` | The carousel corrects the category error from the start. |
| 2 | `ASK THIS FIRST: DO YOU NEED A PARAGRAPH OR A DECISION?` | A paragraph/explanation needs a generative model; a bounded choice/score/review can be a decision slot. |
| 3 | `1. MODEL ROUTING` | Decide whether a request needs a fast model, a reasoning model, vision, or human review. Jev routes; it does not write the answer. |
| 4 | `2. TRIAGE + HUMAN HANDOFF` | Support, leads, incidents or applications: route to respond, review, urgent, or other. Low confidence goes safer/human. |
| 5 | `3. TOOL GATES` | Before an agent sends an email, refunds, changes data or deploys: allow, ask, review, or block. Code enforces the final rule. |
| 6 | `4. RAG FILTERING` | Before a chatbot answers: is this retrieved passage relevant, contradictory, or worth showing the writer? |
| 7 | `5. AGENT EVALS` | Did the run meet a closed success criterion? Did it need review? Decision first; benchmark and thresholds in code. |
| 8 | `MY GYM ASSISTANT` | GPT understands the messy check-in; Jev chooses progress/hold/ask/review; policy stops unsafe action; GPT/template explains. |
| 9 | `WHEN NOT TO USE JEV` | Chat, writing, novel open-ended work, unclear success criteria, or a job where one model already meets quality and latency. |
| 10 | `THE RULE` | Add Jev only when it replaces a repeated, bounded, testable decision—and prove the full system earns it. |

## Claim discipline

The linked article repeats **up to 200× faster / 400× cheaper** claims. If this
appears anywhere, use a small source label:

`TYPE SAFE VENDOR CLAIM · SELECTED STRUCTURED-DECISION WORKLOADS · MEASURE YOUR OWN SYSTEM`

Do not put the figures on the cover. The higher-credibility hook is the
paragraph-versus-decision test. An independent Jev field guide similarly maps
model routing, triage, guardrails and RAG filtering to decision workflows, and
states that a single model that already meets quality/latency is a reason not
to add the extra call. [Use-case guide](https://jev.pro/usecases/), [model-routing guide](https://jev.pro/usecases/model-routing/).
