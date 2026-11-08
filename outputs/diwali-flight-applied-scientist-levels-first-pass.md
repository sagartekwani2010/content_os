# Diwali flight agent: L5, L6 and L7 first pass

Status: **REVISE before publication**. This is an illustrative interview case, not an Amazon interview question or official leveling rubric.

## Brief fingerprint

- Topic: Three Applied Scientist answers to a Diwali flight rebooking agent question
- Core thesis: Strong agent design grows from recommending a valid option, to completing a changing tool workflow, to defining and evaluating safe autonomy. The three answers are illustrative scopes, not Amazon's official interview rubric.
- Learning objective: Viewers can distinguish a valid recommendation, reliable execution and a verified customer outcome in an agent design answer.
- Format: Reel
- Brand pillar: Become AI-Native: Career & Leadership (`ai_career`)
- High-level sections: Diwali flight cancellation and ₹10,000 original fare with ₹5,000 extra-spend limit; L5 valid option and evaluation; L6 stateful rebooking skill and action control; L7 autonomy boundary and outcome evaluation; transferable distinction between recommendation, execution and verified outcome.

## Execution plan

**Learning payoff:** Tell apart a recommendation, an attempted action and a verified customer outcome. **Story spine:** salary ladder → familiar cancellation → competent L5 answer → seat disappears → L6 handles rebooking → booking pending → L7 defines safe autonomy → practical rule. **Visual rule:** one idea per beat, face-led, large state labels. **Risk:** the compensation figures are creator-supplied and lack source metadata; do not publish the salary claim until checked. The exact meaning of “₹5,000 more” (immediate cash versus final net cost after a refund) is a clarification the agent must make if it affects the recommendation.

## Hook options

1. **Selected, comparison:** “₹90 lakh. ₹1.5 crore. ₹2.5 crore. Same agent design question. What changes?” The numbers earn attention; the story supplies the answer.
2. **Failure reveal:** “The AI found a Diwali flight home. The customer still had no ticket.” Stronger failure hook, less explicit career framing.
3. **Mistake:** “A seat in search results is not a seat you can book.” Strong technical claim, narrower reach.

## Content package — first-pass Reel, about 42 seconds

| Time | Voiceover, paste-ready | On-screen copy and visual | New information |
|---|---|---|---|
| 0–4s | “₹90 lakh. ₹1.5 crore. ₹2.5 crore. Same agent design question. What changes?” | Face-led; three large level and salary cards. Small persistent label: “Illustrative answers.” | Same question, three scopes. |
| 4–9s | “Your ₹10,000 Diwali flight is cancelled. You can add ₹5,000, max. Design the support agent.” | Minimal ticket card: “₹10k paid · +₹5k max · home before Diwali.” | Exact customer constraint. |
| 9–17s | “L5: I’d check rebooking rights, search live seats, rank on-time routes by actual extra cost, and test deadline and budget violations.” | `booking → entitlement → live options`; stamp `L5 ≈ ₹90L`. | A competent answer defines the task and tests its output. |
| 17–19s | “Then the seat vanishes.” | Clean card: `SEAT EXPIRED`; no fake app screenshot. | A valid recommendation can become invalid. |
| 19–29s | “L6: I’d build a rebooking skill: quote, get approval, book, verify. Fare changed? The agent replans. The booking tool blocks overspend.” | `QUOTE → APPROVE → BOOK → VERIFY`; after “fare changed,” arrow back to `SEARCH`; stamp `L6 ≈ ₹1.5Cr`. | Agent chooses the next step; deterministic tool enforces spend. |
| 29–31s | “But the booking stays pending.” | Clean card: `BOOKING PENDING`. | Tool call success is not customer success. |
| 31–39s | “L7: I’d define when the agent acts, retries or hands off. Simulate price jumps and uncertain bookings. Measure confirmed tickets within budget, not chat resolution.” | State decision: `CONFIRMED? yes → close / no → retry or hand off`; stamp `L7 ≈ ₹2.5Cr`. | Safe autonomy requires a stop rule and outcome evaluation. |
| 39–42s | “The ladder: recommend, execute, verify.” | Three large words, one at a time; face-led close. | Reusable answer structure. |

**Caption:**

Finding a flight is the easy part. The seat can disappear, the fare can change, and a booking request can stay pending.

For this illustrative agent-design case, I would separate three questions: Did it recommend a valid option? Did it execute within the customer’s limit? Did the customer receive a confirmed ticket?

The Amazon compensation estimates shown are from my dataset and need source details checked before publication. These are example answer scopes, not Amazon’s interview rubric.

**CTA:** “Which transition would you test first: expired seat, changed fare, or pending booking?”

## Thumbnail and visual plan

**Thumbnail (`thumbnail.png`):** Finished 9:16 editorial cover, central 1:1 safe zone. Off-white background; Sagar portrait if an approved real photo is available, otherwise a clean type-only layout. Exact headline: “SAME AGENT QUESTION”. Subline: “L5 · L6 · L7”. Small ticket cue: “DIWALI FLIGHT CANCELLED”. No salary figure on thumbnail until verified; no airline logo, robot or fake interface. Alt text: “Three Applied Scientist levels compared through a cancelled Diwali flight agent question.”

**Scene assets:** All scenes use a real talking-head or approved avatar recording with editorial text overlays; no generated media is necessary. Render one phone-safe state card for each reveal: `SEAT EXPIRED` (`04-seat-expired.png`) and `BOOKING PENDING` (`06-booking-pending.png`), and one `QUOTE → APPROVE → BOOK → VERIFY` process card (`05-rebooking-skill.png`). Cards are finished 9:16 assets with charcoal type, warm light background and one muted lime highlight. No fabricated airline UI or company logos. The salary cards need a source note in the final edit. Each scene shows one state or decision, with the two failure cards supplying the story turns.

## QA report

Preliminary editorial scores (0–10): hook strength 8.0; clarity 7.5; technical accuracy 7.5; brand fit 8.5; originality 7.0; share potential 7.5; save potential 7.0; visual potential 7.5; learning value 7.5; execution against brief 8.0; AI hype penalty 1.0; generic content penalty 1.0. Weighted composite using the configured weights and penalty rule: **7.135**. Numeric hard gates: **none failed**. Section coverage: **all five sections present**. Thesis drift: **none**.

**Required factual checks:** Verify the compensation source, geography, annual period, total-compensation definition and sample size; label the answer scopes and travel case as illustrative. Confirm that the audience can understand “actual extra cost” without implying a cancelled ticket is automatically a ₹10,000 credit. The budget ambiguity should be stated in the companion case study.

**Verdict: REVISE.** The story and technical structure are ready for creator review, but the salary claim is not publish-ready until its source details are attached. The script may also need a speaking-speed trim after a read-through.
