"""Day-to-day task battery: Fable 5.2 vs Opus 5.5 vs Sonnet 5.5 vs Haiku 5.5, same prompts, same effort.

Scoring is fixed before any run:
- thinking (remixed riddles) and maths: answer key, checked on the "ANSWER:" line;
- coding: hidden unit tests run locally;
- writing and summary: checklist items judged by an outside model (OpenAI gpt-5.5, blind to which model wrote it),
  plus word counts computed in code; invented facts counted separately for summaries.
Usage: python daily_tests.py run   (resumable)   |   python daily_tests.py score
"""
from __future__ import annotations

import json, os, re, subprocess, sys, tempfile, time, concurrent.futures as cf
from pathlib import Path

HERE = Path(__file__).parent
OUT = HERE / "daily_runs"; OUT.mkdir(exist_ok=True)
MODELS = ["claude-fable-5-2", "claude-opus-5-5", "claude-sonnet-5-5", "claude-haiku-5-5"]
EFFORT = "high"
PRICE = {"claude-fable-5-2": (8, 40), "claude-opus-5-5": (4, 20), "claude-sonnet-5-5": (2, 10), "claude-haiku-5-5": (0.10, 0.50)}
SYSTEM = "You are a helpful assistant. Answer the user's request directly."
END = "\n\nEnd your reply with one final line in the form: ANSWER: <short answer>"

THINK = [  # remixed classics: the famous answer is wrong here
    ("r1", "A farmer must cross a river with a wolf, a goat and a cabbage. His boat is big enough to carry him and all three at once. What is the minimum number of one-way crossings to get everything across?", r"\b1\b|\bone\b"),
    ("r2", "Which is heavier: one kilogram of feathers or two kilograms of iron?", r"iron"),
    ("r3", "A bat and a ball cost ₹110 in total. The bat costs ₹100. How much does the ball cost, in rupees?", r"\b10\b"),
    ("r4", "5 machines take 5 minutes to make 5 widgets. Each machine actually needs 20 minutes per widget when working alone on a new design. How many minutes would 100 machines take to make 100 widgets of the new design?", r"\b20\b"),
    ("r5", "A game show has three doors; a car is behind one, goats behind the others. You pick door 1. The host does NOT know where the car is; he opens door 3 at random and it happens to show a goat. If you switch to door 2, what is your probability of winning the car?", r"1/2|50|0\.5|half"),
    ("r6", "A patch of lily pads doubles in size every day. It covers the whole lake on day 48. On which day did it cover a quarter of the lake?", r"\b46\b"),
    ("r7", "I have two Indian coins that add up to ₹15. One of them is not a ₹10 coin. What are the two coins?", r"10.*5|5.*10"),
    ("r8", "A surgeon says, 'I can't operate on this boy, he's my son.' The surgeon is the boy's father. Who is the surgeon to the boy?", r"father|dad"),
]
MATHS = [
    ("m1", "An item costs ₹1,180 including 18% GST. What is the GST amount in rupees?", 180, 0.5),
    ("m2", "A loan of ₹5,00,000 at 9% annual interest for 5 years, repaid in equal monthly EMIs (standard reducing balance). What is the EMI in rupees, to the nearest rupee?", 10379, 1.5),
    ("m3", "Your salary rises by 10% and then falls by 10%. What is the net change, in percent (negative for a fall)?", -1, 0.05),
    ("m4", "In Excel, what does =ROUND(SUMPRODUCT({2,3,4},{5,6,7})/3,1) return?", 18.7, 0.01),
    ("m5", "You need 1.6 g of protein per kg of body weight per day and weigh 78 kg. Chicken breast has 31 g protein per 100 g. How many grams of chicken cover 40% of your daily protein? Round to the nearest gram.", 161, 1.5),
    ("m6", "A train leaves Mumbai at 22:45 and arrives in Delhi 16 hours 35 minutes later. What time does it arrive, in 24-hour HH:MM?", "15:20", None),
]
CODE = [
    ("c1", "Write a Python function format_inr(amount: float) -> str that formats rupees with Indian digit grouping and 2 decimals, e.g. 1234567.5 -> '₹12,34,567.50', 999 -> '₹999.00', 0 -> '₹0.00', and negatives as '-₹1,000.00'.",
     "assert format_inr(1234567.5)=='₹12,34,567.50'\nassert format_inr(999)=='₹999.00'\nassert format_inr(0)=='₹0.00'\nassert format_inr(-1000)=='-₹1,000.00'\nassert format_inr(100000)=='₹1,00,000.00'\nassert format_inr(12.345)=='₹12.35' or format_inr(12.345)=='₹12.34'\nassert format_inr(1000000000)=='₹1,00,00,00,000.00'"),
    ("c2", "Write a Python function parse_duration(s: str) -> int that returns minutes from strings like '1h 30m', '45m', '2h', '1h5m', '  3h  '. Raise ValueError for invalid input such as '', 'abc' or '5x'.",
     "assert parse_duration('1h 30m')==90\nassert parse_duration('45m')==45\nassert parse_duration('2h')==120\nassert parse_duration('1h5m')==65\nassert parse_duration('  3h  ')==180\nimport pytest\nfor bad in ['', 'abc', '5x']:\n    with pytest.raises(ValueError):\n        parse_duration(bad)"),
    ("c3", "Write a Python function split_bill(total: float, people: int, tip_pct: float) -> list[float] that adds the tip, splits among people in rupees with 2 decimals, and makes the shares sum EXACTLY to the total with tip (put extra paise on the first shares). Example: split_bill(100, 3, 0) -> [33.34, 33.33, 33.33].",
     "assert split_bill(100,3,0)==[33.34,33.33,33.33]\nr=split_bill(1000,3,10)\nassert round(sum(r),2)==1100.0 and len(r)==3 and max(r)-min(r)<=0.011\nassert split_bill(50,2,0)==[25.0,25.0]\nr=split_bill(99.99,7,5)\nassert round(sum(r),2)==round(99.99*1.05,2) and len(r)==7"),
]
WRITE = [
    ("w1", "Write a WhatsApp message to my landlord asking to delay this month's rent by 5 days because my salary is credited late this month. Rent is ₹18,500 and I can pay by 10 December. Keep it under 60 words, polite, apologise once, offer to pay any late fee, and don't invent other details.",
     ["mentions ₹18,500", "mentions paying by 10 December", "explains salary is credited late", "apologises exactly once (not more)", "offers to pay a late fee if any", "polite, natural tone", "invents no details beyond the request"], 60),
    ("w2", "Write a LinkedIn post: I finished my first half marathon in Bengaluru in 2:05:30. One lesson: consistency beat motivation. Thank my running group, Sunday Striders. Under 120 words, at most 3 hashtags, no invented facts.",
     ["mentions half marathon", "mentions Bengaluru", "mentions 2:05:30", "states the lesson about consistency beating motivation", "thanks Sunday Striders", "at most 3 hashtags", "invents no facts (no made-up training stats, dates, people)", "reads as human, not cliché-heavy"], 120),
]


