# Gym Jarvis Ep 3 · Workout Analyser · TRIAL script v3 (Ep 2 structure)

Written 21 Nov 2026 from `SCRIPT_TRIAL_v2.md`, `../facts.md` and the creator's round-2 notes. This is rewrite round 2
of 2, the last before the creator reads it. Nothing here has been recorded, rendered or timed.

## 1. Emotion arc + hook rationale

**Arc: suspicion -> vindication -> earned trust** (unchanged from v2). The main reel runs on builder pride and
curiosity. The trial starts from doubt about my own system and makes the system earn the trust.

| Stage | Beats | What the viewer feels |
|---|---|---|
| Suspicion | 1-2 | Only 6 of 23 passed, and it was wrong about a stop. Why would I trust it? |
| Scrutiny | 3-12 | Fine, show me exactly how it decides, and who decides. |
| Vindication | 13-15 | There is the wrong stop: a good lunge. |
| Earned trust | 16-17 | It now needs two agents to agree, and the one STOP left is one I accept. |
| Tease | 18-19 | Same as the main. |

**Hook:** "Gym Jarvis checked twenty-three of my sets; only six got a clear continue. One of its stops was wrong."
- The reason to stay ("was wrong") is the 19th spoken word: about 6.6 s at 2.9 words a second, about 7.6 s at 2.5.
  Both are estimates; nothing is timed.
- It says a stop was wrong, not which set or why. "Except this one" (beat 14) still reveals the lunge, the two
  verdicts and the camera cause. The two red bars in beat 13 now carry a sharper question: which one is the wrong one?
- "Gym Jarvis" is the first two words and beat 2 runs over the Gym Jarvis diagram.
- "Clear continue" is exact: CONTINUE 6 of 23. HOLD is not called a fail anywhere.

**"Second element" reading (corrected):** it means the second agent. Beats 10 and 11 now use the Ep 2 framing word
for word: "The first agent is the judge", "The second agent is the coach". "Its second part" is gone from beat 2.

## 2. Skeleton mapping (default for every system/build reel)

| # | Skeleton step | Ep 2 (calories) lines | This reel, beats |
|---|---|---|---|
| 1 | SERIES ANCHOR | 1 | 1 |
| 2 | TODAY'S TASK | 2 | 2 |
| 3 | RESEARCH | 3 | 3 |
| 4 | EASY vs HARD insight | 4 | 4 |
| 5 | SPLIT INTO PARTS | 5-6 | 5 |
| 6 | COMPONENT 1 (what it does) | 7 | 6-9 (pose tool + rep maths, then the wave mechanism), 10 (first agent: judge) |
| 7 | COMPONENT 1 is NOT allowed to | 8 | carried by 11: the coach is not allowed the numbers |
| 8 | COMPONENT 2 (and why it exists) | 9-10 | 11 (second agent: coach); the "why" is paid off in 16 |
| 9 | GUARDRAIL | 11-12 | 12 |
| 10 | TESTED ON MANY (real count) | 13 | 1 (count), 13 (body parts) |
| 11 | RESULTS (dashboard) | 14 | 13 |
| 12 | "EXCEPT THIS ONE" failure | 15-16 | 14-15 |
| 13 | THE FIX | 17-18 | 16-17 |
| 14 | NEXT / CTA | 19 | 18-19 |

Order is unchanged from v2. The same two deliberate differences from Ep 2 remain: the real count sits in the hook
(step 10 is split), and the mechanism gets four beats (6-9).

## 3. Script

19 beats, 184 spoken words ("twenty-three" and "200" each counted as one word; 185 if "twenty-three" counts as two).

