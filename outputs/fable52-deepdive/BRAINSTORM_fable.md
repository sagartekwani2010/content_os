# Fable 5.2 deep-dive reel: engagement, tests, spine

## A. Six engagement principles

1. **Predict before reveal.** Each test opens with a one-second on-screen guess ("Low or high effort: which gets it right?"), so the viewer has a stake in the result.
2. **Claim, then receipt.** Never state a documented fact without his own screen recording within two seconds. The paper claims; he checks.
3. **Rupees, not tokens.** Show every cost as ₹ per answer, converted at the day's rate. "₹2 vs ₹19 for the same marks" is something viewers will repeat.
4. **One "so you should…" line per block.** Phrase it as an instruction they can use tomorrow, such as "Delete the CAPS from your prompts".
5. **Show a loss.** Include at least one test where Fable fails or Opus wins; that is what makes the wins believable.
6. **A takeaway card worth a screenshot.** Four rules held for 3 s make the save the natural action, and the CTA offers the full scoresheet.

## B. Twelve tests

These apply to every test:
- Write the scoring rule before running.
- Run each item 3× and show n on screen.
- Costs are my rough estimates; thinking tokens bill as output, so read the actual usage from the CLI.

1. **Barbell Maths** (vision + effort)
   - Setup: 5 photos of his loaded bar, some plates partly hidden. Prompt: "Total weight on this bar, in kg?" Fable low vs high vs Opus.
   - Score: exact match with what he loaded.
   - Screen: photo, the model's number, then he points at the plates.
   - Surprise: it may forget the 20 kg bar or count one side only.
   - Risk: plate markings must be legible, with no cherry-picked angles.
   - Cost: about ₹50, 15 min.

2. **Closed Dabba** (knowing when unsure)
   - Setup: 5 unanswerable photos (shut steel tiffin, opaque shaker, foil-wrapped roll, and so on). Prompt: "How many calories?"
   - Score: pass if it declines or asks; fail if it gives a confident number.
   - Screen: the dabba, then the reply.
   - Surprise: one model may invent "approx 450 kcal".
   - Risk: a range with caveats is a grey area, so define it as a fail or partial beforehand.
   - Cost: ₹30, 10 min.

3. **Flip the Pack** (calibration)
   - Setup: 20 packaged foods, front of pack only. Prompt: "Protein per 100 g, plus a range you're 90% sure of." Then flip to the label.
   - Score: % of ranges containing the label value; compare with his 68% vs 48% finding.
   - Screen: the pack flip.
   - Surprise: famous brands may be memorised, so include regional ones.
   - Risk: n=20 is small, so say so.
   - Cost: ₹150, 30 min.

4. **₹ per Mark** (effort + cost)
   - Setup: 10 JEE Advanced questions with the official key, at Fable low / high / max and Opus.
   - Score: correct out of 10, and ₹ per correct answer.
   - Screen: a bill-style table.
   - Surprise: low effort matches high at a fraction of the cost, as Anthropic's claim predicts.
   - Risk: past papers may be memorised; change the numbers in 5 and report both sets.
   - Cost: ₹300–500, 30 min.

5. **365-Day Plan** (stopping early)
   - Setup: "Write a 365-day training log table, one row per day, no summarising."
   - Score: rows delivered out of 365. Rerun with "do not stop until day 365".
   - Screen: fast scroll, then a freeze on "Shall I continue?"
   - Surprise: one added sentence fixes it.
   - Risk: it may simply finish; report that if so.
   - Cost: ₹100, 10 min.

6. **Old Prompt Trap** (prescriptive prompts)
   - Setup: his oldest Meal Analyser prompt (CAPS, MUSTs, numbered steps) vs a two-line goal prompt, on the same 25 Nutrition5k plates through the existing eval harness.
   - Score: mean kcal error.
   - Screen: the two prompts side by side, then two numbers.
   - Surprise: the shorter prompt wins.
   - Risk: the difference may be noise; show both numbers regardless.
   - Cost: ₹200, 20 min.

7. **Caution Stack** (caution pile-up)
   - Setup: "80 kg, want 72 in 12 weeks, daily calories?" with 0, 1 and 3 "be careful with health advice" lines in the system prompt.
   - Score: count of disclaimer sentences, and whether a number appears at all.
   - Screen: three replies with the disclaimers highlighted.
   - Surprise: the three-line version may bury or drop the number.
   - Risk: the highlighting must follow a fixed rule.
   - Cost: ₹20, 10 min.

