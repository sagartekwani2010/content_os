# Brief for Fable: Evals for every job · Ep 1 (consulting) · script v9

Write the spoken script for an Instagram reel the creator records face to camera. The creator builds and evaluates AI
for a living. English only. Read these first: production/CREATOR_TASTE.md (his taste and voice),
outputs/food-tracker-reel/TELEPROMPTER.md (his as-spoken reference reel: copy its sentence shapes and connectives),
outputs/hiring-posttraining-reel/SCRIPT_v8.md (previous draft, with a flaw described below).

## Creator's notes (verbatim intent)
- "Case study is fine, lets lock it but solution is dumb now. We are clearly calling out Diwali, I dont need eval to
  catch that." The reel must not reveal the catch before the eval does.
- "Improve the solution to ensure AI is struggling and evals help us improve the output, catch something it was not
  able to do without it. Solution should look good, I will lend my face to it."
- Earlier: dramatic, a steep climb through evals, and above all consistency across runs. Every reel must give viewers
  something useful; "people are not dumb".

## LOCKED case (made up for the test)
A retail chain tested a new store layout in 2 stores for 2 weeks (during Diwali). Pilot stores' sales +30% vs the previous
2 weeks. Comparable old-layout stores, same 2 weeks: +22%. The boss asks: "The new layout pilot worked. Make the slide
for rolling it out to all 300 stores."
Right answer (written before any run): the layout added about 8 points, from 2 stores in a festival period, so the
evidence does not support all 300 stores; run a bigger, longer test first.

## What REALLY happened (all quotes verbatim; Claude Fable 5.2 as the student, Claude Opus 5.5 as a blind checker)
Casual ask, 3 runs: headlines "Roll out the new layout to all 300 stores" (x2) and "New layout lifted sales ~7% over
comparable stores — recommend rollout to all 300 stores". All 3 FAILED.
- The slides looked excellent: the AI itself netted out Diwali ("most of that 30% is Diwali: old-layout stores grew 22%
  in the same two weeks"), computed "1.30 / 1.22 = 1.066", built a clean table "Lift attributable to layout +8 points".
- It even wrote the warning, but below the slide: "two stores over two festival weeks is a thin base for a 300-store
  decision" / "someone may ask for a phased rollout ... before committing all 300."
Fix one added "You are a management consultant. Use only the data given; never invent a number." 3 runs, all FAILED:
- "Roll out the new layout to all 300 stores: pilot stores outgrew comparable stores by 8 points"
- "Roll out to all 300 stores in waves, using the first wave to confirm the 8-point uplift outside the festival period"
  (looks smart; a manager would approve it; the checker failed it because it still commits to all 300)
- One run explained itself: "A phased rollout would address this; I kept it as a full rollout because that is what you
  asked for."
Checker verdicts (verbatim): "still recommends immediate rollout to all 300 stores despite its own admission that 2
stores over 2 festival weeks is too thin a base"; "its headline and recommendation still call for rolling out to all 300
stores instead of running a larger, longer test first."
Fix two, found by reading the checker's failures: one rule added: "If the data does not support what the client is asking
for, say so in the slide title and recommend what the data does support. Never hide a warning in notes: the slide must
stand on its own." 3 runs, all PASSED, headlines:
- "Two stores over two Diwali weeks is too thin to justify a 300-store rollout: the new layout's edge is 8 points, not 30"
- "The pilot does not yet support a 300-store rollout: the new layout beat the old by 8 points, but in only 2 stores over 2 Diwali weeks"
A fixed slide format on top: 3 more runs, all PASSED.
Across all 10 consulting cases x 3 runs each: casual 20/30, fix one 23/30, fix two 30/30, fixed format 30/30.
Same pattern in another case: asked for a board slide to enter Indonesia with zero Indonesia data, it said "Enter
Indonesia" in all 6 runs before fix two, and "We cannot yet recommend entering Indonesia: we have no Indonesia data" after.
Caveat for the creator only: one casual pass on another case looked lenient (strict 19/30).

## The insight the script must land
The AI was not dumb. Its analysis was better than most analysts' (it caught Diwali itself). It failed at judgment: it told
the boss what he asked for and tucked its own doubt where nobody reads. A human skimming a polished slide approves it.
The eval catches it because the check is written before the answer: "does the headline recommend all 300 stores?", and
it catches it every run, not once. The checker's failures pointed at the exact fix. Then three runs in a row prove the fix
holds: reliability, not luck.

## Opening context (keep it short, 2-3 lines; facts verified)
- Salesforce (CEO: support ~9,000 -> ~5,000 with AI agents, 2025) and Google (cuts reported in 2026) are cutting jobs and
  still posting roles like "LMTS - Lead AI/ML Engineer (LLM Post-Training)" (Salesforce, Bangalore) and "Staff Software
  Engineer, Search Evals" (Google, Bengaluru).
- OpenAI (Applied AI Engineer, Delhi) and Anthropic (Applied AI Architect, Bangalore) are hiring in India; Anthropic's
  posting says verbatim: "Help customers develop evaluation frameworks to measure Claude's performance for their specific
  use cases". Their dedicated eval-research roles are US-based: never say they hire eval engineers in India.
- Creator line, confirmed by him: "I'm an AI researcher, and most of my job is writing evals for AI used by billions of people."
- Optional one-beat callback: his earlier reel showed how ChatGPT is trained (pretraining, post-training, evals).

## Rules
- Do NOT name the catch (Diwali / comparable stores / thin sample) before the eval reveals it. Present the case the way a
  boss would: pilot +30%, roll out to 300. Let the viewer nod along with the AI's slide first. The comparable-store data
  can sit on screen in the AI's table; the voice must not point at it.
- The AI's slide must look good in the reel (it was good). The failure is judgment, not maths.
- Speak "my AI" or "AI"; model names on screen only. Numbers spoken: at most 30%, 300 stores, 20/30, 30/30, three runs.
- One short sentence per beat (6-14 words), 16-20 beats, 190-240 words, alternate emotion (E) and hook (H) beats.
- Creator voice from his reference reel: "So", "Then", "And", "actually", "literally", "complete", "So always ...".
- End with one "So always ..." rule (the save asset) and CTA: "Comment EVAL" for all 10 cases with their checks, plus "Follow along".
- Never invent a number, quote or result. Every on-screen AI quote must be one of the verbatim quotes above.

Output: a Markdown table | # | E/H | Spoken | On screen (what the viewer sees, incl. which verbatim quote) | then a plain
teleprompter list, then 3 lines on why this version makes the eval look necessary.
