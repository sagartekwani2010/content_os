---
name: form-coach
description: Watch a video of one of your gym sets and judge it like a coach on the gym floor (lift, sets, reps, good / bad / unclear and why, with rep numbers and timestamps). Use when you share a workout clip and ask whether the set was good.
---

# Form coach skill (Gym Jarvis Ep 3)

1. Run `python label_sets.py <clip>` from this folder. It samples the clip at 2 frames per second (fewer for long
   clips), tiles the frames into timestamped sheets and asks Claude to judge them as a coach.
2. Read `form_coach_out/<clip>/label.json`: lift, camera view, each set's start/end, reps, verdict, issues
   (what, which reps, a timestamp that shows it) and a coach note.
3. Show the user the verdict and the one thing to fix next set. Say "unclear" rather than guessing.

## Limits
- One phone angle; joints hidden by a machine or the camera angle can fool any vision model. Check a "bad" verdict
  on the footage yourself before changing anything.
- At 2 frames per second, fast bounces and lowering speed can be missed.
- Not a coach, physio or doctor. Not training advice.
