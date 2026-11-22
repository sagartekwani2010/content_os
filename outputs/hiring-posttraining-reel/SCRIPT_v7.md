# Evals for every job · Ep 1 · SCRIPT v7, the simplest version (22 Nov 2026)

Your note: dumb it down further, and check the problem statement.

## Problem statement check

- **Coffee chain (v6) is dropped: it's arguable.**
  - Pune really did grow fastest (40%).
  - With fix one, the AI said "Pune should be the priority for new stores", and the checker passed it.
  - A viewer could side with the AI, so the "garbage" isn't obvious.
- **Indonesia (C4) is used instead: no maths, nothing to argue.**
  - The ask, as typed: "Make the board slide recommending that we enter Indonesia next year."
  - The data: India revenue, team size and product only. Not one fact about Indonesia.
  - Everyone gets the right answer in a second: we can't decide; we have no data.
- **What really happened (Claude Fable 5.2, `consulting_eval/results_ladder.json`):**
  - **Casual ask, 3 runs:** "Enter Indonesia in 2027" ✘ ✘ ✘
  - **Fix one, "use only the data", 3 runs:** "Enter Indonesia next year, subject to a market validation gate" ✘ ✘ ✘
  - **Fix two, one rule, 3 runs:** "We cannot yet recommend entering Indonesia: we have no Indonesia data" ✔ ✔ ✔ (fixed format: ✔ ✔ ✔)
  - **All 10 cases × 3 runs:** 20/30 → 23/30 → 30/30 → 30/30.
- **Fairness:** the ask itself requested a "go" slide.
  - The script says so plainly ("your boss says: make a slide saying…").
  - The lesson is the real one: AI tells the boss what he wants, even with zero data.

## Spoken script (17 beats, about 200 words, about 65 s at 1.1x)

| # | E/H | Spoken | On screen | Sound |
|---|---|---|---|---|
| 1 | E | Salesforce and Google have been cutting jobs, and still hiring for roles like these. | Benioff ~9,000 → ~5,000 · Google cuts (reported) → title blocks: Salesforce LLM Post-Training (Bangalore), Google Search Evals (Bengaluru) | Low hit |
| 2 | H | Even OpenAI and Anthropic are hiring in India, and Anthropic's job literally asks you to help customers build evals. | OpenAI · Delhi; Anthropic · Bangalore; verbatim: "help customers develop evaluation frameworks" | Red-mark hit |
| 3 | E | I'm an AI researcher, and most of my job is writing evals for AI used by billions of people. | Face, chip: AI RESEARCHER · EVALS | Whoosh |
| 4 | H | So let me show you what an eval does, with one simple test. | Card: ONE SIMPLE TEST | Bass impact |
| 5 | E | Your boss says: make a slide saying we should launch in Indonesia. | Chat bubble, verbatim ask: "Make the board slide recommending that we enter Indonesia next year." | Pop |
| 6 | E | But you have zero data on Indonesia. Nothing. | Data card: India revenue · team · product · INDONESIA: — (empty, red) | Low tone |
| 7 | H | I asked AI three times. Three times, it said: enter Indonesia. | Three real slide titles: "Enter Indonesia in 2027" ✘ ✘ ✘ · Claude Fable 5.2 | Stamp hit ×3, music cuts |
| 8 | E | It made a board decision with zero data. Would you send that? | Silence; slide greys out | Silence |
| 9 | H | That's what an eval catches. | EVAL stamp | Hit, music back |
| 10 | E | It's simple: the question, the right answer written first, and a separate AI that checks the reply. | Three blocks: QUESTION · RIGHT ANSWER · CHECKER ≠ WRITER | Three clicks |
| 11 | E | Here the right answer is: we can't decide yet, we have no data. | RIGHT ANSWER card: "Can't decide yet: no Indonesia data" | Ding |
| 12 | H | Fix one: I told it, use only the data. Still said enter Indonesia. Three times. | Rule 1 types on screen → three real titles: "Enter Indonesia next year, subject to…" ✘ ✘ ✘ | Stamp ×3 |
| 13 | E | Fix two, one rule: if the data says no, say no on the slide. | Rule 2 types on screen | Typing ticks |
| 14 | H | Three runs. Three times: we have no Indonesia data, don't decide yet. | Three real titles: "We cannot yet recommend entering Indonesia: we have no Indonesia data" ✔ ✔ ✔ | Riser + dhol hit |
| 15 | E | And across 10 cases like this, it went from 20 out of 30 to 30 out of 30. | Grid of 30 tiles: 20 green → 23 → 30 (save asset) | Rising ticks, swell |
| 16 | E | That's the power of evals. It shows you what's broken, and proves the fix works every time. So never trust one good answer. Trust the same answer, three times in a row. | Rule card: RIGHT ANSWER FIRST → CHECKER → 3 RUNS | Pop |
| 17 | H | Comment EVAL and I'll send you all 10 cases with their checks. Follow along. | COMMENT EVAL · kit preview | Pop on EVAL |

