---
name: reel-script-writing
description: Write or revise spoken scripts for Content OS Reels, especially face-led AI explainers, career stories and linked series episodes.
---

# Reel script writing

Read `AGENTS.md`, `CLAUDE_WORKFLOW.md`, the relevant brief when one exists, `config/brand.yaml`, and the current versioned Reel-writing guidance before drafting. Preserve the creator's hook promise, approved beat order and series label. Keep earlier drafts available when revising.

## Spoken story

Open with the viewer's real question, show a familiar case early, then explain one mechanism at a time. Make each beat answer a new question. Write for natural speech and preserve the full thought before shortening for runtime. Give a linked follow-up its own concrete payoff.

When the creator requests a broad or theatrical treatment, use stakes, rhythm and a vivid illustrative case. Keep exact role titles, qualification lists and source details in production notes or the caption when they burden the spoken story. Name familiar labs or products when they help orient viewers. Do not invent company-specific processes, hiring outcomes, measurements or personal experience; mark illustrative examples and forward-looking claims clearly.

End with the creator's real connection to the subject and a precise reason to return when the next episode is planned. Tag the requested series consistently on the script, cover and caption.

For a production package, follow the repo workflow and run `python cli.py check <brief>` when a matching brief exists. A script revision alone is a reviewable draft, not proof that a video has been recorded or approved.

## Emotion, hooks and the independent check (since 18 Nov 2026)

The orchestrator script prompt is `prompts/orchestrator_script_v2.md`; follow it when writing by hand too.

- Plan the emotional arc first (e.g. fear -> curiosity -> surprise -> hope -> pride). Every beat names the
  viewer `emotion`, a `delivery` cue for the creator's face and voice, and a `continuity` note (start/end
  pose and energy, and whether the cut needs covering with a full-frame visual or a punch-in).
- Beat 1 works for a stranger in 1.5 s: a number, conflict or claim; never a recap of an earlier
  episode. Product or result within 8 s. Re-hook at one third and two thirds. End on a loop or the
  payoff, not "next up".
- Write 3 hook variants, each on a different emotion, for Instagram Trial Reels.
- Every reel has a save asset (a frame worth keeping) and an honest comment trigger.
- One idea per reel, 40-60 s.
- Positioning: the creator builds AI agents for a living and tests them on their own training and
  food. Prefer a test only they can run and advice from having done the work.

After a draft, an independent model checks it: `python -m content_os.orchestrator check <reel>`
(Opus 5.5, `prompts/orchestrator_story_check_v1.md`) writes `SCRIPT_CHECK.md`. The orchestrator's script
stage does this automatically and lets Fable revise once from the notes. Show the creator the script
with its check. The visual plan gets the same check (`--phase visuals`, `VISUALS_CHECK.md`) before
rendering.

## Script factory: the default way to draft (since 19 Nov 2026)

The creator's time is the scarce resource; drafting rounds run unattended and the creator sees two gates only.
1. Gate 1 (about 2 min): creator approves a one-line-per-section outline in `BRIEF.md` (LOCKED decisions listed)
   and a `facts.md` with only measured or sourced values.
2. `python -m content_os.factory run --brief BRIEF.md --facts facts.md --out outputs/<reel>/factory --open`
   (run it overnight or in the background). Six angles are drafted in parallel (four by Fable 5.2, two by
   GPT-6.2 Astra). Each is scored by Opus 5.5 (facts, honesty, house rules), a GPT-6.2 Astra 16-persona panel, and a
   Fable creator critic that applies `production/CREATOR_TASTE.md`. The top two are revised while they gain.
3. Gate 2 (about 10 min): the creator reads `REVIEW.html` (recommendation, at most 5 decisions, the top two
   packages). Notes go back with `python -m content_os.factory revise outputs/<reel>/factory <id> "notes"`.
4. After every reel ships, rebuild the taste model (`python -m content_os.factory taste`) so the critic learns
   from the latest change lists and the lines as actually spoken.
Never show the creator intermediate rounds. `python -m content_os.factory usage` shows weekly model use.

## Learnings from the Fable 5.2 deep-dive and Ep 3 drafts (19 Nov 2026)

These cost many rounds last time. Apply them before the first draft, not after the panel.

