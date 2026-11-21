"""Full-length reel preview BEFORE the shoot: final timing, real visuals, captions, SFX, music; temp TTS voice.

Reads the MAIN beat table of a locked factory draft. For each beat: the spoken line (temp voice: macOS `say`),
the visual clips named in backticks in the top-half column (played in order, last frame held), captions at the seam.
Music: an intro bed (stand-in for a library song) until the end of beat --intro-until, then each --bed option
(ducked under the voice). Writes one MP4 per bed option.

Usage: python scripts/shoot/make_preview.py <draft.md> <visuals_dir> <out_dir> --intro-bed X.wav --intro-until 6
       --bed name=path[@start_s] ... [--voice Aman] [--speed 1.15]
Every file is a PREVIEW: the voice is synthetic and the bottom half is a placeholder for the creator's take.
"""
import argparse, json, re, subprocess, tempfile
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

W, H, PH, FPS = 1080, 1920, 960, 30
FONT = Path.home() / ".cache/content_os/fonts/BarlowCondensed-ExtraBold.ttf"
SFX = Path.home() / "Movies/ContentOS/sfx"


def font(n):
    try:
        return ImageFont.truetype(str(FONT), n)
    except OSError:
        return ImageFont.load_default()


def run(*a):
    subprocess.run(a, check=True, capture_output=True)


def dur(p):
    return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(p)],
                                capture_output=True, text=True).stdout.strip() or 0)


