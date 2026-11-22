"""Render an Instagram carousel from ``outputs/<id>/slides.json`` (spec ``content_os.carousel/spec@1``).

Canvas 1080x1350 (4:5) on the visuals paper background. Each slide = headline (+ yellow highlighter words) and
body at the top, then free-placed items (photo, sticky, quote, card, icon, arrow, ring, text). Stills are JPEG;
video slides are H.264 + silent AAC, 30 fps, BT.709, with the same layout drawing on (frame 0 already shows the
headline and body). Writes into the media folder: ``render/``, ``POST/`` (upload order), ``contact_sheet.jpg``,
``PREVIEW.html`` and ``qa.json``.
"""
from __future__ import annotations

import html
import json
import shutil
import subprocess
from pathlib import Path

import numpy as np
import skia

from content_os.pipeline import media
from content_os.visuals import rough as R
from content_os.visuals.elements import Element

from . import items as I

W, H, FPS = 1080, 1350, 30
MARGIN, UI_BOTTOM = 60, 180          # keep clear of the edges and Instagram's bottom UI
MIN_TEXT = 40
MIN_QUOTE = 44                       # verbatim output quotes: large enough to read on a phone
LOWER_THIRD = 1000                   # content should reach at least this far down (bottom UI zone starts at 1170)
SPEC = "content_os.carousel/spec@1"


def media_dir(spec: dict) -> Path:
    return Path(spec.get("media_dir") or f"~/Movies/ContentOS/{spec['id']}").expanduser()


