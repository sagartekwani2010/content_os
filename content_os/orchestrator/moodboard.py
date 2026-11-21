"""Mood board + keyframes: written by Fable from the approved script/screenplay, rendered as a page
(MOODBOARD.html) the creator approves at the ``moodboard`` gate. Later stages read moodboard.json:
the shoot plan takes its shot list, the visuals drafter its per-beat keyframes, the edit its
transitions and sound.

Keyframe images: any ``moodboard/KFxx.png`` next to the reel is shown on the board (rendered stills
from content_os.visuals, demo screenshots). Frames without one are drawn as layout mock-ups;
``render_frames`` turns those mock-ups into PNGs with headless Chrome when it is installed.
"""

from __future__ import annotations

import html
import json
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Any

CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
E = html.escape


def load(reel_dir: Path) -> dict[str, Any] | None:
    p = Path(reel_dir) / "moodboard.json"
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None


def keyframes_for_beat(mb: dict[str, Any] | None, beat: int) -> list[dict[str, Any]]:
    return [k for k in (mb or {}).get("keyframes", []) if beat in (k.get("beats") or [])]


def _swatch(entry: str) -> str:
    hexv = entry.split()[0] if entry.startswith("#") else "#888"
    return f'<div class="sw"><span style="background:{E(hexv)}"></span>{E(entry)}</div>'


PERSON = ("<svg class='person' viewBox='0 0 200 160' preserveAspectRatio='xMidYMax meet'>"
          "<circle cx='100' cy='52' r='30' fill='#3a404c' stroke='#8c94a3' stroke-width='2'/>"
          "<path d='M30 160 C35 105 70 92 100 92 C130 92 165 105 170 160 Z' fill='#2c313b' stroke='#8c94a3' stroke-width='2'/></svg>")


def _device(lay: str, k: dict[str, Any]) -> str:
    body = E(k.get("top_visual") or k.get("shot", ""))
    cls = "laptop" if "laptop" in (k.get("shot", "") + k.get("top_visual", "")).lower() else "phone"
    return f'<div class="dev {cls}"><div class="scr">{body}</div></div>'


def frame_html(k: dict[str, Any], accent: str = "#FFD23F", img: str | None = None) -> str:
    """One 9:16 storyboard frame: the image if there is one, otherwise a schematic sketch of the layout."""
    if img:
        return f'<div class="frame"><img src="{E(img)}" alt="{E(k["id"])}"></div>'
    lay = (k.get("layout") or "split").lower()
    ost = f'<div class="ost" style="color:{E(accent)}">{E(k.get("on_screen_text", ""))}</div>' if k.get("on_screen_text") else ""
    emo = f'<div class="emochip">{E(k.get("emotion", ""))}</div>' if k.get("emotion") else ""
    note = f'<div class="note">{E(k.get("shot", ""))}</div>'
    who = f'<div class="dir">{E(k.get("creator_direction", ""))}</div>' if k.get("creator_direction") else ""
    text = (k.get("shot", "") + " " + k.get("top_visual", "")).lower()
    if lay == "card":
        inner = f'<div class="card" style="color:{E(accent)}">{E(k.get("on_screen_text") or k.get("shot", ""))}</div>'
        ost = ""
    elif lay == "split":
        top = _device(lay, k) if any(w in text for w in ("screen", "phone", "laptop", "gpt", "chatgpt")) else \
            f'<div class="draw">{E(k.get("top_visual") or k.get("shot", ""))}</div>'
        inner = f'<div class="top">{ost}{top}</div><div class="bot">{PERSON}{who}</div>'
        ost = ""
    elif lay in ("screen_recording", "full_visual") and any(w in text for w in ("screen", "phone", "laptop", "gpt", "chatgpt", "recording")):
        inner = f'<div class="full">{_device(lay, k)}</div>'
    elif lay in ("broll", "full_visual"):
        inner = f'<div class="full"><div class="draw big">{E(k.get("top_visual") or k.get("shot", ""))}</div></div>'
    else:  # full_creator and anything else: the creator in frame, props described
        prop = f'<div class="prop">{E(k.get("top_visual"))}</div>' if k.get("top_visual") else ""
        inner = f'<div class="full creator">{prop}{PERSON}{who}</div>'
    return f'<div class="frame">{emo}{ost}{inner}{note}</div>'


