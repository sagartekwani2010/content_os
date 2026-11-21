# Gym Jarvis form coach (Ep 3 giveaway)

What this is: the "coach" half of my Workout Analyser. Claude Fable 5.2 watches timestamped frames of one of your
sets, like a coach on the gym floor, and says good / bad / unclear, with the rep and timestamp of each problem.

- `SKILL.md`: the Claude skill (drop it into `.claude/skills/form-labeller/`).
- `label_sets.py`: turns a clip into frame sheets and asks the model. Needs Python, Pillow, ffmpeg and Claude Code.
  Run: `python label_sets.py my_set.mov`
- `architecture.png`: the full system from the reel (pose -> rep maths -> safety check -> judge + coach -> verdict).

Limits: phone video from one angle; it can miss tempo at 2 frames per second; it is not a coach or a doctor,
and this is not training advice. In my 23 sets the coach and the judge agreed on 9 of the 16 sets both could judge.
