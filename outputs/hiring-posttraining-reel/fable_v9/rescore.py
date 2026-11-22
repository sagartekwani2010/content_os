import json, random, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from run import BRIEF, run, js, HERE
d = json.loads((HERE / "drafts.json").read_text())
final = (HERE.parent / "SCRIPT_v9.md").read_text()
pair = {"prior_winner": d["reliability"], "merged": final}
keys = list(pair); random.seed(5); random.shuffle(keys); lab = {k: "AB"[i] for i, k in enumerate(keys)}
blind = "\n\n".join(f"=== SCRIPT {lab[k]} ===\n{pair[k]}" for k in keys)
p = f"""You are an independent judge; you wrote neither script. Brief the writers had:\n{BRIEF}\n
Same 16-persona Indian Instagram panel as standard (1 TCS support eng 24; 2 CA 31; 3 HR exec 28; 4 bank RM 35; 5 teacher 38;
6 BTech student 21; 7 FP&A 25; 8 equity research 33; 9 Big4 analyst 24; 10 strategy mgr 32; 11 perf marketing 26; 12 FMCG
brand mgr 34; 13 backend dev 27; 14 ML eng 30; 15 gym trainer 29; 16 BCom student 20; mass 2,3,4,5,12,15,16; fcm 7-12;
builders 1,6,13,14). Strict: an ordinary good reel = 5-6.\n\n{blind}\n
Score each: personas (16), mass, fcm, builders, overall, eval_necessity, voice_match, the drop-off beat for mass viewers,
and the 3 changes that would most raise mass viewers without breaking facts.
JSON only: {{"scripts":{{"A":{{"personas":[],"mass":n,"fcm":n,"builders":n,"overall":n,"eval_necessity":n,"voice_match":n,"mass_dropoff_beat":str,"top_fixes":[str,str,str]}},"B":{{}}}}}}"""
r = js(run(p)); r["labels"] = lab
(HERE / "rescore.json").write_text(json.dumps(r, indent=1))
for k in keys: print(k, {x: r["scripts"][lab[k]][x] for x in ("overall","mass","fcm","builders","eval_necessity","voice_match","mass_dropoff_beat")})
for k in keys: print(k, r["scripts"][lab[k]]["top_fixes"])
