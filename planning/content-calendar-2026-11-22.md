# Content calendar · 22-29 Nov 2026 (format screening week) + standing week

Agreed with the creator on 22 Nov 2026. Each item below is worked on in **its own chat**. Start that chat with the
item's kickoff line. When a chat ends, update the item's `STATUS.md` and the Status column here.

## Rules for every item

- **Two domains merged** in every piece; only rage (fast-lane) reels are exempt. Build demos use the creator's own
  products. Playbooks (prompting, guardrails, evals) may borrow any relatable domain (Ramayan, cricket, cooking, health).
  The analogy is the hook. Each piece still shows **one real run** with real output. Religious stories are told
  faithfully and respectfully.
- Analogy carousels (the Lakshman Rekha style) are the house style for Playbooks.
- Script gates from `.agents/skills/reel-script-writing/SKILL.md` apply to reels. Carousels get a blind Fable score
  and an Opus fact check before the creator sees them.
- A comment keyword ships only with its `dm_kit/` built and tested (`production/REEL_DEFAULTS.md`).
- Facts: "reportedly" for unconfirmed news. No invented screenshots or headlines. Paper numbers are checked against
  the PDF and labelled author-reported.
- Media and screenshots stay out of Git.

## This week

Posting times are starting defaults (IST); check them against Insights "most active times".

| # | Day / time | Format tested | Item | Two domains | Owner of the work | Status |
|---|---|---|---|---|---|---|
| 1 | **Sun 22**, 19:30 | Careers carousel | Salesforce → evals → consulting eval run + kit, keyword EVAL | Careers × consulting × evals | Claude (creator approves) | to start now |
| 2 | **Mon 23**, 13:00 | Static Playbook carousel | "Prompt like a family recipe" | Cooking × prompting | Claude | v2 (gym, 8 techniques) rendered 22 Nov; PREVIEW.html awaiting creator review |
| 3 | Tue 24 | Fast-lane rage reel | Only if something trends (manual check until a trend scan exists) | exempt | creator call | standby |
| 4 | **Wed 25**, 13:00 | Carousel with video slides | Lakshman Rekha = guardrails, Ravana in disguise = prompt injection | Ramayan × guardrails | Claude | start Mon |
| 5 | **Thu 26**, 13:00 | Paper reel | Memento-Skills deep-dive: "My gym AI rewrote its own instructions" | Research × own fitness agent | Claude builds, creator records VO Wed | start Mon |
| 6 | **Fri 27**, 13:00 | Companion carousel | Item 5's implementation: loop, skill-file diff, held-out result | same as 5 | Claude (in item 5's chat) | after 5 |
| 7 | **Sat 28**, 08:30 | Build reel | Scoring Analyser (demo already in Gym Jarvis) | to be decided in its chat | creator records Fri | ready to start |
| 8 | **Sun 29**, 19:30 | Careers reel | New careers topic: TBD | Careers × to be decided | creator records Fri | topic TBD |

Readouts: **Thu 26** (48 h for items 1-2), **Tue 1 Dec** (full week). Record for each post at 24 h and 48 h:
reach, % non-follower reach, saves, sends, follows, profile visits, keyword comments. For reels, also 3-s hold and
average watch. One post per format gives a direction only; treat gaps under about 2x as noise. Winners repeat the
following week before they become defaults.

Creator camera time this week: one voiceover (Wed, item 5) and one batch recording (Fri, items 7 + 8).

## Item briefs and kickoff lines

