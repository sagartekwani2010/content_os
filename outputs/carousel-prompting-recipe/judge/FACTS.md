# FACTS for v2 (gym prompting techniques) — what is true, measured 22 Nov 2026

Model for every run: claude-fable-5-2 via `claude -p`, plain system prompt "You are a helpful assistant.", single-turn
calls, default effort. Each BEFORE and AFTER prompt ran twice. AFTER differs from BEFORE only by the added line(s).
Chained/clarifying AFTER runs have a 2nd step whose user reply is a SCRIPTED TEST REPLY (made up for the test, not the
creator's real data). Files: runs/g*_*.md. All personas in prompts ("34, bank job…", "78 kg") are TEST PERSONAS, not
the creator. The creator is not known to be vegetarian (his food tracker logged chicken).

All calories/protein/prices in outputs are the MODEL'S ESTIMATES, not verified nutrition or prices.

1 Context (g1). Before "Suggest a diet to lose weight. Under 100 words." -> both runs generic: deficit, "1.6–2 g per
  kg", "eggs, chicken, fish, paneer…". After (+ "This is for me: 34, bank job, sitting 9 hours, vegetarian, lunch from
  the office canteen, dinner at 9:30 pm with family.") -> both runs: "Canteen lunch…", 5 pm snack "so you aren't
  starving at 9:30", lightest meal at dinner, walk after meals, vegetarian items only.
2 Constraints (g2). Before "Suggest a high-protein dinner. Under 80 words." -> both runs "Chicken and paneer bowl
  (~60 g protein)". After (+ "Must: vegetarian, no eggs, under Rs 100, cooked on one gas burner. Must not: protein
  powder.") -> both runs a one-pot soya chunk + moong dal khichdi, "~Rs 60-70" / "roughly Rs 60", "Roughly 40 g
  protein" (run 1) / "about 48 g protein" (run 2, with 200 g curd).
3 Examples (g3). Before "Suggest 5 names for our 6 am gym WhatsApp group." -> run 1: Dawn Patrol, 6 AM Iron Club,
  Snooze Is Not a Rep, Rise and Grind Crew, First Set Before Sunrise; run 2: Sunrise Sets, The 6 AM Club, Snooze Is for
  the Weak, Reps Before Chai, Alarm Survivors. After (+ two example names "Sore But Showing Up", "Alarm Beaters 5:30")
  -> run 1: Snooze Is Not a Rep, Tired But Present 6:00, Sunrise Before Excuses, Half Asleep, Full Sets, First Light,
  Last Rep; run 2: Snooze Is Not a Rep, Six Sharp, Barely Awake, Up Before Excuses, Still Dark, Still Lifting, Dawn
  Patrol 6:00. Honest read: the after copies the examples' self-deprecating tone and time-stamp pattern; the before
  already had some good names. A moderate difference.
4 Output format (g4). Before "How do I deadlift with correct form?" -> 344 and 415 words (measured, list numbers and markdown excluded). After (+ "Answer in
  5 bullets, in the order I do them, max 8 words each.") -> 36 and 33 words, 5 bullets, e.g. "Push floor away, keeping
  bar against legs."
5 Chaining (g5). Before "Make me a 12-week plan to go from no running to a 5 km run. Under 150 words." -> a full
  12-week table (cannot react to anything). After step 1: weeks 1-2 only, then stop and ask how it went; step 2 scripted
  reply "week 1 was fine, but my left shin hurt after the second run of week 2" -> run 1 "Before week 3: rest until the
  shin is pain-free… Week 3: repeat week 1"; run 2 "Week 3: Repeat week 2…". The plan changed because of the check.
6 Clarifying questions (g6). Before "Make me a weekly workout plan. Under 100 words." -> both runs a gym split with
  bench press, pull-ups, deadlifts, squats, lunges. After step 1 (+ "Before you start, ask me up to 3 questions.") ->
  3 questions: goal; days and time; equipment and injuries. Step 2 scripted answers (build muscle; 4 days, 45 min; home,
  two 10 kg dumbbells; left knee hurts on deep squats) -> 4-day dumbbell plan with "Box squat to a chair (pain-free
  depth only)".
7 Don't guess (g7). Before "I'm 78 kg and want to lose fat. Tell me my daily calories and protein." -> both runs "Start
  at about 2,000 kcal" "assuming you train a few times a week" / "assuming you are moderately active". After (+ "Use
  only what I told you. Where you need something I didn't give, write [ASK ME] instead of assuming.") -> both runs give
  protein "about 125–170 g" from weight, and "Calories: I can't give a number from weight alone" with [ASK ME] for
  height, age, sex, activity.
8 Show working + self-check (g8). Before "Give me one day of vegetarian eating: 1,800 calories and 100 g protein. Under
  120 words." -> per-meal numbers; run 1 states "about 1,785 kcal and 110 g protein" but its meals add to 1,785 kcal and
  111 g; run 2 states "about 1,800 kcal and 105 g protein" but its meals add to 1,775 kcal and 109 g (measured by us).
  After (+ "Show calories and protein next to each item, add them up, and tell me honestly if the total misses my
  targets.") -> per-item numbers; run 1 total "1,805 kcal, 102 g protein", run 2 "1,803 kcal, 114 g protein"; both
  totals match the item sums exactly (measured). Item values remain the model's estimates. Honest note: on a modern
  model this makes the answer checkable; it does not make the nutrition values more correct.