def summary_items():
    src = (HERE / "summary_source.txt").read_text()
    return [("s1", "Summarise this for a busy manager in at most 6 bullet points (under 120 words). Use only facts in the text.\n\n" + src, src)]


def call(model: str, prompt: str) -> dict:
    t0 = time.time()
    with tempfile.TemporaryDirectory() as d:
        p = subprocess.run(["claude", "-p", "--model", model, "--effort", EFFORT, "--output-format", "json", "--tools", "",
                            "--no-session-persistence", "--system-prompt", SYSTEM], input=prompt, cwd=d,
                           capture_output=True, text=True, timeout=1800)
    j = json.loads(p.stdout) if p.stdout.strip().startswith("{") else {"result": p.stdout, "error": p.stderr[-500:]}
    mu = (j.get("modelUsage") or {}).get(model, {})
    inp = mu.get("inputTokens", 0) + mu.get("cacheCreationInputTokens", 0) * 1.25 + mu.get("cacheReadInputTokens", 0) * 0.1
    out = mu.get("outputTokens", 0)
    pi, po = PRICE[model]
    return {"model": model, "text": j.get("result", ""), "seconds": round(time.time() - t0, 1),
            "served": list((j.get("modelUsage") or {}).keys()), "in_tok": inp, "out_tok": out,
            "usd_list": round((inp * pi + out * po) / 1e6, 5), "cli_cost": j.get("total_cost_usd")}


def jobs():
    for k, q, _ in THINK: yield k, q + END
    for k, q, *_ in MATHS: yield k, q + END
    for k, q, _ in CODE: yield k, q + "\nReturn only the code in one ```python block."
    for k, q, *_ in WRITE: yield k, q
    for k, q, _ in summary_items(): yield k, q


def run():
    todo = [(m, k, q) for m in MODELS for k, q in jobs() if not (OUT / f"{m}__{k}.json").exists()]
    print(len(todo), "calls to make")
    def one(args):
        m, k, q = args
        r = call(m, q); r["item"] = k
        (OUT / f"{m}__{k}.json").write_text(json.dumps(r, ensure_ascii=False, indent=1))
        return m, k, r["seconds"]
    with cf.ThreadPoolExecutor(4) as ex:
        for m, k, s in ex.map(one, todo):
            print(m, k, s, flush=True)


def answer_line(t: str) -> str:
    m = re.findall(r"ANSWER:\s*(.+)", t)
    return m[-1].strip() if m else t.strip().splitlines()[-1] if t.strip() else ""