| Beat | Spoken line | Words | On-screen visual | Skeleton step | Emotion |
|---|---|---|---|---|---|
| 1 | Gym Jarvis checked twenty-three of my sets; only six got a clear continue. | 13 | `wall_of_sets.mp4`, all 23 clips; six tiles turn green, the rest dim. Text: GYM JARVIS · 23 SETS · 6 CONTINUE | SERIES ANCHOR | Suspicion |
| 2 | One of its stops was wrong. Let's open the Workout Analyser. | 11 | Two tiles flash red, a "?" lands between them (no set is singled out). Then `gj_zoom.mp4`: Gym Jarvis diagram, zoom to WORKOUT ANALYSER. Text: 1 STOP WAS WRONG | TODAY'S TASK | Suspicion |
| 3 | First, Claude went through over 200 papers and tools. | 9 | `research_blocks.mp4`, first block only. Text: OVER 200 PAPERS + TOOLS | RESEARCH | Scrutiny |
| 4 | Counting reps is easy; judging one is hard. | 8 | `research_blocks.mp4`: COUNT THEM -> EASY (green), JUDGE THEM -> HARD (red). Small third block stays grey: CAMERA ANGLE CAN FOOL IT (pays off in beat 15) | EASY vs HARD | Scrutiny |
| 5 | So I split it: one tool, two agents. | 8 | `system_card.mp4`: three empty boxes drawn left to right: SEE -> JUDGE -> CHECK. Tags under them: TOOL · AGENT 1 · AGENT 2 | SPLIT INTO PARTS | Scrutiny |
| 6 | A pose tool tracks my joints; rep maths turns one angle into a wave. | 14 | SEE box fills: POSE TOOL · 17 JOINTS + REP MATHS. `lockon_red.mp4`: skeleton overlay on the lat pulldown, elbow ringed; the elbow angle draws a live line beside it | COMPONENT 1 | Scrutiny |
| 7 | One wave is one rep; its height is how far I moved. | 12 | Rep wave diagram (`dual_wave.mp4`, relabelled): each wave numbered as it is drawn, a vertical arrow on one wave. Text: 1 WAVE = 1 REP · HEIGHT = RANGE | COMPONENT 1 (mechanism) | Scrutiny |
| 8 | Each wave is checked against my best, not a textbook. | 10 | Same diagram: the best rep's wave lifts off as a ghost line and slides across every other wave. Text: BASELINE = MY BEST REP, SAME SET · NOT A TEXTBOOK | COMPONENT 1 (mechanism) | Scrutiny |
| 9 | Rep four is clearly shorter. | 5 | Ghost line sits on rep 4; the gap shades amber. Text: LAT PULLDOWN · REP 4: 62° · BEST REP: 86° · "RANGE SHRINKING LATE" · HOLD stamp (`judge_hold.mp4`) | COMPONENT 1 (mechanism, real example) | Scrutiny, first "ok, that's fair" |
| 10 | The first agent is the judge: it goes by my numbers. | 11 | Gym footage stays under the diagram. JUDGE box fills, tagged FIRST AGENT: JUDGE · FABLE 5.2 · REP TABLE + 4 KEY FRAMES -> CONTINUE / HOLD / STOP. The rep table from beat 9 slides into its hands | COMPONENT 1 (first agent) | Scrutiny: one person, one job |
| 11 | The second agent is the coach: video only, numbers not allowed. | 11 | CHECK box fills, tagged SECOND AGENT: COACH · FABLE 5.2 · FRAMES ONLY. The rep table slides towards it and hits a barrier. Text: NEVER SEES THE NUMBERS -> GOOD / BAD / UNCLEAR | COMPONENT 2 + NOT ALLOWED | Scrutiny: a second opinion who can't copy the first |
| 12 | Joint hidden? Gym Jarvis refuses to guess. | 7 | `hidden_diagram.mp4` then `cant_see.mp4` on the leg extension: "CAN'T SEE YOUR KNEE. NOT JUDGING THIS SET." Text: HIDDEN IN OVER 25% OF FRAMES -> NO VERDICT · 4 OF 23 SETS | GUARDRAIL | Trust starts |
| 13 | Chest, back, legs, core: six continue, eleven hold, four refused. | 11 | Results dashboard (NEW): 23 bars, one per set, grouped CHEST · BACK · LEGS · CORE; taller = better (CONTINUE tall green, HOLD mid amber, CAN'T SEE grey stub). Tally counts up: CONTINUE 6 · HOLD 11 · CAN'T SEE 4. Two bars stay red and pulsing | TESTED ON MANY + RESULTS | Suspicion returns: which red one is wrong? |
| 14 | Except this one: judge said stop, coach said good. | 9 | `false_alarm.mp4`: the lunge, skeleton overlay. Left stamp JUDGE: STOP, right stamp COACH: GOOD. Text: DUMBBELL LUNGE · 17 REPS | "EXCEPT THIS ONE" | Vindication |
| 15 | I'd only turned towards the camera. | 6 | Lunge split: side-on rep vs turned-to-camera rep, same depth, knee angle reads shallower from the front. The grey block from beat 4 turns red: CAMERA ANGLE CAN FOOL IT. STOP struck through: FALSE ALARM | Failure, cause | Vindication (I was right to doubt it) |
| 16 | Now stop needs both agents; otherwise, check footage. | 8 | `check_gate.mp4`: JUDGE and CHECK feed one gate. BOTH SAY STOP -> STOP · ELSE -> CHECK FOOTAGE. Dashboard: the lunge bar flips from red to CHECK FOOTAGE 1 | THE FIX | Earned trust |
| 17 | Only one stop survived: my reverse crunch. Fair. | 8 | `ghost_stop.mp4`: crunch with best-rep ghost. Text: HIP RANGE · WORST REP 53° · BEST REP 122° · SHORT, SWUNG REPS · JUDGE: STOP + COACH: BAD = STOP. Final tally: CONTINUE 6 · HOLD 11 · STOP 1 · CHECK FOOTAGE 1 · CAN'T SEE 4. Corner: COMMENT FORM | FIX, proven | Earned trust |
| 18 | Next up: Salesforce is reportedly letting people go, but hiring people with AI experience. | 14 | `news_jobs.mp4`, as in the main: real headline on top, real posting below, title ringed. Text: REPORTEDLY · NOT CONFIRMED BY SALESFORCE · LMTS - LEAD AI/ML ENGINEER (LLM POST-TRAINING) | NEXT | Curiosity |
| 19 | How can you be that one? Follow along to know. | 10 | `ending_screen.mp4` | CTA | Curiosity |

Beats 18-19 are word for word v2's beats 18-19 (the main's beats 14-15), so the main takes can be reused. Beats 14
and 16 are word for word v2. Beats 1 and 7 differ from v2 only in punctuation or one dropped "and". Beats 1-17 need
recording.

