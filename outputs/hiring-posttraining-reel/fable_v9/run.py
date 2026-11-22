"""Script v9 by Fable: 3 parallel drafts (levers), a blind judge, then a merge (house scoring loop).

Run from this folder: python run.py   (writes drafts.json, judge.json, SCRIPT_v9_fable.md)
"""
import concurrent.futures as cf
import json
import random
import re
import subprocess
from pathlib import Path

HERE = Path(__file__).parent
REPO = HERE.parents[2]
BRIEF = (HERE / "BRIEF.md").read_text()
LEVERS = {
    "suspense": "Make the eval the detective: the viewer should believe the AI's slide is great until the checker turns it red, then hear the AI's own line 'I kept it as a full rollout because that is what you asked for'.",
    "struggle": "Make the AI's struggle the spine: it is smart (caught Diwali itself), the first fix does not work, the smart-looking 'waves' answer still fails, and only the checker's failure notes reveal the real problem and the fix.",
    "reliability": "Make consistency the payoff: one good answer is luck; three red runs in a row, then three green in a row, then 30 out of 30; the creator as the researcher who builds this for a living.",
}


def run(prompt: str, model: str = "claude-fable-5-2") -> str:
    cmd = ["claude", "-p", prompt, "--model", model, "--output-format", "json", "--no-session-persistence",
           "--tools", "Read", "--allowedTools", "Read"]
    for _ in range(3):
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=1800, cwd=REPO)
        try:
            out = json.loads(p.stdout[p.stdout.index("{"):])
            if not out.get("is_error"):
                return out["result"]
        except ValueError:
            pass
    raise SystemExit("failed: " + p.stdout[-300:] + p.stderr[-300:])


def js(t: str) -> dict:
    return json.loads(re.search(r"\{.*\}", t, re.S).group(0))


def main() -> None:
    with cf.ThreadPoolExecutor(3) as ex:
        futs = {k: ex.submit(run, f"{BRIEF}\n\nYOUR LEVER (deliver a complete script, but lean on this): {v}")
                for k, v in LEVERS.items()}
        drafts = {k: f.result() for k, f in futs.items()}
    (HERE / "drafts.json").write_text(json.dumps(drafts, indent=1))

    keys = list(drafts)
    random.seed(21)
    random.shuffle(keys)
    labels = {k: "ABC"[i] for i, k in enumerate(keys)}
    blind = "\n\n".join(f"=== SCRIPT {labels[k]} ===\n{drafts[k]}" for k in keys)
    judge = f"""You are an independent judge. You did not write these scripts and do not know who did.
Context (the brief the writers had):
{BRIEF}

Panel: Indian Instagram viewers scrolling at 10 pm: 1 TCS support eng 24; 2 CA 31; 3 HR exec 28; 4 bank RM 35;
5 teacher 38; 6 BTech student 21; 7 FP&A 25; 8 equity research 33; 9 Big4 analyst 24; 10 strategy mgr 32;
11 perf marketing 26; 12 FMCG brand mgr 34; 13 backend dev 27; 14 ML eng 30; 15 gym trainer 29; 16 BCom student 20.
Groups: mass 2,3,4,5,12,15,16; fin-consult-mktg 7-12; builders 1,6,13,14. Strict: an ordinary good reel = 5-6.

{blind}

For each script: per-persona engagement 0-10, group means, overall; EVAL_NECESSITY 0-10 (does the viewer believe the
AI's slide until the eval catches it, so the eval feels necessary, not obvious); VOICE_MATCH 0-10 vs the creator's
as-spoken reference (outputs/food-tracker-reel/TELEPROMPTER.md); FACT_SAFETY 0-10 (every quote and number matches the
brief's verbatim results); the 2 weakest lines with fixes. Then pick a winner and list up to 6 line-level grafts from the
others that would raise it.
JSON only: {{"scripts":{{"A":{{"personas":[16 numbers],"mass":n,"fcm":n,"builders":n,"overall":n,"eval_necessity":n,
"voice_match":n,"fact_safety":n,"weakest":[str,str]}},"B":{{...}},"C":{{...}}}},"winner":"A|B|C","graft":[str]}}"""
    res = js(run(judge))
    res["labels"] = labels
    (HERE / "judge.json").write_text(json.dumps(res, indent=1))
    win = next(k for k in keys if labels[k] == res["winner"])

    merge = f"""{BRIEF}

You wrote the script below (it won a blind judge). Apply these grafts and fixes from the judge, keep everything that
works, and recheck every quote and number against the brief. Return the final script in the same output format.

JUDGE NOTES ON YOUR SCRIPT: {json.dumps(res['scripts'][res['winner']]['weakest'])}
GRAFTS: {json.dumps(res['graft'])}

YOUR SCRIPT:
{drafts[win]}"""
    final = run(merge)
    (HERE / "SCRIPT_v9_fable.md").write_text(
        f"<!-- Fable 5.2 draft, lever '{win}', merged with blind-judge grafts. Blind scores in judge.json. -->\n\n{final}\n")
    print(json.dumps({labels[k] + "=" + k: {x: res["scripts"][labels[k]][x] for x in
                      ("overall", "mass", "fcm", "builders", "eval_necessity", "voice_match", "fact_safety")}
                      for k in keys}, indent=1))
    print("winner", res["winner"], win)


if __name__ == "__main__":
    main()
