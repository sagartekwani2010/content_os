import json, re, subprocess, random
from pathlib import Path
d=json.load(open('round3_drafts.json')); fc=json.load(open('round4_factcheck.json'))
EP2=open('../../food-tracker-reel/TELEPROMPTER.md').read()
def run(prompt, model="claude-fable-5-2"):
    cmd=["claude","-p",prompt,"--model",model,"--output-format","json","--no-session-persistence","--tools","Read","--allowedTools","Read","--add-dir",".."]
    for _ in range(3):
        p=subprocess.run(cmd,capture_output=True,text=True,timeout=1800)
        try:
            o=json.loads(p.stdout[p.stdout.index('{'):])
            if not o.get("is_error"): return o["result"]
        except Exception: pass
    raise SystemExit("fail")
def js(t): return json.loads(re.search(r"\{.*\}",t,re.S).group(0))
stake="\n".join(f"{b['n']}. {b['line']}" for b in d['stake']['beats'])
fix=f"""You are Claude Fable 5.2. Apply ONLY these independent fact-check fixes to this script (minimal edits, keep the voice and every other word). The last two lines stay word for word as the main reel's (same tease in both A/B arms), so ignore notes on them.
Fact rules: the system measures range, not fatigue; the can't-see refusal is a code check before any AI (4 of 23 sets); final verdicts are continue 6, hold 11, stop 1, check footage 1, can't see 4 (judge alone said stop on 2: lunge and crunch).
SCRIPT:
{stake}
FACT NOTES: {json.dumps(fc['claims'])}
JSON only: {{"beats":[{{"n":int,"line":str}}],"changes":[str]}}"""
f=js(run(fix)); Path("round5_trial.json").write_text(json.dumps(f,indent=1))
trial="\n".join(f"{b['n']}. {b['line']}" for b in f['beats'])
main=open('../SCRIPT_FINAL.md').read()
S={"trial":trial}
items=list(S.items())+[("main","(read the spoken lines of the latest version in ../SCRIPT_FINAL.md and judge exactly those)")]
random.seed(3); random.shuffle(items); lab={k:"PQ"[i] for i,(k,_) in enumerate(items)}
body="\n\n".join(f"SCRIPT {lab[k]}:\n{v}" for k,v in items)
judge=f"""Independent judge; you wrote neither. Two spoken scripts for the same Instagram reel topic (creator reads to camera; visuals carry numbers). Ep 2 voice reference:
{EP2}
Panel (Indian Instagram viewers, 10 pm): 1 TCS support eng 24; 2 CA 31; 3 HR 28; 4 bank RM 35; 5 teacher 38; 6 BTech 21; 7 FP&A 25; 8 equity research 33; 9 Big4 24; 10 strategy mgr 32; 11 perf mktg 26; 12 FMCG brand mgr 34; 13 backend dev 27; 14 ML eng 30; 15 gym trainer 29; 16 BCom 20. mass 2,3,4,5,12,15,16; fcm 7-12; builders 1,6,13,14. Strict: ordinary good reel = 5-6.
{body}
JSON only: {{"P":{{"overall":n,"mass":n,"fcm":n,"builders":n,"voice_match":n,"mechanism":n,"jarvis_connection":n,"weakest":[str]}},"Q":{{...}},"better":"P"|"Q","why":str}}"""
r=js(run(judge)); r["labels"]=lab; Path("round5_vs_main.json").write_text(json.dumps(r,indent=1))
print(trial); print(f['changes'])
for k,L in lab.items(): print(k, {x:r[L][x] for x in ('overall','mass','fcm','builders','voice_match','mechanism','jarvis_connection')})
print("better:",[k for k,L in lab.items() if L==r['better']], r['why'])
