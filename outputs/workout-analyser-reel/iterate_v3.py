"""Best-of-3 drama tournament: each round Fable 5.2 writes 3 takes in parallel (different dramatic strategies), the
Fable panel scores each twice (mean), the best survives, Opus 5.5 checks it. Stops at --target or after --rounds.
Output: rounds_v3/rN_{A,B,C}.md, rN_scores.json, BEST.md, log.json
"""
import argparse, json, re
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from iterate import PANEL, claude, context, HERE
from iterate_v2 import LOCKED, JUDGE

OUT = HERE / "rounds_v3"
CLIPS = ("ghost_stop.mp4, raw_swing.mp4, wait_is_over.mp4, countdown_blast.mp4, wall_of_sets.mp4, arch_1.mp4, lockon_red.mp4, "
         "dual_wave.mp4, arch_2.mp4, cant_see.mp4, arch_3.mp4, false_alarm.mp4, arch_4.mp4, arch_5.mp4, sample_result.mp4, tease_jd.mp4")
ANGLES = {
 "A": "MYSTERY: open a question in beat 1 that is only answered at the payoff; plant 'it got one wrong' and 'the job Salesforce is hiring for' as promises on screen before the five steps; every step ends on a small cliffhanger.",
 "B": "SELF-ROAST COMEDY: the creator is the butt of the joke (the AI caught him cheating his own reps, then he fooled the AI by turning to the camera); dry one-liners, one real laugh, warmth; the gym buddy line is the forwardable joke.",
 "C": "STAKES: say in plain physical words what a short, swung rep costs (the work you think you did but didn't), make '23 sets, one STOP' feel like a verdict, and make the Salesforce ending the personal stake for every viewer's job.",
}
FIXES = """Apply these panel findings (they respect every LOCKED item):
- Plain physical stake in the first beats: say what a short, swung rep is in ordinary words (e.g. "My legs stopped halfway. Momentum did the rest."); degrees stay on screen, not in the voice.
- Plant two promises on screen before the five steps: IT GOT ONE WRONG and the job tease (a small corner tag is fine).
- A 1/5 ... 5/5 progress marker on screen through the five steps; steps 1-3 move fast.
- One CTA per purpose: 'send to your gym buddy' once on the swing; 'Comment FORM' once at the end, saying what they get in plain words (my AI coach prompt + the diagram).
- Bridge the build to the Salesforce ending with one short line (e.g. "This judge-and-coach check? That's the job.").
- No [SLOT]s, no risk/injury wording, no 'unwatched'. Garden-leave line keeps "reportedly", with the source tag on screen."""

WRITE = """You are Claude Fable 5.2 writing the final shooting script of an Instagram reel. Rewrite the CURRENT BEST SCRIPT
with this dramatic strategy:
{angle}

{fixes}
Keep beats SHORT (max ~12 spoken words each), E/H alternating, 55-62 s at 1.15x. Use only these clip names (in backticks,
in the Top-half visual column): {clips}. The first 6 beats run under the Desi Boyz beat (no chant) and beat 6 ends on the
wall of sets. TRIAL hook: "My AI told me to stop my set. It was wrong."; after the hook reuse MAIN lines wherever possible.

OUTPUT exactly (nothing before it):
## MAIN
| Beat | E/H | Time | Spoken | Top-half visual | On-screen text | Music / SFX |
|---|---|---|---|---|---|---|
(rows; "(no line)" for silent beats)

## TRIAL
(same columns)

## WHY THIS LANDS
3-5 bullets."""

CHECK = """Independent checker: compare the script with FACTS (including 'Settled items'). List MUST-FIX items only: a claim
not in FACTS, any "stopped me mid-set" implication, a number not measured, a missing "reportedly" on the garden-leave
line, a clip name outside this list: {clips}. Under 200 words. If none, reply exactly NONE."""


def retry(fn, waits=(0, 600, 1800, 3600, 3600, 3600)):
    """Survive usage limits: wait and try again instead of crashing (limits reset within hours)."""
    import time
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
    ov = sum(p["overall"] for p in ps) / 2
    groups = {k: round(sum(p["groups"][k] for p in ps) / 2, 2) for k in ps[0]["groups"]}
    return round(ov, 2), groups, ps


def main(target, rounds):
    OUT.mkdir(exist_ok=True); ctx = context()
    cur = (HERE / "rounds_v2" / "v1_SCRIPT.md").read_text(); best = {"overall": 0}; log = []; notes = ""; start = 1
    if (OUT / "log.json").exists() and (OUT / "BEST.md").exists():   # resume after a crash
        log = json.loads((OUT / "log.json").read_text()); best = max(log, key=lambda r: r["overall"])
        cur = (OUT / "BEST.md").read_text(); start = len(log) + 1
        notes = "CHECKER MUST-FIX:\n" + (OUT / "BEST_CHECK.md").read_text()
    for n in range(start, rounds + 1):
        def make(k):
            f = OUT / f"r{n}_{k}.md"
            if f.exists() and "## MAIN" in f.read_text():   # resume: reuse a draft written before a crash
                d = f.read_text()
            else:
                d, _ = retry(lambda: claude(f"{ctx}\n\n{LOCKED}\n\nCURRENT BEST SCRIPT:\n{cur}\n\n{notes}\n\n" +
                             WRITE.format(angle=ANGLES[k], fixes=FIXES, clips=CLIPS), "claude-fable-5-2"))
                d = d[d.find("## MAIN"):] if "## MAIN" in d else d
                f.write_text(d)
            ov, g, ps = score(d)
            return k, d, ov, g, ps
        with ThreadPoolExecutor(3) as ex:
            res = list(ex.map(make, ANGLES))
        res.sort(key=lambda r: -r[2]); k, d, ov, g, ps = res[0]
        (OUT / f"r{n}_scores.json").write_text(json.dumps({r[0]: {"overall": r[2], "groups": r[3], "panels": r[4]} for r in res}, indent=1))
        check, _ = retry(lambda: claude(f"{ctx}\n\nSCRIPT:\n{d}\n\n" + CHECK.format(clips=CLIPS), "claude-opus-5-5"))
        (OUT / f"r{n}_{k}_CHECK.md").write_text(check)
        row = {"round": n, "winner": k, "overall": ov, "groups": g, "all": {r[0]: r[2] for r in res}, "check_clean": check.strip().upper().startswith("NONE")}
        log.append(row); (OUT / "log.json").write_text(json.dumps(log, indent=1)); print(json.dumps(row), flush=True)
        if ov > best["overall"]:
            best = row; cur = d; (OUT / "BEST.md").write_text(d); (OUT / "BEST_CHECK.md").write_text(check)
        if best["overall"] >= target and best.get("check_clean"):
            break
        notes = ("PANEL NOTES ON THE CURRENT BEST (fix what loses people; keep what works):\n" +
                 json.dumps({"top_fixes": ps[0]["top_fixes"] + ps[1]["top_fixes"],
                             "drops": [{"id": x["id"], "score": x["score"], "drop": x["drop"], "why": x["why"]} for x in ps[0]["personas"] if x["score"] < 6]}, indent=1) +
                 "\n\nCHECKER MUST-FIX:\n" + check)
    print("BEST", json.dumps(best), flush=True)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--target", type=float, default=8.0); ap.add_argument("--rounds", type=int, default=4)
    a = ap.parse_args(); main(a.target, a.rounds)
