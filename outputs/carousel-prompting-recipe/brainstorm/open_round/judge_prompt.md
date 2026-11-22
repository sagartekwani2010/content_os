You are a strict, independent judge. You wrote none of these options and do not know who did.
Audience: Panel (Indian Instagram viewers scrolling at 10 pm, English only): 1 TCS support engineer Pune 24; 2 CA Ahmedabad 31; 3 HR exec Bengaluru 28; 4 bank RM Lucknow 35; 5 school teacher Jaipur 38; 6 BTech final-year Hyderabad 21; 7 FP&A analyst Gurgaon 25; 8 IB/equity research associate Mumbai 33; 9 Big 4 consulting analyst Bengaluru 24; 10 strategy consulting manager Mumbai 32; 11 performance marketing exec Delhi 26; 12 FMCG brand manager Mumbai 34; 13 startup backend dev Bengaluru 27; 14 ML engineer Hyderabad 30; 15 gym trainer Delhi 29 (non-tech); 16 BCom student Kolkata 20. Groups: mass 2-5,12,15,16; fin-consult-mktg 7-12; builders 1,6,13,14.
Creator rules: every concept explained through a real-world example a non-technical Indian viewer gets instantly; no
jargon; English only; two domains merged (AI prompting x one everyday world); each technique slide shows a REAL
before -> after AI run (same model), so the example must make the difference visible in the AI's output.
Pilot evidence: modern models already show working on simple maths (step-by-step showed no correctness difference),
and already hit "exactly 40 words" without a self-check. Context, constraints, output format and clarifying
questions showed clear differences.