CSS = """
:root{--bg:#0f1115;--panel:#171a21;--ink:#f3f1ea;--mut:#9aa0ab;--line:#2a2f3a}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.45 Inter,system-ui,sans-serif}
header{padding:28px 20px 8px;max-width:1300px;margin:auto}h1{font:700 34px 'Barlow Condensed',sans-serif;letter-spacing:.5px;margin:0}
.meta{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:12px;max-width:1300px;margin:12px auto;padding:0 20px}
.box{background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:12px 14px}.box h3{margin:0 0 6px;font-size:13px;color:var(--mut);text-transform:uppercase;letter-spacing:1px}
.sw{display:flex;gap:8px;align-items:center;margin:3px 0}.sw span{width:22px;height:22px;border-radius:5px;border:1px solid #fff3}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(230px,1fr));gap:18px;max-width:1300px;margin:18px auto 60px;padding:0 20px}
.kf{background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:10px}
.kh{display:flex;justify-content:space-between;font-weight:600;margin-bottom:6px}.emo{color:#FFD23F}
.frame{aspect-ratio:9/16;background:radial-gradient(120% 80% at 50% 30%,#1b2029,#0b0c10);border-radius:8px;overflow:hidden;display:flex;flex-direction:column;border:1px solid #fff1;position:relative}
.emochip{position:absolute;top:6px;left:6px;font-size:9px;padding:2px 6px;border-radius:9px;background:#FFD23F22;color:#FFD23F;border:1px solid #FFD23F55;z-index:3}
.ost{position:absolute;top:16%;left:6%;right:6%;text-align:center;font:800 22px/1 'Barlow Condensed',sans-serif;text-transform:uppercase;text-shadow:0 2px 0 #000,0 0 8px #000;z-index:3}
.note{position:absolute;bottom:0;left:0;right:0;font-size:9px;line-height:1.25;color:#aab1bd;background:#000a;padding:4px 6px;z-index:3}
.person{width:70%;max-height:62%;display:block;margin:0 auto}
.creator{justify-content:flex-end;align-items:center;padding-bottom:16%}
.prop{font-family:'Caveat',cursive;font-size:14px;line-height:1.05;color:#f3f1ea;border:2px solid #f3f1ea;border-radius:6px;padding:6px;background:#ffffff10;max-width:80%;margin:0 auto 8px;transform:rotate(-2deg)}
.top .ost{position:static;margin:0 0 6px}
.dev{margin:auto;border:3px solid #cfd3da;border-radius:14px;background:#0e1116;padding:6px;display:flex}
.dev.phone{width:62%;aspect-ratio:9/17}.dev.laptop{width:90%;aspect-ratio:16/10;border-radius:6px}
.scr{flex:1;font:11px/1.3 ui-monospace,Menlo,monospace;color:#9ef0c9;overflow:hidden}
.draw.big{font-size:17px;margin:auto 6%}
.frame img{width:100%;height:100%;object-fit:cover}
.top,.bot{flex:1;position:relative;padding:8px;display:flex;flex-direction:column;justify-content:center}.top{border-bottom:2px solid #fff2}
.bot{background:linear-gradient(#20242c,#14161b);align-items:center;justify-content:flex-end;padding-bottom:14%}
.face{width:44%;aspect-ratio:1;border-radius:50%;border:2px dashed #fff5;display:flex;align-items:center;justify-content:center;color:var(--mut);font-size:11px}
.dir{font-size:10px;color:var(--mut);text-align:center;margin-top:6px}
.ost{font:700 19px/1.05 'Barlow Condensed',sans-serif;text-transform:uppercase;color:#FFD23F;margin-bottom:6px}
.draw{font-size:11px;color:#cfd3da;border:1.5px solid #6ee7f9;border-radius:6px;padding:6px;font-family:'Caveat',cursive;font-size:15px;line-height:1.1}
.full{flex:1;padding:10px;display:flex;flex-direction:column;justify-content:center;gap:8px}.tag{font-size:10px;color:#6ee7f9;text-transform:uppercase;letter-spacing:1px}
.card{flex:1;display:flex;align-items:center;justify-content:center;text-align:center;padding:12px;font:800 34px/0.95 'Barlow Condensed',sans-serif;text-transform:uppercase}
dl{margin:8px 0 0;font-size:12px}dt{color:var(--mut);float:left;width:64px}dd{margin:0 0 3px 68px}
@media (max-width:520px){.grid{grid-template-columns:1fr 1fr;gap:10px;padding:0 12px}}
"""


