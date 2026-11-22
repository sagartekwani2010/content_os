import json, sys, concurrent.futures as cf
from pathlib import Path
HERE = Path(__file__).parent; sys.path.insert(0, str(HERE))
from run import CHECKER, js, run, checker_prompt
S = sys.argv[1]
d = json.loads((HERE / "hero_daily.json").read_text())
pA = d["prompts"]["A"]
caseA = {"ask": pA.split("\n\n")[0], "data": "\n\n".join(pA.split("\n\n")[1:]) + "\n\n(This analyst was given ONLY the table above: no orders, app opens or platform split.)", "key": d["key"]}
caseF = {"ask": pA.split("\n\n")[0], "data": "\n\n".join(d["prompts"]["B"].split("\n\n")[1:]), "key": d["key"]}
def regrade(x): return js(run(checker_prompt(caseA, x["answer"]), CHECKER, S))
A = [x for x in d["rows"] if x["cond"] == "A"]
with cf.ThreadPoolExecutor(4) as ex:
    for x, e in zip(A, ex.map(regrade, A)): x["exam"] = e
    c3 = next(x for x in d["rows"] if x["cond"] == "C" and x["run"] == 3)
    c3["answer"] = run(d["prompts"]["C"], "claude-fable-5-2", S)
    c3["exam"] = js(run(checker_prompt(caseF, c3["answer"]), CHECKER, S))
(HERE / "hero_daily.json").write_text(json.dumps(d, indent=1))
for c in "ABC":
    rs = [x for x in d["rows"] if x["cond"] == c]
    print(c, [x["exam"]["pass"] for x in rs], [x["exam"].get("failure", "")[:150] for x in rs if not x["exam"]["pass"]])
for x in A:
    print("\nA run", x["run"], ":", "\n".join(l for l in x["answer"].splitlines() if l.strip())[:700])
