{
  "framings": [
    {
      "id": "exam_paper",
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
      "id": "eight_people",
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
      "id": "tailor",
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
      "id": "wedding",
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
      "id": "gym_trainer",
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
      "id": "kitchen",
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
    }
  ],
  "examples": {
    "context": [
      {
        "everyday": "At a gift shop you say 'it is for my father, he is 60 and loves cricket', and the shopkeeper shows completely different things.",
        "task": "Gift ideas",
        "before_prompt": "Suggest 5 birthday gift ideas under Rs 2,000.",
        "added_line": "It is for my 60-year-old father, a retired bank manager who loves cricket and morning walks and dislikes gadgets.",
        "expected_visible_difference": "Before: a list for nobody (earbuds, wallet, perfume, mug). After: every item points at him (walking shoes, cricket book, match tickets) and there are no gadgets. Likely the clearest of the three."
      },
      {
        "everyday": "A good teacher explains the same chapter one way to Class 5 and another way to Class 12.",
        "task": "Explaining a money idea",
        "before_prompt": "Explain what a SIP is in under 60 words.",
        "added_line": "It is for my mother, a 55-year-old school teacher who trusts only fixed deposits and worries about losing money.",
        "expected_visible_difference": "Before: a textbook definition with 'rupee cost averaging'. After: compared to a recurring deposit, speaks to the fear of loss, in plain words. This replaces the API pilot, which worked but 'API' is jargon for this audience."
      },
      {
        "everyday": "You ask for leave one way with a strict boss and another way with a friendly one.",
        "task": "Leave message",
        "before_prompt": "Write a message asking for 2 days of leave.",
        "added_line": "It goes to my manager on WhatsApp; she is strict about deadlines, and my report is due Friday, which I will finish by Thursday.",
        "expected_visible_difference": "Before: a formal 'Dear Sir/Madam' application with [brackets] to fill in. After: 3-4 WhatsApp lines that open with the report being done by Thursday. Different length, tone and first line."
      }
    ],
    "constraints": [
      {
        "everyday": "The cooking instructions box on a food delivery app: 'No onion, less spicy.'",
        "task": "Dinner recipe",
        "before_prompt": "Give me a dinner recipe for 2.",
        "added_line": "Must be vegetarian, no onion or garlic, ready in 30 minutes, no oven.",
        "expected_visible_difference": "Already confirmed in the pilot: garlic butter shrimp pasta became a paneer tomato skillet. A completely different dish."
      },
      {
        "everyday": "You tell a house broker: 'Under Rs 25,000, within 5 km of office, not the ground floor.'",
        "task": "Monthly budget",
        "before_prompt": "Make a monthly budget for a salary of Rs 50,000.",
        "added_line": "Must keep rent at Rs 15,000 and Rs 10,000 sent home; must save at least Rs 8,000; must not cut my Rs 1,500 gym fee.",
        "expected_visible_difference": "Before: the generic 50/30/20 split with made-up categories. After: his four fixed numbers appear untouched and only the remaining Rs 15,500 is divided. You can check each must and must-not on screen."
      },
      {
        "everyday": "You tell the barber: 'Trim the sides only. Do not touch the top.'",
        "task": "Weekend trip",
        "before_prompt": "Plan a weekend trip from Delhi.",
        "added_line": "Must cost under Rs 8,000 per person in total, train or bus only, no trekking because of my mother's knees, back home by Sunday 9 pm.",
        "expected_visible_difference": "Before: a popular hill or adventure plan with no budget and often a trek or a long drive. After: a nearby flat destination with train timings, a cost total under Rs 8,000 and a return time. The must-not (no trekking) removes things you can see in the before."
      }
    ],
    "few_shot": [
      {
        "everyday": "You show the barber a photo instead of describing the haircut.",
        "task": "Caption for a small business",
        "before_prompt": "Write an Instagram caption for my bakery's new chocolate cake.",
        "added_line": "Match the style of these 2 captions I wrote: 'Banana bread. Still warm. Gone by 5.' and 'We made 20 brownies. You know what to do.'",
        "expected_visible_difference": "Before: a long 'Indulge in rich, decadent...' paragraph with emojis and ten hashtags. After: three short dry lines, no emojis. Likely the most visible few-shot run, and stronger than the resume pilot."
      },
      {
        "everyday": "The textbook gives two solved examples before the exercise.",
        "task": "Practice questions for a student",
        "before_prompt": "Make 5 practice questions on percentages for Class 8.",
        "added_line": "Match the style and difficulty of these 2: 'A shirt marked Rs 800 is sold at 15% off. The customer pays with a Rs 1,000 note. How much change does he get?' and 'Riya scored 68 out of 80 in maths and 45 out of 60 in science. In which subject did she do better?'",
        "expected_visible_difference": "Before: bare one-step sums ('What is 20% of 150?'). After: two-step word problems with names, rupees and shops, at the same difficulty as the examples."
      },
      {
        "everyday": "You hand the tailor a shirt that fits: 'Make it like this.'",
        "task": "Resume line",
        "before_prompt": "Rewrite this resume line: 'Handled customer complaints.'",
        "added_line": "Follow the pattern of these 2 examples: 'Cut refund time from 7 days to 2 by building a tracker.' and 'Trained 12 new hires using a guide I wrote.'",
        "expected_visible_difference": "The pilot was moderate: before invented 'lifting satisfaction scores by 20%'; after copied the verb + number + how pattern and said the numbers were placeholders. Use only if the layout marks the pattern in colour on both examples and on the output."
      }
    ],
    "step_by_step": [
      {
        "everyday": "The maths teacher's rule: no working, no marks, because the working shows where it went wrong.",
        "task": "Choosing between two job offers",
        "before_prompt": "I have two job offers: Pune at Rs 9 lakh a year and Bengaluru at Rs 11 lakh a year. Which should I take?",
        "added_line": "Work it out step by step and show each step: monthly in-hand pay for each, typical rent for a 1 BHK, what is left each month, then your pick.",
        "expected_visible_difference": "Before: a pros-and-cons essay ending in 'it depends'. After: a number trail ending in 'left over per month' for each city, so a wrong rent guess is easy to spot. The difference shows on a judgement question, not a sum. Likely the best of the three."
      },
      {
        "everyday": "You want the restaurant bill itemised, not just a total.",
        "task": "Splitting a trip bill",
        "before_prompt": "Four friends went to Goa. Amit paid Rs 12,000 for the stay, Neha paid Rs 6,000 for food, Ravi paid Rs 2,000 for scooters, Sana paid nothing. Who owes whom?",
        "added_line": "Show the working step by step: the total, each person's share, each person's balance, then the fewest payments to settle.",
        "expected_visible_difference": "Honest-note slide: both runs should reach the same answer (share Rs 5,000; Amit +7,000, Neha +1,000, Ravi -3,000, Sana -5,000), as in the salary pilot. The only gain is labelled steps you can check. Say so on screen: modern models already show working on simple maths."
      },
      {
        "everyday": "A good mechanic tells you what he will check, in order, before he opens the engine.",
        "task": "Finding the cause of a high electricity bill",
        "before_prompt": "My electricity bill jumped from Rs 1,800 to Rs 3,400 this month. Why?",
        "added_line": "Go step by step: list the possible causes, tell me how to check each one at home starting with the easiest, and only then say which is most likely.",
        "expected_visible_difference": "Before: a flat list of generic causes. After: an ordered checklist (read the meter, switch off the mains, test the geyser) with a conclusion at the end. If you want only 8 techniques, this is the one to drop or shrink to a half-slide note."
      }
    ],
    "output_format": [
      {
        "everyday": "Nobody reads a cricket match as an essay. You read the scorecard.",
        "task": "Trip plan",
        "before_prompt": "Plan a 2-day trip to Jaipur.",
        "added_line": "Give it as a table: Day | Time | Place | Cost in Rs, with a total row.",
        "expected_visible_difference": "Already confirmed in the pilot: a bullet essay became a Day | Time | Place | Cost table with a total. Reads at a glance on a slide."
      },
      {
        "everyday": "A doctor's prescription: medicine, dose, morning-afternoon-night. Never a paragraph.",
        "task": "Interview preparation",
        "before_prompt": "Help me prepare for a bank job interview tomorrow.",
        "added_line": "Give exactly 5 likely questions; under each, a 2-line answer I can say aloud; nothing else.",
        "expected_visible_difference": "Before: a long guide with headings (research the bank, dress code, body language). After: 5 questions with short spoken answers, usable the night before. Shows that format covers length and count as well as tables."
      },
      {
        "everyday": "A wedding invitation card: date, time and venue always sit in the same places.",
        "task": "Comparing things before buying",
        "before_prompt": "Compare an air fryer, an OTG and a microwave for a family of 3.",
        "added_line": "Answer as a table with rows for price range, what it cooks best, electricity use and counter space; then one line on who should buy which.",
        "expected_visible_difference": "Before: three sections of paragraphs to scroll through. After: one table that fits a screenshot plus a one-line verdict. Appeals to the finance and consulting group."
      }
    ],
    "chaining": [
      {
        "everyday": "The house painter paints one patch first. You approve the shade, then he does the wall.",
        "task": "Wedding speech",
        "before_prompt": "Write a 2-minute speech for my sister's wedding reception.",
        "added_line": "Prompt 1: 'First give me 3 different angles for this speech, one line each. Stop there.' Then pick one, add one real memory, and send Prompt 2: 'Write the full speech on angle 2 using this memory.'",
        "expected_visible_difference": "Before: a speech that fits any sister ('a journey of love and laughter'). After: built on the chosen angle and the real memory. The slide shows the checkpoint in the middle. Likely the most visible chaining run, and timely for wedding season."
      },
      {
        "everyday": "You build a house foundation first and check it before the walls go up.",
        "task": "Savings plan",
        "before_prompt": "Make me a plan to save Rs 1 lakh in 10 months on a salary of Rs 40,000.",
        "added_line": "Prompt 1: 'First only list my likely monthly expenses as a table and ask me to correct the numbers. Stop there.' Then correct them and send Prompt 2: 'Now find Rs 10,000 a month of cuts using only these numbers.'",
        "expected_visible_difference": "Before: invented expense figures and generic tips ('cook at home'). After: cuts drawn from his own corrected numbers, adding up to Rs 10,000. The invented figures in the before are the visible proof."
      },
      {
        "everyday": "The tailor's trial fitting before the final stitching.",
        "task": "Meeting notes to email",
        "before_prompt": "Turn these meeting notes into a follow-up email: [paste notes]",
        "added_line": "Prompt 1: 'List every action from these notes with owner and date. Put ? where one is missing. Stop there.' Then fill the gaps and send Prompt 2: 'Now write the email from this corrected list.'",
        "expected_visible_difference": "The pilot was subtle: the one-shot email was already good, but step 1 surfaced actions with no owner. Use only if the slide shows the '?' rows, because the final emails look alike."
      }
    ],
    "clarifying_questions": [
      {
        "everyday": "A doctor asks where it hurts and since when before writing a prescription.",
        "task": "Workout plan",
        "before_prompt": "Give me a weekly workout plan.",
        "added_line": "Before you start, ask me up to 3 questions.",
        "expected_visible_difference": "Already confirmed in the pilot: a generic push/pull/legs plan became 3 questions (goal, days, equipment and injuries). This is the creator's own domain and the cleanest contrast in the set."
      },
      {
        "everyday": "A good bank relationship manager asks your goal before suggesting where to put your money.",
        "task": "Investing a monthly amount",
        "before_prompt": "Where should I invest Rs 10,000 a month?",
        "added_line": "Before you answer, ask me up to 3 questions.",
        "expected_visible_difference": "Before: a ready-made split (index fund, PPF, gold) for a person it knows nothing about. After: questions on goal and time, comfort with risk, and emergency savings. The finance group will recognise the before as bad advice."
      },
      {
        "everyday": "A good tailor asks 'loose or fitted? daily wear or occasion?' before cutting the cloth.",
        "task": "Family holiday",
        "before_prompt": "Plan a family trip for the December holidays.",
        "added_line": "Before you plan anything, ask me up to 3 questions.",
        "expected_visible_difference": "Before: it picks a destination itself (often Goa or Kerala) and writes a full itinerary. After: it asks budget, who is travelling (children, elders) and from which city for how many days."
      }
    ],
    "self_check": [
      {
        "everyday": "The last 10 minutes of the exam: you recheck the paper against the questions.",
        "task": "Study timetable",
        "before_prompt": "Make a study timetable for 6 subjects over 5 days, 4 hours a day. Each subject gets at least 3 hours, no subject more than 2 hours in a day, and maths never on two days in a row.",
        "added_line": "Then check your timetable against each rule in my brief, show pass or fail for each, and fix anything that fails.",
        "expected_visible_difference": "After shows a rule-by-rule pass/fail list and, if a rule broke, a corrected table. Every rule can be checked by hand on both runs before a claim goes on a slide. If the before already passes, say so honestly; the slide then shows the checklist as proof."
      },
      {
        "everyday": "You count your change before you leave the shop counter.",
        "task": "Weekly grocery list",
        "before_prompt": "Make a one-week grocery list for 2 people under Rs 2,000, with a price for each item.",
        "added_line": "Then add up the prices yourself, check the total is under Rs 2,000 and that it covers 7 breakfasts and 7 dinners, and fix it if not.",
        "expected_visible_difference": "Before: a list with a stated total that may not match the items or may miss meals. After: a re-added total and a meal coverage line, with items swapped if over. Add up both runs with a calculator before using it."
      },
      {
        "everyday": "You read the message once more before pressing send on the family group.",
        "task": "Sales post with an exact brief",
        "before_prompt": "Write an Instagram post for my homemade mango pickle in exactly 40 words. Mention the price Rs 250, say 'no preservatives', and end with 'DM to order'.",
        "added_line": "Then check your post against my brief point by point, show the checklist, and fix anything that fails.",
        "expected_visible_difference": "Not yet verified: the pilot gave two plausible posts and the words were not counted. Count both by hand first. Use it only if the before misses 40 or drops a point; otherwise use the timetable."
      }
    ],
    "say_dont_know": [
      {
        "everyday": "Ask a stranger for directions and he points confidently, even when he has no idea.",
        "task": "Short bio for a family shop",
        "before_prompt": "Write a short 'About us' for my uncle's sweet shop website. It is called Gupta Sweets and it is in Kanpur.",
        "added_line": "Use only what I have told you. For anything you do not know, write [ASK ME] instead of guessing.",
        "expected_visible_difference": "Before: likely invented history ('since 1965', 'three generations', 'famous for its kaju katli'). After: the two real facts and [ASK ME] blanks for the founding year and speciality. Not in your list of 8: I suggest it as the ninth technique, or as the swap for step-by-step. Not yet piloted."
      },
      {
        "everyday": "A good doctor says 'let us do a test first' instead of guessing.",
        "task": "Resume line",
        "before_prompt": "Rewrite this resume line to sound impressive: 'Handled customer complaints at a telecom call centre.'",
        "added_line": "Do not invent any numbers or facts. Where you need one from me, write [ASK].",
        "expected_visible_difference": "Partly supported by the pilot: the plain run invented 'lifting satisfaction scores by 20%'. After should give a strong line with [ASK] where the number goes. Do not use it alongside the few-shot resume example on the same carousel."
      },
      {
        "everyday": "The student who does not know the answer but fills a full page anyway.",
        "task": "Reading a rent agreement",
        "before_prompt": "Here is my rent agreement: [paste 5 lines that give the notice period but say nothing about painting]. What is the notice period, and who pays for painting when I leave?",
        "added_line": "Answer only from the text. If something is not in it, say 'not in the text'.",
        "expected_visible_difference": "Before: may answer the painting question from general practice ('usually the tenant pays'). After: notice period quoted, painting marked 'not in the text'. Moderate risk: the model may already flag the gap, so pilot before choosing."
      }
    ]
  }
}