**Runtime (estimate, not measured):** 184 words. At 2.9 words a second after 1.15x that is about 63 s, inside the
~65 s target. At the slower 2.5 words a second implied by the main's expected runtime it is about 74 s. The script
fits 65 s only if the recorded pace is about 2.85 words a second or faster. See Open risks for the cut order.

## 4. Principle checks

| Principle | Applies? | Verdict | Evidence |
|---|---|---|---|
| SERIES-ANCHOR | Yes: series episode | PASS | "Gym Jarvis" is the first two words, beat 2 runs over the Gym Jarvis diagram, and beat 12 names it again. |
| ARCHITECTURE-SHOWN | Yes: system/build reel | PASS | Pose tool and rep maths (6), first agent: judge (10), second agent: coach (11), guardrail (12), decision rule (16). SEE -> JUDGE -> CHECK builds box by box on screen; "see, judge, check" is no longer spoken. |
| MECHANISM-CONCRETE | Yes: creator asked for it | PASS | Beats 6-9: angle -> wave, one wave = one rep, height = range, checked against my best, shown on rep 4 (62° vs 86°). Same four steps as v2, 4 words shorter. |
| RESULTS-SHOWN | Yes: 23 sets measured | PASS | Count in the hook, 23-bar dashboard in beat 13, full five-way tally on screen in beat 17. |
| FAILURE-AND-FIX | Yes: one real failure exists | PASS | Lunge: judge STOP, coach GOOD, turned towards the camera (14-15); both-must-agree rule and CHECK FOOTAGE (16). |
| CLAIMS-TRUE | Always | PASS, three notes | Every number is in facts.md. The two red bars and "one of its stops" rest on the creator's check of `verdicts.json` (judge STOP on IMG_2650 and IMG_2661 only); I did not open that file. Note 1: "its stops" in beat 2 means the judge's two STOPs before the fix; the final output has one STOP. Note 2: "it goes by my numbers" (beat 10) is a spoken shorthand; the judge also reads 4 key frames, which the screen states. Note 3: "Fair." (beat 17) is the creator's own opinion and only he can confirm it. v2's "half reps" note is gone: the words are cut and the screen uses facts.md's "short, swung reps". |
| EMOTION-DIFFERS-FROM-MAIN | Yes: A/B trial | PASS | Main: pride + curiosity. Trial: suspicion -> vindication -> earned trust; the builder says his own system was wrong in the first 8 s. |
| HOOK-PAYOFF-BY-8S | Yes: trial reels reach cold viewers | PASS on estimate | "One of its stops was wrong" completes at word 19, about 6.6 to 7.6 s depending on pace. Was PARTIAL in v2. Unmeasured until a take exists; a slow read of beat 1 pushes it past 8 s. |

