"""Resolve the Edits SFX plan from beat/word anchors against a cuts.json, so timings survive speed changes.
Usage: python3 sfx_anchors.py <cuts.json> <plan_in.json> <plan_out.json>"""
import json, sys

cuts, plan_in, plan_out = sys.argv[1:4]
c = json.load(open(cuts)); seg = {s["beat"]: s for s in c["segments"]}


def beat_start(b):
    return seg[b]["out_start"]


def word(b, w, nth=0):
    hits = [x for x in seg[b]["words"] if w.lower() in x["text"].lower()]
    return hits[nth]["start"] if hits else beat_start(b)


plan = json.load(open(plan_in))
if "anchors" in plan:  # generic: the plan names beats/words; resolve them against this reel's cuts
    SECTIONS = plan.get("sections", [])
    lv = plan.get("section_sfx_db", {"whoosh": -4, "impact": -2})
    anchors = []
    for b in SECTIONS:
        if b in seg:
            anchors.append({"at": beat_start(b) - 0.18, "title": "Whoosh (short) 4", "db": lv["whoosh"], "on": f"section card, beat {b}"})
            anchors.append({"at": beat_start(b) + 0.02, "title": "Impact (bassy)", "db": lv["impact"], "on": f"card lands, beat {b}"})
    for a in plan["anchors"]:
        if a["beat"] not in seg:
            continue
        at = (word(a["beat"], a["word"]) if a.get("word") else beat_start(a["beat"])) + a.get("offset", 0.0)
        anchors.append({"at": at, "title": a["title"], "db": a.get("db", -4), "on": a.get("on", "")})
else:  # Ep 2 (food tracker) anchors
    SECTIONS = [1, 3, 6, 11, 13, 17, 19]           # each gets a card: whoosh in, bass impact as it lands
    anchors = []
    for b in SECTIONS:
        anchors.append({"at": beat_start(b) - 0.18, "title": "Whoosh (short) 4", "db": -4, "on": f"section card, beat {b}"})
        anchors.append({"at": beat_start(b) + 0.02, "title": "Impact (bassy)", "db": -2, "on": f"card lands, beat {b}"})
    anchors += [
        {"at": word(0, "94") - 0.03, "title": "Boom impact 1", "db": 0, "on": "cold open '94'"},
        {"at": word(8, "calories") + 0.45, "title": "Arrow impact 3", "db": -4, "on": "'calories' crossed out"},
        {"at": word(9, "database") + 0.05, "title": "Button press (light)", "db": -4, "on": "13,224 highlighted"},
        {"at": word(12, "flag") + 0.02, "title": "Notification (pop-up) 4", "db": -4, "on": "'flag'"},
        {"at": beat_start(15) - 0.25, "title": "Vinyl scratch hit", "db": 0, "on": "music stops: the twist"},
        {"at": word(16, "94") - 0.03, "title": "Boom impact 1", "db": 0, "on": "'94' callback"},
    ]
plan["sfx"] = [{"at_s": round(max(0.0, a["at"]), 3), "title": a["title"], "volume_db": a["db"], "lands_on": a["on"]}
               for a in sorted(anchors, key=lambda a: a["at"])]
if "drop_beats" in plan:
    a, b = plan["drop_beats"]
    plan["drop"] = [round(beat_start(a), 3), round(beat_start(b), 3)] if a in seg and b in seg else None
elif 15 in seg and 17 in seg and "anchors" not in plan:
    plan["drop"] = [round(beat_start(15), 3), round(beat_start(17), 3)]
plan["total"] = c["duration"]
json.dump(plan, open(plan_out, "w"), indent=1)
for s in plan["sfx"]:
    print(f"{s['at_s']:7.2f}s {s['volume_db']:>4} dB  {s['title']:<26} {s['lands_on']}")
print("music drop", plan.get("drop"), "total", plan["total"])
