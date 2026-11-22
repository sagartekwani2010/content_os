```json
{
  "angle": "Warm and personal: 'Your AI is a great trainer. It just doesn't know you.' Day 1 with a brilliant new trainer who met you 10 seconds ago and only knows what you tell him. Every slide is one thing you'd say to him on day 1. You brief, the trainer delivers.",
  "cover_hooks": [
    "Your AI is a great trainer. It just doesn't know you.",
    "Your AI trainer met you 10 seconds ago.",
    "Brief your AI like a new trainer."
  ],
  "keyword": "TRAINER",
  "slides": [
    {
      "n": 1,
      "kind": "cover",
      "headline": "Your AI is a great trainer.",
      "body": "It just doesn't know you. 8 things I'd tell a new trainer on day 1.",
      "technique": null,
      "gym": null,
      "copy": null,
      "before": null,
      "after": null,
      "visual": "Creator's real gym photo as a tilted polaroid on a light paper background. Hand-drawn bright marker headline above, the 'It just doesn't know you' line handwritten below the polaroid. Small tag: 'The Playbook · Part 1'. Swipe arrow bottom right."
    },
    {
      "n": 2,
      "kind": "still",
      "headline": "He only knows what you tell him.",
      "body": "AI knows every exercise but met you 10 seconds ago. You brief, the trainer delivers. 8 day-1 lines, each tested twice.",
      "technique": null,
      "gym": null,
      "copy": null,
      "before": null,
      "after": null,
      "visual": "Hand-drawn line sketch: a gym member (you) handing a small note to a trainer holding a clipboard. Below it, the layout legend used on every later slide: grey card labelled 'Lazy ask' on the left, bright card labelled 'Sharp ask' on the right, with a '+ one line' arrow between them. No quotes in the legend. Footer in small text: 'Tests: Claude Fable 5.2, every prompt run twice, 22 Nov 2026. People in the prompts are test personas, not me. Calories, protein and prices are the AI's estimates.'"
    },
    {
      "n": 3,
      "kind": "video",
      "headline": "Tell him who you are.",
      "body": "Same question, one extra line about a test persona. The answer now plans around the canteen and the 9:30 dinner.",
      "technique": "Give context",
      "gym": "Day 1 you'd say: desk job, vegetarian, dinner is always late.",
      "copy": "This is for me: [age], [job], [how you eat], [your daily timings].",
      "before": {
        "prompt": "Suggest a diet to lose weight. Under 100 words.",
        "output": "Calorie deficit: eat roughly 300–500 kcal below maintenance. Protein first: 1.6–2 g per kg of body weight (eggs, chicken, fish, paneer, dal, Greek yoghurt)…",
        "run": "g1 before · run 1"
      },
      "after": {
        "added": "This is for me: 34, bank job, sitting 9 hours, vegetarian, lunch from the office canteen, dinner at 9:30 pm with family.",
        "output": "Canteen lunch: Half plate sabzi/salad, one bowl dal or curd, 2 rotis or one small rice serving (not both)… 5 pm snack: Roasted chana, fruit, or nuts (a handful), so you aren't starving at 9:30. Dinner: Smallest meal…",
        "run": "g1 after · run 1"
      },
      "visual": "VIDEO. Frame 0: grey 'Lazy ask' card with the before prompt and output fully visible. Then the added line types in under the prompt in bright marker, and the 'Sharp ask' card writes on. Hand-drawn underline on 'Canteen lunch' and circle on '9:30'. Tag on the added line: 'test persona, not me'. Run labels in small text under each card."
    },
    {
      "n": 4,
      "kind": "still",
      "headline": "Tell him your limits.",
      "body": "Five test limits in, and the chicken bowl became a one-pot khichdi. Price and protein are the AI's estimates, not verified.",
      "technique": "Set limits (must / must not)",
      "gym": "You'd say: no eggs, tight budget, one burner. Plan inside that.",
      "copy": "Must: [your rules]. Must not: [what to avoid].",
      "before": {
        "prompt": "Suggest a high-protein dinner. Under 80 words.",
        "output": "Chicken and paneer bowl (~60 g protein)… 150 g grilled chicken breast… 1 cup cooked quinoa or brown rice…",
        "run": "g2 before · run 1"
      },
      "after": {
        "added": "Must: vegetarian, no eggs, under Rs 100, cooked on one gas burner. Must not: protein powder.",
        "output": "Soya chunk and moong dal khichdi (one pot, ~Rs 60-70)… 50 g soya chunks (~26 g protein)… Roughly 40 g protein.",
        "run": "g2 after · run 1"
      },
      "visual": "STILL. Left grey card: before prompt and output with a small hand-drawn chicken bowl. Right bright card: the added line as five ticked chips (vegetarian, no eggs, under Rs 100, one gas burner, no protein powder) and the after output with a hand-drawn pressure cooker on a single burner. Small tags on the Rs and protein figures: 'AI's estimate'. Tag: 'test limits, not my diet'."
    },
    {
      "n": 5,
      "kind": "video",
      "headline": "Tell him to ask first.",
      "body": "The first plan needed a barbell and a pull-up bar. After 3 questions and a scripted test reply, it used two dumbbells and a chair.",
      "technique": "Ask me questions first",
      "gym": "You'd say: before you plan anything, ask me what you need to know.",
      "copy": "Before you start, ask me up to 3 questions.",
      "before": {
        "prompt": "Make me a weekly workout plan. Under 100 words.",
        "output": "Mon – Push: bench press, overhead press, incline dumbbell press, triceps dips (3×8–12)… Tue – Pull: deadlifts, pull-ups, barbell rows, biceps curls (3×8–12)…",
        "run": "g6 before · run 1"
      },
      "after": {
        "added": "Before you start, ask me up to 3 questions.",
        "output": "AI asked: \"1. Goal: What are you training for… 2. Schedule: How many days a week can you train… 3. Setup and limits: Do you have a full gym, home equipment, or bodyweight only, and are there any injuries or exercises to avoid?\" | Scripted test reply: \"…build muscle; 4 days a week, 45 minutes; at home with two 10 kg dumbbells, and my left knee hurts on deep squats.\" | AI then wrote: \"4-day upper/lower split, 45 min… Box squat to a chair (pain-free depth only)… Knee: skip deep squats and lunges.\"",
        "run": "g6 after · run 1 (steps 1 and 2)"
      },
      "visual": "VIDEO. Frame 0: grey 'Lazy ask' card with the before prompt and gym-split output. Then three beats write on in the bright card: (1) the three questions, (2) a reply bubble clearly stamped 'scripted test reply, not my data', (3) the new plan lines, with a hand-drawn chair next to 'Box squat to a chair'. Underline 'pain-free depth only'."
    },
    {
      "n": 6,
      "kind": "video",
      "headline": "Tell him not to guess.",
      "body": "78 kg is a test persona. Before, the AI assumed regular training. After, it gave protein and asked for the rest.",
      "technique": "Don't guess, ask me",
      "gym": "You'd say: if you don't know my height or my routine, ask. Don't assume.",
      "copy": "Use only what I told you. Where you need something I didn't give, write [ASK ME] instead of assuming.",
      "before": {
        "prompt": "I'm 78 kg and want to lose fat. Tell me my daily calories and protein.",
        "output": "Start at about 2,000 kcal and 140 to 155 g of protein a day. This is an estimate from your weight alone, assuming you are moderately active (training 3 to 5 times a week).",
        "run": "g7 before · run 2"
      },
      "after": {
        "added": "Use only what I told you. Where you need something I didn't give, write [ASK ME] instead of assuming.",
        "output": "Protein: about 125 to 170 g per day… Calories: [ASK ME]. I can't give a number from weight alone… Maintenance: [ASK ME]. I need either of these: Your height, age, sex and activity level…",
        "run": "g7 after · run 2"
      },
      "visual": "VIDEO. Frame 0: grey card with before prompt and output, the word 'assuming' circled in marker. Then the added line types in and the bright card writes on, each [ASK ME] popping in as a bright highlighted stamp. Tags: 'test persona, not me' on 78 kg, 'AI's estimate' on the kcal and protein figures."
    },
    {
      "n": 7,
      "kind": "still",
      "headline": "Show him what you like.",
      "body": "Honest read: a moderate change. The names picked up the examples' tired-but-here humour and the time stamp. The before already had good ones.",
      "technique": "Give examples",
      "gym": "You'd say: here are two workouts I loved. More like these.",
      "copy": "I like ones like \"[example 1]\" and \"[example 2]\".",
      "before": {
        "prompt": "Suggest 5 names for our 6 am gym WhatsApp group.",
        "output": "1. Dawn Patrol… 2. 6 AM Iron Club… 3. Snooze Is Not a Rep… 4. Rise and Grind Crew… 5. First Set Before Sunrise…",
        "run": "g3 before · run 1"
      },
      "after": {
        "added": "We like names like \"Sore But Showing Up\" and \"Alarm Beaters 5:30\".",
        "output": "1. Snooze Is Not a Rep 2. Tired But Present 6:00 3. Sunrise Before Excuses 4. Half Asleep, Full Sets 5. First Light, Last Rep",
        "run": "g3 after · run 1"
      },
      "visual": "STILL. Two hand-drawn phone screens showing a WhatsApp-style group name list (drawn, no real screenshot, no names or photos). Left grey: the five before names. Right bright: the two example names pinned on top as sticky notes, the five after names below, with '6:00' circled and an arrow back to '5:30' in the example. 'Snooze Is Not a Rep' gets a small 'in both' mark on each side. Tag: 'test group, made up for the test'."
    },
    {
      "n": 8,
      "kind": "video",
      "headline": "Tell him how you want it.",
      "body": "Before: 362 words (measured). After: 5 bullets you can read between sets.",
      "technique": "Ask for the format",
      "gym": "You'd say: no lecture. Give me 5 cues I can remember under the bar.",
      "copy": "Answer in 5 bullets, in the order I do them, max 8 words each.",
      "before": {
        "prompt": "How do I deadlift with correct form?",
        "output": "Here is the conventional barbell deadlift, step by step. Setup 1. Feet: Stand hip-width apart with the bar over your midfoot, about 2-3 cm from your shins. 2. Grip: Hinge down and grip the bar just outside your legs, without moving the bar…",
        "run": "g4 before · run 1"
      },
      "after": {
        "added": "Answer in 5 bullets, in the order I do them, max 8 words each.",
        "output": "- Stand mid-foot under bar, feet hip-width apart. - Hinge down, grip bar just outside your shins. - Flatten back, brace core, pull shoulders down. - Push floor away, keeping bar against legs. - Lock hips out, then lower with control.",
        "run": "g4 after · run 1"
      },
      "visual": "VIDEO. Frame 0: grey card showing the top of the before answer with a long hand-drawn scroll trailing off the bottom of the slide, labelled '362 words'. Then the added line types in and the five bullets write on one by one beside a simple line drawing of a deadlift. PRODUCTION NOTE: show '5 bullets', not '41 words'. The 41 in FACTS appears to count the five bullet dashes; the text itself is 36 words by hand count. The 362 figure is the measured count from FACTS and was not recounted here."
    },
    {
      "n": 9,
      "kind": "video",
      "headline": "Two weeks, then check in.",
      "body": "The 12-week table can't hear about a sore shin. Two weeks at a time, with a scripted test reply, and week 3 changed.",
      "technique": "Go step by step",
      "gym": "You'd say: give me two weeks, then ask how my body took it.",
      "copy": "Give me [the first part] only. Then stop and ask me how it went.",
      "before": {
        "prompt": "Make me a 12-week plan to go from no running to a 5 km run. Under 150 words.",
        "output": "Week | Session… 1 | Run 1 min, walk 2 min × 8… 3 | Run 3 min, walk 2 min × 5… 12 | Two 20-min runs, then your 5 km",
        "run": "g5 before · run 1"
      },
      "after": {
        "added": "Give me weeks 1 and 2 only, under 80 words. Then stop and ask me how it went.",
        "output": "AI wrote weeks 1 and 2, then asked: \"How did it go? Tell me how the jogs felt and whether you had any aches…\" | Scripted test reply: \"…week 1 was fine, but my left shin hurt after the second run of week 2.\" | AI then wrote: \"Before week 3: rest until the shin is pain-free when walking and when you press on it… Week 3: repeat week 1 (8 rounds of 1 min jog + 90 sec walk), on soft, flat ground.\"",
        "run": "g5 after · run 1 (steps 1 and 2)"
      },
      "visual": "VIDEO. Frame 0: grey card with the full 12-row table drawn as a locked, already-finished sheet. Then the bright card writes on in three beats: weeks 1-2 with the AI's question, a reply bubble stamped 'scripted test reply, not my data', then the new week 3 with 'repeat week 1' underlined. PRODUCTION NOTE: in this test the after prompt also replaced 'Under 150 words.' with 'under 80 words', so show the added text exactly as quoted."
    },
    {
      "n": 10,
      "kind": "still",
      "headline": "Ask him to show the maths.",
      "body": "Before: numbers per meal. After: numbers per item, and the total matches the sum. Checkable, not more accurate. All values are the AI's estimates.",
      "technique": "Show the working",
      "gym": "You'd say: write the numbers next to each food so I can check.",
      "copy": "Show calories and protein next to each item, add them up, and tell me honestly if the total misses my targets.",
      "before": {
        "prompt": "Give me one day of vegetarian eating: 1,800 calories and 100 g protein. Under 120 words.",
        "output": "Breakfast (440 kcal, 34 g protein): 250 g non-fat Greek yogurt, 40 g oats, 100 g berries, 15 g almonds… Total: about 1,785 kcal and 110 g protein.",
        "run": "g8 before · run 1"
      },
      "after": {
        "added": "Show calories and protein next to each item, add them up, and tell me honestly if the total misses my targets.",
        "output": "Non-fat Greek yogurt, 300 g: 175 kcal, 30 g… Oats, 50 g dry: 190 kcal, 7 g… Banana: 105 kcal, 1 g… Total: 1,805 kcal, 102 g protein… This hits both targets, 5 kcal and 2 g over.",
        "run": "g8 after · run 1"
      },
      "visual": "STILL. Left grey card: one meal as a single lump with one pair of numbers. Right bright card: a hand-drawn bill-style list, one line per food with its numbers, a ruled line and the total, with a tick and 'adds up (we checked the sum)'. Optional small note on the left: 'says 110 g; its meals add to 111 g'. Tags: 'AI's estimates, not verified nutrition' and 'test prompt, not my diet'."
    },
    {
      "n": 11,
      "kind": "still",
      "headline": "Your day-1 briefing. Save this.",
      "body": "8 lines. Add the one you need to any ask.",
      "technique": null,
      "gym": null,
      "copy": null,
      "before": null,
      "after": null,
      "visual": "Hand-drawn trainer's clipboard filling the slide, 8 numbered rows from cheat_sheet: the plain technique name in bright marker, the copy line in monospace under it. Brackets in a second colour so the fill-in parts are obvious. 'Save' bookmark doodle in the corner."
    },
    {
      "n": 12,
      "kind": "cta",
      "headline": "Comment TRAINER for the full sheet.",
      "body": "I'll DM the sheet plus one combined prompt. Follow for Wednesday: the Lakshman Rekha, rules your AI can't cross. Then: how to test it.",
      "technique": null,
      "gym": null,
      "copy": null,
      "before": null,
      "after": null,
      "visual": "The word TRAINER inside a hand-drawn comment bubble, arrow to a DM envelope holding the clipboard from slide 11. Below, a three-step path: 'Today: the briefing' (ticked), 'Wed 25 Nov: Lakshman Rekha', 'Next: testing'. PRODUCTION NOTE: dm_kit/ (DM reply, short DM, cheat sheet deliverable with the combined template, image) must exist before posting."
    }
  ],
  "cheat_sheet": [
    {
      "technique": "Tell him who you are",
      "copy": "This is for me: [age], [job], [how you eat], [your daily timings]."
    },
    {
      "technique": "Tell him your limits",
      "copy": "Must: [your rules]. Must not: [what to avoid]."
    },
    {
      "technique": "Tell him to ask first",
      "copy": "Before you start, ask me up to 3 questions."
    },
    {
      "technique": "Tell him not to guess",
      "copy": "Use only what I told you. Where you need something I didn't give, write [ASK ME] instead of assuming."
    },
    {
      "technique": "Show him what you like",
      "copy": "I like ones like \"[example 1]\" and \"[example 2]\"."
    },
    {
      "technique": "Tell him how you want it",
      "copy": "Answer in 5 bullets, in the order I do them, max 8 words each."
    },
    {
      "technique": "Two weeks, then check in",
      "copy": "Give me [the first part] only. Then stop and ask me how it went."
    },
    {
      "technique": "Ask him to show the maths",
      "copy": "Show the numbers next to each item, add them up, and tell me honestly if the total misses my targets."
    }
  ],
  "caption": "Your AI is a great trainer. It just doesn't know you.\n\nThink of day 1 with a new trainer. He knows every exercise. But he met you 10 seconds ago, and he only knows what you tell him.\n\nSo I ran 8 gym and food asks two ways: a lazy ask, and the same ask with one extra line. Each one twice, on the same AI (Claude Fable 5.2), on 22 Nov.\n\nWhat changed:\n1. Who you are: the diet planned around a canteen lunch and a 9:30 dinner\n2. Your limits: a chicken bowl became a one-pot khichdi\n3. Ask me first: the plan used two dumbbells and worked around a sore knee\n4. Don't guess: it stopped assuming and wrote [ASK ME]\n5. Show what you like: names in the same tone (honestly, a moderate change)\n6. How you want it: 362 words became 5 bullets\n7. Two weeks, then check in: week 3 changed after a sore shin\n8. Show the maths: a total you can add up yourself\n\nHonest notes: the people in the prompts are test personas and the replies are scripted for the test, not my own data. Calories, protein and prices are the AI's estimates, not verified. Number 8 makes the answer checkable, not more correct.\n\nComment TRAINER and I'll DM you the full cheat sheet plus one combined prompt template.\n\nThis is part 1 of the Playbook. Wednesday: the Lakshman Rekha, rules your AI can't cross. After that: how to test it.\n\n#AItips #prompting #gymlife #fitnessindia #claude",
  "pinned_comment": "Comment TRAINER and I'll DM you the cheat sheet plus one combined prompt template. Which of the 8 lines are you adding first?"
}
```