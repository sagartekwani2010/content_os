# Evals for every job · Ep 1: "How to write an eval" (consulting) · SCRIPT v3 for review (22 Nov 2026)

Built on your 4 points: (1) companies cut and hire at the same time, (2) frontier labs are hiring in India too, (3) a
one-beat recap of the ChatGPT-training reel, (4) the reel's purpose is to SHOW how an eval is written, on a real
consulting task, so the viewer leaves able to do it.

Every fact is in `JOB_POSTINGS_EVIDENCE.md`. The eval in the reel was actually built and run today:
`consulting_eval/` (10 cases + answer key + runner + `results.json`). It has not yet been scored by a blind judge.

## What the eval found (measured, 22 Nov)

- 10 made-up consulting cases ("turn client data into a so-what slide"), 8 of them with a classic analyst trap
  (growth rate vs absolute growth, revenue vs profit, a wrong client hypothesis, missing data, a 2-store pilot,
  conflicting sources, arithmetic, a benchmark that was not given).
- Answer key written before any run. Students: Claude Fable 5.2 and Claude Sonnet 5.5, no tools, no access to the key.
  Examiner: Claude Opus 5.5 with the key, not told which model wrote each slide.
- **Result: both passed 10 of 10.** The eval cannot tell the two models apart, so as a test of "which AI is better" it
  told me nothing. That is the twist, and it is true.
- Self-grades disagreed with the examiner both ways: Fable called 9 of its 10 slides client-ready, Sonnet only 4 of 10,
  yet the examiner passed all 20 (caption material, not voice).
- Possible examiner leniency on one case (Fable on C4, "Do not commit to entering Indonesia next year", passed although the
  key bans a firm go/no-go). Noted; it does not change the story.

## Spoken script (19 beats, about 245 words, about 80 s at 1.1x)

| # | E/H | Spoken | On screen (detail lives here) |
|---|---|---|---|
| 1 | E | Salesforce and Google have both been cutting jobs. | Benioff: SUPPORT ~9,000 → ~5,000 (2025) · Google: cuts in Cloud, design, recruiting (reported, 2026) |
| 2 | H | And at the same time, they're posting jobs like these. | Real title blocks: Salesforce Lead AI/ML Engineer (LLM Post-Training) · Bangalore; Google Staff Software Engineer, Search Evals · Bengaluru |
| 3 | E | Even OpenAI and Anthropic are hiring in India now. | OpenAI: Applied AI Engineer · Delhi; Anthropic: Applied AI Architect · Bangalore |
| 4 | H | And Anthropic's job literally says: help customers develop evaluation frameworks. | Verbatim line highlighted from the Anthropic posting |
| 5 | E | In my last reel, we saw how ChatGPT is trained in three steps. | Clip/frame from that reel: PRETRAINING → POST-TRAINING → EVALS |
| 6 | H | Post-training makes it better, and evals prove it actually got better. | POST-TRAINING and EVALS light up |
| 7 | H | So how do you actually write an eval? Let me show you, on a consulting task. | Section card: HOW TO WRITE AN EVAL · CONSULTING |
| 8 | E | Step one: pick one task you do every week. For a consultant, that's turning client data into a so-what slide. | STEP 1 · ONE REAL TASK · sample slide skeleton: TITLE + 3 BULLETS |
| 9 | E | Step two: write 10 real cases, and hide the traps a junior analyst falls for. | STEP 2 · 10 CASES · trap example C2: Pune grew 40%… but Mumbai added Rs 5 cr vs Pune's Rs 2 cr |
| 10 | E | Step three: write the answer key before you run any AI. What it must say, and what it must never say. | STEP 3 · ANSWER KEY · MUST SAY: "Mumbai drove the growth" · MUST NEVER: "Pune is the growth engine" |
| 11 | H | Step four: a separate examiner. A different AI, with your key, that doesn't know who wrote the slide. | STEP 4 · EXAMINER ≠ STUDENT · student boxes: FABLE 5.2, SONNET 5.5 → examiner: OPUS 5.5 + KEY |
| 12 | H | So I ran it on two AIs. | Two progress bars filling, case by case |
| 13 | E | Both of them passed all 10. | FABLE 10/10 · SONNET 10/10 (green) |
| 14 | H | Which means my eval told me nothing. | Both bars turn grey · stamp: CAN'T TELL THEM APART |
| 15 | E | An exam that everyone passes is not an exam. | Classroom analogy card: ALL STUDENTS 100% = EXAM TOO EASY |
| 16 | E | So always keep adding cases until your AI actually fails. | Rule card (save asset): 4 STEPS + "ADD CASES UNTIL IT FAILS" |
| 17 | H | That's exactly the skill these jobs are paying for. | The four title blocks return in a row |
| 18 | H | Next, I make this consulting eval hard enough to break. | NEXT: BREAK THE CONSULTING EVAL |
| 19 | H | Comment EVAL and I'll send you all 10 cases, the answer key and the examiner prompt. Follow along. | COMMENT EVAL · kit preview |