def beats_from(md, section="MAIN"):
    m = re.search(rf"^## {section}\b.*?\n(\|.*?)(?:\n\n|\n#|\Z)", md, re.S | re.M)
    rows = [r for r in m.group(1).splitlines() if r.startswith("|")]
    head = [c.strip().lower() for c in rows[0].strip("|").split("|")]
    col = lambda *n: next(i for i, h in enumerate(head) if any(x in h for x in n))
    ib, isp, iv = col("beat"), col("spoken"), col("top-half", "visual")
    out = []
    for r in rows[2:]:
        c = [x.strip() for x in r.strip("|").split("|")]
        if len(c) < len(head):
            continue
        sp = re.sub(r"\*\*|`", "", c[isp]).strip().strip('"')
        if sp.lower() in ("—", "-", "(none)", "none", "") or sp.startswith("("):
            sp = ""
        clips = re.findall(r"`([\w\-]+\.mp4)`", c[iv]) or re.findall(r"([\w\-]+\.mp4)", c[iv])
        hold_m = re.search(r"hold (\d+(?:\.\d+)?) ?s", c[iv])
        out.append({"beat": c[ib], "text": sp, "clips": list(dict.fromkeys(clips)), "hold": float(hold_m.group(1)) if hold_m else 0.0})
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("draft"); ap.add_argument("visuals"); ap.add_argument("out")
    ap.add_argument("--intro-bed"); ap.add_argument("--intro-until", type=int, default=6)
    ap.add_argument("--bed", action="append", default=[]); ap.add_argument("--voice", default="Aman")
    ap.add_argument("--speed", type=float, default=1.15)
    ap.add_argument("--section", default="MAIN")
    a = ap.parse_args(); vis = Path(a.visuals); out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    beats = beats_from(Path(a.draft).read_text(), a.section); tmp = Path(tempfile.mkdtemp())
    # 1. temp voice per beat, sped up like the real edit
    t = 0.0; timeline = []; seen = set()
    for i, b in enumerate(beats):
        if b["text"]:
            aiff, wav = tmp / f"v{i}.aiff", tmp / f"v{i}.wav"
            run("say", "-v", a.voice, "-r", "175", "-o", str(aiff), b["text"])
            run("ffmpeg", "-y", "-i", str(aiff), "-af", f"atempo={a.speed},apad=pad_dur=0.12", "-ar", "48000", "-ac", "1", str(wav))
            d = dur(wav)
            vis_len = sum(dur(vis / c) for c in b["clips"] if (vis / c).exists() and c not in seen)
            d = max(d + 0.25, min(vis_len, d + 0.7))  # cut to the speech, with a short hold when the visual is longer
            d = max(d, b.get("hold", 0.0))           # creator-requested minimum time on screen ("hold N s")
        else:
            wav = None; d = sum(dur(vis / c) for c in b["clips"] if (vis / c).exists()) or 1.0
        seen.update(b["clips"])
        timeline.append({**b, "t0": round(t, 3), "dur": round(d, 3), "wav": str(wav) if wav else None}); t += d
    total = t
    (out / "timeline.json").write_text(json.dumps(timeline, indent=1))
    # 2. voice track
    parts = [f"[{k}]adelay={int(x['t0'] * 1000)}|{int(x['t0'] * 1000)}[d{k}]" for k, x in enumerate([x for x in timeline if x["wav"]])]
    ins = sum([["-i", x["wav"]] for x in timeline if x["wav"]], [])
    nv = len(parts)
    run("ffmpeg", "-y", *ins, "-filter_complex", ";".join(parts) + ";" + "".join(f"[d{k}]" for k in range(nv)) +
        f"amix=inputs={nv}:normalize=0,apad,atrim=0:{total},loudnorm=I=-14:TP=-1.5", "-ar", "48000", str(tmp / "voice.wav"))
    # 3. video frames: top = clips, bottom = placeholder, captions at the seam
    caps = []
    for x in timeline:
        w = x["text"].split()
        if not w:
            continue
        chunks = [" ".join(w[i:i + 3]) for i in range(0, len(w), 3)]
        for k, ch in enumerate(chunks):
            caps.append((x["t0"] + k * x["dur"] / len(chunks), x["t0"] + (k + 1) * x["dur"] / len(chunks), ch))
    vw = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
                           "-i", "-", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "22", str(tmp / "video.mp4")], stdin=subprocess.PIPE)
    import cv2
    last = Image.new("RGB", (W, PH), (3, 12, 20)); pos = {}
    for bi, x in enumerate(timeline):
        frames = []
        for c in x["clips"]:
            cap = cv2.VideoCapture(str(vis / c))
            if pos.get(c, 0) >= cap.get(cv2.CAP_PROP_FRAME_COUNT) - 2:
                pos[c] = 0  # clip already played to the end: replay it (e.g. the STOP ghost at the payoff)
            cap.set(cv2.CAP_PROP_POS_FRAMES, pos.get(c, 0))
            while True:
                ok, fr = cap.read()
                if not ok:
                    break
                frames.append(fr)
            cap.release()
        n = max(1, int(round(x["dur"] * FPS)))
        if len(x["clips"]) == 1:
            pos[x["clips"][0]] = pos.get(x["clips"][0], 0) + min(n, len(frames))
        bottom = Image.new("RGB", (W, PH), (14, 16, 20)); d = ImageDraw.Draw(bottom)
        d.text((W // 2, 300), "YOUR TAKE", font=font(64), fill=(90, 100, 110), anchor="mm")
        d.text((W // 2, 380), f"beat {bi + 1} · {x['beat']}", font=font(40), fill=(70, 80, 90), anchor="mm")
        d.text((W // 2, 900), "PREVIEW · TEMP VOICE", font=font(32), fill=(200, 90, 60), anchor="mm")
        for k in range(n):
            tt = x["t0"] + k / FPS
            if frames:
                fr = frames[min(k, len(frames) - 1)]
                last = Image.fromarray(cv2.cvtColor(cv2.resize(fr, (W, PH)), cv2.COLOR_BGR2RGB))
            img = Image.new("RGB", (W, H)); img.paste(last, (0, 0)); img.paste(bottom, (0, PH))
            cd = ImageDraw.Draw(img)
            for (c0, c1, txt) in caps:
                if c0 <= tt < c1:
                    cd.text((W // 2, PH + 10), txt.upper(), font=font(76), fill=(255, 255, 255), anchor="mt", stroke_width=6, stroke_fill=(0, 0, 0))
            vw.stdin.write(img.tobytes())
    vw.stdin.close(); vw.wait()
    # 4. SFX + music per bed option
    T_int = sum(x["dur"] for x in timeline[:a.intro_until])
    cd_beat = next((x for x in timeline if any("countdown" in c for c in x["clips"])), None)
    sfx_ins, sfx_parts = [], []
    if cd_beat:
        c0 = cd_beat["t0"] + (0.9 if any("wait_is_over" in c for c in cd_beat["clips"]) else 0)
        pts = [(SFX / "desi/dhol_roll.wav", max(0, c0 - 1.0))] + [(Path(out / "_tick.wav"), c0 + k * 0.45) for k in range(3)] + [(Path(out / "_boom.wav"), c0 + 1.35)]
        run("ffmpeg", "-y", "-f", "lavfi", "-i", "sine=f=1800:d=0.06", "-af", "afade=t=out:st=0.02:d=0.04,volume=0.6", str(out / "_tick.wav"))
        run("ffmpeg", "-y", "-f", "lavfi", "-i", "aevalsrc='0.9*sin(2*PI*48*t)*exp(-3*t)+0.25*(random(0)*2-1)*exp(-9*t)':d=1.6:s=48000", str(out / "_boom.wav"))
        for k, (p, s) in enumerate(pts):
            sfx_ins += ["-i", str(p)]; sfx_parts.append(f"[{k}]adelay={int(s * 1000)}|{int(s * 1000)}[s{k}]")
    end_roll = timeline[-1]["t0"] - 0.6
    sfx_ins += ["-i", str(SFX / "desi/dhol_roll.wav")]; k = len(sfx_parts); sfx_parts.append(f"[{k}]adelay={int(end_roll * 1000)}|{int(end_roll * 1000)}[s{k}]")
    run("ffmpeg", "-y", *sfx_ins, "-filter_complex", ";".join(sfx_parts) + ";" + "".join(f"[s{j}]" for j in range(len(sfx_parts))) +
        f"amix=inputs={len(sfx_parts)}:normalize=0,apad,atrim=0:{total}", "-ar", "48000", str(tmp / "sfx.wav"))
    results = []
    for spec in a.bed:
        name, rest = spec.split("=", 1); path, _, st = rest.partition("@"); st = float(st or 0)
        run("ffmpeg", "-y", "-i", a.intro_bed, "-af", f"aloop=loop=-1:size=2e9,atrim=0:{T_int + 0.4},afade=t=out:st={T_int - 0.1}:d=0.5,loudnorm=I=-17:TP=-2",
            "-ar", "48000", "-ac", "2", str(tmp / "intro.wav"))
        run("ffmpeg", "-y", "-ss", str(st), "-i", path, "-af", f"atrim=0:{total - T_int + 0.5},afade=t=in:d=0.4,afade=t=out:st={total - T_int - 1.2}:d=1.5,loudnorm=I=-17:TP=-2,adelay={int((T_int - 0.2) * 1000)}|{int((T_int - 0.2) * 1000)}",
            "-ar", "48000", "-ac", "2", str(tmp / "bed.wav"))
        final = out / f"PREVIEW_{a.section}_{name}.mp4"
        run("ffmpeg", "-y", "-i", str(tmp / "video.mp4"), "-i", str(tmp / "voice.wav"), "-i", str(tmp / "intro.wav"), "-i", str(tmp / "bed.wav"), "-i", str(tmp / "sfx.wav"),
            "-filter_complex", "[2][3]amix=inputs=2:normalize=0[m];[1]asplit=2[v][vs];[m][vs]sidechaincompress=threshold=0.03:ratio=6:attack=20:release=300[md];"
            "[v][md][4]amix=inputs=3:normalize=0:weights='1 0.8 1.2',alimiter=limit=0.79[a]",
            "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", str(final))
        results.append(str(final))
    print(json.dumps({"total_s": round(total, 2), "intro_until_s": round(T_int, 2), "beats": len(timeline), "files": results}, indent=1))


if __name__ == "__main__":
    main()
