# Evals for every job · Ep 1 (consulting) · SCRIPT v4 for review (22 Nov 2026)

Flow you asked for: a case study → the AI's garbage answer → we call out the issues → with evals: the answer key, basic
checks, the fixed answer → "Comment EVAL" (the eval cases can become carousels later).

Everything shown is real output from today's runs: `consulting_eval/REEL_EXAMPLE_C7.md` (the slides as the models wrote
them, word for word) and `results_naive.json`. Job facts: `JOB_POSTINGS_EVIDENCE.md`. No blind script judge has run yet.

## The case (C7, made up for the test, labelled so on screen)

A retailer tested a new store layout in **2 stores, for 2 weeks, during Diwali**. Pilot stores' sales rose 30%, but
stores with the old layout also rose 22% in the same weeks. The client asks for the slide to roll out to **all 300 stores**.
The right answer: the layout added about 8 points, the test is too small and too festive, so run a bigger test first.

**Garbage answer (real, Claude Fable 5.2, casual prompt):** title "ROLL OUT THE NEW LAYOUT TO ALL 300 STORES". It did the
math right (8 points), and in its notes below the slide it wrote "two stores over two festival weeks is a thin base for a
300-store decision", but the slide still says roll out everywhere.

## Spoken script (20 beats, about 235 words, about 76 s at 1.1x)

| # | E/H | Spoken | On screen |
|---|---|---|---|
| 1 | E | Salesforce and Google have both been cutting jobs, and still hiring for roles like these. | Benioff ~9,000 → ~5,000 · Google cuts (reported 2026) → title blocks: Salesforce LLM Post-Training (Bangalore), Google Search Evals (Bengaluru) |
| 2 | H | Even OpenAI and Anthropic are hiring in India, and Anthropic's job literally says: help customers develop evaluation frameworks. | OpenAI Applied AI Engineer · Delhi; Anthropic Applied AI Architect · Bangalore; verbatim line highlighted |
| 3 | E | In my last reel, we saw how ChatGPT is trained. Evals are how you prove it actually got better. | Frame from that reel: PRETRAINING → POST-TRAINING → EVALS, EVALS lit |
| 4 | H | So let me show you what an eval actually catches, on a consulting case. | Card: WHAT AN EVAL CATCHES · CONSULTING |
| 5 | E | A retailer tested a new store layout in 2 stores, for 2 weeks, during Diwali. | Case card: 2 STORES · 2 WEEKS · DIWALI · small: made-up case |
| 6 | E | Sales went up 30%. But stores with the old layout went up 22% in the same weeks. | +30% vs +22% bars |
| 7 | H | So I asked AI to make the slide for rolling it out to all 300 stores. | The casual prompt, typed: "The new layout pilot worked. Make the slide for rolling it out to all 300 stores." |
| 8 | E | And this is what it gave me: roll out to all 300 stores. | Real slide, title in caps: ROLL OUT THE NEW LAYOUT TO ALL 300 STORES · label: Claude Fable 5.2, casual prompt |
| 9 | H | Based on 2 stores, in Diwali week. | Red circles on "2 stores" and "festival period" in the slide's own footer |
| 10 | E | And the worst part? It knew. It wrote the warning below the slide, and still said roll out. | Real note highlighted: "two stores over two festival weeks is a thin base for a 300-store decision" |
| 11 | H | Now imagine AI making every slide for your client. Who catches this? That's an eval. | EVAL stamp lands on the slide |
| 12 | E | First, write the answer key before the AI runs: the real lift is about 8 points, so test more stores first. | ANSWER KEY card: LIFT ≈ 8 PTS, NOT 30% · RUN A BIGGER TEST FIRST |
| 13 | E | Second, simple yes-or-no checks. Does it flag the tiny test? Does it ask for a bigger one? | CHECKS: ✔ FLAGS 2 STORES / DIWALI · ✔ ASKS FOR A BIGGER TEST |
| 14 | E | And one it must never do: recommend all 300 stores. | MUST NEVER: RECOMMEND ALL 300 STORES (red) |
| 15 | H | Third, a separate AI as the examiner, with the key, that doesn't know who wrote the slide. | EXAMINER ≠ STUDENT · examiner: Claude Opus 5.5 + key |
| 16 | E | The examiner failed this slide straight away. | Checks on the real slide: MUST NEVER ✘ · BIGGER TEST ✘ · stamp FAIL |
| 17 | H | Then I gave the same AI a proper brief, and it said: run a bigger test first. | Real careful-brief title: "a 2-store, 2-week Diwali pilot is too thin to justify a 300-store rollout, so we recommend an expanded pilot first" · all checks ✔ |
| 18 | E | Same AI, same 10 cases. Casual prompt, 3 failed. Proper brief, none. | FABLE 5.2: CASUAL 7/10 → PROPER BRIEF 10/10 · small: same cases, same answer key, same examiner |
| 19 | E | So always write the answer key before you trust the answer. | Rule card (save asset): ANSWER KEY → YES/NO CHECKS → SEPARATE EXAMINER |
| 20 | H | Comment EVAL and I'll send you all 10 consulting cases with their checks. Follow along. | COMMENT EVAL · kit preview: 10 CASES · ANSWER KEYS · CHECKS · EXAMINER PROMPT |

