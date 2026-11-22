# Reel defaults

Settled by the creator while producing the food-tracker reel (16-17 November 2026). Every new reel starts
from these; change one only when a reel genuinely needs it, and record why in that reel's folder. Pipeline
and visuals code carry these as defaults where they can.

## Positioning and hooks (18 Nov 2026)

- Positioning: the creator builds AI agents for a living and tests them on their own training and food.
  Lead with a test only they can run, or advice from having done the work.
- Beat 1 stops a stranger in 1.5 s (number, conflict, claim); never a recap of an earlier episode;
  "Ep N" lives on the cover only. Show the product or result within 8 s; re-hook at 1/3 and 2/3.
- Every beat carries a target viewer emotion, a face/voice delivery cue and a continuity note; the arc
  moves (e.g. fear -> curiosity -> surprise -> hope -> pride).
- Three hook variants per reel, each on a different emotion, tested as Instagram Trial Reels before
  the main post.
- One idea, 40-60 s; one save asset; one honest comment trigger; end on a loop or payoff, not "next up".
- Fable 5.2 writes; Opus 5.5 checks emotion and hooks at the script and the visual-plan phase
  (`SCRIPT_CHECK.md`, `VISUALS_CHECK.md`); Fable revises once from the notes.

## Screenplay -> mood board -> everything else (18 Nov 2026)

- Every reel starts as a screenplay (scenes, exact lines, emotion curve, hook map with 4+ hooks in
  55 s, real demos, reason-to-use), written by Fable 5.2 and checked by an independent panel (Opus 5.5,
  12 Indian viewer personas incl. finance, consulting, marketing). Fable revises from the panel.
- Then a mood board with keyframes (`moodboard` stage, Fable 5.2): palette, type, texture, music, SFX,
  pacing, one keyframe per visual change (layout, shot, drawing, on-screen text, motion, transition,
  sound, creator direction) and the shot list. The creator approves `MOODBOARD.html` at the
  `moodboard` gate.
- **The mood board is a playable page, not a static plan (creator standard since 20 Nov 2026, Ep 3).** Before the
  shoot, render the real visuals first, then build `<reel>/MOODBOARD.html` with
  `python scripts/moodboard/build_moodboard.py <reel>/moodboard_spec.json` (example spec:
  `outputs/workout-analyser-reel/moodboard_spec.json`). It must contain, in order: cover + one-line flow + key measured
  numbers; an animatic (every visual concatenated in story order); 3-7 music previews, each laid under the same
  animatic with the track's biggest drop placed on the reel's key moment and its measured energy lift, one marked
  recommended; every visual clip playing with its beat, length and data source; palette and type; a sound-design table
  (moment, SFX, level). Open it in Chrome for the creator. Licensed music candidates go in `music/candidates/`
  (gitignored) with their licence noted in `music/LICENSES.md` once chosen; personal footage renders stay gitignored.
- **The mood board always carries full-length previews with a dummy voice (creator, 20 Nov 2026).** Before the shoot,
  render MAIN and TRIAL end to end with `python scripts/shoot/make_preview.py <script.md> <visuals_dir> <out_dir>
  --section MAIN|TRIAL ...`: the spoken lines in a temporary TTS voice at the edit speed, every visual at final timing,
  seam captions, SFX and each music option, with a "YOUR TAKE" placeholder in the bottom half. Put the previews at
  the top of `MOODBOARD.html`. Library songs (Instagram/Edits catalogue) cannot be in exported files: build that
  version as an Edits project and say so on the board.
