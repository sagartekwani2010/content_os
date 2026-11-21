# Gym Jarvis Ep 3 · Workout Analyser · TRIAL script v2 (Ep 2 structure)

Written 21 Nov 2026 from `../facts.md`, `../SCRIPT_FINAL.md` and the creator's note. Replaces the spines in
`SPINES.md`, which were rejected for leaving the Ep 2 structure. Nothing here has been recorded, rendered or timed.

## 1. Emotion arc + hook rationale

**Arc: suspicion -> vindication -> earned trust.** The main reel runs on builder pride and curiosity ("found the one
set", "how did I build it?"). The trial starts from doubt about my own system and makes the system earn the trust.

| Stage | Beats | What the viewer feels |
|---|---|---|
| Suspicion | 1-2 | It passed only 6 of my 23 sets. I don't believe it. |
| Scrutiny | 3-12 | Fine, show me exactly how it decides. |
| Vindication | 13-15 | I was right to doubt it: it called STOP on a good lunge. |
| Earned trust | 16-17 | It now needs two agents to agree, and the one STOP left is one I accept. |
| Tease | 18-19 | Same as the main. |

**Hook:** "Gym Jarvis checked twenty-three of my sets; only six got a clear continue."
- Different from the main (STOP stamp, "the one set I should never have done") and from the old trial (false alarm first).
- It names Gym Jarvis in the first two words, gives two real numbers, and is a bruise any gym-goer understands.
- It does not spend the false alarm, so "Except this one" still lands in its Ep 2 position.
- "Clear continue" is exact: CONTINUE 6 of 23. HOLD is not called a fail anywhere.

**"Second element" reading:** I took the creator's note to mean the Workout Analyser is the second part of Gym Jarvis
(the meal scanner was the first), so beat 2 says "its second part" over the five-part Gym Jarvis diagram. If the note
meant the second agent, beat 11 already calls it out by role.

## 2. Skeleton mapping (default for every system/build reel)

| # | Skeleton step | Ep 2 (calories) lines | This reel, beats |
|---|---|---|---|
| 1 | SERIES ANCHOR | 1 | 1 |
| 2 | TODAY'S TASK | 2 | 2 |
| 3 | RESEARCH | 3 | 3 |
| 4 | EASY vs HARD insight | 4 | 4 |
| 5 | SPLIT INTO PARTS | 5-6 | 5 |
| 6 | COMPONENT 1 (what it does) | 7 | 6-9 (pose tool + rep maths, then the wave mechanism), 10 (judge agent) |
| 7 | COMPONENT 1 is NOT allowed to | 8 | carried by 11: the coach agent is not allowed the numbers |
| 8 | COMPONENT 2 (and why it exists) | 9-10 | 11 (coach agent); the "why" is paid off in 16 |
| 9 | GUARDRAIL | 11-12 | 12 |
| 10 | TESTED ON MANY (real count) | 13 | 1 (count), 13 (body parts) |
| 11 | RESULTS (dashboard) | 14 | 13 |
| 12 | "EXCEPT THIS ONE" failure | 15-16 | 14-15 |
| 13 | THE FIX | 17-18 | 16-17 |
| 14 | NEXT / CTA | 19 | 18-19 |

Two deliberate differences from Ep 2: the real count moves into the hook (step 10 is split), and the mechanism gets
four beats (6-9) because the creator asked for the exact good-rep / bad-rep method.

## 3. Script

19 beats, 198 spoken words. Numbers live on screen; the spoken lines stay short.

| Beat | Spoken line | On-screen visual | Skeleton step | Emotion |
|---|---|---|---|---|
| 1 | Gym Jarvis checked twenty-three of my sets; only six got a clear continue. | `wall_of_sets.mp4`, all 23 clips; six tiles turn green, the rest dim. Text: GYM JARVIS · 23 SETS · 6 CONTINUE | SERIES ANCHOR | Suspicion |
| 2 | I doubted that, so let's open its second part: the Workout Analyser. | `gj_zoom.mp4`: five-part Gym Jarvis diagram, part 1 ticked (MEAL SCAN, Ep 2), part 2 lights red, zoom to WORKOUT ANALYSER. Text: GYM JARVIS · PART 2 OF 5 | TODAY'S TASK | Suspicion |
| 3 | First, I had Claude dig through over 200 papers and tools. | `research_blocks.mp4`, first block only. Text: OVER 200 PAPERS + TOOLS | RESEARCH | Scrutiny |
| 4 | Counting reps is easy, judging a rep is hard. | `research_blocks.mp4`: COUNT THEM -> EASY (green), JUDGE THEM -> HARD (red). Small third block stays grey: CAMERA ANGLE CAN FOOL IT (pays off in beat 15) | EASY vs HARD | Scrutiny |
| 5 | So I split it into three: see, judge, check. | `system_card.mp4`: block diagram, three empty boxes drawn left to right: SEE -> JUDGE -> CHECK | SPLIT INTO PARTS | Scrutiny |
| 6 | A pose tool tracks my joints, and rep maths turns one joint's angle into a wave. | SEE box fills: POSE TOOL · 17 JOINTS + REP MATHS. `lockon_red.mp4`: skeleton overlay on the lat pulldown, elbow ringed; the elbow angle draws a live line beside it | COMPONENT 1 | Scrutiny |
| 7 | One wave is one rep, and its height is how far I moved. | Rep wave diagram (`dual_wave.mp4`, relabelled): each wave numbered as it is drawn, a vertical arrow on one wave. Text: 1 WAVE = 1 REP · HEIGHT = RANGE | COMPONENT 1 (mechanism) | Scrutiny |
| 8 | Each wave is compared with my own best wave, not a textbook. | Same diagram: the best rep's wave lifts off as a ghost line and slides across every other wave. Text: BASELINE = MY BEST REP, SAME SET · NOT A TEXTBOOK | COMPONENT 1 (mechanism) | Scrutiny |
| 9 | Rep four here is clearly shorter. | Ghost line sits on rep 4; the gap shades amber. Text: LAT PULLDOWN · REP 4: 62° · BEST REP: 86° · "RANGE SHRINKING LATE" · HOLD stamp (`judge_hold.mp4`) | COMPONENT 1 (mechanism, real example) | Scrutiny, first "ok, that's fair" |
| 10 | The judge agent reads those numbers plus four key frames. | JUDGE box fills: JUDGE AGENT · FABLE 5.2 · REP TABLE + 4 KEY FRAMES (best rep and worst rep, both ends) -> CONTINUE / HOLD / STOP | COMPONENT 1 (judge agent) | Scrutiny |
| 11 | The coach agent only watches video, and isn't allowed the numbers. | CHECK box fills: COACH AGENT · FABLE 5.2 · FRAMES ONLY. The rep table slides towards it and hits a barrier. Text: NEVER SEES THE NUMBERS -> GOOD / BAD / UNCLEAR | COMPONENT 2 + NOT ALLOWED | Scrutiny |
| 12 | One guardrail: joint hidden, no verdict. | `hidden_diagram.mp4` then `cant_see.mp4` on the leg extension: "CAN'T SEE YOUR KNEE. NOT JUDGING THIS SET." Text: HIDDEN IN OVER 25% OF FRAMES -> NO VERDICT · 4 OF 23 SETS | GUARDRAIL | Trust starts |
| 13 | Across chest, back, legs and core: six continue, eleven hold, four can't see. | Results dashboard (NEW): 23 bars, one per set, grouped CHEST · BACK · LEGS · CORE; taller = better (CONTINUE tall green, HOLD mid amber, CAN'T SEE grey stub). Tally counts up: CONTINUE 6 · HOLD 11 · CAN'T SEE 4. Two bars stay red and pulsing | TESTED ON MANY + RESULTS | Suspicion returns: what about the two red ones? |
| 14 | Except this one: judge said stop, coach said good. | `false_alarm.mp4`: the lunge, skeleton overlay. Left stamp JUDGE: STOP, right stamp COACH: GOOD. Text: DUMBBELL LUNGE · 17 REPS | "EXCEPT THIS ONE" | Vindication |
| 15 | I'd only turned to the camera, as the research warned. | Lunge split: side-on rep vs turned-to-camera rep, same depth, knee angle reads shallower from the front. The grey block from beat 4 turns red: CAMERA ANGLE CAN FOOL IT. STOP struck through: FALSE ALARM | Failure, cause | Vindication (I was right to doubt it) |
| 16 | Now stop needs both agents; otherwise, check footage. | `check_gate.mp4`: JUDGE and CHECK feed one gate. BOTH SAY STOP -> STOP · ELSE -> CHECK FOOTAGE. Dashboard: the lunge bar flips from red to CHECK FOOTAGE 1 | THE FIX | Earned trust |
| 17 | Only one stop survived: my reverse crunch, half reps. | `ghost_stop.mp4`: crunch with best-rep ghost. Text: HIP RANGE · WORST REP 53° · BEST REP 122° · JUDGE: STOP + COACH: BAD = STOP. Final tally: CONTINUE 6 · HOLD 11 · STOP 1 · CHECK FOOTAGE 1 · CAN'T SEE 4. Corner: COMMENT FORM | FIX, proven | Earned trust |
| 18 | Next up: Salesforce is reportedly letting people go, but hiring people with AI experience. | `news_jobs.mp4`, as in the main: real headline on top, real posting below, title ringed. Text: REPORTEDLY · NOT CONFIRMED BY SALESFORCE · LMTS - LEAD AI/ML ENGINEER (LLM POST-TRAINING) | NEXT | Curiosity |
| 19 | How can you be that one? Follow along to know. | `ending_screen.mp4` | CTA | Curiosity |

