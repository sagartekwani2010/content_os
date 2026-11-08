# Diwali flight agent: scientist-led 60-second fourth pass

Status: **REVISE before publication**. This is an illustrative interview case, not an official Amazon interview or leveling rubric. Earlier drafts remain preserved.

## Brief fingerprint

- Topic: Three Applied Scientist answers to a Diwali flight rebooking agent question
- Core thesis: All three Applied Scientist answers must deliver a confirmed ticket within the customer's constraints. Their scientific judgment grows from identifying a viable option with a measurable baseline, to choosing the option most likely to achieve the customer's outcome under uncertainty, to deciding when autonomous booking is justified using unbiased evaluation and risk limits. The answers are illustrative scopes, not Amazon's official interview rubric.
- Learning objective: Viewers can distinguish three scientific questions in agent design: which option fits, which viable option is most likely to work, and when the agent should act autonomously.
- Format: Reel
- Brand pillar: Become AI-Native: Career & Leadership (`ai_career`)
- High-level sections: Diwali flight cancellation and ₹10,000 original fare with ₹5,000 extra-spend limit; all three answers produce a confirmed on-time ticket; L5 viable choice, approval and measured baseline; L6 outcome likelihood under changing observations; L7 autonomy policy, selection bias and online evaluation; progression from fit to reliability to justified autonomy.

## Execution plan

**Viewer payoff:** Identify three increasingly demanding scientific questions in agent design, without treating an L5 answer as a failure. **Story:** salary ladder → familiar Diwali disruption → confirmed-ticket outcome stated upfront → L5 asks “which option fits?” → L6 asks “which one is most likely to work?” → L7 asks “when should the agent act alone?” **Case assumption:** an on-time replacement exists within the ₹5,000 additional-spend limit; its fare is intentionally omitted. A second eligible route with a tight connection supplies a concrete reliability trade-off. Each candidate ends with a confirmed on-time ticket. **Visual evidence:** a constraint card, a route comparison, and an action/handoff threshold card; all return to the same green confirmed-ticket outcome. **Risks:** salary data needs provenance; a short Reel cannot prove the proposed models outperform the baseline, so the language remains a design answer rather than a claimed result.

## Hook options

1. **Selected, comparison:** “In my salary data: Amazon Applied Scientist L5, ₹90 lakh; L6, ₹1.5 crore; L7, ₹2.5 crore. Same question.”
2. **Outcome first:** “All three scientists got a Diwali traveller a ticket. Their scientific questions were different.”
3. **Mistake:** “A chat agent that books a ticket is only the start of the science problem.”

## Content package — approximately 60 seconds

| Time | Spoken script | On-screen copy and visual purpose |
|---|---|---|
| 0–7s | “Amazon Applied Scientist: L5, ₹90 lakh. L6, ₹1.5 crore. L7, ₹2.5 crore. Same question.” | Face-led; three salary cards, all `≈`; small label `Illustrative answer scopes`. |
| 7–16s | “Your ₹10,000 Diwali flight is cancelled. You can add ₹5,000. Free reroute arrives too late. Design the agent.” | Ticket card: `₹10K PAID · +₹5K MAX · HOME BEFORE DIWALI`. Free option stamped `TOO LATE`. |
| 16–19s | “All three confirm a ticket.” | Same green `TICKET CONFIRMED` outcome card under all levels. |
| 19–31s | “L5: I check rebooking rights, live arrival time and final extra cost. I get exact-fare consent, book, verify the ticket, and test for constraint violations.” | Large question `WHICH FLIGHT FITS?`; trace `booking + policy → live options → valid route → consent → confirmed`. Metric chip: `deadline/budget violations`. |
| 31–46s | “L6: Earliest flight, tight connection. I estimate which valid route is likeliest to arrive on time using live delay data. If a seat disappears, the agent replans, refreshes the quote, books and verifies. I compare it with L5’s baseline.” | Large question `WHICH ROUTE GETS THEM HOME?`; two eligible route cards with qualitative reliability, no invented probabilities. Show `seat unavailable` tool result → rerank → fresh quote → confirmed ticket. Metric chip: `on-time confirmed tickets versus rules baseline`. |
| 46–60s | “L7: I decide when automation beats a human queue. Past outcomes cover only offered routes, so I validate with guarded trials. Fresh quote, exact consent, and calibrated low risk? Auto-book and verify. Otherwise hand off.” | Large question `WHEN MAY IT ACT?`; `AUTO-BOOK` or `HAND OFF` decision. Label the risk as `missed arrival or unauthorized spend`; main-case branch reaches `TICKET CONFIRMED`. End card: `FIT → OUTCOME → AUTONOMY`. |

**Caption:**

Three Applied Scientists can all get the traveller a confirmed ticket. Their answers differ in the scientific decision they take responsibility for.

