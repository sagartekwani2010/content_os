"""Verify a finished reel against its clean render before handover.

Usage: verify_final.py <FINAL.mp4> <final_clean.mp4> [--points 5,35,70]

Checks (exit 1 on failure):
  - lip sync: speech-band (300-3000 Hz) cross-correlation of FINAL vs clean at several points, |lag| < 5 ms
  - music present: bass-band (40-200 Hz) loudness of FINAL at least 2 dB above the clean stem
  - duration within 0.1 s of the clean render
Why: Edits caches media by path; a rebuilt clean/bed re-imported under the same name played the old audio
(lip-sync drift, old bed) on the Fable 5.2 reel, 19 Nov 2026.
"""
import re
import subprocess
import sys

import numpy as np

SR = 16000


def pcm(path, start, dur, band):
    lo, hi = band
    out = subprocess.run(
        ["ffmpeg", "-v", "error", "-ss", str(start), "-t", str(dur), "-i", path, "-ac", "1", "-ar", str(SR),
         "-af", f"highpass=f={lo},lowpass=f={hi}", "-f", "f32le", "-"],
        capture_output=True, check=True).stdout
    return np.frombuffer(out, dtype=np.float32)


def lag_ms(final, clean, t):
    a, b = pcm(final, t, 4, (300, 3000)), pcm(clean, t, 4, (300, 3000))
    n = min(len(a), len(b))
    a, b = a[:n] - a[:n].mean(), b[:n] - b[:n].mean()
    max_lag = int(0.2 * SR)
    best, best_c = 0, -1.0
    denom = np.sqrt((a * a).sum() * (b * b).sum()) or 1.0
    for k in range(-max_lag, max_lag + 1, 8):
        c = (a[max(k, 0):n + min(k, 0)] * b[max(-k, 0):n - max(k, 0)]).sum() / denom
        if c > best_c:
            best, best_c = k, c
    return best * 1000 / SR, best_c


def lufs(path, band):
    lo, hi = band
    err = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", path, "-af",
                          f"highpass=f={lo},lowpass=f={hi},ebur128", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    return float(re.findall(r"I:\s+(-?[\d.]+) LUFS", err)[-1])


def duration(path):
    return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0",
                                 path], capture_output=True, text=True).stdout)


def main():
    final, clean = sys.argv[1], sys.argv[2]
    total = duration(clean)
    points = [5, total * 0.45, total - 10]
    if "--points" in sys.argv:
        points = [float(x) for x in sys.argv[sys.argv.index("--points") + 1].split(",")]
    ok = True
    for t in points:
        lag, c = lag_ms(final, clean, t)
        good = abs(lag) < 5
        ok &= good
        print(f"sync t={t:.0f}s lag {lag:.1f} ms corr {c:.2f} {'OK' if good else 'FAIL'}")
    bf, bc = lufs(final, (40, 200)), lufs(clean, (40, 200))
    good = bf - bc >= 2
    ok &= good
    print(f"music bass-band FINAL {bf:.1f} vs clean {bc:.1f} LUFS (+{bf - bc:.1f} dB) {'OK' if good else 'FAIL'}")
    df = duration(final)
    good = abs(df - total) < 0.1
    ok &= good
    print(f"duration FINAL {df:.2f}s vs clean {total:.2f}s {'OK' if good else 'FAIL'}")
    print("VERIFY PASSED" if ok else "VERIFY FAILED")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
