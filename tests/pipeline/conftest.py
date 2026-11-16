"""Pipeline test helpers. Media tests generate synthetic files with ffmpeg / macOS `say` in tmp dirs;
nothing here touches the network (the judge CLI and OpenAI client are mocked)."""

from __future__ import annotations

import shutil
from pathlib import Path

import pytest

np = pytest.importorskip("numpy")

from content_os.pipeline import media  # noqa: E402
from content_os.pipeline.config import load_config  # noqa: E402

HAVE_FFMPEG = media.have_tool("ffmpeg") and media.have_tool("ffprobe")
HAVE_SAY = shutil.which("say") is not None
HAVE_WHISPER = media.have_tool("whisper-cli") and Path(load_config()["transcribe"]["model"]).exists()
try:
    import cv2  # noqa: F401

    HAVE_FACE = Path(load_config()["face"]["model"]).exists()
except ImportError:
    HAVE_FACE = False

needs_ffmpeg = pytest.mark.skipif(not HAVE_FFMPEG, reason="ffmpeg/ffprobe not available")
needs_say = pytest.mark.skipif(not HAVE_SAY, reason="macOS `say` not available")
needs_whisper = pytest.mark.skipif(not HAVE_WHISPER, reason="whisper-cli or model not available")
needs_face = pytest.mark.skipif(not HAVE_FACE, reason="opencv or YuNet model not available")


def words_from(spec: list[tuple[str, float]], word_dur: float = 0.3, gap: float = 0.05) -> list[dict]:
    """Build a word list. spec: (text, pause_before_seconds). Times are synthetic and exact."""
    out, t = [], 0.5
    for text, pause in spec:
        for i, w in enumerate(text.split()):
            t += pause if i == 0 else gap
            out.append({"text": w, "start": round(t, 3), "end": round(t + word_dur, 3)})
            t += word_dur
    return out


@pytest.fixture
def cfg():
    return load_config(overrides={"judge": {"enabled": False}})
