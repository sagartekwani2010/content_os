"""Stage 6, cut_review: one self-contained HTML page showing every join, plus contact-sheet PNGs.

Per join: the last frame before and first frame after (as the viewer sees them, i.e. inside the
speaker crop), face-centre jump as % of the output frame width (and of the source width),
loudness of each side after gain matching, the words either side, and a 4 s audio clip of the
join as it will sound (crossfade included). Approval is a CLI command that writes approvals.json.
"""

from __future__ import annotations

import base64
import html
import shutil

import numpy as np

from . import media
from .face import get_detector
from .reel import Reel, read_json, write_json
from .render import build_voice


def _crop_frame(frame, seg: dict, src: dict):
    import cv2

    if frame is None:
        return None
    pw = frame.shape[1]
    scale = pw / (src["video"]["display_width"])
    c = seg["crop"]
    x0, y0 = int(c["x"] * scale), int(c["y"] * scale)
    x1, y1 = int((c["x"] + c["w"]) * scale), int((c["y"] + c["h"]) * scale)
    crop = frame[y0:y1, x0:x1]
    return cv2.resize(crop, (480, int(480 * crop.shape[0] / max(1, crop.shape[1]))))


def _face_out_x(face, seg: dict, src: dict, out_width: int, panel_w: int) -> float | None:
    if face is None:
        return None
    sw = src["video"]["display_width"]
    c = seg["crop"]
    x_src = face.cx * sw
    return ((x_src - c["x"]) * panel_w / c["w"]) / out_width


def _b64(data: bytes) -> str:
    return base64.b64encode(data).decode()


def _jpg(img) -> str:
    import cv2

    ok, buf = cv2.imencode(".jpg", img, [cv2.IMWRITE_JPEG_QUALITY, 82])
    return _b64(buf.tobytes()) if ok else ""


def measure_joins(reel: Reel, cfg: dict, cuts: dict, sources: dict) -> list[dict]:
    det = get_detector(cfg)
    fps = cuts["fps"]
    layout = cuts["layout"]
    panel_w = layout["panels"]["speaker"]["w"]
    out_w = layout["width"]
    segs = cuts["segments"]
    joins = []
    for j in cuts["joins"]:
        L, R = segs[j["left"]], segs[j["right"]]
        ls, rs = sources[L["source"]], sources[R["source"]]
        rec = {"index": j["index"], "time": j["time"], "left": {"take": L["take"], "beat": L["beat"]},
               "right": {"take": R["take"], "beat": R["beat"]}}
        frames = {}
        for side, seg, src, t in (("left", L, ls, L["out"] - 1.0 / fps), ("right", R, rs, R["in"])):
            fr = media.extract_frames(reel.resolve(src["proxy"]), [t])[0] if src.get("proxy") else None
            face = det.detect(fr) if (det is not None and fr is not None) else None
            rec[side].update({
                "face_cx_src": None if face is None else round(face.cx, 4),
                "face_x_out": None if face is None else round(_face_out_x(face, seg, src, out_w, panel_w), 4),
                "lufs_after_gain": None, "words": " ".join(w["text"] for w in (seg["words"][-8:] if side == "left" else seg["words"][:8])),
            })
            win = 1.5
            a = (seg["out"] - win) if side == "left" else seg["in"]
            ld = media.loudness(reel.resolve(src["wav48"]), max(seg["in"], a), min(win, seg["out"] - seg["in"]))
            if ld["integrated_lufs"] is not None:
                rec[side]["lufs_after_gain"] = round(media.finite(ld["integrated_lufs"]) + seg["gain_db"], 2)
            frames[side] = _crop_frame(fr, seg, src)
        lx, rx = rec["left"]["face_x_out"], rec["right"]["face_x_out"]
        rec["face_jump_pct_out"] = None if lx is None or rx is None else round(abs(lx - rx) * 100, 2)
        lc, rc = rec["left"]["face_cx_src"], rec["right"]["face_cx_src"]
        rec["face_jump_pct_src"] = None if lc is None or rc is None else round(abs(lc - rc) * 100, 2)
        la, ra = rec["left"]["lufs_after_gain"], rec["right"]["lufs_after_gain"]
        rec["level_step_db"] = None if la is None or ra is None else round(ra - la, 2)
        rec["_frames"] = frames
        joins.append(rec)
    return joins


