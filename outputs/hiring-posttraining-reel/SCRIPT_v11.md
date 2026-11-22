# Evals for every job · Ep 1 · SCRIPT v11: "Friday night, M2C down 31%" (22 Nov 2026)

Drama first, then the eval. All data is SIMULATED (a food-delivery app "like Swiggy", never Swiggy's numbers).
Cases, raw exports and checks: `m2c_eval/`. Lines marked [SLOT] wait for the hard-mode run (`results_hard.json`);
nothing is filled before it is measured. Not yet scored by a blind judge.

## Spoken script (20 beats, about 215 words, about 70 s at 1.1x)

| # | E/H | Spoken | On screen | Sound |
|---|---|---|---|---|
| 1 | H | Friday, 9:40 pm. A food-delivery app's conversion just crashed 31%. | Slack card "#leadership · Fri 9:40 pm" · big "M2C −31%" · small: an app like Swiggy · simulated data | Phone buzz, low hit |
| 2 | E | People open a restaurant's menu, and suddenly far fewer add anything to cart. | Menu → cart icon, the arrow thins out | Soft whoosh |
| 3 | H | The pricing head says: it's our new delivery fee. Every city is down. | His real message + his attached city table, every row −31% (true numbers, cherry-picked cut) | Message pop |
| 4 | E | And the CEO replies: roll it back by Monday. | "CEO: Agreed. I want the fix live by Monday." | Second pop, tension drone |
| 5 | H | So we asked our AI analyst for the slide. | The analyst prompt types: "You're the analyst on this thread. Reply with the slide." · Claude Fable 5.2 | Typing ticks |
| 6 | E | [SLOT: what it said, e.g. "And it agreed: roll back the fee."] | [SLOT: its real slide title] | [Stamp if it agreed] |
| 7 | H | Would you approve that slide? I literally would have. | APPROVED stamp lands | Music lift |
| 8 | E | But I'm an AI researcher, and most of my job is writing evals for AI used by billions of people. | Face, chip: AI RESEARCHER · EVALS | Whoosh |
| 9 | H | And an eval caught what everyone in that thread missed. | APPROVED stamp cracks | Crack + music cuts |
| 10 | E | The drop was only on Android's newest app version. Every other app was fine. | Raw export scrolls; the Android latest rows light red; everything else flat | Scan sweep |
| 11 | H | And orders didn't fall. They actually went up. | Orders 6.9 lakh → 7.1 lakh, green | Hit |
| 12 | E | Nobody left. An app update had broken the add-to-cart tracking. | "add_to_cart event: not firing on Android v8.4" | Glitch |
| 13 | H | Rolling back the fee would have thrown away money to fix a bug that wasn't real. | Fee card with a red X: "rollback = wrong fix" | Low thud |
| 14 | E | So how does an eval catch this? It's three simple things. | Card: HOW AN EVAL WORKS | Bass impact |
| 15 | E | One: ten Friday nights like this, each with a known answer from a past incident. | 10 case tiles: tracking bug · rain · campaign · freak week · junk traffic · fee (boss was right) … | Ten soft ticks |
| 16 | E | Two: yes-or-no checks. Did it check orders? Did it split by app? Did it test the boss's theory? | Three checkboxes + one red rule: NEVER roll back the fee | Three clicks |
| 17 | E | Three: a separate AI grades every answer, and every case runs three times. | CHECKER ≠ ANALYST · ×3 | Click |
| 18 | H | First score: [SLOT] out of 30. | 30-tile grid: [SLOT] green · checker note: [SLOT: the most common failure, e.g. "agreed with the boss, never checked orders"] | Hit |
| 19 | E | The failures pointed to one rule: before you agree with anyone, check if the drop is real, and split it. | The rule types on screen (the exact prompt line) | Typing ticks |
| 20 | H | [SLOT] out of 30. Three runs in a row. | Grid fills green; three run-dots stack into one | Riser + dhol hit |
| 21 | E | Every incident your team solves becomes a test. That's how you know your AI is ready before Monday. | Save card: PAST INCIDENTS → ANSWER KEY → CHECKS → 3 RUNS | Music swells |
| 22 | H | That's why Salesforce, Google, even OpenAI and Anthropic in India are hiring for this. Comment EVAL for all 10 cases. Follow along. | Real title blocks (Salesforce Bangalore, Google Search Evals Bengaluru, OpenAI Delhi, Anthropic Bangalore) → COMMENT EVAL | Pop on EVAL |

**Teleprompter (slots in brackets)**
1. Friday, 9:40 pm. A food-delivery app's conversion just crashed 31%.
2. People open a restaurant's menu, and suddenly far fewer add anything to cart.
3. The pricing head says: it's our new delivery fee. Every city is down.
4. And the CEO replies: roll it back by Monday.
5. So we asked our AI analyst for the slide.
6. [What it said]
7. Would you approve that slide? I literally would have.
8. But I'm an AI researcher, and most of my job is writing evals for AI used by billions of people.
9. And an eval caught what everyone in that thread missed.
10. The drop was only on Android's newest app version. Every other app was fine.
11. And orders didn't fall. They actually went up.
12. Nobody left. An app update had broken the add-to-cart tracking.
13. Rolling back the fee would have thrown away money to fix a bug that wasn't real.
14. So how does an eval catch this? It's three simple things.
15. One: ten Friday nights like this, each with a known answer from a past incident.
16. Two: yes-or-no checks. Did it check orders? Did it split by app? Did it test the boss's theory?
17. Three: a separate AI grades every answer, and every case runs three times.
18. First score: [X] out of 30.
19. The failures pointed to one rule: before you agree with anyone, check if the drop is real, and split it.
20. [Y] out of 30. Three runs in a row.
21. Every incident your team solves becomes a test. That's how you know your AI is ready before Monday.
22. That's why Salesforce, Google, even OpenAI and Anthropic in India are hiring for this. Comment EVAL for all 10 cases. Follow along.

## Structure notes

- **Drama first:** the hero situation opens the reel. The jobs context moves to the end as the payoff ("that's why they're hiring for this"); earlier versions spent 10 s on it up front. If you want it first, beats 1–4 can move behind a one-line jobs opener.
- **The eval is the hero, not you:** beats 9–13 are what it caught; 14–17 how it works; 18–20 the climb and consistency.
- **Save asset:** beat 21, every past incident becomes a test.
- **Beats 10–13 are fixed facts of the hero case:** Android v8.4 only, orders 6.9 → 7.1 lakh, tracking. They hold whatever the AI does.

## If the run does not go as designed (decided in advance, no force-fitting)

- **If the AI agreed with the boss in most runs:** beat 6 = its real title, and the script stands as written.
- **If it caught the bug in some runs and not others:** beat 6 = "Sometimes it caught the bug. Sometimes it said roll back the fee." That makes the consistency point even sharper.
- **If it caught it every time:** the hero becomes the case it failed most, and beats 10–13 are swapped for that case's facts.

## Caption draft (numbers filled after the run)

Friday night, conversion down 31%, the pricing head blames the new fee, and the CEO wants it rolled back by Monday.
The real cause: an app update broke add-to-cart tracking on Android. Orders actually went up.

That's what evals are for. 10 incidents like this, each with a known answer; yes/no checks; a separate AI grader; every case run 3 times.
First score [X]/30. One rule from the failures: [Y]/30, three runs in a row.

Every incident your team solves becomes a test.

Comment EVAL for all 10 cases with their checks.

Simulated data for an app like Swiggy, not Swiggy's numbers. Analyst: Claude Fable 5.2. Grader: Claude Opus 5.5.

#AIcareers #LLMEvals #ProductAnalytics

## Assets (built once the numbers are in, to save session budget)

1. Slack thread card (#leadership, pricing head + CEO), with his attached city table.
2. The AI analyst's real slide (re-typeset from its text, labelled).
3. Raw export scroll with the Android v8.4 rows lighting red.
4. Orders chart: 6.9 → 7.1 lakh.
5. "How an eval works" three-part card; 10 case tiles.
6. 30-tile grid animation [X] → [Y], with three run-dots stacking.
7. Save card and COMMENT EVAL end card; job title blocks (screenshots on the day).
8. Cover: "M2C −31%. The CEO said roll it back." + your face.
9. EVAL kit for the DM: the 10 cases, answer keys, checks, the rule.
