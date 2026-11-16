import pytest

from content_os.pipeline import ingest, media
from content_os.pipeline.approvals import approve, require_approval
from content_os.pipeline.reel import Reel, StageError, write_json

from .conftest import needs_ffmpeg


@needs_ffmpeg
def test_loudness_of_known_sine(tmp_path):
    f = tmp_path / "sine.wav"
    # 1 kHz sine at -20 dBFS peak (mono) reads about -23 LUFS
    media.ffmpeg("-v", "error", "-f", "lavfi", "-i", "sine=f=1000:d=5:sample_rate=48000", "-af", "volume=-20dB+0dB",
                 "-c:a", "pcm_s16le", str(f))
    ld = media.loudness(f)
    assert -27 < ld["integrated_lufs"] < -20
    assert ld["true_peak_db"] < -10


@needs_ffmpeg
def test_hdr_hlg_source_is_converted_to_bt709_proxy(tmp_path, cfg):
    raw = tmp_path / "raw"
    raw.mkdir()
    src = raw / "IMG_0001.MOV"
    media.ffmpeg("-v", "error", "-f", "lavfi", "-i", "testsrc2=s=640x360:r=30:d=1", "-f", "lavfi", "-i",
                 "sine=d=1:sample_rate=48000", "-pix_fmt", "yuv420p10le", "-c:v", "libx265", "-tag:v", "hvc1",
                 "-x265-params", "log-level=error:colorprim=bt2020:transfer=arib-std-b67:colormatrix=bt2020nc",
                 "-color_primaries", "bt2020", "-color_trc", "arib-std-b67", "-colorspace", "bt2020nc",
                 "-c:a", "aac", "-shortest", str(src))
    reel = Reel.at(tmp_path)
    data = ingest.run(reel, cfg)
    s = data["sources"][0]
    assert s["video"]["hdr"] is True and s["video"]["color_transfer"] == "arib-std-b67"
    p = media.probe(reel.resolve(s["proxy"]))["video"]
    assert (p["color_transfer"], p["color_primaries"], p["pix_fmt"]) == ("bt709", "bt709", "yuv420p")
    assert media.probe(reel.resolve(s["wav16"]))["audio"]["sample_rate"] == 16000
    assert media.probe(reel.resolve(s["wav48"]))["audio"]["sample_rate"] == 48000
    assert (tmp_path / "work" / ".gitignore").read_text().strip().endswith("*")


def test_approval_gate(tmp_path):
    reel = Reel.at(tmp_path)
    write_json(reel.cuts_file, {"sha256": "aaa"})
    with pytest.raises(StageError, match="no recorded cut_review approval"):
        require_approval(reel, "cut_review", "aaa")
    with pytest.raises(StageError, match="cut_review.html"):
        approve(reel, "cut_review", "tester")
    reel.review_html.write_text("<html></html>")
    approve(reel, "cut_review", "tester")
    require_approval(reel, "cut_review", "aaa")
    with pytest.raises(StageError, match="older version"):
        require_approval(reel, "cut_review", "bbb")


def test_final_render_refuses_without_approval(tmp_path, cfg):
    from content_os.pipeline import render

    reel = Reel.at(tmp_path)
    write_json(reel.cuts_file, {"sha256": "aaa", "segments": []})
    with pytest.raises(StageError, match="approval"):
        render.run(reel, cfg, draft=False)
