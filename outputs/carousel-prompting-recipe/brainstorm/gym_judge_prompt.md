You are a strict, independent judge. You wrote none of these options and do not know who did.
Audience: Panel (Indian Instagram viewers scrolling at 10 pm, English only): 1 TCS support engineer Pune 24; 2 CA Ahmedabad 31; 3 HR exec Bengaluru 28; 4 bank RM Lucknow 35; 5 school teacher Jaipur 38; 6 BTech final-year Hyderabad 21; 7 FP&A analyst Gurgaon 25; 8 IB/equity research associate Mumbai 33; 9 Big 4 consulting analyst Bengaluru 24; 10 strategy consulting manager Mumbai 32; 11 performance marketing exec Delhi 26; 12 FMCG brand manager Mumbai 34; 13 startup backend dev Bengaluru 27; 14 ML engineer Hyderabad 30; 15 gym trainer Delhi 29 (non-tech); 16 BCom student Kolkata 20. Groups: mass 2-5,12,15,16; fin-consult-mktg 7-12; builders 1,6,13,14.
Creator rules: every concept explained through a real-world example a non-technical Indian viewer gets instantly; no
jargon; English only; analogies ONLY from the gym/fitness world (the creator's own); one fixed casting (who is you, who is the AI) on every slide; each technique slide shows a REAL
before -> after AI run (same model), so the example must make the difference visible in the AI's output.
Pilot evidence: modern models already show working on simple maths (step-by-step showed no correctness difference),
and already hit "exactly 40 words" without a self-check. Context, constraints, output format and clarifying
questions showed clear differences. Also judge: does the casting stay fixed on every slide (an earlier gym framing failed because roles flipped)? Is the CTA keyword good?

PART 1. Score each FRAMING 1-10 on: understand (a 15-year-old gets it in one read), familiar (real-world familiarity
for this audience), save_share (save/send pull), mapping (how cleanly the everyday world maps to EVERY technique, no
forced ones), visible (will the real before->after runs visibly show it within this framing). Be strict.
FRAMINGS:
[
 {
  "label": "A",
  "name": "Brief your spotter",
  "casting": "you = the lifter under the bar; AI = the spotter standing behind you, strong and willing but unable to read your mind. Risk: non-lifters (teacher, CA, bank RM) may not know what a spotter does, so slide 2 must show it in one drawing.",
  "hooks": [
   "A spotter who can't read your mind is dangerous. So is AI.",
   "You brief your spotter before a heavy set. You tell AI nothing.",
   "Talk to AI the way you talk to your spotter"
  ],
  "mapping": {
   "context": "You tell him the set: 'Going for 5 reps at 60 kg. It's my heaviest.'",
   "constraints": "You set the rule: 'Don't touch the bar unless it stops moving.'",
   "few_shot_examples": "You point to two past moments: 'Help like Tuesday's lift-off and that light touch on the last rep.'",
   "output_format": "You tell him how to speak: 'Count my reps out loud. One-word cues only.'",
   "prompt_chaining": "One set at a time: you talk after each set, then decide the next weight.",
   "clarifying_questions": "You tell him to ask first: 'How many reps? Do you want a lift-off?'",
   "dont_guess": "You say: 'Not sure if I'm stuck? Ask \"help?\" Don't guess and grab.'",
   "show_working_self_check": "You say: 'After the set, tell me what you saw and why you stepped in.' The set was the same, but now you can judge his call."
  },
  "save_share": "Save: the cheat sheet is 'the 8-line spotter brief'. Share: lifters tag their gym buddy ('this is you when you grab the bar on rep 2').",
  "keyword": "SPOT"
 },
 {
  "label": "B",
  "name": "Day 1 with a new trainer",
  "casting": "you = the gym member; AI = a brilliant new trainer who knows every exercise but met you 10 seconds ago. On every slide you are the one briefing and the trainer is the one delivering.",
  "hooks": [
   "Your AI is a great trainer. It just doesn't know you.",
   "You'd never tell a trainer 'make me fit' and walk off. You do it to AI daily.",
   "8 things to tell AI before it writes a single word"
  ],
  "mapping": {
   "context": "You tell him who you are: 34, desk job, bad knee, want to lose 6 kg.",
   "constraints": "You give the rules: 45 minutes, no jumping, no barbell.",
   "few_shot_examples": "You show him two workouts you enjoyed and say 'more like these'.",
   "output_format": "You ask for it on one card: exercise, sets, reps.",
   "prompt_chaining": "You ask for week 1 only, try it, report back, then he writes week 2.",
   "clarifying_questions": "You say: 'Ask me 3 things before you write the plan.'",
   "dont_guess": "You say: 'Don't guess my weights. If you don't know what I lift, leave it blank and ask me.'",
   "show_working_self_check": "You say: 'Tell me why each exercise is there, and check it against my knee before you hand it over.' The plan is not better, but now you can check it."
  },
  "save_share": "Save: the cheat sheet is 'the day-1 talk', 8 lines to paste before any ask. Share: send to the friend who says 'AI only gives generic answers'.",
  "keyword": "TRAINER"
 },
 {
  "label": "C",
  "name": "You're the coach now",
  "casting": "you = the coach; AI = the strongest new member in the gym, who lifts anything and does exactly what you say but has no idea what you want. On every slide you give the cue and the member performs.",
  "hooks": [
   "AI is the strongest guy in the gym. And he has no coach.",
   "Stop asking AI. Start coaching it.",
   "8 coaching cues that make AI lift properly"
  ],
  "mapping": {
   "context": "You tell him what he is training for: 'This is for a 5 km run, not a bodybuilding show.'",
   "constraints": "You set the session rules: 'Stop 2 reps before failure. Nothing above 40 kg.'",
   "few_shot_examples": "You do two reps yourself: 'Like this. Now you.'",
   "output_format": "You tell him how to log it: 'One line per set: weight x reps.'",
   "prompt_chaining": "One set at a time: warm-up set, you check his form, then you add plates.",
   "clarifying_questions": "You say: 'Before you touch the bar, ask me anything that is unclear.'",
   "dont_guess": "You say: 'Don't know this machine? Don't wing it. Call me.'",
   "show_working_self_check": "You say: 'Talk me through your setup before you lift: feet, grip, back.' He is not stronger for saying it, but you hear the mistake before the bar moves."
  },
  "save_share": "Save: '8 coaching cues' reads like a card pinned on the gym wall. Share: the viewer is the coach, not the confused beginner, so managers and builders can forward it without feeling silly.",
  "keyword": "COACH"
 },
 {
  "label": "D",
  "name": "The floor trainer with 200 members",
  "casting": "you = one of 200 members; AI = the floor trainer who gives everyone the same 3 sets of 10 unless you ask properly. Every slide is 'lazy ask vs sharp ask' from the same member to the same trainer.",
  "hooks": [
   "AI gives everyone the same 3 sets of 10.",
   "Generic question. Generic workout. Same with AI.",
   "Why AI gives you the same answer as everyone else"
  ],
  "mapping": {
   "context": "Instead of 'what should I do today?' you say: 'I sit 9 hours a day and my lower back hurts.'",
   "constraints": "You say: 'I have 20 minutes and the squat rack is taken.'",
   "few_shot_examples": "You say: 'I liked the two exercises you gave me last week. More like those.'",
   "output_format": "You say: 'Just write it on my card: exercise, sets, reps.'",
   "prompt_chaining": "You say: 'Show me the first exercise only. I'll do a set, you check, then the next one.'",
   "clarifying_questions": "You say: 'Ask me what you need to know first.'",
   "dont_guess": "You say: 'If you're not sure it is safe for my back, say so. Don't guess.'",
   "show_working_self_check": "You say: 'Tell me why this exercise, and look at it once more against my back pain before I start.' It is the same exercise, but now you can question it."
  },
  "save_share": "Save: 8 'lazy ask vs sharp ask' pairs on one page. Share: 'same 3 sets of 10 for everyone' is a pain every gym-goer knows, so it travels beyond the tech audience.",
  "keyword": "REPS"
 },
 {
  "label": "E",
  "name": "Text your online coach",
  "casting": "you = the client typing on WhatsApp; AI = an online coach who has never seen you and knows only what you type. On every slide you add one line to the message and the coach replies.",
  "hooks": [
   "AI has never seen you. It only reads what you type.",
   "Your AI is an online coach who has never seen your body.",
   "The 8-line message that gets a real plan, not a copy-paste one"
  ],
  "mapping": {
   "context": "Your first message says who you are: age, job, goal, injuries. He cannot see you.",
   "constraints": "You type the rules: 'Home only. 2 dumbbells. 30 minutes. No eggs.'",
   "few_shot_examples": "You forward two plans you liked: 'Like these.'",
   "output_format": "You type: 'Send it as one table I can screenshot.'",
   "prompt_chaining": "You type: 'Send week 1 only. I'll report on Sunday. Then week 2.'",
   "clarifying_questions": "You type: 'Ask me 3 questions before you make it.'",
   "dont_guess": "You type: 'If I didn't tell you something, don't assume. Write ASK ME.'",
   "show_working_self_check": "You type: 'Add one line of why per exercise and tick it against my rules before you send.' The plan may be the same, but you can now check it."
  },
  "save_share": "Save: the cheat sheet is drawn as one WhatsApp message with 8 lines, and the DM'd template is literally that first message. Share: it is the most literal framing, because prompting really is typing to someone who cannot see you.",
  "keyword": "PLAN"
 }
]

PART 2. For each technique, score each EXAMPLE 1-10 on the same five criteria (mapping = how cleanly the everyday
example maps to the technique) and pick the best one. If no example will visibly show the technique on a modern model,
say so and propose a fix.
EXAMPLES:
{
 "context": [
  {
   "label": "con1",
   "gym_moment": "The same question gets a different answer from a trainer when a 20-year-old student asks and when his worried father asks.",
   "task": "Supplement question",
   "before_prompt": "Explain creatine to me.",
   "added_line": "I'm a 20-year-old student. My parents think every supplement is a steroid, and I have to explain it to them.",
   "expected_visible_difference": "Before: a textbook explanation (energy system, loading phase, dosage). After: plain lines he can say to his parents (not a steroid, found in everyday food, what it does), with their worries answered first."
  },
  {
   "label": "con2",
   "gym_moment": "A first-timer says 'I've never lifted and I feel everyone is watching me', so the trainer starts in a quiet corner with three machines.",
   "task": "Starting the gym as a nervous beginner",
   "before_prompt": "How do I start going to the gym?",
   "added_line": "This is for me: a 38-year-old school teacher, never exercised, nervous about being judged, free only from 6 to 7 am.",
   "expected_visible_difference": "Before: generic steps (set goals, choose a gym, learn compound lifts). After: a first-week routine that fits 6 to 7 am, a note that the gym is nearly empty then, what to say at the front desk, and a direct answer to the fear of being watched."
  },
  {
   "label": "con3",
   "gym_moment": "You tell a new trainer 'I'm 34, I sit 9 hours at a bank desk, I'm vegetarian' and the plan changes on the spot.",
   "task": "Diet for weight loss",
   "before_prompt": "Suggest a diet to lose weight.",
   "added_line": "This is for me: 34, bank job, sitting 9 hours, vegetarian, lunch from the office canteen, dinner at 9:30 pm with family.",
   "expected_visible_difference": "Before: a generic list for anyone (oats, salads, grilled chicken, 5 small meals). After: what to pick at the canteen, a fix for the late family dinner, a desk snack, no meat anywhere."
  }
 ],
 "constraints": [
  {
   "label": "con1",
   "gym_moment": "Before chest day you tell the trainer: 'My right shoulder hurts. Nothing overhead.'",
   "task": "Chest workout around a sore shoulder",
   "before_prompt": "Give me a chest workout.",
   "added_line": "Must not include overhead pressing or dips: my right shoulder hurts. Max 4 exercises.",
   "expected_visible_difference": "Before: 6 or 7 exercises, usually including dips. After: exactly 4 exercises, none of them banned, so the viewer can check the list against the rule in 5 seconds."
  },
  {
   "label": "con2",
   "gym_moment": "You tell the trainer: 'No jumping, I live on the 2nd floor, and I only have two 5 kg dumbbells.'",
   "task": "Home workout",
   "before_prompt": "Give me a full-body workout.",
   "added_line": "Must: only two 5 kg dumbbells, 20 minutes. Must not: any jumping or anything loud, I live above my landlord.",
   "expected_visible_difference": "Before: a gym session with barbell squats, pull-ups and burpees, 45 to 60 minutes. After: a quiet dumbbell-only circuit that adds up to 20 minutes, with no burpees or jumping jacks anywhere."
  },
  {
   "label": "con3",
   "gym_moment": "You tell the gym's diet guy: 'Vegetarian, no eggs, hostel room, 100 rupees.'",
   "task": "High-protein dinner on a budget",
   "before_prompt": "Suggest a high-protein dinner.",
   "added_line": "Must: vegetarian, no eggs, under ₹100, cooked on one gas burner. Must not: protein powder.",
   "expected_visible_difference": "Before: grilled chicken, fish or egg dishes. After: paneer, soya chunks or dal dishes with a rough cost under ₹100, one pan, no eggs and no powder."
  }
 ],
 "few_shot_examples": [
  {
   "label": "few1",
   "gym_moment": "You play your gym buddy two songs you lift to, and he builds the rest of the playlist.",
   "task": "Names for a gym WhatsApp group",
   "before_prompt": "Suggest 5 names for our 6 am gym WhatsApp group.",
   "added_line": "We like names like \"Sore But Showing Up\" and \"Alarm Beaters 5:30\".",
   "expected_visible_difference": "Before: stock names ('Fitness Freaks', 'Morning Warriors'). After: five self-mocking, specific names in the same pattern as the two examples."
  },
  {
   "label": "few2",
   "gym_moment": "You show your trainer two workouts you actually enjoyed and say 'more like these'.",
   "task": "Message to a gym buddy who skipped",
   "before_prompt": "Write a message to my gym buddy who skipped leg day today.",
   "added_line": "In this style: \"The squat rack was asking about you. I said you're busy being weak.\" \"Your legs called. They want a refund.\"",
   "expected_visible_difference": "Before: a polite motivational message ('Consistency is key, see you tomorrow!'). After: a short teasing one-liner in the same voice as the two examples."
  },
  {
   "label": "few3",
   "gym_moment": "You show the trainer a photo of the body you want, lean not bulky, instead of trying to describe it.",
   "task": "Form cues for a squat",
   "before_prompt": "Write 3 form cues for a squat.",
   "added_line": "Write them like these two: \"Chest up, like you're showing off the logo on your T-shirt.\" \"Sit back, like the chair is a little too far.\"",
   "expected_visible_difference": "Before: textbook cues ('brace your core', 'knees track over toes'). After: three cues in the same picture style, each with a 'like...' image a beginner can feel."
  }
 ],
 "output_format": [
  {
   "label": "out1",
   "gym_moment": "The list stuck inside your locker door: shoes, towel, bottle, lock.",
   "task": "Food around a workout",
   "before_prompt": "What should I eat before and after a workout?",
   "added_line": "Reply as a checklist I can screenshot: 3 items before, 3 after, one line each.",
   "expected_visible_difference": "Before: paragraphs on carbs, protein and timing. After: a 6-line checklist. Needs a pilot, because the model may already use bullets here; the count and line limit should still make it visibly shorter."
  },
  {
   "label": "out2",
   "gym_moment": "The trainer writes your workout on one card (exercise, sets, reps) instead of giving a 10-minute speech you forget by the locker room.",
   "task": "Workout routine",
   "before_prompt": "Give me a push, pull, legs routine.",
   "added_line": "Give it as one table: day, exercise, sets, reps. No text outside the table.",
   "expected_visible_difference": "Before: a long answer with headings, tips and notes that needs scrolling. After: one table that fits a single screenshot. The exercises are the same; only the shape changes."
  },
  {
   "label": "out3",
   "gym_moment": "Under the bar you can only remember short cues like 'chest up, push the floor', not a paragraph.",
   "task": "Deadlift form",
   "before_prompt": "How do I deadlift with correct form?",
   "added_line": "Answer in 5 bullets, in the order I do them, max 8 words each.",
   "expected_visible_difference": "Before: a long guide with setup, execution, common mistakes and safety notes. After: 5 short lines you can read between sets."
  }
 ],
 "prompt_chaining": [
  {
   "label": "pro1",
   "gym_moment": "A good trainer gives you week 1, watches how you handle it, then writes week 2.",
   "task": "Zero to 5 km running plan",
   "before_prompt": "Make me a 12-week plan to go from no running to a 5 km run.",
   "added_line": "Give me weeks 1 and 2 only. Then stop and ask me how it went before writing the next weeks.",
   "expected_visible_difference": "Before: a full 12-week table written blind. After: two weeks, followed by check-in questions (any pain, how hard it felt), so the later weeks depend on your report."
  },
  {
   "label": "pro2",
   "gym_moment": "Setting up a home gym: first you agree on the equipment and the budget, and only then on the exercises.",
   "task": "Home gym in a budget",
   "before_prompt": "Set up a home gym for me in ₹30,000: what to buy, where to keep it in a small flat, and a 4-day workout plan using it.",
   "added_line": "One step at a time. First only the shopping list with prices. Stop there until I approve it.",
   "expected_visible_difference": "Before: everything at once, with a workout plan built on equipment you never agreed to. After: only a priced list and a stop, so you can swap an item before any plan depends on it."
  },
  {
   "label": "pro3",
   "gym_moment": "You don't load 100 kg on the first set. You add plates set by set and check your form before the next jump.",
   "task": "Fat-loss plan in steps",
   "before_prompt": "I'm 82 kg with a desk job. Plan my fat loss: daily calorie target, a 7-day Indian vegetarian meal plan and a grocery list.",
   "added_line": "Do step 1 only: the calorie and protein target and how you got it. Then stop and wait for my OK.",
   "expected_visible_difference": "Before: one very long answer where the meal plan and grocery list all rest on a calorie number nobody checked. After: a short answer with only the target, then a stop. The slide can show the creator correcting the number before the meals get built."
  }
 ],
 "clarifying_questions": [
  {
   "label": "cla1",
   "gym_moment": "A good trainer asks 'any injuries, how many days, what's the goal?' before writing a single exercise.",
   "task": "Weekly workout plan (already piloted with a clear difference)",
   "before_prompt": "Make me a weekly workout plan.",
   "added_line": "Before you start, ask me up to 3 questions.",
   "expected_visible_difference": "Before: a full generic 5-day plan straight away. After: no plan yet, only 3 questions (goal, days and equipment, injuries)."
  },
  {
   "label": "cla2",
   "gym_moment": "The supplement shop guy who asks 'what's your budget, and are you vegetarian?' is better than the one who hands you the biggest tub.",
   "task": "Choosing a protein powder",
   "before_prompt": "Which protein powder should I buy?",
   "added_line": "Before you start, ask me up to 3 questions.",
   "expected_visible_difference": "Before: a general buying guide covering every type. After: 3 short questions (budget, vegetarian or milk trouble, goal) and no recommendation until you answer."
  },
  {
   "label": "cla3",
   "gym_moment": "The front desk asks 'morning or evening, only gym or classes too?' before quoting a membership price.",
   "task": "Career: asking for a raise",
   "before_prompt": "Help me ask my manager for a raise.",
   "added_line": "Before you start, ask me up to 3 questions.",
   "expected_visible_difference": "Before: a generic script with blanks to fill in. After: 3 questions (time since last raise, what you achieved, the number you want) so the script can be about you."
  }
 ],
 "dont_guess": [
  {
   "label": "don1",
   "gym_moment": "The trainer filling your assessment form leaves 'body fat %' blank until he measures it. He doesn't write 18% because it looks right.",
   "task": "Career: resume bullets",
   "before_prompt": "Write 3 resume bullets for my job. I handle customer support tickets at an IT company.",
   "added_line": "Use only what I told you. Where you need something I didn't give, write [ASK ME] instead of assuming.",
   "expected_visible_difference": "Before: polished bullets with numbers you never gave ('resolved 50+ tickets daily', '95% satisfaction'). After: the same bullets with [ASK ME: tickets per day] and similar markers, so nothing false reaches your resume."
  },
  {
   "label": "don2",
   "gym_moment": "A good trainer who doesn't know your max says 'let's test it'. He doesn't just write 60 kg on your card.",
   "task": "Daily calories and protein",
   "before_prompt": "I'm 78 kg and want to lose fat. Tell me my daily calories and protein.",
   "added_line": "Use only what I told you. Where you need something I didn't give, write [ASK ME] instead of assuming.",
   "expected_visible_difference": "Before: a confident calorie number built on a height, age and activity level it assumed for you. After: protein worked out from 78 kg, and calories marked [ASK ME: height, age, activity]. Needs a pilot, because the model may state its assumptions even in the before."
  },
  {
   "label": "don3",
   "gym_moment": "Your gym buddy doesn't know that machine. The good one says 'I don't know, let's ask the trainer' instead of inventing a technique.",
   "task": "WhatsApp message to the gym owner",
   "before_prompt": "Write a WhatsApp message to my gym owner asking for a discount on my membership renewal.",
   "added_line": "Use only what I told you. Where you need something I didn't give, write [ASK ME] instead of assuming.",
   "expected_visible_difference": "Before: likely to carry made-up details such as how long you have been a member or how regular you are. After: the same message with [ASK ME] where those facts go. Needs a pilot, because the model may already leave blanks."
  }
 ],
 "show_working_self_check": [
  {
   "label": "sho1",
   "gym_moment": "You ask the diet guy: 'Show me the protein in each item.' The food is the same, but now you can add it up yourself.",
   "task": "One day of eating with the numbers shown",
   "before_prompt": "Give me one day of vegetarian eating: 1,800 calories and 100 g protein.",
   "added_line": "Show calories and protein next to each item, add them up, and tell me honestly if the total misses my targets.",
   "expected_visible_difference": "Before: a menu, often with only a claimed total. After: numbers per item, a visible sum and a verdict line (hit or short, and by how much). Needs a pilot, because the model may show per-item numbers by default; the verdict line is the part most likely to be new."
  },
  {
   "label": "sho2",
   "gym_moment": "The trainer counts the plates on both sides before you lift. The bar isn't lighter, but a loading mistake gets caught before it hurts.",
   "task": "Home workout checked against your rules",
   "before_prompt": "Plan a 3-day home workout. Rules: dumbbells only, 30 minutes a day, no jumping, easy on my left knee.",
   "added_line": "After the plan, check it against each of my 4 rules, one line per rule, and fix anything that fails before you show me.",
   "expected_visible_difference": "The plan itself will probably be about the same. After adds a 4-line check, one per rule, that the viewer can verify in 10 seconds. Say this on the slide: checkable, not more correct."
  },
  {
   "label": "sho3",
   "gym_moment": "Your trainer says 'good progress'. You ask 'compared to what?' Now you can judge his judgement.",
   "task": "Progress check",
   "before_prompt": "My bench press went from 40 kg to 50 kg in 8 weeks. Is that good progress?",
   "added_line": "Show how you judged it: what you compared it to and what you assumed about me.",
   "expected_visible_difference": "The verdict will likely be the same. After lists the assumptions behind it (beginner, body weight, reps) so you can correct a wrong one. Weakest of the three: a modern model may already explain itself, so pilot twice before choosing it."
  }
 ]
}

Reply with JSON only:
{"framings": {"<label>": {"understand": int, "familiar": int, "save_share": int, "mapping": int, "visible": int,
  "weak_mappings": [str], "best_hook": str, "keyword_ok": bool, "note": str}}, "framing_winner": str, "framing_why": str,
 "examples": {"<technique>": {"scores": {"<label>": {"understand": int, "familiar": int, "save_share": int,
  "mapping": int, "visible": int}}, "best": str, "fix": str}},
 "keep_techniques": [str], "drop_or_merge": str}