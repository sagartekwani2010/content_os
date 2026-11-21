# Independent review: Fable 5.2 deep-dive v3

These scores are my simulation of the 14 personas. I did not test the script with real viewers.

## Panel scores (1–10)

| # | Viewer | Stop | Clarity | Value | Emotion | Send | Save |
|---|---|---|---|---|---|---|---|
| 1 | TCS support, Pune | 6 | 5 | 5 | 4 | 3 | 5 |
| 2 | CA, Ahmedabad | 5 | 5 | 4 | 3 | 2 | 3 |
| 3 | HR, Bengaluru | 6 | 5 | 4 | 4 | 3 | 3 |
| 4 | Bank RM, Lucknow | 4 | 4 | 3 | 3 | 2 | 2 |
| 5 | Teacher, Jaipur | 5 | 4 | 3 | 4 | 2 | 2 |
| 6 | BTech, Hyderabad | 7 | 6 | 6 | 6 | 6 | 6 |
| 7 | FP&A, Gurgaon | 6 | 6 | 6 | 5 | 4 | 6 |
| 8 | IB/ER, Mumbai | 5 | 6 | 5 | 4 | 3 | 4 |
| 9 | Big 4, Bengaluru | 6 | 6 | 6 | 5 | 5 | 6 |
| 10 | Strategy mgr, Mumbai | 6 | 7 | 6 | 5 | 4 | 5 |
| 11 | Perf marketing, Delhi | 6 | 6 | 6 | 5 | 5 | 6 |
| 12 | FMCG BM, Mumbai | 6 | 6 | 4 | 5 | 4 | 3 |
| **Avg 1–12** | | **5.67** | **5.50** | **4.83** | **4.42** | **3.58** | **4.25** |
| 13 | Backend dev, Bengaluru | 8 | 7 | 8 | 7 | 7 | 8 |
| 14 | ML eng, Hyderabad | 7 | 7 | 7 | 6 | 7 | 7 |
| **Avg all 14** | | **5.93** | **5.71** | **5.21** | **4.71** | **4.07** | **4.71** |

The reel works for builders but not for the general 12. Mythos, Lean, the effort dial and four model names come too fast. Prices are in dollars, and most of these viewers don't pay for Claude, so the Pro and Max lines don't apply to them.

## Length

- **Literal spoken words:** 218, plus 3 placeholders. At about 4 words per placeholder, that is about **230**, not the 225 stated.
- **Runtime:** 230 / 2.6 = 88.5 s, and / 1.1 = **80.4 s**. Adding 4.8 s of cards and holds gives **about 85 s**, not 83 s.

## Claims not supported by FACTS

1. **Beat 9 and Card 1, "Haiku routine":** no source supports this. The help center only says to use Sonnet for most tasks. "Opus: long write-ups" is also an inference, from GDPval-AA and Briefcase only.
2. **Beat 6, "DO: plan with Fable, execute cheap":** the Fermat result was a 1,000-Fable team. It does not show cheap execution working.
3. **Card 1 tip, "Try high or xhigh before max":** this generalises from one benchmark (FrontierCode). Keep "on one benchmark" on screen.
4. **Beat 1, "they tied":** this is true only for the two-step pipeline. In direct-guess mode it was 74 vs 81 kcal. Either say "in one setup" or don't hide the second result.
5. **Beat 1, "costs twice":** it is twice per token. Fable always thinks, so the cost per task is likely higher. Say "per word".
6. **Beats 2 and 12, versions:** the facts sheet doesn't say which Fable and Opus versions the Meal Analyser used. The author already flagged this.
7. **Beat 17, Saturday tease:** unconfirmed.

## Top 5 fixes

1. **Beats 2 and 11–12 (spoiled guess):** beat 2 already reveals that Opus overestimated "far more". Beat 11 then asks viewers to "guess the gap", and beat 12 answers with bias rather than the error gap. Cut "far more" from beat 2, for example: "But on portions, one of them was way off. Guess which." Then make beat 11 "Guess which one, and by how much."
2. **Beats 1 and 7 (money):** dollars per million tokens mean little to these viewers. Lead with one spoken ₹-per-task number from [INR_*] in beat 7 and move the 2x/4x/80x ratios to the screen. That is the line that gets sent to friends.
3. **Beat 6 (Fermat):** "Lean proof" loses viewers 2–5 and 12. Say "a computer-checked proof of Fermat's Last Theorem in thirty hours" and move "building on earlier work" to the screen. This saves about 2 s.
4. **Beat 9 (router):** change it to "Sonnet for most things, Fable for the hard planning, Opus for office docs," which matches the sources. Drop Haiku from speech, or label the whole card "my draft, to be updated with tonight's results."
5. **Beat 8 (Pro/Max):** add "and it burns through limits faster", which the help center supports. Also add one line for non-subscribers, such as "On the free plan? Skip to the router," or the line loses half the panel.

## Verdict: **Revise**

The structure, sourcing and honesty labels are strong, and nothing in it is invented. The problems are a spoiled guess beat, two unsupported router rows, and no ₹ hook for the general audience. It also can't ship until the placeholders are filled and the creator has listened to the final file.