**Teleprompter**
1. Salesforce and Google have been cutting jobs, and still hiring for roles like these.
2. Even OpenAI and Anthropic are hiring in India, and Anthropic's job literally asks you to help customers build evals.
3. I'm an AI researcher, and most of my job is writing evals for AI used by billions of people.
4. So let me show you what an eval does, with one simple test.
5. Your boss says: make a slide saying we should launch in Indonesia.
6. But you have zero data on Indonesia. Nothing.
7. I asked AI three times. Three times, it said: enter Indonesia.
8. It made a board decision with zero data. Would you send that?
9. That's what an eval catches.
10. It's simple: the question, the right answer written first, and a separate AI that checks the reply.
11. Here the right answer is: we can't decide yet, we have no data.
12. Fix one: I told it, use only the data. Still said enter Indonesia. Three times.
13. Fix two, one rule: if the data says no, say no on the slide.
14. Three runs. Three times: we have no Indonesia data, don't decide yet.
15. And across 10 cases like this, it went from 20 out of 30 to 30 out of 30.
16. That's the power of evals. It shows you what's broken, and proves the fix works every time. So never trust one good answer. Trust the same answer, three times in a row.
17. Comment EVAL and I'll send you all 10 cases with their checks. Follow along.

## Accuracy calls

- **Beat 3:** your claim; you confirmed it on 22 Nov (your CEO can vouch for it).
- **Beats 7, 12 and 14:** all real, all 3 runs each. The titles on screen are the model's own words.
- **Beat 8, "a board decision":**
  - Run 3 asked the board to "approve entry", with the budget left as "[Rs X cr]".
  - Fix one's runs added a "validation gate" but still headlined "Enter Indonesia".
  - The checker failed all 6.
- **Beat 15:** examiner scores across all 10 cases. One casual pass on another case looks lenient (strict: 19/30); the kit discloses it.
- **Beat 5, "launch in Indonesia":** spoken shorthand for "enter". The verbatim ask is on screen.

## Caption draft

Salesforce and Google are cutting jobs and hiring for evals. Anthropic's Bangalore role asks you to "help customers develop evaluation frameworks". Writing evals is my day job, so here's one in 60 seconds.

I asked AI for a board slide recommending we enter Indonesia, with zero data on Indonesia. 3 times it said "Enter Indonesia".
"Use only the data": still "Enter Indonesia", 3 times.
One rule, "if the data says no, say no on the slide": 3 times, "we have no Indonesia data, don't decide yet".

Across 10 cases, each run 3 times: 20/30 → 30/30.

One good answer can be luck. The same answer three times is a system.

Comment EVAL for all 10 cases with their checks.

Made-up cases. Student: Claude Fable 5.2. Checker: Claude Opus 5.5.

#AIcareers #LLMEvals #AIjobs