class Slide:
    def __init__(self, sd: dict, spec: dict, total: int):
        self.sd, self.n = sd, sd["n"]
        self.video = sd.get("kind") == "video" or bool(sd.get("video"))
        self.duration = float(sd.get("duration", 6.0))
        self.boxes: list[I.TextBox] = []
        self.elements: list[Element] = []
        self.bottom_text = 0.0
        self._build(spec, total)

    # ---------------------------------------------------------------- layout
    def _build(self, spec: dict, total: int) -> None:
        sd, b = self.sd, self.boxes
        y = sd.get("text_top", 128)
        hs = sd.get("headline_size", 72)
        el, bottom = I.text_block("headline", sd["headline"], MARGIN, y, W - 2 * MARGIN, hs, R.INK, sd.get("headline_weight", "letters"),
                                  lh=1.12, highlight=sd.get("hl"), boxes=b)
        self.elements.append(el)
        if sd.get("body"):
            el, bottom = I.text_block("body", sd["body"], MARGIN, bottom + sd.get("body_gap", 62), W - 2 * MARGIN,
                                      sd.get("body_size", 48), R.INK, "regular", lh=1.2,
                                      highlight=sd.get("body_hl"), boxes=b)
            self.elements.append(el)
        self.bottom_text = bottom
        if sd.get("layout") == "before_after":
            self._before_after(sd, bottom)
        by_id: dict[str, Element] = {}
        for k, it in enumerate(sd.get("items", [])):
            el = self._item(it, spec, f"i{k}")
            by_id[it.get("id", f"i{k}")] = el
            self.elements.append(I.animate(el, it.get("at"), it.get("dur"), it.get("action")))
        for it in sd.get("rings", []):
            tgt = by_id[it["target"]]
            x, y0, w, h = tgt.bounds() if "rect" not in it else it["rect"]
            if "sub" in it:  # ring a sub-rectangle given relative to the target
                x, y0, w, h = x + it["sub"][0], y0 + it["sub"][1], it["sub"][2], it["sub"][3]
            el = I.ring("ring" + it["target"], (x, y0, w, h), it.get("color", "red"), it.get("pad", 14))
            self.elements.append(I.animate(el, it.get("at"), it.get("dur", 0.7)))
        page = f"{self.n}/{total}"
        self.boxes.append(I.TextBox("page", page, 30, (W - MARGIN - 60, H - 66, 60, 30), exempt=True))
        pg = I.Custom("page", (W - MARGIN - 60, H - 66, 60, 30),
                      lambda c, p, a, t: R.draw_text(c, page, W - MARGIN, H - 40, 30, R.GREY, weight="regular",
                                                     align="right", alpha=a))
        self.elements.append(pg)

    def _before_after(self, sd: dict, top: float) -> None:
        """Technique slide: a sticky with the copy-ready line, then a BEFORE card and an AFTER card, stacked with
        measured heights. On a video slide the sticky and BEFORE are on screen at frame 0 and AFTER writes on."""
        b, x, w = self.boxes, MARGIN + 10, W - 2 * MARGIN - 20
        qs = sd.get("quote_size", 44)
        y = top + sd.get("gap", 34)
        el, y = I.sticky("copy", x, y, w, [sd["copy"]], sd.get("copy_size", 44), sd.get("copy_title"),
                         tilt=-0.8, boxes=b, pad=22)
        self.elements.append(el)
        bf, af = sd["before"], sd["after"]
        el, y = I.quote_card("before", x, y + sd.get("card_gap", 30), w, bf["lines"], None, qs, boxes=b, border=R.GREY,
                             title=bf.get("title", "BEFORE"), title_col=R.RED, hl=bf.get("hl", ()))
        self.elements.append(el)
        el, y = I.quote_card("after", x, y + sd.get("card_gap", 30), w, af["lines"], None, qs, boxes=b, border=R.GREEN,
                             title=af.get("title", "AFTER"), title_col=R.GREEN, hl=af.get("hl", ()))
        if self.video:
            el.cues.append(I.Cue("draw", float(sd.get("after_at", 0.8)), float(sd.get("after_dur", 2.6))))
        self.elements.append(el)

    def _item(self, it: dict, spec: dict, key: str) -> Element:
        t, b = it["type"], self.boxes
        iid = it.get("id", key)
        if t == "photo":
            raw = it.get("path") or spec.get("cover_photo")  # one place to swap the cover photo
            if not raw:
                raise ValueError(f"slide {self.n}: photo item needs a path or a top-level cover_photo")
            path = Path(raw).expanduser() if "/" in raw else media_dir(spec) / "photo" / raw
            return I.photo(iid, path, it["rect"], it.get("tilt", -3), it.get("caption"), boxes=b)[0]
        if t == "sticky":
            return I.sticky(iid, it["x"], it["y"], it["w"], it["lines"], it.get("size", 42), it.get("title"),
                            I.col(it.get("color"), I.NOTE), it.get("tilt", -1.5), boxes=b)[0]
        if t == "quote":
            return I.quote_card(iid, it["x"], it["y"], it["w"], it["lines"], it.get("tag"), it.get("size", 46),
                                boxes=b, hl=it.get("hl", ()), border=I.col(it.get("border")),
                                tilt=it.get("tilt", 0.0), title=it.get("title"),
                                title_col=I.col(it.get("title_color"), I.col(it.get("border"))))[0]
        if t == "card":
            el = I.recipe_card(iid, it["x"], it["y"], it["w"], it["rows"], it.get("size", 44), boxes=b,
                               static_frame=bool(it.get("static_frame")))[0]
            return el
        if t == "text":
            return I.text_block(iid, it["text"], it["x"], it["y"], it.get("w", W - 2 * MARGIN), it.get("size", 44),
                                I.col(it.get("color")), it.get("weight", "regular"), it.get("align", "left"),
                                highlight=it.get("hl"), boxes=b)[0]
        if t == "icon":
            return I.icon(iid, it["name"], it["cx"], it["cy"], it.get("s", 1.0), it.get("color"))
        if t == "arrow":
            return I.line_arrow(iid, it["from"], it["to"], it.get("color"), it.get("bend", 0.0))
        raise ValueError(f"slide {self.n}: unknown item type {t!r}")

    # ---------------------------------------------------------------- drawing
    def frame(self, t: float, bg: skia.Image) -> np.ndarray:
        surf = skia.Surface(W, H)
        c = surf.getCanvas()
        c.drawImage(bg, 0, 0)
        for el in sorted(self.elements, key=lambda e: e.z):
            ac = el.appear_cue()
            if getattr(el, "render_before", False) and ac is not None and t < ac.t:
                el.paint(c, 0.0, 1.0, t)  # e.g. an empty card that the rows then write into
            else:
                el.render(c, t)
        return surf.makeImageSnapshot().toarray(colorType=skia.ColorType.kRGBA_8888_ColorType)

    def end_time(self) -> float:
        ends = [c.t + c.dur for el in self.elements for c in el.cues]
        return max(ends, default=0.0)


