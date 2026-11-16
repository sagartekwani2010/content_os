"""End to end on a synthetic reel (macOS `say` voice + drawn face), with the real whisper model.
Judge is disabled here (it is covered, mocked, in test_judge.py)."""

import pytest

from content_os.pipeline import cli, media
from content_os.pipeline.reel import Reel, read_json
from content_os.pipeline.synth import make_reel

from .conftest import needs_face, needs_ffmpeg, needs_say, needs_whisper

pytestmark = [needs_ffmpeg, needs_say, needs_whisper]


@pytest.fixture(scope="module")
def reel_dir(tmp_path_factory):
    root = tmp_path_factory.mktemp("synthreel")
    make_reel(root)
    return root


def main(*args):
    return cli.main(["--set", "judge.enabled=false", *args])


def test_whisper_smoke_on_say_clip(tmp_path, cfg):
    """Real-path smoke test of the transcribe engine on a short `say` clip."""
    import subprocess

    from content_os.pipeline.transcribe import transcribe_file

    aiff = tmp_path / "a.aiff"
    subprocess.run(["say", "-o", str(aiff), "Beat two. Here is the test I use."], check=True)
    wav = tmp_path / "a16.wav"
    media.ffmpeg("-v", "error", "-i", str(aiff), "-ac", "1", "-ar", "16000", str(wav))
    res = transcribe_file(wav, tmp_path / "asr", cfg, "whisper_cpp")
    text = " ".join(w["text"] for w in res["words"]).lower()
    assert "test i use" in text
    # whisper writes the cue as "Beat two", "Beat 2" or "B2,": all must parse as beat 2
    from content_os.pipeline import textmatch as tm

    toks = tm.tokens(text)
    assert any(tm.parse_cue(toks, i, 5) and tm.parse_cue(toks, i, 5)[0] == 2 for i in range(len(toks)))
    assert all(w["end"] > w["start"] for w in res["words"])


@needs_face
def test_full_pipeline(reel_dir):
    assert main("run", str(reel_dir), "--until", "cut_review", "--no-auditions") == 0
    reel = Reel.at(reel_dir)
    takes = read_json(reel.takes_file)
    assert [c["beat"] for c in takes["cues"]] == [1, 2, 3]
    assert [t["complete"] for t in takes["takes"]] == [True, True, False, True, True, True, True]
    sel = read_json(reel.selects_file)
    assert [e["take"] for e in sel["beats"]] == ["b1_t2", "b2_t3", "b3_t2"]  # last complete fluent take
    cuts = read_json(reel.cuts_file)
    assert cuts["segments"][2]["crop_realigned"] is True  # the head moved ~3% on that take
    assert cuts["segments"][1]["gain_db"] > 4  # the -6 dB take is matched up
    review = read_json(reel.work / "review" / "review.json")
    assert review["max_face_jump_pct_out"] < 1.0 and review["max_level_step_db"] < 2.0
    assert main("render", str(reel_dir)) == 1  # refused: not approved yet
    assert main("approve", str(reel_dir), "cut_review", "--by", "test") == 0
    assert main("render", str(reel_dir)) == 0
    assert main("qa", str(reel_dir)) == 0
    qa = read_json(reel.qa_json)
    assert qa["passed"], qa["hard_failures"]
    assert abs(qa["loudness"]["integrated_lufs"] + 14) <= 1.0 and qa["loudness"]["true_peak_db"] <= -1.0
    by = {c["name"]: c for c in qa["checks"]}
    assert by["transcript_vs_script_wer"]["value"] <= 0.15
    assert by["captions_present"]["status"] == "pass"


def test_no_face_detector_degrades_gracefully(reel_dir, tmp_path):
    reel = Reel.at(reel_dir)
    if not reel.takes_file.exists():
        assert main("run", str(reel_dir), "--until", "segment") == 0
    assert cli.main(["--set", "face.detector=none", "--set", "judge.enabled=false", "score", str(reel_dir),
                     "--no-auditions"]) == 0
    scores = read_json(reel.scores_file)
    assert scores["face_detector"] is None
    assert all(t["face"]["measured"] is False for t in scores["takes"])
    assert [e["take"] for e in read_json(reel.selects_file)["beats"]] == ["b1_t2", "b2_t3", "b3_t2"]
