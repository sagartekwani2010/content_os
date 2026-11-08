# Diwali flight agent: tool calls, skill, autonomy and latency

Status: **REVISE before publication**. Illustrative interview answers, not an Amazon leveling rubric. Earlier drafts remain preserved.

## Brief fingerprint

- Topic: Three Applied Scientist answers to a Diwali flight rebooking agent question
- Core thesis: All three Applied Scientist answers must deliver a confirmed ticket within the customer's constraints. Their agent-design judgment grows from a bounded tool-use loop, to a reusable rebooking skill that preserves state and reduces avoidable tool latency, to an autonomy policy that spends calls and human attention only when the expected decision benefit justifies the delay. The answers are illustrative scopes, not Amazon's official interview rubric.
- Learning objective: Viewers can distinguish tools, a skill, state, autonomy, and latency through three hireable answers to the same agent-design question.
- Format: Reel
- Brand pillar: `ai_career`
- High-level sections:
  - Diwali flight cancellation and ₹10,000 original fare with ₹5,000 extra-spend limit
  - all three answers produce a confirmed on-time ticket within the spending limit
  - L5 Applied Scientist answer: bounded agent loop with the required booking tools, exact-fare consent and confirmed-ticket stop condition
  - L6 Applied Scientist answer: reusable rebooking skill, preserved state, independent calls in parallel and local recovery from a stale quote
  - L7 Applied Scientist answer: call and latency budget, autonomy and handoff policy, mandatory safety calls and outcome evaluation
  - transferable progression from tool loop to reusable skill to budgeted autonomy

## Execution plan

**Viewer payoff:** A reusable interview lens: *What tools are required? What repeatable procedure belongs in a skill? Which calls and actions can the agent decide for itself?* **Same case for each level:** ₹10,000 paid; free reroute misses Diwali; the traveller allows up to ₹5,000 additional spend. A suitable live replacement exists. The exact replacement fare is deliberately omitted. Every candidate ends with a confirmed on-time ticket and stays inside the cap.

**System boundary:** One coordinating agent. A tool reads or changes the airline/booking system; a skill is the reusable procedure that tells the agent how to use those tools; the booking workflow enforces irreversible purchase rules. The skill does not itself make external calls or magically reduce latency. Independent tool calls can run in parallel, repeated lookups can be avoided by retaining state, and optional calls can be skipped when their decision value is lower than their delay. Quote, exact customer approval, cap enforcement, booking and status verification remain required.

**Story:** salary hook → familiar cancellation → L5 complete loop → L6 reusable skill and critical path → L7 action policy and latency budget → confirmed ticket in each column. **Main risk:** compensation numbers are creator supplied and need provenance before publication; level answers are illustrative.

## Hook options

1. **Selected, comparison:** “Amazon Applied Scientist: L5, ₹90 lakh. L6, ₹1.5 crore. L7, ₹2.5 crore. Same agent question.” It promises a level comparison and uses the creator's salary hook.
2. **Outcome first:** “Three candidates book the same Diwali replacement. Only one designs the agent's autonomy.” This emphasizes the result and the final design decision.
3. **Mistake:** “A flight agent with six tools can still be slow.” This opens the tool-call and latency tension.

## Content package — 60-second spoken script

| Time | Spoken script | On-screen proof |
|---|---|---|
| 0–7s | “Amazon Applied Scientist: L5, ₹90 lakh. L6, ₹1.5 crore. L7, ₹2.5 crore. Same agent question.” | Face-led; salary cards marked `≈`; small `ILLUSTRATIVE ANSWERS`. |
| 7–16s | “₹10,000 Diwali flight cancelled. You can add ₹5,000. The free reroute is too late. Get a confirmed replacement.” | `₹10K PAID` → `+₹5K MAX` → `HOME BEFORE DIWALI`; free route stamped `TOO LATE`. |
| 16–29s | “L5: I read booking rights, search live seats, refresh the quote, ask approval for the exact fare, book, and verify ticket status. The booking tool enforces the ₹5,000 cap. Complete loop.” | Tool trace: `booking → policy → seats → quote → approval → book → status: CONFIRMED`. Highlight tool result before each next decision. |
| 29–44s | “L6: I make rebooking a skill: inputs, tool dependencies, retry and stop rules. The agent retains state, checks policy and seats in parallel, re-quotes and re-asks consent on price changes, then books and verifies.” | Skill card `PNR · deadline · +₹5K cap`; two independent read calls in parallel after booking lookup. `QUOTE CHANGED` → refresh quote + approval only → `CONFIRMED`. |
| 44–60s | “L7: I optimize confirmed bookings and time-to-confirm under hard consent and spending rules. Quote and status checks stay mandatory; extra searches must earn their delay. Clear cases book after approval; uncertain rights or prices hand off. I track p95 latency and violations.” | Decision card: `CLEAR + APPROVED → AUTO-BOOK → CONFIRMED`; `UNCERTAIN → HUMAN`. Metric strip `confirmed · p95 time · cap breaches`. End `TOOLS → SKILL → AUTONOMY`. |

**Caption:**

What changes between three good agent-design answers? The scope of the decision they own.