def contact_sheets(reel: Reel, joins: list[dict]) -> list[str]:
    import cv2

    rdir = reel.work / "review"
    paths = []
    tiles = []
    for j in joins:
        fl, fr = j["_frames"].get("left"), j["_frames"].get("right")
        if fl is None or fr is None:
            continue
        h = max(fl.shape[0], fr.shape[0])
        pad = lambda im: cv2.copyMakeBorder(im, 0, h - im.shape[0], 0, 0, cv2.BORDER_CONSTANT, value=(0, 0, 0))
        row = np.hstack([pad(fl), np.full((h, 8, 3), 255, np.uint8), pad(fr)])
        bar = np.full((40, row.shape[1], 3), 30, np.uint8)
        label = (f"cut {j['index'] + 1}  {j['left']['take']} -> {j['right']['take']}  "
                 f"face jump {j['face_jump_pct_out'] if j['face_jump_pct_out'] is not None else 'n/a'}%  "
                 f"level step {j['level_step_db'] if j['level_step_db'] is not None else 'n/a'} dB")
        cv2.putText(bar, label, (8, 27), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1, cv2.LINE_AA)
        tile = np.vstack([bar, row])
        p = rdir / f"join_{j['index'] + 1:02d}.png"
        cv2.imwrite(str(p), tile)
        paths.append(reel.rel(p))
        tiles.append(tile)
    if tiles:
        w = max(t.shape[1] for t in tiles)
        sheet = np.vstack([cv2.copyMakeBorder(t, 0, 6, 0, w - t.shape[1], cv2.BORDER_CONSTANT, value=(255, 255, 255))
                           for t in tiles])
        p = rdir / "contact_sheet.png"
        cv2.imwrite(str(p), sheet)
        paths.insert(0, reel.rel(p))
    return paths


def join_audio(reel: Reel, voice, cuts: dict) -> dict[int, str]:
    out = {}
    for j in cuts["joins"]:
        a = max(0.0, j["time"] - 2.0)
        clip = reel.work / "review" / f"join_{j['index'] + 1:02d}.m4a"
        media.ffmpeg("-v", "error", "-ss", f"{a:.3f}", "-t", "4", "-i", str(voice), "-c:a", "aac", "-b:a", "96k", str(clip))
        out[j["index"]] = _b64(clip.read_bytes())
    return out


def run(reel: Reel, cfg: dict) -> dict:
    cuts = reel.need(reel.cuts_file, "cutpoints")
    sources = {s["id"]: s for s in reel.need(reel.sources_file, "ingest")["sources"]}
    rdir = reel.work / "review"
    if rdir.exists():
        shutil.rmtree(rdir)
    rdir.mkdir(parents=True)
    joins = measure_joins(reel, cfg, cuts, sources)
    sheets = contact_sheets(reel, joins)
    voice = build_voice(reel, cuts, sources, rdir / "voice_preview.wav")
    audio = join_audio(reel, voice, cuts)
    judge = read_json(reel.work / "judge_cuts.json") if (reel.work / "judge_cuts.json").exists() else None
    page = render_html(reel, cfg, cuts, joins, audio, judge)
    reel.review_html.write_text(page)
    data = {"cuts_sha256": cuts["sha256"], "contact_sheets": sheets,
            "joins": [{k: v for k, v in j.items() if k != "_frames"} for j in joins],
            "max_face_jump_pct_out": max([j["face_jump_pct_out"] for j in joins if j["face_jump_pct_out"] is not None], default=None),
            "max_level_step_db": max([abs(j["level_step_db"]) for j in joins if j["level_step_db"] is not None], default=None)}
    write_json(rdir / "review.json", data)
    return data


def _cls(v, warn, fail):
    if v is None:
        return "na"
    return "fail" if v > fail else "warn" if v > warn else "ok"


