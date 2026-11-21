"""Stage 2: from the best loop draft, make MAIN and TRIAL versions that differ only in the hook, then score both.

Experiment E2 (proposed): hook type, personal test vs contrarian self-correction, tone positive in both
(so it does not overlap with E1, which tests positive vs fear tone).

Writer: Claude Fable 5.2. Checker: Claude Opus 5.5. Panel: Claude Fable 5.2, fresh session, same 16 personas.
Usage: python ab.py
"""
import json, re
from pathlib import Path

from iterate import HERE, R, WRITER, CHECKER, JUDGE, PANEL, CHECK_TASK, LOCKED, claude, context

HYPOTHESIS = """EXPERIMENT E2 (hook type; tone held positive in both; body identical after the hook beats)
- MAIN = PERSONAL TEST hook: the creator's own test with stakes for himself, e.g. "I gave an AI every set I've
  filmed. It found the one I should never have done." Emotion: curiosity -> self-stakes.
- TRIAL = CONTRARIAN SELF-CORRECTION hook: the twist up front, e.g. "I thought this was my worst set. My AI said it
  was fine." (works with no prior reel) Emotion: surprise -> trust. It must work cold for a stranger (a claim, not a recap of the last reel).
Prediction to test: contrarian wins 3-second hold and comments (surprise + admitting a mistake); personal test
wins average watch time and saves (clear promise, payoff at the end).
Decide on, in order: 3-s hold, average watch, sends per reach, then saves and comment-keyword count."""

TASK = """Using the BEST DRAFT below, produce the two versions for EXPERIMENT E2.
Rules: change ONLY the hook beats (beat 1, and beat 2 if the hook needs it) plus the cover text; every later beat,
visual and line stays identical so the result says something about the hook alone. In TRIAL, the twist is now in
the hook, so replace the later twist re-hook with a line that pays it off instead of repeating it; keep runtime equal
within 2 s. Keep all FACTS and [SLOTS]; English only.

OUTPUT:
# MAIN (personal test)
Full beat table (same columns as the best draft), cover text, runtime.
# TRIAL (contrarian self-correction)
Full beat table, cover text, runtime.
# DIFF
Exactly which beats differ, and why each change is needed.
# HYPOTHESIS
The hypothesis, what each outcome would teach us for later reels, and the EXPERIMENTS.md log row."""

SCORE = f"""You are an engagement panel. Another model wrote these two Instagram reel versions; you did not.
{PANEL}
For EACH version and EACH persona give: 3-second hold Y/N, watch %, ENGAGEMENT 0-10 (holds, watches to the end,
would send, save or comment), send 0-10, save 0-10, comment Y/N. Be strict: an ordinary good reel scores 5-6.
Reply with JSON only:
{{"main":{{"personas":[{{"id":int,"hold":bool,"watch":num,"score":num,"send":num,"save":num,"comment":bool}}],
          "overall":num,"groups":{{"mass":num,"fin_consult_mktg":num,"builders":num}}}},
  "trial":{{same shape}},
  "prediction":str, "does_each_hook_evoke_its_emotion":str, "fixes_main":[str], "fixes_trial":[str]}}"""


def main():
    log = json.loads((HERE / "iterate_log.json").read_text())
    best = max(log, key=lambda r: r["overall"])["round"]
    draft = (R / f"v{best}_DRAFT.md").read_text()
    ctx = context()
    ab, _ = claude(f"{ctx}\n\n{HYPOTHESIS}\n\nBEST DRAFT (round {best}):\n{draft}\n\n{TASK}", WRITER)
    (HERE / "AB_VERSIONS.md").write_text(ab)
    chk, _ = claude(f"{ctx}\n\n{HYPOTHESIS}\n\nREEL PACKAGE:\n{ab}\n\n{CHECK_TASK}\n"
                    "Also check that MAIN and TRIAL differ only in the hook beats and cover.", CHECKER)
    (HERE / "AB_CHECK.md").write_text(chk)
    raw, _ = claude(f"VERSIONS:\n{ab}\n\n{SCORE}\n{LOCKED}", JUDGE)
    panel = json.loads(re.search(r"\{.*\}", raw, re.S).group(0))
    (HERE / "AB_PANEL.json").write_text(json.dumps(panel, indent=1))
    print(json.dumps({"best_round": best, "main": panel["main"]["overall"], "trial": panel["trial"]["overall"],
                      "main_groups": panel["main"]["groups"], "trial_groups": panel["trial"]["groups"]}), flush=True)


if __name__ == "__main__":
    main()
