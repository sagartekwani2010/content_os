## MUST-FIX

1. **"REAL: 11" (beat 6 on-screen text, K8).** The count of 11 comes from the labeller, which is Fable working at confidence 0.6, not ground truth. Either count the reps by hand and record that, or relabel it "AI COACH: 11".
2. **"Two AIs agreeing" (caption).** The labeller and the judge are the same model, Fable 5.2, in two roles with different inputs, so this overstates how independent the check is. Say so: "same model, two roles (frames only vs pose data)". Calling the labeller "a second AI coach" without naming it as Fable hides the same thing.
3. **Beat 6 breaks the one-sentence rule.** It has 19 words and two claims in 5.2 s, about 200 wpm even before the 1.1x speed-up. Beats 5 and 7 (15–16 words) are also fast. Split beat 6, for example "My tool counted fourteen reps. On eleven." and let the 11° dip be text-only, or trim each line.
4. **The wall of ticks overstates (beat 2, K2).** The draft puts a green tick on every clip except the X. Clips where the guardrail fired, IMG_2649 included, must show a grey "can't see" mark, and any HOLD needs its own mark. A tick should mean the judge actually said CONTINUE.
5. **The pose-maths label exists only in the notes.** The gate note says the ghost and red gap "are labelled as pose maths", but no on-screen text does this. In beats 10/K14 the red gap fills and then the judge's stamp lands, which implies Fable saw the gap. Add a small "POSE MATHS" tag to the gap, or reword the note.
6. **Arithmetic in the caption and the beat 6 notes.** "2 half reps + 1 tracker jump" implies 14 − 3 = 11. FACTS does not say the labeller left out reps 1 and 14. Check this before implying the numbers reconcile.

## SHOULD-FIX

1. **Hook 3** says "My AI counted fourteen". That was the pose tool, not the judge. Use "My pose tracker…". It also repeats the payoff of beat 6, so beat 6 needs a new line if hook 3 wins.
2. **The 2/3 re-hook comes late.** Beat 9 starts at 32.8 s, which is 71% of a 46 s reel; 2/3 is about 30.7 s. Trimming beats 5–7 fixes this.
3. **Beat 7 "now it says…" and K11 "guardrail output"** need confirmation that the guardrail has actually run on IMG_2649. FACTS lists it as the fix but gives no measured output.
4. **The knee-trail unroll (K4→K5).** The trail is the knee's position path, but the graph is angle over time. Make the morph a transition only, and plot the final graph from computed angles, not from the reshaped trail.
5. **Brief deviations.** The blind-test scoreboard shrank to a corner tally, and the verdict stamp moved off the desk. Only the ghost swap is flagged. Flag both, or restore them.
6. **"17 DOTS · EVERY FRAME"** ignores the 3.1% of frames with no usable pose. Use "17 DOTS · 30 FPS".
7. **Grey joints in beat 3** spoil the guardrail reveal in beat 7. Keep beat 3 all-blue.
8. **Calendar risk.** Beats 1, 2, 8, 10, 11, K1–K2, K12–K17 and the caption all depend on the judge run and the [BAD_SET]/[BEST_SET] pair, two days before posting. Add a named fallback reel in case no same-angle pair or no STOP exists.

**Passes:**
- No "stopped me live" claim; "would have" is used consistently.
- Beat 1 is not a recap, and the result lands by about 6.5 s.
- E/H alternation is correct.
- About 46 s total.
- One save asset.
- The comment trigger is conditional and honest.
- The reel ends on a loop.
- Unmeasured values stay as slots.