The L5 answer establishes a viable, measured baseline. L6 estimates the chance of an on-time arrival among eligible routes, then replans when a live seat check changes the available set. Its offline and live evaluation should compare confirmed on-time tickets with the L5 baseline, including calibration and failure cases. L7 sets the decision policy for booking versus handoff: human queues have delay costs too, but the agent may act only after an exact fare approval and a fresh quote within the hard ₹5,000 cap. Past support logs selectively contain the routes earlier agents offered; customer outcomes for unoffered routes are missing. Use stress tests and randomized, guarded trials among safe alternatives to calibrate the policy, then monitor missed arrivals, handoff delays and unauthorized spend.

The Diwali case and level answers are illustrative, not Amazon's interview rubric. The compensation figures are creator-supplied estimates that need source details checked before publication.

**CTA:** “Which question is hardest in your agent: fit, reliability or autonomy?”

## Scientific decision behind each answer

| Level | Question owned | Testable claim | Decision and evidence |
|---|---|---|---|
| L5 | Can the agent reliably find and complete a valid rebooking? | A rules baseline can avoid deadline and budget violations while reaching a confirmed ticket. | Policy and booking tools return entitlement, final extra charge, live seats and confirmation status; consent is tied to the exact fare. Test success and constraint errors on cancellation cases. |
| L6 | Which eligible route maximizes the chance of a confirmed, on-time arrival? | A calibrated route choice can improve the customer outcome over L5's rules baseline, especially when a tight connection or changed inventory makes the advertised arrival misleading. | The agent uses live delay and seat observations to update its choice, refreshes the quote, then books and verifies. Evaluate on-time confirmations, calibration and failures against the baseline; do not claim improvement before measuring it. |
| L7 | When is autonomous booking better than waiting for a human? | A decision policy can trade the risk of a bad automatic action against the cost of a human queue, while keeping exact consent and the spending cap inviolable. | Historical logs cover routes earlier agents offered, so offline evaluation alone cannot establish the policy's value. Stress-test disruptions, run guarded randomized trials among safe alternatives, calibrate auto-book versus handoff thresholds, and monitor customer outcomes and unauthorized spend. |

## Thumbnail and visual plan

**Thumbnail (`thumbnail.png`):** Finished 9:16 cover with central 1:1 safe zone, approved real portrait if available, otherwise type-led. Warm off-white, charcoal text, muted lime decision highlight. Exact headline: `SAME AGENT QUESTION`; subline: `L5 · L6 · L7`; small ticket cue `DIWALI FLIGHT`. Keep salary figures off the cover until verified. No airline logos, fake app UI, robot or dense dashboard. Alt text: “Three scientific scopes for the same flight support agent question.”

**Scene assets:** Face-led footage or approved avatar plus finished phone-safe editorial cards. `02-customer-constraint.png`: ₹10K original fare, +₹5K limit, deadline, and too-late free route. `03-confirmed-ticket.png`: one green confirmed-ticket outcome card reused after each answer. `04-fit.png`: booking and policy tool evidence narrowed to a valid route. `05-reliability.png`: two eligible routes, one with a tight connection; `seat unavailable` tool response causes a rerank and fresh quote. `06-autonomy.png`: fresh quote and exact consent meet a calibrated risk threshold, leading to booking; uncertain cases lead to handoff. These are illustrative case diagrams, never simulated airline product screenshots. The visual trace is observed booking/policy evidence → bounded option → customer consent → confirmed ticket; L6 adds a changed tool observation and replan; L7 adds a safe action boundary.

## QA report

Preliminary editorial scores (0–10): hook strength 8.0; clarity 8.0; technical accuracy 8.0; brand fit 8.5; originality 8.0; share potential 7.5; save potential 8.0; visual potential 7.5; learning value 8.5; execution against brief 8.5; AI hype penalty 0.5; generic content penalty 0.5. Configured weighted composite: **7.855**; numeric gates failed: **none**. Spoken script: **140 words in 60 seconds** (about 140 words/minute overall); the L6 beat is the fastest and still needs a real read-through. All six brief sections are covered. Thesis drift: none.

**Factual checks:** Verify the salary source, geography, period, annual total-compensation definition and sample size. Keep the scenario hypothetical. The statement about biased historical logs is a methodological inference about selectively offered options; some unchosen flight outcomes may still be observable, while customer-specific results for unoffered choices are not. "Calibrated low risk" means a pretested estimate of a confirmed on-time arrival under the spending and approval constraints, not the model's own verbal confidence. Do not imply the three answer scopes are Amazon's official expectations or that a particular answer causes a salary.

**Issues and required changes before publishing:** Attach salary provenance with geography, period and compensation definition; record a spoken read-through and trim the L6 beat if needed. **Verdict: REVISE** until those checks are complete. The earlier drafts remain available for comparison.
