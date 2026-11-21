Script is 215 spoken words (hand-counted), about 78 s of speech at 1.1x plus four ~0.7 s cards, so roughly 81 s. I did not check it against the `reel-script-writing` skill or `REEL_DEFAULTS.md` in this pass.

## A. Five improvements (all applied)

1. **Cold open on your own data.** "Costs twice Opus, tied on my calorie test" beats any spec line and sets up the question the reel answers.
2. **Price meter.** A corner counter shows the output-price multiple versus Haiku (1x, 20x, 40x, 80x) and jumps whenever Fable is on screen. It uses multiples, not rupees, until your measured ₹ arrive.
3. **Predict before reveal.** The table draws on empty, the viewer guesses, then the winners fill in.
4. **Paper behaviour as a late re-hook.** "Least self-critical" lands just before the CTA and turns into an action: check its work.
5. **A "DO:" line per section and a router card to screenshot.** Each section ends with a one-line on-screen action, and the router card is the CTA asset.

## B. Script

| # | Section | Spoken | Top-half visual | On-screen text | Viewer feels |
|---|---|---|---|---|---|
| 1 | Cold open | "Fable 5.2 costs twice what Opus does. On my calorie test, they tied." | Two bars draw on "twice" ($40 vs $20); two equal bars on "tied" | 81 vs 83 kcal error, 25 dishes | Wait, what? |
| 2 | Cold open | "So when is it worth it?" | Meter appears at 80x | Fable 5.2, released 9 Nov 2026 | Curious |
| C1 | Card | (whoosh + impact) | Full frame | THE BODY, NOT THE BRAIN | Reset |
| 3 | 1 | "Anthropic won't show you the brain. No layers, no parameters. The paper shows the body." | Black box with "?" on "brain"; outline draws around it on "body" | Internals: not published | Intrigued |
| 4 | 1 | "One model, two configurations: Fable for everyone, Mythos for vetted organisations." | Box splits into two branches on "two" | Same model, different safeguards | Clear |
| 5 | 1 | "It always thinks, hidden. An effort dial sets how hard." | Dashed thinking loop on "thinks"; dial low→max on "dial" | You see a summary only | Aha |
| 6 | 1 | "Safety classifiers reroute blocked requests to a weaker model." | Gate before the box; arrow bends away on "reroute" | Auto in apps, opt-in on API | Informed |
| 7 | 1 | "Training? Web, datasets, synthetic data, then constitution tuning. No new trick." | Four inputs funnel in; stamp on "constitution" | + opted-in user data. DO: stop hunting for a secret | Trusts you |
| C2 | Card | (whoosh + impact) | Full frame | FABLE BECOMES THE BOSS | Reset |
| 8 | 2 | "The real shift: Fable plans or advises. Cheaper models do the work." (re-hook 1) | Fable node on top; arrows down to three small nodes on "cheaper" | Orchestrator / Advisor | Sees the pattern |
| 9 | 2 | "Gym Jarvis before: one model did everything. After: Fable plans, Sonnet and Haiku execute." | Left: one fat box. Right draws on "After": Fable → Sonnet, Haiku. Meter drops | Before / After | Wants to copy it |
| 10 | 2 | "A thousand agents finished a Lean proof of Fermat's Last Theorem in thirty hours." | Dot grid fills; tick on "thirty" | Earlier snapshot, built on an earlier formalization. DO: plan with Fable, execute cheap | Wow |
| C3 | Card | (whoosh + impact) | Full frame | THE BILL | Reset |
| 11 | 3 | "Now the bill. Fable output costs twice Opus, four times Sonnet, eighty times Haiku." (re-hook 2) | Four bars draw on each number; meter spins | 2x / 4x / 80x per token; thinking bills as output | Ouch |
| 12 | 3 | "On Pro, Fable isn't in your plan; it burns paid credits. On Max, at most half your week." | Pro tank with a side pipe to "credits"; Max tank half-shaded on "half" | Max/Ultra: up to 50% of weekly limit | That's me |
| 13 | 3 | "Max effort cost twenty-one times low, and wasn't the best score." | Line climbs $2.10 → $44.70; star lands one step below max | FrontierCode, Anthropic's numbers | Surprised |
| 14 | 3 | "So route it: Haiku for routine, Sonnet for drafts, Fable for hard planning." | Router draws: task type → model, one arrow per phrase | DO: /model before you start | Relief |
| C4 | Card | (whoosh + impact) | Full frame | THE SCORESHEET | Reset |
| 15 | 4 | "I ran four models on six daily tasks. Guess the winner." (re-hook 3) | Empty 6x4 table draws; 1 s hold | Writing, Thinking, Coding, Summary, Maths, Vision | Guessing |
| 16 | 4 | "Fable won [N_F] of six. [N_CHEAP] went to a cheaper model." | Winner cells fill row by row; ₹ and seconds columns slide in | [INR_*], [SEC_*]; small "Anthropic's numbers" strip | Was I right? |
| 17 | Re-hook | "Its own paper: among the least self-critical Claudes. Check its work." (re-hook 4) | Fable node grading itself with a tick; red "?" on "check" | DO: review with a second model or tests | Wary, armed |
| 18 | CTA | "Comment FABLE for the router card and full scoresheet." | Router card, full top half, held 2 s | Comment FABLE | Acts |
| 19 | Tease | "Saturday: the Workout Analyser." | One outline of a new diagram starts drawing, then cuts | Saturday | Returns |

