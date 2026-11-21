---
name: reel-finish-edits
description: Finish a rendered Content OS reel in the Edits Mac app - Fable-planned transitions, library sound effects, a ducked music bed, frame-exact sections - then master, verify and package it (caption + cover). Use after the pipeline's final render and QA pass, when the creator wants the reel finished, exported or ready to post.
---

# Finish a reel in Edits

Read `production/REEL_DEFAULTS.md` first; it holds the creator's settled choices. Tool-level notes:
`.agents/skills/reel-footage-edit/references/edits-automation.md`. Scripts: `scripts/edits/finish/`.

## Preconditions

- `python -m content_os.pipeline render` and `qa` passed for the reel (`work/render/final/final_clean.mp4`
  exists: picture with burned captions and section cards, mastered voice, no music, no SFX).
- Edits is open, automation is on and `METAPILOT_TOKEN` is set (`launchctl getenv METAPILOT_TOKEN`). After a
  reboot or a token change, ask the creator for the token shown in Edits > Settings > Automation.

## Steps

1. Copy `final_clean.mp4` to the reel's `deliver/` folder under `~/Movies` (Edits cannot read elsewhere).
2. Read the reel's approved `moodboard.json`: its keyframes' `transition_in`, `sfx` and `music` are the
   brief for this plan. Plan with Fable 5.2 (`claude -p --model claude-fable-5-2 --tools ""`): transitions at section changes
   from the Edits catalogue, library SFX titles, and why. Keep the plan JSON next to the reel.
3. `python3 scripts/edits/finish/sfx_anchors.py <cuts.json> <plan.json> <plan_resolved.json>`: SFX times come
   from words and section starts in cuts.json, so they survive speed changes.
4. `scripts/edits/finish/make_bed.sh <clean.mp4> <music> <bed.m4a> <total> <drop_from> <drop_to>`: music
   bed with the twist drop, ducking and fades baked in. Use a licensed-for-use track listed in
   `music/LICENSES.md`.
5. `python3 scripts/edits/finish/edits_build_split.py <clean.mp4> <plan_resolved.json> <cuts.json>`:
   30 fps project, one import, `splitAt` the section times, refuses to continue unless drift is 0.
6. `python3 scripts/edits/finish/edits_finish.py <plan_resolved.json> <cuts.json> <bed.m4a> 0`: imports the
   bed as an audio element and places the SFX, each capped at 2 s and never past the end.
7. Export from Edits to `deliver/`, then master the audio only (video stream copied):
   `ffmpeg -i edits.mp4 -map 0:v -map 0:a -c:v copy -af "aresample=192000,alimiter=limit=0.79:attack=1:release=80:level=0,aresample=48000" -c:a aac -b:a 256k <reel>_FINAL.mp4`

## Verify before showing the creator (all required)

- Length equals cuts.json duration (a long SFX sample can add a black tail).
- Integrated loudness about -14 LUFS, true peak at or below -1 dBTP.
- Lip sync: cross-correlate the voice of FINAL against `final_clean.mp4` at 4+ points; offset under 5 ms.
- Music audible: compare a bass-band level of FINAL against the clean stem while speaking (+2 dB or more)
  and confirm silence through the twist. The OpenAI reviewer is unreliable on music; trust the measurement.
- Frames: section cards, transitions, low captions, ending.
- OpenAI A/V review (`python -m content_os.orchestrator av-review --file ...`), advisory.
- Package: `CAPTION.txt` (short, sassy) and `cover.png` (series name, one hook, face) are present.

## Why this exists

The first Edits pass on 17 Nov 2026 hit, in order: imports landing in reverse (playhead insert), trims
snapping a frame each (lip-sync drift), the music slot not exporting, 7-13 s library samples adding a black
tail, captions over the mouth, and clipping from stacked hits. Each step above is the fix.

## Lessons from the Fable 5.2 reel (19 Nov 2026: footage to final in under an hour)

Run it with `scripts/edits/finish/fable52_prep.sh <reel> <files>` (footage -> cut review) and
`scripts/edits/finish/fable52_finish.sh <reel>` (render -> bed -> SFX -> Edits build -> export -> limiter); generalise
the reel name when reusing.

