"""Pipeline settings: built-in defaults merged with an optional ``<reel_dir>/pipeline.yaml``.

Every threshold the pipeline uses lives here so a run is reproducible from the files alone.
"""

from __future__ import annotations

import copy
import os
from pathlib import Path
from typing import Any

import yaml

CACHE_DIR = Path(os.environ.get("CONTENT_OS_CACHE", Path.home() / ".cache" / "content_os"))

DEFAULTS: dict[str, Any] = {
    "fps": 30,
    "output": {"width": 1080, "height": 1920},
    "ingest": {
        "source_glob": ["raw/*.mov", "raw/*.MOV", "raw/*.mp4", "raw/*.MP4", "raw/*.m4v"],
        "proxy_width": 960,
        # HDR (HLG/PQ) to SDR BT.709. "swscale" uses ffmpeg's scale filter transfer/primaries
        # conversion (works without GPU); "none" only retags.
        "hdr_method": "swscale",
    },
    "transcribe": {
        "engine": "whisper_cpp",
        "whisper_cli": "whisper-cli",
        "model": str(CACHE_DIR / "whisper" / "ggml-small.en.bin"),
        "dtw_preset": "auto",          # derived from model name (small.en) for token timestamps
        "threads": 4,                  # performance cores; more threads slowed it down here
        "gpu": "cpu",                  # "auto" tries Metal first; Metal crashes in the conda 1.9.3 build
        "language": "en",
        "chunk_max_s": 28.0,           # our own energy-VAD chunking (keeps original timeline)
        "chunk_split_gap_s": 0.5,      # every pause this long starts a new chunk (retakes decoded alone)
        "whisper_vad": False,          # whisper --vad: token offsets come back in VAD time (1.9.3)
        "vad_model": str(CACHE_DIR / "whisper" / "ggml-silero-v5.1.2.bin"),
        "dtw_lead_s": 0.08,
        "openai_model": "whisper-1",   # only model with word timestamps (deprecated Feb 2027)
        "openai_chunk_max_s": 600.0,
    },
    "vad": {                           # energy speech detector on the 16 kHz wav
        "frame_ms": 10,
        "min_threshold_above_floor_db": 8.0,
        "threshold_fraction": 0.3,
        "merge_gap_s": 0.12,
        "min_region_s": 0.08,
    },
    "segment": {
        "cue_min_pre_gap_s": 0.2,
        "cue_min_post_gap_s": 0.15,
        "attempt_gap_s": 0.45,
        "hard_gap_s": 1.5,
        "complete_threshold": 0.8,
        "token_similarity": 0.8,
        "beat_mismatch_margin": 0.3,
        "fallback_min_similarity": 0.5,
    },
    "score": {
        "face_sample_fps": 2.0,
        "max_fillers": 1,
        "min_face_present": 0.8,
        "frontal_yaw_max": 0.18,
        "target_wpm": 160,
        "close_call_gap": 0.05,
        "audition_seconds": 10.0,
        "weights": {
            "completeness": 0.35, "fluency": 0.15, "frontal": 0.15,
            "alignment": 0.15, "loudness": 0.10, "pace": 0.10,
        },
    },
    "face": {
        "detector": "yunet",
        "model": str(CACHE_DIR / "models" / "face_detection_yunet_2023mar.onnx"),
        "score_threshold": 0.6,
    },
    "cutpoints": {
        "lead_s": 0.040,
        "tail_s": 0.080,
        "snap_window_s": 0.020,
        "crossfade_ms": 30,
    },
    "speaker": {
        "zoom": 1.0,                  # 1.0 = full source height in the speaker panel
        "eye_line": 0.40,             # eyes at 40% from the panel top when zoom > 1
        "realign_threshold": 0.02,    # take face offset (fraction of source width) that re-centres
    },
    "layout": {
        "name": "split_vertical",
        "params": {"speaker_ratio": 0.5, "speaker_position": "bottom", "caption_position": "top_safe"},
    },
    "safe_area": {"bottom": 250, "right": 120, "left": 60, "top": 220},
    "captions": {
        "enabled": True,
        "min_words": 2,
        "max_words": 4,
        "max_chars": 22,
        "font_file": "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
        "font_name": "Arial",
        "bold": True,
        "font_size": 64,
        "primary": "#FFFFFF",
        "outline": "#111111",
        "outline_px": 5,
        "shadow_px": 0,
        "uppercase": False,
        "margin_above_seam": 36,
    },
    "cards": {
        "font_file": "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
        "font_size": 76,
        "bg": "#F4EFE6",
        "fg": "#1E1E1E",
        "wrap_chars": 18,
    },
    "master": {
        "target_lufs": -14.0,
        "true_peak_db": -1.5,
        "take_gain_clamp_db": 12.0,
        "music_gain_db": -20.0,
        "duck": {"threshold": 0.03, "ratio": 6, "attack_ms": 15, "release_ms": 350},
    },
    "video": {"crf": 18, "preset": "medium", "draft_crf": 23, "draft_preset": "veryfast",
              "audio_bitrate": "192k"},
    "judge": {
        "enabled": True,               # `run` calls it after score and after cut_review
        "cli": "claude",
        "model": "claude-fable-5-2",
        "effort": "high",
        "timeout_s": 900,
        "max_images": 20,
        "max_budget_usd": 3.0,
    },
    "qa": {
        "max_duration_s": 120.0,       # reel target: under 2 minutes
        "duration_tolerance_s": 0.15,
        "max_silence_s": 0.6,
        "silence_noise_db": -45,
        "silence_hard": True,
        "lufs_tolerance": 1.0,
        "max_true_peak_db": -1.0,
        "min_clip_s": 1.0,
        "face_jump_warn_pct": 2.0,
        "face_jump_fail_pct": 5.0,
        "wer_warn": 0.15,
        "wer_fail": 0.40,
        "black_min_s": 0.1,
        "transcribe_render": True,
    },
}


def deep_merge(base: dict, override: dict) -> dict:
    out = copy.deepcopy(base)
    for key, value in (override or {}).items():
        if isinstance(value, dict) and isinstance(out.get(key), dict):
            out[key] = deep_merge(out[key], value)
        else:
            out[key] = copy.deepcopy(value)
    return out


def load_config(reel_dir: Path | str | None = None, overrides: dict | None = None) -> dict:
    cfg = copy.deepcopy(DEFAULTS)
    if reel_dir is not None:
        path = Path(reel_dir) / "pipeline.yaml"
        if path.exists():
            cfg = deep_merge(cfg, yaml.safe_load(path.read_text()) or {})
    if overrides:
        cfg = deep_merge(cfg, overrides)
    return cfg
