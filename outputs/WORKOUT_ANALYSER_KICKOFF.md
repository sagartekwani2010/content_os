# Kickoff: Gym Jarvis Ep 3, Workout Analyser reel (posting Saturday 21 Nov 2026)

Paste this into a new Claude Code session opened in `~/Desktop/codebases/content_os`, then start.
Updated 20 Nov 2026 after the Fable 5.2 reel shipped and the first script-factory run.

## 1. The story so far
- Series: Gym Jarvis. Ep 1 intro; Ep 2 Meal Analyser (two agents on Fable 5.2, Nutrition5k eval, hidden-chicken
  failure, confidence guardrail); Fable 5.2 deep-dive (19 Nov, Fable rating 7/10).
- The deep-dive ENDS on a tease: "Let's see how Fable stopped me from doing a wrong set in my Workout Analyser",
  over IMG_2649 (hack squat) with a red circle, "WORKOUT ANALYSER" and a red X "STOP!". Saturday must pay that off
  honestly. Footage was filmed before the analyser existed: say "found" / "would have stopped me", never "stopped
  me mid-set".
- Existing code: `demos/workout-hud` (pose, knee wave, rep count, `label/`, `visuals/`), the `form-labeller` skill
  in `.claude/skills/form-labeller/` (not public yet).

## 2. Where the script stands
- Brief v2 (outline + LOCKED decisions): `outputs/workout-analyser-reel/BRIEF.md`; facts: `.../facts.md`.
- Earlier loop (another session): `outputs/workout-analyser-reel/iterate.py`, `rounds/old_v1_brief/`.
- **Script factory run, 20 Nov:** `outputs/workout-analyser-reel/factory/REVIEW.html` (open this first),
  `DECISIONS.md`, `leaderboard.json`, all drafts in `round_0/`, `round_1/`.
  - Leader: **F** (GPT-6.2 Astra, cold-open scene; panel 6.47, creator critic 6.5) and **B** (Fable, contrarian
    self-correction; panel 6.0, critic 6.5). No draft passed 7.5, mainly because the stake (the bad set) is still a
    [SLOT]. Rule from the script skill: measure first, then rewrite.
  - Recommendation: MAIN = F's body with B's short hook "My AI found the one set I should never have done."
    TRIAL = "I thought this was my worst set. My AI said it was fine. It flagged this one."
  - Ignore the drafts' `bottom_px 440` caption note: captions now sit at the seam by default (section 5).

## 3. What YOU need to prepare (the factory cannot do these)
1. **Build/run the judge** on your filmed sets: it must return CONTINUE / HOLD / STOP with one reason, using your
   best set as the baseline. Pick the set where its measured call is STOP.
2. `[BAD_SET]`: lift, date, rep number, fault. `[REASON]`: the judge's own reason, 4 words max.
3. `[BEST_SET]`: same lift and a similar camera angle (otherwise the ghost overlay becomes side-by-side skeletons).
4. `[N_SETS]`: how many clips were analysed, and confirm exactly one got STOP (the "1 FLAGGED" line depends on it).
5. `[CAN'T-SEE STRING]`: the exact message the system prints when the leg is hidden.
6. 14 -> 11 reps: the raw export path, so the three dropped detections come from `reps_clean.json`.
7. `[RISK]`: your wording, 3 words max, or cut the risk line.
8. Answer the 5 decisions in `DECISIONS.md` (hook length, trial line, comment keyword FORM vs JARVIS and whether you
   send the skill, keep the two extra beats, post a measured-only cut if no STOP exists by Saturday).
Put the numbers in `facts.md`, then run:
`python -m content_os.factory revise outputs/workout-analyser-reel/factory F "facts updated; my decisions: ..."`

## 4. How scripting runs now (two gates for you)
- Gate 1: outline + LOCKED decisions in BRIEF.md, measured facts in facts.md.
- `python -m content_os.factory run --brief ... --facts ... --out outputs/<reel>/factory --open` drafts 6 angles
  (4 Fable 5.2, 2 GPT-6.2 Astra). Opus 5.5 checks facts/rules, an Astra panel of 16 personas scores engagement, and a Fable
  creator critic applies `production/CREATOR_TASTE.md`. The top two are revised automatically.
- Gate 2: REVIEW.html, then `factory revise <out> <id> "notes"`. `factory taste` after each reel; `factory usage`
  for weekly model use (first run: Fable 16 calls / 45 min, Opus 8, Astra 10).
- Model roles: `config/factory.yaml`. Skill: `.agents/skills/reel-script-writing/SKILL.md`.

## 5. Production defaults that changed this week
- Speed 1.15x for talking-head explainers; catchy techno bed from second 0 (-15/-16 LUFS); about one SFX every
  2-3 s; section cards with whoosh + bassy impact.
- **Captions at the seam** (`caption_position: seam`, now the pipeline default): low captions crossed the IG ad
  "Visit Instagram profile" button. Keep the bottom ~100 px of every visual panel empty; put chart fixes inside the
  visual clip, never as an overlay after export.
- Charts show a higher-is-better metric. Quotes word for word. Tips are the creator's own.
- Finish: `scripts/edits/finish/fable52_prep.sh` / `fable52_finish.sh` (generalise the reel name). Edits caches
  media by path, so rebuilds import timestamped files; `verify_final.py` checks sync, music and length before handover.
- Fable rates the final before posting; log it with the A/B result in `production/EXPERIMENTS.md` (E2: personal-test
  hook vs contrarian self-correction).

## 6. Aim higher than the last reel
The Fable reel scored emotion 6 and sends 6. Show a real personal stake from the gym in the first 12 s, with one line
a viewer would forward to their gym buddy.
