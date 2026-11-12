# Workout HUD ("Gym Jarvis")

A 9:16 browser heads-up display for one day of training, built with Claude Fable 5.2 on 11 to 12 November 2026.

**State: every value in `app/day.js` is placeholder data.** Nothing on screen may be filmed as real until real
media and logs are analysed and `placeholder` is set to `false`.

## Run it

Open `app/index.html` in Chrome, in a 9:16 window. It scales to fill the window. No build step.

- Tabs: Meals, Exercise, Score, Why, Plan. The three top tiles change with the tab.
- `Run` plays a start-up sequence and then all five sections for Today.
- `Yesterday / Today` switches the day. Left and right arrow keys move between sections.

## Files

| File | Purpose |
| --- | --- |
| `app/index.html` | The whole app: layout, styles, drawing code, animations |
| `app/day.js` | All data, as `window.HUD`. Replace this to load real days |
| `pose/analyse_pose.py` | Side-on lifting clip in; `set-1.mp4` and `pose.json` out (joints, knee angle, torso lean, reps) |
| `pose/photo_pose.py` | Front-facing body photo in; `me.jpg` and keypoints out for Score photo mode |

The pose scripts need `ultralytics`, `opencv-python-headless`, `pillow` and `ffmpeg`, plus `yolo11n-pose.pt`.

## What is and is not true

- The app shows prepared results. It makes no model calls and does not run by itself.
- The form scan has run end to end on a blank test clip only, never on a person.
- Weekly score = 50 x sets done / planned + 30 x progress vs last week + 20 x clean form, computed in the app.
- Proposals are changes to Sagar's own plan that he approves. This is not nutrition or training advice.
- The dark HUD look is a one-off exception to the light editorial system in `config/brand.yaml`.
