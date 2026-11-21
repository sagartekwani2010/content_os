# Food tracker reel: finishing in Edits on another Mac

The reel is built on the home Mac by `content_os.pipeline` (cuts, split-screen visuals, captions,
mastered voice, QA). Edits is used only for the last step: licensed or trending Instagram music, and
posting. Nothing needs rebuilding on the second Mac.

## What you receive (AirDrop or private release; never committed to Git)

| File | Use |
|---|---|
| `food_tracker_reel_voice_only.mp4` | Main file for Edits. Picture, captions, mastered voice (-14 LUFS), no music. |
| `food_tracker_reel_full_mix.mp4` | Fallback. Same picture, royalty-free Mixkit bed already mixed and ducked. Post as is if Edits is not used. |
| `CAPTION.txt` | Post caption. |
| `cover.png` | Cover frame. |

## Steps in Edits (about 15 minutes)

1. Import `food_tracker_reel_voice_only.mp4` as a single clip. Do not trim it: cuts and visuals are
   already timed to the voice.
2. Add a track from Edits' music catalog. Set its volume low (about 15-25%) so the voice stays clearly on
   top; duck it further under the hook (first 4 s).
3. Add captions with Edits' auto-captions (they are not burned in). Fix spellings it mishears:
   "Gym Jarvis", "Claude skill", "guardrail", "grams", "Fable 5.2", "matcher agent".
4. Sound effects: Edits' library is higher quality than our synthesized set. Use the clean
   voice-only file and place effects from `SFX_CUES.md` (exact timestamps, type, the word or
   visual each lands on, suggested level). Keep them under the voice.
5. Listen once end to end on headphones.
6. Post from Edits (licensed catalog music only survives when posting from Edits, not in exports).

## Context for a Claude session on that Mac

Clone `sagartekwani2010/content_os`, branch `claude/food-tracker-reel-pipeline`, and read
`CLAUDE.md`, `CURRENT_REEL_CONTEXT.md` and this file. Personal footage, photos and the OpenAI key stay
on the home Mac; Edits finishing needs none of them.
