# Current Reel context — 15 November 2026

This is the short entry point for Claude Code or Codex working on the current
creator projects. Read `AGENTS.md`, `HANDOFF.md`, `config/brand.yaml`, and
`feedback/VIDEO_LEARNING_LOOP.md` before changing the editorial system.

## Repository boundaries

- **Content OS** (`sagartekwani2010/content_os`) holds briefs, scripts, brand
  memory, production notes, feedback, and the Workout HUD demo.
- **TakeSelect Lab** (`invideo_recreate` locally) is a separate video editing
  and take-selection tool. Its code and tests do not contain the Content OS
  briefs, learning memory, Gym Jarvis demo, or final Reel assets.
- The original personal footage, Edits projects, rendered videos, covers, and
  licensed music live on the creator's machine. They are not reproduced in this
  public repository. Asset names and export details are indexed below.

## Gym Jarvis launch Reel

The final **main** and **trial** exports use the same 51.07-second portrait
picture and selected `IMG_3470.MOV` narration at **1.2×, pitch preserved**.
The wrong Why screen near 19 seconds and five blank opening frames were
repaired. The Gym Jarvis title is a separate, prominent beat; the opener starts
with the Anthropic line. The visuals show meal photo analysis, set analysis,
body-part score, evidence-backed decision, and a next-day plan that waits for
approval. Keep the product screens as the visual hero and Sagar's face brief,
preferably at the start or end.

The main export uses **Mixkit Techno Fest Vibes**, clean phrase captions, and a
Gym Jarvis title cover. The trial uses **Memory Reboot** from Edits' licensed
catalog, word-highlight captions, and a set-scan cover. Check track availability
on the posting account. The user reported that the main Reel had more traction
than earlier Reels, while the trial performed poorly; there are no comparable
reach, watch-time, or follow metrics here, so do not infer why.

See `outputs/gym-jarvis-launch/` for delivery notes, captions, and the take
map. The actual local exports, when present on the creator's machine, are
`outputs/gym_jarvis_main_reel.mp4` and `outputs/gym_jarvis_trial_reel.mp4` in
the November 12 Codex editing workspace. Original visuals also exist in the
local Edits project. These media paths are a locator, not a claim that GitHub
has the files.

The Workout HUD source is in `demos/workout-hud/`. Some current meal and body
visuals refer to local `app/media/*.jpg`, which are ignored; a fresh clone will
need creator-provided media or suitable replacements. HUD values are demo
examples, and the creator explicitly declined adding a spoken "demo data" line
to the launch Reel. Do not turn screen examples into claims of measured personal
training outcomes.

## Agentic AI learning-mission Reel

**Status: posted, and judged poor by the creator.** After the v3 selects cut
(`outputs/agentic-ai-mission/manifest_v3.json`), a Claude Code session rebuilt
the reel in Edits through eight versions; the final project is "Agentic AI
mission reel v7 (60s)", 63 seconds at 1.25×. The creator posted the Edits
export, which had unmastered voice and no music, and found the result looked
like an interview extract with abrupt cuts and no clear purpose. The measured
causes and candidate rules are in
`feedback/learning-mission-final-edit-diagnosis-2026-11-15.md`. Do not reuse
this reel's method. The paragraphs below describe the intended argument and
remain useful if the reel is re-recorded.

Source recording: `IMG_3479.MOV`.

The full thought sequence is: people ask how to start AI; first, too much
content; second, IG/YouTube advice is often theoretical for building real-world
AI systems; third, rapid model releases derail learning; fourth, no clear
roadmap. Sagar relates to those problems from his own start, with layoffs
adding pressure. What works for him is deep personal interest and time spent
researching/building, which he recognizes is not possible for everyone. He
started the IG page to make AI learning more structured through real examples.
Short Reels show pieces, not the full journey. He is working with companies on
structured learning solutions and will share details in a few weeks. Meanwhile
he will continue breaking down AI concepts. The next Reel shows how Gym Jarvis
estimates protein and calories from a meal photo.

Select complete, camera-facing deliveries even when a later take is preferred.
Inspect gaze throughout each retained phrase, listen at every cut, and verify
the words in the rendered assembly. Use a visual card or pickup only where the
recording does not supply a usable camera-facing line. Do not fabricate spoken
words from an on-screen caption. See the dated feedback for exact corrections.

## Production system revamp (decided 15 November 2026)

No new reel is produced until the staged pipeline in
`planning/reel-production-system-blueprint-2026-11-15.md` is built: brief,
script and beat sheet, shoot plan, take selection, edit, quality gate. The
60-second cap is dropped. Recording changes to line-by-line or voiceover-led
(`production/RECORDING_KIT.md`). Each reel ends as one finished file with
mastered voice, sound effects and music. Edits stays the editor for now; what
was learned driving it is in
`.agents/skills/reel-footage-edit/references/edits-automation.md`, with helper
scripts in `scripts/edits/` that still need a first test run. Work is moving
to the creator's home Mac; see `production/SETUP_NEW_LAPTOP.md`. Three
decisions are open: voiceover-led or talking head, which reel goes first, and
the music source.

## Current series direction

The creator plans several weeks of Gym Jarvis and agentic-concept Reels,
starting with the food tracker. A structured Agentic AI learning offer is being
developed, but the mission Reel should introduce it subtly and avoid promising
a launch date or calling it a completed course. The mission is to help people
learn through real builds that improve their lives.

## Production memory and evidence

Keep each Reel's review and performance evidence in dated `feedback/` files;
only promote creator-approved or repeated lessons into `config/brand.yaml`.
`feedback/gym-jarvis-music-transitions-review-2026-11-12.md` is a **pre-VO
review** and must not be mistaken for the final export. The November 15
feedback records the later changes and the learning-mission selects review.
