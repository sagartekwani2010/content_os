# Fable 5.2 deep-dive: final script v4

The script is **228 spoken words, about 84.5 s at 1.1x** including cards and holds, with every placeholder filled from tonight's results. I did not check it against the `reel-script-writing` skill or `REEL_DEFAULTS.md`, and it is not saved to a file.

## A. Changes applied

1. **New cold open.** It leads with tonight's surprise: the top and the cheapest model got the same scores, at ₹36 vs ₹1. The ₹ hook is spoken in the first eight seconds.
2. **Guess no longer spoiled.** Beat 2 says only that "one harder task split them". The winner and the numbers wait for beats 11–12.
3. **Placeholders gone.** Beat 13 is now the measured tie plus the takeaway. Speed is excluded because rate-limit queueing distorted the timings, and the summary task is excluded because its checklist was flawed. Both are labelled on screen.
4. **Four-model quantity table** replaces the two-model bias beat. Fable vs Opus stays "not conclusive" on screen.
5. **Fermat in plain English:** "a computer-checked proof … in thirty hours". "Earlier snapshot" and "built on earlier work" are on screen, and the unsupported "execute cheap" line is cut.
6. **Router matches sources.** It is Sonnet for most things (Anthropic), Haiku on simple tasks (tonight's result) and Fable for the hard parts. Opus is a card row only, backed by the system card's office-work result.
7. **"Burns through limits faster"** is added to the Pro/Max beat, and a free-user line opens the router beat.
8. **Moved from speech to screen, to fit 85 s:** Mythos, the 2x/4x/80x token ratios, the Opus office-work result, and "or advises".
9. **Cut from the reel:** the range result (68% vs 48%, different dish sets) is scoresheet only, and "every episode, one more task measured" is dropped.

## B. Beat table

| Beat | Section | Spoken (exact) | Top-half visual | On-screen text | Viewer feels |
|---|---|---|---|---|---|
| 1 | Cold open | "I gave Anthropic's new top model and its cheapest the same everyday tasks. Same scores. One bill: thirty-six rupees. The other: one rupee." | Two equal score bars draw on "same scores"; a tall ₹ bar on "thirty-six", a sliver on "one rupee" | Fable 5.2 vs Haiku 5.5. Riddles 8/8, maths 6/6, code 3/3, writing 16/17, both. Cost of all 20 tasks at list price, ₹88 per $ | Wait, what? |
| 2 | Cold open | "Then one harder task split them. So when is it worth paying?" | The equal bars crack apart on "split"; a "?" sits over the gap | 19 tasks scored; summary task excluded (flawed checklist) | Curious |
| C1 | Card | (whoosh + impact) | Full frame | WHAT YOU'RE PAYING FOR | Reset |
| 3 | 1 | "It's Fable five point two. It always thinks before answering." | One box splits into two branches (Fable, Mythos); a dashed thinking loop draws on "thinks" | Released 9 Nov 2026. Same model as Mythos 5.2, which has looser safeguards for vetted organisations. You see only a summary of the thinking | Clear |
| 4 | 1 | "You pay for that thinking, and a dial sets how hard." | Coins drop into the loop on "pay"; dial sweeps low→max on "dial" | low / medium / high / xhigh / max. Thinking bills as output. On one benchmark (FrontierCode), max cost 21x low ($2.10 → $44.70); best score at xhigh | Aha |
| C2 | Card | (whoosh + impact) | Full frame | FABLE BECOMES THE BOSS | Reset |
| 5 | 2 | "The real shift: Fable plans, and smaller models do the work." (re-hook 1) | Fable node on top; arrows drop to three small nodes on "smaller" | Orchestrator: plans and hands off. Advisor: advises a smaller model | Sees the pattern |
| 6 | 2 | "A thousand Fable agents produced a computer-checked proof of Fermat's Last Theorem in thirty hours." | Dot grid fills on "thousand"; tick on "thirty" | Earlier snapshot of Fable 5.2, built on an earlier formalization. Hour 18: Fable team 0.86, Opus 5.5 team 0.26 | Wow |
| C3 | Card | (whoosh + impact) | Full frame | THE BILL | Reset |
| 7 | 3 | "Opus cost twenty rupees, Sonnet eight. Fable: thirty-two times Haiku, same scores." (re-hook 2) | Four ₹ bars draw in order: 20, 8, then 36 towering over 1 on "thirty-two" | ₹36 / ₹20 / ₹8 / ₹1.1 for 20 tasks. Per task: ₹1.8 / ₹1 / ₹0.4 / ₹0.06. Per token, Fable output is 2x Opus, 4x Sonnet, 80x Haiku. Effort high | Ouch |
| 8 | 3 | "On Pro, Fable runs on paid credits, not your plan. Max or Ultra: half your weekly limit at most, and it burns through limits faster." | Pro tank with a side pipe to "credits"; Max/Ultra tank half-shades on "half", drains fast on "burns" | Pro: pay-as-you-go credits from the first message. Max/Ultra: up to 50% of the weekly limit, then credits or switch model | That's me |
| 9 | 3 | "Not paying? Still applies: Sonnet for most things, says Anthropic. Haiku kept up on my simple tasks. Fable for the hard parts." | Router card draws, one row per sentence | ROUTER (card below). Haiku: 8/8, 6/6, 3/3; writing 16/17 vs Sonnet 17/17 | Relief |
| 10 | 3 | "Then stretch it: lower effort, unused tools off, new chat per topic. Screenshot this." | "Fable on Pro" card replaces the router; a line ticks on each phrase; 1 s hold | FABLE ON PRO (card below) | Saves it |
| C4 | Card | (whoosh + impact) | Full frame | BY HOW MUCH | Reset |
| 11 | 4 | "The harder task: grams of food from a photo, twenty-five weighed dishes. Guess the gap." (re-hook 3) | Plate photo with "? g" over it; 1 s hold | Nutrition5k weighed dishes. Same 25 for all four models | Guessing |
| 12 | 4 | "Average miss: Fable forty-nine grams, Opus fifty-seven, Sonnet seventy-two, Haiku seventy-five. About a third less error than the cheaper two." | Four-model table fills one row per model name; Sonnet and Haiku rows shade on "cheaper two" | Quantity table (below). Fable vs Opus: not conclusive at 25 dishes (95% CI −19.6 to +3.6 g) | Was I right? |
| 13 | 4 | "Everyday: a tie, pay less. Hard judgement: Fable was closer." | Everyday table (below) flashes all-equal on "tie"; the portion bars return on "closer" | Everyday tasks: all four tied on riddles, maths and code. Office work, per Anthropic's system card: Opus 5.5 1866, Fable 5.2 1831 (GDPval-AA Elo) | Sees the rule |
| 14 | Re-hook | "Anthropic's own report: among the least self-critical Claudes. Check its work." (re-hook 4) | Fable node ticks its own work; red "?" lands on "check" | Measured on Mythos 5.2, the same model. Review with tests or a second model | Wary, armed |
| 15 | CTA | "Comment FABLE for the router and Pro tips cards and the full scoresheet." | Both cards side by side; scoresheet slides in behind | Comment FABLE | Acts |
| 16 | Tease | "Saturday: the Workout Analyser." | A new diagram outline starts, then cuts | Saturday | Returns |

**Quantity table (beat 12): same 25 weighed dishes, two-step mode, effort high**

| Model | Portion error | Overestimate | Calorie error | Protein error |
|---|---|---|---|---|
| Fable 5.2 | 49 g | +7 g | 81 kcal | 5.6 g |
| Opus 5.5 | 57 g | +28 g | 83 kcal | 6.0 g |
| Sonnet 5.5 | 72 g | +47 g | 114 kcal | 6.7 g |
| Haiku 5.5 | 75 g | +62 g | 126 kcal | 10.5 g |

**Everyday table (beat 13): same prompts, effort high**

| Task | Fable | Opus | Sonnet | Haiku |
|---|---|---|---|---|
| Riddles (answer key) | 8/8 | 8/8 | 8/8 | 8/8 |
| Maths, GST, EMI, Excel (answer key) | 6/6 | 6/6 | 6/6 | 6/6 |
| Coding (unit tests) | 3/3 | 3/3 | 3/3 | 3/3 |
| Writing (checklist, blind judge) | 16/17 | 16/17 | 17/17 | 16/17 |
| Cost, all 20 tasks | ₹36 | ₹20 | ₹8 | ₹1.1 |

Footer for both tables: "Cost = list price x tokens used, including thinking. ₹88 per $. Speed not compared. Summary task excluded."

## C. Screenshot cards

**Card 1: Router**

| Task | Model | Why |
|---|---|---|
| Most everyday tasks | Sonnet 5.5 | Anthropic's own advice; 17/17 on writing in my test |
| Simple tasks: riddles, sums, small code | Haiku 5.5 | Matched every model on 17 keyed tasks, at ₹1 vs ₹36 |
| Office documents | Opus 5.5 | Ahead of Fable on Anthropic's office-work benchmark (1866 vs 1831) |
| Hard parts: planning, review, tricky judgement | Fable 5.2 | Closest on my food-portion test; costs the most |

Tip line: "Fable's effort dial is a price dial. On one benchmark, max cost 21x low and didn't score best."
Footer: "My test: 20 tasks, one evening. Small sample."

**Card 2: Fable on Pro**

| # | Do this | Why |
|---|---|---|
| 1 | Watch Settings > Usage | Pro: Fable is paid credits from the first message. Max/Ultra: up to half the weekly limit, and it burns through limits faster |
| 2 | Default to the latest Sonnet; keep Fable for planning, review and tricky reasoning | Lower token cost for most tasks |
| 3 | Lower the effort for routine work | Higher effort uses more tokens |
| 4 | Turn off connectors and web search you don't need | Tools are token-intensive |
| 5 | New chat per topic; batch related questions; use Projects for reused documents | Long chats consume more usage; cached documents count less |
| 6 | Claude Code: /model, /clear between tasks, /compact for long ones, file paths instead of pastes, plan first | Same idea in the terminal |

## D. Sources per beat

| Beat | Source |
|---|---|
| 1, 2, 7, 13 | Tonight's everyday-task run (18 Nov 2026, effort high): scores, costs, exclusions |
| 3 | System card p.2 (one model, two configurations); your facts sheet for the release date, always-on thinking and summary-only |
| 4 | Your facts sheet (effort levels, thinking billed as output); system card p.209 (FrontierCode $2.10 → $44.70, best at xhigh) |
| 5 | Launch post (Orchestrator and Advisor roles) |
| 6 | System card p.226 (1,000 agents, earlier snapshot, earlier formalization, hour 30, 0.86 vs 0.26 at hour 18) |
| 7 (ratios) | API list prices in your facts sheet |
| 8, 10, Card 2 | support.claude.com, Nov 2026 |
| 9, Card 1 | Help center (Sonnet for most tasks, Fable for hard parts); tonight's runs (Haiku, Fable rows); system card Table 8.1.A (Opus row) |
| 11, 12 | Tonight's Meal Analyser run, same 25 Nutrition5k dishes, two-step mode; 95% CI from your eval |
| 13 (office work) | System card Table 8.1.A, max effort |
| 14 | System card behaviour findings, measured on Mythos 5.2 |
| 16 | Carried over from v3; not in your facts sheet |

Four things to confirm before recording:

- **Beat 12, "a third less error":** the facts sheet gives no confidence interval for Fable vs Sonnet or Haiku. The gaps are 23 g and 26 g on 25 dishes, so compute the interval. If it crosses zero, the line becomes "closer in my test".
- **Beat 9, "Not paying? Still applies":** this is the routing lesson only. I have no source on which models the free plan includes, so the line makes no claim about that.
- **Beat 1, "cheapest":** Haiku 5.5 is the cheapest of the four models on your price list.
- **Beat 16:** the Saturday topic is yours to confirm.

## E. Word count and runtime

| Beat | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 | 15 | 16 | Total |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Words | 23 | 12 | 10 | 11 | 11 | 15 | 12 | 25 | 22 | 14 | 15 | 20 | 10 | 11 | 13 | 4 | **228** |

- **Speech:** 228 words at 2.6 words/s is 87.7 s, which is 79.7 s at 1.1x.
- **Cards and holds:** four 0.7 s cards plus two 1 s holds (beats 10 and 11) add 4.8 s.
- **Total:** about **84.5 s**, inside the 75–85 s window with half a second to spare.
- **If it runs long:** cut "says Anthropic" from beat 9, since it is already on the card. That saves about 0.7 s.

The runtime is calculated, not measured from a recording. The reel is not done until you have listened to the final file.
