"""Cut beats 1-2 top-half clips from the Gym Jarvis main reel, with a hand-drawn
'food agent' circle drawn on for beat 2. Output: 1080x960, 30 fps, H.264, no audio."""
import math, random, subprocess, sys, tempfile
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

SRC = Path.home() / "content-os-media-staging/codex_editing/outputs/gym_jarvis_main_reel.mp4"
OUT = Path.home() / "Movies/ContentOS/food-tracker/visuals"
FONT = Path.home() / ".cache/content_os/fonts/Kalam-Bold.ttf"
FFMPEG = str(Path.home() / ".local/bin/ffmpeg")
W, H, FPS = 1080, 960, 30
ORANGE = (255, 140, 0, 255)
PAPER = (250, 247, 240, 235)
INK = (25, 25, 25, 255)

def cut(start, dur, crop_y, out, hold=0.0):
    hold_f = f",tpad=stop_mode=clone:stop_duration={hold}" if hold else ""
    subprocess.run([FFMPEG, "-v", "error", "-y", "-ss", str(start), "-t", str(dur), "-i", str(SRC),
                    "-vf", f"crop={W}:{H}:0:{crop_y},fps={FPS}{hold_f},format=yuv420p",
                    "-an", "-c:v", "libx264", "-crf", "16", "-preset", "medium",
                    "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709", str(out)],
                   check=True)

def wobbly_ellipse(cx, cy, rx, ry, seed=7, n=220, turns=1.08):
    rnd = random.Random(seed)
    phase = [rnd.uniform(0, 6.28) for _ in range(3)]
    pts = []
    for i in range(n + 1):
        t = turns * 2 * math.pi * i / n - 0.6
        wob = 1 + 0.018 * math.sin(3 * t + phase[0]) + 0.012 * math.sin(5 * t + phase[1])
        drift = 1 + 0.03 * (i / n)  # marker overshoot: end slightly outside the start
        pts.append((cx + rx * wob * drift * math.cos(t), cy + ry * wob * drift * math.sin(t)))
    return pts

def overlay_frames(tmp, dur, draw_at=0.0, draw_len=0.45, label_at=0.1):
    font = ImageFont.truetype(str(FONT), 64)
    small = ImageFont.truetype(str(FONT), 30)
    pts = wobbly_ellipse(540, 455, 470, 400)
    total = int(dur * FPS)
    for f in range(total):
        t = f / FPS
        im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        p = max(0.0, min(1.0, (t - draw_at) / draw_len))
        p = 1 - (1 - p) ** 3  # ease out
        k = int(len(pts) * p)
        if k > 1:
            d.line(pts[:k], fill=ORANGE, width=13, joint="curve")
        a = max(0.0, min(1.0, (t - label_at) / 0.3))
        if a > 0:
            label = "food agent"
            bx, by = 40, 26
            tw = d.textlength(label, font=font)
            box = [bx, by, bx + tw + 44, by + 92]
            d.rounded_rectangle(box, radius=22, fill=PAPER[:3] + (int(235 * a),),
                                outline=ORANGE[:3] + (int(255 * a),), width=6)
            d.text((bx + 22, by + 4), label, font=font, fill=ORANGE[:3] + (int(255 * a),))
            note = "from my last video · demo data"
            d.text((bx + 6, by + 104), note, font=small, fill=(255, 255, 255, int(235 * a)), stroke_width=3, stroke_fill=(0, 0, 0, int(220 * a)))
        im.save(tmp / f"o_{f:04d}.png")

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    b1 = OUT / "beat01_gym_jarvis_intro.mp4"
    cut(6.25, 1.5, 520, b1, hold=2.0)  # title only: builds in, then holds
    base2 = OUT / "_beat02_base.mp4"
    cut(8.0, 4.0, 485, base2)
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        overlay_frames(td, 4.0)
        b2 = OUT / "beat02_food_agent_circle.mp4"
        subprocess.run([FFMPEG, "-v", "error", "-y", "-i", str(base2), "-framerate", str(FPS),
                        "-i", str(td / "o_%04d.png"), "-filter_complex", "[0][1]overlay=0:0:format=auto,format=yuv420p",
                        "-an", "-c:v", "libx264", "-crf", "16", "-preset", "medium",
                        "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709", str(b2)], check=True)
    base2.unlink()
    print(b1); print(b2)

if __name__ == "__main__":
    main()
