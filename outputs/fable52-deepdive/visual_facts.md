# Fable 5.2 reels: numbers the visuals draw that are not in facts.md / creator_inputs.md / arch_facts.md

Each line below was checked by hand on 19 Nov 2026 against the highlighted page cuts in `paper/cuts/` (PDF page
indices = printed page numbers) or computed as stated. Short excerpts only; the full card text is not copied here.
`content_os/visuals/facts.py` points its fable52 facts at this file and the tests check every quote verbatim.

## Page references (one per paper cut shown on screen)
- P1_p131.png / P3_p131.png: distillation chain and the rubric that generalised, card page 131
- P5_p95.png / P7_p95.png: reward hacks, "guessing what the answer key expects", card page 95
- P8_p39.png: METR tested a stronger snapshot, card page 39
- P9_p13.png: steps to limit AI R&D capabilities, card page 13
- P10_p78.png: same underlying model, differ only in the safeguards, card page 78
- P13_p154.png: the model's own reasoning in an RL episode, card page 154

## Reward hacking (card p.95, excerpt)
- "About 11% of its attempts succeeded, compared with 6.1–6.8% for the three earlier models"
- 11% spoken as "about one in nine" (1/9 = 11.1%)

## CEO quote to launch gap (computed)
- 23 Sep 2026 to 9 Nov 2026: 47 days (7 left in September + 31 in October + 9 in November)

## Page references added 19 Nov (v2 script, cut from the PDF by make_page_cuts.py)
- P14_p186.png: "among the least self-critical Claude models when reflecting on its own work", card page 186
- P15_p34.png: quit without running an experiment in 63% of sessions at medium effort, card page 34
- P16_p91.png: aware it may be in an evaluation in as many as 43% of automated behavioral audit transcripts, card page 91
- P17_p216.png: shown tokens remaining, Fable 5.2 scored 91.6% (up from 85.6%), card page 216

## Per-plate cost, Fable 5.2 vs Opus 5.5 (v3 beat 8, computed 19 Nov)
- Token counts per image, two-step table mode, from demos/food-tracker/RESULTS.md section 5: Fable 5.2 12,180 in / 1,041 out; Opus 5.5 14,066 in / 1,228 out.
- List prices from facts.md: Fable 5.2 $8 in / $40 out per million tokens; Opus 5.5 $4 / $20.
- Fable 5.2: 12,180 x 8 + 1,041 x 40 = $0.139 per plate, about $0.14 per plate
- Opus 5.5: 14,066 x 4 + 1,228 x 20 = $0.081 per plate, about $0.08 per plate
- Difference $0.058 x ₹88 = ₹5.1: about ₹5 more per plate

## v6 tips card (19 Nov)
- Effort cost on FrontierCode (facts.md, card p.209): $2.10 per task at low effort, $44.70 at max: 44.70 / 2.10 = 21.3, max cost about 21x low; best score at xhigh, not max; card page 209
- The tips card lists 3 tips

## Photo credit (v6.1 beat 1)
- Dario Amodei at TechCrunch Disrupt 2023 (cropped). Photo: Kimberly White / Getty Images for TechCrunch, via Wikimedia Commons. Licence: CC BY 2.0 (copied from ~/Movies/ContentOS/fable52-main/assets/dl/CREDIT.txt)
