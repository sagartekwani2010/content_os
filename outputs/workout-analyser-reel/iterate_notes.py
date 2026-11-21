"""Creator-notes revision: Fable 5.2 applies the creator's line notes to the reviewed script (rounds_v5/r2_B.md) in 3
takes; the panel scores each twice; Opus checks the winner; up to --rounds refinement rounds keep the notes fixed.
Output: rounds_notes/
"""
import argparse, json, re
from concurrent.futures import ThreadPoolExecutor

from iterate import claude, context, HERE
from iterate_v5 import CLIPS, CLIP_NOTES, LOCKED, JUDGE, CHECK, retry, score

OUT = HERE / "rounds_notes"
CREATOR_NOTES = """CREATOR'S NOTES on the reviewed script (apply ALL of them; they override everything else):
1. Beat 7 (SEE): say it like "Each exercise is split and tracked across 17 joints."
2. Reps are shown as waves: call out HOW each rep is compared with my best form (the wave of every rep against the
   wave of my best rep).
3. Check continuity around beat 9 (the can't-see refusal must flow from the waves and into JUDGE).
4. Beat 13 (the lunge false alarm) must be more meaningful, and beat 14 better: tie it to the research warning from
   beat 4 (the camera angle can fool it) - the warning came true on my own lunge.
5. Beats 16-18 (the one real STOP) must be EXTREMELY clear, like the calories reel's "chicken hidden under carrots,
   and 500 calories became 94": one concrete, visual, instantly understood moment with one number pair. Here: on my
   reverse crunch my best rep lowered my legs through 122 degrees; this set's worst rep only 53 - my legs stopped short
   and momentum did the rest. Make the viewer SEE it (the green ghost of my best vs the red gap).
6. Beat 19 (the forward/shareable line) must be stronger.
7. Combine beats: 14-15 beats MAX in MAIN (including the silent countdown beat). TRIAL may add at most 3 beats.
Keep: hook line (creator's), "Months of weekends", "Come, let's see", the research line ("I had Claude dig through the
research first. One warning stood out: the camera angle can fool it."), THE WAIT IS OVER + 3-2-1 + blast, three
parts SEE / JUDGE / CHECK, 23 sets on trial, the Salesforce ending ("reportedly", AI engineers with LLM post-training
experience, many companies doing the same, how do you get ready, come let's find out).
Facts to respect: do not claim the creator counted/logged that crunch set; the Salesforce line is a bridge to what's
next (not the reason Gym Jarvis was built)."""

WRITE = """You are Claude Fable 5.2, the creator's chosen writer. Revise the REVIEWED SCRIPT applying the CREATOR'S NOTES.
Take strategy: {angle}
Short beats (max ~14 spoken words), E/H alternating, 55-62 s at 1.15x, one forwardable line, a loop to the hook.
Use only these clip names (in backticks, in the Top-half visual column): {clips}. {clip_notes}
TRIAL: hook "My AI flagged one of my sets as STOP. It was wrong."; reuse MAIN lines after the hook.

OUTPUT exactly (nothing before it):
## MAIN
| Beat | E/H | Time | Spoken | Top-half visual | On-screen text | Music / SFX |
|---|---|---|---|---|---|---|
(14-15 rows; "(no line)" for silent beats)

## TRIAL
(same columns)

## WHAT CHANGED
One line per creator note (1-7): what you did."""

ANGLES = {
 "A": "Keep the courtroom frame light (on trial / guilty / no evidence, no verdict) but never let it blur the facts.",
 "B": "No courtroom: plain, warm, Ep 2 calories-reel clarity - each part one crisp idea, each result one concrete picture.",
 "C": "Maximum drama: the research warning as a ticking clock that pays off twice (it fooled the judge; then CHECK saves it), and the crunch reveal as the climax.",
}


def main(target, rounds):
    OUT.mkdir(exist_ok=True); ctx = context()
    cur = (HERE / "rounds_v5" / "r2_B.md").read_text(); best = {"overall": 0}; log = []; panel_notes = ""
    for n in range(1, rounds + 1):
        def make(k):
            f = OUT / f"r{n}_{k}.md"
            if f.exists() and "## MAIN" in f.read_text():
                d = f.read_text()
            else:
                d, _ = retry(lambda: claude(f"{ctx}\n\n{LOCKED}\n\n{CREATOR_NOTES}\n\nREVIEWED SCRIPT:\n{cur}\n\n{panel_notes}\n\n" +
                                            WRITE.format(angle=ANGLES[k], clips=CLIPS, clip_notes=CLIP_NOTES), "claude-fable-5-2"))
                d = d[d.find("## MAIN"):] if "## MAIN" in d else d
                f.write_text(d)
            ov, g, ps = score(d)
            return k, d, ov, g, ps
        with ThreadPoolExecutor(3) as ex:
            res = sorted(ex.map(make, ANGLES), key=lambda r: -r[2])
        k, d, ov, g, ps = res[0]
        (OUT / f"r{n}_scores.json").write_text(json.dumps({r[0]: {"overall": r[2], "groups": r[3], "panels": r[4]} for r in res}, indent=1))
        check, _ = retry(lambda: claude(f"{ctx}\n\nSCRIPT:\n{d}\n\n" + CHECK.format(clips=CLIPS) +
                                        "\nAlso: MAIN must have at most 15 beats.", "claude-opus-5-5"))
        (OUT / f"r{n}_{k}_CHECK.md").write_text(check)
        clean = check.strip().upper().startswith("NONE")
        row = {"round": n, "winner": k, "overall": ov, "groups": g, "all": {r[0]: r[2] for r in res}, "check_clean": clean}
        log.append(row); (OUT / "log.json").write_text(json.dumps(log, indent=1)); print(json.dumps(row), flush=True)
        if ov > best["overall"]:
            best = row; cur = d; (OUT / "BEST.md").write_text(d); (OUT / "BEST_CHECK.md").write_text(check)
        if best["overall"] >= target and best.get("check_clean"):
            break
        panel_notes = ("PANEL NOTES (apply only where they do not contradict the creator's notes):\n" +
                       json.dumps({"top_fixes": ps[0]["top_fixes"] + ps[1]["top_fixes"],
                                   "drops": [{"id": x["id"], "score": x["score"], "drop": x["drop"], "why": x["why"]}
                                             for x in ps[0]["personas"] if x["score"] < 6]}, indent=1) +
                       "\n\nCHECKER MUST-FIX:\n" + (OUT / "BEST_CHECK.md").read_text())
    print("BEST", json.dumps(best), flush=True)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--target", type=float, default=7.0); ap.add_argument("--rounds", type=int, default=3)
    a = ap.parse_args(); main(a.target, a.rounds)
