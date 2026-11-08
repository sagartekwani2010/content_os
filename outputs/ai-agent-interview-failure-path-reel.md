# The AI-agent interview question that exposes shallow answers — Reel

## Brief fingerprint

- **Topic:** The AI-agent interview question that exposes shallow answers
- **Core thesis:** Naming a model and tools is not an agent-system answer; the
  useful answer explains the failure path, preserved state and safe next step.
- **Learning objective:** Viewers can structure an interview-quality answer to
  an AI-agent system-design question using five practical components.
- **Format:** 30-second Reel
- **Pillar:** AI Career / Interview-Ready Systems Thinking
- **Scenario:** fictional support assistant; illustrative, not a company claim

## Selected hook

> If I’m interviewing for an AI role, I don’t first ask which agent framework
> you know. I ask: what happens when the tool call fails?

Why it works: it challenges framework-first preparation and immediately signals
real implementation judgement.

## Script and scene plan

| Time | Spoken script | On-screen copy | Visual / production |
|---:|---|---|---|
| 0–4s | “If I’m interviewing for an AI role, I don’t first ask which agent framework you know.” | `AI agent interview?` | Direct-to-camera or avatar. Clean close crop; no UI. |
| 4–7s | “I ask: what happens when the tool call fails?” | `What happens when the tool fails?` | Hard cut to black with the question in large type. One short alert sound is optional. |
| 7–12s | “Most answers stop at: user asks a question, the agent calls a tool, the model replies.” | `User → agent → tool → answer` | Four simple large blocks animate left to right. The `tool` block turns red at the end. |
| 12–17s | “That is a demo answer. A production answer needs five things.” | `A demo answer ≠ a system answer` | Return to camera. Beside you, a single numbered rail begins at `1`. |
| 17–25s | “The user goal. The state you keep. The tool and its failure mode. The fallback. And how you evaluate whether the outcome was safe.” | `1 Goal`  `2 State`  `3 Tool + failure`  `4 Fallback`  `5 Eval` | Add one item per beat. Keep each line large. On `Fallback`, show a tiny trace: `timeout → preserve context → human escalation`. |
| 25–30s | “So next time you design an agent, don’t just explain what it can do. Explain what it does when reality breaks.” | `Explain the failure path.` | Direct-to-camera closing. Final frame holds the five-item rail for one second. |

## Production notes

- **Delivery:** human talking head is preferred for credibility; avatar is an
  acceptable control version for a later avatar-vs-human experiment.
- **Visual language:** dark ink background, white type, cyan for the normal
  path, red only for `tool failure`, amber for `fallback`.
- **No fake console:** this Reel teaches an answer structure. The only trace is
  the three-step fallback line, deliberately large and readable.
- **Pacing:** no more than six cuts; leave the five-component frame visible long
  enough to save or screenshot.

## Caption

Framework names are easy to memorise. Failure paths are where system design
starts.

For an AI-agent interview answer, cover: goal, state, tool failure, fallback,
and evaluation.

That structure is useful in the interview—and when you have to build the thing.

## Factual checks

- The script expresses an interview lens, not a universal hiring rule. Say
  “this is what I ask” or “this is how I would assess it”; do not imply every
  interviewer follows it.
- The support-assistant fallback is illustrative. Do not attribute it to a
  specific company.

## QA snapshot

- **Learning payoff:** strong; a reusable five-part answer structure.
- **Execution proof:** failure path and safe fallback are visible, not merely
  named.
- **Risk:** do not overstate personal hiring authority. Keep the hook in the
  first-person conditional as written.
- **Verdict:** `READY_FOR_HUMAN_REVIEW`
