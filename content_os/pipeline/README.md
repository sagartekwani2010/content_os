# Reel editing pipeline (`content_os.pipeline`)

Turns line-by-line iPhone recordings into a measured 1080x1920 split-screen reel. Every measurement
is a script; a Claude model (via the `claude` CLI) is consulted only for judgement calls, and only
among options that passed the hard checks. Nothing here edits `cli.py`, `config/` or the tracking code.

```
python -m content_os.pipeline setup                       # models -> ~/.cache/content_os (sha256-checked)
python -m content_os.pipeline run <reel_dir>              # ingest ... cut_review (+ judge if enabled)
open <reel_dir>/work/cut_review.html                      # look at and listen to every cut
python -m content_os.pipeline approve <reel_dir> cut_review --by <name>
python -m content_os.pipeline run <reel_dir> --from render --until qa
```

Single stages: `ingest | transcribe | segment | score | cutpoints | cut_review | render [--draft] | qa [--draft]`,
plus `judge --phase takes|cuts`, `select --beat N --take bN_tK` (override; eligible takes only),
`approve`, `synth <dir> [--hdr] [--files 2]` (synthetic test reel). Any setting can be overridden
per call with `--set key.sub=value` or per reel in `<reel_dir>/pipeline.yaml` (defaults: `config.py`).

Extra Python dependencies: `content_os/pipeline/requirements.txt` (numpy, opencv-python-headless).
External tools: ffmpeg/ffprobe (>= 8: libx264, libass, ebur128, swscale transfer conversion),
whisper-cli (whisper.cpp), `say` (synthetic tests only), `claude` (judge step only).

## Recording protocol it is built for

iPhone, landscape 16:9 (4K HEVC, HDR/HLG allowed), camera locked. Before each beat say "beat N";
read the line, look up, say it two or three times with a short pause, move on. One file or several.
ASR variants of the cue are accepted ("beat for", "bit 3", "beat number three", "B2"). A beat
recorded again later simply adds takes; files without cues fall back to matching by words.

## Reel directory

```
<reel_dir>/
  beats.json            input: the script, one line per beat (example: examples/beats.json)
  cue_sheet.json        input: visuals, SFX, music, layout (example: examples/cue_sheet.json)
  pipeline.yaml         optional config overrides
  raw/                  footage (*.MOV, *.mp4), or pass `ingest --source`
  work/                 everything generated; has its own .gitignore ("*")
    sources.json  audio/  proxy/  asr/  transcript.json  transcript.txt
    takes.json  scores.json  selects.json  auditions/
    judge_takes.json  judge_cuts.json  judge_*_request.json  cue_sheet.suggested.json
    cuts.json  review/  cut_review.html  approvals.json
    render/draft/draft.mp4  render/final/final.mp4  render/*/render.json
    qa.json  qa.md  qa_asr/  timings.json
```

Nothing under `work/` may be committed: it holds the creator's voice, transcripts and footage.

## Stages and files

All generated files carry `"schema": "content_os.pipeline/<name>@1"`. Times are seconds in the source
file unless named `out_*` (output timeline).

### Inputs

`beats.json`
```json
{"reel_id": "id", "target_duration_s": 58,
 "beats": [{"id": 1, "text": "Spoken line exactly as scripted.", "section": "hook"}]}
```

`cue_sheet.json` (every key optional; beats without an entry hold the previous visual)
```json
{"layout": "split_vertical",
 "layout_params": {"speaker_ratio": 0.5, "speaker_position": "bottom", "caption_position": "top_safe"},
 "beats": [{"beat": 1,
            "visual": {"type": "card|image|video", "text": "CARD TEXT", "path": "assets/x.png",
                       "fit": "contain|cover", "start": 0.0, "loop": false, "bg": "#F4EFE6", "fg": "#1E1E1E"},
            "start_offset": 0.4,
            "sfx": [{"path": "assets/sfx/pop.wav", "at": 0.4, "gain_db": -16}]}],
 "music": {"path": "music/bed.m4a", "gain_db": -20, "fade_in": 0.5, "fade_out": 2.0,
           "duck": {"threshold": 0.03, "ratio": 6, "attack_ms": 15, "release_ms": 350}}}
```
`start_offset` = seconds after the beat starts when its visual appears; `visual.start` = in-point
inside a video file; `music.gain_db` is relative to the voice target (the bed is loudness-normalised
first, then ducked under the voice with a sidechain compressor). Tested with 15 beats.

`"visual_clips": "work/visuals"` (optional) uses the word-anchored, hand-drawn beat clips rendered by
`python -m content_os.visuals render <reel_dir>` (from `visual_cues.json` and `work/cuts.json`) for every
beat that has no explicit `visual`; a clip starts at its beat's first frame. Explicit visuals can use
`{"type": "clip", "path": "work/visuals/beat_04.mp4"}`. The final render refuses clips whose
`visuals.json` records a different cuts.json hash (re-render them after changing a take or a cut).

