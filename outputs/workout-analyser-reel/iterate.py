"""Write -> check -> score -> revise loop for the Ep 3 script and visual board.

Writer: Claude Fable 5.2. Checker (accuracy + house rules): Claude Opus 5.5.
Engagement panel: Claude Fable 5.2 in a fresh session, told another model wrote the draft.
Stops when the panel's overall engagement score reaches TARGET, or after MAX_ROUNDS.

Usage: python iterate.py [--target 7.5] [--max-rounds 5]
"""
import argparse, json, re, subprocess, tempfile, time
from pathlib import Path

HERE = Path(__file__).resolve().parent
R = HERE / "rounds"
WRITER = JUDGE = "claude-fable-5-2"
CHECKER = "claude-opus-5-5"

PANEL = ("Panel (Indian Instagram viewers scrolling at 10 pm, English only): 1 TCS support engineer Pune 24; "
         "2 CA Ahmedabad 31; 3 HR exec Bengaluru 28; 4 bank RM Lucknow 35; 5 school teacher Jaipur 38; "
         "6 BTech final-year Hyderabad 21; 7 FP&A analyst Gurgaon 25; 8 IB/equity research associate Mumbai 33; "
         "9 Big 4 consulting analyst Bengaluru 24; 10 strategy consulting manager Mumbai 32; 11 performance marketing "
         "exec Delhi 26; 12 FMCG brand manager Mumbai 34; 13 startup backend dev Bengaluru 27; 14 ML engineer "
         "Hyderabad 30; 15 gym trainer Delhi 29 (non-tech); 16 BCom student Kolkata 20. "
         "Groups: mass 2-5,12,15,16; fin-consult-mktg 7-12; builders 1,6,13,14.")

WRITE_TASK = """You are writing Gym Jarvis Ep 3 (Instagram reel, 40-60 s at 1.1x). Follow BRIEF and FACTS exactly.
Unmeasured values stay as [SLOTS]; never invent numbers or results. English only.

OUTPUT, in this order:
# SCRIPT
Beat table: Beat | E/H | Time | Spoken (one short sentence) | Top-half visual (exact: what draws on which word) |
Bottom half (face / gym footage / punch-in) | On-screen text | Viewer feels | Delivery (face/voice) | Sound.
Then: runtime estimate, save asset, honest comment trigger, the re-hooks at 1/3 and 2/3.
# VISUAL BOARD
Palette (hex), type, texture, music and SFX direction, pacing. Then one KEYFRAME per visual change:
id | time | layout (split/full) | what is on screen | motion (one or two, anchored to a word) | data source
(which measured file or [SLOT]) | why it awes without being complex.
# HOOKS
3 beat-1 variants, each on a different emotion, one line each, plus the A/B hypothesis for EXPERIMENTS.md.
# CAPTION
Caption draft (Ep 3 tag, not advice disclaimer, comment keyword)."""

CHECK_TASK = """You are an independent checker. Another model wrote this reel package. Check it against BRIEF and FACTS:
1. Every factual or numeric claim: supported by FACTS, or a clearly marked [SLOT]? List any violation.
2. Honesty: does anything imply the analyser stopped a set live, or that Fable did work the pose tool did (or the reverse)?
3. House rules: beat 1 in 1.5 s and not a recap; result by 8 s; re-hooks at 1/3 and 2/3; E/H alternation;
   40-60 s; one short sentence per beat; save asset; comment trigger; ends on payoff or loop, not "next up".
4. Visuals: are the hero visuals buildable from real pose data? Anything too complex for a viewer?
Reply: a numbered list of MUST-FIX items, then SHOULD-FIX items. Under 400 words."""

JUDGE_TASK = f"""You are an engagement panel. Another model wrote this Instagram reel package; you did not.
{PANEL}
Imagine each persona meeting this reel cold in their feed. For each persona give an ENGAGEMENT score 0-10
(10 = holds past 3 s, watches to the end, and would send, save or comment) with a short reason and the beat
where they would drop off (or "none"). Be strict: an ordinary good reel scores 5-6. Judge the visuals as
described in the VISUAL BOARD, as if built well.

Reply with JSON only:
{{"personas":[{{"id":int,"score":num,"drop_beat":str,"why":str}}],
  "groups":{{"mass":num,"fin_consult_mktg":num,"builders":num}},
  "overall":num,
  "strongest_beat":str, "weakest_beat":str,
  "top_fixes":[str, str, str, str, str]}}
overall = mean of the 16 persona scores."""


