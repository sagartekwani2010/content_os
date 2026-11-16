"""Waveform analysis: energy envelope, speech regions, onset snapping, pitch/energy variation."""

from __future__ import annotations

import numpy as np


def envelope_db(x: np.ndarray, sr: int, frame_ms: float = 10.0) -> np.ndarray:
    """RMS level in dBFS per non-overlapping frame."""
    hop = max(1, int(sr * frame_ms / 1000))
    n = len(x) // hop
    if n == 0:
        return np.zeros(0)
    frames = x[: n * hop].reshape(n, hop).astype(np.float64)
    rms = np.sqrt(np.mean(frames ** 2, axis=1) + 1e-12)
    return 20 * np.log10(rms + 1e-10)


def speech_threshold(env: np.ndarray, vad_cfg: dict) -> float:
    if len(env) == 0:
        return -60.0
    floor = float(np.percentile(env, 10))
    loud = float(np.percentile(env, 95))
    return max(floor + vad_cfg["min_threshold_above_floor_db"],
               floor + vad_cfg["threshold_fraction"] * (loud - floor))


def speech_regions(x: np.ndarray, sr: int, vad_cfg: dict) -> list[list[float]]:
    """Energy-based speech regions [[start, end], ...] in seconds (deterministic)."""
    frame_s = vad_cfg["frame_ms"] / 1000
    env = envelope_db(x, sr, vad_cfg["frame_ms"])
    if len(env) == 0:
        return []
    thr = speech_threshold(env, vad_cfg)
    active = env > thr
    regions: list[list[float]] = []
    i = 0
    n = len(active)
    while i < n:
        if active[i]:
            j = i
            while j < n and active[j]:
                j += 1
            regions.append([i * frame_s, j * frame_s])
            i = j
        else:
            i += 1
    merged: list[list[float]] = []
    for r in regions:
        if merged and r[0] - merged[-1][1] < vad_cfg["merge_gap_s"]:
            merged[-1][1] = r[1]
        else:
            merged.append(r)
    return [[round(a, 3), round(b, 3)] for a, b in merged if b - a >= vad_cfg["min_region_s"]]


def snap_low_energy(env: np.ndarray, frame_s: float, t: float, window: float, *, not_after: float | None = None,
                    not_before: float | None = None) -> float:
    """Move t to the quietest frame within +-window, respecting bounds."""
    lo = t - window
    hi = t + window
    if not_after is not None:
        hi = min(hi, not_after)
    if not_before is not None:
        lo = max(lo, not_before)
    if hi < lo or len(env) == 0:
        return t
    i0 = max(0, int(np.floor(lo / frame_s)))
    i1 = min(len(env) - 1, int(np.ceil(hi / frame_s)))
    if i1 < i0:
        return t
    seg = env[i0: i1 + 1]
    k = int(np.argmin(seg))
    # choose the frame centre, clamped to the window
    return float(min(max((i0 + k + 0.5) * frame_s, lo), hi))


def f0_track(x: np.ndarray, sr: int, frame_s: float = 0.04, fmin: float = 70, fmax: float = 400,
             min_db: float = -45) -> np.ndarray:
    """Very small autocorrelation pitch tracker; returns f0 (Hz) for voiced frames only."""
    hop = int(sr * frame_s)
    lag_min, lag_max = int(sr / fmax), int(sr / fmin)
    out = []
    for i in range(0, len(x) - hop, hop):
        fr = x[i: i + hop].astype(np.float64)
        fr = fr - fr.mean()
        if 20 * np.log10(np.sqrt(np.mean(fr ** 2)) + 1e-10) < min_db or len(fr) <= lag_max:
            continue
        ac = np.correlate(fr, fr, mode="full")[len(fr) - 1:]
        if ac[0] <= 0:
            continue
        seg = ac[lag_min: lag_max]
        k = int(np.argmax(seg))
        if seg[k] / ac[0] < 0.3:
            continue
        out.append(sr / (lag_min + k))
    return np.array(out)


def variation_features(x: np.ndarray, sr: int) -> dict:
    """Expressiveness proxies: pitch spread in semitones and energy spread in dB over voiced frames."""
    env = envelope_db(x, sr, 25)
    voiced = env[env > (np.percentile(env, 95) - 25)] if len(env) else env
    f0 = f0_track(x, sr)
    pitch_st = float(np.std(12 * np.log2(f0 / np.median(f0)))) if len(f0) >= 5 else None
    return {"pitch_std_semitones": None if pitch_st is None else round(pitch_st, 2),
            "energy_std_db": round(float(np.std(voiced)), 2) if len(voiced) else None,
            "voiced_frames": int(len(f0))}
