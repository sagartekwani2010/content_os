"""v5: creator's outline (SEE / JUDGE / CHECK). Fable 5.2 brainstorms 3 story takes, panel scores each twice, then
best-of-3 refinement rounds with the panel's notes; Opus 5.5 checks each winner. Stops at --target with a clean check.
Resumable; survives usage limits. Output: rounds_v5/
"""
import argparse, json, re, time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from iterate import PANEL, claude, context, HERE

OUT = HERE / "rounds_v5"
CLIPS = ("ghost_stop.mp4, raw_swing.mp4, verdict_chips.mp4, wait_over_wall.mp4, countdown_wall.mp4, wall_from_count.mp4, "
         "lockon_red.mp4, dual_wave.mp4, cant_see.mp4, false_alarm.mp4, sample_result.mp4, tease_jd.mp4, arch_job_split.mp4, "
         "arch3_overview.mp4, arch3_see.mp4, arch3_judge.mp4, arch3_check.mp4, build_montage.mp4")
CLIP_NOTES = ("arch3_*.mp4 = a 3-part HUD schematic (overview with SEE / JUDGE / CHECK, then each part lit); build_montage.mp4 = "
              "quick cuts of the Gym Jarvis HUD, code and earlier episodes (months of weekends). Both will be rendered to match "
              "the script.")
LOCKED = """LOCKED (creator; do not change, do not recommend changing): the creator's outline order in BRIEF (hook ->
the build, months of weekends -> come, let's see -> ONE research line (Claude dug through the research; the camera
angle can fool it) -> THE WAIT IS OVER + 3-2-1 + blast -> "I split it into three parts":
SEE, JUDGE, CHECK, each explained -> the lunge failing case -> results and the creator's views dropped in between ->
the Salesforce ending: reportedly letting people go while hiring AI engineers with LLM post-training experience, many
companies doing the same, how do you get ready, come let's find out). Max 3-4 components. NO "film from the side".
Short spoken beats (max ~12 words), visuals do the talking, E/H alternating. English only. Every number from FACTS."""

ANGLES = {
 "A": "BUILDER'S JOURNEY: warm and personal. The months of weekends are the emotional engine; the creator built a coach "
      "that tells the truth, even about him. The payoff is pride with a laugh.",
 "B": "23 SETS ON TRIAL: a courtroom frame running through the reel (the accused: 23 sets; the judge; the witness that "
      "only watches video; a wrongful conviction (the lunge); the verdict). Punchy, dramatic, playful.",
 "C": "EVERYDAY RELATABLE: written for someone who doesn't code and barely trains. Every part gets an everyday analogy "
      "(a friend filming you, a referee, a second opinion from another doctor); gym-buddy humour; the job ending as the "
      "stake for every viewer's career.",
}
WRITE = """You are Claude Fable 5.2, the creator's chosen writer. Write the shooting script of this Instagram reel.
Strategy for this take: {angle}

{notes}
Rules: follow BRIEF v5 and FACTS exactly. Short beats (max ~12 spoken words each), E/H alternating, re-hooks at 1/3 and
2/3, one line a viewer forwards to a gym buddy, a loop at the end, 55-62 s at 1.15x. The first beats up to and
including the blast run under the Desi Boyz beat. Use only these clip names (in backticks, in the Top-half visual
column): {clips}. {clip_notes}
TRIAL: hook "My AI flagged one of my sets as STOP. It was wrong."; reuse MAIN lines after the hook wherever possible.

OUTPUT exactly (nothing before it):
## MAIN
| Beat | E/H | Time | Spoken | Top-half visual | On-screen text | Music / SFX |
|---|---|---|---|---|---|---|
(rows; "(no line)" for silent beats)

## TRIAL
(same columns)

## WHY THIS LANDS
3-5 bullets."""

JUDGE = f"""You are an engagement panel. Another model wrote this Instagram reel script; you did not.
{PANEL}
Imagine each persona meeting this reel cold in their feed, with the described visuals and music. For each persona give
ENGAGEMENT 0-10 (10 = holds past 3 s, watches to the end, and would send, save, follow or comment), the drop-off beat
(or "none") and why. Be strict: an ordinary good reel scores 5-6.
{LOCKED}
Reply with JSON only: {{"personas":[{{"id":int,"score":num,"drop":str,"why":str}}],"groups":{{"mass":num,"fin_consult_mktg":num,"builders":num}},
"overall":num,"top_fixes":[str,str,str,str,str]}}"""

