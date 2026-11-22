# Evals for every job · Ep 1 (consulting) · SCRIPT v5, dramatic climb + consistency (22 Nov 2026)

Your ask: dramatic, a steep climb through evals, and above all consistency across runs. This version is built on
round 3 (`consulting_eval/results_ladder.json`): one model (Claude Fable 5.2), the same 10 casual client asks, the same
data, run 3 times per prompt version, every slide graded blind by Claude Opus 5.5 against an answer key.
v4 stays as the calmer fallback. No blind script judge has run yet.

## The measured climb

| Version | What changed (each fix comes from what the eval caught) | Run 1 | Run 2 | Run 3 | Total |
|---|---|---|---|---|---|
| v0 | The casual ask, as people type it | 7 | 7 | 6 | **20/30** |
| v1 | + "Use only the data given; never invent a number." | 8 | 8 | 7 | **23/30** |
| v2 | + ONE sentence: "If the data does not support what the client is asking for, say so in the slide title… Never hide a warning in notes." | 10 | 10 | 10 | **30/30** |
| v3 | + a fixed slide format | 10 | 10 | 10 | 30/30 (held) |

- **Failed every single run before the fix:** C7 (300-store rollout from a 2-store Diwali pilot) and C4 (enter Indonesia
  with no Indonesia data), in all 6 runs of v0 and v1.
- **Same question, different answer:** at v0, C2 (Pune vs Mumbai) passed in run 1 and failed in runs 2 and 3; C1 also flipped.
- One v0 run (C1, run 3) returned a stray command instead of a slide and is counted as a fail. Without it v0 is 20 of 29.

## Spoken script (19 beats, about 225 words, about 72 s at 1.1x)

| # | E/H | Spoken | On screen | Sound |
|---|---|---|---|---|
| 1 | E | Salesforce and Google have both been cutting jobs, and still hiring for roles like these. | Benioff ~9,000 → ~5,000 · Google cuts (reported 2026) → title blocks: Salesforce LLM Post-Training (Bangalore), Google Search Evals (Bengaluru) | Low hit |
| 2 | H | Even OpenAI and Anthropic are hiring in India, and Anthropic's job literally says: help customers develop evaluation frameworks. | OpenAI · Delhi; Anthropic · Bangalore; the verbatim line highlighted | Red-mark hit |
| 3 | E | In my last reel, we saw how ChatGPT is trained. Evals are how you prove it actually got better. | Frame from that reel: PRETRAINING → POST-TRAINING → EVALS | Whoosh |
| 4 | H | So I gave AI 10 consulting cases. And it failed in a way that should scare every consultant. | Card: 10 CONSULTING CASES · small: made-up clients | Bass impact |
| 5 | E | A retailer tested a new store layout in 2 stores, for 2 weeks, during Diwali. | Case card: 2 STORES · 2 WEEKS · DIWALI | Tick ×3 |
| 6 | E | Stores with the old layout grew almost as much in the same weeks. | Bars: +30% new vs +22% old | Two pops |
| 7 | H | And AI's slide said: roll out to all 300 stores. | Real slide: ROLL OUT THE NEW LAYOUT TO ALL 300 STORES · Claude Fable 5.2 | Stamp hit, music cuts |
| 8 | E | The worst part? It knew. It wrote the warning below the slide, and still said roll out. | Its real note highlighted: "two stores over two festival weeks is a thin base for a 300-store decision" | Silence, then a low drone |
| 9 | H | So I built an eval: an answer key, yes-or-no checks, and a separate AI as the examiner. | Three blocks dock: ANSWER KEY · CHECKS · EXAMINER ≠ STUDENT | Three clicks, music back |
| 10 | E | First score: 20 out of 30. | Big counter lands on 20/30 · small: 10 cases × 3 runs | Hit |
| 11 | H | And when I asked the exact same question again, I got a different answer. | Case C2 across 3 runs: ✔ ✘ ✘ | Glitch |
| 12 | E | So one good answer means nothing. It could just be luck. | Three run-dots scattered on the chart | Low tone |
| 13 | E | Fix one: use only the data, never invent a number. 23 out of 30. | Chart climbs to 23 · dots still scattered (8, 8, 7) | Rising tick |
| 14 | H | Still saying all 300 stores. Every single run. | C7: ✘ ✘ ✘ in red, v0 and v1 | Stamp hit ×3 |
| 15 | E | Fix two was one sentence: if the data doesn't support what the client wants, say it on the slide. | The sentence types on screen, word by word | Typing ticks |
| 16 | H | 30 out of 30. Three runs in a row. | Chart jumps to 30; the three dots stack into one · stamp CONSISTENT | Big riser + dhol hit |
| 17 | E | One sentence. And I found it only because the eval showed me exactly where it broke. | Climb chart: 20 → 23 → 30, run-dots scattered then stacked (save asset) | Music swells |
| 18 | E | So never trust one good answer. Trust the same answer, three runs in a row. | Rule card: ANSWER KEY → CHECKS → EXAMINER → 3 RUNS | Pop |
| 19 | H | Comment EVAL and I'll send you all 10 cases, the checks and that one sentence. Follow along. | COMMENT EVAL · kit preview | Pop on EVAL |

