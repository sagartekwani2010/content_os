"""Build a reel's playable MOODBOARD.html from a small JSON spec (the standard since Gym Jarvis Ep 3, 20 Nov 2026).

The page shows, in this order: title + cover + one-line flow, the animatic (every rendered visual in story order),
music previews (same animatic under each candidate, drop placed on the key moment, with measured energy lift),
every visual clip playing with its beat, length and data source, palette + type, and the sound-design table.

Usage: python scripts/moodboard/build_moodboard.py <reel_dir>/moodboard_spec.json
Writes <reel_dir>/MOODBOARD.html next to the spec. Media paths in the spec are relative to the reel folder.

Spec keys (see outputs/workout-analyser-reel/moodboard_spec.json for a full example):
  title, subtitle, cover, lede[], pills[{text,color}], flow, previews[{src,title,note,recommended}], previews_note,
  animatic{src,title,note}, music_note, music[{src,title,meta,license,recommended}],
  visuals[{src,beat,desc,source}], palette[{name,hex,use}], type_note, sfx[[moment,sfx,level]], audio_note,
  theme{bg,panel,accent,warn,stop,ok,ink,dim}
"""
import html, json, sys
from pathlib import Path

DEFAULT_THEME = {"bg": "#03121c", "panel": "#062233", "accent": "#35e0ff", "warn": "#ffb23e", "stop": "#ff3b30",
                 "ok": "#3dffa8", "ink": "#ebfaff", "dim": "#7fa3b3"}
e = html.escape


