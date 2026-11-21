---
name: form-labeller
description: Label Sagar's workout clips (lift, sets, reps, good/bad set and why) with Claude Fable 5.2 acting as a coach on timestamped frame sheets, to create the reference labels the Workout Analyser is scored against. Use when new workout footage needs labelling, or when the analyser's accuracy needs a fresh reference.
---

# Form labeller skill

This skill produces the **reference labels** for the Workout Analyser (Gym Jarvis Ep 3). It is separate
from the analyser on purpose:

| | Form labeller (this skill) | Workout Analyser |
| --- | --- | --- |
| Model | Claude Fable 5.2 | YOLO pose + Claude Fable 5.2 judge |
| Sees | timestamped frame sheets only | pose keypoints, knee angle, rep table, a few key frames |
| Instructions | coach on the gym floor: is this set good or bad? | compare each rep with the lifter's own best set |
| Output | `demos/workout-hud/data/<clip>/label.json` | `demos/workout-hud/data/<clip>/analysis.json` |

Never give the labeller pose data, and never let the analyser read `label.json`.

## Run

From the repo root:

```
demos/workout-hud/.venv/bin/python demos/workout-hud/label/label_sets.py ~/Downloads/*.MOV ~/Downloads/*.mp4
```

Each clip becomes frame sheets (2 fps for short clips, at most 288 frames for long ones) and one Fable call.

## Limits to state whenever the labels are used

- The labeller and the analyser's judge are the same model, so they can share blind spots. Agreement between
  them is not proof. The creator checks every set where they disagree, and every "bad" set shown in a reel.
- At 2 fps or lower, tempo and fast bounces can be missed; those sets should come back "unclear".
- Footage and derived frames are personal and stay out of Git (`demos/workout-hud/data/` is gitignored).
