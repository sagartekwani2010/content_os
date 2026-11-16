import numpy as np

from content_os.pipeline import audio, cutpoints
from content_os.pipeline.config import DEFAULTS


def bursts(spans, sr=16000, total=6.0):
    x = np.random.default_rng(0).normal(0, 1e-4, int(sr * total)).astype(np.float32)
    t = np.arange(len(x)) / sr
    for a, b in spans:
        m = (t >= a) & (t < b)
        x[m] += 0.3 * np.sin(2 * np.pi * 180 * t[m])
    return x, sr


def test_speech_regions_find_bursts():
    x, sr = bursts([(0.5, 1.5), (2.0, 3.2), (3.25, 4.0)])
    regions = audio.speech_regions(x, sr, DEFAULTS["vad"])
    assert len(regions) == 2  # the 50 ms gap is merged
    assert abs(regions[0][0] - 0.5) <= 0.02 and abs(regions[0][1] - 1.5) <= 0.02
    assert abs(regions[1][1] - 4.0) <= 0.02


def test_refine_lead_tail_frame_grid_and_neighbours():
    x, sr = bursts([(0.5, 1.5), (2.0, 3.0), (3.15, 4.0)])
    env = audio.envelope_db(x, sr, 10)
    regions = [[0.5, 1.5], [2.0, 3.0], [3.15, 4.0]]
    r = cutpoints.refine({"start": 2.0, "end": 3.0}, env, 0.01, regions, 6.0, 30, DEFAULTS["cutpoints"])
    # on the frame grid (times are stored to 4 decimals)
    assert abs(r["in"] * 30 - round(r["in"] * 30)) < 0.01 and abs(r["out"] * 30 - round(r["out"] * 30)) < 0.01
    assert 0.03 <= r["lead_s"] <= 0.1
    # the next utterance starts 150 ms after: the tail must stop before it
    assert r["out"] < 3.15 and r["tail_s"] >= 0.04
    assert r["frames"] == round((r["out"] - r["in"]) * 30)


def test_variation_features_on_tone():
    sr = 16000
    t = np.arange(sr * 2) / sr
    x = (0.3 * np.sin(2 * np.pi * (150 + 50 * t) * t)).astype(np.float32)
    v = audio.variation_features(x, sr)
    assert v["voiced_frames"] > 10 and v["pitch_std_semitones"] is not None
