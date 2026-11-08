# Diwali flight agent: closed agent loop and B-roll — seventh pass

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

**Story:** salary hook → familiar cancellation → L5 complete tool loop → L6 reusable skill and critical path → L7 goal, observation, policy, action, result and stop condition → confirmed ticket in each column. The L7 choice to make another tool call is governed by its expected decision value and delay. **Main risk:** compensation numbers are creator supplied and need provenance before publication; level answers are illustrative.

## Hook options

1. **Selected, comparison:** “Amazon Applied Scientist: L5, ₹90 lakh. L6, ₹1.5 crore. L7, ₹2.5 crore. Same agent question.” It promises a level comparison and uses the creator's salary hook.
2. **Outcome first:** “Three candidates book the same Diwali replacement. Only one designs the agent's autonomy.” This emphasizes the result and the final design decision.
3. **Mistake:** “A flight agent with six tools can still be slow.” This opens the tool-call and latency tension.

## Content package — 60-second spoken script

| Time | Spoken script | On-screen proof |
|---|---|---|
| 0–7s | “Amazon Applied Scientist: L5, ₹90 lakh. L6, ₹1.5 crore. L7, ₹2.5 crore. Same agent question.” | Face-led; salary cards marked `≈`; small `ILLUSTRATIVE ANSWERS`. |
| 7–16s | “₹10,000 Diwali flight cancelled. You can add ₹5,000. Free reroute misses Diwali. All three must confirm a ticket.” | `₹10K PAID` → `+₹5K MAX` → `HOME BEFORE DIWALI`; free route stamped `TOO LATE`. |
| 16–27s | “L5: Tools read or change airline systems. I check rights and seats, quote the fare, ask approval, book, then verify confirmation. The booking service enforces the ₹5,000 cap.” | Header `TOOLS = READ OR ACT`; trace `booking → policy → seats → quote → approval → book → status: CONFIRMED`. Highlight tool result before each next decision. |
| 27–40s | “L6: A skill is the playbook for those tools. The agent keeps booking state, checks rights and seats in parallel, and re-quotes with fresh approval if prices change. Then books and verifies.” | Header `SKILL = PLAYBOOK`; skill card `PNR · deadline · +₹5K cap`; two independent read calls in parallel after booking lookup. `QUOTE CHANGED` → refresh quote + approval only → `CONFIRMED`. |
| 40–60s | “L7: Goal: confirmed on-time travel. Observe rights, fare and seats. My policy chooses: re-quote, book after approval, or hand off—based on whether another call is worth the delay. The booking tool acts; ticket status returns. Confirmed means stop; failure means replan. That’s bounded autonomy.” | Header `GOAL → OBSERVE → DECIDE → ACT → OBSERVE AGAIN`; concrete route labels `RE-QUOTE · BOOK · HAND OFF`. Show quote and cap guard on the book branch, status `CONFIRMED` returning as evidence, then `STOP`. Small evaluation strip: `confirmed · p95 time · cap breaches`. |

**Caption:**

What changes between three good agent-design answers? The scope of the decision they own.

L5 makes the tool loop complete: no success claim until the ticket-status tool returns confirmed. L6 makes the repeated rebooking procedure a skill, keeps the booking state, runs independent reads in parallel, and handles a changed quote without replaying the whole flow. L7 closes the agent loop: live rights, fare and seats are observations; the policy chooses another call, booking or handoff; the booking tool changes the reservation; ticket status is the next observation; confirmed means stop and failure means replan. It never skips a fresh quote, exact approval or confirmation check. All three get this traveller a confirmed on-time ticket within the ₹5,000 extra limit.

**Technical distinction:** A skill is a reusable playbook for the agent. Tools perform external reads and actions. The booking tool, not the prompt, enforces the hard spend cap and idempotency. If a quote changes, the earlier exact-fare approval is invalid and must be requested again. If rights or final price stay uncertain, the agent hands off. For L7, an optional second search is worth its delay only when it could materially improve the choice before the live quote expires. The objective is faster confirmed travel subject to hard consent and spending constraints, not merely fewer tool calls.

These answer scopes are illustrative, not Amazon's interview rubric. Salary figures are creator-supplied estimates requiring source verification.

**CTA:** “In your agent, which calls are truly mandatory?”

## Interview architecture behind the script

| Building block | Concrete contract in this case | Level distinction |
|---|---|---|
| Agent state | Booking ID, destination, Diwali arrival deadline, ₹5,000 additional-spend ceiling, rights, candidate itinerary, quote and expiry, exact-fare consent, booking transaction ID, final ticket status. | L5 tracks enough to finish; L6 preserves it across retry; L7 uses it to decide the next call or handoff. |
| Tools | `get_booking`, `get_rebooking_rights`, `search_seats`, `get_final_quote`, `book_replacement`, `get_ticket_status`. Typed results include timestamps/status; `book_replacement` checks cap, consent and an idempotency key. | Same external capabilities for all three. A skill is not an extra airline API. |
| Skill | `flight_rebooking`: inputs are booking ID, deadline and cap; procedure defines tool dependencies, consent invalidation when price changes, local retry, verified confirmation stop condition, and handoff cases. | L6 packages expertise so the agent does not reason afresh about routine steps on every turn. |
| Autonomy | Goal: confirmed on-time travel. Observation: rights, quote, available seats. Policy selects `RE-QUOTE`, `BOOK_AFTER_APPROVAL`, or `HAND_OFF`. The booking tool changes the reservation, and ticket status returns as the next observation. `CONFIRMED` stops; `PENDING` waits and checks status again; `FAILED` replans or escalates. | L7 defines the closed decision loop and when an optional observation is worth its delay. Hard checks cannot be skipped. |
| Latency | After booking lookup, rights and seat search are independent reads. Parallel execution shortens elapsed time; it does not reduce the number of mandatory calls. A changed quote needs local refresh and renewed consent, not full restart. | L6 improves critical path; L7 allocates latency to calls most likely to change a consequential decision. |
| Evaluation | Confirmed on-time tickets, p95 time from request to confirmation, unnecessary/repeated calls, handoff delay, duplicate charges and hard-constraint breaches. | L5 proves correctness; L6 tests efficiency against that baseline; L7 evaluates the full speed-versus-risk policy. No unmeasured improvement is claimed. |

