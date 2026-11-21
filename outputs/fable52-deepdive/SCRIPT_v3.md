# Fable 5.2 deep-dive: final script v3

The script is **225 spoken words**, about **83 s** at 1.1x, counting four 0.7 s cards, the 1 s guess hold and a 1 s screenshot hold on the Pro card (2.6 words/s base pace; placeholders counted as about four words). It cannot ship until tonight's tasks have run and the placeholders are filled. I did not check it against the `reel-script-writing` skill or `REEL_DEFAULTS.md`, and it is not saved to a file.

## A. Applied ideas

**New in v3**
1. **"Fable on Pro" card** is the value moment of section 3, straight after the router, built only from the help-center tips.
2. **Two consecutive cards, not one combined.** Ten lines on one card would be unreadable at top-half size; the CTA delivers both as one image.
3. **Section 4 is now "by how much".** It opens on your portion test, then tonight's tasks, each with one gap number.
4. **Portion numbers corrected to the same-25-dish set:** bias +7 g vs +28 g is spoken; the 8 g error gap is labelled "not conclusive" on screen.
5. **Range result relabelled** as different dish sets (50 vs 25).
6. **Series line added:** "Every episode, one more task measured."

**Kept from v2 (panel fixes)**
- The cold open has no jargon or model names in the first line; the tie and the portion result are both spoken.
- The spec section is two beats; fallback and "nothing new disclosed" stay on screen.
- The Fermat wording is unchanged.
- The office-work result is spoken and Opus is in the spoken router.
- Ultra sits beside Max.
- "You see only a summary" and the "max effort" label on the strip are unchanged.

**Three places I departed from v2, to make room**
- **Gym Jarvis before/after is cut from speech.** It was also the one beat that depended on an unconfirmed fact. The before/after diagram can stay as the visual on beat 5 if the split is live.
- **The effort benchmark (21x) moved from speech to screen**, on the router beat and the router card's tip line. It is not on the Pro card, because it comes from the system card, not the help center.
- **The cold open says who overestimated, not by how much.** The numbers are held for the guess in section 4.

## B. Script