def board_html(mb: dict[str, Any], title: str, images: dict[str, str] | None = None) -> str:
    images = images or {}
    accent = next((c.split()[0] for c in mb.get("palette", []) if "accent" in c.lower() and c.startswith("#")), "#FFD23F")
    kfs = []
    for k in mb["keyframes"]:
        rows = "".join(f"<dt>{E(lbl)}</dt><dd>{E(str(k.get(key)))}</dd>" for lbl, key in (
            ("shot", "shot"), ("visual", "top_visual"), ("template", "template"), ("motion", "motion"),
            ("in", "transition_in"), ("sfx", "sfx"), ("music", "music"), ("creator", "creator_direction"))
            if k.get(key))
        beats = ",".join(str(b) for b in k.get("beats", []))
        kfs.append(f'<div class="kf"><div class="kh"><span>{E(k["id"])} · {k["time_s"]:.0f}s'
                   f'{" · beat " + beats if beats else ""}</span><span class="emo">{E(k.get("emotion", ""))}</span></div>'
                   f'{frame_html(k, accent, images.get(k["id"]))}<dl>{rows}</dl></div>')
    meta = [("Concept", E(mb.get("concept", ""))), ("Palette", "".join(_swatch(c) for c in mb.get("palette", []))),
            ("Type", E(mb.get("typography", ""))), ("Texture", E(mb.get("texture", ""))),
            ("Music", E(mb.get("music", ""))), ("SFX", "<br>".join(E(s) for s in mb.get("sfx_palette", []))),
            ("Pacing", E(mb.get("pacing", ""))),
            ("References", "<br>".join(E(s) for s in mb.get("references", []))),
            ("Shot list", "<ol>" + "".join(f"<li>{E(s)}</li>" for s in mb.get("shot_list", [])) + "</ol>"),
            ("Risks", "<br>".join(E(s) for s in mb.get("risks", [])))]
    boxes = "".join(f'<div class="box"><h3>{h}</h3>{v}</div>' for h, v in meta if v)
    return ("<!doctype html><html><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'>"
            f"<title>{E(title)}</title><link rel='preconnect' href='https://fonts.googleapis.com'>"
            "<link href='https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@600;700;800&family=Caveat:wght@500"
            "&family=Inter:wght@400;600&display=swap' rel='stylesheet'>"
            f"<style>{CSS}</style></head><body><header><h1>{E(title)}</h1></header>"
            f"<section class='meta'>{boxes}</section><section class='grid'>{''.join(kfs)}</section></body></html>")


def find_images(reel_dir: Path) -> dict[str, str]:
    d = Path(reel_dir) / "moodboard"
    return {p.stem: f"moodboard/{p.name}" for p in sorted(d.glob("KF*.png"))} if d.is_dir() else {}


def write_board(reel_dir: Path, mb: dict[str, Any], title: str) -> dict[str, Path]:
    reel_dir = Path(reel_dir)
    js = reel_dir / "moodboard.json"
    js.write_text(json.dumps(mb, indent=2, ensure_ascii=False), encoding="utf-8")
    page = reel_dir / "MOODBOARD.html"
    page.write_text(board_html(mb, title, find_images(reel_dir)), encoding="utf-8")
    return {"moodboard.json": js, "MOODBOARD.html": page}


def render_frames(reel_dir: Path, mb: dict[str, Any], width: int = 720) -> list[Path]:
    """Mock-up PNGs (moodboard/KFxx.png) for keyframes that have no image yet; needs Chrome."""
    if not Path(CHROME).exists():
        return []
    out_dir = Path(reel_dir) / "moodboard"
    out_dir.mkdir(exist_ok=True)
    have = find_images(reel_dir)
    accent = next((c.split()[0] for c in mb.get("palette", []) if "accent" in c.lower() and c.startswith("#")), "#FFD23F")
    made = []
    with tempfile.TemporaryDirectory() as tmp:
        for k in mb["keyframes"]:
            if k["id"] in have:
                continue
            page = Path(tmp) / f"{k['id']}.html"
            page.write_text("<!doctype html><html><head><meta charset='utf-8'>"
                            "<link href='https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@700;800&family=Caveat:wght@500"
                            "&family=Inter:wght@400;600&display=swap' rel='stylesheet'>"
                            f"<style>{CSS} body{{margin:0}} .frame{{width:100vw;height:100vh;border-radius:0}}"
                            f".ost{{font-size:9vw}} .draw{{font-size:5vw}} .card{{font-size:16vw}} .dir{{font-size:3.2vw}} .note{{font-size:3vw}} .emochip{{font-size:3vw}} .prop{{font-size:5vw}} .scr{{font-size:3.4vw}}</style>"
                            f"</head><body>{frame_html(k, accent)}</body></html>", encoding="utf-8")
            png = out_dir / f"{k['id']}.png"
            subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars", f"--screenshot={png}",
                            f"--window-size={width},{width * 16 // 9}", "--virtual-time-budget=3000", page.as_uri()],
                           capture_output=True, timeout=60)
            if png.exists():
                made.append(png)
    return made