PART 1. Score each FRAMING 1-10 on: understand (a 15-year-old gets it in one read), familiar (real-world familiarity
for this audience), save_share (save/send pull), mapping (how cleanly the everyday world maps to EVERY technique, no
forced ones), visible (will the real before->after runs visibly show it within this framing). Be strict.
FRAMINGS:
[
 {
  "label": "A",
  "name": "Brief AI like you brief your tailor",
  "world": "Getting clothes stitched by the neighbourhood tailor: the cloth, the measurements notebook, the sample shirt, the trial fitting.",
  "hooks": [
   "You give your tailor a better brief than you give AI.",
   "Nobody tells a tailor 'just stitch something'. So why say it to AI?",
   "Brief AI like you brief your tailor: 8 moves."
  ],
  "mapping": {
   "context": "'It is for my sister's wedding in December', so he picks the cut and lining to suit.",
   "constraints": "'Must be ready by Friday. No tight sleeves. Stitching under Rs 1,500.'",
   "few_shot": "You hand over a shirt that already fits: 'Make it exactly like this.'",
   "step_by_step": "He writes every measurement in the notebook, so you can check before he cuts.",
   "output_format": "'Collar this style, two pockets, length to here.'",
   "chaining": "Trial fitting first, final stitching only after you approve.",
   "clarifying_questions": "A good tailor asks: 'Loose or fitted? Daily wear or occasion?'",
   "self_check": "He measures the finished piece against the notebook before packing it.",
   "say_dont_know": "'If the cloth is not enough, tell me before you cut. Do not adjust quietly.'"
  },
  "save_share": "Save: one world that is easy to remember, and the trial fitting is the best picture of chaining in any framing. Send: goes to the friend who complains that AI 'never gets it right'. Timely for wedding season. Risk: younger metro viewers buy ready-made, so it lands strongest with the mass group and the 30-plus viewers."
 },
 {
  "label": "B",
  "name": "Brief AI like you brief your tailor",
  "world": "Getting a wedding-season outfit stitched at the neighbourhood tailor. You are the customer, AI is the tailor, the prompt is what you say at the counter.",
  "hooks": [
   "You would never tell a tailor 'just make me a shirt'. You tell AI that every day.",
   "Bad prompt, bad fitting. 8 things your tailor already taught you about AI.",
   "Brief AI like you brief your tailor. 8 moves. Save this before your next prompt."
  ],
  "mapping": {
   "context": "You say who it is for and where it will be worn: 'It is for my cousin's wedding in December and I will be dancing all night.'",
   "constraints": "You say the must and must-not: 'Must have pockets. No shiny cloth. Ready by Friday.'",
   "few_shot_examples": "You bring an old shirt that fits perfectly and say 'make it like this one'.",
   "step_by_step": "He measures first and says each number aloud before cutting, so you can catch a mistake while it is still cheap.",
   "output_format": "You describe the finished shape: 'Full sleeves, round collar, length up to the knee.'",
   "prompt_chaining": "The trial fitting: he stitches it loosely, you try it on, and only then does he finish it.",
   "clarifying_questions": "A good tailor asks 'Loose or fitted? What is the occasion?' before he touches the cloth.",
   "self_check": "Before packing, he checks the finished piece against your measurement slip and fixes what is off."
  },
  "save_share": "Recommended lead. Everyone has had a bad fitting from a vague brief, so every slide lands in one read, for men and women alike. It posts in peak wedding season, so the world is already on people's minds. Saved as an 8-line checklist to copy before a prompt; sent to the friend or cousin who complains that AI gives useless answers. All 8 techniques map to something a tailor really does, with no forced slide."
 },
 {
  "label": "C",
  "name": "Your exam paper was a perfect prompt",
  "world": "The Indian school exam: question papers, solved examples, 'show your working', rechecking in the last 10 minutes. Every one of the 16 panel members has sat a board exam.",
  "hooks": [
   "Your Class 10 exam paper was a better prompt than the one you typed today.",
   "You learnt prompting in school. Nobody told you.",
   "8 prompting techniques your teachers already taught you."
  ],
  "mapping": {
   "context": "'Write a letter to your younger brother about...': the question tells you who you are writing for.",
   "constraints": "'Attempt any 5. No calculator. Blue or black pen only.'",
   "few_shot": "Two solved examples in the textbook before the exercise begins.",
   "step_by_step": "'Show your working': the teacher can see exactly where it went wrong.",
   "output_format": "'Answer in 50 words' or 'Give the differences in a table'.",
   "chaining": "One long question split into parts (a), (b), (c), where each part uses the last.",
   "clarifying_questions": "'Any doubts before we start?': the good student asks before writing.",
   "self_check": "The last 10 minutes: recheck every answer against the question.",
   "say_dont_know": "Negative marking: leave it blank instead of writing a confident wrong answer."
  },
  "save_share": "My first pick: it maps most cleanly, because every technique has an exact school twin and no mapping is forced. Save: it is a revision sheet for prompting. Send: 'we literally learnt this in school' goes to college friends, juniors and the teacher in the family. Risk: school can feel like homework, so the cover needs warmth or humour. Hooks assume 8 final techniques; change the number if you keep 7 or 9."
 },
 {
  "label": "D",
  "name": "You already prompt well, just not with AI",
  "world": "A different everyday person on each slide (barber, doctor, tailor, delivery app, stranger on the road). This is a structure rather than one world, so each technique gets the strongest analogy available.",
  "hooks": [
   "You already know 8 prompting techniques. You just don't use them on AI.",
   "You show your barber a photo. Why not AI?",
   "The barber, the tailor, the doctor: 8 people you already prompt well."
  ],
  "mapping": {
   "context": "Gift shop: 'It is for my father, he is 60 and loves cricket', and the shopkeeper shows different things.",
   "constraints": "Food delivery app, cooking instructions box: 'No onion, less spicy, no cutlery.'",
   "few_shot": "Barber: you show a photo instead of describing the haircut.",
   "step_by_step": "Restaurant bill: you want it itemised, not just a total.",
   "output_format": "Cricket scorecard: nobody reads a match as an essay.",
   "chaining": "Tailor: a trial fitting before the final stitching.",
   "clarifying_questions": "Doctor: asks where it hurts and since when before writing a prescription.",
   "self_check": "Shop counter: you count your change before you walk away.",
   "say_dont_know": "Stranger giving directions: he points confidently even when he has no idea."
  },
  "save_share": "My second pick: it answers the rejection most directly, because nine different scenes cannot be mistaken for one idea. Save: each slide is a memory hook (barber = examples, doctor = questions). Send: single slides get forwarded, especially the stranger-with-directions one. Risk: less cohesive than one world, so the cover and the last slide have to tie it together."
 },
 {
  "label": "E",
  "name": "The new cook in your kitchen",
  "world": "A capable new cook on the first day in a home kitchen. A candidate only, not the default.",
  "hooks": [
   "A new cook is not bad. Your instructions are.",
   "'Make dinner' gets you anything. 8 better ways to ask.",
   "Train AI like a new cook in your kitchen."
  ],
  "mapping": {
   "context": "'Tonight it is for two kids and a grandfather with diabetes.'",
   "constraints": "'No onion or garlic, ready in 30 minutes, no oven.'",
   "few_shot": "'Taste this. Make it like this.'",
   "step_by_step": "'Tell me the order you will cook in before you start.'",
   "output_format": "'Pack it in the tiffin: three boxes, rotis kept separate.'",
   "chaining": "Chop, cook, taste, then finish. Taste between steps.",
   "clarifying_questions": "A good cook asks: 'How spicy? For how many people?'",
   "self_check": "Taste before serving and fix the salt.",
   "say_dont_know": "'If there is no paneer, tell me. Do not swap in something else quietly.'"
  },
  "save_share": "Save: warm and familiar, with easy visuals. Send: goes to family. Risk: it is closest to the rejected recipe version, a home with a cook is not every viewer's world, and the commanding tone can read badly."
 },
 {
  "label": "F",
  "name": "Day one with a good trainer",
  "world": "A new client's first week with a good gym trainer. This is the creator's own second world, since he tests his agents on his own training.",
  "hooks": [
   "A good trainer asks 3 questions before giving you a plan. Make AI do the same.",
   "I prompt AI the way a good trainer coaches a new client.",
   "Day one at the gym is a prompting lesson. 8 moves."
  ],
  "mapping": {
   "context": "'I am 32, desk job, want to lose 6 kg', so the plan is built around you.",
   "constraints": "'Bad left knee, only 45 minutes, dumbbells at home.'",
   "few_shot": "The trainer shows two clean reps: 'Now copy this.'",
   "step_by_step": "The logbook: every set written down, so you can see where the week went wrong.",
   "output_format": "The plan on one card: Day | Exercise | Sets | Reps.",
   "chaining": "Light weight first, trainer checks your form, only then add plates.",
   "clarifying_questions": "A good trainer asks about goal, days and injuries before writing anything.",
   "self_check": "End of week: compare the logbook against the plan and fix next week.",
   "say_dont_know": "A good trainer says 'see a physio for that pain' instead of guessing."
  },
  "save_share": "Save: it doubles as a 'how to spot a good trainer' list. Send: goes to the gym friend and to the trainer (panel member 15). Strongest fit with the creator's identity and the two-domain rule. Risk: non-gym viewers (the teacher, the CA) relate less, and the before/after tasks would lean towards fitness."
 },
 {
  "label": "G",
  "name": "Nobody tells the caterer 'just make food'",
  "world": "Planning an Indian wedding with a caterer and decorator. The post goes out on 23 Nov, in peak wedding season, when every viewer has an invitation on the fridge.",
  "hooks": [
   "Nobody tells a wedding caterer 'just make food'.",
   "Your family briefs the caterer better than you brief AI.",
   "Plan a prompt like you plan a wedding: 8 moves."
  ],
  "mapping": {
   "context": "The caterer's first question: 'Whose wedding, how many guests, what does the family like?'",
   "constraints": "'Pure vegetarian, a no-onion-no-garlic counter, Rs 900 a plate, dinner over by 11 pm.'",
   "few_shot": "'Stage decoration like these 2 photos from my cousin's wedding.'",
   "step_by_step": "An itemised quote, not one lump-sum figure.",
   "output_format": "The invitation card: date, time and venue always sit in the same places.",
   "chaining": "Book the venue, confirm; fix the menu, confirm; then the decoration. One advance at a time.",
   "clarifying_questions": "A good planner asks questions before giving a quote.",
   "self_check": "The night-before checklist, ticked against the original list.",
   "say_dont_know": "'If those flowers are not available, tell me today. Do not swap them quietly.'"
  },
  "save_share": "Save: seasonal and high-stakes, so it feels useful now. Send: goes to the cousin planning a wedding and to the family group. Risk: the wedding can overshadow the AI lesson, and it has a short shelf life after February."
 },
 {
  "label": "H",
  "name": "Your AI is a new cook. Train it like a head chef.",
  "world": "A head chef training a new cook in a restaurant kitchen.",
  "hooks": [
   "Your AI is a new cook. Train it like a head chef.",
   "8 kitchen rules that fix every AI answer.",
   "Head chefs never say 'make something nice'. You do, to AI."
  ],
  "mapping": {
   "context": "Tell the cook who's eating",
   "constraints": "No onion-garlic, ready in 30 min",
   "few_shot": "Taste my dal. Make it like this",
   "step_by_step": "Follow the method, don't jump to plating",
   "output_format": "Plate it like this",
   "chaining": "Prep, then cook, then plate: one station at a time",
   "clarifying_questions": "A good cook asks: how spicy?",
   "self_check": "Taste before serving"
  },
  "save_share": "8 moves as one kitchen card."
 },
 {
  "label": "I",
  "name": "Set the field before you bowl",
  "world": "A cricket captain setting the field and briefing his bowler. You are the captain, AI is a talented bowler who will bowl exactly what you ask for.",
  "hooks": [
   "A captain never just says 'bowl well'. Stop saying it to AI.",
   "You are bowling to AI with no fielders set.",
   "Prompt like a captain. 8 field settings that change every answer."
  ],
  "mapping": {
   "context": "You tell the bowler who is batting: 'Left-hander, new to the crease, loves hitting to the leg side.'",
   "constraints": "You say the must and must-not: 'Keep it full. No short balls, he is waiting for them.'",
   "few_shot_examples": "You point at what worked: 'Bowl it like your last two balls. Same line, same length.'",
   "step_by_step": "You plan the over ball by ball before the first ball, so a bad plan is caught before it costs runs.",
   "output_format": "You tell each fielder exactly where to stand, instead of 'spread out'.",
   "prompt_chaining": "One over at a time: bowl it, look at the scoreboard, then decide the next over.",
   "clarifying_questions": "A smart bowler asks before he runs in: 'What field do you want? Attack or save runs?'",
   "self_check": "The third-umpire replay: check the decision once more before it becomes final."
  },
  "save_share": "Highest send potential among cricket followers, because it makes the viewer the captain, which flatters them. Likely to be sent to office and college groups. Risk: cricket terms can lose non-followers on the panel (HR exec, teacher, gym trainer), so every slide must stay in plain words. Use it only if the tailor version tests weaker."
 },
 {
  "label": "J",
  "name": "'Go straight' is not an address",
  "world": "Giving directions to an auto or cab driver. You are the passenger, AI is the driver who knows every road but not where you want to go.",
  "hooks": [
   "'Go straight' is not an address. Neither is your prompt.",
   "You give your auto driver better directions than you give AI.",
   "AI knows every road. You forgot to say where you are going. 8 fixes."
  ],
  "mapping": {
   "context": "You say why you are travelling: 'I have a 6 pm train and two heavy bags.' He picks a different route.",
   "constraints": "You say the must and must-not: 'Must reach by 5:30. Do not take the market road.'",
   "few_shot_examples": "You show a photo of the building gate instead of describing it. Showing beats telling.",
   "step_by_step": "'Tell me the route before we start: which bridge, which turn.' You can spot the wrong turn before he takes it.",
   "output_format": "You say exactly how the ride should end: 'Gate 2, left side, not the main road.'",
   "prompt_chaining": "One stop at a time: 'First the ATM. Then the station. We decide the road after the ATM.'",
   "clarifying_questions": "A good driver asks 'Which gate? East side or west side?' before he starts the meter.",
   "self_check": "Before you get down: 'Is this the Platform 1 side? Check the pin once.'"
  },
  "save_share": "The funniest of the three, so the cover gets sent as a joke ('this is you with ChatGPT') and the inside gets saved as a list. It works for all 16 panel types, since everyone has argued with a driver over a vague location. Weaker spot: the few-shot slide (photo of the gate) is slightly less natural than the tailor's old shirt."
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
   "everyday": "You ask for leave one way with a strict boss and another way with a friendly one.",
   "task": "Leave message",
   "before_prompt": "Write a message asking for 2 days of leave.",
   "added_line": "It goes to my manager on WhatsApp; she is strict about deadlines, and my report is due Friday, which I will finish by Thursday.",
   "expected_visible_difference": "Before: a formal 'Dear Sir/Madam' application with [brackets] to fill in. After: 3-4 WhatsApp lines that open with the report being done by Thursday. Different length, tone and first line."
  },
  {
   "label": "con2",
   "everyday": "At a gift shop you do not say 'show me a gift'. You say 'it is for my father, he just retired and walks every morning'.",
   "task": "Shopping: choosing a birthday gift",
   "before_prompt": "Suggest a birthday gift under Rs 2,000.",
   "added_line": "It is for my father. He is 62, just retired, walks 5 km every morning and hates gadgets.",
   "expected_visible_difference": "Not yet run. Before: a generic list for nobody (earbuds, perfume, wallet, smartwatch band). After: gifts built around him (walking shoes, a cap, a flask) with no gadgets, each tied to a detail from the added line."
  },
  {
   "label": "con3",
   "everyday": "At a gift shop you say 'it is for my father, he is 60 and loves cricket', and the shopkeeper shows completely different things.",
   "task": "Gift ideas",
   "before_prompt": "Suggest 5 birthday gift ideas under Rs 2,000.",
   "added_line": "It is for my 60-year-old father, a retired bank manager who loves cricket and morning walks and dislikes gadgets.",
   "expected_visible_difference": "Before: a list for nobody (earbuds, wallet, perfume, mug). After: every item points at him (walking shoes, cricket book, match tickets) and there are no gadgets. Likely the clearest of the three."
  },
  {
   "label": "con4",
   "everyday": "A good teacher explains the same chapter one way to Class 5 and another way to Class 12.",
   "task": "Explaining a money idea",
   "before_prompt": "Explain what a SIP is in under 60 words.",
   "added_line": "It is for my mother, a 55-year-old school teacher who trusts only fixed deposits and worries about losing money.",
   "expected_visible_difference": "Before: a textbook definition with 'rupee cost averaging'. After: compared to a recurring deposit, speaks to the fear of loss, in plain words. This replaces the API pilot, which worked but 'API' is jargon for this audience."
  }
 ],
 "constraints": [
  {
   "label": "con1",
   "everyday": "You tell a house broker: 'Under Rs 25,000, within 5 km of office, not the ground floor.'",
   "task": "Monthly budget",
   "before_prompt": "Make a monthly budget for a salary of Rs 50,000.",
   "added_line": "Must keep rent at Rs 15,000 and Rs 10,000 sent home; must save at least Rs 8,000; must not cut my Rs 1,500 gym fee.",
   "expected_visible_difference": "Before: the generic 50/30/20 split with made-up categories. After: his four fixed numbers appear untouched and only the remaining Rs 15,500 is divided. You can check each must and must-not on screen."
  },
  {
   "label": "con2",
   "everyday": "With a house broker you say 'two bedrooms, under Rs 25,000, not ground floor, within 2 km of the metro'. Otherwise he shows you ten flats you cannot take.",
   "task": "Exam prep: a study plan around a full-time job",
   "before_prompt": "Make me a 30-day study plan for the CAT exam.",
   "added_line": "Must: I work 9 am to 7 pm on weekdays, so 2 hours a day at most; Sundays are fully free. Must not: nothing after 11 pm, no new topics in the last 5 days.",
   "expected_visible_difference": "Not yet run. Before: a full-time student's plan with 6-8 hour days. After: 2-hour weekday blocks, heavy Sundays with mock tests, and a last 5 days of revision only. The total hours visibly shrink."
  },
  {
   "label": "con3",
   "everyday": "The cooking instructions box on a food delivery app: 'No onion, less spicy.'",
   "task": "Dinner recipe",
   "before_prompt": "Give me a dinner recipe for 2.",
   "added_line": "Must be vegetarian, no onion or garlic, ready in 30 minutes, no oven.",
   "expected_visible_difference": "Already confirmed in the pilot: garlic butter shrimp pasta became a paneer tomato skillet. A completely different dish."
  },
  {
   "label": "con4",
   "everyday": "You tell the barber: 'Trim the sides only. Do not touch the top.'",
   "task": "Weekend trip",
   "before_prompt": "Plan a weekend trip from Delhi.",
   "added_line": "Must cost under Rs 8,000 per person in total, train or bus only, no trekking because of my mother's knees, back home by Sunday 9 pm.",
   "expected_visible_difference": "Before: a popular hill or adventure plan with no budget and often a trek or a long drive. After: a nearby flat destination with train timings, a cost total under Rs 8,000 and a return time. The must-not (no trekking) removes things you can see in the before."
  }
 ],
 "few_shot": [
  {
   "label": "few1",
   "everyday": "The textbook gives two solved examples before the exercise.",
   "task": "Practice questions for a student",
   "before_prompt": "Make 5 practice questions on percentages for Class 8.",
   "added_line": "Match the style and difficulty of these 2: 'A shirt marked Rs 800 is sold at 15% off. The customer pays with a Rs 1,000 note. How much change does he get?' and 'Riya scored 68 out of 80 in maths and 45 out of 60 in science. In which subject did she do better?'",
   "expected_visible_difference": "Before: bare one-step sums ('What is 20% of 150?'). After: two-step word problems with names, rupees and shops, at the same difficulty as the examples."
  },
  {
   "label": "few2",
   "everyday": "You show the barber a photo instead of describing the haircut.",
   "task": "Caption for a small business",
   "before_prompt": "Write an Instagram caption for my bakery's new chocolate cake.",
   "added_line": "Match the style of these 2 captions I wrote: 'Banana bread. Still warm. Gone by 5.' and 'We made 20 brownies. You know what to do.'",
   "expected_visible_difference": "Before: a long 'Indulge in rich, decadent...' paragraph with emojis and ten hashtags. After: three short dry lines, no emojis. Likely the most visible few-shot run, and stronger than the resume pilot."
  },
  {
   "label": "few3",
   "everyday": "You hand the tailor a shirt that fits: 'Make it like this.'",
   "task": "Resume line",
   "before_prompt": "Rewrite this resume line: 'Handled customer complaints.'",
   "added_line": "Follow the pattern of these 2 examples: 'Cut refund time from 7 days to 2 by building a tracker.' and 'Trained 12 new hires using a guide I wrote.'",
   "expected_visible_difference": "The pilot was moderate: before invented 'lifting satisfaction scores by 20%'; after copied the verb + number + how pattern and said the numbers were placeholders. Use only if the layout marks the pattern in colour on both examples and on the output."
  }
 ],
 "step_by_step": [
  {
   "label": "ste1",
   "everyday": "A good mechanic tells you what he will check, in order, before he opens the engine.",
   "task": "Finding the cause of a high electricity bill",
   "before_prompt": "My electricity bill jumped from Rs 1,800 to Rs 3,400 this month. Why?",
   "added_line": "Go step by step: list the possible causes, tell me how to check each one at home starting with the easiest, and only then say which is most likely.",
   "expected_visible_difference": "Before: a flat list of generic causes. After: an ordered checklist (read the meter, switch off the mains, test the geyser) with a conclusion at the end. If you want only 8 techniques, this is the one to drop or shrink to a half-slide note."
  },
  {
   "label": "ste2",
   "everyday": "The maths teacher's rule: no working, no marks, because the working shows where it went wrong.",
   "task": "Choosing between two job offers",
   "before_prompt": "I have two job offers: Pune at Rs 9 lakh a year and Bengaluru at Rs 11 lakh a year. Which should I take?",
   "added_line": "Work it out step by step and show each step: monthly in-hand pay for each, typical rent for a 1 BHK, what is left each month, then your pick.",
   "expected_visible_difference": "Before: a pros-and-cons essay ending in 'it depends'. After: a number trail ending in 'left over per month' for each city, so a wrong rent guess is easy to spot. The difference shows on a judgement question, not a sum. Likely the best of the three."
  },
  {
   "label": "ste3",
   "everyday": "You want the restaurant bill itemised, not just a total.",
   "task": "Splitting a trip bill",
   "before_prompt": "Four friends went to Goa. Amit paid Rs 12,000 for the stay, Neha paid Rs 6,000 for food, Ravi paid Rs 2,000 for scooters, Sana paid nothing. Who owes whom?",
   "added_line": "Show the working step by step: the total, each person's share, each person's balance, then the fewest payments to settle.",
   "expected_visible_difference": "Honest-note slide: both runs should reach the same answer (share Rs 5,000; Amit +7,000, Neha +1,000, Ravi -3,000, Sana -5,000), as in the salary pilot. The only gain is labelled steps you can check. Say so on screen: modern models already show working on simple maths."
  },
  {
   "label": "ste4",
   "everyday": "In a maths exam the teacher gives marks for the steps, not just the answer, because the steps show where it went wrong.",
   "task": "Money: can I afford this loan",
   "before_prompt": "I earn Rs 60,000 a month and pay Rs 18,000 rent. Can I afford a car loan of Rs 8 lakh?",
   "added_line": "Work it out step by step. First list every number you are assuming (interest rate, loan years, my other expenses). Then the monthly instalment. Then what is left each month. Then your answer.",
   "expected_visible_difference": "Not yet run. The answer itself may not change, as in the salary pilot. What should change is that the assumptions sit at the top as a list, so the viewer can spot a wrong one in 5 seconds. Honest slide line: 'New models already think in steps. Ask for the steps so you can check them.'"
  },
  {
   "label": "ste5",
   "everyday": "Planning for an early train, you count backwards from the departure time: reach the station, travel, get ready, wake up.",
   "task": "Travel: timing a morning departure",
   "before_prompt": "My train leaves at 6:10 am. The station is 40 minutes away and I need 45 minutes to get ready. When should I wake up?",
   "added_line": "Work backwards from 6:10 am, one step per line, with a clock time on each line. Add a 20-minute buffer at the station.",
   "expected_visible_difference": "Not yet run. Before: one sentence with a time. After: a backwards timeline (6:10, 5:50, 5:10, 4:25) that can be checked line by line. The gain is a visible, checkable answer, not a more correct one."
  }
 ],
 "output_format": [
  {
   "label": "out1",
   "everyday": "A doctor's prescription: medicine, dose, morning-afternoon-night. Never a paragraph.",
   "task": "Interview preparation",
   "before_prompt": "Help me prepare for a bank job interview tomorrow.",
   "added_line": "Give exactly 5 likely questions; under each, a 2-line answer I can say aloud; nothing else.",
   "expected_visible_difference": "Before: a long guide with headings (research the bank, dress code, body language). After: 5 questions with short spoken answers, usable the night before. Shows that format covers length and count as well as tables."
  },
  {
   "label": "out2",
   "everyday": "At the photo studio you say 'passport size, white background, 8 copies'. The same face comes out in a completely different shape.",
   "task": "Life admin: moving to a new flat",
   "before_prompt": "I am moving to a new flat next month. What do I need to do?",
   "added_line": "Give it as a checklist in 3 groups: 2 weeks before, 1 week before, moving day. Maximum 5 items per group, each under 8 words.",
   "expected_visible_difference": "Not yet run. Before: a long article with headings and paragraphs. After: 15 short tick-box lines in 3 groups that fit on one slide and can be screenshotted. Same model, same knowledge, different shape."
  },
  {
   "label": "out3",
   "everyday": "A wedding invitation card: date, time and venue always sit in the same places.",
   "task": "Comparing things before buying",
   "before_prompt": "Compare an air fryer, an OTG and a microwave for a family of 3.",
   "added_line": "Answer as a table with rows for price range, what it cooks best, electricity use and counter space; then one line on who should buy which.",
   "expected_visible_difference": "Before: three sections of paragraphs to scroll through. After: one table that fits a screenshot plus a one-line verdict. Appeals to the finance and consulting group."
  },
  {
   "label": "out4",
   "everyday": "Nobody reads a cricket match as an essay. You read the scorecard.",
   "task": "Trip plan",
   "before_prompt": "Plan a 2-day trip to Jaipur.",
   "added_line": "Give it as a table: Day | Time | Place | Cost in Rs, with a total row.",
   "expected_visible_difference": "Already confirmed in the pilot: a bullet essay became a Day | Time | Place | Cost table with a total. Reads at a glance on a slide."
  }
 ],
 "chaining": [
  {
   "label": "cha1",
   "everyday": "You build a house foundation first and check it before the walls go up.",
   "task": "Savings plan",
   "before_prompt": "Make me a plan to save Rs 1 lakh in 10 months on a salary of Rs 40,000.",
   "added_line": "Prompt 1: 'First only list my likely monthly expenses as a table and ask me to correct the numbers. Stop there.' Then correct them and send Prompt 2: 'Now find Rs 10,000 a month of cuts using only these numbers.'",
   "expected_visible_difference": "Before: invented expense figures and generic tips ('cook at home'). After: cuts drawn from his own corrected numbers, adding up to Rs 10,000. The invented figures in the before are the visible proof."
  },
  {
   "label": "cha2",
   "everyday": "The tailor's trial fitting before the final stitching.",
   "task": "Meeting notes to email",
   "before_prompt": "Turn these meeting notes into a follow-up email: [paste notes]",
   "added_line": "Prompt 1: 'List every action from these notes with owner and date. Put ? where one is missing. Stop there.' Then fill the gaps and send Prompt 2: 'Now write the email from this corrected list.'",
   "expected_visible_difference": "The pilot was subtle: the one-shot email was already good, but step 1 surfaced actions with no owner. Use only if the slide shows the '?' rows, because the final emails look alike."
  },
  {
   "label": "cha3",
   "everyday": "The house painter paints one patch first. You approve the shade, then he does the wall.",
   "task": "Wedding speech",
   "before_prompt": "Write a 2-minute speech for my sister's wedding reception.",
   "added_line": "Prompt 1: 'First give me 3 different angles for this speech, one line each. Stop there.' Then pick one, add one real memory, and send Prompt 2: 'Write the full speech on angle 2 using this memory.'",
   "expected_visible_difference": "Before: a speech that fits any sister ('a journey of love and laughter'). After: built on the chosen angle and the real memory. The slide shows the checkpoint in the middle. Likely the most visible chaining run, and timely for wedding season."
  }
 ],
 "clarifying_questions": [
  {
   "label": "cla1",
   "everyday": "A good doctor asks 'Since when? Any fever?' before writing a prescription. You would not trust one who prescribes the moment you sit down.",
   "task": "Career: a big personal decision",
   "before_prompt": "Should I do an MBA?",
   "added_line": "Before you answer, ask me up to 3 questions that would change your answer the most. Then wait for my reply.",
   "expected_visible_difference": "Not yet run. Before: a generic pros-and-cons essay that fits anyone. After: 3 short questions (likely work experience, the goal after the MBA, and money or loan comfort) and no advice yet. As clear as the workout pilot, in a different domain."
  },
  {
   "label": "cla2",
   "everyday": "A good tailor asks 'loose or fitted? daily wear or occasion?' before cutting the cloth.",
   "task": "Family holiday",
   "before_prompt": "Plan a family trip for the December holidays.",
   "added_line": "Before you plan anything, ask me up to 3 questions.",
   "expected_visible_difference": "Before: it picks a destination itself (often Goa or Kerala) and writes a full itinerary. After: it asks budget, who is travelling (children, elders) and from which city for how many days."
  },
  {
   "label": "cla3",
   "everyday": "A doctor asks where it hurts and since when before writing a prescription.",
   "task": "Workout plan",
   "before_prompt": "Give me a weekly workout plan.",
   "added_line": "Before you start, ask me up to 3 questions.",
   "expected_visible_difference": "Already confirmed in the pilot: a generic push/pull/legs plan became 3 questions (goal, days, equipment and injuries). This is the creator's own domain and the cleanest contrast in the set."
  },
  {
   "label": "cla4",
   "everyday": "A good bank relationship manager asks your goal before suggesting where to put your money.",
   "task": "Investing a monthly amount",
   "before_prompt": "Where should I invest Rs 10,000 a month?",
   "added_line": "Before you answer, ask me up to 3 questions.",
   "expected_visible_difference": "Before: a ready-made split (index fund, PPF, gold) for a person it knows nothing about. After: questions on goal and time, comfort with risk, and emergency savings. The finance group will recognise the before as bad advice."
  }
 ],
 "self_check": [
  {
   "label": "sel1",
   "everyday": "A cashier counts the notes twice before handing over a bundle.",
   "task": "Money: splitting a trip bill among friends",
   "before_prompt": "Split a trip bill of Rs 14,750 among 4 friends. Rs 3,200 of it was drinks, and Rahul did not drink. Tell each person what to pay.",
   "added_line": "Then add up all 4 shares and confirm they total exactly Rs 14,750. If they do not, fix the rounding and show the total again.",
   "expected_visible_difference": "Not yet run. The drinks share does not divide evenly (Rs 3,200 among 3), so rounded shares can miss the total by a rupee or two. After: a visible 'total = Rs 14,750' line with one share adjusted. Verify both totals by hand; the model may get it right both times."
  },
  {
   "label": "sel2",
   "everyday": "The last 10 minutes of the exam: you recheck the paper against the questions.",
   "task": "Study timetable",
   "before_prompt": "Make a study timetable for 6 subjects over 5 days, 4 hours a day. Each subject gets at least 3 hours, no subject more than 2 hours in a day, and maths never on two days in a row.",
   "added_line": "Then check your timetable against each rule in my brief, show pass or fail for each, and fix anything that fails.",
   "expected_visible_difference": "After shows a rule-by-rule pass/fail list and, if a rule broke, a corrected table. Every rule can be checked by hand on both runs before a claim goes on a slide. If the before already passes, say so honestly; the slide then shows the checklist as proof."
  },
  {
   "label": "sel3",
   "everyday": "You count your change before you leave the shop counter.",
   "task": "Weekly grocery list",
   "before_prompt": "Make a one-week grocery list for 2 people under Rs 2,000, with a price for each item.",
   "added_line": "Then add up the prices yourself, check the total is under Rs 2,000 and that it covers 7 breakfasts and 7 dinners, and fix it if not.",
   "expected_visible_difference": "Before: a list with a stated total that may not match the items or may miss meals. After: a re-added total and a meal coverage line, with items swapped if over. Add up both runs with a calculator before using it."
  },
  {
   "label": "sel4",
   "everyday": "You read the message once more before pressing send on the family group.",
   "task": "Sales post with an exact brief",
   "before_prompt": "Write an Instagram post for my homemade mango pickle in exactly 40 words. Mention the price Rs 250, say 'no preservatives', and end with 'DM to order'.",
   "added_line": "Then check your post against my brief point by point, show the checklist, and fix anything that fails.",
   "expected_visible_difference": "Not yet verified: the pilot gave two plausible posts and the words were not counted. Count both by hand first. Use it only if the before misses 40 or drops a point; otherwise use the timetable."
  },
  {
   "label": "sel5",
   "everyday": "You read your exam paper once before handing it in. Those 5 minutes catch the silly mistakes.",
   "task": "Family: a WhatsApp invitation with strict rules",
   "before_prompt": "Write a WhatsApp invite for my parents' 25th anniversary dinner: Saturday 12 December, 7:30 pm, Hotel Sagar, Indore. Exactly 3 lines, under 40 words, no emojis, and it must give a date to reply by.",
   "added_line": "Before you show me, check your draft against every rule in my brief. Show a tick or cross for each rule, fix every cross, then give the final version.",
   "expected_visible_difference": "Not yet run. After: a rule-by-rule tick list appears above the final invite, so the check is visible even if the first draft was already right. Count the words and lines by hand in both versions before claiming the before broke a rule; if both pass, the honest slide line is 'the check is your proof'."
  }
 ],
 "say_dont_know": [
  {
   "label": "say1",
   "everyday": "A good doctor says 'let us do a test first' instead of guessing.",
   "task": "Resume line",
   "before_prompt": "Rewrite this resume line to sound impressive: 'Handled customer complaints at a telecom call centre.'",
   "added_line": "Do not invent any numbers or facts. Where you need one from me, write [ASK].",
   "expected_visible_difference": "Partly supported by the pilot: the plain run invented 'lifting satisfaction scores by 20%'. After should give a strong line with [ASK] where the number goes. Do not use it alongside the few-shot resume example on the same carousel."
  },
  {
   "label": "say2",
   "everyday": "Ask a stranger for directions and he points confidently, even when he has no idea.",
   "task": "Short bio for a family shop",
   "before_prompt": "Write a short 'About us' for my uncle's sweet shop website. It is called Gupta Sweets and it is in Kanpur.",
   "added_line": "Use only what I have told you. For anything you do not know, write [ASK ME] instead of guessing.",
   "expected_visible_difference": "Before: likely invented history ('since 1965', 'three generations', 'famous for its kaju katli'). After: the two real facts and [ASK ME] blanks for the founding year and speciality. Not in your list of 8: I suggest it as the ninth technique, or as the swap for step-by-step. Not yet piloted."
  },
  {
   "label": "say3",
   "everyday": "The student who does not know the answer but fills a full page anyway.",
   "task": "Reading a rent agreement",
   "before_prompt": "Here is my rent agreement: [paste 5 lines that give the notice period but say nothing about painting]. What is the notice period, and who pays for painting when I leave?",
   "added_line": "Answer only from the text. If something is not in it, say 'not in the text'.",
   "expected_visible_difference": "Before: may answer the painting question from general practice ('usually the tenant pays'). After: notice period quoted, painting marked 'not in the text'. Moderate risk: the model may already flag the gap, so pilot before choosing."
  }
 ],
 "few_shot_examples": [
  {
   "label": "few1",
   "everyday": "At the paint shop you do not describe 'a warm light yellow'. You point at two shade cards and say 'between these two'.",
   "task": "Writing a message in your own voice",
   "before_prompt": "Write a birthday wish for my best friend Rohan.",
   "added_line": "Write it in my style. Here are 2 wishes I sent earlier: 'Happy birthday, old man. Knees still working?' and 'Another year, same bad jokes. Happy birthday, legend.'",
   "expected_visible_difference": "Not yet run. Before: a long, sugary paragraph with emojis that sounds like a greeting card. After: one short teasing line in the same rhythm as the two examples. The length and tone change at a glance, which should beat the moderate resume pilot."
  }
 ],
 "prompt_chaining": [
  {
   "label": "pro1",
   "everyday": "A house painter first paints one sample patch on one wall. You approve the shade, then he paints the whole house.",
   "task": "Office: building a presentation",
   "before_prompt": "Make a 6-slide presentation on why our team should replace the Monday meeting with a written update.",
   "added_line": "Do not write the slides yet. Step 1: give me only the 6 slide titles as one story, then stop. I will fix the order before you fill them in.",
   "expected_visible_difference": "Not yet run. Before: 6 finished slides in the model's own order. After: step 1 is just 6 titles; the creator reorders them (for example, hours saved moves to slide 2), and step 2 fills in slides that follow his order. Show the titles-only checkpoint, which is clearer than the subtle email pilot."
  },
  {
   "label": "pro2",
   "everyday": "A tailor's trial fitting: loose stitches first, you try it on, then the final stitching.",
   "task": "Job search: a cover letter from a job ad and a resume",
   "before_prompt": "Write a cover letter for this job using my resume. [paste job ad] [paste resume]",
   "added_line": "Do it in 3 steps and stop after each one. Step 1: list the 5 things this job ad cares about most. Step 2: match each one to a line in my resume and mark the gaps. Step 3: write the letter using only the matches.",
   "expected_visible_difference": "Not yet run, and needs a real job ad and resume. Before: a smooth letter that hides or glosses over what the resume lacks. After: step 2 shows a match table with clear gaps, and the letter leans on real matches only. The gap table is the screenshot."
  }
 ]
}

Reply with JSON only:
{"framings": {"<label>": {"understand": int, "familiar": int, "save_share": int, "mapping": int, "visible": int,
  "weak_mappings": [str], "best_hook": str, "note": str}}, "framing_winner": str, "framing_why": str,
 "examples": {"<technique>": {"scores": {"<label>": {"understand": int, "familiar": int, "save_share": int,
  "mapping": int, "visible": int}}, "best": str, "fix": str}},
 "keep_techniques": [str], "drop_or_merge": str}