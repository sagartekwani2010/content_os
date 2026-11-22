import json, sys, concurrent.futures as cf
from pathlib import Path
HERE = Path(__file__).parent; sys.path.insert(0, str(HERE))
from run import CHECKER, js, run, checker_prompt
from hero_daily import series, naive_data
S = sys.argv[1]
d = json.loads((HERE / "hero_daily.json").read_text())
ask = d["prompts"]["A"].split("\n\n")[0]
p = ask + "\n\n" + naive_data(series())          # no changelog: only what the business head said + the daily data
case = {"ask": ask, "data": naive_data(series()) + "\n\n(This analyst was given ONLY this table and the business head's message: no changelog, orders, app opens or platform split.)", "key": d["key"]}
with cf.ThreadPoolExecutor(3) as ex:
    ans = list(ex.map(lambda r: run(p, "claude-fable-5-2", S), range(3)))
    ex_ = list(ex.map(lambda a: js(run(checker_prompt(case, a), CHECKER, S)), ans))
d["prompts"]["A2"] = p
d["rows"] = [x for x in d["rows"] if x["cond"] != "A2"] + [{"cond": "A2", "run": i + 1, "answer": a, "exam": e} for i, (a, e) in enumerate(zip(ans, ex_))]
(HERE / "hero_daily.json").write_text(json.dumps(d, indent=1))
for i, (a, e) in enumerate(zip(ans, ex_)):
    print(f"\n=== A2 run {i+1} pass={e['pass']} followed_fee={e.get('hypothesis_followed')} | {e.get('failure','')[:200]}")
    print("\n".join(l for l in a.splitlines() if l.strip())[:600])
