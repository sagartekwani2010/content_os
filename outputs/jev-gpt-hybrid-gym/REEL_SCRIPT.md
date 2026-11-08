# Jev + GPT-5.6 Sol inside my Gym Assistant — master script

## What this Reel proves—and what it does not

This Reel explains the architecture and shows a **simulated architecture
estimate**. It does not claim that the hybrid is faster, cheaper, safer, or
better than GPT-only in the live Gym Assistant. Those are end-to-end outcome
claims that require recorded runs.

The continuity point from the prior Reel is deliberate: a faster bounded
decision model does not replace a conversational model. The story's useful
turn is that the answer is **not** “use both everywhere”; it is “replace only
the separately necessary, repeated decision step—and make the combined system
earn its complexity.”

## Overall script — speakable reference

Last Reel, Jev was 99% lower cost than GPT in one clean Gym decision. I
combined them. Surprise: the hybrid saves only 49% on model cost.

My Gym Assistant gets messages like: “I slept badly and missed a workout.
Should I progress?”

GPT turns that messy message into a clean check-in. Jev—because it cannot
chat—gets that clean check-in, looks at the risk, and picks one thing:
progress, hold, ask for more information, or human review.

A system rule then checks the answer. A risky check-in can never become
automatic progress.

In the GPT-only version I am testing, GPT does both jobs. In the hybrid, Jev
replaces only the decision job. That gives an estimated 36% less waiting and
49% lower model cost. Why not 99%? GPT is still part of the system. These are
estimates until I run live logs.

The rule: do not stack models to look smart. Use GPT for messy human input, a
specialist model for repeat decisions, and hard rules for safety. If one GPT
call can safely do it all, keep it simple.

## Time-driven recording script

| Time | Spoken line | Visual proof / treatment | New information |
| --- | --- | --- | --- |
| 0–5s | “Last Reel, Jev was 99% lower cost than GPT. I combined them. Surprise: the hybrid saves only 49%.” | Sagar on camera. Large text: `99% → 49%`. Small persistent label: `ESTIMATE · LIVE LOGS PENDING`. | Immediate tension: why did the saving shrink? |
| 5–11s | “My Gym Assistant gets messages like: ‘I slept badly and missed a workout. Should I progress?’” | One saved check-in card labelled `MESSY HUMAN MESSAGE`. | A relatable input, before any jargon. |
| 11–17s | “GPT turns that messy message into a clean check-in.” | `GPT → CLEAN CHECK-IN`: recovery, completed workouts, risk flag. | GPT's job in plain English. |
| 17–25s | “Jev gets that clean check-in, looks at the risk, and picks one thing: progress, hold, ask for more information, or human review.” | One Jev route card with four big buttons. `HUMAN REVIEW` uses a calm amber colour, not alarm imagery. | Jev's job and risk judgment. |
| 25–29s | “A system rule then checks the answer. A risky check-in can never become automatic progress.” | Simple red block: `RISK + PROGRESS = BLOCKED`. | Rules protect the boundary. |
| 29–37s | “In GPT-only, GPT does both jobs. In the hybrid, Jev replaces only the decision job.” | Two sparse lanes: `GPT → GPT` versus `GPT → JEV`. No code, no dashboard. | The precise point of comparison. |
| 37–43s | “That gives an estimated 36% less waiting and 49% lower model cost.” | One clean result card: `36% LESS WAITING` / `49% LOWER MODEL COST`; header remains `ESTIMATE · NOT LIVE RESULT`. | Concrete impact, without fake precision. |
| 43–50s | “Why not 99%? GPT is still part of the system. Don’t stack models to look smart: GPT for messy input, specialists for repeat decisions, rules for safety. If one GPT call works safely, keep it simple.” | Sagar on camera. Three short labels beside him: `UNDERSTAND · DECIDE · PROTECT`. | The reusable agent-building rule. |

## Architecture shown in the Reel

```text
GPT-only control
  raw check-in → GPT state interpretation → GPT route + response

Hybrid
  raw check-in → GPT state interpretation → Jev risk + route decision
                                                 │
                                                 ▼
                              deterministic policy enforcement + response template
                              ├── risk + non-escalation → block; do not action
                              └── permitted route       → locked user response
```

For the controlled comparison, both arms keep the same GPT check-in interpreter
and the same validator/policy enforcement. `GPT-only` uses GPT-5.6 Sol for the
second route-and-response step; the hybrid uses Jev for the complete
risk-and-route decision and a deterministic response template. The estimate
counts both model calls in each arm. It is intentionally **not** compared with
an optimised single-call GPT implementation; that is a separate baseline the
live evaluation must include.

## Evaluation contract for the next result Reel

Use the prior `Jev vs GPT` fixture suite as the starting harness, but change
the comparison labels to `gpt_only`, `hybrid`, and `gpt_single_call`. The first
two mirror the traceable two-step path shown in this Reel. The third protects
against a false hybrid win: it tests whether one GPT call can safely understand,
decide and respond more simply. Keep all five fixture types, ten recorded runs
each, fixed versions, fixed prompts/settings and raw logs.

| Gate, in order | What must be reported | Why it matters |
| --- | --- | --- |
| 1. Contract validity | Schema-valid route and permitted reason for every run | A fluent explanation is not a valid system decision. |
| 2. Risk routing and boundary safety | Correct Jev/GPT `escalate` judgment on risk states; any policy-block or boundary escape separately—not averaged away | The model judges the route, while the system refuses to action a dangerous route. |
| 3. Decision quality | Valid-safe decisions across the 50 saved runs | Confirms the hybrid has not weakened the core action. |
| 4. Response consistency | Returned copy matches the locked route and human-review status | Neither template nor GPT prose can contradict the decision. |
| 5. End-to-end operation | Wall-clock latency and cost of **all** model calls | The hybrid must pay for the GPT and Jev calls it actually makes. |

### Release rule

Do not call the hybrid better unless it has no hard-boundary failures and the
same-or-better valid-safe outcome on the saved suite. Only then compare total
latency and cost against **both** the two-step GPT-only control and the simpler
one-call GPT baseline. Treat the `36% lower latency` and `49% lower cost` as a
model-call estimate for the traceable two-step path only. A slower or more
expensive hybrid can still be justified for a user-facing reason, but that
reason must be shown—not assumed.

## Story validation

| Judge test | Pass rationale |
| --- | --- |
| Exact question by 5 seconds | Why does Jev's 99% component cost saving become only 49% in the hybrid? |
| Proof / mechanism by 15 seconds | One raw check-in enters two visible, controlled paths. |
| Story turn | The hybrid saves only where it replaces a separately necessary GPT decision step. |
| No category error | Jev is never presented as a chatbot or replacement for GPT. |
| Evidence boundary | Every percentage is visibly a simulated model-call estimate; the live test remains distinct. |
| Earned implication | Use a hybrid only for a repeated, measurable decision that survives full-system evaluation. |