**Before drafting**
- Lock a FACTS sheet first and pass it, whole, to every writer, checker and panel call. Unmeasured values are
  `[SLOTS]`. Why: panels flagged real numbers as unsupported because they were given only part of the facts.
- Do not draft lines whose meaning depends on a result that does not exist yet (the bad set, a score, a verdict).
  Run the test first, then write. Why: [DUMMY] beats were written, then the measurement came back flat and the beat
  was dropped; Ep 3 rounds 1-2 scored 5.2 and 5.0 mainly because the stake (what went wrong) was a slot.
- Get creator sign-off on a one-line-per-section outline before beats, screenplays or visual specs.
- Put this SKILL, `production/REEL_DEFAULTS.md` and the creator's memory rules into every writer prompt.
- Bring the creator's own lines in verbatim, marked LOCKED; the writer may suggest changes beside them only.
- Runtime: estimate at 2.8 spoken words/s before the 1.1x speed-up (measured on Ep 2 takes); state the target
  length up front.

**Structure**
- Payoff image within about 12 s. Show the result (the caught moment, the number) first, then how it works.
  Why: in both deep-dive and Ep 3 panels, mass viewers left at 3-20 s while the payoff sat at 35-40 s.
- A human stake in plain words in the first beats: what went wrong and what it risked, as a trainer would say it.
- One actor per idea. In speech say "my AI"; tool and model names live on the diagram, not the voice track.
  Why: "pose tool, coach, judge, safety check, tally" read as five characters in 46 s.
