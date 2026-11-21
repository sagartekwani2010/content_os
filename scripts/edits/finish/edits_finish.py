"""Continue the Edits build on the open project: music (local file, drop through the twist) + library SFX.
Usage: python3 edits_finish.py <plan.json> <cuts.json> <music_path> <music_volume_db>"""
import json, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from ed import call  # noqa: E402

plan = json.load(open(sys.argv[1])); cuts = json.load(open(sys.argv[2]))
music, vol_db = sys.argv[3], float(sys.argv[4])
seg = {s["beat"]: s for s in cuts["segments"]}
TOTAL = cuts["duration"]
log = []


def step(name, args=None):
    r = call(name, args or {})
    ok = not (isinstance(r, dict) and r.get("error"))
    log.append({"tool": name, "args": args, "ok": ok, "result": r if isinstance(r, dict) else str(r)[:300]})
    if not ok:
        print(f"WARN {name} failed: {r}")
    return r


def db(x):
    return round(10 ** (x / 20), 4)


def elements():
    return {e["id"]: e for e in call("elements", {"limit": 300})["elements"]}


def new_id(before):
    after = elements()
    new = [i for i in after if i not in before]
    return (new[0] if new else None), after


# music: a pre-mixed, pre-ducked bed (drop + fades baked in) imported as a normal audio element,
# because the Edits music slot does not export
before = elements()
step("seek", {"seconds": 0})
step("importMedia", {"path": music})
m1, els = new_id(before)
m2 = None
if m1 and abs(els[m1]["startTime"]) > 0.02:
    step("move", {"id": m1, "toSeconds": 0})
if m1:
    step("setVolume", {"id": m1, "volume": db(vol_db)})
# library sound effects at exact times
placed = []
for s in plan["sfx"]:
    before = elements()
    step("seek", {"seconds": s["at_s"]})
    step("addSoundEffect", {"effect": s["title"]})
    sid, els = new_id(before)
    if sid:
        if abs(els[sid]["startTime"] - s["at_s"]) > 0.02:
            step("move", {"id": sid, "toSeconds": s["at_s"]})
        step("setVolume", {"id": sid, "volume": db(s["volume_db"])})
        # library effects can be long samples (7-13 s): cap at 2 s, never past the end, short fade
        e = elements()[sid]
        over = e["startTime"] + e["duration"] - min(e["startTime"] + 2.0, TOTAL)
        if over > 0.01:
            step("trim", {"id": sid, "side": "right", "deltaSeconds": round(over, 3)})
            step("setFade", {"id": sid, "fadeIn": 0.0, "fadeOut": 0.25})
        placed.append((s["at_s"], s["title"], sid))
json.dump(log, open(Path(sys.argv[1]).with_name("edits_finish_log.json"), "w"), indent=1, default=str)
els = elements()
print(json.dumps({"music": [m1, m2], "sfx_placed": len(placed), "sfx_planned": len(plan["sfx"]),
                  "elements": len(els), "failures": sum(1 for x in log if not x["ok"])}))
for at, title, sid in placed:
    e = els.get(sid, {})
    print(f"  {at:6.2f}s -> {e.get('startTime')!s:>8} {title}")