L5 makes the tool loop complete: no success claim until the ticket-status tool returns confirmed. L6 makes the repeated rebooking procedure a skill, keeps the booking state, runs independent reads in parallel, and handles a changed quote without replaying the whole flow. L7 decides which *additional* calls or human reviews are worth their delay; it never skips a fresh quote, exact approval or confirmation check. All three get this traveller a confirmed on-time ticket within the ₹5,000 extra limit.

**Technical distinction:** A skill is a reusable playbook for the agent. Tools perform external reads and actions. The booking tool, not the prompt, enforces the hard spend cap and idempotency. If a quote changes, the earlier exact-fare approval is invalid and must be requested again. If rights or final price stay uncertain, the agent hands off. For L7, an optional second search is worth its delay only when it could materially improve the choice before the live quote expires. The objective is faster confirmed travel subject to hard consent and spending constraints, not merely fewer tool calls.

These answer scopes are illustrative, not Amazon's interview rubric. Salary figures are creator-supplied estimates requiring source verification.

**CTA:** “In your agent, which calls are truly mandatory?”

## Interview architecture behind the script

| Building block | Concrete contract in this case | Level distinction |
|---|---|---|
| Agent state | Booking ID, destination, Diwali arrival deadline, ₹5,000 additional-spend ceiling, rights, candidate itinerary, quote and expiry, exact-fare consent, booking transaction ID, final ticket status. | L5 tracks enough to finish; L6 preserves it across retry; L7 uses it to decide the next call or handoff. |
| Tools | `get_booking`, `get_rebooking_rights`, `search_seats`, `get_final_quote`, `book_replacement`, `get_ticket_status`. Typed results include timestamps/status; `book_replacement` checks cap, consent and an idempotency key. | Same external capabilities for all three. A skill is not an extra airline API. |
| Skill | `flight_rebooking`: inputs are booking ID, deadline and cap; procedure defines tool dependencies, consent invalidation when price changes, local retry, verified confirmation stop condition, and handoff cases. | L6 packages expertise so the agent does not reason afresh about routine steps on every turn. |
| Autonomy | With a valid quote, exact approval and clear rights, the agent can execute booking and verify it. Uncertain entitlement, price or failed confirmation triggers further evidence or human review. | L7 defines the decision policy for *optional* evidence and handoff. Hard checks cannot be skipped. |
| Latency | After booking lookup, rights and seat search are independent reads. Parallel execution shortens elapsed time; it does not reduce the number of mandatory calls. A changed quote needs local refresh and renewed consent, not full restart. | L6 improves critical path; L7 allocates latency to calls most likely to change a consequential decision. |
| Evaluation | Confirmed on-time tickets, p95 time from request to confirmation, unnecessary/repeated calls, handoff delay, duplicate charges and hard-constraint breaches. | L5 proves correctness; L6 tests efficiency against that baseline; L7 evaluates the full speed-versus-risk policy. No unmeasured improvement is claimed. |

## Thumbnail and visual plan

**Thumbnail asset `thumbnail.png`:** Finished 9:16 cover with a central 1:1 safe zone. Face-led if an approved real portrait is supplied; otherwise finished editorial type. Warm off-white, charcoal type, muted lime highlight. Exact copy: `SAME AGENT. THREE LEVELS.` and small `DIWALI FLIGHT`. Add a simple ticket glyph. No salary figures on cover until sourced. No airline logo, fake app UI, robot, terminal dump or tiny type. Alt text: “Three agent-design answers to one Diwali flight rebooking question.”

**Scene assets:** `01-hook.png` salary ladder, `02-case.png` traveller constraints, `03-l5-loop.png` sequential tool trace, `04-l6-skill.png` skill contract with parallel read branches and local quote retry, `05-l7-policy.png` clear-case booking versus uncertain-case handoff. Each is a phone-safe, 9:16 finished card with one main idea, a consistent confirmed-ticket stamp, and no fabricated airline screen. Face footage fills the opening and transitions; cards supply the mechanism. The visuals must show tool observation → agent decision → booking action → ticket-status observation.

## QA report

**Editorial scores (0–10):** hook 8.0, clarity 8.5, technical accuracy 8.5, brand fit 8.5, originality 8.0, share potential 7.5, save potential 8.5, visual potential 8.0, learning value 8.5, execution against brief 8.5, AI hype penalty 0.5, generic content penalty 0.5. Deterministic composite: **8.005**; failed numeric gates: **none**. Section coverage: all six brief sections. Thesis drift: none. Spoken script: approximately **145 words in 60 seconds**; a real read-through is still needed.

**Factual checks:** Salary source, geography, period, annual compensation definition and sample size. Hypothetical customer-support case. Do not present the answers as Amazon's official rubric or assert that any one answer earns a salary. If a live airline provider does not offer a particular tool or hold capability, the interview answer must state the integration assumption rather than invent it.

**Verdict: REVISE** until salary provenance and spoken timing are checked. The required `python cli.py check <brief>` command was attempted, but this checkout has no `check` subcommand; the brief passed Pydantic model validation and the numeric QA gates were evaluated directly.