| # | Section | Spoken | Top-half visual | On-screen text | Viewer feels |
|---|---|---|---|---|---|
| 1 | Cold open | "Anthropic's new top model costs twice the next one down. On my calorie test, they tied." | Two bars draw on "twice" ($40 vs $20); two equal bars on "tied" | Calorie error 81 vs 83 kcal. Same 25 dishes, my own test | Wait, what? |
| 2 | Cold open | "But the cheaper one overestimated portions far more. So when is double worth it?" | Plate outline inflates on "overestimated"; meter appears at 80x | Fable 5.2 vs Opus 5.5. Stated kcal range held the truth: 68% (50 dishes) vs 48% (25 dishes), different sets | Curious |
| C1 | Card | (whoosh + impact) | Full frame | WHAT YOU'RE PAYING FOR | Reset |
| 3 | 1 | "It's Fable five point two. One model, two configurations: Fable for everyone, Mythos for vetted organisations." | One box splits into two branches on "two"; a gate bends one arrow away | Released 9 Nov 2026. Same model, different safeguards. Blocked requests fall back to a less capable model: auto in apps, opt-in on API | Clear |
| 4 | 1 | "It always thinks. You see only a summary. An effort dial sets how hard." | Dashed thinking loop on "thinks"; dial low→max on "dial" | low / medium / high / xhigh / max. Internals not published; no new training method disclosed. Apps default medium, API high | Aha |
| C2 | Card | (whoosh + impact) | Full frame | FABLE BECOMES THE BOSS | Reset |
| 5 | 2 | "The real shift: Fable plans or advises, and smaller models execute." (re-hook 1) | Fable node on top; arrows down to three small nodes on "smaller" | Orchestrator / Advisor | Sees the pattern |
| 6 | 2 | "A thousand Fable agents, building on earlier work, got a Lean proof of Fermat's Last Theorem accepted by hour thirty." | Dot grid fills; tick on "thirty" | Earlier snapshot of Fable 5.2, built on an earlier formalization. Hour 18: Fable team 0.86, Opus 5.5 team 0.26. DO: plan with Fable, execute cheap | Wow |
| C3 | Card | (whoosh + impact) | Full frame | THE BILL | Reset |
| 7 | 3 | "Fable output costs twice Opus, four times Sonnet, eighty times Haiku." (re-hook 2) | Four bars draw on each number; meter spins | 2x / 4x / 80x per token; thinking bills as output. [INR_*] per task | Ouch |
| 8 | 3 | "On Pro, Fable runs on paid credits, not your plan. Max or Ultra: at most half your weekly limit." | Pro tank with a side pipe to "credits"; Max/Ultra tank half-shaded on "half" | Pro: pay-as-you-go credits from the first message. Max/Ultra: up to 50% of the weekly limit, then credits or switch model | That's me |
| 9 | 3 | "So route it: Haiku routine, Sonnet drafts, Opus office work, Fable hard planning." | Router card draws, one row per phrase | ROUTER. On one benchmark (FrontierCode), max effort cost 21x low ($2.10 → $44.70) and best score came at xhigh | Relief |
| 10 | 3 | "Then stretch it: lower effort, unused tools off, new chat per topic. Screenshot this." | "Fable on Pro" card replaces the router; lines tick on each phrase; 1 s hold | FABLE ON PRO (card below) | Saves it |
| C4 | Card | (whoosh + impact) | Full frame | BY HOW MUCH | Reset |
| 11 | 4 | "Task one, mine: grams of food from a photo, twenty-five weighed dishes. Guess the gap." (re-hook 3) | Plate photo with "? g" over it; 1 s hold | Nutrition5k weighed dishes. Same 25 for both models | Guessing |
| 12 | 4 | "Opus overestimated by twenty-eight grams. Fable by seven." | Two bars from a zero line: +28 g, +7 g | Big: +28 g vs +7 g. Small: average miss 57 g vs 49 g, gap not conclusive at 25 dishes (95% CI −19.6 to +3.6 g). Calories: tie | Was I right? |
| 13 | 4 | "Then [N_MORE] more daily tasks. Fable won [N_F]; biggest gap, [GAP_MAX]." | Table fills row by row: task, Fable, best other, by how much, ₹ | [GAP_*] per row, [INR_*], [SEC_*]. Effort: [EFFORT]. [N_ITEMS] items per task. [N_CHEAP] went to a cheaper model | Sees the size |
| 14 | 4 | "For office work, Anthropic's own system card puts Opus ahead." | Strip slides in; the office-work row highlights | GDPval-AA Elo: Opus 5.5 1866, Fable 5.2 1831. Max effort | Finally, my job |
| 15 | Re-hook | "The same card: among the least self-critical Claudes. Check its work." (re-hook 4) | Fable node grading itself with a tick; red "?" on "check" | Measured on Mythos 5.2, the same model. DO: review with a second model or tests | Wary, armed |
| 16 | CTA | "Comment FABLE for both cards and the scoresheet." | Both cards side by side | Comment FABLE | Acts |
| 17 | Tease | "Every episode, one more task measured. Saturday: the Workout Analyser." | Table gains one empty row; a new diagram outline starts, then cuts | Saturday | Returns |

**Card 1: Router (beat 9)**

| Task | Model |
|---|---|
| Routine, extraction, formatting | Haiku 5.5 |
| Drafts, summaries, most everyday tasks | Sonnet 5.5 |
| Office documents, long write-ups | Opus 5.5 |
| Hard planning, advising, multi-agent lead | Fable 5.2 |

Tip line: "Try high or xhigh before max. On one benchmark, max cost 21x low and didn't score best." The rows are a draft, so adjust them to tonight's results.

**Card 2: Fable on Pro (beat 10)**

| # | Do this | Why |
|---|---|---|
| 1 | Watch Settings > Usage | Pro: Fable is paid credits from the first message. Max/Ultra: up to half the weekly limit, and Fable uses it faster |
| 2 | Default to the latest Sonnet; keep Fable for planning, review and tricky reasoning | Lower token cost for most tasks |
| 3 | Lower the effort for routine work | Higher effort uses more tokens |
| 4 | Turn off connectors and web search you don't need | Tools are token-intensive |
| 5 | New chat per topic; batch related questions; use Projects for reused documents | Long chats consume more usage; cached documents count less |
| 6 | Claude Code: /model, /clear between tasks, /compact for long ones, file paths instead of pastes, plan first | Same idea in the terminal |

**System card strip for beat 14 (Fable 5.2 vs Opus 5.5, max effort)**