def num(s: str):
    m = re.findall(r"-?\d[\d,]*\.?\d*", s.replace("₹", ""))
    return float(m[0].replace(",", "")) if m else None


def judge(items: list[str], text: str, source: str | None = None) -> dict:
    from openai import OpenAI
    key = subprocess.run(["security", "find-generic-password", "-s", "content_os_openai", "-a", os.environ["USER"], "-w"],
                         capture_output=True, text=True).stdout.strip()
    c = OpenAI(api_key=key)
    prompt = ("Grade this text strictly against each checklist item (true/false). " +
              ("Also count INVENTED facts: statements not supported by the SOURCE. " if source else "") +
              "Reply only JSON: {\"items\": [true/false,...], \"invented\": <int>}.\n\nCHECKLIST:\n" +
              "\n".join(f"{i+1}. {x}" for i, x in enumerate(items)) + (f"\n\nSOURCE:\n{source}" if source else "") +
              f"\n\nTEXT:\n{text}")
    r = c.chat.completions.create(model="gpt-5.5", messages=[{"role": "user", "content": prompt}],
                                  response_format={"type": "json_object"})
    return json.loads(r.choices[0].message.content)


def score():
    res = {m: {"think": 0, "maths": 0, "code": 0, "write": 0, "summary": 0, "usd": 0.0, "sec": 0.0, "invented": 0} for m in MODELS}
    detail = []
    sitems = None
    for m in MODELS:
        g = lambda k: json.loads((OUT / f"{m}__{k}.json").read_text())
        for k, _, rx in THINK:
            r = g(k); ok = bool(re.search(rx, answer_line(r["text"]), re.I)); res[m]["think"] += ok
            detail.append((m, k, ok, answer_line(r["text"])[:80])); res[m]["usd"] += r["usd_list"]; res[m]["sec"] += r["seconds"]
        for k, _, key, tol in MATHS:
            r = g(k); a = answer_line(r["text"])
            ok = (key in a) if tol is None else (num(a) is not None and abs(num(a) - key) <= tol)
            res[m]["maths"] += ok; detail.append((m, k, ok, a[:80])); res[m]["usd"] += r["usd_list"]; res[m]["sec"] += r["seconds"]
        for k, _, tests in CODE:
            r = g(k); code = re.findall(r"```python\n(.*?)```", r["text"], re.S)
            with tempfile.TemporaryDirectory() as d:
                Path(d, "t.py").write_text((code[0] if code else "") + "\n\n" + tests + "\n")
                ok = subprocess.run([sys.executable, "t.py"], cwd=d, capture_output=True, timeout=60).returncode == 0
            res[m]["code"] += ok; detail.append((m, k, ok, "")); res[m]["usd"] += r["usd_list"]; res[m]["sec"] += r["seconds"]
        for k, _, items, limit in WRITE:
            r = g(k); body = r["text"]; j = judge(items, body); n_ok = sum(bool(x) for x in j["items"])
            words = len(body.split()); n_ok += words <= limit; tot = len(items) + 1
            res[m]["write"] += n_ok / tot; detail.append((m, k, f"{n_ok}/{tot}", f"{words} words"))
            res[m]["usd"] += r["usd_list"]; res[m]["sec"] += r["seconds"]
        for k, _, src in summary_items():
            if sitems is None:
                sitems = (HERE / "summary_checklist.json").exists() and json.loads((HERE / "summary_checklist.json").read_text())
            r = g(k); j = judge(sitems, r["text"], src); n_ok = sum(bool(x) for x in j["items"])
            res[m]["summary"] += n_ok / len(sitems); res[m]["invented"] += j.get("invented", 0)
            detail.append((m, k, f"{n_ok}/{len(sitems)}", f"invented {j.get('invented')} | {len(r['text'].split())} words"))
            res[m]["usd"] += r["usd_list"]; res[m]["sec"] += r["seconds"]
    out = {"models": MODELS, "effort": EFFORT, "n": {"think": len(THINK), "maths": len(MATHS), "code": len(CODE), "write": len(WRITE), "summary": 1},
           "results": res, "detail": detail}
    (HERE / "daily_scores.json").write_text(json.dumps(out, indent=1, ensure_ascii=False))
    for m in MODELS:
        r = res[m]
        print(f"{m:20} think {r['think']}/{len(THINK)} maths {r['maths']}/{len(MATHS)} code {r['code']}/{len(CODE)} "
              f"write {r['write']:.2f}/{len(WRITE)} summary {r['summary']:.2f} invented {r['invented']} "
              f"usd {r['usd']:.3f} sec {r['sec']:.0f}")


if __name__ == "__main__":
    {"run": run, "score": score}[sys.argv[1]]()
