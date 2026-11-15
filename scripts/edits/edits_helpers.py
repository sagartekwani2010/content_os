"""Helpers for driving the Edits Mac app through its local automation server.

These are the calls that worked while building the "Agentic AI mission" reel on 2026-11-15, collected
into functions. They were run as inline scripts that day, not as this module, so treat the module as
untested until the first reel built with it passes.

Needs: Edits open, METAPILOT_TOKEN set (see .agents/skills/reel-footage-edit/references/
edits-automation.md), mcp.py next to this file. Run from scripts/edits/ or add it to sys.path.
"""
import base64
import json

import mcp

mcp.init()

SANDBOX = "~/Library/Containers/com.burbn.basel.mac/Data/Documents"  # Edits can only read/write here


def T(name, args=None):
    """Call a tool and return its JSON result as a dict."""
    r = mcp.call(name, args or {})
    res = r.get("result", r)
    for c in res.get("content", []):
        if c.get("type") == "text":
            try:
                return json.loads(c["text"])
            except Exception:
                return {"text": c["text"]}
    return res


def IMG(name, args, out):
    """Call a tool that returns an image (frameSheet, captureFrame) and save it to `out`."""
    r = mcp.call(name, args)
    n = 0
    for c in r.get("result", r).get("content", []):
        if c.get("type") == "image":
            open(out if n == 0 else out.replace(".", f"_{n}.", 1), "wb").write(base64.b64decode(c["data"]))
            n += 1
    return n


def frame_sheet(times, out, columns=8, cell_width=220):
    """Contact sheet of the rendered edit at the given timeline seconds."""
    return IMG("frameSheet", {"id": "", "path": "", "times": ",".join(str(t) for t in times),
                              "columns": columns, "cellWidth": cell_width}, out)


# ---------- project ----------

def new_project(title):
    T("saveProject")                      # save whatever is open first
    T("newProject")
    T("wait", {"seconds": 2})
    T("setTitle", {"name": title})
    T("setCanvas", {"aspect": "9:16", "frameRate": 30})


def import_media(path):
    """Import into the media panel. `path` must be inside SANDBOX. Returns the alias id."""
    r = T("importToMediaPanel", {"path": path})
    if not r.get("ok"):
        raise RuntimeError(f"import failed for {path}: {r.get('error')}")
    return r["aliasIds"][0]


def set_sdr():
    """iPhone HLG footage makes the project HDR; call this after the first import."""
    T("setProjectDynamicRange", {"range": "sdr"})


# ---------- main track ----------

def add_main_clip(alias, source_in, source_out, speed=1.0, gain_db=0.0):
    r = T("addMediaPanelItemsToTimeline", {"aliasIds": [alias], "sourceIn": source_in, "sourceOut": source_out})
    cid = r["added"][0]["id"]
    if speed != 1.0:
        T("setSpeed", {"id": cid, "speed": speed})
    T("setSound", {"id": cid, "volumeDb": gain_db, "reduceNoise": 35, "enhanceVoice": 35})
    return cid


def framing(cid, duration, scale_start, scale_end=None, x=0.5):
    """Static or slow push framing. y is nudged down as scale grows to keep headroom."""
    y = lambda s: round(0.5 + 0.33 * (s - 1), 4)
    if scale_end is None or scale_end == scale_start:
        return T("setTransform", {"id": cid, "scale": scale_start, "x": x, "y": y(scale_start),
                                  "allowBeyondCanvas": True, "keyframes": "clear"})
    kf = [{"time": 0, "x": x, "y": y(scale_start), "scale": scale_start},
          {"time": round(duration - 0.04, 3), "x": x, "y": y(scale_end), "scale": scale_end}]
    return T("setTransformKeyframes", {"id": cid, "keyframes": json.dumps(kf)})


def transition(from_id, to_id, kind="transition_dissolve", seconds=0.25):
    """Omit to_id for an end fade. Transitions do not change timeline length."""
    args = {"fromId": from_id, "filterId": kind, "durationSeconds": seconds}
    if to_id:
        args["toId"] = to_id
    return T("addTransition", args)


# ---------- free elements ----------

def fit(eid, start=None, end=None, speed=1.0):
    """Move and/or trim an element to exact times. Re-reads after every trim because a trim right
    after a move sometimes lengthens the element instead of shortening it."""
    if start is not None:
        T("move", {"id": eid, "toSeconds": round(start, 3)})
    e = T("getElement", {"id": eid})
    if end is not None:
        for _ in range(4):
            over = e["endTime"] - end
            if abs(over) < 0.04:
                break
            T("trim", {"id": eid, "side": "right", "deltaSeconds": round(over * speed, 3)})
            e = T("getElement", {"id": eid})
    return e


def scrim(start, end, opacity=0.6):
    """Full-screen dark layer. Create scrims before cards and text so they sit underneath."""
    r = T("addShape", {"x": 0.5, "y": 0.5, "width": 1.0, "height": 1.0, "color": "#000000",
                       "opacity": opacity, "cornerRadius": 0, "startSeconds": round(start, 3),
                       "duration": round(end - start, 3)})
    return r["id"]