def _jpeg(arr: np.ndarray, out: Path, quality: int = 92) -> None:
    from PIL import Image
    out.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(arr).convert("RGB").save(out, "JPEG", quality=quality, subsampling=0)


def encode(slide: Slide, bg: skia.Image, out: Path, fps: int = FPS, crf: int = 16) -> dict:
    n = max(1, int(round(slide.duration * fps)))
    out.parent.mkdir(parents=True, exist_ok=True)
    cmd = [media.tool("ffmpeg"), "-hide_banner", "-nostdin", "-y", "-v", "error",
           "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{W}x{H}", "-r", str(fps), "-i", "-",
           "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo",
           "-vf", f"scale=out_color_matrix=bt709:out_range=tv,format=yuv420p,{media.SETPARAMS_709}",
           "-c:v", "libx264", "-preset", "medium", "-crf", str(crf), "-tune", "animation", "-profile:v", "high",
           *media.BT709_ARGS, "-r", str(fps), "-frames:v", str(n), "-c:a", "aac", "-b:a", "128k",
           "-t", f"{n / fps:.3f}", "-movflags", "+faststart", str(out)]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
    try:
        for i in range(n):
            proc.stdin.write(slide.frame(i / fps, bg).tobytes())
        proc.stdin.close()
    except BrokenPipeError:
        pass
    err = proc.stderr.read().decode()
    if proc.wait() != 0:
        raise media.MediaError(err[-2000:])
    return {"frames": n, "duration": round(n / fps, 3)}


# ---------------------------------------------------------------- QA

def layout_issues(slide: Slide) -> list[str]:
    """Text size, edge margins, the bottom UI zone and items that overlap the headline/body block."""
    out = []
    for tb in slide.boxes:
        x, y, w, h = tb.box
        if tb.exempt:
            continue
        if tb.size < MIN_TEXT:
            out.append(f"slide {slide.n}: {tb.item} text {tb.size:.0f}px < {MIN_TEXT}px: {tb.text!r}")
        if x < MARGIN - 1 or x + w > W - MARGIN + 1 or y < MARGIN - 1:
            out.append(f"slide {slide.n}: {tb.item} within {MARGIN}px of an edge: {tb.text!r}")
        if y + h > H - UI_BOTTOM:
            out.append(f"slide {slide.n}: {tb.item} in the bottom {UI_BOTTOM}px UI zone: {tb.text!r}")
    for el in slide.elements:
        if el.id in ("headline", "body", "page"):
            continue
        x, y, w, h = el.bounds()
        if y < slide.bottom_text + 10 and not el.id.startswith("ring"):
            out.append(f"slide {slide.n}: item {el.id} starts at y={y:.0f}, above the text block end {slide.bottom_text:.0f}")
        if y + h > H - UI_BOTTOM + 1:
            out.append(f"slide {slide.n}: item {el.id} reaches y={y + h:.0f} (UI zone starts {H - UI_BOTTOM})")
        if x < MARGIN - 20 or x + w > W - MARGIN + 20:
            out.append(f"slide {slide.n}: item {el.id} near the side edge (x {x:.0f}-{x + w:.0f})")
    for it in slide.sd.get("items", []):
        if it.get("type") == "quote" and it.get("size", 46) < MIN_QUOTE:
            out.append(f"slide {slide.n}: quote text {it.get('size')}px < {MIN_QUOTE}px (phone reading)")
    items = [e for e in slide.elements if e.id not in ("headline", "body", "page")]
    if items:
        low = max(e.bounds()[1] + e.bounds()[3] for e in items)
        if low < LOWER_THIRD:
            out.append(f"slide {slide.n}: content ends at y={low:.0f}; the lower third (to {H - UI_BOTTOM}) is empty")
    if slide.video:
        visible0 = [e for e in items if e.appear_cue() is None or e.appear_cue().t <= 0
                    or getattr(e, "render_before", False)]
        if not visible0:
            out.append(f"slide {slide.n}: video frame 0 shows only text; put the main diagram on screen at t=0")
    if slide.video and slide.end_time() > slide.duration - 0.8:
        out.append(f"slide {slide.n}: animation ends at {slide.end_time():.1f}s, less than 0.8 s before the end")
    return out