- Never rely on a previous reel for a twist or hook; cold viewers never saw it. Put series callbacks in the caption.
- Architecture stays (it is the creator's signature) but is made clearer, never cut, to fix mass scores:
  two ideas spoken, the rest on a progressively built diagram with a running label.
- Max three findings or ideas; no teases like "one number made me stop".
- Every finding: evidence on screen -> one plain line -> an everyday Indian comparison -> "So [one action]".
- A spoken bridge question at every topic change; close by name every loop the hook opened, before the CTA.
- Gloss proper nouns on screen in the first 3 s; keep insider terms (guardrail, occlusion, pipeline) off the voice.
- Speak one comparison, not a run of numbers.

**Accuracy**
- Rewrite any spoken claim that needs a footnote to be true (exact ratio, sample size, "cost" not "billed").
- Consistency pass: no beat contradicts an earlier rule or number (e.g. "never let it check itself" then "Fable judges").
- Tips are the creator's own, each backed by a measurement or a page reference.
- Every beat that leaves text to read gets an explicit on-screen hold.

**Panel and iteration**
- Freeze one persona set (the 16 in `outputs/workout-analyser-reel/iterate.py`) and one metric (engagement 0-10
  per persona, mean = overall) so rounds compare. Tell the panel which creator decisions are locked and may not
  be reopened (architecture section, the A/B variable, verbatim lines).
- If a revision round scores lower than the one before, stop and diagnose from the panel's drop-off beats; do not
  keep looping. Decide the experiment variable once and log it in `production/EXPERIMENTS.md`.

**From the Fable 5.2 shoot and final (19 Nov 2026; Fable final rating 7/10)**
- Quotes on camera must match the source word for word; paraphrase as "he warned..." if the exact line is long.
  Why: "AI could wipe out humanity" was spoken but the real quote says something else; the screen had to carry it.
- Expect rewording on camera: the edit matches the spoken lines (audio is ground truth), so keep each beat one
  self-contained thought that can be recorded alone; skipped beats must not break the story.
- Weakest scores were emotion (6) and sends (6): write one personal stake line ("this nearly cost me...") and one
  line a viewer would forward to a friend. Strongest were hook (8), value (8), saves (8): concrete rules with page refs.
- Fable predicted drops at 8-12 s (a credit/context clip before the payoff), the middle of a three-finding stretch,
  and just before the CTA. Put the payoff before any context clip and change visual mode every finding.

## Ep 3 retro: hard gates (21 Nov 2026; creator: "visuals were amazing but script was very weak, no connection to Jarvis")

What went wrong on the Workout Analyser reel: visuals were rendered before the finding existed and the script was bent
around them (the story changed about eight times); no version passed the score bar (best 5.6, target 7.5) and it was
shot anyway; "Gym Jarvis" was written out of the voice ("my AI system"); the hook ("the one set I should never have
done") overpromised a mild catch (half reps); the as-recorded words were never judged before the edit.

Gates, in order. Each one blocks the next step:
1. FINDING FIRST. The measured result must exist and be strong enough to carry the hook before any outline. If the
   catch is mild, change the episode, not the adjectives.
2. SCRIPT BEFORE PIXELS. No visual is rendered until a one-page script (spoken lines only) passes gate 3. One
   throwaway look-test clip is allowed; nothing else.
3. THE SCORE GATE IS HARD. Panel below 7: do not shoot. Maximum two rewrite rounds; then change the premise or cut
   scope with the creator. Never polish visuals to compensate for a script that has not passed.
4. SERIES ANCHOR (only when the reel belongs to a series; a judgement per reel, not a blind rule). The series (e.g. Gym Jarvis) is named early; the episode says what it learned to do
   today and what it does next. Naming the series is not a recap (the "never a recap" rule bans retelling, not the name).
5. (Removed 21 Nov: the creator does not see length or several ideas as the problem. Keep a clear
   problem -> system -> failure -> fix -> proof arc, but scope and length are the creator's call.)
6. JUDGE THE RECORDING. After the shoot, the as-recorded transcript is judged as a script before the edit starts;
   weak or off-spine lines are re-recorded then.
7. CALIBRATE. Feed real Instagram numbers (3-s hold, average watch, sends) for past reels to the panel so its scores
   are anchored; log predicted vs real in production/EXPERIMENTS.md.

## Default skeleton for system / build reels (21 Nov 2026, creator: "think through such things should happen by default across all use-cases")

Applies when the reel shows something the creator built or measured (a Gym Jarvis feature, an agent, a pipeline,
a model tested in his own system). Not for pure career stories or news reels; that is a judgement per reel profile.
The Ep 2 calories narration is the reference the creator loves; new spines must start from this skeleton, and a
different structure (e.g. failure-first) is only offered as a variant beside it, never instead of it.

SERIES ANCHOR ("In last video, you met my Gym Jarvis") -> TODAY'S TASK -> RESEARCH -> EASY vs HARD insight ->
SPLIT INTO PARTS -> COMPONENT 1 (what it does + what it is NOT allowed to do) -> COMPONENT 2, called out as "the
second agent / second part" (and why it exists) -> GUARDRAIL -> TESTED ON MANY (real count) -> RESULTS as a
dashboard (taller = better) -> "EXCEPT THIS ONE" failure -> THE FIX -> NEXT / CTA.

Must be present whenever the skeleton applies (judged per reel, with evidence):
- COMPONENTS NAMED: every system part named by role, built up as one block diagram.
- MECHANISM CONCRETE: say exactly how it decides, in words a gym trainer could repeat (Ep 3: joint angle draws a
  wave, one wave = one rep, height = range, compared with my own best wave; real numbers on screen).
- RESULTS SHOWN: the real test count and the full outcome tally on a dashboard, not just the one interesting case.
- Each component beat carries a human stake or rule in its own line ("it's not allowed to say calories"), so the
  architecture holds mass viewers instead of being cut for them.
Origin: Ep 3 trial spines dropped the Ep 2 structure, the system parts and the 23-set results; creator rejected them.

## Scoring loop: never let the writer grade itself (21 Nov 2026)

On the Ep 3 trial, Fable self-scored v3 at 6.9; a fresh blind Fable judge scored the same script 5.0 (voice match 4/10).
Self-scores run about 2 points high and must not be used for the score gate. Default loop for every script round:
1. Diagnose against the creator's own as-spoken reference reel (voice stats: words per line, connectives, no
   semicolons or clipped caption fragments; spoken lines are not on-screen text).
2. Write 3 drafts in parallel, each pulling a different lever (voice, stake, anchor/hook...).
3. A fresh judge (no authorship, scripts shuffled and labelled A-D, previous version included) scores panel +
   VOICE_MATCH + MECHANISM_CLARITY and names grafts from the losers.
4. The writer merges the grafts; a second blind judge compares merged vs winner; Opus checks facts and voice.
Only blind-judge scores count for the gate.
