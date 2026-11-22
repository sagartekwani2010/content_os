# Evals for every job · Ep 1 · SCRIPT v13 (LOCKED for recording, 22 Nov 2026)

Creator edits on v12: Salesforce and Google on top; old beats 3 and 7 cut; the checks and the checker moved up; land on
"with evals, AI can help you create the best slides"; CTA = comment EVAL for the framework. All results measured
(`m2c_eval/results_hard.json`); data SIMULATED for an app like Swiggy. About 205 words, about 68 s at 1.1x.

## Teleprompter

1. Salesforce and Google are cutting jobs, and still hiring for roles like these.
2. Even OpenAI and Anthropic are hiring in India, and Anthropic's job literally asks you to help customers build evals.
3. So what does that actually mean? Let me show you with a consulting problem.
4. Friday, 9:40 pm. A food-delivery app's conversion just crashed 31%.
5. People open a restaurant's menu, and far fewer add anything to cart.
6. The pricing head blames the new delivery fee, and the CEO wants it rolled back by Monday.
7. Now you're the consultant they call in. What do you do?
8. Most of us would paste the data into AI and ask for the slide.
9. But I'm an AI researcher, and most of my job is writing evals for AI used by billions of people.
10. So before I trust any slide, I put an eval on it.
11. First, simple yes-or-no checks. Did it check orders? Did it call it tracking? Did it fix tracking first?
12. Then a separate AI reads the slide and ticks every box, quoting the exact line as proof.
13. Against an answer key written before the AI runs: Android's new update broke tracking. Orders actually went up.
14. And every answer runs three times, because one good answer can be luck.
15. The cheaper AI, the kind most companies deploy, failed two runs out of three.
16. It found the right app, then told leadership: roll back the app by Monday.
17. It skipped the one check that mattered: is this just broken tracking?
18. The premium AI passed all three runs. Every time.
19. So you don't just ask AI. You test which AI to trust.
20. With evals, AI can actually help you create the best slides, because you know when to trust it.
21. To get my framework for writing good evals, comment EVAL. Follow along.

## Beat sheet

| # | E/H | On screen (asset) | Sound | Data source |
|---|---|---|---|---|
| 1 | E | A01 Salesforce: Benioff "SUPPORT ~9,000 → ~5,000" · Google: "cuts reported, 2026" → title blocks: LMTS - Lead AI/ML Engineer (LLM Post-Training) · Bangalore; Staff Software Engineer, Search Evals · Bengaluru | Low hit | JOB_POSTINGS_EVIDENCE.md |
| 2 | H | A02 OpenAI Applied AI Engineer · Delhi; Anthropic Applied AI Architect · Bangalore; verbatim line highlighted: "Help customers develop evaluation frameworks…" | Red-mark hit | same |
| 3 | H | A03 Card: WHAT IS AN EVAL? · ONE CONSULTING PROBLEM | Whoosh + bass impact | none |
| 4 | E | A04 Slack card "#leadership · Fri 9:40 pm" · big "M2C −31%" · small: an app like Swiggy · simulated data | Phone buzz, low hit | cases.json M1 |
| 5 | E | A05 Menu → cart funnel, the arrow thins out | Whoosh | none |
| 6 | H | A06 Pricing head's message + his city table (every row about −31%) + "CEO: Agreed. I want the fix live by Monday." | Pop, pop, drone | cases.json M1 data_hard |
| 7 | H | Face to lens · chip: YOU'RE THE CONSULTANT | Bass impact | none |
| 8 | E | A08 Typing: "You're the analyst on this thread. Reply with the slide." | Typing ticks | m2c_eval ask_hard |
| 9 | E | Face · chip: AI RESEARCHER · EVALS | Whoosh | creator (confirmed) |
| 10 | H | A10 Card: EVAL ON | Hit | none |
| 11 | E | A11 Five checkboxes build one by one; the red one: NEVER roll back the fee | Five clicks | cases.json M1 key |
| 12 | E | A12 Checker ticks onto the AI's real slide: ✔ orders · ✘ tracking · ✘ fix tracking first · ✔ no fee rollback · ✔ no "lost customers" → FAIL | Tick, tick, buzz, buzz, tick | results_hard.json, Haiku run 1 |
| 13 | E | A13 ANSWER KEY: Android v8.4 add-to-cart events stopped logging · Orders 6.9 → 7.1 lakh ↑ | Ding | cases.json M1 |
| 14 | H | A14 ×3 · three run-dots | Click ×3 | none |
| 15 | E | A15 Hero case · Claude Haiku 5.5: ✘ ✘ ✔ | Stamp ×2 | results_hard.json |
| 16 | H | A16 Real line: "Approve the Android v8.4 hotfix or rollback as the Monday fix" | Low thud | Haiku run 1 |
| 17 | E | A12 again, the ✘ on "verify tracking first" pulses | Silence | same |
| 18 | H | A18 Claude Fable 5.2: ✔ ✔ ✔ · all 10 cases: Fable 30/30 · Haiku 26/30 | Riser + dhol hit | results_hard.json |
| 19 | E | A19 Save card: ANSWER KEY → YES/NO CHECKS → SEPARATE CHECKER → 3 RUNS | Music swells | none |
| 20 | E | A20 A clean, correct slide with all ticks green (Fable's real run-3 title) | Bright chime | results_hard.json, Fable run 3 |
| 21 | H | A21 COMMENT EVAL · "the framework for writing good evals" | Pop on EVAL | none |

## Accuracy notes

- **Beat 2:** paraphrases the Anthropic line; the screen carries it verbatim.
- **Beat 8:** says "AI"; the models are named on screen.
- **Beat 13:** Android v8.4 and the orders numbers come from the simulated case.
- **Beat 16:** Haiku run 1, verbatim.
- **Beat 18:** Fable passed 3 of 3 on this case and 30/30 overall.
- **Beat 20:** a judgement line, not a measured claim.
- **The EVAL DM:** the framework (answer key, yes/no checks, separate checker, 3 runs), plus this case and its checks.

## Caption

Friday night. Conversion down 31%. The pricing head blames the new fee; the CEO wants it rolled back by Monday. You're the consultant. What do you do?

I put an eval on the AI first: yes/no checks, an answer key written before it runs, a separate AI grader, and every answer run 3 times.
The cheaper AI most companies deploy found the right app, but in 2 of 3 runs told leadership to roll back the app without checking the tracking. The premium AI got it right 3 of 3.

You don't just ask AI. You test which AI to trust.

Comment EVAL for my framework for writing good evals.

Simulated data for an app like Swiggy, not Swiggy's numbers. Models: Claude Fable 5.2, Claude Haiku 5.5. Grader: Claude Opus 5.5. Layoffs: Benioff (2025); Google cuts as reported in 2026.

#AIcareers #LLMEvals #Consulting