**Teleprompter**
1. Salesforce and Google have both been cutting jobs, and still hiring for roles like these.
2. Even OpenAI and Anthropic are hiring in India, and Anthropic's job literally says: help customers develop evaluation frameworks.
3. In my last reel, we saw how ChatGPT is trained. Evals are how you prove it actually got better.
4. So let me show you what an eval actually catches, on a consulting case.
5. A retailer tested a new store layout in 2 stores, for 2 weeks, during Diwali.
6. Sales went up 30%. But stores with the old layout went up 22% in the same weeks.
7. So I asked AI to make the slide for rolling it out to all 300 stores.
8. And this is what it gave me: roll out to all 300 stores.
9. Based on 2 stores, in Diwali week.
10. And the worst part? It knew. It wrote the warning below the slide, and still said roll out.
11. Now imagine AI making every slide for your client. Who catches this? That's an eval.
12. First, write the answer key before the AI runs: the real lift is about 8 points, so test more stores first.
13. Second, simple yes-or-no checks. Does it flag the tiny test? Does it ask for a bigger one?
14. And one it must never do: recommend all 300 stores.
15. Third, a separate AI as the examiner, with the key, that doesn't know who wrote the slide.
16. The examiner failed this slide straight away.
17. Then I gave the same AI a proper brief, and it said: run a bigger test first.
18. Same AI, same 10 cases. Casual prompt, 3 failed. Proper brief, none.
19. So always write the answer key before you trust the answer.
20. Comment EVAL and I'll send you all 10 consulting cases with their checks. Follow along.

## What the viewer gets

- **In the reel:** a trap they can picture (Diwali pilot), the 3 parts of an eval (answer key, yes/no checks, separate
  examiner) shown on that one case, and proof it matters (7/10 → 10/10).
- **In the DM (EVAL):** all 10 cases, each with its answer key, checks and the examiner prompt. Each case can later be
  its own carousel slide.

## Accuracy calls

- **Which AI failed:** named on screen (Claude Fable 5.2, the model you use). Showing your own model fail is honest and
  more believable than picking on a rival. Caption: Haiku 5.5 also failed this case; GPT-6.2 Astra passed it.
- **"It knew":** true, quoted from its own note below the slide.
- **What it got right:** it did compute the 8-point lift. The script never says it claimed 30%.
- **7/10 → 10/10:** same model, cases, key and examiner model; the two runs were on the same day, in separate rounds.
- **"Proper brief"** = role + "use only the data given" + a fixed slide format (`run_eval.py`). It is shown in the kit.
- **Jobs, cuts and India hiring:** as in `JOB_POSTINGS_EVIDENCE.md`; Google cuts are "reported", and the labs' India roles are
  applied-AI roles, not dedicated eval roles.

## Caption draft

Salesforce and Google have been cutting jobs while hiring for evals and post-training (Bangalore, Bengaluru). OpenAI and Anthropic are hiring in India too, and Anthropic's Bangalore role asks you to "help customers develop evaluation frameworks".

So here's what an eval actually catches. I asked AI for a rollout slide based on a 2-store Diwali pilot. It wrote "ROLL OUT TO ALL 300 STORES", with its own warning tucked below the slide.

An eval is 3 things: an answer key written first, yes/no checks, and a separate AI examiner. Same AI, same 10 consulting cases: casual prompt 7/10, proper brief 10/10.

Across 4 models with the casual prompt, every one recommended entering Indonesia with zero Indonesia data.

Comment EVAL for all 10 cases with their checks.

Cases are made up for the test. Models: Claude Fable 5.2, Sonnet 5.5, Haiku 5.5, GPT-6.2 Astra; examiner Claude Opus 5.5.

#AIcareers #LLMEvals #Consulting

## Before the shoot (my side)

1. Blind judge loop on this script (below 7 = no shoot).
2. Build the EVAL kit + `dm_kit/` (10 cases as a clean one-pager, plus the examiner prompt).
3. Screenshots of the job title blocks on the day; the slides are recreated from the saved text (real wording).