### 1 · Sun 22 · Evals for every job, Ep 1: consulting (carousel only, no reel)
Folder `outputs/hiring-posttraining-reel/`. Read its `STATUS.md` and `GATE1_SPINES_SCRIPT_v1.md`: the finding, facts
and limits already exist there. Today posts a **carousel**, not a reel. It is the series introduction and the kit
together, so no separate kit carousel follows on Monday.
Slides (about 10): hook paying off the Ep 3 tease → the JD evidence ("evaluat-" ×14, "prompt" ×5, "not a
prompt-engineering-only role") → evals explained through the cricket third umpire ("the examiner is never the student")
→ own proof (self-score 6.9 vs blind 5.0) → **real consulting run**: 10 public or made-up (labelled) consulting tasks,
Fable vs one other model, blind judge, real numbers → honest limit (10+ years asked; evals is the part you can start
today without a GPU) → comment EVAL.
Needs: the run, slides, caption, pinned comment, `dm_kit/` (cases, rubric, judge prompt). Check whether an OpenAI key
exists. If not, compare two Claude models and say so on the slide.
> Kickoff: "Item 1 of planning/content-calendar-2026-11-22.md: build tonight's consulting evals carousel."

### 2 · Mon 23 · "Prompt like a family recipe"
Folder `outputs/carousel-prompting-recipe/`. Hook: "a pinch of this, cook till done" is how most people prompt.
Show 3-4 real before/after prompts with real outputs, plus a rule per slide. English only on screen. Optional
keyword. If one is used, it needs a DM kit.
> Kickoff: "Item 2 of planning/content-calendar-2026-11-22.md: the family-recipe prompting carousel for Mon 23."

### 4 · Wed 25 · Lakshman Rekha guardrails (carousel with video slides)
Folder `outputs/carousel-guardrails-lakshman-rekha/`. The Rekha is a guardrail. Ravana arriving as a sage is a prompt
injection: a trusted-looking input that gets the system to cross its own boundary. Short screen-recorded slides show
a **real** injection beating a naive guardrail, then the fix holding. Tell the story faithfully. The point lands on
the AI, never on mocking the story. Check Instagram's per-clip video limit for carousels before building.
> Kickoff: "Item 4 of planning/content-calendar-2026-11-22.md: the Lakshman Rekha guardrails carousel for Wed 25."

### 5 + 6 · Thu 26 reel + Fri 27 companion · Memento-Skills in Gym Jarvis
Folder `outputs/paper-memento-skills-reel/`. Paper: *Memento-Skills: Let Agents Design Agents*, arXiv 2603.18743
(19 Mar 2026), code at github.com/Memento-Teams/Memento-Skills. Contrast in one beat: SkillRL (arXiv 2602.08234,
NeurIPS 2026) retrains the model (8× H100, about 30 h per run). Memento rewrites skill files and never retrains.
Analogy: a cricketer's net practice (muscle memory = retraining) vs a notebook of each bowler's habits (skill files).
**Real implementation:** the Workout Analyser's set-judging skill (judge-vs-coach agreement 9/16 today) improves
through a Memento-style loop (judge, then failure attribution, then skill rewrite, then test gate) on half of the
coach-labelled sets. Measure on the **held-out half**. Report either outcome honestly ("it memorised, it didn't
learn" is a valid story). On screen: "8 sets: a direction, not proof." Check paper numbers against the PDFs
(SkillRL's text and Table 1 disagree on the GRPO baseline). Reuse visual prompts from
`outputs/skillrl-agent-skills-paper-reel/` for the contrast beat. Item 6 is the companion carousel from the same
chat: loop diagram, skill-file diff, held-out result.
> Kickoff: "Items 5+6 of planning/content-calendar-2026-11-22.md: the Memento-Skills paper reel and its companion carousel."

### 7 · Sat 28 · Scoring Analyser (build reel)
The creator has the plan, and the demo already exists in Gym Jarvis (it is not the posted Workout Analyser). Follow
the build-reel skeleton and script gates. Name the folder in that chat. Must not repeat the evals carousel or the
paper reel.
> Kickoff: "Item 7 of planning/content-calendar-2026-11-22.md: script the Scoring Analyser build reel from the Gym Jarvis demo."

### 8 · Sun 29 · Careers reel
Topic TBD (not evals). Folder to be named. The topic is set by Tue 24, the script gates by Thu 26, recording on Fri 27.
> Kickoff: "Item 8 of planning/content-calendar-2026-11-22.md: pick and script the Sun 29 careers reel."

## Standing week (from Mon 30 Nov)

| Day | Slot | Category |
|---|---|---|
| Mon | Carousel | Companion to Sunday's reel, keyword for leads |
| Tue | Fast lane | Rage, only if trending |
| Wed | Carousel | Analogy Playbook (next: evals through the cricket DRS) |
| Thu | Reel | Paper deep-dive with an implementation |
| Fri | Carousel | Playbook (static or video, whichever won this week) |
| Sat, morning | Reel | Build in public, rotating Gym Jarvis → AI Wardrobe Stylist → Content OS |
| Sun, evening | Reel | AI careers |
| Daily | Stories | Keyword reminders, polls, waitlist link |

"Evals for every job" continues as carousels, one job per week, if item 1's feedback supports it. The Tue 1 Dec
readout can change which format fills a slot. It does not change the day moods behind the slots.

## Not done yet

- A daily trend scan for the fast lane (needs the creator's go; costs tokens per run).
- The Instagram Graph API token, which would automate the readouts and allow Business Discovery on competitor accounts.
- The content catalogue itself (series and entries with status, links and performance); this calendar becomes its first week.
