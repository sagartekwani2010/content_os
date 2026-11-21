# Fable 5.2 deep-dive: final script v2

The script is **225 spoken words**, about **82 s** at 1.1x, counting four 0.7 s cards and the 1 s guess hold (2.6 words/s base pace, taken from the review). It cannot ship until the 24-cell test has run and the placeholders are filled. I did not check it against the `reel-script-writing` skill or `REEL_DEFAULTS.md`.

## A. Applied ideas

**Kept from v1**
1. **Cold open on your own data**, now without model names in the first line.
2. **Price meter** in the corner (1x, 20x, 40x, 80x versus Haiku output), with ₹ per task under it once measured.
3. **Predict before reveal** on the scoresheet.
4. **"Least self-critical" as the late re-hook**, turned into an action.
5. **A "DO:" line per section and the router card** as the CTA asset.

**Panel fixes applied**
1. **Cold open:** no jargon, and the tie is no longer selective. The portion result is spoken, and the range result and n=25 are on screen.
2. **Spec section cut from five beats to two.** Brain/body, fallback and training are no longer spoken; fallback and "nothing new disclosed" moved to on-screen text with the corrected wording.
3. **Fermat line rewritten:** Fable is named, "building on earlier work" and "accepted by hour thirty" are spoken.
4. **Office-work result is spoken** (beat 14), and Opus is in the spoken router.
5. **Ultra added** beside Max, with ₹ placeholders on the meter and the bill beats.
6. **Smaller wording fixes:**
   - "Hidden" became "you see only a summary".
   - "Not max" is a tip tied to one benchmark.
   - The strip is labelled "max effort".
   - The release-date source is corrected.

**Two places I departed from the review**
- **Hour-18 scores (0.86 vs 0.26) are on screen, not spoken.** The facts don't say what the score measures, and speaking them costs 16 words.
- **"Anthropic's own test" became "Anthropic's own system card".** The facts show the card reports GDPval-AA, not that Anthropic built it.

## B. Script

| # | Section | Spoken | Top-half visual | On-screen text | Viewer feels |
|---|---|---|---|---|---|
| 1 | Cold open | "Anthropic's new top model costs twice the next one down. On my calorie test, they tied." | Two bars draw on "twice" ($40 vs $20); two equal bars on "tied" | Calorie error ~81 vs ~83 kcal. 25 dishes, my own test | Wait, what? |
| 2 | Cold open | "But the pricier one judged portions better. So when is it worth it?" | Portion bars +3 g vs +28 g; meter appears at 80x | Fable 5.2 vs Opus 5.5. Stated range held the truth 68% vs 48% | Curious |
| C1 | Card | (whoosh + impact) | Full frame | WHAT YOU'RE PAYING FOR | Reset |
| 3 | 1 | "It's Fable five point two. One model, two configurations: Fable for everyone, Mythos for vetted organisations." | One box splits into two branches on "two"; a gate bends one arrow away | Released 9 Nov 2026. Same model, different safeguards. Blocked requests fall back to a less capable model: auto in apps, opt-in on API | Clear |
| 4 | 1 | "It always thinks. You see only a summary. An effort dial sets how hard." | Dashed thinking loop on "thinks"; dial low→max on "dial" | low / medium / high / xhigh / max. Internals not published; no new training method disclosed. DO: check your effort setting (apps default medium, API high) | Aha |
| C2 | Card | (whoosh + impact) | Full frame | FABLE BECOMES THE BOSS | Reset |
| 5 | 2 | "The real shift: Fable plans or advises, and smaller models execute." (re-hook 1) | Fable node on top; arrows down to three small nodes on "smaller" | Orchestrator / Advisor | Sees the pattern |
| 6 | 2 | "Gym Jarvis before: one model did everything. After: Fable plans, Sonnet and Haiku execute." | Left: one fat box. Right draws on "After": Fable → Sonnet, Haiku. Meter drops | Before / After | Wants to copy it |
| 7 | 2 | "A thousand Fable agents, building on earlier work, got a Lean proof of Fermat's Last Theorem accepted by hour thirty." | Dot grid fills; tick on "thirty" | Earlier snapshot of Fable 5.2, built on an earlier formalization. Hour 18: Fable team 0.86, Opus 5.5 team 0.26. DO: plan with Fable, execute cheap | Wow |
| C3 | Card | (whoosh + impact) | Full frame | THE BILL | Reset |
| 8 | 3 | "Fable output costs twice Opus, four times Sonnet, eighty times Haiku." (re-hook 2) | Four bars draw on each number; meter spins | 2x / 4x / 80x per token; thinking bills as output. [INR_*] per task | Ouch |
| 9 | 3 | "On Pro, Fable isn't in your plan; it runs on paid credits. On Max or Ultra, at most half your weekly limit." | Pro tank with a side pipe to "credits"; Max/Ultra tank half-shaded on "half" | Pro: pay-as-you-go credits. Max/Ultra: up to 50% of the weekly limit, then credits or switch model | That's me |
| 10 | 3 | "On one benchmark, max effort cost twenty-one times low effort, and didn't score best." | Line climbs $2.10 → $44.70; star lands one step below max | FrontierCode, cost per task, from Anthropic's system card. Best score at xhigh | Surprised |
| 11 | 3 | "So route it: Haiku for routine, Sonnet for drafts, Opus for office work, Fable for hard planning." | Router draws: task type → model, one arrow per phrase | DO: /model before you start | Relief |
| C4 | Card | (whoosh + impact) | Full frame | THE SCORESHEET | Reset |
| 12 | 4 | "I ran four models on six daily tasks. Guess the winner." (re-hook 3) | Empty 6x4 table draws; 1 s hold | Writing, Thinking, Coding, Summary, Maths, Vision. Effort: [EFFORT]. [N_ITEMS] items per task | Guessing |
| 13 | 4 | "Fable won [N_F] of six. [N_CHEAP] went to a cheaper model." | Winner cells fill row by row; ₹ and seconds columns slide in | [INR_*], [SEC_*]. Vision row: my 25 dishes | Was I right? |
| 14 | 4 | "For office work, Anthropic's own system card puts Opus ahead." | Strip slides in; the office-work row highlights | GDPval-AA Elo: Opus 5.5 1866, Fable 5.2 1831. Max effort | Finally, my job |
| 15 | Re-hook | "The same card: among the least self-critical Claudes. Check its work." (re-hook 4) | Fable node grading itself with a tick; red "?" on "check" | Measured on Mythos 5.2, the same model. DO: review with a second model or tests | Wary, armed |
| 16 | CTA | "Comment FABLE for the router card and full scoresheet." | Router card, full top half, held 2 s | Comment FABLE | Acts |
| 17 | Tease | "Saturday: the Workout Analyser." | One outline of a new diagram starts drawing, then cuts | Saturday | Returns |