Beats 18-19 are word for word the main's beats 14-15, so the main takes can be reused and the tease is identical in
both arms. Beats 1-17 are new lines and need recording.

**Runtime (estimate, not measured):** 198 words. At 2.9 words a second after 1.15x that is about 68 s. The main script
is about 190 words with an expected ~80 s, which implies a slower real pace (about 2.5 words a second with its holds);
at that pace this runs about 78 s, over the 70 s limit. See Open risks for the cut order.

## 4. Principle checks

| Principle | Applies? | Verdict | Evidence |
|---|---|---|---|
| SERIES-ANCHOR | Yes: series episode | PASS | "Gym Jarvis" is the first two words; beat 2 names the Workout Analyser as its second part over the five-part diagram. |
| ARCHITECTURE-SHOWN | Yes: system/build reel | PASS | Pose tool, rep maths, judge agent, coach agent all named (6, 10, 11); SEE -> JUDGE -> CHECK builds box by box; the decision rule is beat 16. |
| MECHANISM-CONCRETE | Yes: creator asked for it | PASS | Beats 6-9: joint angle -> wave, one wave = one rep, height = range, compared with my best wave, shown on rep 4 (62° vs 86°). A trainer could repeat it. |
| RESULTS-SHOWN | Yes: 23 sets measured | PASS | Count in the hook, 23-bar dashboard in beat 13, full five-way tally on screen in beat 17. CHECK FOOTAGE 1 and STOP 1 are spoken as stories, not in the tally line. |
| FAILURE-AND-FIX | Yes: one real failure exists | PASS | Lunge: judge STOP, coach GOOD, turned to the camera (14-15); both-must-agree rule and CHECK FOOTAGE (16). |
| CLAIMS-TRUE | Always | PASS, two notes | Every number is in facts.md. Note 1: "half reps" is the main's wording for "short, swung reps". Note 2: beat 13 shows two red bars before the fix, which assumes the judge said STOP on exactly the lunge and the crunch; facts.md states both, but check `verdicts.json` for any other judge STOP. |
| EMOTION-DIFFERS-FROM-MAIN | Yes: A/B trial | PASS | Main: pride + curiosity. Trial: suspicion -> vindication -> earned trust; the builder doubts his own system in beat 2. |
| HOOK-PAYOFF-BY-8S | Yes: trial reels reach cold viewers | PARTIAL | The hook's number is shown in full by 4 s (six green tiles of 23). The "why only six" answer starts at beat 6 (about 20 s) and completes at beat 13. The first 8 s set the question rather than answer it, as Ep 2 does. |

