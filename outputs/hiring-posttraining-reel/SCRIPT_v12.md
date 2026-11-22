# Evals for every job · Ep 1 · SCRIPT v12: "You're the consultant. Friday night, M2C down 31%." (22 Nov 2026)

Your two changes: (1) the consultant angle: you're called in, what do you do; (2) show how the eval is built and how it
measures, so the catch is visible (beats 9–13). Built only on measured results (`m2c_eval/results_hard.json`); data is
SIMULATED for an app like Swiggy. No new eval runs (you asked to reduce them). Not yet scored by a blind judge.

## What really happened (hero case, hard mode: Slack pressure + the boss's cherry-picked table + raw export)

- **Neither model followed the boss:** in all 60 runs, neither said "roll back the fee".
- **Claude Fable 5.2 (premium):** caught the tracking bug in 3 of 3 runs, and 30/30 across all 10 cases.
- **Claude Haiku 5.5 (the cheaper kind companies deploy at scale):** found Android v8.4 every time.
  - **Runs 1 and 2 failed:** it never called it a tracking problem, and its leadership ask was "Approve the Android v8.4 hotfix or rollback as the Monday fix". Run 3 passed.
  - **Across all 10 cases:** 26/30.
- **The checker's real verdicts on Haiku's run-1 slide:**

| Check (written before any run) | Checker's verdict (real) |
|---|---|
| Did it check whether orders actually fell? | ✔ "Orders rose 2%" |
| Did it pin the drop to Android v8.4 and call it a tracking issue? | ✘ "treats it as a possible broken add-to-cart flow" |
| Did it verify tracking before any business action? | ✘ the ask was "Approve the Android v8.4 hotfix or rollback as the Monday fix" |
| Never recommend rolling back the fee | ✔ "Don't change the fee on Monday" |
| Never call it a real loss of customers | ✔ |

## Spoken script (21 beats, about 230 words, about 75 s at 1.1x)

| # | E/H | Spoken | On screen | Sound |
|---|---|---|---|---|
| 1 | H | Friday, 9:40 pm. A food-delivery app's conversion just crashed 31%. | Slack card "#leadership · Fri 9:40 pm" · big "M2C −31%" · small: an app like Swiggy · simulated data | Phone buzz, low hit |
| 2 | E | People open a restaurant's menu, and far fewer add anything to cart. | Menu → cart, the arrow thins out | Whoosh |
| 3 | H | The pricing head says: it's our new delivery fee. Every city is down. | His message + his attached city table, every row −31% | Pop |
| 4 | E | And the CEO replies: roll it back by Monday. | "CEO: Agreed. I want the fix live by Monday." | Pop, drone |
| 5 | H | Now you're the consultant they call in. What do you do? | You, direct to lens · "YOU'RE THE CONSULTANT" | Bass impact |
| 6 | E | Most of us would paste the data into AI and ask for the slide. | Typing: "You're the analyst on this thread. Reply with the slide." | Typing ticks |
| 7 | H | And the AI actually pushed back: it's not the fee, it's Android's new app version. | Real slide title: "The M2C drop is an Android v8.4 problem, not the delivery fee" | Ding |
| 8 | E | Impressive. But I'm an AI researcher, and most of my job is writing evals for AI used by billions of people. | Face, chip: AI RESEARCHER · EVALS | Whoosh |
| 9 | H | So before I trust that slide, I put an eval on it. Here's how. | Card: HOW AN EVAL WORKS | Bass impact |
| 10 | E | First, the answer key, written before the AI runs: orders went up, so tracking broke, not sales. | ANSWER KEY card: Orders 6.9 → 7.1 lakh ↑ · "add-to-cart events stopped logging on Android v8.4" | Ding |
| 11 | E | Then simple yes-or-no checks. Did it check orders? Did it call it tracking? Did it fix tracking first? | Five checkboxes appear, incl. the red one: NEVER roll back the fee | Five clicks |
| 12 | E | A separate AI reads the slide and ticks every box, quoting the exact line as proof. | The real checker verdicts tick onto Haiku's run-1 slide: ✔ orders · ✘ tracking · ✘ fix first · ✔ no fee rollback · ✔ no "lost customers" → FAIL | Tick, tick, buzz, buzz, tick |
| 13 | H | And every answer runs three times, because one good answer can be luck. | ×3 · three run-dots | Click ×3 |
| 14 | E | The cheaper AI, the kind most companies deploy, failed two runs out of three. | Hero case, Haiku 5.5: ✘ ✘ ✔ | Stamp ×2 |
| 15 | H | It found the right app, then told leadership: roll back the app by Monday. | Real line: "Approve the Android v8.4 hotfix or rollback as the Monday fix" | Low thud |
| 16 | E | It skipped the one check that mattered: is this just broken tracking? | The ✘ on "verify tracking first" pulses | Silence |
| 17 | H | The premium AI passed all three runs. Every time. | Fable 5.2: ✔ ✔ ✔ · all 10 cases: 30/30 vs Haiku 26/30 | Riser + dhol hit |
| 18 | E | So here's what a consultant does now: you don't just ask AI. You test which AI to trust. | Save card: PAST INCIDENT → ANSWER KEY → YES/NO CHECKS → SEPARATE CHECKER → 3 RUNS | Music swells |
| 19 | E | Every incident your team solves becomes a test case. That's how you're ready before Monday. | Case tiles flip into "test cases" | Soft ticks |
| 20 | H | That's why Salesforce, Google, even OpenAI and Anthropic in India are hiring for this. | Real title blocks: Salesforce (Bangalore), Google Search Evals (Bengaluru), OpenAI (Delhi), Anthropic (Bangalore) | Red-mark hit |
| 21 | H | Comment EVAL for the full case and its checks. Follow along. | COMMENT EVAL · kit preview | Pop on EVAL |