**Router card (screenshot asset)**

| Task | Model |
|---|---|
| Routine, extraction, formatting | Haiku 5.5 |
| Drafts, summaries, everyday code | Sonnet 5.5 |
| Office documents, long write-ups | Opus 5.5 |
| Hard planning, advising, multi-agent lead | Fable 5.2, effort high or xhigh, not max |

The card's rows are a draft; adjust them to match tonight's results before it goes out.

**"Anthropic's numbers" strip for beat 16 (Fable 5.2 vs Opus 5.5)**

| Day-to-day task | Benchmark | Fable 5.2 | Opus 5.5 |
|---|---|---|---|
| Coding | SWE-bench Pro | 93.0 | 89.9 |
| Hard reasoning | Humanity's Last Exam, no tools | 73.2 | 64.4 |
| Office work | GDPval-AA Elo | 1831 | 1866 |
| Freelance projects | Remote Labor Index | 41.3% | 21.3% |

Vision gets your own Meal Analyser row, labelled as your data: portion bias +3 g vs +28 g, and the stated range held the truth 68% vs 48%.

## C. Placeholders and what to measure

All use the same prompts for all four models (F, O, S, H) at one fixed effort setting, which you state on screen.

- **[W_F] [W_O] [W_S] [W_H]:** writing, scored as checklist items met, plus a blind judge for style only.
- **[T_*]:** critical thinking, scored as correct out of N against an answer key.
- **[C_*]:** coding, scored as unit tests passed out of N.
- **[S_*]:** summarising, scored as checklist facts kept with zero invented facts.
- **[M_*]:** maths/Excel, scored as correct out of N against an answer key.
- **[V_*]:** vision/photo, scored against known ground truth; you can reuse the Meal Analyser dishes.
- **[INR_*]:** ₹ cost per task per model, from billed tokens including thinking; state the exchange rate used.
- **[SEC_*]:** wall-clock seconds per task per model.
- **[N_F]:** number of the six tasks Fable won outright.
- **[N_CHEAP]:** number won or tied by a cheaper model.

Two lines depend on facts I can't confirm:

- **Beat 16:** if Fable wins all six, the line becomes "Fable won all six. Here's what it cost."
- **Beat 9:** "After" must describe what Gym Jarvis actually does now. If the split is only planned, say "Next:" instead of "After:".

## D. Sources

- **Release date, one model in two configurations:** system card p.2.
- **Internals not published, training mix, constitution post-training, no new technique:** card p.11.
- **Always-on thinking, summary only, effort dial:** your verified facts sheet (no page ref given).
- **Fallback routing, automatic in apps and opt-in on the API:** card p.~44 and launch post.
- **Orchestrator and Advisor roles:** launch post.
- **Fermat result (1,000 agents, earlier snapshot, hour 30, earlier formalization):** card p.226.
- **Prices and the 2x/4x/80x ratios:** API pricing in your facts sheet.
- **Effort cost $2.10 to $44.70, best score at xhigh:** card p.209.
- **Pro on usage credits, Max/Ultra 50% cap, /model:** support.claude.com, Nov 2026.
- **Benchmark strip:** card Table 8.1.A, max effort.
- **Least self-critical:** card behaviour findings, measured on Mythos 5.2 (same model).
- **Calorie tie, portion bias, range coverage:** your Meal Analyser eval, 25 dishes.