## 5. Panel scores (16 personas, strict; ordinary good reel = 5-6)

v1 was the first draft; it scored under 7, so it was revised once into the script above (v2).

**v1 -> v2 changes**
- Beat 1: "My Gym Jarvis says it can spot a bad rep." -> "Gym Jarvis checked twenty-three of my sets; only six got a clear continue."
- Beat 2: "I doubted it, so..." -> "I doubted that, so..." (the doubt now points at a number).
- Beat 7: "its height is the range" -> "its height is how far I moved".
- v1 beats 13 ("Then I tested it on twenty-three sets.") and 14 merged into one results beat with the body parts spoken; the dashboard leaves two red bars to carry suspense into "Except this one".

| # | Persona | v1 | v2 | Why (v2) |
|---|---|---|---|---|
| 1 | TCS support eng, Pune, 24 | 7 | 7 | Likes the two-agent build; wants to copy it. |
| 2 | CA, Ahmedabad, 31 | 5 | 6 | "6 of 23" reads like an audit; the middle is still technical. |
| 3 | HR exec, Bengaluru, 28 | 5 | 6 | Stays for the hook number and the Salesforce tease. |
| 4 | Bank RM, Lucknow, 35 | 4 | 5 | Follows the wave picture, drifts at the agents. |
| 5 | Teacher, Jaipur, 38 | 4 | 4 | No gym, no AI stake; likely swipes by beat 5. |
| 6 | BTech final-year, Hyderabad, 21 | 7 | 7 | Architecture plus job tease. |
| 7 | FP&A, Gurgaon, 25 | 6 | 7 | Dashboard and tally are his language. |
| 8 | Equity research, Mumbai, 33 | 6 | 7 | Respects the false alarm being shown. |
| 9 | Big4 analyst, Bengaluru, 24 | 6 | 7 | Two-checker control is familiar; gym-goer. |
| 10 | Strategy mgr, Mumbai, 32 | 6 | 7 | Clear problem -> system -> exception -> fix. |
| 11 | Perf marketing, Delhi, 26 | 6 | 7 | Number hook; would test this himself. |
| 12 | FMCG brand mgr, Mumbai, 34 | 5 | 6 | Clean story, low personal relevance. |
| 13 | Startup backend dev, Bengaluru, 27 | 8 | 8 | Judge sees numbers, coach doesn't: saves it. |
| 14 | ML eng, Hyderabad, 30 | 7 | 7 | Wants the 9-of-16 agreement figure; it is caption only. |
| 15 | Gym trainer, Delhi, 29 | 7 | 8 | "Compared with your own best rep" is how he coaches. |
| 16 | BCom student, Kolkata, 20 | 5 | 6 | Hook lands; the middle is long for him. |

