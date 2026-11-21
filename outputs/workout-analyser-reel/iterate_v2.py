"""Drama pass on the short-beats script: Fable 5.2 rewrites -> Opus 5.5 checks -> Fable 5.2 panel (16 personas) scores.
Stops at --target (default 8.0), when a round scores lower than the best so far, or after --max-rounds.
Output: rounds_v2/vN_SCRIPT.md (same table format as SCRIPT_FINAL.md, so make_preview.py can render it).
"""
import argparse, json, re
from pathlib import Path

from iterate import PANEL, claude, context, HERE

OUT = HERE / "rounds_v2"
LOCKED = """LOCKED (creator; the panel may not recommend changing these): short spoken beats, one short sentence each, the
visuals do the talking; the five-step architecture explanation (pose -> rep maths -> safety check -> judge vs my best
-> coach, both must agree) stays and is the save asset; THE WAIT IS OVER + 3-2-1 + blast after the opening; Desi Boyz
music (beat only, no chant) under the first half; the ending shows the real Salesforce LMTS LLM Post-Training job
posting (Bangalore, 13 Nov 2026) with the reportedly-garden-leave line; English only; every number from FACTS."""

WRITE = """Rewrite the CURRENT SCRIPT for more ENGAGEMENT and DRAMA (stakes, tension, a twist that lands, a payoff that
feels earned), keeping every LOCKED item and every fact. Techniques to use where they fit: open a loop in beat 1 and
close it by name; a reversal (the AI was wrong, then right); a ticking-clock or stakes line a gym-goer feels; a line a
viewer would forward to a gym buddy; contrast (my best vs my worst); short punchy lines with rhythm; one comedic beat.
Keep beats SHORT (max ~12 words spoken each). Keep only these visual clips (names exactly): ghost_stop.mp4,
raw_swing.mp4, wait_is_over.mp4, countdown_blast.mp4, wall_of_sets.mp4, arch_1.mp4, lockon_red.mp4, dual_wave.mp4,
arch_2.mp4, cant_see.mp4, arch_3.mp4, false_alarm.mp4, arch_4.mp4, arch_5.mp4, sample_result.mp4, tease_jd.mp4.
Target 55-62 s at 1.15x. The first 6 beats run under the Desi Boyz beat (end beat 6 right after the wall of sets).

OUTPUT exactly this, nothing else before it:
## MAIN
| Beat | E/H | Time | Spoken | Top-half visual | On-screen text | Music / SFX |
|---|---|---|---|---|---|---|
(rows; put clip names in backticks in the Top-half visual column; "(no line)" for silent beats)

## TRIAL
(same columns; TRIAL hook: "My AI told me to stop my set. It was wrong."; reuse MAIN lines after the hook wherever possible)

## WHY THIS IS MORE DRAMATIC
3-5 bullets."""

JUDGE = f"""You are an engagement panel. Another model wrote this Instagram reel script; you did not.
{PANEL}
Imagine each persona meeting this reel cold in their feed, with the described visuals and music. For each persona give
ENGAGEMENT 0-10 (10 = holds past 3 s, watches to the end, and would send, save or comment), the drop-off beat (or
"none") and why. Be strict: an ordinary good reel scores 5-6.
{LOCKED}
Reply with JSON only: {{"personas":[{{"id":int,"score":num,"drop":str,"why":str}}],"groups":{{"mass":num,"fin_consult_mktg":num,"builders":num}},
"overall":num,"top_fixes":[str,str,str,str,str]}}"""

CHECK = """Independent checker: compare the script with FACTS. List MUST-FIX items only (any claim not in FACTS, any
"stopped me mid-set" implication, any number not measured, a missing "reportedly" on the garden-leave line, a clip name
not in the allowed list). Under 200 words. If none, say NONE."""


def main(target, max_rounds):
    OUT.mkdir(exist_ok=True)
    ctx = context()
    cur = (HERE / "SCRIPT_FINAL.md").read_text()
    best, log, notes = None, [], ""
    for n in range(1, max_rounds + 1):
        draft, _ = claude(f"{ctx}\n\n{LOCKED}\n\nCURRENT SCRIPT:\n{cur}\n\n{notes}\n\n{WRITE}", "claude-fable-5-2")
        draft = draft[draft.find("## MAIN"):] if "## MAIN" in draft else draft
        check, _ = claude(f"{ctx}\n\nSCRIPT:\n{draft}\n\n{CHECK}", "claude-opus-5-5")
        raw, _ = claude(f"SCRIPT:\n{draft}\n\n{JUDGE}", "claude-fable-5-2")
        panel = json.loads(re.search(r"\{.*\}", raw, re.S).group(0))
        (OUT / f"v{n}_SCRIPT.md").write_text(draft); (OUT / f"v{n}_CHECK.md").write_text(check)
        (OUT / f"v{n}_PANEL.json").write_text(json.dumps(panel, indent=1))
        row = {"round": n, "overall": panel["overall"], "groups": panel["groups"], "must_fix": "NONE" not in check.upper()[:40]}
        log.append(row); (OUT / "log.json").write_text(json.dumps(log, indent=1)); print(json.dumps(row), flush=True)
        if best is None or panel["overall"] > best["overall"]:
            best = row; cur = draft
        else:
            print("STOP: no improvement", flush=True); break
        if panel["overall"] >= target and not row["must_fix"]:
            break
        notes = ("PANEL (fix what loses people, keep what works):\n" + json.dumps(panel, indent=1) +
                 "\n\nCHECKER MUST-FIX:\n" + check)
    print("BEST", json.dumps(best), flush=True)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--target", type=float, default=8.0); ap.add_argument("--max-rounds", type=int, default=4)
    a = ap.parse_args(); main(a.target, a.max_rounds)