| Day-to-day task | Benchmark | Fable 5.2 | Opus 5.5 |
|---|---|---|---|
| Coding | SWE-bench Pro | 93.0 | 89.9 |
| Hard reasoning | Humanity's Last Exam, no tools | 73.2 | 64.4 |
| Office work | GDPval-AA Elo | 1831 | 1866 |
| Freelance projects | Remote Labor Index | 41.3% | 21.3% |

**Scoresheet row 1 (measured, same 25 dishes, two-step pipeline)**

| Measure | Fable | Opus | By how much |
|---|---|---|---|
| Portion bias (overestimate) | +7 g | +28 g | Opus overestimates about 4x more |
| Portion error | 49 g (28.5%) | 57 g (33.1%) | 8 g, not conclusive at n=25 |
| Calorie error | 81 kcal | 83 kcal | Tie |
| Protein error | 5.6 g | 6.0 g | 0.4 g |

Direct-guess mode on the same 25 dishes points the same way (bias +12 g vs +31 g, portion error 39 g vs 50 g, calories 74 vs 81 kcal). It is on the full scoresheet, not in the reel.

## C. Placeholders and what to measure

Use the same prompts for all four models (F, O, S, H) at one fixed effort setting.

- **[GAP_W]:** writing, Fable minus the best other model, in checklist items met; a blind judge for style only.
- **[GAP_T]:** critical thinking, gap in correct answers out of N against an answer key.
- **[GAP_C]:** coding, gap in unit tests passed out of N.
- **[GAP_S]:** summarising, gap in checklist facts kept, with invented facts counted separately.
- **[GAP_M]:** maths/Excel, gap in correct answers out of N against an answer key.
- **[GAP_MAX]:** the largest of those gaps, spoken in beat 13 with its unit and task name.
- **[N_MORE]:** how many of the five tasks you finish tonight.
- **[N_F]:** tasks Fable won outright.
- **[N_CHEAP]:** tasks a cheaper model won outright; show ties separately.
- **[INR_*]:** ₹ per task per model, from billed tokens including thinking; state the exchange rate on screen.
- **[SEC_*]:** wall-clock seconds per task per model.
- **[EFFORT]** and **[N_ITEMS]:** shown on screen at beat 13.

Apply the portion-test rule to every row: if N is too small to separate two models, the cell says "not conclusive" and does not count as a win.

Four lines depend on things I can't confirm:

- **Beats 2 and 12:** the facts sheet says "Fable vs Opus" for the Meal Analyser eval without versions. "Fable 5.2 vs Opus 5.5" holds only if those were the models you ran.
- **Beat 13:** if Fable wins every task, the line becomes "Fable won all [N_MORE]. Here's what it cost." If it wins none, the cold open still holds but beat 13 needs a rewrite.
- **Beat 5 visual:** use the Gym Jarvis before/after diagram only if the split is live.
- **Beat 17:** the Saturday tease is carried over from v2 and is yours to confirm.

## D. Sources

- **One model in two configurations:** system card p.2.
- **Release date 9 Nov 2026:** your facts sheet (no page ref given).
- **Internals not published, no new training technique disclosed:** card p.11.
- **Always-on thinking, summary only, effort dial and defaults:** your facts sheet (no page ref given).
- **Fallback to a less capable model, automatic in apps and opt-in on the API:** card p.~44 and launch post.
- **Orchestrator and Advisor roles:** launch post.
- **Fermat result (1,000 agents, earlier snapshot, earlier formalization, hour 30, 0.86 vs 0.26 at hour 18):** card p.226.
- **Prices and the 2x/4x/80x ratios, thinking billed as output:** API pricing in your facts sheet.
- **Effort cost $2.10 to $44.70 (21x), best score at xhigh:** card p.209, FrontierCode.
- **Pro on usage credits, Max/Ultra 50% cap, and every line of the Fable on Pro card:** support.claude.com, Nov 2026.
- **Benchmark strip and the office-work line:** card Table 8.1.A, max effort.
- **Least self-critical:** card behaviour findings, measured on Mythos 5.2 (same model).
- **Portion bias, portion error with its 95% CI, calorie tie, protein error, direct-guess figures:** your Meal Analyser eval, same 25 Nutrition5k dishes.
- **Range coverage 68% vs 48%:** your Meal Analyser eval, 50 dishes for Fable and 25 for Opus, different sets.
