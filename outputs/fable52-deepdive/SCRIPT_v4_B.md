# Fable 5.2 deep-dive: Version B (wonder hook)

Version B opens on the Fermat proof and runs **221 spoken words, about 81.4 s at 1.1x** including cards and holds. I did not check it against the `reel-script-writing` skill or `REEL_DEFAULTS.md`, and it is not saved to a file.

## 1. Hypothesis

**B bets that wonder followed by a twist holds the first three seconds better than a money comparison.** The twist is that the cheapest model tied the proof-making model on everyday tasks.

- **Why Fermat over the food test:** the food hook is another "my own test" opener, so it sits too close to A. Fermat is an outside fact, and the tie gives it stakes for the viewer.
- **Why it is a different bet:** A speaks rupees in the first eight seconds. B speaks no rupee figure until beat 7, at about 26 s, so the two openings share nothing but the tie.
- **What to compare:** B also moves the Fermat beat and drops one card, so the 3-second hold and the first 10 s of retention are the clean comparison. Later retention reflects both the hook and the structure.
- **Risk:** the wonder hook may pull viewers who do not care about plan limits, so check saves and "FABLE" comments as well as hold rate.

## 2. Beat table

| Beat | Section | Spoken (exact) | Top-half visual | On-screen text | Viewer feels |
|---|---|---|---|---|---|
| 1 | Cold open | "A thousand AI agents produced a computer-checked proof of Fermat's Last Theorem. In thirty hours." | Dot grid of 1,000 fills on "thousand"; a proof tick lands on "thirty hours" | Earlier snapshot of Fable 5.2. Built on an earlier formalization. Lean proof accepted by the grader by hour 30 (Anthropic system card) | Wow |
| 2 | Cold open | "Then I gave the released model everyday tasks. Anthropic's cheapest model tied it." | The grid shrinks to one node; a small node rises beside it; two equal score bars draw on "tied" | Fable 5.2 vs Haiku 5.5. Riddles 8/8, maths 6/6, code 3/3, writing 16/17, both. 19 tasks scored; summary task excluded (flawed checklist) | Wait, what? |
| 3 | Cold open | "One harder task split them. So when is it worth paying?" | The equal bars crack apart on "split"; a "?" sits over the gap | So when is it worth paying? | Curious |
| C1 | Card | (whoosh + impact) | Full frame | WHAT YOU'RE PAYING FOR | Reset |
| 4 | 1 | "It's Fable five point two. It always thinks before answering." | One box splits into two branches (Fable, Mythos); a dashed thinking loop draws on "thinks" | Released 9 Nov 2026. Same model as Mythos 5.2, which has looser safeguards for vetted organisations. You see only a summary of the thinking | Clear |
| 5 | 1 | "You pay for that thinking, and a dial sets how hard." | Coins drop into the loop on "pay"; dial sweeps low→max on "dial" | low / medium / high / xhigh / max. Thinking bills as output. On one benchmark (FrontierCode), max cost 21x low ($2.10 → $44.70); best score at xhigh | Aha |
| 6 | 1 | "The real shift: Fable plans, and smaller models do the work." (re-hook 1) | Fable node on top; arrows drop to three small nodes on "smaller"; the dot grid from beat 1 ghosts in behind | Orchestrator: plans and hands off. Advisor: advises a smaller model. 1,000-agent teams at hour 18: Fable 0.86, Opus 5.5 0.26 | Sees the pattern |
| C2 | Card | (whoosh + impact) | Full frame | THE BILL | Reset |
| 7 | 2 | "The bill: Fable thirty-six rupees, Opus twenty, Sonnet eight, Haiku one. Fable and Haiku: same scores." (re-hook 2) | Four ₹ bars draw in spoken order; 36 towers over 1; the equal score bars return on "same scores" | ₹36 / ₹20 / ₹8 / ₹1.1 for 20 tasks, list price, ₹88 per $. Per task: ₹1.8 / ₹1 / ₹0.4 / ₹0.06. Per token, Fable output is 2x Opus, 4x Sonnet, 80x Haiku. Effort high | Ouch |
| 8 | 2 | "On Pro, Fable runs on paid credits, not your plan. Max or Ultra: half your weekly limit at most, and it burns through limits faster." | Pro tank with a side pipe to "credits"; Max/Ultra tank half-shades on "half", drains fast on "burns" | Pro: pay-as-you-go credits from the first message. Max/Ultra: up to 50% of the weekly limit, then credits or switch model | That's me |
| 9 | 2 | "Not paying? Still applies: Sonnet for most things, says Anthropic. Haiku kept up on my simple tasks. Fable for the hard parts." | Router card draws, one row per sentence | ROUTER (card unchanged from v4). Haiku: 8/8, 6/6, 3/3; writing 16/17 vs Sonnet 17/17 | Relief |
| 10 | 2 | "Then stretch it: lower effort, unused tools off, new chat per topic. Screenshot this." | "Fable on Pro" card replaces the router; a line ticks on each phrase; 1 s hold | FABLE ON PRO (card unchanged from v4) | Saves it |
| C3 | Card | (whoosh + impact) | Full frame | BY HOW MUCH | Reset |
| 11 | 3 | "The harder task: grams of food from a photo, twenty-five weighed dishes. Guess the gap." (re-hook 3) | Plate photo with "? g" over it; 1 s hold | Nutrition5k weighed dishes. Same 25 for all four models | Guessing |
| 12 | 3 | "Average miss: Fable forty-nine grams, Opus fifty-seven, Sonnet seventy-two, Haiku seventy-five. About a third less error than the cheaper two." | Four-model table fills one row per model name; Sonnet and Haiku rows shade on "cheaper two" | Quantity table (unchanged from v4). Fable vs Opus: not conclusive at 25 dishes (95% CI −19.6 to +3.6 g) | Was I right? |
| 13 | 3 | "Everyday: a tie, pay less. Hard judgement: Fable was closer." | Everyday table flashes all-equal on "tie"; the portion bars return on "closer" | Everyday tasks: all four tied on riddles, maths and code. Office work, per Anthropic's system card: Opus 5.5 1866, Fable 5.2 1831 (GDPval-AA Elo) | Sees the rule |
| 14 | Re-hook | "Anthropic's own report: among the least self-critical Claudes. Check its work." (re-hook 4) | Fable node ticks its own work; red "?" lands on "check" | Measured on Mythos 5.2, the same model. Review with tests or a second model | Wary, armed |
| 15 | CTA | "Comment FABLE for the router and Pro tips cards and the full scoresheet." | Both cards side by side; scoresheet slides in behind | Comment FABLE | Acts |
| 16 | Tease | "Saturday: the Workout Analyser." | A new diagram outline starts, then cuts | Saturday | Returns |

