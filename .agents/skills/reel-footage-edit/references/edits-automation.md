# Edits automation notes

What was learned driving the Edits Mac app (bundle `com.burbn.basel.mac`, version 455) through its local
automation server on 2026-11-15. Read this before the first Edits call in a new session.

## Connecting

- The server runs at `http://127.0.0.1:19501/mcp` while Edits is open. It speaks JSON-RPC
  (`initialize`, `tools/list`, `tools/call`) and needs `Authorization: Bearer <token>`.
- The token is shown in Edits under **Settings > Automation > Access token**. Set it once per login with
  `launchctl setenv METAPILOT_TOKEN <token>`; `scripts/edits/mcp.py` reads it from the environment or from
  `launchctl getenv`. Never write the token into a file or a commit. This repository is public.
- If Claude Code's own `edits` MCP entry fails to connect (Edits was closed at session start, or the
  variable was missing), use `scripts/edits/mcp.py` directly: `python3 mcp.py list` prints all tools.
- `getCapabilities` and `listCatalog` describe conventions and the transition, effect, text and caption
  catalogs. Canvas coordinates are normalized 0-1 from the top left; x/y is the element centre.

## Files

- Edits is sandboxed. It cannot read Downloads, Desktop, Documents or `/tmp`. Copy media into
  `~/Library/Containers/com.burbn.basel.mac/Data/Documents/<reel>/` (`cp -c` clones without using disk)
  and import from there. Exports must be written there too, then copied out. `media-tools.md` records
  a second route that also worked: a hard link under `~/Movies/Edits/Import Staging/`.
- iPhone footage recorded in HDR (HLG) makes the project HDR. Call `setProjectDynamicRange` with `sdr`
  after the first import. Better: record with HDR off.

## Building a timeline

- `addMediaPanelItemsToTimeline` with `sourceIn`/`sourceOut` appends a trimmed clip to the main track.
  Add `asOverlay` and `startTime` to place B-roll or image cards on overlay tracks.
- The main track is magnetic: trimming, inserting or changing speed ripples every later clip. Overlay
  tracks are free and do **not** move, so any change to the main track after overlays exist means
  remapping every overlay, text, sound effect and music cue. Lock the main track before adding layers.
- `transcribeClip` on the library item gives word-level timings for a whole recording (47 minutes took
  about a minute). Use these, not rough transcripts, to place cuts between words.
- `detectSubjects` with `aliasId` returns face boxes at source times; use it to compare face position
  across a cut. `quietPoint` finds the quietest instant near a time.
- `trim` deltas are in source seconds for clips with a speed change. A `trim` straight after a `move`
  sometimes lengthens the element; always re-read with `getElement` and trim again.
- `addText` does not always honour `atSeconds`; move the element to its start afterwards and check.
- `applyTextPreset` needs `ids` (a comma-separated string), not `id`.
- Layer order follows creation order (later = on top), and text may reuse an older, lower track.
  Create scrims first, then B-roll and cards, then text, then captions. `moveToLayer` fixes strays.
- `setTransformKeyframes` takes clip-relative times and keys `time, x, y, scale, rotationDegrees`.
- `processAudio` replaces a clip's media even with an empty chain and is not undone by `undo`.

## Look that worked

- Titles: preset `Super serious`, white plus `#FFD23F`, animation `fligPop`.
- Labels: preset `None`, font `HelveticaNeue-CondensedBold`, emphasis `backgroundPill` `#0B1020EE`,
  animation `fligZoomBox`. `fligCaptionSlide` clips pill text; `typewriter` and `fadeIn` are slow.
- Captions: style `Word Highlight Box`, highlight `#FF5A36`, y 0.775.
- Transitions used: `transition_slide_left`, `transition_blur`, `transition_exposure`,
  `transition_zoom_in`, `transition_dissolve`, `transition_fade` (end). `transition_light_wipe` is pink.

## Sound

- Sound effects from `searchSoundEffects` are included in exported files.
- Licensed catalog music plays in the project and when sharing to Instagram from Edits, but is silently
  left out of exported files, and the app refuses a manual download while it is on the timeline.
  Royalty-free "full file" tracks failed to download on 2026-11-15 (DownloadError 3); retry before
  assuming that is permanent.
- Edits has no usable master limiter. Exports measured about -18 to -20 LUFS. Finish audio outside with
  `scripts/edits/master.sh`, which brings the voice to about -14 LUFS and can mix a music file under it.
- Voice level differed 6-8 dB between takes in one recording; match with `setSound` `volumeDb` per clip.

## Checks that caught real problems

- `frameSheet` of the rendered edit after every stage (wrapped titles, wrong layer order, early text).
- Transcribing the export and comparing with the script (clipped words, stray syllables).
- Loudness per section of the export.
- None of these replace listening: Claude cannot hear the audio.

## Edits 455 on macOS 27 (17 November 2026)

- The app container (`~/Library/Containers/com.burbn.basel.mac/Data/Documents`) is no longer writable by
  other processes. `importMedia` reads straight from `~/Movies/...`, so import from there.
- `importMedia` inserts at the playhead, not at the end: `seek` to the intended start before each import.
- Transitions (`addTransition fromId/toId/filterId/durationSeconds`) do not change any clip's start, end or
  source range, so voice stays in sync.
- `addMusicTrack` fills a single music slot (a second call replaces the first) and that slot was missing
  from the export. Import a pre-mixed, pre-ducked bed with `importMedia` instead: it lands as a normal
  audio element and exports.
- Library music downloads (`addSongToComposition`) failed again with DownloadError 3.
- Library sound effects can be long samples (Boom impact ~7 s, Impact (tense) ~12.7 s): trim each to about
  2 s and never past the end, or the export grows a black tail.
- Captions: `generateCaptions`, then `editCaption` for spellings, `setCaptionStyle`, and
  `setTextPosition` (x 0.5, y 0.5) per caption to sit on the split-screen seam instead of over the face.
- Export to any path under `~/Movies` works; output was 1440x2560, 60 fps, HEVC, AAC 44.1 kHz.
