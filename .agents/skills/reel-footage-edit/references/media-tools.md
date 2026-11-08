# Media tool routing and export checks

## Edits MCP: primary local editor

Use Edits' local Automation Server for footage review and the editable timeline. Its MCP endpoint is configured on the host; credentials belong in the host's secret store or environment, never in this repo. If tools are not visible in the current chat, a fresh Codex session may be needed after MCP configuration.

- Inspect: `probeMedia`, `transcribeClip`, `frameSheet`, `sampleFrames`, `detectCuts`, `detectSubjects`, `clipMetadata`, `findPauses`, `quietPoint`, `audioLevels`, `loudness`.
- Assemble: `newProject`, `importToMediaBin`, `addMedia`, `splitAt`, `trim`, `slipClip`, `move`, `reorderClip`, `saveProject`.
- Finish: `addOverlay`, `addText`, `setTextStyle`, `setTextPosition`, `addTransition`, `setSpeed`, `setVolume`, `setDucking`, `setFade`, `generateCaptions`, `editCaption`, `splitCaption`, `setCaptionStyle`.
- Review/export: `previewVideo`, `previewVideoStatus`, `captureFrame`, `captions`, `getCanvas`, `export`, `exportStatus`.

Check live tool schemas and capabilities before calling them. Use a new project for experiments; do not modify the creator's existing project just to test a connection. A local editor state is not proof of a valid deliverable: review the rendered video and its metadata.

## InVideo MCP: optional generated and browser NLE work

Use a dry run and a per-run credit ceiling before starting. Record the actual
charge, project URL, model and generation ID in the review log. Keep the scope
to the selected shot; the creator handles fal.ai runs separately.

Use InVideo for generated B-roll, rough visual variants, captions, or browser NLE tasks when that materially improves the cut. Send it the exact approved narration, shot duration, vertical aspect ratio, and visual constraints. Keep the narration/take map authoritative. Avoid generating a full video from a prompt when the task is to edit the creator's actual performance. Inspect the account's available tools and credit impact before a paid generation.

## Magnific MCP: selective visual enhancement

If the live model catalog or pricing cannot be read, do not start a paid run.

Use Magnific for a chosen hero frame, cover, or asset that needs upscaling or detail work. Check balance and current model cost before generation. Its MCP generation and upscaling consume credits even if the web plan labels some operations unlimited. Do not batch every frame merely to use an allowance; spend on approved assets with a clear role in the edit.

## Portable delivery target for Instagram Reels

- Vertical 9:16, typically 1080×1920, constant 30 fps.
- MP4 with H.264 video, yuv420p, Rec.709 SDR metadata; AAC-LC stereo audio at 48 kHz; fast-start metadata (`moov` before `mdat`).
- Decode the entire export and inspect first/middle/last frames, captions, and audio. Do not infer compatibility from the `.mp4` extension alone.
- Retain the high-quality master if a platform-compatible re-encode is needed.

Run the repo's read-only verification command on the rendered file:

```bash
.venv/bin/python -m content_os.tools.video_delivery /absolute/path/to/reel.mp4 --decode
```

It reports codec, color, audio, fast-start atom order, and full-decode errors
as JSON. Then watch the whole video for editorial issues that metadata cannot
detect.
