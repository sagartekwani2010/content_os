"""Gym Jarvis Ep 3 finish: insert the full-screen 3-2-1 blast after a beat, add the bed under the voice, master.

Input: the pipeline's final render (voice + SFX + subtitles, 1080x1920) and render/cuts info.
Output (in --out): ep3_main_FOR_EDITS.mp4 (no music in the opening window: Desi Boyz goes on top in Edits) and
ep3_main_PREVIEW_dhol.mp4 (same, with the original dhol stand-in in the opening so it can be watched anywhere).

Usage: python ep3_finish.py <reel_dir> <out_dir> --insert-after-beat 2 --insert FULL_countdown.mp4 --bed bed.mp3 --bed-start 22.0
"""
import argparse, json, subprocess, tempfile
from pathlib import Path


def run(*a):
    subprocess.run(a, check=True)


def dur(p):
    return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(p)],
                                capture_output=True, text=True).stdout.strip())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("reel"); ap.add_argument("out"); ap.add_argument("--insert-after-beat", type=int, default=2)
    ap.add_argument("--insert"); ap.add_argument("--bed"); ap.add_argument("--bed-start", type=float, default=0.0)
    ap.add_argument("--intro-bed", help="stand-in for the opening window in the preview version")
    ap.add_argument("--bed-db", type=float, default=-15.0)
    ap.add_argument("--cd", type=float, default=1.35, help="countdown length inside the insert; ticks every cd/3, blast at cd")
    ap.add_argument("--bed-from-zero", action="store_true", help="one track from frame 0; its --bed-start is placed so the drop lands on the blast")
    ap.add_argument("--drop-at", type=float, default=None, help="time of the track's drop (s); with --bed-from-zero, aligned to the blast")
    a = ap.parse_args(); R = Path(a.reel); O = Path(a.out); O.mkdir(parents=True, exist_ok=True)
    final = R / "work/render/final/final.mp4"
    cuts = json.loads((R / "work/cuts.json").read_text())
    seg = next(s for s in cuts["segments"] if s["beat"] == a.insert_after_beat)
    t_cut = round((seg["out_start"] + seg["duration"]), 3)          # end of the beat on the output timeline
    ins = Path(a.insert); d_ins = dur(ins); total = dur(final); new_total = total + d_ins
    with tempfile.TemporaryDirectory() as tmp:
        T = Path(tmp)
        # 1. picture: [0, t_cut] + insert (scaled to 1080x1920) + [t_cut, end]; audio: same with SFX under the insert
        run("ffmpeg", "-v", "error", "-y", "-i", str(final), "-t", str(t_cut), "-c:v", "libx264", "-crf", "16", "-pix_fmt", "yuv420p",
            "-c:a", "pcm_s16le", "-ar", "48000", "-ac", "2", str(T / "a.mov"))
        run("ffmpeg", "-v", "error", "-y", "-ss", str(t_cut), "-i", str(final), "-c:v", "libx264", "-crf", "16", "-pix_fmt", "yuv420p",
            "-c:a", "pcm_s16le", "-ar", "48000", "-ac", "2", str(T / "c.mov"))
        sfx = Path.home() / "Movies/ContentOS/sfx"
        cd = a.cd; tk = int(cd / 3 * 1000)
        run("ffmpeg", "-v", "error", "-y", "-i", str(ins), "-i", str(sfx / "tick.wav"), "-i", str(sfx / "tick.wav"), "-i", str(sfx / "tick.wav"),
            "-i", str(sfx / "whoosh.wav"), "-i", str(sfx / "hit.wav"), "-filter_complex",
            f"[0:v]scale=1080:1920,setsar=1,fps=30[v];[1]adelay=0|0,volume=2.0[a1];[2]adelay={tk}|{tk},volume=2.0[a2];[3]adelay={2 * tk}|{2 * tk},volume=2.0[a3];"
            f"[4]adelay=0|0,volume=1.4[a4];[5]adelay={int(cd * 1000)}|{int(cd * 1000)},volume=2.5[a5];"
            f"[a1][a2][a3][a4][a5]amix=inputs=5:normalize=0,apad,atrim=0:{d_ins},aformat=sample_rates=48000:channel_layouts=stereo[a]",
            "-map", "[v]", "-map", "[a]", "-c:v", "libx264", "-crf", "16", "-pix_fmt", "yuv420p", "-c:a", "pcm_s16le", str(T / "b.mov"))
        (T / "l.txt").write_text("".join(f"file '{T / n}'\n" for n in ("a.mov", "b.mov", "c.mov")))
        run("ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(T / "l.txt"), "-c", "copy", str(T / "joined.mov"))
        # 2. bed from the blast to the end, ducked under the voice (sidechain on the programme audio)
        blast = t_cut + cd
        if a.bed_from_zero:
            start = max(0.0, (a.drop_at if a.drop_at is not None else a.bed_start) - blast); delay = 0; bed_len = new_total + 0.2
        else:
            start = a.bed_start; delay = blast; bed_len = new_total - blast + 0.2
        run("ffmpeg", "-v", "error", "-y", "-ss", str(start), "-i", a.bed, "-af",
            f"atrim=0:{bed_len},afade=t=in:d=0.3,afade=t=out:st={bed_len - 1.8}:d=1.6,loudnorm=I={a.bed_db}:TP=-3,"
            f"adelay={int(delay * 1000)}|{int(delay * 1000)},apad,atrim=0:{new_total}", "-ar", "48000", "-ac", "2", str(T / "bed.wav"))
        def mix(out, intro=None):
            ins_ = ["-i", str(T / "joined.mov"), "-i", str(T / "bed.wav")]
            fc = "[0:a]asplit=2[p][sc];[1:a][sc]sidechaincompress=threshold=0.06:ratio=2.5:attack=25:release=450[bd];"
            if intro:
                ins_ += ["-i", intro]
                fc += f"[2:a]aloop=loop=-1:size=2e9,atrim=0:{blast + 0.3},afade=t=out:st={blast - 0.1}:d=0.4,loudnorm=I=-19:TP=-3,aformat=channel_layouts=stereo[in];[p][bd][in]amix=inputs=3:normalize=0[m];"
            else:
                fc += "[p][bd]amix=inputs=2:normalize=0[m];"
            fc += "[m]loudnorm=I=-14:TP=-1.5:LRA=11,aresample=48000[a]"
            run("ffmpeg", "-v", "error", "-y", *ins_, "-filter_complex", fc, "-map", "0:v", "-map", "[a]", "-c:v", "libx264",
                "-crf", "18", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "256k", "-movflags", "+faststart", str(out))
        mix(O / ("ep3_main_FINAL.mp4" if a.bed_from_zero else "ep3_main_FOR_EDITS.mp4"))
        if a.intro_bed:
            mix(O / "ep3_main_PREVIEW_dhol.mp4", a.intro_bed)
    print(json.dumps({"insert_at_s": t_cut, "blast_at_s": round(t_cut + cd, 2), "duration_s": round(new_total, 2),
                      "desi_boyz_window_s": [0, round(t_cut + cd, 2)]}))


if __name__ == "__main__":
    main()
