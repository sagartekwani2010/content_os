import json, random, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from run import BRIEF, run, js, HERE
v9 = (HERE.parent / "SCRIPT_v9.md").read_text()
fixes = json.loads((HERE / "rescore.json").read_text())
lab = fixes["labels"]; mfix = fixes["scripts"][lab["merged"]]["top_fixes"]
p = f"""{BRIEF}

Below is your current script (v9). A blind judge scored it 6.5 (mass viewers 5.7, eval_necessity 8). The gate is 7.
Apply exactly these three fixes, keep everything else that works, keep every quote verbatim (results in
outputs/hiring-posttraining-reel/consulting_eval/results_ladder.json), keep 18-20 beats, each spoken beat 14 words or fewer
except the creator's confirmed line. The creator rejected any version where HE names the Diwali catch: the checker must
reveal it. Return the full script in the same format (table, teleprompter), nothing else.

FIXES:
1. {mfix[0]}
2. {mfix[1]}
3. {mfix[2]}

CURRENT SCRIPT:
{v9}"""
v10 = run(p)
(HERE.parent / "SCRIPT_v10.md").write_text("<!-- Written by Claude Fable 5.2: v9 + the blind judge's 3 fixes (round 2 of 2). -->\n\n" + v10[v10.find('#'):] + "\n")
pair = {"v9": v9, "v10": v10}
keys = list(pair); random.seed(8); random.shuffle(keys); L = {k: "AB"[i] for i, k in enumerate(keys)}
blind = "\n\n".join(f"=== SCRIPT {L[k]} ===\n{pair[k]}" for k in keys)
j = f"""You are an independent judge; you wrote neither script. Brief:\n{BRIEF}\n
Same 16-persona Indian Instagram panel (1 TCS support eng 24; 2 CA 31; 3 HR exec 28; 4 bank RM 35; 5 teacher 38; 6 BTech
student 21; 7 FP&A 25; 8 equity research 33; 9 Big4 analyst 24; 10 strategy mgr 32; 11 perf marketing 26; 12 FMCG brand mgr 34;
13 backend dev 27; 14 ML eng 30; 15 gym trainer 29; 16 BCom student 20; mass 2,3,4,5,12,15,16; fcm 7-12; builders 1,6,13,14).
Strict: an ordinary good reel = 5-6.\n\n{blind}\n
JSON only: {{"scripts":{{"A":{{"personas":[],"mass":n,"fcm":n,"builders":n,"overall":n,"eval_necessity":n,"voice_match":n,"fact_safety":n,"weakest":[str,str]}},"B":{{}}}}}}"""
r = js(run(j)); r["labels"] = L
(HERE / "round2_judge.json").write_text(json.dumps(r, indent=1))
for k in keys: print(k, {x: r["scripts"][L[k]][x] for x in ("overall","mass","fcm","builders","eval_necessity","voice_match","fact_safety")})
for k in keys: print(k, r["scripts"][L[k]]["weakest"])