def build(spec):
    t = DEFAULT_THEME | spec.get("theme", {})
    pills = "".join(f'<span class="pill" style="color:{p.get("color", t["accent"])}">{e(p["text"])}</span>' for p in spec.get("pills", []))
    lede = "".join(f'<p class="lede">{e(x)}</p>' for x in spec.get("lede", []))
    music = "".join(f'''<figure class="mcard{' rec' if m.get('recommended') else ''}"><video src="{e(m['src'])}" controls preload="metadata" playsinline></video>
<figcaption><b>{'RECOMMENDED · ' if m.get('recommended') else ''}{e(m['title'])}</b><span>{e(m.get('meta', ''))}</span><em>{e(m.get('license', ''))}</em></figcaption></figure>''' for m in spec.get("music", []))
    cards = "".join(f'''<figure class="card"><video src="{e(v['src'])}" muted loop playsinline autoplay preload="metadata"></video>
<figcaption><b>{i + 1:02d} · {e(v['beat'])}</b><span>{e(v.get('desc', ''))}</span><em>{e(v.get('source', ''))}</em><code>{e(v['src'])}</code></figcaption></figure>''' for i, v in enumerate(spec.get("visuals", [])))
    pal = "".join(f'<div class="sw"><i style="background:{p["hex"]}"></i><b>{e(p["name"])}</b><br>{p["hex"]}<br><span style="color:var(--dim)">{e(p.get("use", ""))}</span></div>' for p in spec.get("palette", []))
    sfx = "".join(f"<tr><td>{e(a)}</td><td>{e(b)}</td><td>{e(c)}</td></tr>" for a, b, c in spec.get("sfx", []))
    pv = spec.get("previews", [])
    prev = ("<h2>Full previews (dummy voice)</h2><p class='lede'>" + e(spec.get("previews_note", "")) + "</p><div class='grid' style='grid-template-columns:repeat(auto-fill,minmax(300px,1fr))'>" +
            "".join(f'''<figure class="mcard{' rec' if x.get('recommended') else ''}"><video src="{e(x['src'])}" controls preload="metadata" playsinline style="aspect-ratio:9/16"></video>
<figcaption><b>{'WATCH FIRST · ' if x.get('recommended') else ''}{e(x['title'])}</b><span>{e(x.get('note', ''))}</span></figcaption></figure>''' for x in pv) + "</div>") if pv else ""
    an = spec.get("animatic")
    anim = (f'<h2>Animatic (visual order, no voice)</h2><div class="grid" style="grid-template-columns:minmax(0,560px)"><figure class="card">'
            f'<video src="{e(an["src"])}" controls muted playsinline preload="metadata"></video><figcaption><b>{e(an.get("title", "Animatic"))}</b>'
            f'<span>{e(an.get("note", ""))}</span></figcaption></figure></div>') if an else ""
    cover = f'<img src="{e(spec["cover"])}" alt="Cover" onerror="this.style.display=\'none\'">' if spec.get("cover") else ""
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(spec.get("page_title", "Reel Moodboard"))}</title>
<link href="https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@500;700;800&family=Inter:wght@400;600&display=swap" rel="stylesheet">
<style>
:root{{--bg:{t["bg"]};--panel:{t["panel"]};--cyan:{t["accent"]};--amber:{t["warn"]};--red:{t["stop"]};--green:{t["ok"]};--ink:{t["ink"]};--dim:{t["dim"]}}}
*{{box-sizing:border-box}} body{{margin:0;background:var(--bg);color:var(--ink);font-family:Inter,system-ui,sans-serif;
background-image:linear-gradient(rgba(127,163,179,.06) 1px,transparent 1px),linear-gradient(90deg,rgba(127,163,179,.06) 1px,transparent 1px);background-size:48px 48px}}
main{{max-width:1240px;margin:0 auto;padding:32px 16px 80px}}
h1,h2,b{{font-family:"Barlow Condensed",sans-serif;text-transform:uppercase;letter-spacing:.02em}}
h1{{font-size:clamp(40px,7vw,76px);margin:0;line-height:.95}} h1 span{{color:var(--cyan)}}
h2{{font-size:30px;margin:48px 0 14px;color:var(--cyan);border-left:4px solid var(--cyan);padding-left:12px}}
.lede{{color:var(--dim);max-width:820px;font-size:16px;line-height:1.55}}
.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(270px,1fr));gap:16px}}
.card,.mcard{{margin:0;background:var(--panel);border:1px solid color-mix(in srgb,var(--cyan) 35%,transparent)}}
video{{width:100%;display:block;background:#000;aspect-ratio:9/8}}
figcaption{{padding:12px 14px 14px;display:grid;gap:5px;font-size:13.5px;line-height:1.45}}
figcaption b{{font-size:20px;color:var(--ink)}} figcaption span{{color:var(--ink);opacity:.85}} figcaption em{{color:var(--amber);font-style:normal;font-size:12.5px}}
code{{color:var(--dim);font-size:11.5px}}
.mcard.rec{{border:2px solid var(--green)}} .mcard.rec b{{color:var(--green)}}
.row{{display:flex;flex-wrap:wrap;gap:10px}} .sw{{width:150px;padding:10px;border:1px solid rgba(255,255,255,.15);font-size:13px}}
.sw i{{display:block;height:46px;margin-bottom:8px}}
table{{width:100%;border-collapse:collapse;font-size:14px}} td,th{{border-bottom:1px solid color-mix(in srgb,var(--cyan) 20%,transparent);padding:9px 8px;text-align:left;vertical-align:top}}
th{{font-family:"Barlow Condensed";text-transform:uppercase;color:var(--cyan);font-size:16px}}
.hero{{display:grid;grid-template-columns:minmax(0,1.1fr) minmax(0,1fr);gap:22px;align-items:center;margin-top:22px}}
.hero img{{width:100%;max-width:360px;border:2px solid var(--red)}}
.pill{{display:inline-block;padding:3px 10px;border:1px solid currentColor;font-family:"Barlow Condensed";font-weight:700;margin:2px}}
@media (max-width:720px){{.hero{{grid-template-columns:1fr}}}}
</style></head><body><main>
<h1>{e(spec.get("title", ""))}<br><span>{e(spec.get("subtitle", ""))}</span></h1>
<div class="hero"><div>{lede}<p class="lede">{pills}</p><p class="lede">{e(spec.get("flow", ""))}</p></div>{cover}</div>
{prev}
{anim}
<h2>Music (pick one)</h2><p class="lede">{e(spec.get("music_note", ""))}</p><div class="grid">{music}</div>
<h2>Visual clips</h2><div class="grid">{cards}</div>
<h2>Palette &amp; type</h2><div class="row">{pal}</div><p class="lede">{e(spec.get("type_note", ""))}</p>
<h2>Sound design</h2><table><tr><th>Moment</th><th>SFX</th><th>Level</th></tr>{sfx}</table><p class="lede">{e(spec.get("audio_note", ""))}</p>
</main></body></html>'''


if __name__ == "__main__":
    sp = Path(sys.argv[1]).resolve()
    out = sp.parent / "MOODBOARD.html"
    out.write_text(build(json.loads(sp.read_text())))
    print(out)