def card(alias, start, end, x, y, scale, rotation=0.0, exit_dy=0.9):
    """Image card that slides in, holds, and slides out. scale 1.0 = canvas width."""
    r = T("addMediaPanelItemsToTimeline", {"aliasIds": [alias], "asOverlay": True, "startTime": round(start, 3)})
    cid = r["added"][0]["id"]
    e = fit(cid, end=end)
    d = round(e["endTime"] - e["startTime"], 3)
    kf = [{"time": 0, "x": x, "y": y + 0.7, "scale": scale * 0.9, "rotationDegrees": rotation * 2},
          {"time": 0.22, "x": x, "y": y, "scale": scale, "rotationDegrees": rotation},
          {"time": d - 0.24, "x": x, "y": y - 0.01, "scale": scale * 1.03, "rotationDegrees": rotation},
          {"time": d - 0.04, "x": x, "y": y + exit_dy, "scale": scale, "rotationDegrees": rotation}]
    T("setTransformKeyframes", {"id": cid, "keyframes": json.dumps(kf)})
    T("setMask", {"id": cid, "shape": "rectangle", "centerX": 0.5, "centerY": 0.5, "sizeW": 1, "sizeH": 1,
                  "cornerRadius": 0.07, "feather": 0})
    return cid


def overlay_video(alias, start, end, source_in, source_out, mute=True):
    """Full-screen B-roll clip, speed-fitted to the window."""
    r = T("addMediaPanelItemsToTimeline", {"aliasIds": [alias], "asOverlay": True, "startTime": round(start, 3),
                                           "sourceIn": source_in, "sourceOut": source_out})
    vid = r["added"][0]["id"]
    speed = round((source_out - source_in) / (end - start), 4)
    T("setSpeed", {"id": vid, "speed": speed})
    if mute:
        T("setVolume", {"id": vid, "volume": 0})
    fit(vid, end=end, speed=speed)
    return vid


def _text(txt, start, end, y, size, color):
    r = T("addText", {"text": txt, "duration": round(end - start, 3), "atSeconds": round(start, 3)})
    tid = r["id"]
    return tid


def title(txt, start, end, y=0.62, size=52, color="#FFFFFF"):
    """Large condensed title. Check the result on a frame sheet: long lines wrap."""
    tid = _text(txt, start, end, y, size, color)
    T("applyTextPreset", {"ids": tid, "name": "Super serious"})          # needs `ids`, not `id`
    T("setTextStyle", {"id": tid, "size": size, "color": color, "alignment": "center"})
    T("setTextPosition", {"id": tid, "x": 0.5, "y": y})
    T("setTextAnimation", {"id": tid, "animation": "fligPop"})
    fit(tid, start=start, end=end)                                        # addText does not always honour atSeconds
    return tid


def label(txt, start, end, y=0.13, size=24, fg="#FFFFFF", bg="#0B1020EE"):
    """Small pill label. Keep under about 24 characters at size 24 or it wraps."""
    tid = _text(txt, start, end, y, size, fg)
    T("applyTextPreset", {"ids": tid, "name": "None"})
    T("setTextFont", {"id": tid, "family": "HelveticaNeue-CondensedBold"})
    T("setTextStyle", {"id": tid, "size": size, "color": fg, "alignment": "center"})
    T("setTextPosition", {"id": tid, "x": 0.5, "y": y})
    T("setEmphasis", {"id": tid, "style": "backgroundPill", "color": bg})
    T("setTextAnimation", {"id": tid, "animation": "fligZoomBox"})       # fligCaptionSlide clips pill text
    fit(tid, start=start, end=end)
    return tid


# ---------- captions, sound, export ----------

def captions(style="Word Highlight Box", highlight="#FF5A36", y=0.775, fixes=None):
    """Generate captions from the timeline audio, style them, apply text fixes, and position them."""
    T("deleteCaptions", {})
    T("generateCaptions", {"source": "video", "language": "en", "curseWords": True})
    T("setCaptionStyle", {"style": style})
    T("setCaptionHighlightColor", {"color": highlight})
    for c in T("captions")["captions"]:
        new = c["text"]
        for a, b in (fixes or {}).items():
            new = new.replace(a, b)
        if new != c["text"]:
            T("editCaption", {"id": c["id"], "text": new})
        T("setTextPosition", {"id": c["id"], "x": 0.5, "y": y})
    return T("captions")["captions"]


def sound_effect(effect_id, at, volume=0.3):
    """effect_id comes from searchSoundEffects. Sound effects DO appear in exported files."""
    T("seek", {"seconds": round(at, 3)})
    r = T("addSoundEffect", {"effect": effect_id})
    sid = r.get("id") or r.get("elementId")
    e = T("getElement", {"id": sid})
    if abs(e.get("startTime", -1) - at) > 0.05:
        T("move", {"id": sid, "toSeconds": round(at, 3)})
    T("setVolume", {"id": sid, "volume": volume})
    return sid


def export(path):
    """Export to a path inside SANDBOX and wait. Licensed catalog music is silently left out."""
    T("saveProject")
    T("export", {"path": path})
    for _ in range(300):
        s = T("exportStatus")
        if s.get("state") in ("complete", "failed", "cancelled"):
            return s.get("state")
        T("wait", {"seconds": 3})
    return "timeout"