| Group | v1 | v2 |
|---|---|---|
| Mass (2, 3, 4, 5, 12, 15, 16) | 5.0 | 5.9 |
| Fin-consult-mktg (7-12) | 5.8 | 6.8 |
| Builders (1, 6, 13, 14) | 7.3 | 7.3 |
| **Overall (16)** | **5.9** | **6.6** |

**v2 is still under 7.** The one allowed revision is used, so it is reported as it stands. The gap is the mass group:
beats 10-12 are three component beats in a row with no person or stake on screen.

## 6. Open risks

1. **Under the 7 bar (6.6).** The structure the creator asked for costs mass-viewer retention in beats 10-12. The
   strongest lever left is visual: keep gym footage under every diagram so no beat is diagram only.
2. **Runtime may exceed 70 s.** Nothing is timed. If the recorded take runs long, cut in this order: beat 9 voice
   (diagram and numbers stay, -6 words), "as the research warned" in beat 15 (the red block says it, -4), beat 3
   "First," and "and tools" (-3). Beats 18-19 stay untouched to keep the tease identical.
3. **Wave vs dip.** The main's `dual_wave.mp4` says "1 DIP = 1 REP". This script says wave and height, so the label
   needs changing, and the best-rep ghost line on the wave may be a new render. I have not opened any asset file; every
   asset name is taken from `SCRIPT_FINAL.md`, and `judge_hold.mp4` being the lat pulldown is an assumption.
4. **New pixels:** the 23-bar results dashboard (beat 13, 16, 17), the coach-agent barrier (beat 11), the lunge split
   (beat 15) if `false_alarm.mp4` does not already contain it.
5. **Hook reading.** "Only six got a clear continue" can be heard as "17 were bad". The script never says that, and
   beat 13 shows HOLD in amber, not red; the caption should say HOLD means "range varied", not fail.
6. **Crunch wording.** Beat 17 shows worst rep and best rep without rep numbers or a rep count (the pose tool split
   that set into 20 reps where the coach counts 12). Keep "survived", "flagged", "found"; never "stopped me mid-set".
7. **Caption must carry the limits:** judge and coach agree on 9 of 16 sets both could judge; one phone angle; not
   training advice; about USD 0.15 per set for the judge.
8. **A/B is a package test.** Hook, emotion and middle all differ from the main, so a win shows the package works,
   not which element did it. Log it that way in `production/EXPERIMENTS.md`.
9. **Not checked:** audio, pacing, whether the lines read naturally aloud. The creator has to read and listen.