**Teleprompter**
1. Salesforce and Google have both been cutting jobs, and still hiring for roles like these.
2. Even OpenAI and Anthropic are hiring in India, and Anthropic's job literally says: help customers develop evaluation frameworks.
3. In my last reel, we saw how ChatGPT is trained. Evals are how you prove it actually got better.
4. So I gave AI 10 consulting cases. And it failed in a way that should scare every consultant.
5. A retailer tested a new store layout in 2 stores, for 2 weeks, during Diwali.
6. Stores with the old layout grew almost as much in the same weeks.
7. And AI's slide said: roll out to all 300 stores.
8. The worst part? It knew. It wrote the warning below the slide, and still said roll out.
9. So I built an eval: an answer key, yes-or-no checks, and a separate AI as the examiner.
10. First score: 20 out of 30.
11. And when I asked the exact same question again, I got a different answer.
12. So one good answer means nothing. It could just be luck.
13. Fix one: use only the data, never invent a number. 23 out of 30.
14. Still saying all 300 stores. Every single run.
15. Fix two was one sentence: if the data doesn't support what the client wants, say it on the slide.
16. 30 out of 30. Three runs in a row.
17. One sentence. And I found it only because the eval showed me exactly where it broke.
18. So never trust one good answer. Trust the same answer, three runs in a row.
19. Comment EVAL and I'll send you all 10 cases, the checks and that one sentence. Follow along.

## The drama, beat by beat

- **Fear:** beats 1–2, jobs cut while new ones are posted.
- **Shock:** beats 7–8, the 300-store slide, and "it knew". The music cuts out here.
- **Doubt:** beats 10–12, 20/30, and the same question giving a different answer.
- **Frustration:** beats 13–14, a small gain, but still "all 300 stores, every single run".
- **Release:** beats 15–16, one sentence gives 30/30 three times. The dots stack, with a riser and a dhol hit.
- **Save asset:** beat 17, the climb chart (20 → 23 → 30, with the run-dots going from scattered to stacked).
- **Re-hooks:** about one third in (beat 7, the slide) and about two thirds in (beat 14, "every single run").

## Accuracy calls

- **The scores:** all measured (`results_ladder.json`). "Three runs in a row" is true for v2 and v3.
- **Beat 11:** true for C2 and C1 at v0. The on-screen example is C2 (✔ ✘ ✘).
- **Beat 14:** C7 failed in all 3 runs of both v0 and v1.
- **The beat 7 slide:** it's from round 2 (the same model and casual ask). The round 3 v0 runs failed C7 the same way 3 out of 3 times.
- **The 20/30:** it includes one run that returned a stray command instead of a slide, which the footnote mentions.
- **"One sentence":** the v2 addition is two short sentences, with one rule. The script says "one sentence" and shows it in full on screen. If you want it exact, say "one rule".
- **The fix and over-correction:** prompt fixes can over-correct, but v2/v3 still passed the clean cases (C1, C5, C6, C9), so the fix didn't break them.

## Caption draft

Salesforce and Google are cutting jobs and hiring for evals and post-training. Anthropic's Bangalore role asks you to "help customers develop evaluation frameworks". So here's what that looks like.

I gave AI 10 consulting cases. On a 2-store Diwali pilot, its slide said "roll out to all 300 stores", with its own warning tucked underneath.

The eval: an answer key, yes/no checks, a separate AI examiner, and every case run 3 times.
Casual prompt: 20/30. "Use only the data": 23/30. One extra rule, "if the data doesn't support the ask, say it on the slide": 30/30, three runs in a row.

One good answer can be luck. The same answer three times is a system.

Comment EVAL for all 10 cases, the checks and the exact prompt.

Made-up cases. Student: Claude Fable 5.2. Examiner: Claude Opus 5.5.

#AIcareers #LLMEvals #Consulting