### 1. ingest -> `sources.json`
Per source: `id` (s1, s2 ... in filename order), `path`, `duration`, `video` (codec, size, display size,
rotation, fps, pix_fmt, colour tags, `hdr`), `audio`, `wav16` (16 kHz mono s16, for ASR), `wav48`
(48 kHz mono s24, for the mix), `proxy` (960 px wide BT.709 SDR H.264, GOP 15; for face detection and
review frames), `proxy_size`, `notes`. HLG/PQ sources are converted with ffmpeg's `scale`
transfer/primaries conversion (`ingest.hdr_method: swscale`).

### 2. transcribe -> `transcript.json`, `transcript.txt`
```json
{"engine": "whisper_cpp", "model": "ggml-small.en.bin",
 "sources": {"s1": {"duration": 29.7, "speech_regions": [[0.84, 1.42]], "chunks": [[0.59, 1.67]],
                    "words": [{"text": "Beat", "start": 0.84, "end": 1.1, "conf": 0.5, "anchor": 0.96, "region": 0}]}}}
```
whisper.cpp: `whisper-cli -m ggml-small.en.bin -l en -ojf -np -t 4 -mc 64 -dtw small.en -nfa -ng
chunk_000.wav chunk_001.wav ...` (one call, model loaded once). Audio is chunked by an energy VAD at
every pause >= 0.5 s, because whisper drops a sentence that repeats inside one 30 s window (which is
what retakes are). Word anchors come from DTW token timestamps (`t_dtw`); word edges at pauses are
snapped to the energy-VAD regions (10 ms). whisper's own `--vad` is off: in 1.9.3 its token offsets
come back in VAD-compressed time. Metal crashes in the conda build used here, so `gpu: cpu`.
`openai` engine (opt-in, uploads audio): `whisper-1`, `response_format=verbose_json`,
`timestamp_granularities=["word"]`, key from `OPENAI_API_KEY` only; `whisper-1` is the only model
with word timestamps and is scheduled to shut down on 26 February 2027.

