# Check: Gym Jarvis Ep 3 reel package

## MUST-FIX

1. **The "one set" claim is hard-coded.** Beat 2 says "the one set" on screen ("ONE RED X") and in speech. Hook 2 and the K2 X count say the same. The script flags this dependency, but the text still asserts it. Make the count a slot, `[N_STOP]`, and write a fallback line for the case where it isn't 1.

2. **Beat 3 credits the wrong component.** "First it pins seventeen joints" uses "it", which in beat 1 is the AI agent. The joints come from YOLO11n-pose, not Fable. Say "First a pose tool pins seventeen joints on me."

3. **Beat 7 states a reading as a fact.** "One rep bent my knee to eleven degrees" says the knee bent that far, but only the reading did. Use "One rep read my knee at eleven degrees, which is impossible."

4. **The beat 10 column label is wrong.** "ANALYSER (pose data)" leaves out that the judge also sees 3 to 4 key frames. Relabel it "ANALYSER (pose maths + key frames)". The current label oversells how separate the two sides of the blind test are.

5. **The ghost and red gap are not Fable's work.** In K11 the ghost skeleton flies onto the judge's desk, and in beat 12 "That red gap is where it would have stopped me." Both imply Fable reads skeletons. Facts say the judge reads a rep table plus key frames and compares against the baseline, and the gap is pose maths.
   - Show the baseline on the desk as a best-set rep row, not the ghost.
   - Freeze K15 on the rep named in `[JUDGE_VERDICT reason]`. If the widest gap and the judge's rep differ, the line is false.

6. **The ghost is only honest under strict conditions.** `[BEST_SET]` must be the same lift from the same camera angle. Normalise the skeletons (hip anchor, limb-length scale) and align them by rep phase, not wall-clock time. Otherwise the red gap measures camera placement, not form. Add these as requirements on the slot.

7. **The caption breaks the comment-trigger rule.** It commits to "Comment GHOST and I'll send you…" with no condition, while the script makes that line conditional. Make the caption follow the same rule.

## SHOULD-FIX

1. **Beat 1 "every workout I've ever filmed".** Clips are still uploading, so this is only true once all are in. Drop "ever" or confirm before posting.

2. **Beat 4 dips must be the raw data.** Show all 14 raw dips, including the 0.2 s spike and the two half reps. Beat 6 then reveals the same graph honestly. A cleaned graph in beat 4 would quietly show the fix before the failure.

3. **Beat 8 only explains one cause.** The 14-vs-11 count had three causes: the hidden leg, a tracker jump and the clip-edge half reps. The current beat implies the hidden leg explains all of it. Add a small on-screen note or measure a `[CLEAN_COUNT]`.

4. **K1/K3 may draw joints the camera can't see.** On a side-view hack squat, the far-side joints are occluded. Draw low-confidence keypoints grey or omit them, or beat 1 contradicts the guardrail. Pick the highest-confidence frame.

5. **Beat 5 "was actually good".** The coach was 0.6 confident and couldn't check heels or knee cave. The card shows this, but "looked good" is the safer spoken line.

6. **The judge is unbuilt but written in the present tense.** Beat 9 and the caption say "Fable judges". Treat a measured judge run as a gate for the 21 Nov post.

7. **The 2/3 re-hook is on-screen only.** Consider making it spoken in beat 9.

8. **"Not training advice" appears only in the caption.** Add a small end-card line.

## Passes

- About 52 s runtime.
- E/H alternation holds across all 12 beats.
- Beat 1 is not a recap, and the lock-on lands within 1.5 s.
- The result arrives by 6.2 s.
- The twist sits at about 1/3 and the beat 9 re-hook at about 2/3.
- One sentence per beat.
- The save asset is clear.
- It ends on a loop, not "next up".
- "Would have stopped me" is worded correctly: nothing implies a live stop.