## Thumbnail and visual plan

**Thumbnail asset `thumbnail.png`:** Finished 9:16 cover with a central 1:1 safe zone. Face-led if an approved real portrait is supplied; otherwise finished editorial type. Warm off-white, charcoal type, muted lime highlight. Exact copy: `SAME AGENT. THREE LEVELS.` and small `DIWALI FLIGHT`. Add a simple ticket glyph. No salary figures on cover until sourced. No airline logo, fake app UI, robot, terminal dump or tiny type. Alt text: “Three agent-design answers to one Diwali flight rebooking question.”

**B-roll production list:** Record the opening and level introductions as face-led A-roll. These eight assets are the inserts needed to make each claim visible. Use 1080 × 1920, keep key text inside the central safe zone, and label all itinerary graphics `ILLUSTRATIVE`. The only live-action insert is creator-shot; the rest are clean editorial motion graphics or stills, never simulated airline product screens.

| Asset | Insert window | Exact visual and on-screen copy | Source / edit instruction |
|---|---|---|---|
| `b01-travel-cancel.mp4` | 7–12s | Suitcase by the door, subtle Diwali lights, phone or paper ticket with large `CANCELLED` overlay. Establish the human stakes. | Shoot original 9:16 footage; hide personal booking details and airline branding. Place the status as editorial overlay, not a fake app notification. |
| `b02-constraints.png` | 12–16s | One large card: `₹10K PAID` · `+₹5K MAX` · `HOME BEFORE DIWALI`; beneath it, `FREE REROUTE → TOO LATE`. | Finished graphic; no replacement fare or invented route time. |
| `b03-l5-tool-loop.mp4` | 16–27s | Animate one call and result at a time: `RIGHTS → SEATS → QUOTE → APPROVAL → BOOK → STATUS: CONFIRMED`. A `₹5K CAP` lock sits on `BOOK`. | Editorial motion graphic. Each node appears only when named; avoid a six-box dashboard on one frame. Reuse the final confirmation frame after L6. |
| `b04-l6-skill-card.png` | 27–31s | Large `SKILL = REBOOKING PLAYBOOK`; three input chips `BOOKING · DEADLINE · SPEND CAP`; small rule `PRICE CHANGED → NEW APPROVAL`. | Finished still with legible type. This depicts instructions/state, not a new external tool. |
| `b05-l6-parallel-requote.mp4` | 31–40s | After `BOOKING LOOKUP`, split to simultaneous `RIGHTS` and `SEATS`; converge at `QUOTE`. A changed-quote result refreshes quote and consent only, then lands on `CONFIRMED`. | Motion graphic; animate simultaneous reads to convey shorter wall time without claiming fewer mandatory calls. |
| `b06-l7-policy.mp4` | 40–51s | `GOAL: HOME ON TIME` → `OBSERVE: RIGHTS · FARE · SEAT` → `DECIDE: ANOTHER CALL WORTH THE DELAY?`; bounded routes `RE-QUOTE`, `BOOK AFTER APPROVAL`, `HAND OFF`. | Motion graphic with only one route visible per frame. The handoff branch represents uncertain rights or price, not this successful case. |
| `b07-l7-feedback.mp4` | 51–60s | `BOOKING TOOL → TICKET STATUS → CONFIRMED → STOP`; secondary branches `PENDING → RECHECK` and `FAILED → REPLAN`. Finish with small `CONFIRMED · p95 TIME · CAP BREACHES`. | Motion graphic. Show returned status as a new observation, not as a claim that submitting a booking equals success. Reveal secondary branches sequentially to keep the phone frame readable. |
| `b08-confirmed-stamp.png` | Reuse at 26s, 39s, 58s | Large `TICKET CONFIRMED` stamp, identical across L5, L6 and L7. | Transparent overlay so the three outcomes look matched. No fabricated ticket number. |

**Edit note:** The B-roll carries the mechanics while the speaker remains on screen for the salary hook and each level label. Do not add generic plane takeoff footage, a robot, code rain, or an invented airline interface; none would prove a tool result or decision.

## QA report

**Editorial scores (0–10):** hook 8.0, clarity 8.5, technical accuracy 8.5, brand fit 8.5, originality 8.0, share potential 7.5, save potential 8.5, visual potential 8.0, learning value 8.5, execution against brief 8.5, AI hype penalty 0.5, generic content penalty 0.5. Deterministic composite: **8.005**; failed numeric gates: **none**. Section coverage: all six brief sections. Thesis drift: none. Spoken script: approximately **143 words in 60 seconds**; a real read-through is still needed.

**Factual checks:** Salary source, geography, period, annual compensation definition and sample size. Hypothetical customer-support case. Do not present the answers as Amazon's official rubric or assert that any one answer earns a salary. If a live airline provider does not offer a particular tool or hold capability, the interview answer must state the integration assumption rather than invent it.

**Verdict: REVISE** until salary provenance and spoken timing are checked. The required `python cli.py check <brief>` command was attempted, but this checkout has no `check` subcommand; the brief passed Pydantic model validation and the numeric QA gates were evaluated directly.