CHECK = """Independent checker: compare the script with BRIEF v5 and FACTS (including 'Settled items' and 'v5 additions').
List MUST-FIX items only: a claim not in FACTS, any live / mid-set implication, an unmeasured number, the garden-leave or
letting-go line without "reportedly", "AI scientists" instead of AI engineers, more than 4 architecture components, a
"film from the side" line, a clip name outside this list: {clips}. Under 200 words. If none, reply exactly NONE."""


def retry(fn, waits=(0, 600, 1800, 3600, 3600, 3600)):
    last = None
    for w in waits:
        time.sleep(w)
        try:
            return fn()
        except Exception as e:  # noqa: BLE001
            last = e; print("RETRY after error:", str(e)[-160:].replace("\n", " "), flush=True)
    raise last


def score(draft):
    def one(_):
        raw, _c = retry(lambda: claude(f"SCRIPT:\n{draft}\n\n{JUDGE}", "claude-fable-5-2"))
        return json.loads(re.search(r"\{.*\}", raw, re.S).group(0))
    with ThreadPoolExecutor(2) as ex:
        ps = list(ex.map(one, range(2)))
    ov = round(sum(p["overall"] for p in ps) / 2, 2)
    return ov, {k: round(sum(p["groups"][k] for p in ps) / 2, 2) for k in ps[0]["groups"]}, ps


def main(target, rounds):
    OUT.mkdir(exist_ok=True); ctx = context()
    log = json.loads((OUT / "log.json").read_text()) if (OUT / "log.json").exists() else []
    best = max(log, key=lambda r: r["overall"]) if log else {"overall": 0}
    cur = (OUT / "BEST.md").read_text() if (OUT / "BEST.md").exists() else ""
    notes = (OUT / "NOTES.txt").read_text() if (OUT / "NOTES.txt").exists() else ""
    for n in range(len(log) + 1, rounds + 1):
        def make(k):
            f = OUT / f"r{n}_{k}.md"
            if f.exists() and "## MAIN" in f.read_text():
                d = f.read_text()
            else:
                base = f"CURRENT BEST SCRIPT (improve it with this strategy):\n{cur}\n\n{notes}" if cur else "No script yet: write it fresh."
                d, _ = retry(lambda: claude(f"{ctx}\n\n{LOCKED}\n\n{base}\n\n" +
                                            WRITE.format(angle=ANGLES[k], notes="", clips=CLIPS, clip_notes=CLIP_NOTES), "claude-fable-5-2"))
                d = d[d.find("## MAIN"):] if "## MAIN" in d else d
                f.write_text(d)
            ov, g, ps = score(d)
            return k, d, ov, g, ps
        with ThreadPoolExecutor(3) as ex:
            res = sorted(ex.map(make, ANGLES), key=lambda r: -r[2])
        k, d, ov, g, ps = res[0]
        (OUT / f"r{n}_scores.json").write_text(json.dumps({r[0]: {"overall": r[2], "groups": r[3], "panels": r[4]} for r in res}, indent=1))
        check, _ = retry(lambda: claude(f"{ctx}\n\nSCRIPT:\n{d}\n\n" + CHECK.format(clips=CLIPS), "claude-opus-5-5"))
        (OUT / f"r{n}_{k}_CHECK.md").write_text(check)
        clean = check.strip().upper().startswith("NONE")
        row = {"round": n, "winner": k, "overall": ov, "groups": g, "all": {r[0]: r[2] for r in res}, "check_clean": clean}
        log.append(row); (OUT / "log.json").write_text(json.dumps(log, indent=1)); print(json.dumps(row), flush=True)
        if ov > best["overall"]:
            best = row; cur = d; (OUT / "BEST.md").write_text(d); (OUT / "BEST_CHECK.md").write_text(check)
        notes = ("PANEL NOTES ON THE CURRENT BEST (fix what loses people; keep what works):\n" +
                 json.dumps({"top_fixes": ps[0]["top_fixes"] + ps[1]["top_fixes"],
                             "drops": [{"id": x["id"], "score": x["score"], "drop": x["drop"], "why": x["why"]}
                                       for x in ps[0]["personas"] if x["score"] < 6]}, indent=1) +
                 "\n\nCHECKER MUST-FIX:\n" + (OUT / "BEST_CHECK.md").read_text())
        (OUT / "NOTES.txt").write_text(notes)
        if best["overall"] >= target and best.get("check_clean"):
            break
    print("BEST", json.dumps(best), flush=True)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--target", type=float, default=7.0); ap.add_argument("--rounds", type=int, default=5)
    a = ap.parse_args(); main(a.target, a.rounds)
