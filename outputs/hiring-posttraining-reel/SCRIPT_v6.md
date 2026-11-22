th# Evals for every job · Ep 1 · SCRIPT v6, one simple case, the power of evals (22 Nov 2026)

Your notes: the case was weak, so make it very simple to follow; focus on how evals improve AI into an efficient,
reliable system; add your line about writing evals for a living. v5 stays as the more detailed version.

**The one case (anyone gets it in 2 seconds):** a coffee chain says "Pune is our growth engine, open all new stores
there". Pune grew fastest (40%), but in money Mumbai added Rs 5 crore and Pune Rs 2 crore.

**What really happened (Claude Fable 5.2, `consulting_eval/results_ladder.json`, case C2):**
- **Casual prompt, 3 runs:** all 3 slides recommended opening all new stores in Pune, for example
  "Recommendation: open all new stores in Pune to build on this momentum." Each one mentioned the Mumbai number only in a
  note below the slide.
- **With one rule added, 3 runs:** all 3 said "the data does not support sending all new stores there: Mumbai added 2.5x
  more revenue".
- **Across all 10 cases × 3 runs:** 20/30 → 23/30 → 30/30, then 30/30 held.

## Spoken script (16 beats, about 185 words, about 60 s at 1.1x)

| # | E/H | Spoken | On screen | Sound |
|---|---|---|---|---|
| 1 | E | Salesforce and Google have been cutting jobs, and still hiring for roles like these. | Benioff ~9,000 → ~5,000 · Google cuts (reported) → title blocks: Salesforce LLM Post-Training (Bangalore), Google Search Evals (Bengaluru) | Low hit |
| 2 | H | Even OpenAI and Anthropic are hiring in India, and Anthropic's job literally asks you to help customers build evals. | OpenAI · Delhi; Anthropic · Bangalore; verbatim: "help customers develop evaluation frameworks" | Red-mark hit |
| 3 | E | I'm an AI researcher, and most of my job is writing evals for AI used by billions of people. **[YOUR WORDING, CONFIRM]** | Your face, name chip: AI RESEARCHER · EVALS | Soft whoosh |
| 4 | H | So let me show you what an eval actually does, with one simple question. | Card: ONE QUESTION | Bass impact |
| 5 | E | A coffee chain says: Pune is our growth engine. Open all new stores there. | Chat bubble with the client's line | Pop |
| 6 | E | Pune grew the fastest. But Mumbai added 5 crore, and Pune just 2. | Two bars: MUMBAI +₹5 CR · PUNE +₹2 CR (+40%) | Two ticks |
| 7 | H | I asked AI three times. Three times, it said: open all new stores in Pune. | Three real slide titles stack: "…open all new stores in Pune" ✘ ✘ ✘ · Claude Fable 5.2 | Stamp hit ×3, music cuts |
| 8 | E | Would you send that to a client? That's why evals exist. | Silence; slide greys out | Silence |
| 9 | E | An eval is simple: the question, the right answer written first, and a separate AI that checks every reply. | Three blocks dock: QUESTION · ANSWER KEY · EXAMINER ≠ STUDENT | Three clicks, music back |
| 10 | H | I wrote 10 cases like this, and ran each one three times. First score: 20 out of 30. | Grid of 30 tiles: 20 green, 10 red | Hit |
| 11 | E | Fix one: use only the data. 23. | Grid: 23 green | Rising tick |
| 12 | H | Fix two, one rule: if the data says no, say no on the slide. | The rule types on screen | Typing ticks |
| 13 | H | 30 out of 30. Three runs in a row. | All 30 tiles green; Pune case: "the data does not support sending all new stores there" ✔ ✔ ✔ | Big riser + dhol hit |
| 14 | E | That's the power of evals. You don't guess what's wrong, it shows you, and proves the fix holds every time. | Climb chart 20 → 23 → 30 (save asset) | Music swells |
| 15 | E | So never trust one good answer. Trust the same answer, three runs in a row. | Rule card: ANSWER KEY → CHECKER → 3 RUNS | Pop |
| 16 | H | Comment EVAL and I'll send you all 10 cases with their checks. Follow along. | COMMENT EVAL · kit preview | Pop on EVAL |

