# Food tracker reel: script (v5, 16 November 2026)

Status: **draft for creator approval.** All numbers are from `demos/food-tracker/RESULTS.md`
(Nutrition5k test split, n = 50, Claude Fable 5.2). `{QUESTION}` and `{DELTA}` are measured on the
morning of the shoot from Sagar's lunch photo, before recording beat 11.

- **Promise:** "I built an AI calorie counter the way the research says. The lazy version matched it."
- **Science layer:** agents with defined jobs, a retrieval tool, a Claude skill with a guardrail, then
  experiments: a baseline, an oracle test, a calibration check.
- **Plate thread (subtle):** Sagar's lunch is the first frame and the last; in between, only a small
  corner chip with its calorie number.
- **Length:** about 270 spoken words, about 1:45.

| # | Spoken line | Top-half visual |
|---|---|---|
| 1 | "I built an AI calorie counter exactly the way the research says to. Then I tested it against the lazy version. The lazy version matched it." | B1: phone photographing Sagar's lunch; chip "? kcal" |
| 2 | "Two Google papers shaped it. Nutrition5k weighed five thousand dishes and found the hard part isn't naming the food. It's how much is there." | `01_paper_nutrition5k.png` |
| 3 | "Im2Calories split the job in three: find the food, size it, look it up." | `02_paper_im2calories.png` |
| 4 | "So I built it as two agents. A vision agent on Fable 5.2 lists every item and its grams. It is not allowed to say calories." | NEW `agents_diagram.png`, step 1 lit |
| 5 | "A retrieval tool searches thirteen thousand USDA foods, and a matcher agent picks the right one, or rejects them all." | Same diagram, steps 2–3 lit |
| 6 | "I packaged it as a Claude skill with one guardrail: if it isn't sure, it has to ask me before it saves." | Same diagram, guardrail lit; `SKILL.md` header as a card |
| 7 | "Then the experiment. Fifty dishes, each weighed in a lab. It missed by about 84 calories a plate." | `06_eval_result_card.png` |
| 8 | "The lazy version, one prompt asking for calories: 77. Statistically, a tie." | `07_two_step_vs_direct.png` |
| 9 | "So I ran an oracle test: keep everything, just fix the weight. The miss drops from 77 to 45. The error was never the food. It's the portion." | `13_moment_size_is_the_hard_part.png` |
| 10 | "Its worst miss: 194 grams of chicken hidden under carrots. It saw 35. Five hundred calories became ninety-four." | `08_failure_1.png` |
| 11 | "But it knew. On that plate its confidence was 0.3. Flagging unsure plates caught 12 of its 15 worst misses." | NEW `confidence_catch.png` |
| 12 | "So every estimate is now logged and monitored. My lunch: 653 calories, but anywhere from 453 to 911. And the thing it was least sure about? The ghee in my dal." | `14_monitoring_dashboard` (simplified) → lunch, chip settles |
| 13 | "Next: a card in the photo for scale, and tables built for Indian food." | Lunch photo with card (shot tomorrow) + `15_improvements_roadmap.png` |
| 14 | "So trust AI for what's on your plate. Not for how much." | Lunch, chip final; text "what ✓ · how much ✗" |

## Small on-screen text

- Beats 7–11: `Nutrition5k test dishes · n = 50 · Claude Fable 5.2 · 95% CI shown`.
- Beat 8: "difference within error bars".
- Beat 11: "flagged 31 of 50 plates" (the cost of the catch).
- Beat 12: "history: simulated data".

## Claims this reel does not make

- Two-step beats direct guessing; Fable beats Opus; any accuracy on Indian or home food.
- Oil or ghee as the main error; real usage history; nutrition advice.
- "Agents improved accuracy." They make every number traceable and make the guardrail possible;
  accuracy is limited by portion size.

## Cut from v4 (kept in reserve)

Chia pudding wrong-row failure (+389 kcal), same photo twice (up to 57 kcal apart), dal 50–145 kcal
per 100 g source spread.
