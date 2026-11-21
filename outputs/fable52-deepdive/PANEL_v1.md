# Independent review: Fable 5.2 deep-dive reel

## Per-persona read

1. **TCS support, Pune, 24.** Watches to the router (beat 14) and takes away "use cheap models for routine work." Sends it to the team WhatsApp.
2. **CA, Ahmedabad, 31.** Swipes at beat 3, because "brain vs body" is abstract. Takes nothing away and sends to no one.
3. **HR exec, Bengaluru, 28.** Swipes at beat 2, since "Fable" and "Opus" mean nothing to them. No takeaway, no send.
4. **Bank RM, Lucknow, 35.** Swipes at beat 1, because model names and dollar prices are cold. No takeaway, no send.
5. **Teacher, Jaipur, 38.** "Calorie test" holds them for a moment, then they swipe at beat 3. No takeaway, no send.
6. **BTech, Hyderabad, 21.** Stays through the scoresheet. Fermat is the wow moment, and they learn that Pro means paying credits. Sends to batchmates.
7. **FP&A, Gurgaon, 25.** Drifts at beats 5–7 and comes back for the Maths/Excel row. Wants a ₹ figure, and may send it to their manager.
8. **IB associate, Mumbai, 33.** Swipes at beat 5. The one fact they would value, that Opus beats Fable on office work, is never spoken. No send.
9. **Big 4 analyst, Bengaluru, 24.** Stays to the router card and saves it. Sends it to the project team.
10. **Strategy manager, Mumbai, 32.** The orchestrator idea lands at beat 8. Leaves around beat 12 and sends to a peer.
11. **Performance marketing, Delhi, 26.** The 2x/4x/80x figures read like CPA, and they stay through beat 14. Sends to the growth team.
12. **FMCG brand manager, Mumbai, 34.** Swipes at beat 3. Nothing in the reel is about their work.
13. **Backend dev, Bengaluru, 27.** Watches to the end and saves the router card and effort tip. Sends to team Slack. Will question the "safety classifiers" wording.
14. **ML engineer, Hyderabad, 30.** Knows most of it already, but the effort-cost and self-critical findings are new. Will flag that the Fermat line drops its caveats. Sends to a few people.

## Scores (1–10)

| # | Stop | Clarity | Value | Emotion | Send | Save |
|---|---|---|---|---|---|---|
| 1 | 6 | 6 | 6 | 4 | 4 | 5 |
| 2 | 4 | 4 | 3 | 3 | 2 | 2 |
| 3 | 3 | 4 | 2 | 3 | 1 | 1 |
| 4 | 3 | 3 | 2 | 2 | 1 | 1 |
| 5 | 3 | 4 | 2 | 3 | 2 | 1 |
| 6 | 7 | 6 | 6 | 6 | 6 | 6 |
| 7 | 5 | 5 | 5 | 4 | 3 | 4 |
| 8 | 5 | 5 | 4 | 3 | 2 | 3 |
| 9 | 5 | 6 | 5 | 4 | 4 | 5 |
| 10 | 5 | 6 | 5 | 4 | 4 | 4 |
| 11 | 6 | 6 | 5 | 5 | 4 | 5 |
| 12 | 4 | 5 | 3 | 3 | 2 | 2 |
| **Avg, panel of 12** | **4.7** | **5.0** | **4.0** | **3.7** | **2.9** | **3.3** |
| 13 | 8 | 8 | 7 | 6 | 7 | 8 |
| 14 | 7 | 7 | 5 | 5 | 5 | 6 |
| **Avg, all 14** | **5.1** | **5.4** | **4.3** | **3.9** | **3.4** | **3.8** |

The reel works for AI builders and falls flat for the general panel.

## Length

I counted **214 spoken words** (the script says 215). Reading "5.2" aloud adds about 2 words.

- At 2.6 words/s: **82.3 s**.
- At 1.1x speed: **74.8 s**, plus about 2.8 s of cards, so **about 78 s**.

The script's "78 s of speech, about 81 s total" is about 3 s high. Either way it is long for a reel. I did not check it against `REEL_DEFAULTS.md`.

## Fact check

**Supported:**
- 2x/4x/80x price ratios
- $40 vs $20 output price
- Meter multiples (20/40/80x vs Haiku)
- Release on 9 Nov
- One model, two configurations
- Layers and parameters not published
- Training mix and constitution tuning
- Thinking always on, summary only
- Effort dial
- Fallback automatic in apps, opt-in on API
- Orchestrator and Advisor roles
- Pro runs on credits
- Max up to 50% of the week
- $44.70 / $2.10 = 21.3x
- Best score at xhigh
- All four strip benchmarks
- "Least self-critical" (measured on Mythos, same model)
- Meal Analyser bias and range figures

**Flagged:**
- **Beat 6, "Safety classifiers":** the facts say blocked requests fall back. They don't name the mechanism. Say "blocked requests fall back to an older model."
- **Beat 7, "No new trick":** the card discloses no new technique, which is not the same as there being none. Say "nothing new disclosed."
- **Beat 10, overstated:**
  - Fable is never named in the line.
  - "Finished… in thirty hours" implies a proof from scratch. It was an earlier snapshot, building on an earlier formalization, accepted by hour 30, and those caveats appear only on screen.
- **Beat 1, "they tied":** this is selective. The tie holds on calorie error only; Fable won on portion bias and range coverage. Also, n=25 is a small sample, so say so.
- **Beat 5, "hidden":** a summary is shown, so "hidden" overstates it slightly.
- **Router "not max":** this rests on one benchmark (FrontierCode). Present it as a tip, not a rule.
- **Benchmark strip:** label it "max effort." It sits next to advice to avoid max.
- **Sources:** the release date is attributed to card p.2, but the facts sheet only ties the two-configurations line to p.2.

## Top 6 fixes

1. **Beats 1–2, the cold open assumes viewers know model names.** Try: "Anthropic's priciest AI costs 2x the next one. On my calorie test, it tied, but it was more honest about what it didn't know." That is accurate and sets up a payoff.
2. **Beats 3–7, cut five spec beats to two.** This section is where 7 of the 12 swipe. Keep the one-model/two-configurations beat and the always-thinks/effort-dial beat, and apply the beat 6 and 7 wording fixes. That saves about 12 s.
3. **Beat 10, rewrite the Fermat line.** Try: "A thousand Fable agents, building on earlier work, got a Lean proof of Fermat accepted by hour 30. At hour 18, Opus's team scored 0.26; Fable's, 0.86."
4. **Beat 16, speak the office-work result.** "For office work, Anthropic's own test says Opus beats it." That one line serves the CA, FP&A, IB, consulting and brand personas.
5. **Beats 11–12, add ₹ for Indian viewers.** Express the meter and the Pro/Max lines as ₹ per task as soon as your numbers are in, and include Ultra alongside Max. Multiples alone don't land with personas 4, 5 and 12.
6. **Beats 15–16, gate the reel on the test.** It cannot ship until the 24-cell test has run. On screen, state the effort setting, how many items per task, and that the 25 dishes are your own data. If Fable sweeps, use the alternate line.

## Verdict: **REVISE**

The facts are mostly clean, with four wording fixes. The structure is the problem: front-loaded specs lose the general panel. Fix 2 and fix 4 together should lift stop and value scores for viewers 2, 7, 8 and 12.

I did not check this against the `reel-script-writing` skill.
