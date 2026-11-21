# Independent review: Fable 5.2 reel (main + trial)

**Method note:** this panel is simulated. I modelled the 16 personas against the script text, so the numbers are judgement, not measured audience data. I checked claims only against the FACTS and CHANGES you pasted. I did not open the repo, `config/models.yaml` or the source PDFs.

## Panel averages (n = 16)

| | Stop at 3 s | Watch % | Relatability /10 | Learned /10 | Send | Save |
|---|---|---|---|---|---|---|
| Main | 63% | 47% | 6.0 | 7.1 | 13% | 22% |
| Trial | 69% | 50% | 6.7 | 6.9 | 19% | 25% |

- **The money hook stops more people.** The CA, RM, FP&A analyst and brand manager react to "forty times the price" more than to a UN quote.
- **The CEO hook splits the panel by background.** It works for the ML engineer, strategy manager and IB associate. The teacher, gym trainer and BCom student don't know what "Fable 5.2" is, so the stakes never register.
- **The main reel's biggest drop is at about 7 s.** Unease turns into "amazing things" and the risk thread is never picked up again, so several viewers feel baited.

## The four observations

- **1 · Answer key: lands.** Past papers is universal Indian exam culture and the strongest beat for all 16. The analogy is slightly off, though. Mugging up past papers is memorising, but the hack is gaming the grader. "The student who writes what the examiner wants to see" is closer and just as familiar.
- **2 · Pasted text: confuses.** "A grading rule spread to harmful instructions" can't be parsed when spoken. About 12 of 16 can't say what happened. The WhatsApp analogy lands, but it implies the model *obeys* hidden orders. The paper says it *failed to flag* them. That is a small overreach.
- **3 · Self-critical: lands.** "Marking your own exam paper" is instant and apt.
- **4 · Effort: partly lands.**
  - The intern analogy works. "Quit open-ended research without running an experiment" is lab language and loses the non-tech half of the panel.
  - The script also misses a supported fact that would make this personal: the Claude apps default to medium effort.

## Claims not supported by FACTS/CHANGES

**CEO quote (beat 1):**
- The timeline is fine: 23 Sep to 9 Nov is 47 days, so "7 weeks" holds.
- The spoken line is the one you approved. It does drop the conditional "If managed poorly". The full quote is on screen, so this is defensible.
- "Warned the UN" is accurate: it was a special Security Council meeting.
- No "wipe out" wording appears anywhere. Good.

**14% / 6 cents (beat 8):**
- The arithmetic holds: (57.2 − 49.3) / 57.2 = 13.8%, and $0.14 − $0.08 = 6 cents.
- **"Next best model, Opus" is not supported.** FACTS only compare Fable with Opus and Haiku. If Sonnet was never tested, or was tested and did better, the line is wrong.
- **"Extensively"** overstates 25 plates when the result is not conclusive.
- **"Lower" is stated as fact** while the 95% CI crosses zero. The footnote helps, but the spoken line carries the claim.
- **"6 cents"** reads oddly to an all-Indian panel. The bank RM and the teacher both asked "how much is that?"

**Other claims:**
- **"264 pages"** comes from CHANGES only. It is not in the verified facts.
- **Trial: "eleven everyday jobs", "same scores", ₹22 vs ₹0.60 and 97%** are all absent from today's FACTS.
- **The trial contradicts itself.** Beat 8 says Fable is 34% better than Haiku on food, while the hook says "same scores" on "everyday jobs".
- **The tips card is unsourced.** Tip 2 ("high only for multi-step reasoning") also conflicts with rule 4 on your own rules card ("high effort for real work").

## Top 6 fixes

1. **Beat 1 + beat 3 (main): bridge the hook.**
   - Name the product: "…before launching **Claude** Fable 5.2…".
   - In beat 3, add: "…read all 264 pages **they published about its risks**."
   - This turns the CEO warning into the reason for reading, instead of a dropped thread.
2. **Beat 5: rewrite the spoken line** (about the same length):
   - "Two: it was trained not to flag instructions in your own message, and that spread to harmful instructions hidden in pasted text. Mostly fixed. Think WhatsApp forward with a hidden order. Pasted text is data, not instructions."
3. **Beat 8: fix three claims.**
   - Say "on 25 weighed plates" instead of "extensively".
   - Keep "next best" only if Sonnet was tested and lost. Otherwise say "than Opus".
   - Add "early result" or "not conclusive yet" to the spoken line, and give the cost as about ₹5 per plate, using the conversion rate you choose.
4. **Beat 7: make it personal and plain.** "At medium effort, **the Claude app's default**, it quit research tasks without trying an experiment 63% of the time." This adds about 1 s; take it back by trimming "A half-day intern who stops at the first obstacle" to "Like a half-day intern."
5. **Beat 10 / tips card:**
   - **Option A (no sourcing work):** swap to the verified Anthropic help-center tips (Sonnet for most tasks, lower effort for routine work, new chat per topic) and attribute them to Anthropic.
   - **Option B (keep the Reddit tips):** source the threads, then reword tip 2 so it doesn't contradict rule 4, for example "lower effort for routine work, high for real work."
6. **Trial beats 1 and 13: scope and re-verify.**
   - Change "everyday jobs" to "eleven **text** jobs" in the hook, so beat 8's food result doesn't read as a contradiction.
   - Replace "Because…", which doesn't follow "That's how I use Fable", with "And on those eleven text jobs, Haiku matched Fable at 97% lower cost."
   - Re-verify ₹22 / ₹0.60 / 16/17 against the source eval before recording.

**Not checked:** whether `config/models.yaml` matches beat 9's role split, the 264 page count, and whether Sonnet was in the food eval.