- The approved screenplay and mood board drive the beat sheet/teleprompter (shot list and keyframes in
  SHOOT_PLAN.md), the visuals (draft-spec follows each beat's keyframes), the edit and Edits finishing
  (transitions and SFX from the keyframes), and the final video. Deviations are noted in the reel folder.

## Rhythm and final review (19 Nov 2026)

- Alternate emotion and hook beats: emotion -> hook -> emotion -> hook (small deviations allowed). Label beats E/H in the
  beat sheet; no two hook beats or two emotion beats in a row without a reason.
- Fable 5.2 judges the script's structure before recording, and the final MP4 (frames + transcript) before posting; act
  on reorder suggestions (e.g. moving a strong section earlier).

## Script and recording

- One short sentence per beat; the top-half diagram carries the detail.
- The recorded audio of the chosen takes is ground truth: script files, captions and visuals follow what was
  said. Numbers on screen must still come from measured facts.
- Teleprompter: full-screen Chrome page, one beat per screen; say "beat N", 2 s between attempts; the last
  complete take after the last "final" call is used.
- Mic check before every shoot (5 s recording played back); the first check on arrival is the audio level.
- Landscape, back camera, 4K, HDR off, fixed chair.
- Continuity: reset to a base pose (hands resting together) before every take; hold 1 s on the lens
  before and after each line; start each beat at the previous beat's ending energy; gestures mid-line
  only; same clothes, light and chair in one sitting. The teleprompter shows FEEL / FACE-VOICE / POSE
  per beat. The take and cut judges reject cuts with visible pose, hand or energy jumps.
- Vary the bottom half deliberately: punch-ins, lean-ins and, where the story allows, other shots
  (gym floor, screen recordings) rather than one pose for the whole reel.

## Edit

- Playback speed 1.1x, pitch preserved; the cold open and the twist/punchline beats stay at 1.0x.
- Cold open with the most surprising moment; section changes marked by a full-frame title card (dark
  background, huge condensed uppercase, quick punch-in) with a whoosh in and a bass impact on landing.
- Name lower-third (creator, 22 Nov 2026): whenever the creator introduces himself on camera ("I'm a lead AI
  researcher…"), show a two-line lower-third: **Sagar Tekwani** on top and **AI Researcher** below it in smaller
  type. It lands on the intro line and holds for the whole line, placed above Instagram's bottom UI zone.
- Visuals land on or ~0.25 s before the word; a concept appears big first, then its detailed diagram; two or
  more scenes per beat when a line carries two ideas; results shown as dashboards; no visual gap over ~2 s.
- End on the payoff or a loop back to the opening. A next-episode tease goes in the caption or a
  final second over real footage, never as a "next up" card that signals the end.

## Post caption and cover (20 Nov 2026)

- Terms: "caption" means the Instagram POST CAPTION (CAPTION.txt, the text under the reel); burned-in text is
  "subtitles". Fable 5.2 writes the post caption, the pinned comment and 3 cover headlines (and picks one) from the
  final script + facts sheet; every claim must be in the facts. The first ~125 characters must stop the scroll.
- Cover: a real frame of the reel's key moment, headline readable inside the 3:4 profile-grid crop (centre 1080x1440).
- Comment keyword => DM kit before posting (20 Nov 2026): `<reel>-deliver/dm_kit/` with DM_REPLY.txt (full reply incl.
  the deliverable), DM_SHORT.txt, the deliverable file (e.g. COACH_PROMPT.txt), one attachable 4:5 image and README.txt.
  Fable 5.2 writes it from the facts sheet. Never post a keyword CTA with nothing ready to send.

## Captions (burned-in subtitles)

- Always burned in by the pipeline: 2-4 words, one line, white with a dark outline, spelling from the
  confirmed spoken line.
- Placed at the seam between the visual panel and the face (`caption_position: seam`), from 20 Nov 2026.
  Why: the reel ran as an Instagram ad and the low captions sat under the "Visit Instagram profile" button;
  Meta keeps the bottom ~35% of a Reels ad for its UI, and that line runs through the creator's mouth, so
  nothing below the face panel's top is ad-safe. The organic Ep 2 / Fable 5.2 posts used `bottom_safe`.
- Visuals keep the bottom ~100 px of the 960 px visual panel empty (the seam caption band, y 877-1043 in a
  1080x1920 frame): no credits, footnotes or labels there. Check with a band scan before rendering.
- Put chart or figure fixes into the beat's visual clip, never as an overlay after export (an overlay
  covers the burned-in captions).

## Audio

- Voice mastered to -14 LUFS integrated, true peak at or below -1 dBTP.
- Music bed clearly audible: about -18 LUFS before ducking, roughly 10 dB under the voice while speaking,
  swelling in pauses; silent through the twist; 1.5 s fade at the end.
- Sound effects audible: hits about 0 dB, whooshes and pops -4 to -6 dB (Edits volume scale); each effect
  capped at about 2 s and never past the end of the reel.

## Finishing in Edits

- Fable 5.2 plans the transitions and library sound effects; quick-pan or zoom at section changes, a short
  flicker into the twist, a light wipe out of it.
- Import from `~/Movies`; seek before each import; import the pre-mixed music bed as an audio element (the
  Edits music slot does not export); no Edits captions when the pipeline burns them in.
- See `.agents/skills/reel-footage-edit/references/edits-automation.md` for the tool-level notes.

## Packaging (mandatory)

- Post caption: short and sassy, not a summary of the video, with a small "not nutrition advice"-style
  disclaimer where relevant.
- Cover: plain and simple: series name, one hook, the creator's face; key content inside the 3:4 grid crop.
- Series features get names that pair (Meal Analyser / Workout Analyser).

## Review

The creator reviews one end-to-end export. Before it is shown: frame check of every beat, sync, length,
loudness and true peak, transcript of the render against the spoken lines, and the OpenAI A/V review.

## Visual tools

Which tool for which beat (Manim, Anidoodle, Lemo Opuscar, real-page screenshots, HTML stills) and how to install a new one:
`production/TOOL_DISCOVERY.md`. Update it whenever a tool is tried.

## Skills that carry these defaults

- `reel-orchestrator` (`.claude/skills/reel-orchestrator/`): runs a reel from idea to post-ready, with the
  creator's gates, feedback backtracking and lesson memory.
- `reel-finish-edits` (`.claude/skills/reel-finish-edits/`): the Edits finishing pass, its scripts in
  `scripts/edits/finish/`, and the verification list.
- `food-tracker` (`.claude/skills/food-tracker/`): the Meal Analyser itself.
