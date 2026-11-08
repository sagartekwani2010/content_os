# Diwali flight agent: six-asset B-roll cut — eighth pass

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

**Story:** salary bar first → cancellation and constraints as two simple PNGs → L5 complete tool loop → L6 reusable skill → L7 goal, observation, policy, action, result and stop condition in one two-beat video. The L7 choice to make another tool call is governed by its expected decision value and delay. **Main risk:** compensation numbers are creator supplied and need provenance before publication; level answers are illustrative.

## Hook options

1. **Selected, comparison:** “Amazon Applied Scientist: L5, ₹90 lakh. L6, ₹1.5 crore. L7, ₹2.5 crore. Same agent question.” It promises a level comparison and uses the creator's salary hook.
2. **Outcome first:** “Three candidates book the same Diwali replacement. Only one designs the agent's autonomy.” This emphasizes the result and the final design decision.
3. **Mistake:** “A flight agent with six tools can still be slow.” This opens the tool-call and latency tension.

## Content package — 60-second spoken script

| Time | Spoken script | On-screen proof |
|---|---|---|
| 0–7s | “Amazon Applied Scientist: L5, ₹90 lakh. L6, ₹1.5 crore. L7, ₹2.5 crore. Same agent question.” | `01-salary-bars.png` fills the opening frame. Three bars start at zero; each has its approximate salary label. |
| 7–11s | “₹10,000 Diwali flight cancelled.” | `02-cancelled-flight.png`: one ticket graphic stamped `CANCELLED`. |
| 11–16s | “You can add ₹5,000. Free reroute misses Diwali. All three must confirm a ticket.” | `03-travel-constraints.png`: `₹10K PAID · +₹5K MAX · HOME BEFORE DIWALI`; free option `TOO LATE`. |
| 16–27s | “L5: Tools read or change airline systems. I check rights and seats, quote the fare, ask approval, book, then verify confirmation. The booking service enforces the ₹5,000 cap.” | `04-l5-tool-calls.mp4`: calls and results reveal in order; final frame `TICKET CONFIRMED`. |
| 27–40s | “L6: A skill is the playbook for those tools. The agent keeps booking state, checks rights and seats in parallel, and re-quotes with fresh approval if prices change. Then books and verifies.” | `05-l6-rebooking-skill.png`: one static skill diagram with parallel reads, changed-quote branch and `TICKET CONFIRMED`. |
| 40–60s | “L7: Goal: confirmed on-time travel. Observe rights, fare and seats. My policy chooses: re-quote, book after approval, or hand off—based on whether another call is worth the delay. The booking tool acts; ticket status returns. Confirmed means stop; failure means replan. That’s bounded autonomy.” | `06-l7-agent-loop.mp4`: beat 1 chooses `RE-QUOTE / BOOK / HAND OFF`; beat 2 applies `BOOK` and returns `CONFIRMED → STOP`, with failed status looping to replan. |

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

**Minimum B-roll list: six files total.** The salary bar is the first visual. Use 1080 × 1920, keep essential text inside the central safe zone, and label the hypothetical travel cards `ILLUSTRATIVE`. No additional stock clips or separate confirmation overlay are needed; each level asset ends on its own identical green `TICKET CONFIRMED` card.

| File | Type and timing | Required content | Production instruction |
|---|---|---|---|
| `01-salary-bars.png` | PNG, 0–7s | Three zero-baseline bars labelled `L5 ≈₹90L`, `L6 ≈₹1.5Cr`, `L7 ≈₹2.5Cr`; small `Creator-supplied estimates`. | Clean horizontal comparison, one scale, large labels; final numbers need source verification before publishing. |
| `02-cancelled-flight.png` | PNG, 7–11s | Generic ticket card `₹10,000 PAID` with a bold `CANCELLED` stamp and small Diwali travel cue. | Editorial ticket illustration, no airline logo, real PNR or fake airline app UI. |
| `03-travel-constraints.png` | PNG, 11–16s | `+₹5,000 MAX`, `HOME BEFORE DIWALI`, `FREE REROUTE → TOO LATE`; the viable paid alternative stays unpriced. | Three large facts only. This card establishes the success condition before the technical answers. |
| `04-l5-tool-calls.mp4` | Video, 16–27s | One call/result at a time: `RIGHTS → SEATS → QUOTE → APPROVAL → BOOK → STATUS: CONFIRMED`; put `₹5K CAP` guard on booking. | Single legible animated tool trace, not a dense dashboard. Use the same green confirmation end frame as L6 and L7. |
| `05-l6-rebooking-skill.png` | PNG, 27–40s | `SKILL = REBOOKING PLAYBOOK`; inputs `BOOKING · DEADLINE · CAP`; arrows show rights and seats read in parallel; `PRICE CHANGED → RE-QUOTE + NEW APPROVAL`; end `CONFIRMED`. | One static diagram, revealed by editor crop/highlight rather than another video. The skill guides tool use; it is not an airline API. |
| `06-l7-agent-loop.mp4` | One video, 40–60s | **Action 1, 40–50s:** `GOAL → OBSERVE RIGHTS/FARE/SEATS → POLICY: RE-QUOTE / BOOK / HAND OFF`, with the question `ONE MORE CALL WORTH THE DELAY?`. **Action 2, 50–60s:** booking tool acts after approval; ticket-status observation returns `CONFIRMED → STOP`, with small `FAILED → REPLAN` branch. | Keep these as two beats inside one file. On the book path show fresh quote, exact approval and ₹5K cap. End on the same green confirmation frame. |

**Edit note:** The salary bars open full-frame. Creator A-roll can appear as a small picture-in-picture or between these six inserts; it does not require another B-roll asset. Avoid generic plane footage, robots and invented airline screens, which would add editing time without showing the agent's decision.

## QA report

**Editorial scores (0–10):** hook 8.0, clarity 8.5, technical accuracy 8.5, brand fit 8.5, originality 8.0, share potential 7.5, save potential 8.5, visual potential 8.0, learning value 8.5, execution against brief 8.5, AI hype penalty 0.5, generic content penalty 0.5. Deterministic composite: **8.005**; failed numeric gates: **none**. Section coverage: all six brief sections. Thesis drift: none. Spoken script: approximately **143 words in 60 seconds**; a real read-through is still needed.

**Factual checks:** Salary source, geography, period, annual compensation definition and sample size. Hypothetical customer-support case. Do not present the answers as Amazon's official rubric or assert that any one answer earns a salary. If a live airline provider does not offer a particular tool or hold capability, the interview answer must state the integration assumption rather than invent it.

**Verdict: REVISE** until salary provenance and spoken timing are checked. The required `python cli.py check <brief>` command was attempted, but this checkout has no `check` subcommand; the brief passed Pydantic model validation and the numeric QA gates were evaluated directly.