## 5. Panel scores (16 personas, strict; ordinary good reel = 5-6)

These are my estimates of how each persona would react, not viewer data. v2 scored 6.6; this is the second and last
revision.

**v2 -> v3 changes**
- Beat 2: "I doubted that, so let's open its second part: the Workout Analyser." -> "One of its stops was wrong.
  Let's open the Workout Analyser." Hook payoff moves from about 20 s to under 8 s (estimate); "second part" removed.
- Beat 3: "First, I had Claude dig through..." -> "First, Claude went through..." (-2 words; facts.md's allowed wording).
- Beat 4: "judging a rep is hard" -> "judging one is hard" (-1).
- Beat 5: "So I split it into three: see, judge, check." -> "So I split it: one tool, two agents." Sets up the
  first/second count; SEE -> JUDGE -> CHECK stays on screen.
- Beats 6-9: same mechanism, 4 words shorter ("and" dropped twice, "one joint's angle" -> "one angle", "compared
  with my own best wave" -> "checked against my best", "here" dropped).
- Beat 10: "The judge agent reads those numbers plus four key frames." -> "The first agent is the judge: it goes by
  my numbers." Ep 2 first/second framing; a person with one job. The four key frames move to screen only.
- Beat 11: "The coach agent only watches video, and isn't allowed the numbers." -> "The second agent is the coach:
  video only, numbers not allowed." The second agent is called out; the rule a person gets is kept.
- Beat 12: "One guardrail: joint hidden, no verdict." -> "Joint hidden? Gym Jarvis refuses to guess."
- Beat 13: "Across chest, back, legs and core: ... four can't see." -> "Chest, back, legs, core: ... four refused."
  (-2; "refused" echoes beat 12). The screen still says CAN'T SEE 4.
- Beat 15: "as the research warned" cut (-4); the grey block turning red says it.
- Beat 17: "half reps" -> "Fair." (-1). The creator's acceptance is spoken; the reason is on screen.
- Visual: gym footage stays under beats 10-12; beat 2 gets a two-tile red flash that does not single out a set.
- Words: 198 -> 184. Beats 14, 16, 18 and 19 are untouched.

| # | Persona | v2 | v3 | Why (v3) |
|---|---|---|---|---|
| 1 | TCS support eng, Pune, 24 | 7 | 7 | Same build story; first/second agent is easier to copy. |
| 2 | CA, Ahmedabad, 31 | 6 | 7 | "One of its stops was wrong" is an audit finding; "refuses to guess" is a control he respects. |
| 3 | HR exec, Bengaluru, 28 | 6 | 6 | Faster hook, but the wave beats are still not hers. |
| 4 | Bank RM, Lucknow, 35 | 5 | 6 | Judge and coach as two people with two jobs is followable; no longer drifts at the agents. |
| 5 | Teacher, Jaipur, 38 | 4 | 5 | A machine being wrong is a reason to stay past beat 2; still no gym or AI stake of her own. |
| 6 | BTech final-year, Hyderabad, 21 | 7 | 7 | Architecture plus job tease, unchanged. |
| 7 | FP&A, Gurgaon, 25 | 7 | 7 | Dashboard and tally are his language. |
| 8 | Equity research, Mumbai, 33 | 7 | 7 | Likes the error admitted up front; nothing new in the evidence. |
| 9 | Big4 analyst, Bengaluru, 24 | 7 | 7 | Two-checker control, now named first and second. |
| 10 | Strategy mgr, Mumbai, 32 | 7 | 7 | Same clean problem -> system -> exception -> fix. |
| 11 | Perf marketing, Delhi, 26 | 7 | 8 | A number and a contradiction inside 8 s is the hook he would write. |
| 12 | FMCG brand mgr, Mumbai, 34 | 6 | 6 | Tighter, still low personal relevance. |
| 13 | Startup backend dev, Bengaluru, 27 | 8 | 8 | "Numbers not allowed" keeps the save; misses the four key frames in voice. |
| 14 | ML eng, Hyderabad, 30 | 7 | 7 | "Goes by my numbers" is a simplification; still wants 9-of-16 in voice. |
| 15 | Gym trainer, Delhi, 29 | 8 | 8 | "Checked against my best" is how he coaches. |
| 16 | BCom student, Kolkata, 20 | 6 | 7 | Hook pays early and the middle is 14 words shorter. |

| Group | v2 | v3 |
|---|---|---|
| Mass (2, 3, 4, 5, 12, 15, 16) | 5.9 | 6.4 |
| Fin-consult-mktg (7-12) | 6.8 | 7.0 |
| Builders (1, 6, 13, 14) | 7.3 | 7.3 |
| **Overall (16)** | **6.6** | **6.9** |

**v3 is still under 7 (6.9, 110 of 160 points).** Both allowed revisions are used, so it goes to the creator as it
stands. Fin-consult-mktg reaches the bar; the mass group moved 0.5 and is still the gap. What is left in the mass gap
is beats 6-9: four mechanism beats the creator asked to keep, which personas 3, 5 and 12 sit through without a stake.

## 6. Open risks

1. **Under the 7 bar (6.9).** Words are no longer the main lever. For the mass group the lever is picture: gym
   footage under every diagram in beats 6-12, and the rep-4 example on a real clip.
2. **Runtime depends on pace.** 184 words is about 63 s at 2.9 words a second and about 74 s at 2.5. Nothing is
   timed. If the take runs long, cut in this order: beat 9 voice (diagram and numbers stay, -5), "First," in beat 3
   (-1), "Fair." in beat 17 (-1). Beats 18-19 stay untouched.
3. **Hook spends part of the surprise.** The viewer knows a stop was wrong before beat 14. I judge that as a gain
   (the red bars become a question), but "Except this one" lands as a reveal of which and why, not as a shock.
4. **"Its stops" is pre-fix.** Beat 2 counts the judge's two STOPs; the final tally shows STOP 1. Beat 17 closes
   the gap ("only one stop survived"), and the caption should say the lunge is now CHECK FOOTAGE.
5. **"Goes by my numbers."** The judge also gets 4 key frames. The screen says so in beat 10; if a checker objects,
   the fallback line is "it gets my numbers" (same length).
6. **Lines I cannot hear.** "video only, numbers not allowed", "Joint hidden?" and "four refused" are clipped
   phrasings. The creator has to read them aloud; "four refused" may need to become "four can't see" (+1 word).
7. **Wave vs dip.** The main's `dual_wave.mp4` says "1 DIP = 1 REP"; this script says wave and height, so the label
   needs changing, and the best-rep ghost line may be a new render. I have not opened any asset file; every asset
   name is carried over from v2, and `judge_hold.mp4` being the lat pulldown is still an assumption.
8. **New pixels:** the 23-bar dashboard (13, 16, 17), the two-tile red flash (2), the first/second agent tags and
   coach barrier (10, 11), the lunge split (15) if `false_alarm.mp4` does not already contain it.
9. **Hook reading.** "Only six got a clear continue" can be heard as "17 were bad". Beat 13 shows HOLD in amber,
   not red; the caption should say HOLD means "range varied", not fail.
10. **Crunch wording.** Beat 17 shows worst and best rep without rep numbers or a rep count (the pose tool split
    that set into 20 reps where the coach counts 12). Never "stopped me mid-set".
11. **Caption must carry the limits:** judge and coach agree on 9 of 16 sets both could judge; one phone angle; not
    training advice; about USD 0.15 per set for the judge.
12. **A/B is a package test.** Hook, emotion and middle all differ from the main, so a win shows the package works,
    not which element did it. Log it that way in `production/EXPERIMENTS.md`.
13. **Not checked:** audio, pacing, `verdicts.json` (taken from the creator's note), any asset file, and whether
    the Ep 2 "first agent / second agent" wording matches Ep 2 exactly beyond the framing quoted in the brief.
