"""Beat 19 top-half clip: real Workout Analyser footage from the Gym Jarvis launch reel (set scan,
rep count, form checks), branded with a hand-drawn 'Workout Analyser' tag. 1080x960, 30 fps, no audio.
Usage: python make_outro_clip.py [duration_s]"""
import math, random, subprocess, sys, tempfile
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

SRC = Path.home() / "content-os-media-staging/codex_editing/outputs/gym_jarvis_main_reel.mp4"
OUT = Path.home() / "Movies/ContentOS/food-tracker/visuals/beat19_workout_analyser.mp4"
FONT = Path.home() / ".cache/content_os/fonts/Kalam-Bold.ttf"
FFMPEG = str(Path.home() / ".local/bin/ffmpeg")
W, H, FPS = 1080, 960, 30
PURPLE = (124, 58, 237, 255)
PAPER = (250, 247, 240, 240)


def overlay_frames(tmp: Path, dur: float, tag_at=0.15, draw_len=0.45):
    big, small = ImageFont.truetype(str(FONT), 70), ImageFont.truetype(str(FONT), 34)
    rnd = random.Random(11)
    for f in range(int(dur * FPS)):
        t = f / FPS
        im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        a = max(0.0, min(1.0, (t - tag_at) / 0.25))
        if a > 0:
            label = "Workout Analyser"
            tw = d.textlength(label, font=big)
            x, y = 34, 24
            d.rounded_rectangle([x, y, x + tw + 48, y + 100], radius=24, fill=PAPER[:3] + (int(240 * a),),
                                outline=PURPLE[:3] + (int(255 * a),), width=7)
            d.text((x + 24, y + 6), label, font=big, fill=PURPLE[:3] + (int(255 * a),))
            # underline drawn on
            p = max(0.0, min(1.0, (t - tag_at - 0.2) / draw_len))
            if p > 0:
                pts = [(x + 24 + (tw) * i / 30 * p, y + 92 + rnd.uniform(-1.5, 1.5)) for i in range(31)]
                d.line(pts, fill=(255, 140, 0, int(255 * a)), width=8)
            d.text((x + 8, y + 116), "next episode", font=small, fill=(255, 255, 255, int(235 * a)),
                   stroke_width=3, stroke_fill=(0, 0, 0, int(220 * a)))
        im.save(tmp / f"o_{f:04d}.png")


def main(dur: float = 4.6):
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        base = td / "base.mp4"
        # source is 1080x1920; keep y 330-1530 (scene + form checks, above the old captions), fit to 960 high
        subprocess.run([FFMPEG, "-v", "error", "-y", "-ss", "16.0", "-t", f"{dur:.2f}", "-i", str(SRC),
                        "-vf", "crop=1080:1200:0:330,scale=-2:960,pad=1080:960:(ow-iw)/2:0:color=0x0B0F17,"
                               f"fps={FPS},format=yuv420p", "-an", "-c:v", "libx264", "-crf", "16", str(base)], check=True)
        overlay_frames(td, dur)
        subprocess.run([FFMPEG, "-v", "error", "-y", "-i", str(base), "-framerate", str(FPS), "-i", str(td / "o_%04d.png"),
                        "-filter_complex", "[0][1]overlay=0:0:format=auto,format=yuv420p", "-an", "-c:v", "libx264",
                        "-crf", "16", "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709",
                        str(OUT)], check=True)
    print(OUT)


if __name__ == "__main__":
    main(float(sys.argv[1]) if len(sys.argv) > 1 else 4.6)
