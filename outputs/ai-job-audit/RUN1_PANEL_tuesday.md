# Independent review: "Run #1" (v2)

These panel reactions are my own simulation, not real viewer data. I did not open `production/REEL_DEFAULTS.md` or the script skill, so pace and caption limits have not been checked against them.

## Per-persona

1. **TCS support, Pune, 24:** The layoffs line lands. They hold to the score, but beat 8 reads as "AI person moving up" and they drift. They'd comment "ticket triage" and send it to the team WhatsApp.
2. **CA, Ahmedabad, 31:** "GST filing?" stops them. If the board shows only tech tasks, they swipe at beat 4. They'd comment only if asked for one task, and send it to articleship batchmates.
3. **HR exec, Bengaluru, 28:** Holds and reads the layoffs line as sincere. They're mildly wary of the "hand over" framing. They'd comment and send it to an HR peer.
4. **Bank RM, Lucknow, 35:** "Last year's model" is insider talk, so they swipe at beat 5. No comment, no send.
5. **Teacher, Jaipur, 38:** "Lesson plans?" holds them. They'd comment "report cards" and send it to the staff group.
6. **BTech, Hyderabad, 21:** The most anxious viewer. They watch it all, comment, send to friends, and come back for Run 2.
7. **FP&A, Gurgaon, 25:** Likes the rubric. They'd question "graded by me", comment "variance commentary", and send it to a colleague.
8. **IB/ER, Mumbai, 33:** Holds for the method, then comments a methodology critique (self-graded, same prompts on the old model). Doesn't send.
9. **Big 4, Bengaluru, 24:** Strong fit. They'd comment "deck formatting" and send it to their cohort.
10. **Strategy manager, Mumbai, 32:** Likes the measure → hand over → re-measure loop. They'll smell consultant-speak in "[HIGHER_ORDER_WORK]" and share it on LinkedIn.
11. **Performance marketer, Delhi, 26:** Already uses AI for copy, so it's "duh" unless [TASK] surprises. They swipe at beat 3.
12. **FMCG BM, Mumbai, 34:** Sees it as a team exercise. They'd send it to their team but are unlikely to comment.

## Scores (1–10)

| # | Stop | Relate | Emotion | Comment | Send | Return |
|---|---|---|---|---|---|---|
| 1 | 7 | 7 | 6 | 5 | 5 | 6 |
| 2 | 7 | 5 | 5 | 5 | 4 | 5 |
| 3 | 6 | 6 | 6 | 5 | 5 | 5 |
| 4 | 5 | 4 | 4 | 3 | 3 | 3 |
| 5 | 7 | 5 | 6 | 6 | 5 | 5 |
| 6 | 8 | 8 | 7 | 7 | 7 | 8 |
| 7 | 6 | 6 | 5 | 6 | 5 | 6 |
| 8 | 5 | 4 | 4 | 6 | 3 | 5 |
| 9 | 7 | 7 | 6 | 7 | 6 | 7 |
| 10 | 6 | 5 | 5 | 4 | 6 | 6 |
| 11 | 5 | 5 | 4 | 3 | 3 | 4 |
| 12 | 6 | 5 | 5 | 4 | 6 | 6 |
| **Avg** | **6.3** | **5.6** | **5.3** | **5.1** | **4.8** | **5.5** |

Relate and send are weakest among non-tech viewers (2, 4, 5). The doorway exists only as on-screen text; the body never shows their kind of task.

## Word count and runtime

- **My count:** 124 spoken words with placeholders, which matches the script's figure.
- **Filled-in estimate:** about 138–145, not 132–136. Times like "forty minutes" are two words each, and [TASK], [FAILED_TASK] and [HIGHER_ORDER_WORK] are likely 2–4 words each.
- **Runtime:** at 2.6 words per second that is about 54–56 s of speech plus about 5 s of holds, so **about 59–61 s**, not 53 s.
- **Beat-level pace problems:**
  - Beat 1 has 10–12 words in 3 s, about 4 words per second. That is too fast for a hook.
  - Beat 8 has about 19–20 filled words in 7 s, about 2.8 words per second, which contradicts its own "don't rush" note.
  - Beat 6 fits 15–17 words plus a 1.5 s screen recording into 7 s, which is tight.

## Line flags

- **Overclaim:**
  - "That was my [DAY] morning": unless [BEFORE_TIME] really filled the morning, this inflates the time saved.
  - "Every month I re-run it": this is Run #1, so the habit hasn't happened yet. Say "I'll re-run it every month."
- **Unmeasured:**
  - "My hours move to [HIGHER_ORDER_WORK]": the time is neither tracked nor shown.
  - Beat 5's "Sees the speed" rests on one model pair, which is not a trend.
  - Prompts tuned on today's model and reused on the old one bias the back-test. Disclose that or use neutral prompts.
- **Smug risk:**
  - "I build AI for a living" can read as a humblebrag. It is saved by "doesn't make me safe."
  - Beat 8 "I hand over… my hours move to…" is the main risk. It frames AI as a promotion for someone with the choice to hand work over.
- **Blames laid-off people:** no line does this directly. Beat 8's "agency" framing can imply that people who lost jobs failed to act. Soften it with concreteness, not a lecture.
- **Self-grading:** "graded by me" is honest, but expect viewer 8's critique. Put the outputs with the rubric so it's checkable.

## Top 6 fixes

1. **Beat 1:** Say only "AI does my [TASK] now." Put "My [DAY] morning →" on screen, or extend the beat to 4 s. Keep "morning" only if the task really took the morning.
2. **Beat 3:** Make three real task rows legible on the board, including at least one that crosses over (reconciling an Excel sheet, follow-up emails, meeting notes), and name one aloud. This is the biggest lift for viewers 2, 4 and 5.
3. **Beat 5:** Replace "Last year's model" with plain words, e.g. "AI from a year ago" if the age is accurate. Add small text "same prompts" or disclose the bias. Drop the spoken "Now [N]" because the card already shows it, which saves 2 words.
4. **Beat 6:** Cut "used to" ("[TASK] took me [BEFORE_TIME]. Now AI does it, I check it: [AI_TIME]."), or extend the beat by 1 s for the screen recording.
5. **Beat 8:** Use the future tense, "I'll re-run it every month." Replace abstract [HIGHER_ORDER_WORK] with one concrete thing actually done in the freed time. This cuts both the smugness and the unmeasured claim.
6. **Beat 10:** Ask for **one** task instead of three; three is high friction. To make people return for Run 2, say "Most-commented task goes into Run #2," but only if that is committed. Cut the on-screen text to two items.

## Verdict

**Revise.** The structure, the honesty scaffolding and the open loop are sound. Fix the hook pace, the missing non-tech specificity, beat 8's tense and tone, and the CTA friction. After those fixes, re-time it with real values, aiming for 55 s or less.