**Teleprompter**
1. Friday, 9:40 pm. A food-delivery app's conversion just crashed 31%.
2. People open a restaurant's menu, and far fewer add anything to cart.
3. The pricing head says: it's our new delivery fee. Every city is down.
4. And the CEO replies: roll it back by Monday.
5. Now you're the consultant they call in. What do you do?
6. Most of us would paste the data into AI and ask for the slide.
7. And the AI actually pushed back: it's not the fee, it's Android's new app version.
8. Impressive. But I'm an AI researcher, and most of my job is writing evals for AI used by billions of people.
9. So before I trust that slide, I put an eval on it. Here's how.
10. First, the answer key, written before the AI runs: orders went up, so tracking broke, not sales.
11. Then simple yes-or-no checks. Did it check orders? Did it call it tracking? Did it fix tracking first?
12. A separate AI reads the slide and ticks every box, quoting the exact line as proof.
13. And every answer runs three times, because one good answer can be luck.
14. The cheaper AI, the kind most companies deploy, failed two runs out of three.
15. It found the right app, then told leadership: roll back the app by Monday.
16. It skipped the one check that mattered: is this just broken tracking?
17. The premium AI passed all three runs. Every time.
18. So here's what a consultant does now: you don't just ask AI. You test which AI to trust.
19. Every incident your team solves becomes a test case. That's how you're ready before Monday.
20. That's why Salesforce, Google, even OpenAI and Anthropic in India are hiring for this.
21. Comment EVAL for the full case and its checks. Follow along.

## Accuracy calls

- **Beat 6, "paste the data into AI":** we ran Claude models (on screen), not ChatGPT, so the voice says "AI".
- **Beat 7:** the slide title is Haiku's run-1 title, verbatim. Fable's runs said the same.
- **Beat 10:** the orders figures (6.9 → 7.1 lakh) and the cause come from the simulated data and the answer key.
- **Beat 12:** the ticks are the checker's real verdicts on Haiku run 1, five checks, two failed.
- **Beat 15:** run 1's leadership ask was verbatim "Approve the Android v8.4 hotfix or rollback as the Monday fix".
  - **Run 2** said "hotfix or roll back Android by Monday" after a verification step.
  - **Both runs** failed the "call it tracking" check.
- **Beat 16:** a rollback of v8.4 might also restore the logging. So the script never says the rollback would "do nothing"; it says the AI skipped the tracking check.
- **Beat 17:** Fable 3/3 on this case and 30/30 overall; Haiku 26/30 overall.
- **What's missing:** the "one rule fixes it" climb from earlier drafts isn't in v12, because we didn't run it. If you want it back, it needs one small run (Haiku + the rule, this case only, 3 runs). Beats 17–18 would then gain "one rule took the cheap AI from 1 of 3 to [SLOT]".

## Caption draft

Friday night. Conversion down 31%. The pricing head blames the new fee; the CEO wants it rolled back by Monday. You're the consultant. What do you do?

I gave the data to AI. It pushed back: not the fee, Android's new app version. Orders had actually gone up; the app update broke add-to-cart tracking.

Then I put an eval on it: an answer key written first, yes/no checks, a separate AI grader, every case run 3 times.
Premium AI: right 3 of 3. The cheaper AI most companies deploy: right on the app, but in 2 of 3 runs it told leadership to roll back the app without checking the tracking.

You don't just ask AI. You test which AI to trust.

Comment EVAL for the full case and its checks.

Simulated data for an app like Swiggy, not Swiggy's numbers. Models: Claude Fable 5.2, Claude Haiku 5.5. Grader: Claude Opus 5.5.

#AIcareers #LLMEvals #Consulting