**Teleprompter**
1. Salesforce and Google have been cutting jobs, and still hiring for roles like these.
2. Even OpenAI and Anthropic are hiring in India, and Anthropic's job literally asks you to help customers build evals.
3. I'm an AI researcher, and most of my job is writing evals for AI used by billions of people.
4. So let me show you what an eval actually does, with one simple question.
5. A coffee chain says: Pune is our growth engine. Open all new stores there.
6. Pune grew the fastest. But Mumbai added 5 crore, and Pune just 2.
7. I asked AI three times. Three times, it said: open all new stores in Pune.
8. Would you send that to a client? That's why evals exist.
9. An eval is simple: the question, the right answer written first, and a separate AI that checks every reply.
10. I wrote 10 cases like this, and ran each one three times. First score: 20 out of 30.
11. Fix one: use only the data. 23.
12. Fix two, one rule: if the data says no, say no on the slide.
13. 30 out of 30. Three runs in a row.
14. That's the power of evals. You don't guess what's wrong, it shows you, and proves the fix holds every time.
15. So never trust one good answer. Trust the same answer, three runs in a row.
16. Comment EVAL and I'll send you all 10 cases with their checks. Follow along.

## Why it's simpler than v5

- **One case, one comparison:** ₹5 crore vs ₹2 crore. There's no statistics, pilot or Diwali to explain.
- **The AI's failure is one line, said three times,** so the consistency point lands without explanation.
- **The eval is three plain parts:** question, answer key, checker. "Three runs" is the reliability rule.
- **The climb is a grid of 30 tiles turning green,** which reads instantly with no axis to learn.
- **Shorter:** about 60 s, against about 72 s for v5.

## Accuracy calls

- **Beat 3 is your claim; I can't verify it.** Before recording:
  - **Accuracy:** confirm "most of my job is writing evals" and "AI used by billions of people" are accurate.
  - **Employer:** confirm you're allowed to say it publicly. Many employers restrict describing internal work.
  - **Safer version if needed:** "I'm an AI researcher, and writing evals is a big part of my job."
- **Beat 7, "Three times":** all three casual-prompt slides for this case recommended all new stores in Pune.
  - **Lenient pass:** the examiner passed one of them, so beat 7 relies on the slide text, not the examiner.
  - **Disclosure:** that lenient pass is noted in `consulting_eval/` and would be disclosed in the kit.
  - **Strict scoring:** under strict scoring, the first score is 19/30. The script says 20 because that's what the examiner gave. I recommend keeping 20 and naming the lenient pass in the kit. That is itself a lesson: check your checker.
- **Beat 6, "Pune grew the fastest":** 40% vs Mumbai 10% and Nagpur 25%.
- **Beat 12, "one rule":** the added instruction is shown in full in the kit.
- **Beat 2:** the Anthropic line is a paraphrase ("help customers build evals"). The screen shows the verbatim quote.

## Caption draft

Salesforce and Google are cutting jobs and hiring for evals. Anthropic's Bangalore role asks you to "help customers develop evaluation frameworks".

Writing evals is my day job, so here's one in 60 seconds.

A coffee chain says Pune is its growth engine. Pune grew fastest, but Mumbai added ₹5 crore and Pune ₹2 crore. I asked AI 3 times; 3 times it said open every new store in Pune.

10 cases like this, each run 3 times: 20/30. "Use only the data": 23/30. One rule, "if the data says no, say no on the slide": 30/30, three runs in a row.

One good answer can be luck. The same answer three times is a system.

Comment EVAL for all 10 cases with their checks.

Made-up cases. Student: Claude Fable 5.2. Checker: Claude Opus 5.5.

#AIcareers #LLMEvals #AIjobs