**Word count and runtime**

| Beat | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 | 15 | 16 | Total |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Words | 15 | 13 | 11 | 10 | 11 | 11 | 16 | 25 | 22 | 14 | 15 | 20 | 10 | 11 | 13 | 4 | **221** |

- **Speech:** 221 words at 2.6 words/s is 85.0 s, which is 77.3 s at 1.1x.
- **Cards and holds:** three 0.7 s cards plus two 1 s holds (beats 10 and 11) add 4.1 s.
- **Total:** about **81.4 s**, inside the 75–85 s window.
- **Hook timing:** beat 1 ends at about 5.2 s and the twist lands by about 9.8 s.

The runtime is calculated, not measured from a recording. The reel is not done until you have listened to the final file.

## 3. What changed vs A

1. **Hook swapped.** A's beats 1–2 (same scores, ₹36 vs ₹1) are replaced by three beats: the Fermat proof, the tie with the cheapest model, then "one harder task split them".
2. **Fermat moved, not repeated.** A's beat 6 is now beat 1, with its caveats on screen in the first frame. The hour-18 comparison (0.86 vs 0.26) moves to beat 6's on-screen text.
3. **Money held back.** The rupee figures are first spoken in beat 7, which now reads all four bills. A's "thirty-two times Haiku" line is cut, since the bars show it.
4. **One card dropped.** "FABLE BECOMES THE BOSS" is gone because its section was left with one beat. The orchestrator beat now closes section 1.
5. **Wording kept honest.** The hook says "produced a computer-checked proof", not "proved", and "the released model", because the proof run used an earlier snapshot.
6. **"Same scores" narrowed.** Beat 7 says "Fable and Haiku: same scores", because Sonnet scored 17/17 on writing against 16/17 for the others.
7. **Unchanged:** beats 8–16, both tables and both screenshot cards, the sources, and the takeaway.

Two items carried over from A still need you before recording:

- **Beat 12, "a third less error":** there is no confidence interval for Fable vs Sonnet or Haiku. Compute it; if it crosses zero, the line becomes "closer in my test".
- **Beat 16:** the Saturday topic is yours to confirm.
