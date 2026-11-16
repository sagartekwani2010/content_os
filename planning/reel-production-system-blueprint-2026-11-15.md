# Reel production system blueprint (15 November 2026)

Status: proposed after the learning-mission reel review; not yet built. It extends what Content OS
already has (briefs, `reel-script-writing`, `reel-footage-edit`, the video learning loop) with the
stages and gates that were missing. Evidence is in
`feedback/learning-mission-final-edit-diagnosis-2026-11-15.md` and
`research/short-form-production-practices-2026-11-15.md`.

## Why the existing skills were not enough

`reel-footage-edit` already says to cut at sentence boundaries, remove off-camera gaze and listen at
every join. The learning-mission edit still failed, because:

- nothing upstream stopped a recording that could not be cut that way;
- the rules were prose, with no measurement that could fail an edit;
- there was no beat sheet tying each line to a planned visual, so B-roll became a patch;
- there was no single finished file, and no required listen by the creator.

## Pipeline

| Stage | What happens | Output | Gate | Skill |
|---|---|---|---|---|
| 1. Brief | One promise, audience, same-day takeaway | `briefs/<id>.yaml` | Creator approves | existing brief flow |
| 2. Script and beat sheet | Spoken-language script split into beats; each beat names its visual; hook and payoff written first | `outputs/<id>/beats.json` | Creator approves | `reel-script-writing` (extend) |
| 3. Shoot plan | Teleprompter text per beat, B-roll shot list, recording checklist | `outputs/<id>/shoot_plan.md` | Creator records | new `reel-shoot-plan` |
| 4. Ingest and take selection | Word-level transcript, takes matched to beats, each take scored, whole-sentence takes only | `outputs/<id>/selects.json` | Weak or missing beats go back for a re-record | new `reel-take-select` |
| 5. Edit in Edits | Timeline built from the selects with fixed recipes | Edits project | Automatic checks | `reel-footage-edit` (rewrite sections 2-4) |
| 6. Quality gate and delivery | Measured checks, creator's listen-through, export, master with music, caption, cover | One finished MP4, caption, cover | Creator signs off | new `reel-quality-gate` |

## Elements

1. **Skills, one per stage**, each with scripts, so a stage follows a recipe instead of improvising.
2. **Script library** (`scripts/edits/`): Edits connection and helpers, mastering and music mix. To add:
   face-jump, loudness and words-per-minute measurement; cover builder.
3. **Design system** (`config/design.yaml`, to write): one font pairing, one palette, one caption style,
   one card style for all screenshots, screen zones and Instagram safe areas, at most two text layers
   at once, the agreed punch-in size and cadence.
4. **Edit rules that can fail an edit:**
   - no mid-sentence splices;
   - at every cut the face is aligned or the framing clearly changes;
   - B-roll appears only where the beat sheet planned it;
   - speed is fixed up front from words per minute;
   - the main track is locked before overlays are added.
5. **Take scoring:** eye contact, face position against a reference frame, voice level, fluency.
6. **Quality gate report:** biggest face jump at a cut, clips under two seconds, loudness per section,
   seconds with no face on screen, caption errors, transcript against script. Then the creator listens.
7. **One finished file:** picture, voice and sound effects from Edits; `scripts/edits/master.sh`
   masters the voice and mixes a music file from `music/`. What is checked is what is uploaded.
8. **Recording kit:** `production/RECORDING_KIT.md`.
9. **Learning loop:** unchanged; each reel still gets a dated `feedback/` record, and only approved or
   repeated lessons enter `content_learning_memory`.

## Keeping agent usage down

- New session per reel, started from the reel's files, not from chat history.
- Routine steps run as scripts; model judgment is spent on script and edit decisions.
- Approval happens at the brief and beat sheet, where changes are cheap.

## Decisions (16 November 2026)

- **Editing:** ffmpeg plus an editor. The selects/EDL file is the source of truth; ffmpeg renders a
  measurable draft first; the editor (Edits) is used for finishing. Once a project is open in the
  editor, change it in place rather than regenerating it.
- **Transcription:** local whisper.cpp by default. Keep a provision for the OpenAI transcription API
  behind one interface (`engine: whisper_cpp | openai`), with the key read from `OPENAI_API_KEY` in the
  environment and never written to a file. The OpenAI engine uploads the voice, so it is opt-in per reel.
- **Recording:** iPhone, front or back camera, with a teleprompter (see the shoot-plan stage below).
- **First reel through the pipeline:** the food tracker reel.
- Still open: format (voiceover-led or line-by-line talking head), music source, and whether to trial a
  DaVinci Resolve MCP after two or three reels (it needs Resolve Studio for scripting).

## Pipeline changes adopted from public editing pipelines

Sources compared on 16 November 2026: Built to Click video-editing-playbook, browser-use video-use,
ghost-editor, Takes for Mac, OpenMontage.

1. **Line-by-line recording from the beat sheet.** The shoot plan gives one teleprompter card per beat.
   Each line is said two or three times with a short pause; no slate is needed because selection
   matches by words.
2. **Mechanical take selection.** Match takes to script lines by words, never by timecodes; default to
   the last complete take; cut points from the waveform with 40 ms lead-in and 80 ms tail; 30 ms audio
   fade at every cut. A line with no clean take goes back for a re-record.
3. **The agent reads transcripts, not video.** One packed transcript file per reel, plus a filmstrip,
   waveform and words image only at decision points (retake comparisons, cut checks).
4. **Cut-review gate.** A page with a frame at every cut and the face-jump numbers, approved by the
   creator before captions, music or B-roll are added.
5. **Self-check before the creator sees anything.** Check every cut boundary and the render (ffprobe,
   black frames, -14 LUFS integrated, no clipping, captions present, transcript against script); fix and
   re-render at most three times. Then the creator listens to the exact file that is posted.
6. **Gates enforced in `cli.py`.** A stage cannot be marked complete without a recorded approval.
7. **One cue sheet** drives picture, sound effects and music; a style recipe lives in
   `config/design.yaml`.

## Build order

1. Home laptop set up and Edits reachable (`production/SETUP_NEW_LAPTOP.md`).
2. Open decisions settled.
3. `config/design.yaml`, then the skills in pipeline order.
4. `scripts/edits/edits_helpers.py` and `master.sh` proven on a ten-second test timeline. They are
   collected from inline scripts that worked on 15 November but have not run as files.
5. First reel through every stage; where it fails, fix the system, not the reel.