def probe(path: Path) -> dict:
    r = subprocess.run([media.tool("ffprobe"), "-v", "error", "-show_entries",
                        "stream=codec_type,codec_name,width,height,r_frame_rate,pix_fmt:format=duration,size",
                        "-of", "json", str(path)], capture_output=True, text=True, check=True)
    return json.loads(r.stdout)


# ---------------------------------------------------------------- packaging

def contact_sheet(frames: list[tuple[str, np.ndarray]], out: Path, cols: int = 4) -> None:
    from PIL import Image, ImageDraw
    tw, th = 360, 450
    rows = (len(frames) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * (tw + 16) + 16, rows * (th + 50) + 16), "#DDD8CC")
    d = ImageDraw.Draw(sheet)
    for i, (label, arr) in enumerate(frames):
        im = Image.fromarray(arr).convert("RGB").resize((tw, th))
        x, y = 16 + (i % cols) * (tw + 16), 16 + (i // cols) * (th + 50)
        sheet.paste(im, (x, y))
        d.text((x, y + th + 8), label, fill="#16150F")
    sheet.save(out, "JPEG", quality=90)


PREVIEW_CSS = """
:root{--bg:#EFEBE2;--fg:#16150F;--muted:#5F5A52;--card:#FFFFFF}
@media (prefers-color-scheme: dark){:root{--bg:#15171D;--fg:#F3F0E8;--muted:#A7ADB8;--card:#20242E}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--fg);font:16px/1.45 -apple-system,system-ui,sans-serif}
.phone{max-width:430px;margin:24px auto;padding:0 16px}
.head{display:flex;align-items:center;gap:10px;margin-bottom:10px;font-weight:600}
.dot{width:34px;height:34px;border-radius:50%;background:#C9C1B2}
.track{display:flex;overflow-x:auto;scroll-snap-type:x mandatory;border-radius:6px;background:#000;scrollbar-width:none}
.track::-webkit-scrollbar{display:none}
.track>*{flex:0 0 100%;width:100%;aspect-ratio:4/5;object-fit:cover;scroll-snap-align:start;display:block}
.nav{display:flex;justify-content:space-between;align-items:center;margin:10px 0}
.nav button{border:0;background:var(--card);color:var(--fg);border-radius:20px;padding:6px 14px;font-size:15px;cursor:pointer}
.count{color:var(--muted)}
.cap{white-space:pre-wrap;background:var(--card);padding:14px;border-radius:10px;margin-top:8px}
.pin{color:var(--muted);margin-top:12px;white-space:pre-wrap}
h2{font-size:14px;color:var(--muted);text-transform:uppercase;letter-spacing:.05em;margin:20px 0 6px}
"""


def preview_html(spec: dict, post: list[Path], caption: str, pinned: str) -> str:
    media_tags = []
    for p in post:
        rel = f"POST/{p.name}"
        if p.suffix == ".mp4":
            media_tags.append(f'<video src="{rel}" muted playsinline loop preload="auto"></video>')
        else:
            media_tags.append(f'<img src="{rel}" alt="slide {p.stem}">')
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>{html.escape(spec.get('title', spec['id']))}</title>
<style>{PREVIEW_CSS}</style></head><body><div class="phone">
<div class="head"><div class="dot"></div>{html.escape(spec.get('account', 'your account'))}</div>
<div class="track" id="t">{''.join(media_tags)}</div>
<div class="nav"><button onclick="go(-1)">&larr;</button><span class="count" id="c"></span><button onclick="go(1)">&rarr;</button></div>
<h2>Caption</h2><div class="cap">{html.escape(caption)}</div>
<h2>Pinned comment</h2><div class="pin">{html.escape(pinned)}</div>
<p class="count">Post: {html.escape(spec.get('post_at', ''))}. Videos play muted, as in the feed.</p>
</div><script>
const t=document.getElementById('t'),c=document.getElementById('c'),n=t.children.length;
function idx(){{return Math.round(t.scrollLeft/t.clientWidth)}}
function go(d){{t.scrollTo({{left:(idx()+d)*t.clientWidth,behavior:'smooth'}})}}
function upd(){{const i=idx();c.textContent=(i+1)+' / '+n;[...t.children].forEach((e,k)=>{{if(e.tagName==='VIDEO'){{if(k===i){{e.currentTime=0;e.play().catch(()=>{{}})}}else e.pause()}}}})}}
t.addEventListener('scroll',()=>{{clearTimeout(t._s);t._s=setTimeout(upd,120)}});upd();
</script></body></html>"""


def render(folder: Path, only: list[int] | None = None) -> dict:
    folder = Path(folder)
    spec = json.loads((folder / "slides.json").read_text())
    if spec.get("spec") != SPEC:
        raise ValueError(f"{folder}/slides.json: expected spec {SPEC!r}")
    R.set_theme("paper")
    out = media_dir(spec)
    rdir, pdir = out / "render", out / "POST"
    rdir.mkdir(parents=True, exist_ok=True)
    bg = R.paper_background(W, H)
    total = len(spec["slides"])
    report = {"slides": [], "issues": []}
    sheet = []
    for sd in spec["slides"]:
        sl = Slide(sd, spec, total)
        name = f"{sl.n:02d}_{sd.get('name', sd.get('kind', 'slide'))}"
        issues = layout_issues(sl)
        report["issues"] += issues
        entry = {"n": sl.n, "name": name, "video": sl.video, "issues": issues}
        if only and sl.n not in only:
            existing = next(iter(sorted(rdir.glob(name + ".*"))), None)
            entry["file"] = str(existing) if existing else None
            report["slides"].append(entry)
            if existing:  # reuse the earlier render on the contact sheet
                from PIL import Image
                srcs = ([(f"{name} first frame", rdir / "frames" / f"{name}_first.jpg"),
                         (f"{name} last frame", rdir / "frames" / f"{name}_last.jpg")] if sl.video
                        else [(name, existing)])
                sheet += [(lab, np.asarray(Image.open(p).convert("RGBA"))) for lab, p in srcs if p.exists()]
            continue
        if sl.video:
            f = rdir / f"{name}.mp4"
            entry.update(encode(sl, bg, f, spec.get("fps", FPS)))
            first, last = sl.frame(0.0, bg), sl.frame(sl.duration - 1 / FPS, bg)
            _jpeg(first, rdir / "frames" / f"{name}_first.jpg")
            _jpeg(last, rdir / "frames" / f"{name}_last.jpg")
            sheet += [(f"{name} first frame", first), (f"{name} last frame", last)]
        else:
            f = rdir / f"{name}.jpg"
            arr = sl.frame(1e6, bg)
            _jpeg(arr, f)
            sheet.append((name, arr))
        entry["file"] = str(f)
        report["slides"].append(entry)
    # package: POST/ in upload order, contact sheet, preview
    if pdir.exists():
        shutil.rmtree(pdir)
    pdir.mkdir(parents=True)
    post = []
    for e in report["slides"]:
        if e.get("file"):
            dst = pdir / Path(e["file"]).name
            shutil.copy2(e["file"], dst)
            post.append(dst)
            e["probe"] = probe(dst)
    if sheet:
        contact_sheet(sheet, out / "contact_sheet.jpg")
    cap = (folder / "CAPTION.txt").read_text() if (folder / "CAPTION.txt").exists() else ""
    pin = (folder / "PINNED_COMMENT.txt").read_text() if (folder / "PINNED_COMMENT.txt").exists() else ""
    (out / "PREVIEW.html").write_text(preview_html(spec, post, cap, pin))
    (out / "qa.json").write_text(json.dumps(report, indent=1))
    return report