def claude(prompt, model, timeout=1800):
    cmd = ["claude", "-p", "--model", model, "--output-format", "json", "--no-session-persistence", "--tools", ""]
    with tempfile.TemporaryDirectory() as cwd:  # neutral cwd: no repo CLAUDE.md, fresh session every call
        for attempt in range(3):
            p = subprocess.run(cmd, input=prompt, capture_output=True, text=True, timeout=timeout, cwd=cwd)
            try:
                out = json.loads(p.stdout)
                if not out.get("is_error") and len(out.get("result", "")) > 200:
                    return out["result"], out.get("total_cost_usd") or 0
            except json.JSONDecodeError:
                pass
            time.sleep(20)
    raise RuntimeError(f"{model} failed: {p.stderr[-400:]} {p.stdout[-400:]}")


REPO = HERE.parent.parent


def context():
    """Everything a writer or checker needs, whole: brief, facts, the script skill and the reel defaults."""
    return ("BRIEF:\n" + (HERE / "BRIEF.md").read_text() + "\n\nFACTS:\n" + (HERE / "facts.md").read_text()
            + "\n\nSCRIPT SKILL:\n" + (REPO / ".agents/skills/reel-script-writing/SKILL.md").read_text()
            + "\n\nREEL DEFAULTS:\n" + (REPO / "production/REEL_DEFAULTS.md").read_text())


LOCKED = ("LOCKED creator decisions you may not recommend changing: the architecture diagram section stays (clarify it, "
          "never cut it); no new lifting footage; 'my AI' as the single spoken actor; the A/B variable (hook type).")


def main(target, max_rounds):
    R.mkdir(exist_ok=True)
    ctx = context()
    log, draft, check, panel = [], None, None, None
    for n in range(1, max_rounds + 1):
        if draft is None:
            wp = f"{ctx}\n\n{WRITE_TASK}"
        else:
            wp = (f"{ctx}\n\nYOUR PREVIOUS DRAFT:\n{draft}\n\nINDEPENDENT CHECK (fix every MUST-FIX):\n{check}\n\n"
                  f"ENGAGEMENT PANEL (overall {panel['overall']}/10; target {target}):\n{json.dumps(panel, indent=1)}\n\n"
                  "Revise to raise engagement for the weakest personas and groups without breaking any fact or rule. "
                  "Change what the panel says loses people; keep what works.\n\n" + WRITE_TASK)
        draft, c1 = claude(wp, WRITER)
        (R / f"v{n}_DRAFT.md").write_text(draft)
        check, c2 = claude(f"{ctx}\n\nREEL PACKAGE:\n{draft}\n\n{CHECK_TASK}", CHECKER)
        (R / f"v{n}_CHECK.md").write_text(check)
        raw, c3 = claude(f"REEL PACKAGE:\n{draft}\n\n{JUDGE_TASK}\n{LOCKED}", JUDGE)
        panel = json.loads(re.search(r"\{.*\}", raw, re.S).group(0))
        (R / f"v{n}_PANEL.json").write_text(json.dumps(panel, indent=1))
        row = {"round": n, "overall": panel["overall"], "groups": panel["groups"],
               "min_persona": min(p["score"] for p in panel["personas"]), "cost_usd": round(c1 + c2 + c3, 2)}
        log.append(row); (HERE / "iterate_log.json").write_text(json.dumps(log, indent=1))
        print(json.dumps(row), flush=True)
        if panel["overall"] >= target:
            break
        if len(log) > 1 and panel["overall"] < log[-2]["overall"]:
            print("STOP: score fell; diagnose from drop-off beats before another round", flush=True)
            break
    best = max(log, key=lambda r: r["overall"])
    print("BEST", json.dumps(best), flush=True)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--target", type=float, default=7.5)
    ap.add_argument("--max-rounds", type=int, default=5)
    a = ap.parse_args()
    main(a.target, a.max_rounds)