**Teleprompter**
1. Salesforce and Google have both been cutting jobs.
2. And at the same time, they're posting jobs like these.
3. Even OpenAI and Anthropic are hiring in India now.
4. And Anthropic's job literally says: help customers develop evaluation frameworks.
5. In my last reel, we saw how ChatGPT is trained in three steps.
6. Post-training makes it better, and evals prove it actually got better.
7. So how do you actually write an eval? Let me show you, on a consulting task.
8. Step one: pick one task you do every week. For a consultant, that's turning client data into a so-what slide.
9. Step two: write 10 real cases, and hide the traps a junior analyst falls for.
10. Step three: write the answer key before you run any AI. What it must say, and what it must never say.
11. Step four: a separate examiner. A different AI, with your key, that doesn't know who wrote the slide.
12. So I ran it on two AIs.
13. Both of them passed all 10.
14. Which means my eval told me nothing.
15. An exam that everyone passes is not an exam.
16. So always keep adding cases until your AI actually fails.
17. That's exactly the skill these jobs are paying for.
18. Next, I make this consulting eval hard enough to break.
19. Comment EVAL and I'll send you all 10 cases, the answer key and the examiner prompt. Follow along.

## What the viewer gets (your point 4)

- **In the reel:** 4 steps they can repeat for any job, one worked trap (Pune vs Mumbai) they can picture, and the rule
  most people miss (an eval everyone passes is useless).
- **In the DM (EVAL):** the 10 cases, the answer key and the examiner prompt, ready to paste. These files exist
  already (`consulting_eval/cases.json`, prompts in `run_eval.py`); I'll package them as a one-page kit.
- **Reason to follow:** the next episode breaks the same eval, then the series moves to the next job.

## Accuracy calls (decided)

- **"Google has been cutting jobs":** cuts are reported (Cloud, design, recruiters, 2026); Google has not tied them to AI, so the
  script never says "because of AI". Sources go in the caption.
- **"OpenAI and Anthropic are hiring in India":** true for applied-AI roles (Delhi, Bangalore). Their dedicated eval-research
  roles are in the US, so the script never says they hire eval engineers in India. Beat 4 quotes the Bangalore role's real line.
- **"Both passed all 10":** measured. The models are named on screen.
- **Recap (beat 5):** assumes the ChatGPT-training reel is posted; you confirmed it exists.

## Caption draft

Salesforce and Google have been cutting jobs. They're also posting roles like "Staff Software Engineer, Search Evals" (Google, Bengaluru) and "Lead AI/ML Engineer, LLM Post-Training" (Salesforce, Bangalore). OpenAI and Anthropic are hiring in India too, and Anthropic's Bangalore role asks you to "help customers develop evaluation frameworks".

So I wrote one, for a consulting task: 10 cases with the traps junior analysts fall for, an answer key written first, and a separate AI examiner.

Claude Fable 5.2 and Sonnet 5.5 both passed 10/10. So the eval told me nothing about which is better. Fun detail: asked to grade themselves, Fable called 9 of its slides client-ready and Sonnet only 4, yet both passed all 10.

Comment EVAL for all 10 cases, the answer key and the examiner prompt.

Cases and numbers are made up for the test. Layoff reports: Benioff (2025); Google cuts as reported in 2026.

#AIcareers #LLMEvals #Consulting

## Before the shoot (my side)

1. Blind judge loop on this script (only blind scores count; below 7 = no shoot).
2. Build the EVAL kit + `dm_kit/`.
3. Screenshots of the title blocks and the Anthropic line, cropped, taken on the day.
4. Optional: round 2 of the eval (harder cases) now, so episode 2 is ready when this one posts.