**Router card (screenshot asset)**

| Task | Model |
|---|---|
| Routine, extraction, formatting | Haiku 5.5 |
| Drafts, summaries, everyday code | Sonnet 5.5 |
| Office documents, long write-ups | Opus 5.5 |
| Hard planning, advising, multi-agent lead | Fable 5.2 |

Tip line under the card: "Try high or xhigh before max. On one benchmark, max cost 21x low and didn't score best." The rows are a draft, so adjust them to match your results before it goes out.

**System card strip for beat 14 (Fable 5.2 vs Opus 5.5, max effort)**

| Day-to-day task | Benchmark | Fable 5.2 | Opus 5.5 |
|---|---|---|---|
| Coding | SWE-bench Pro | 93.0 | 89.9 |
| Hard reasoning | Humanity's Last Exam, no tools | 73.2 | 64.4 |
| Office work | GDPval-AA Elo | 1831 | 1866 |
| Freelance projects | Remote Labor Index | 41.3% | 21.3% |

The Vision row uses your Meal Analyser data, labelled as yours: portion bias +3 g vs +28 g, and the stated range held the truth 68% vs 48%.

## C. Placeholders and what to measure

Use the same prompts for all four models (F, O, S, H) at one fixed effort setting.

- **[W_F] [W_O] [W_S] [W_H]:** writing, scored as checklist items met, plus a blind judge for style only.
- **[T_*]:** critical thinking, correct out of N against an answer key.
- **[C_*]:** coding, unit tests passed out of N.
- **[S_*]:** summarising, checklist facts kept with zero invented facts.
- **[M_*]:** maths/Excel, correct out of N against an answer key.
- **[V_*]:** vision, scored against known ground truth; the Meal Analyser dishes can be reused.
- **[INR_*]:** ₹ per task per model, from billed tokens including thinking; state the exchange rate on screen.
- **[SEC_*]:** wall-clock seconds per task per model.
- **[EFFORT]:** the effort setting used, shown on screen at beat 12.
- **[N_ITEMS]:** items per task, shown on screen at beat 12.
- **[N_F]:** tasks Fable won outright.
- **[N_CHEAP]:** tasks a cheaper model won outright; show ties separately on the table.

Four lines depend on things I can't confirm:

- **Beats 1–2:** your facts sheet says "Fable vs Opus" for the Meal Analyser eval without versions. The on-screen "Fable 5.2 vs Opus 5.5" holds only if those were the models you ran.
- **Beat 6:** "After" must describe what Gym Jarvis does now. If the split is only planned, say "Next:" instead.
- **Beat 13:** if Fable wins all six, the line becomes "Fable won all six. Here's what it cost."
- **Beat 17:** the Saturday tease is carried over from v1 and is yours to confirm.

## D. Sources

- **One model in two configurations:** system card p.2.
- **Release date 9 Nov 2026:** your facts sheet (no page ref given).
- **Internals not published, no new training technique disclosed:** card p.11.
- **Always-on thinking, summary only, effort dial and defaults:** your facts sheet (no page ref given).
- **Fallback to a less capable model, automatic in apps and opt-in on the API:** card p.~44 and launch post.
- **Orchestrator and Advisor roles:** launch post.
- **Fermat result (1,000 agents, earlier snapshot, earlier formalization, hour 30, 0.86 vs 0.26 at hour 18):** card p.226.
- **Prices and the 2x/4x/80x ratios, thinking billed as output:** API pricing in your facts sheet.
- **Effort cost $2.10 to $44.70, best score at xhigh:** card p.209.
- **Pro on usage credits, Max/Ultra 50% cap, /model:** support.claude.com, Nov 2026.
- **Benchmark strip and the office-work line:** card Table 8.1.A, max effort.
- **Least self-critical:** card behaviour findings, measured on Mythos 5.2 (same model).
- **Calorie tie, portion bias, range coverage:** your Meal Analyser eval, 25 dishes.
- **Gym Jarvis before/after:** your own project, not in the facts sheet.
