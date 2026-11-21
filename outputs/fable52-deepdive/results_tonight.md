TONIGHT'S MEASURED RESULTS (18 Nov 2026, Claude CLI, effort high for all, same prompts; costs = Anthropic list prices x tokens actually used incl. thinking; 1 USD = ~₹88, state on screen)
A. QUANTITY (his Meal Analyser pipeline, same 25 weighed Nutrition5k dishes, two-step table mode):
| Model | portion error (g) | overestimate bias (g) | calorie error (kcal) | protein error (g) |
| Fable 5.2 | 49 | +7 | 81 | 5.6 |
| Opus 5.5 | 57 | +28 | 83 | 6.0 |
| Sonnet 5.5 | 72 | +47 | 114 | 6.7 |
| Haiku 5.5 | 75 | +62 | 126 | 10.5 |
Fable vs Opus portion gap not conclusive at n=25; vs Sonnet/Haiku it is about a third smaller error and calories ~30% closer.
B. EVERYDAY TASKS (20 tasks: 8 remixed riddles with answer keys, 6 maths/GST/EMI/Excel with keys, 3 coding tasks with unit tests, 2 writing tasks with checklists judged blind by OpenAI gpt-5.5, 1 summary):
- Riddles 8/8, maths 6/6, coding 3/3 for ALL FOUR models.
- Writing checklist: Fable 16/17, Opus 16/17, Sonnet 17/17, Haiku 16/17.
- Cost for the whole 20-task set: Fable $0.414 (~₹36), Opus $0.224 (~₹20), Sonnet $0.093 (~₹8), Haiku $0.013 (~₹1.1). Per task: Fable ~₹1.8, Opus ~₹1, Sonnet ~₹0.4, Haiku ~₹0.06. Fable cost ~32x Haiku, ~4.5x Sonnet, ~1.8x Opus for the same everyday results.
- Summary item excluded (checklist flawed). Speed excluded (rate-limit queueing distorted timings).
TAKEAWAY: everyday tasks = tie, pay less; hard perception/judgement (how much food is on a plate) = Fable measurably better.
CONFIDENCE (paired bootstrap, same 25 dishes, 95% CI of Fable minus other, absolute error): vs Sonnet grams -23 g [-43.4, -4.6], kcal -33 [-59.6, -7.2]; vs Haiku grams -25 g [-47.7, -5.2], kcal -44 [-86.4, -11.0] -> Fable's advantage over Sonnet and Haiku is statistically clear; vs Opus grams -8 [-19.5, +3.5], kcal -2 [-19.5, +14.2] -> not conclusive.
