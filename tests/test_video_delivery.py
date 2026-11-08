"""Regression checks for the export failure seen on the Diwali Reel."""

from content_os.tools.video_delivery import profile_errors


def _probe() -> dict:
    return {"streams": [
        {"codec_type": "video", "codec_name": "h264", "width": 1080,
         "height": 1920, "pix_fmt": "yuv420p", "avg_frame_rate": "30/1",
         "color_space": "bt709", "color_transfer": "bt709", "color_primaries": "bt709"},
        {"codec_type": "audio", "codec_name": "aac", "profile": "LC",
         "sample_rate": "48000", "channels": 2},
    ]}


def test_compatible_reel_profile() -> None:
    assert profile_errors(_probe(), ["ftyp", "moov", "mdat"]) == []


def test_rejects_original_reels_export_failure() -> None:
    probe = _probe()
    probe["streams"][0]["color_primaries"] = "bt2020"
    probe["streams"][0]["color_transfer"] = "arib-std-b67"
    probe["streams"][1]["sample_rate"] = "96000"
    errors = profile_errors(probe, ["ftyp", "mdat", "moov"])
    assert any("color_primaries" in error for error in errors)
    assert any("color_transfer" in error for error in errors)
    assert any("sample_rate" in error for error in errors)
    assert any("faststart" in error for error in errors)
