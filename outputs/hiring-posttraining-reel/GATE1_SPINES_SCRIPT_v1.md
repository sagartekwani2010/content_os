# Salesforce reel → Evals series · Gate 1, spines, script v1 (22 Nov 2026)

Status: draft for the creator. No blind judge has run yet, so it has no score that counts.
Nothing is rendered: the gates say script before pixels.

## The promise this reel pays off

Ep 3 ended, as spoken: "Next up: Salesforce is reportedly letting people go, but hiring people with AI experience.
How can you be that one? Follow along to know."
The answer must be one concrete skill, not "learn AI".

## Gate 1: the finding only you add

**Finding: the job Salesforce is hiring for is mostly about proving a model got better, which is evals. You already
run evals on your own agents, and you have one measured result that shows the most common mistake.**

All measured or quoted:
- The posting (JR368314, saved verbatim) uses **"evaluat-" 14 times and "prompt" 5 times**. One of the prompt
  mentions is the line "This is a model-training role, not a wrapper around a hosted LLM and not a prompt-engineering-only role."
- It asks candidates to show **"the exact denominator, dataset split, and review method behind any quality or
  business-impact metric on their resume."**
- It says Salesforce values **"demonstrated engineering judgment and reproducible results over credentials"**.
- **Your own eval result (Ep 3, 21 Nov):** Fable scored its own script 6.9/10. A fresh, blind Fable judge scored the
  same script 5.0 (`outputs/workout-analyser-reel/STATUS.md`). Rule: the examiner is never the student.
- **Your other real evals:** 50 Nutrition5k plates in the Meal Analyser (protein error per model and cost per image, in
  `demos/food-tracker/eval/results.json`), and the judge-vs-coach agreement of 9 of 16 sets in the Workout Analyser.

Why this is yours: anyone can read a job post. Few creators can say "here is the exact eval mistake I made last week, measured".

**Honest limits (caption, not voice):** the role asks for 10+ years of experience and hands-on post-training.
Evals alone will not get anyone this job; it is the part a viewer can start today without a GPU.
The India garden-leave story is "reportedly". Benioff's 9,000 → 5,000 is on record (2025).

## Reel or carousel first? Reel first, with the carousel as the kit

1. **The tease was a reel.** The Ep 3 viewers were promised the answer in the next video, so pay it off in the same format.
2. **Reels are your proven reach format.** Your account has no carousel numbers yet, so a carousel-first series
   would launch on an untested format.
3. **The carousel is the thing people import.** Each domain episode is a carousel (copyable eval: 10 test cases,
   rubric, judge prompt). The comment keyword DMs the same file. That is your "follow just for that".

Rhythm I recommend: **Reel 1 (this one) opens the series → Carousel 1 consulting (posted 2-3 days later) → every
second or third domain gets a short reel built from its carousel's most surprising result.** We decide after
three domains, using the real save and follow numbers in `production/EXPERIMENTS.md`.

## Where I disagree (short)

1. **A domain eval with no real run is a template listicle.** Your taste model rejects that as filler. Each domain
   episode needs one real run: for example, 10 consulting tasks run through Fable and one other model, scored by a
   blind judge, with the real numbers. Then the carousel shows the kit and the result.
2. **Consulting is not your own work.** That is fine if you say "I tested AI on consulting tasks". The cases must be
   public or made up and labelled as such, never a client's data. A consultant reviewing your 10 cases would add
   credibility, and the carousel could credit them.
3. **The recap of the LLM reel should take one beat, not a section.** Pretraining, post-training and evals is
   one line over the old diagram. I assumed "LLM working reel" means Generic AI 01 (`outputs/ai-training-jobs-reel-01/`),
   which covers those three layers. **Confirm it was posted**, because a recap of an unposted reel confuses viewers.
4. **The comment kit must exist before posting.** "Comment EVAL" only works if the consulting eval starter kit is
   built and tested first. That is about two hours of my work, and I can do it in parallel.

## Three spines

**A · "14 times" (JD decoded). Recommended.**
Salesforce cuts and hires → you read the complete JD → "evaluation 14 times, prompts 5, and 'not a prompt-engineering
role'" → one-line recap: pretraining, post-training, evals → what an eval is, in plain words → your measured mistake:
6.9 self vs 5.0 blind → "So always keep the examiner separate" → the JD's "exact denominator" line = how you become that
one → series: evals for every job, starting with consulting → Comment EVAL.
*Why:* it pays the tease off in the first 10 s, keeps the company story, and carries your own proof.

**B · "My AI graded its own homework" (personal first).**
Hook: "My AI gave its own script 6.9. A blind judge gave it 5.0." → that gap is an eval, and it is exactly the skill
Salesforce is hiring for → the JD lines → series → CTA.
*Why:* a stronger cold hook and more personal. *Risk:* the Salesforce payoff lands late for the Ep 3 viewers.