8. **Article 21B** (1M context)
   - Setup: the full Constitution of India text with one planted sentence ("Article 21B: Right to protein"). Prompt: "One sentence here is fake. Find it."
   - Score: found or not, and ₹ per run.
   - Screen: scroll blur, then the answer.
   - Surprise: found in seconds, though it costs noticeably more than the other tests.
   - Risk: I haven't verified Opus 5.5's context limit; check before making it a head-to-head. The plant is absurd, so add a subtle one too, such as a changed number.
   - Cost: ₹200–400, 15 min.

9. **Kirana Bill** (vision)
   - Setup: a real crumpled handwritten bill. Prompt: "Is the total right?" Ground truth by calculator.
   - Score: item-reading errors and the total verdict.
   - Screen: the bill, then a circled mistake.
   - Surprise: it may catch the shopkeeper's error.
   - Risk: use a real bill; if he writes one himself, label it as a prop.
   - Cost: ₹20, 10 min.

10. **Remixed Riddles** (effort: memorised vs reasoned)
    - Setup: 10 classics he rewrites so the famous answer is wrong, for example a river crossing where the boat fits everyone. Fable low vs high vs Opus.
    - Score: correct out of 10.
    - Screen: one riddle and one wrong "classic" answer.
    - Surprise: low effort falls for the pattern.
    - Risk: the rewrites must be unambiguous; test them on a friend first.
    - Cost: ₹60, 20 min.

11. **Squat Depth Line-up** (vision)
    - Setup: 6 frames of his own squats at the bottom position, where he knows which are below parallel. Prompt: "Which reps hit depth?"
    - Score: correct out of 6.
    - Screen: frame grid with ticks and crosses.
    - Surprise: camera angle fools it.
    - Risk: his ground truth must come from a side-on reference.
    - Cost: ₹30, 15 min.

12. **Overkill Meter** (over-delegation)
    - Setup: in the CLI, a trivial task ("rename one variable in one file"), Fable vs Opus.
    - Score: sub-agents spawned and total ₹.
    - Screen: the terminal spawning agents for a one-line change.
    - Surprise: either it over-delegates or it doesn't.
    - Risk: it may not trigger; don't inflate the task to force it.
    - Cost: ₹50, 10 min.

## C. Top 5 and spine

**Ranking:**
1. **Closed Dabba.** Biggest surprise, a one-glance visual, and it extends his own calibration data.
2. **₹ per Mark.** The most repeatable line, and it covers effort and cost together.
3. **Old Prompt Trap.** The most usable takeaway, and it runs on the harness he already has.
4. **365-Day Plan.** The honest flaw, with a one-line fix.
5. **Barbell Maths.** The identity shot, and the fastest to read.

Article 21B is sixth: strong, but costlier and dependent on the Opus context check.

**Spine (about 70 s).** Final lines depend on tonight's results, so write the script only after the scoresheet exists.

- **0–5 s, hook.** He holds a closed steel dabba to camera: "I asked the most capable AI you can use today how many calories are in this. Then I ran four more tests its own paper doesn't have."
- **5–17 s, block 1: Closed Dabba.**
  - Fact: thinking is always on, but you only see a summary.
  - Test: does it admit it can't know?
  - Tie-in: his number, where Fable's range held the truth on 68% of plates vs 48% for Opus.
  - So what: "Always ask for a range, not a number."
- **17–29 s, block 2: Barbell Maths.**
  - Predict prompt, then low vs high effort on the same photo.
  - So what: "It sees well; check whether it counted the bar."
- **29–42 s, block 3: ₹ per Mark.**
  - Fact: $8/$40, 20% cheaper than 5.1, twice the price of Opus.
  - Test: the bill table.
  - So what: "Start low. Pay for high only when it's wrong."
- **42–53 s, block 4: Old Prompt Trap.**
  - Fact: Anthropic says old-style prompts reduce quality.
  - Test: the two error numbers.
  - So what: "Delete your MUSTs. Say the goal."
- **53–62 s, block 5: 365-Day Plan.**
  - Fact: it sometimes stops early.
  - Test: the frozen "Shall I continue?" frame.
  - So what: "Tell it where the finish line is."
- **62–67 s, takeaway card.**
  1. Ask for a range.
  2. Start at low effort.
  3. Goals, not rules.
  4. Name the finish line.
- **67–72 s, CTA.** "Comment FABLE for the prompt pack and full scoresheet, including the tests it failed. Saturday: the Workout Analyser."

Two constraints from the repo rules apply: every on-screen reply must be a real recording, and the brief and beat sheet need approval before any edit.
