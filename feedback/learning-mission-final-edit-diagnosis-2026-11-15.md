# Agentic AI learning-mission Reel: final edit and diagnosis (15 November 2026)

Follows `gym-jarvis-and-learning-mission-2026-11-15.md`, which ends at the v3 selects cut. This record
covers the Claude Code session that took the reel from v3 to a posted version, the creator's verdict,
and the measured causes. It is a review record, not an approval.

## What was produced

- Tool: Edits Mac app driven through its local automation server, with ffmpeg for checks and mastering.
- Source: `IMG_3479.MOV` (47 minutes, iPhone, HDR), plus the Gym Jarvis launch reel for B-roll.
- Eight versions in one session: 1:43 at 1.0x, then 1.1x, 1.2x, and a rebuilt 58-63 second cut at 1.25x.
- Final Edits project: "Agentic AI mission reel v7 (60s)", 63 seconds, 27 clips, word-highlight
  captions, animated titles and labels, real screenshot cards (two creator DMs cropped to the text,
  Qualcomm layoff headlines, a model-release list), Gym Jarvis meal-scan footage under the closing line.
- Music in the project: two licensed catalog tracks. They are not present in any exported file.
- The creator posted the Edits export directly: unmastered voice (about -18 LUFS) and no music.

## Creator verdict

"It looks like an interview extract and not a unified reel." Cuts are abrupt, the reel did not feel
powerful, and it served no clear purpose. The creator dropped the 60-second requirement and asked for a
full system revamp before any new reel.

## Measured causes

| Area | Evidence |
|---|---|
| Footage not shot to be cut | 47-minute single recording, about 19 minutes of speech for roughly 80 seconds of script; read from a clipboard with frequent mid-sentence restarts |
| Fragment edit | 27 clips in 63 s (2.3 s average). Of 26 joins: 4 continuous speech, 12 take changes (some 15 minutes apart), 10 restart or pause removals inside a thought |
| Subject movement | Face position (Edits `detectSubjects`) jumps up to 13% of frame width at cuts and drifts up to 16% inside single clips. The camera was fixed; the swivel chair was not |
| Mismatched takes | Raw voice level differs 6-8 dB between takes; eyes go to the clipboard in most later takes |
| Script written to be read | Long formal sentences that could not be delivered in one breath from memory |
| Edit choices | No face alignment at cuts; punch-ins of about 12%; four visual styles stacked (DM bubbles, white news cards, cyan HUD, yellow titles); dark screens used to hide head turns, removing the face for about 10 s; speed raised to 1.25x |
| No single job | The reel names a problem, gives background, teases a course and teases the next reel, and resolves none |
| No finished file | The project had music but quiet voice; the mastered copy had loudness but no music |
| No listening step | Claude cannot hear audio; every sound judgment came from transcripts and level meters |

The original brief said "voiceover led, minimal face time". The footage was a full talking head and the
edit followed the footage instead of flagging the mismatch.

## Corrections during the session (before → after → why)

- Full-screen navy cards over the speaker → animated labels and titles with the speaker visible →
  the cards read as slides. Evidence: about 22 s of the v3 cut was a flat card.
- "Advice is largely theoretical" alone → restored "…from people who themselves have never built a
  real world AI system" → the softened line lost the point.
- 16 kHz stitched closing line → rebuilt from the 48 kHz source → audible quality drop at the end.
- HDR source rendered without conversion (washed out) → Edits project set to SDR → correct colour.
- Cold-open repeat of the question → removed at the creator's request → made the reel longer.
- Generated LinkedIn DM screenshots were requested and declined → real message text only, cropped,
  with dimmed copies for scale → invented messages would be shown to viewers as real.
- Take-to-take voice level left as recorded → per-clip gain matching → last lines were 5-7 dB quieter.

## Candidate rules (not yet approved for `content_learning_memory`)

1. One promise per reel, stated in the brief, with a takeaway the viewer can use the same day.
2. Record line by line or voiceover-led; never one long read-through. See `production/RECORDING_KIT.md`.
3. No mid-sentence splices. A beat without a clean whole-sentence take goes back for a re-record.
4. At every cut the face is aligned, or the framing changes clearly (new angle, or a punch-in the
   viewer reads as deliberate). Measure the jump; do not judge it from a contact sheet.
5. B-roll is planned in the beat sheet. It is never added to hide a problem in the footage.
6. One text system on screen: at most two text layers at once, one card style for all screenshots.
7. Lock the main track before adding overlays; in Edits a later ripple desynchronises every layer.
8. Deliver one finished file with mastered voice, sound effects and music in it, and have the creator
   listen to that exact file before it is called done.
9. Choose speed once, up front, from words per minute; do not raise it to hit a duration.

## Open items

- Decide voiceover-led versus line-by-line talking head for the next reels.
- Decide the first reel to run through the new pipeline (food tracker is already teased).
- Choose a music source that can be mixed into the exported file.