**C · "Your job has an exam your AI never sat" (viewer first).**
Opens on a consultant's task (a client-call summary), shows the AI failing one case, then "Salesforce is hiring for
people who can catch this", and teaches the 3-part eval.
*Why:* the most useful for a mass audience. *Risk:* it needs the consulting run first, which does not exist yet
(gate 1 fails today), and the Salesforce link is weakest.

**A trial would be drastically different only as B.** Same facts, but a personal-humour hook instead of a company-fear
hook. Record it only if you think the emotion is different enough (your rule).

## Script v1 (spine A) · spoken lines only

About 205 words, so about 73 s at 2.8 words/s, or about 66 s at 1.1x. E = emotion, H = hook.

| # | E/H | Spoken | On screen (detail lives here) |
|---|---|---|---|
| 1 | E | Salesforce's CEO said AI agents cut his support team from 9,000 to 5,000 people. | Benioff quote card · "I NEED LESS HEADS" · The Logan Bartlett Show, 2025 |
| 2 | H | And this month, Salesforce posted this job in Bangalore. | Real title block: LMTS - Lead AI/ML Engineer (LLM Post-Training) · posted 13 Nov 2026 |
| 3 | E | So, out of curiosity, I read the complete job description. | JD scroll, real page |
| 4 | H | The word evaluation shows up 14 times. Prompts? Only five. | Two counters: EVALUATION 14 · PROMPT 5 · small: counted "evaluat-" and "prompt" in the posting |
| 5 | E | And one line literally says: this is not a prompt-engineering-only role. | Verbatim JD line, highlighted |
| 6 | H | In my last reel, I showed how AI is actually built. | Old diagram returns: PRETRAINING → POST-TRAINING → EVALS |
| 7 | E | Pretraining builds it, post-training shapes it, and evals prove it actually got better. | EVALS box lights up |
| 8 | H | This job needs all three. But evals is the one you can start today, without a GPU. | "NO GPU NEEDED" chip on EVALS |
| 9 | E | An eval is just an exam for your AI: real questions, right answers, and a fair examiner. | Three blocks build: QUESTIONS · ANSWER KEY · EXAMINER |
| 10 | H | And the examiner is where most people go wrong. Including me. | EXAMINER box pulses red |
| 11 | E | For my last reel, my AI wrote the script and gave itself 6.9 out of 10. | Score card: SELF-SCORE 6.9 |
| 12 | H | A fresh AI, that didn't know who wrote it, gave the same script 5.0. | BLIND JUDGE 5.0 · gap of 1.9 drawn in red |
| 13 | E | So always keep the examiner separate from the student. | Rule card (the save asset) |
| 14 | H | Salesforce even asks for the exact denominator behind every number on your resume. | Verbatim JD line: "the exact denominator, dataset split, and review method…" |
| 15 | E | That's how you become that one: you can prove your AI got better. | Callback to the Ep 3 tease words: "HOW CAN YOU BE THAT ONE?" → answered |
| 16 | H | So I'm starting a series: evals for every job, starting with consulting. | Series card: EVALS FOR EVERY JOB · 01 CONSULTING · 02 … (next domains greyed) |
| 17 | H | Comment EVAL and I'll send you my eval starter kit. Follow along. | COMMENT EVAL · kit preview (rubric, 10 cases, judge prompt) |

Voice notes from your taste model: "So, out of curiosity", "literally", "actually", "So always…" are your own
connectives. The scary number is first (beat 1) and the attribution second.

**Not in the voice, on purpose:** the 10+ years requirement, "reportedly" garden leave (caption), DPO/GRPO names
(JD scroll only), and the food tracker numbers (save them for an episode).

## Caption draft

Salesforce cut support from about 9,000 to about 5,000 as AI agents took over half the conversations (Marc Benioff, 2025).
In India, staff were reportedly put on garden leave this month.

The same month, Salesforce posted a Lead AI/ML Engineer (LLM Post-Training) role in Bangalore. I read all of it.
"Evaluation" comes up 14 times. And it asks for the exact denominator behind every metric on your resume.

My own lesson from last week: my AI scored its own script 6.9. A blind judge scored it 5.0. The examiner can never be the student.

New series: evals for every job. Consulting first.
Comment EVAL for the starter kit.

Honest bit: the role asks for 10+ years and hands-on post-training. Evals are one part of it, and the part you can start today.

#AIcareers #LLMEvals #Salesforce

## What I need from you (3 answers)

1. **Spine:** A (recommended), B or C?
2. **Recap:** is "LLM working reel" Generic AI 01 (pretraining, post-training, evals), and was it posted?
3. **Consulting run:** OK for me to build 10 public consulting tasks + rubric + blind judge and run Fable vs one
   other model before the carousel? (I'd pick GPT-6.2 Astra as the other.)

## Next steps once you answer (no creator time needed)

- Blind judge loop on the chosen spine: 3 parallel drafts, a fresh judge, an Opus fact check. Only blind scores count; below 7 = no shoot.
- Build the EVAL starter kit + `dm_kit/` and test it.
- Teleprompter in Chrome, then record.
