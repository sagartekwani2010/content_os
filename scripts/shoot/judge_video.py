"""Fable 5.2 watches a reel preview end to end and judges engagement + editing.

Frames are sampled every --every seconds into timestamped sheets; the spoken timeline (timeline.json from
make_preview.py) is passed alongside. Fable returns per-persona engagement, the overall score and concrete, timestamped
edit fixes (cuts, holds, order, text, SFX, music, pacing). Writes <out_dir>/JUDGE_<stem>.json and .md.

Usage: python scripts/shoot/judge_video.py <video.mp4> <timeline.json> <out_dir> [--every 1.0] [--notes "..."]
"""
import argparse, json, re, subprocess, tempfile, time
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

PANEL = ("Panel (Indian Instagram viewers scrolling at 10 pm, English only): 1 TCS support engineer Pune 24; 2 CA Ahmedabad 31; "
         "3 HR exec Bengaluru 28; 4 bank RM Lucknow 35; 5 school teacher Jaipur 38; 6 BTech final-year Hyderabad 21; "
         "7 FP&A analyst Gurgaon 25; 8 IB/equity research associate Mumbai 33; 9 Big 4 consulting analyst Bengaluru 24; "
         "10 strategy consulting manager Mumbai 32; 11 performance marketing exec Delhi 26; 12 FMCG brand manager Mumbai 34; "
         "13 startup backend dev Bengaluru 27; 14 ML engineer Hyderabad 30; 15 gym trainer Delhi 29 (non-tech); 16 BCom student Kolkata 20. "
         "Groups: mass 2-5,12,15,16; fin-consult-mktg 7-12; builders 1,6,13,14.")

SYSTEM = f"""You are Claude Fable 5.2 judging an Instagram reel PREVIEW before the creator records his talking head.
Use the Read tool to open every frame sheet in order (timestamps are printed on each frame). The top half of each frame is
the visual; the bottom half says YOUR TAKE (the creator's face goes there later). The spoken lines with their times are
given in TIMELINE (a temporary computer voice reads them now; the creator's own voice will replace it).
{PANEL}
1. Score ENGAGEMENT 0-10 for each persona as if the finished reel (with the creator's face and voice) met them cold in
   their feed: 10 = holds past 3 s, watches to the end, and would send, save, follow or comment. Be strict: an ordinary
   good reel scores 5-6. Give the drop-off second (or "none").
2. Give EDIT FIXES: concrete, timestamped changes to the edit only (cut/trim/hold lengths, order of shots, on-screen text
   wording or size, a punch-in, SFX or music moments, pacing, where a visual is unreadable or too long). The script and
   the facts are locked by the creator; do not rewrite lines unless a line is unreadable on screen.
Reply with JSON only:
{{"personas":[{{"id":int,"score":num,"drop_s":str,"why":str}}],"groups":{{"mass":num,"fin_consult_mktg":num,"builders":num}},
 "overall":num,"strongest_moment":str,"weakest_moment":str,
 "edit_fixes":[{{"at_s":str,"fix":str,"why":str,"impact":"high"|"medium"|"low"}}],
 "predicted_overall_after_fixes":num}}"""


def sheets(video, every, out):
    out.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        subprocess.run(["ffmpeg", "-v", "error", "-i", str(video), "-vf", f"fps={1 / every},scale=270:-2", f"{tmp}/f_%04d.jpg"], check=True)
        fr = sorted(Path(tmp).glob("f_*.jpg"))
        try:
            font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 20)
        except OSError:
            font = ImageFont.load_default()
        paths, per = [], 8
        for s in range(0, len(fr), per):
            ims = [Image.open(f) for f in fr[s:s + per]]; w, h = ims[0].size
            sheet = Image.new("RGB", (4 * w, 2 * h))
            for k, im in enumerate(ims):
                x, y = (k % 4) * w, (k // 4) * h; sheet.paste(im, (x, y)); d = ImageDraw.Draw(sheet)
                d.rectangle([x, y, x + 74, y + 26], fill="black"); d.text((x + 4, y + 3), f"{(s + k) * every:4.1f}s", fill="yellow", font=font)
            p = out / f"sheet_{s // per + 1:02d}.jpg"; sheet.save(p, quality=85); paths.append(p)
    return paths


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("video"); ap.add_argument("timeline"); ap.add_argument("out")
    ap.add_argument("--every", type=float, default=1.0); ap.add_argument("--notes", default="")
    ap.add_argument("--model", default="claude-fable-5-2"); ap.add_argument("--final", action="store_true", help="finished reel: face and voice are real")
    a = ap.parse_args(); out = Path(a.out); stem = Path(a.video).stem
    ps = sheets(a.video, a.every, out / f"sheets_{stem}")
    tl = json.loads(Path(a.timeline).read_text())
    timeline = "\n".join(f"{x['t0']:5.1f}s-{x['t0'] + x['dur']:5.1f}s beat {x['beat']}: {x['text'] or '(no line)'}  [clips: {', '.join(x['clips'])}]" for x in tl)
    if a.final:
        global SYSTEM
        SYSTEM = SYSTEM.replace("judging an Instagram reel PREVIEW before the creator records his talking head", "judging the FINISHED Instagram reel (real face and voice, bottom half)").replace("the bottom half says YOUR TAKE (the creator's face goes there later)", "the bottom half is the creator talking").replace("(a temporary computer voice reads them now; the creator's own voice will replace it)", "(as spoken in the final cut)")
    prompt = (f"Reel preview: {Path(a.video).name}, {tl[-1]['t0'] + tl[-1]['dur']:.1f} s.\nTIMELINE:\n{timeline}\n\n"
              f"Music: a desi dhol beat (stand-in for the Desi Boyz beat) to the blast, then an electronic bed. {a.notes}\n\n"
              "FRAME SHEETS (in order):\n" + "\n".join(str(p) for p in ps))
    cmd = ["claude", "-p", prompt, "--system-prompt", SYSTEM, "--model", a.model, "--output-format", "json",
           "--no-session-persistence", "--tools", "Read", "--allowedTools", "Read", "--add-dir", str(ps[0].parent)]
    for attempt in range(6):
        with tempfile.TemporaryDirectory() as cwd:
            p = subprocess.run(cmd, capture_output=True, text=True, timeout=1800, cwd=cwd)
        try:
            o = json.loads(p.stdout)
            if not o.get("is_error"):
                res = json.loads(re.search(r"\{.*\}", o["result"], re.S).group(0)); break
        except Exception:  # noqa: BLE001
            pass
        time.sleep([0, 600, 1800, 3600, 3600, 3600][attempt])
    else:
        raise SystemExit("judge failed: " + p.stdout[-400:])
    (out / f"JUDGE_{stem}.json").write_text(json.dumps(res, indent=1))
    md = [f"# Fable 5.2 judge: {stem}", f"Overall {res['overall']} (mass {res['groups']['mass']} · fin/consult/mktg {res['groups']['fin_consult_mktg']} · builders {res['groups']['builders']}); predicted after fixes {res.get('predicted_overall_after_fixes')}",
          f"Strongest: {res['strongest_moment']}", f"Weakest: {res['weakest_moment']}", "", "## Edit fixes"]
    md += [f"- [{f['impact']}] {f['at_s']}: {f['fix']} ({f['why']})" for f in res["edit_fixes"]]
    md += ["", "## Personas"] + [f"- {x['id']}: {x['score']} · drop {x['drop_s']} · {x['why']}" for x in res["personas"]]
    (out / f"JUDGE_{stem}.md").write_text("\n".join(md)); print("\n".join(md[:4]))


if __name__ == "__main__":
    main()
