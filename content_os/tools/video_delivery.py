"""Check a rendered vertical video against the Content OS delivery profile.

Usage: python -m content_os.tools.video_delivery path/to/reel.mp4 [--decode]
The check is diagnostic; it never rewrites the supplied video.
"""

from __future__ import annotations

import argparse
import json
import subprocess
from fractions import Fraction
from pathlib import Path
from typing import Any


def mp4_atom_order(path: Path) -> list[str]:
    """Read top-level atom names without loading a potentially large video."""
    atoms: list[str] = []
    with path.open("rb") as source:
        end = path.stat().st_size
        while source.tell() + 8 <= end:
            header = source.read(8)
            size = int.from_bytes(header[:4], "big")
            name = header[4:8].decode("ascii", errors="replace")
            if size == 1:
                extended = source.read(8)
                if len(extended) != 8:
                    break
                size = int.from_bytes(extended, "big")
            elif size == 0:
                size = end - (source.tell() - 8)
            if size < 8:
                break
            atoms.append(name)
            source.seek(min(end, source.tell() + size - (16 if header[:4] == b"\x00\x00\x00\x01" else 8)))
    return atoms


def profile_errors(probe: dict[str, Any], atoms: list[str]) -> list[str]:
    streams = probe.get("streams", [])
    video = next((s for s in streams if s.get("codec_type") == "video"), {})
    audio = next((s for s in streams if s.get("codec_type") == "audio"), {})
    errors: list[str] = []
    expected_video = {
        "codec_name": "h264", "width": 1080, "height": 1920,
        "pix_fmt": "yuv420p", "color_space": "bt709",
        "color_transfer": "bt709", "color_primaries": "bt709",
    }
    for field, expected in expected_video.items():
        if video.get(field) != expected:
            errors.append(f"video.{field}: expected {expected}, got {video.get(field)}")
    try:
        fps = Fraction(video.get("avg_frame_rate", "0"))
    except (ValueError, ZeroDivisionError):
        fps = Fraction(0)
    if fps != 30:
        errors.append(f"video.fps: expected 30, got {fps}")
    for field, expected in {"codec_name": "aac", "profile": "LC", "sample_rate": "48000", "channels": 2}.items():
        if audio.get(field) != expected:
            errors.append(f"audio.{field}: expected {expected}, got {audio.get(field)}")
    if "moov" not in atoms or "mdat" not in atoms or atoms.index("moov") > atoms.index("mdat"):
        errors.append("mp4.faststart: moov atom must precede mdat")
    return errors


def verify(path: Path, decode: bool = False) -> dict[str, Any]:
    probe_run = subprocess.run(
        ["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", str(path)],
        capture_output=True, text=True, check=True,
    )
    probe = json.loads(probe_run.stdout)
    atoms = mp4_atom_order(path)
    errors = profile_errors(probe, atoms)
    if decode:
        decoded = subprocess.run(
            ["ffmpeg", "-v", "error", "-xerror", "-i", str(path), "-f", "null", "-"],
            capture_output=True, text=True,
        )
        if decoded.returncode:
            errors.append(f"full_decode_failed: {decoded.stderr.strip()[-500:]}")
    return {"path": str(path), "duration_seconds": float(probe.get("format", {}).get("duration", 0)),
            "atoms": atoms, "decoded": decode and not any(e.startswith("full_decode") for e in errors),
            "compatible": not errors, "errors": errors}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("video", type=Path)
    parser.add_argument("--decode", action="store_true", help="decode the entire file with ffmpeg")
    args = parser.parse_args()
    result = verify(args.video, args.decode)
    print(json.dumps(result, indent=2))
    if not result["compatible"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
