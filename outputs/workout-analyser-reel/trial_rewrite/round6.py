import json, re, subprocess, random
from pathlib import Path

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
t5=json.load(open('round5_trial.json')); r5=json.load(open('round5_vs_main.json'))
trial="\n".join(f"{b['n']}. {b['line']}" for b in t5['beats'])
add=f"""You are Claude Fable 5.2, head writer. Read ../SCRIPT_FINAL.md (the main reel, posted arm of an A/B test) and ../facts.md.
A blind judge scored the TRIAL script below 5.5 vs main 6.0. Trial wins Jarvis connection 8 vs 3, voice 8 vs 6, mechanism 7 vs 6, but loses mass viewers 4.5 vs 6 because it lacks the main's human elements. Judge said: {r5['why']}
Add to the TRIAL, keeping its Ep 2 skeleton, Gym Jarvis anchor, first/second agent lines, wave mechanism and every fact-checked wording:
1. Warmth/personal stake (the main's 'months of effort, on weekends' idea, in the trial's own words; facts.md has the build timeline).
2. One forwardable line before the tease (e.g. send this to a friend who...), true to the content and different wording from the main's.
3. A concrete, felt payoff at beat 15 (the crunch: on screen 53 vs 122 degrees; spoken in plain words), not flat 'which was fair'.
4. Trim the mechanism stretch so mass viewers don't drift: max 4 beats from 'pose tool' to 'like a trainer' (incl.), no idea lost.
TRIAL SCRIPT:
{trial}

Emotion arc stays suspicion -> vindication -> earned trust. Last two lines word for word. 16-19 beats, 170-200 words, Ep 2 voice, no semicolons.
JSON only: {{"beats":[{{"n":int,"line":str,"visual":str}}],"changes":[str]}}"""
n=js(run(add)); Path("round6_trial.json").write_text(json.dumps(n,indent=1))
new="\n".join(f"{b['n']}. {b['line']}" for b in n['beats'])
items=[("trial6",new),("trial5",trial),("main","(read the spoken lines of the latest version in ../SCRIPT_FINAL.md and judge exactly those)")]
random.seed(11); random.shuffle(items); lab={k:"PQR"[i] for i,(k,_) in enumerate(items)}
body="\n\n".join(f"SCRIPT {lab[k]}:\n{v}" for k,v in items)
judge=f"""Independent judge; you wrote none. Three spoken scripts for the same Instagram reel topic (creator reads to camera; visuals carry numbers). Facts in ../facts.md. Ep 2 voice reference:
{EP2}
Panel (Indian Instagram viewers, 10 pm): 1 TCS support eng 24; 2 CA 31; 3 HR 28; 4 bank RM 35; 5 teacher 38; 6 BTech 21; 7 FP&A 25; 8 equity research 33; 9 Big4 24; 10 strategy mgr 32; 11 perf mktg 26; 12 FMCG brand mgr 34; 13 backend dev 27; 14 ML eng 30; 15 gym trainer 29; 16 BCom 20. mass 2,3,4,5,12,15,16; fcm 7-12; builders 1,6,13,14. Strict: ordinary good reel = 5-6.
{body}
JSON only: {{"P":{{"overall":n,"mass":n,"fcm":n,"builders":n,"voice_match":n,"mechanism":n,"jarvis_connection":n,"weakest":[str]}},"Q":{{...}},"R":{{...}},"ranking":[str],"why":str}}"""
r=js(run(judge)); r["labels"]=lab; Path("round6_judge.json").write_text(json.dumps(r,indent=1))
print(new); print(n['changes'])
for k,L in lab.items(): print(k, {x:r[L][x] for x in ('overall','mass','fcm','builders','voice_match','mechanism','jarvis_connection')}, r[L]['weakest'])
print("ranking:",[ {v:k for k,v in lab.items()}[x] for x in r['ranking']], r['why'])
