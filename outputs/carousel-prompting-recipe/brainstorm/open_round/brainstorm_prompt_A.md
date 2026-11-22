# THE JOB
An Instagram carousel (~12 slides, 1080x1350, hand-drawn light paper style) for an Indian AI practitioner who builds AI
agents and tests them on his own gym training and food. Posts Mon 23 Nov 2026, 13:00 IST. Series: the Playbook
(prompting today -> guardrails Wed -> evals). It must teach DIFFERENT PROMPTING TECHNIQUES (not one "be specific" idea)
and be worth saving and sending. The creator rejected a first version that taught only "be specific" through one recipe.

Candidate techniques (you may merge, drop or swap one if a better everyday one exists; keep 7-9):
1 Context (who it is for, what they care about) 2 Constraints (must / must not) 3 Few-shot examples ("here are 2
examples of what I want") 4 Step-by-step reasoning (honest note: modern reasoning models already show working on simple
maths) 5 Output format (table/bullets/length) 6 Prompt chaining (split a big ask into 2-3 prompts, check between steps)
7 Clarifying questions ("ask me up to 3 questions before you start") 8 Self-check ("check your answer against my brief,
then fix it").

# CREATOR RULES
- Every concept is explained through a real-world example a non-technical Indian viewer gets instantly. No jargon, no
  abstract AI-speak. A 15-year-old understands each slide in one read. English only on screen (no Hindi words like
  "Maa", "dal" is fine as a food name).
- Two domains merged: AI prompting x one everyday world. The analogy is the hook. Not "me too".
- Each technique slide will show a REAL before -> after run on the same model (verbatim, trimmed). So for each technique
  the everyday example must also suggest a real task people bring to AI (email, trip, workout, resume, recipe, money,
  exam prep, shopping...) where adding the technique visibly changes the answer.

# AUDIENCE
Panel (Indian Instagram viewers scrolling at 10 pm, English only): 1 TCS support engineer Pune 24; 2 CA Ahmedabad 31; 3 HR exec Bengaluru 28; 4 bank RM Lucknow 35; 5 school teacher Jaipur 38; 6 BTech final-year Hyderabad 21; 7 FP&A analyst Gurgaon 25; 8 IB/equity research associate Mumbai 33; 9 Big 4 consulting analyst Bengaluru 24; 10 strategy consulting manager Mumbai 32; 11 performance marketing exec Delhi 26; 12 FMCG brand manager Mumbai 34; 13 startup backend dev Bengaluru 27; 14 ML engineer Hyderabad 30; 15 gym trainer Delhi 29 (non-tech); 16 BCom student Kolkata 20. Groups: mass 2-5,12,15,16; fin-consult-mktg 7-12; builders 1,6,13,14.

# PILOT EVIDENCE (real runs already done on claude-fable-5-2, each twice)
- Context: "Explain what an API is in under 60 words" vs + "for a grocery shop owner who has never coded; he cares about billing" -> generic waiter analogy vs UPI/stock/billing answer. Clear.
- Constraints: "dinner recipe for 2" -> garlic butter shrimp pasta; + "vegetarian, no onion or garlic, 30 min, no oven" -> paneer tomato skillet. Clear.
- Few-shot: resume line: before invented "lifting satisfaction scores by 20%"; after copied the example pattern (verb + number + how) and said the numbers are placeholders. Moderate.
- Step-by-step: salary/rent/EMI maths: before already showed working and got Rs 19,875; after same answer with labelled steps and a check. NO visible correctness difference.
- Output format: Jaipur 2-day trip -> bullet essay vs a Day|Time|Place|Cost table with a total. Clear.
- Chaining: messy meeting notes -> email: before was already a good email; the chain's first step surfaced actions with no owner ("?"). Subtle.
- Clarifying questions: "weekly workout plan" -> generic push/pull/legs vs 3 questions (goal, days, equipment/injuries). Clear.
- Self-check: "mango pickle post in exactly 40 words": both versions plausible; word counts not yet verified.

# YOUR TASK
1. Propose at least 4 DIFFERENT whole-carousel framings (different everyday worlds or structures; the kitchen /
   "train a new cook like a head chef" idea is only one candidate and must not be privileged). For each: name, the
   one-line cover hook (3 variants), the everyday world, the mapping technique -> everyday move (one line each),
   why someone would save it and send it to a friend.
2. For EACH technique, 3 real-world everyday examples (one line each, instantly familiar to an Indian viewer), each
   paired with a real AI task for the before -> after run (the exact BEFORE prompt and the one line that is ADDED in
   AFTER), chosen so the difference will be visible in the output.
Reply with JSON only:
{"framings": [{"id": str, "name": str, "world": str, "hooks": [str,str,str], "mapping": {"<technique>": str},
  "save_share": str}],
 "examples": {"<technique>": [{"everyday": str, "task": str, "before_prompt": str, "added_line": str, "expected_visible_difference": str}]}}