def render_html(reel: Reel, cfg: dict, cuts: dict, joins: list[dict], audio: dict, judge: dict | None) -> str:
    q = cfg["qa"]
    rejected = {}
    if judge:
        for r in judge.get("result", {}).get("reject_cuts", []):
            rejected[int(r.get("cut", -1))] = r.get("reason", "")
    rows = []
    for j in joins:
        imgs = "".join(f'<figure><img alt="{side}" src="data:image/jpeg;base64,{_jpg(j["_frames"][side])}"><figcaption>'
                       f'{"before" if side == "left" else "after"} &middot; {html.escape(j[side]["take"])}</figcaption></figure>'
                       for side in ("left", "right") if j["_frames"].get(side) is not None)
        fj = j["face_jump_pct_out"]
        jr = rejected.get(j["index"] + 1)
        rows.append(f"""
<section class="cut">
  <h2>Cut {j['index'] + 1} <small>at {j['time']:.2f} s &middot; beat {j['left']['beat']} &rarr; beat {j['right']['beat']}</small></h2>
  <div class="frames">{imgs or '<p class="na">no video frames</p>'}</div>
  <table>
    <tr><th>Face jump (output width)</th><td class="{_cls(fj, q['face_jump_warn_pct'], q['face_jump_fail_pct'])}">{'n/a (no face)' if fj is None else f'{fj:.2f}%'}</td>
        <th>Face jump (source width)</th><td>{'n/a' if j['face_jump_pct_src'] is None else f"{j['face_jump_pct_src']:.2f}%"}</td></tr>
    <tr><th>Level before (last 1.5 s)</th><td>{j['left']['lufs_after_gain']} LUFS</td>
        <th>Level after (first 1.5 s)</th><td>{j['right']['lufs_after_gain']} LUFS</td></tr>
    <tr><th>Level step</th><td class="{_cls(None if j['level_step_db'] is None else abs(j['level_step_db']), 2, 4)}">{j['level_step_db']} dB</td>
        <th>Crossfade</th><td>{cuts['joins'][j['index']]['crossfade_ms']} ms</td></tr>
  </table>
  <p class="words"><span>&hellip;{html.escape(j['left']['words'])}</span> &#9474; <span>{html.escape(j['right']['words'])}&hellip;</span></p>
  {f'<audio controls preload="none" src="data:audio/mp4;base64,{audio[j["index"]]}"></audio>' if j['index'] in audio else ''}
  {f'<p class="judge">Judge would reject: {html.escape(jr)}</p>' if jr else ''}
</section>""")
    seg_rows = "".join(
        f"<tr><td>{s['index'] + 1}</td><td>{s['beat']}</td><td>{html.escape(s['take'])}</td><td>{s['out_start']:.2f}</td>"
        f"<td>{s['duration']:.2f}</td><td>{s['gain_db']:+.1f}</td><td>{s['lead_s']:.3f}/{s['tail_s']:.3f}</td>"
        f"<td>{'yes' if s['crop_realigned'] else ''}</td><td>{html.escape(s['text'])}</td></tr>" for s in cuts["segments"])
    cmd = f"python -m content_os.pipeline approve {html.escape(str(reel.root))} cut_review --by YOUR_NAME"
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Cut review</title>
<style>
:root {{ --bg:#faf8f4; --fg:#1d1d1f; --muted:#6b6b70; --ok:#1e7d32; --warn:#a86b00; --fail:#b3261e; --card:#fff; --line:#e3ded5; }}
@media (prefers-color-scheme: dark) {{ :root {{ --bg:#141416; --fg:#ececf0; --muted:#9a9aa2; --card:#1e1e22; --line:#2e2e34; --ok:#6fcf7a; --warn:#f0b44c; --fail:#ff8a80; }} }}
body {{ background:var(--bg); color:var(--fg); font:15px/1.45 -apple-system, system-ui, sans-serif; margin:0; padding:24px 16px; }}
main {{ max-width:1080px; margin:0 auto; }}
h1 {{ font-size:24px; margin:0 0 4px; }} h2 {{ font-size:18px; margin:0 0 10px; }} h2 small {{ color:var(--muted); font-weight:400; }}
.cut {{ background:var(--card); border:1px solid var(--line); border-radius:10px; padding:16px; margin:16px 0; }}
.frames {{ display:flex; gap:8px; flex-wrap:wrap; }} figure {{ margin:0; flex:1 1 300px; }} img {{ width:100%; border-radius:6px; display:block; }}
figcaption {{ color:var(--muted); font-size:13px; }}
table {{ border-collapse:collapse; width:100%; margin:10px 0; font-size:14px; }} th,td {{ text-align:left; padding:4px 8px; border-bottom:1px solid var(--line); }}
th {{ color:var(--muted); font-weight:500; }}
.ok {{ color:var(--ok); }} .warn {{ color:var(--warn); font-weight:600; }} .fail {{ color:var(--fail); font-weight:700; }} .na {{ color:var(--muted); }}
.words span {{ background:color-mix(in srgb, var(--fg) 7%, transparent); padding:2px 6px; border-radius:4px; }}
.judge {{ color:var(--warn); }} code {{ background:var(--card); border:1px solid var(--line); padding:6px 8px; border-radius:6px; display:block; overflow-x:auto; }}
.scroll {{ overflow-x:auto; }}
</style></head><body><main>
<h1>Cut review</h1>
<p>{len(cuts['segments'])} segments, {len(joins)} cuts, {cuts['duration']:.2f} s. Reference loudness {cuts['reference_lufs']} LUFS
(per-take gain shown below). cuts.json sha256 <code style="display:inline">{cuts['sha256'][:16]}</code></p>
<p>Listen to every cut. When they are all acceptable, record the approval (render refuses without it):</p>
<code>{cmd}</code>
<div class="scroll"><table><tr><th>#</th><th>Beat</th><th>Take</th><th>Starts</th><th>Dur</th><th>Gain dB</th><th>Lead/tail s</th><th>Re-centred</th><th>Text</th></tr>{seg_rows}</table></div>
{''.join(rows) or '<p>No cuts: one segment only.</p>'}
</main></body></html>
"""
