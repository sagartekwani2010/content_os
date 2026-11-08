# Diwali flight Reel: edit retrospective

## Evidence

The creator supplied four vertical takes (`IMG_3400.MOV`–`IMG_3403.MOV`), a salary chart, three-tier pyramid, level videos, and music. The compatible final export is `/Users/sagart/Documents/Codex/2026-11-05/ca/outputs/diwali-agent-reels-compatible.mp4` (about 81.9 seconds). The precise source in/out map is `/Users/sagart/Documents/Codex/2026-11-05/ca/work/diwali_edit/clean_cta/edit_map.tsv`. These local files are evidence, not repo assets.

| Early problem | Reusable correction |
|---|---|
| Opening missed “what gets you 90 LPA,” and the salary take was weak | Find and compare exact source lines before assembly; trim the lead-in to the approved hook. |
| Case, L5 B-tier, L6 A-tier, L7 policy, and CTA were incomplete or out of order | Make a beat checklist, then select complete alternate takes with source timecodes and reasons. |
| Long pauses, wandering gaze, looking down, and jerky joins remained | Remove these by default; inspect words and nearby frames before cutting, and bridge difficult joins with purposeful visuals. |
| Runtime pressure made the story rushed | Build the full 1× narration cut first, then test creator-approved speed such as 1.15×. Preserve every essential point even if the cut exceeds a target. |
| Level videos, pyramid tiers, and salary bars missed their spoken cue | Time graphics to the actual line; reveal tiers progressively and hold level tags for their explanation. |
| An extra-budget card appeared despite no spoken mention | Keep on-screen facts within the recorded narration. |
| Captions, music, and first export passed only a superficial review | Check caption collisions and one-to-two-line breaks; mix music audibly under clear speech; inspect full decode and codec metadata. |

The first Reels file did not load. It had 96 kHz AAC and HLG/BT.2020 metadata; the fixed export uses H.264/yuv420p, Rec.709 SDR, AAC-LC at 48 kHz, 1080×1920 at 30 fps, and fast-start MP4. The initial music mix used `amix` normalization that lowered both tracks; turning normalization off restored the intended audible bed.

The pause-removal log `/Users/sagart/Documents/Codex/2026-11-05/ca/work/diwali_edit/fast_tier/removed_pauses.tsv` records 18 removals. Detection used -32 dB for 0.18 seconds; only gaps at least 0.38 seconds were removed, retaining 0.08 seconds at each edge. These were recording-specific settings, not a universal cut rule.

## Default for future creator footage

Inventory and transcribe all takes. Compare completeness, delivery, gaze, and audio; log exact source ranges. Assemble all required ideas at 1×. Remove dead air and off-camera distractions. Check every join. Lock narration before choosing the minimum useful B-roll. Time captions and graphics to the final words. Verify the actual render and preserve the editable project plus cut map.