### 3. segment -> `takes.json`
```json
{"cues": [{"beat": 2, "heard": "Beat to.", "start": 9.63, "end": 10.18, "source": "s1"}],
 "takes": [{"id": "b2_t3", "beat": 2, "attempt": 3, "source": "s1", "start": 16.66, "end": 19.05,
            "duration": 2.39, "words": [{"text": "Here", "start": 16.66, "end": 16.9}], "text": "...",
            "completeness": 1.0, "precision": 1.0, "covers_start": true, "covers_end": true,
            "text_similarity": 0.98, "complete": true, "restart": false, "repeated_ngrams": [],
            "fillers": 0, "filler_words": [], "internal_pauses": [{"after_word": "change,", "gap_s": 0.4}],
            "best_beat": 2, "best_beat_similarity": 1.0, "assigned_by": "cue|similarity",
            "flags": ["incomplete", "abandoned_restart", "internal_repeat", "stutter", "fillers", "beat_mismatch:3"]}],
 "unassigned": [], "summary": [{"beat": 2, "takes": 3, "complete": 2, "cues_heard": 1}], "missing_beats": []}
```
Completeness = fuzzy (token similarity >= 0.8, numbers normalised) order-constrained LCS coverage
of the beat line; complete when >= 0.8 and the first and last two words of the line are covered.
Attempts split at pauses >= 0.45 s when the speaker goes back in the script, or at pauses >= 1.5 s;
a restart without a pause (the line's opening said again) splits the attempt there.

### 4. score -> `scores.json`, `selects.json`, `auditions/`
Per take (added to the takes fields): `wpm`, `loudness_lufs`, `true_peak_db`, `loudness_rel_beat_db`
(vs beat median), `variation` (`pitch_std_semitones`, `energy_std_db`, `voiced_frames`), `face`
(`measured`, `present_ratio`, `cx`, `cy`, `w` as fractions of the frame, `drift_x`, `frontal_ratio`,
`median_abs_yaw`), `eligible`, `ineligible_reasons`, `score`, `score_parts`.
Face detector: OpenCV YuNet (`cv2.FaceDetectorYN`, face_detection_yunet_2023mar.onnx) on frames
downscaled to <= 640 px; head-pose proxy = nose offset from the eye midpoint / eye distance. No model
or no OpenCV -> `face.measured: false` everywhere and selection proceeds on audio/text.

`selects.json`
```json
{"beats": [{"beat": 2, "take": "b2_t3", "status": "ok|needs_rerecord", "picked_by": "rule:last_complete_fluent",
            "reason": "...", "close_call": true, "better_alternatives": ["b2_t2"], "close_rivals": [],
            "audition_clips": ["work/auditions/beat02_b2_t3_PICK.mp4"],
            "candidates": [{"take": "b2_t1", "eligible": false, "score": 0.65, "reasons": ["incomplete sentence"]}],
            "judge": {"take": "b2_t2", "reason": "...", "confidence": "medium", "accepted": true}}],
 "needs_rerecord": []}
```
Default pick: the last eligible take. Close call: another eligible take within `close_call_gap`
(0.05) of the pick's composite score, or better by more than it; 10 s audition clips are exported.

### Judge (optional, after score and after cut_review) -> `judge_takes.json`, `judge_cuts.json`
`claude -p --model <judge.model> --input-format stream-json --output-format stream-json --verbose
--json-schema <schema> --tools "" --no-session-persistence --strict-mcp-config --system-prompt ...
--effort high --max-budget-usd 3`, run from a temp dir (no CLAUDE.md). Sends beats.json, take
transcripts and measured features as text; for `cuts`, also the contact-sheet PNGs. Model from
`judge.model` (default `claude-fable-5-2`). Take choices are applied only when the take passed every
hard check (`decisions[].accepted`); cut rejections are shown on the review page and recorded with
the approval; visual-timing suggestions go to `work/cue_sheet.suggested.json` (cue_sheet.json is
never edited). Set `judge.enabled: false` to skip.

### 5. cutpoints -> `cuts.json`
```json
{"fps": 30, "layout": {...}, "reference_face": {"cx": 0.5, "cy": 0.46}, "reference_lufs": -17.3,
 "duration": 8.1, "sha256": "...",
 "segments": [{"index": 0, "beat": 1, "take": "b1_t2", "source": "s1", "in": 5.9667, "out": 8.5667,
               "frames": 78, "duration": 2.6, "out_start": 0.0, "lead_s": 0.033, "tail_s": 0.097,
               "lufs": -16.2, "gain_db": -1.1, "face": {...}, "crop": {"x": 234, "y": 0, "w": 810, "h": 720},
               "crop_realigned": false, "src_size": [1280, 720], "words": [{"text": "Most", "start": 0.03}],
               "text": "...", "notes": []}],
 "joins": [{"index": 0, "time": 2.6, "left": 0, "right": 1, "crossfade_ms": 30}]}
```
in/out = first word - 40 ms / last word + 80 ms, moved to the quietest 10 ms frame within 20 ms,
bounded by neighbouring speech, then floored/ceiled to the frame grid. Crop: fixed per reel, centred
on the median face of the selected takes; a take whose face is > 2% of the source width away gets
its own crop (`crop_realigned`). Gain: each segment to the median segment loudness (clamped +-12 dB).

### 6. cut_review -> `cut_review.html`, `review/`
Self-contained page: per cut, the last/first frame inside the speaker crop, face jump (% of output
width and of source width), loudness of the last/first 1.5 s after gain, words either side, and a
4 s audio clip of the join with the crossfade. Also `review/contact_sheet.png`, `review/join_NN.png`,
`review/review.json`. `approve <reel_dir> cut_review --by <name>` writes `approvals.json`
(`{"cut_review": {"sha256": <cuts.json sha256>, "by", "note", "approved_at"}}`); changing the cuts
invalidates it.

### 7. render -> `render/<draft|final>/<name>.mp4`, `render.json`
`--draft` needs no approval: placeholder cards per beat, no music/SFX, a DRAFT label. The final
render refuses unless the approval hash matches. Pipeline: per-segment speaker clips (SDR conversion,
crop, Lanczos scale, exact frame count) -> concat; per-interval visual clips -> concat; voice from
the 48 kHz wavs with per-take gain and 30 ms triangular crossfades (audio extended 15 ms each side, so
picture and sound stay frame-aligned); master: voice gain to -14 LUFS, music normalised then set
`gain_db` under the voice and sidechain-ducked, SFX delayed into place, summed, limited at 4x
oversampling (sample peak -2.0 dB, true peak <= -1.5 dBTP), re-measured and corrected (<= 3 passes);
captions: 2-4 word phrases from the selected words, ASS burned with libass. Output: H.264 High
yuv420p BT.709 (tagged), AAC 192 kb/s 48 kHz, 1080x1920, faststart.

Layouts are plugins (`layouts.LAYOUTS`): `split_vertical` (speaker panel top or bottom, ratio 0.2-0.8;
captions `top_safe` = inside the visual panel just above the seam, or `seam`). A full 9:16 talking-head
layout is a new factory returning a `Layout` (panels, caption box, compose filter).

### 8. qa -> `qa.json`, `qa.md` (exit code 2 on a hard failure)
Checks: format (h264/aac 48k/BT.709/1080x1920), duration vs plan (+-0.15 s) and <= 120 s, black frames
(blackdetect >= 0.1 s), silence gaps > 0.6 s in the voice stem, integrated loudness (-14 +-1 LUFS),
true peak (<= -1 dBTP), clipping (samples at full scale), clips >= 1.0 s, captions present (render vs
caption-free composite inside the caption box), captions clear of the face and of the Instagram UI
(bottom 250 px, right 120 px), max face jump at cuts measured on the render (warn > 2%, fail > 5% of
frame width; soft when no face is found), and a re-transcription of the render compared with the
script per beat (WER warn > 0.15, fail > 0.40). `qa.md` lists what was not checked.
