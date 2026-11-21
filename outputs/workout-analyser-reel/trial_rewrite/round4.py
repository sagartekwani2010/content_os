import json, re, subprocess, concurrent.futures as cf
from pathlib import Path
d=json.load(open('round3_drafts.json')); j=json.load(open('round3_judge.json')); lab=j['labels']; inv={v:k for k,v in lab.items()}
EP2=open('../../food-tracker-reel/TELEPROMPTER.md').read()
def txt(k): return "\n".join(f"{b['n']}. {b['line']}" for b in d[k]['beats'])
def run(prompt, model):
    cmd=["claude","-p",prompt,"--model",model,"--output-format","json","--no-session-persistence","--tools","Read","--allowedTools","Read","--add-dir",".."]
    for _ in range(3):
        p=subprocess.run(cmd,capture_output=True,text=True,timeout=1800)
        try:
            o=json.loads(p.stdout[p.stdout.index('{'):])
            if not o.get("is_error"): return o["result"], list(o.get("modelUsage",{}))
        except Exception: pass
    raise SystemExit("fail "+p.stdout[-300:])
def js(t): return json.loads(re.search(r"\{.*\}",t,re.S).group(0))
merge=f"""You are Claude Fable 5.2, head writer. A blind judge picked script B (below) and listed grafts from the other drafts. Apply ALL grafts and both weakest-line fixes, keep B's stake lines, keep the Ep 2 voice (full spoken sentences, connectives, no semicolons), keep the last two lines word for word, 16-19 beats, 170-200 words. Facts only from ../facts.md (judge said STOP on exactly 2 sets: lunge and reverse crunch; 6 continue, 11 hold, 4 can't see; final 1 stop, 1 check footage). Give each beat an on-screen visual (existing: wall of 23 sets, Gym Jarvis zoom diagram, research blocks easy/hard, SEE->JUDGE->CHECK block diagram, skeleton overlay, rep wave with best-rep ghost line + lat pulldown rep 4 62 vs 86, can't-see card, 23-bar results dashboard taller=better, lunge judge STOP vs coach GOOD, both-agree gate, crunch ghost 53 vs 122, Salesforce news, end screen).
B:
{txt(inv[j['winner']])}
OTHER DRAFTS: {chr(10).join(f'{L}:{chr(10)}{txt(inv[L])}' for L in 'ABCD' if L!=j['winner'])}
JUDGE NOTES: weakest={j['scripts'][j['winner']]['weakest']} grafts={j['graft']}
JSON only: {{"beats":[{{"n":int,"line":str,"visual":str}}],"changes":[str]}}"""
m=js(run(merge,"claude-fable-5-2")[0]); Path("round4_merged.json").write_text(json.dumps(m,indent=1))
new="\n".join(f"{b['n']}. {b['line']}" for b in m['beats'])
judge=f"""Independent judge; you wrote none of these. Two spoken scripts for one Instagram reel (creator reads to camera; visuals carry numbers). Ep 2 voice reference:
{EP2}
Panel (Indian Instagram viewers, 10 pm): 1 TCS support eng 24; 2 CA 31; 3 HR 28; 4 bank RM 35; 5 teacher 38; 6 BTech 21; 7 FP&A 25; 8 equity research 33; 9 Big4 24; 10 strategy mgr 32; 11 perf mktg 26; 12 FMCG brand mgr 34; 13 backend dev 27; 14 ML eng 30; 15 gym trainer 29; 16 BCom student 20. mass 2,3,4,5,12,15,16; fcm 7-12; builders 1,6,13,14. Strict: ordinary good reel = 5-6.
SCRIPT X:
{new}
SCRIPT Y:
{txt(inv[j['winner']])}
JSON only: {{"X":{{"personas":[16 nums],"mass":n,"fcm":n,"builders":n,"overall":n,"voice_match":n,"mechanism":n,"weakest":[str,str]}},"Y":{{...same}}}}"""
fact=f"""You are the independent fact and voice checker (Opus). Read ../facts.md. Check this spoken script line by line: every claim true to facts.md (numbers, which agent sees what, 'stopped me mid-set' never implied since footage predates the analyser, Salesforce 'reportedly'), and whether it sounds like the Ep 2 speaker:
{EP2}
SCRIPT:
{new}
JSON only: {{"claims":[{{"beat":int,"ok":bool,"note":str}}],"voice_issues":[str],"verdict":"PASS"|"FIX"}}"""
with cf.ThreadPoolExecutor(2) as ex:
    a=ex.submit(run,judge,"claude-fable-5-2"); b=ex.submit(run,fact,"claude-opus-5-5")
    jr=js(a.result()[0]); fr=js(b.result()[0])
Path("round4_judge.json").write_text(json.dumps(jr,indent=1)); Path("round4_factcheck.json").write_text(json.dumps(fr,indent=1))
print(new); print({k:{x:jr[k][x] for x in ('overall','mass','fcm','builders','voice_match','mechanism')} for k in 'XY'}); print('X weakest',jr['X']['weakest'])
print('FACT',fr['verdict'],[c for c in fr['claims'] if not c['ok']],fr['voice_issues'])