- **Audio is ground truth for matching.** When the creator rewords or skips lines, rewrite `beats.json` to the spoken
  lines (keep the scripted copy as `beats.scripted.json`), re-run `segment`, and pick the last complete take per beat by
  hand (`work/manual_picks.json` + `pipeline select`). Have Fable 5.2 judge contested beats from measurements.
- **Trim slates and tails at word level** in BOTH `work/takes.json` and `work/scores.json` (cutpoints reads scores):
  drop spoken slates ("Beat 4 final."), repeats after the sentence end, and ASR non-speech tokens (`BLANK_AUDIO]`,
  `CLICK]`, `clears throat)`), which otherwise leave 1-2.4 s of dead air with the creator looking away.
- **Fable's cut judge catches what metrics miss**: 20-40 dB level steps and look-aways at joins came from those tokens.
  Re-run cutpoints -> cut_review -> judge_cuts after every trim; apply its punch-in suggestions (speaker_zoom 1.15).
- **Visuals**: if words changed, use pre-rendered per-beat clips (`visual_clips: visuals`, they hold the last frame)
  rather than re-timing word cues that no longer exist.
- **Show the creator the pipeline render first** (`work/render/final/final.mp4`) while the Edits pass runs; note that it
  has no SFX and only the base music.
- **Levels the creator liked**: bed at -16 LUFS (`BED_LUFS`), SFX about +4 dB over the old defaults (impacts +2, pops
  and whooshes 0 in Edits), limiter after export; final -13.1 LUFS, -1.9 dBTP.
- **Edits export via automation**: `export {path}` then poll `exportStatus` until `state: complete`.
- **Last-minute visual fixes** can be overlaid on the final MP4 (video re-encode, audio copied) instead of a full rebuild.
- **Charts**: show a higher-is-better metric (accuracy, not error) so the winner's bar is taller; never flip data.
- Make the cover from a clean frame of the day's footage (eyes to lens, mouth closed); keep caption credits for any
  third-party clip or CC-licensed photo.
- **Edits caches media by path.** Re-importing a rebuilt `clean.mp4` or `bed.m4a` under the same path played the OLD audio
  (1.1x voice under a 1.15x picture = growing lip-sync drift; old drone bed instead of the new music). Always import
  rebuilt files under a new, timestamped name, then verify sync (speech-band cross-correlation vs the clean render at
  3+ points, < 5 ms) and music presence (bass-band level of FINAL several dB above the clean stem) before handing over.
- **Automatic handover check**: `python scripts/edits/finish/verify_final.py <FINAL.mp4> <final_clean.mp4>` (sync at 3
  points < 5 ms, bass-band music +2 dB over clean, duration match; exit 1 on failure). `fable52_finish.sh` runs it and
  now copies clean/bed under timestamped names on every run and stops polling on `state: complete`.
- **Music the creator wants**: one catchy, beat-driven track (`music_techno_fest_vibes.mp3`) from second 0 to the end,
  bed at -15/-16 LUFS. A slow drone intro read as "not music"; override with `MUSIC=<file>` only on request.
- **SFX density**: about one cue every 2-3 s (36 in 81 s) - pops on key words, whoosh + bassy impact on section cards,
  impact + scratch on the ending stamp. The first pass of 11 was "too few".
- **Pace**: 1.15x for talking-head explainers (1.1x felt slow); set `speed` in cue_sheet.json before render, never after.
- **Before posting**: Fable 5.2 rates the FINAL (frames every 2 s + transcript) on hook, pacing, emotion, clarity,
  value, sends, saves, comments, ending, with predicted drop-off seconds. Log it in `production/EXPERIMENTS.md`.
- **Ad-safe captions (20 Nov)**: the reel was boosted as an ad and low captions crossed the "Visit Instagram profile"
  button. Captions now sit at the seam (`caption_position: seam`); visuals keep their bottom ~100 px empty; chart
  fixes go into the visual clip, not a post-export overlay. Deliver an `_ads` variant if a posted reel used low captions.
