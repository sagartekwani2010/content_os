import json, subprocess, random, re, concurrent.futures as cf
from pathlib import Path
EP2 = open('../../food-tracker-reel/TELEPROMPTER.md').read()
BASE = f"""You are Claude Fable 5.2, head writer. Read SCRIPT_TRIAL_v3.md (current script, self-scored 6.9) and ../facts.md (only source of numbers; judge said STOP on exactly the lunge IMG_2650 and crunch IMG_2661, verified).
The creator says there is still scope to improve. Diagnosis from comparing with the Ep 2 narration he loves (below, as he actually spoke it):
Ep 2 lines average 12.3 words, zero semicolons, 12 of 18 start with a spoken connective (So, Then, And, Which, To, Except), first person builder voice ("Then I built two agents."). v3 averages ~8 words, uses semicolons and clipped fragments ("Fair.", "Joint hidden?") - it reads like on-screen text, not like him talking.
EP 2 AS SPOKEN:
{EP2}
KEEP: Ep 2 skeleton order; Gym Jarvis in beat 1; first agent = judge, second agent = coach (numbers not allowed); pose tool + rep maths; the wave mechanism (one wave = one rep, height = range, compared with my own best wave; lat pulldown rep 4 62 vs 86 on screen); CAN'T SEE guardrail 4 of 23; 23-set results dashboard (6 continue, 11 hold, 1 stop, 1 check footage, 4 can't see); "Except this one" lunge false alarm (turned towards camera, research warned); fix: stop only when both agents agree else check footage; the one surviving stop = reverse crunch, never "stopped me mid-set"; last two beats word for word: "Next up: Salesforce is reportedly letting people go, but hiring people with AI experience." / "How can you be that one? Follow along to know."
Emotion arc: suspicion -> vindication -> earned trust. 15-19 beats, 170-200 words, one sentence per beat, no semicolons.
YOUR LEVER (focus on this, but deliver a complete script): {{lever}}
Output ONLY a JSON object: {{{{"lever":str,"beats":[{{{{"n":int,"line":str,"visual":str}}}}],"why_better":str}}}}"""
LEVERS = {
 "voice": "Rewrite every line in the creator's Ep 2 spoken voice: full conversational sentences, connectives, 'I' doing things ('So I split...', 'Then I built two agents.'). It must sound like the same man as Ep 2.",
 "stake": "Make the mechanism beats (wave) and the component beats carry a stake every gym-goer feels (e.g. your last reps get shorter when you're tired; a trainer judges you against your best rep, not a textbook; a second opinion who can't copy the first). Mass viewers (teacher, CA, HR, student) must not drift in beats 6-12.",
 "anchor": "Open exactly like Ep 2's series anchor ('In last video, Gym Jarvis read my plate...') and turn today's task + a reason to stay into beats 1-2 (one of its STOPs was wrong), then keep tension alive through the middle by planting the two red bars early.",
}
def run(prompt, model="claude-fable-5-2", tools="Read"):
    cmd=["claude","-p",prompt,"--model",model,"--output-format","json","--no-session-persistence","--tools",tools,"--allowedTools",tools,"--add-dir",".."]
    for _ in range(3):
        p=subprocess.run(cmd,capture_output=True,text=True,timeout=1800)
        try:
            o=json.loads(p.stdout[p.stdout.index('{'):])
            if not o.get("is_error"): return o["result"], list(o.get("modelUsage",{}))
        except Exception: pass
    raise SystemExit("fail "+p.stdout[-300:])
def js(t): return json.loads(re.search(r"\{.*\}",t,re.S).group(0))
with cf.ThreadPoolExecutor(3) as ex:
    futs={k:ex.submit(run,BASE.format(lever=v)) for k,v in LEVERS.items()}
    drafts={k:js(f.result()[0]) for k,f in futs.items()}
v3=open('SCRIPT_TRIAL_v3.md').read()
v3b=[{"n":int(m.group(1)),"line":m.group(2).strip()} for m in re.finditer(r'^\| (\d+) \| ([^|]+) \| \d+ \|',v3,re.M)]
drafts["v3"]={"beats":v3b}
Path("round3_drafts.json").write_text(json.dumps(drafts,indent=1))
keys=list(drafts); random.seed(7); random.shuffle(keys); labels={k:"ABCD"[i] for i,k in enumerate(keys)}
blind="\n\n".join(f"SCRIPT {labels[k]}:\n"+"\n".join(f"{b['n']}. {b['line']}" for b in drafts[k]["beats"]) for k in keys)
JUDGE=f"""You are an independent judge (you did not write these). Four spoken scripts for the same Instagram reel (creator reads them to camera; visuals carry numbers). Facts are in ../facts.md if needed.
Reference for the creator's voice, Ep 2 as spoken:
{EP2}
Panel (Indian Instagram viewers, 10 pm scroll): 1 TCS support eng 24; 2 CA 31; 3 HR exec 28; 4 bank RM 35; 5 teacher 38; 6 BTech student 21; 7 FP&A 25; 8 equity research 33; 9 Big4 analyst 24; 10 strategy mgr 32; 11 perf marketing 26; 12 FMCG brand mgr 34; 13 backend dev 27; 14 ML eng 30; 15 gym trainer 29; 16 BCom student 20. Groups: mass 2,3,4,5,12,15,16; fin-consult-mktg 7-12; builders 1,6,13,14. Strict: ordinary good reel = 5-6.
{blind}
For each script: per-persona engagement 0-10, group averages, overall; VOICE_MATCH 0-10 (sounds like the Ep 2 speaker); MECHANISM_CLARITY 0-10 (could a gym trainer repeat how a bad rep is detected); weakest 2 lines with a fix. Then pick a winner and list up to 5 line-level improvements taken from the other scripts that would raise the winner.
JSON only: {{"scripts":{{"A":{{"personas":[num x16],"mass":num,"fcm":num,"builders":num,"overall":num,"voice_match":num,"mechanism":num,"weakest":[str,str]}},...}},"winner":str,"graft":[str]}}"""
res=js(run(JUDGE)[0]); res["labels"]=labels
Path("round3_judge.json").write_text(json.dumps(res,indent=1))
print(json.dumps({labels[k]+"="+k:{x:res["scripts"][labels[k]][x] for x in ("overall","mass","fcm","builders","voice_match","mechanism")} for k in keys},indent=1)); print("winner",res["winner"],[k for k in keys if labels[k]==res["winner"]]); print(res["graft"])
