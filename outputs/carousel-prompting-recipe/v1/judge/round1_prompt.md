You are a strict, independent judge of Instagram carousel scripts. You did not write any of these drafts
and you do not know who did. Score each draft 1-10 on each criterion (be strict: an ordinary good carousel scores 5-6).
CRITERIA:
hook = hook stop power (slide 1 alone, as it appears in a feed);
swipe = swipe-through (does each slide make the next one necessary?);
clarity = could a 15-year-old follow it?;
save = save-worthiness; share = share/send-worthiness;
merge = how well the two domains (cooking and AI prompting) are merged;
proof = the real run, used honestly and visibly;
accuracy = every quote and number matches the REAL RUN; nothing overclaims; personal claims are supported by FACTS.

Panel (Indian Instagram viewers scrolling at 10 pm, English only): 1 TCS support engineer Pune 24; 2 CA Ahmedabad 31; 3 HR exec Bengaluru 28; 4 bank RM Lucknow 35; 5 school teacher Jaipur 38; 6 BTech final-year Hyderabad 21; 7 FP&A analyst Gurgaon 25; 8 IB/equity research associate Mumbai 33; 9 Big 4 consulting analyst Bengaluru 24; 10 strategy consulting manager Mumbai 32; 11 performance marketing exec Delhi 26; 12 FMCG brand manager Mumbai 34; 13 startup backend dev Bengaluru 27; 14 ML engineer Hyderabad 30; 15 gym trainer Delhi 29 (non-tech); 16 BCom student Kolkata 20. Groups: mass 2-5,12,15,16; fin-consult-mktg 7-12; builders 1,6,13,14.
For each draft also predict, from the panel above, which persona numbers stop on slide 1, which swipe to the end, and
which save it.

# FACTS (what is true; the only allowed outputs and numbers)
# Facts for judging (round inputs)

Real run, 22 Nov 2026, model claude-fable-5-2, same plain system prompt ("You are a helpful assistant."), single turn,
each prompt run twice. Files: runs/prompt_vague.txt, runs/prompt_recipe_card.txt, runs/output_*.md.

- Vague prompt "Give me a healthy dinner recipe": run 1 "Lemon-Garlic Chicken with Roasted Vegetables and Quinoa", oven
  220°C, "roughly 500 kcal and 40 g protein per serving"; offers a paneer/tofu swap and a no-oven swap. Run 2 "Lemon-herb
  chicken with roasted vegetables and quinoa", oven 220°C, ends "If you tell me your calorie or protein target, or what's in
  your fridge, I can tailor it."
- Recipe-card prompt (six lines: Serves / Ingredients / Method / Tastes like / Don't / Taste and adjust): run 1 "Palak paneer
  moong dal (serves 2, about 25 minutes)", grams for every ingredient, minutes per step, protein table total 68.5 g,
  "about 34 g per serving", ends "Will you eat this on its own, or with rice or roti?". Run 2 "Paneer-palak moong dal tadka
  (serves 2, about 27 minutes)", "about 34 g protein per serving", ends with a pressure-cooker question.
- All protein/calorie numbers are the model's own estimates, not verified nutrition.
- The recipe-card prompt describes a TEST SCENARIO (dinner for 2 vegetarians, paneer and moong dal in the kitchen, no oven).
  It is NOT a statement about the creator's own diet: the creator is not known to be vegetarian (his food-tracker reel
  logged chicken) and owning an oven is not established. Any draft that says "I'm vegetarian" or "I have no oven" as a
  personal fact is inaccurate.
- The creator's real kitchen was not used; the run is a single-turn API-style test, not a cooked meal.


# DRAFTS
## DRAFT P
{
 "slides": [
  {
   "n": 1,
   "kind": "cover",
   "headline": "The AI isn't a bad cook.",
   "body": "A family recipe says \"a pinch of this, cook till done\". Most prompts read the same. Six lines are missing.",
   "visual": "Hand-drawn polaroid of the creator (photo) taped at a slight angle, holding a ladle. Beside it, a torn old recipe card in handwriting: \"a pinch of this, cook till done\", with six empty dashed lines under it. Handwritten hook above; yellow highlighter on \"isn't a bad cook\". Small arrow from the empty lines to a sticky note: \"6 lines missing\"."
  },
  {
   "n": 2,
   "kind": "video",
   "headline": "Same AI. Two prompts. Two dinners.",
   "body": "One model, two prompts, each run twice. One gave oven-roasted chicken and quinoa. The other gave a paneer dal from my kitchen.",
   "visual": "One line-drawn chef's hat labelled \"same AI\" at the top, two arrows going down to two plates. Left plate: chicken on a baking tray. Right plate: a bowl of dal with paneer cubes. Video (6 s, calm): frame 0 shows the headline and the chef's hat; the two arrows draw down one after the other, then each plate sketches in; yellow highlighter sweeps \"Two dinners\" at the end."
  },
  {
   "n": 3,
   "kind": "still",
   "headline": "It cooked for a stranger",
   "body": "Prompt: \"Give me a healthy dinner recipe\". AI: \"Lemon-Garlic Chicken with Roasted Vegetables and Quinoa … Heat the oven to 220°C …\"",
   "visual": "Left: a small sticky note with the one-line prompt in handwriting. Arrow to the right: a paper printout with the verbatim title \"Lemon-Garlic Chicken with Roasted Vegetables and Quinoa\" and the line \"Heat the oven to 220°C (425°F).\" Tiny label \"real run 1, trimmed\". Line drawing of an oven with a question mark over it. Yellow highlighter on \"Chicken\" and \"oven\"."
  },
  {
   "n": 4,
   "kind": "video",
   "headline": "The AI didn't fail. It guessed.",
   "body": "It couldn't know who was eating. It even said so: \"If you tell me … what's in your fridge, I can tailor it.\"",
   "visual": "A line-drawn cook facing an empty dining table with question marks on the chairs. A speech bubble holds the verbatim quote, tiny label \"real run 2, trimmed\". Below, a blank recipe card with six empty dashed lines numbered 1 to 6. Video (6 s, calm): frame 0 shows the headline and the cook; the question marks draw on one by one, then the six empty lines draw in top to bottom; highlighter on \"It guessed\"."
  },
  {
   "n": 5,
   "kind": "still",
   "headline": "Missing lines 1 and 2: who, what",
   "body": "Serves: who it's for. Ingredients: what you have. Without them, the AI guessed chicken and an oven. With them: paneer, moong dal, no oven.",
   "visual": "The recipe card from slide 4 with lines 1 and 2 now filled in handwriting, verbatim from the prompt: \"Serves: 2 people, vegetarian, about 30 g protein each.\" and \"Ingredients (what is in my kitchen): 200 g paneer, moong dal, onion, tomato, spinach, curd, basic Indian spices, oil. No oven.\" Two sticky notes with arrows: \"Serves = who is this for\" and \"Ingredients = what you already have\". Small doodles of two plates and an open fridge. Highlighter on \"Serves\" and \"Ingredients\"."
  },
  {
   "n": 6,
   "kind": "video",
   "headline": "Missing lines 3 and 4: the shape",
   "body": "Method: the shape of the answer. Tastes like: one example. Vague: \"1/2 cup dry quinoa …\". Card: \"Paneer: 200 g …\", minutes on every step.",
   "visual": "The same card with lines 3 and 4 filled, verbatim: \"Method (what I want back): numbered steps with grams for every ingredient and minutes for every step, then the protein per serving.\" and \"Tastes like: dal tadka, but lighter.\" To the right, a snippet of the real output: \"Make the tadka (7 minutes …\" beside a small kitchen scale and a clock doodle. Sticky notes: \"Method = how the answer should look\", \"Tastes like = one example\". Video (7 s, calm): frame 0 shows the headline and the card with lines 1 and 2; lines 3 and 4 write on, then the scale and clock sketch in; highlighter on \"grams\" and \"minutes\"."
  },
  {
   "n": 7,
   "kind": "still",
   "headline": "Missing lines 5 and 6: the brakes",
   "body": "Don't: your limits. Taste and adjust: self-check, then one question. It ended: \"Will you eat this on its own, or with rice or roti?\"",
   "visual": "The card now complete, lines 5 and 6 verbatim: \"Don't: no deep frying, no cream, nothing that takes more than 30 minutes.\" and \"Taste and adjust: check your protein maths against the 30 g goal and say if it falls short. End with one question I could answer to make it better.\" Three crossed-out doodles: a deep-fry pan, a cream jug, a clock past 30. A spoon doodle labelled \"taste\" with an arrow looping back to the pot. Speech bubble with the AI's closing question, verbatim. Highlighter on \"Don't\" and \"one question\"."
  },
  {
   "n": 8,
   "kind": "video",
   "headline": "Six lines in. A different dinner out.",
   "body": "\"Palak paneer moong dal (serves 2, about 25 minutes)\" … \"about 34 g per serving\" (AI's estimate, not verified nutrition). Same model.",
   "visual": "Left: the full six-line recipe card, small. Arrow to the right: a paper printout with the verbatim title, then \"Sear the paneer (3 minutes …\" and \"about 34 g per serving\". Sticky note stuck on the protein line: \"AI's estimate, not verified nutrition\". A steaming bowl of dal with paneer cubes drawn under it. Video (8 s, calm): frame 0 shows the headline and the card; the arrow draws across, the printout lines write on one at a time, the sticky note drops in, the bowl and its steam sketch last; highlighter on \"about 25 minutes\"."
  },
  {
   "n": 9,
   "kind": "still",
   "headline": "The recipe-card prompt (save this)",
   "body": "Serves: who it's for. Ingredients: what you have. Method: answer's shape. Tastes like: an example. Don't: limits. Taste and adjust: self-check plus one question.",
   "visual": "One large clean recipe card filling the slide, six labelled lines with a blank after each label for the viewer to fill: Serves / Ingredients / Method / Tastes like / Don't / Taste and adjust. Each label has a tiny doodle (plates, fridge, numbered list, spoon, crossed circle, looping arrow). Each label highlighted in yellow. Corner sticky note: \"Works for any ask, not just dinner\". Small save-bookmark doodle top right."
  },
  {
   "n": 10,
   "kind": "cta",
   "headline": "Comment RECIPE for the template",
   "body": "I'll DM the copyable recipe card with one filled example. Follow for the Playbook: guardrails on Wednesday, then evals.",
   "visual": "A hand-drawn comment bubble with \"RECIPE\" in block letters, highlighted yellow, and an arrow to a small envelope holding the recipe card. Below, a three-step path of sticky notes: \"Prompting (today)\" ticked, \"Guardrails: Wed 25 Nov\", \"Evals\". Small polaroid of the creator in the corner with a handwritten \"Follow\" and an arrow."
  }
 ],
 "caption": "The AI isn't a bad cook. Your recipe is missing lines.\n\nA family recipe says \"a pinch of this, cook till done\". It works at home because the cook already knows the kitchen. The AI doesn't know yours.\n\nI tested it. Same model, same plain setup, each prompt run twice.\n\n\"Give me a healthy dinner recipe\" gave lemon chicken with quinoa, roasted in an oven at 220°C, both times. That wasn't wrong. It had no way to know dinner was vegetarian, that there was paneer in the fridge, or that there was no oven. One run even asked me to tell it what's in my fridge.\n\nThen I wrote the prompt like a proper recipe card, six lines:\n\nServes: who it's for\nIngredients: what you have\nMethod: the shape of the answer you want\nTastes like: one example\nDon't: your limits\nTaste and adjust: make it check its own work and ask you one question\n\nBoth runs came back as a palak paneer moong dal in about 25 to 27 minutes, no oven, grams for every ingredient, minutes for every step, and one question back to me. The protein figure (about 34 g per serving) is the AI's own estimate, not verified nutrition.\n\nThis isn't a trick. Next time an answer feels generic, check which of the six lines you left out.\n\nComment RECIPE and I'll DM you the copyable card with one filled example.\n\nThis is part 1 of the Playbook. Guardrails on Wednesday, then evals. Follow so you don't miss them.\n\n#promptengineering #aiforbeginners #aitools #learnai #aiagents",
 "pinned_comment": "Comment RECIPE and I'll DM you the copyable six-line card with one filled example. Which line do you skip most: Serves, Ingredients, Method, Tastes like, Don't, or Taste and adjust?"
}

## DRAFT Q
{
 "slides": [
  {
   "n": 1,
   "kind": "cover",
   "headline": "I'm vegetarian. AI gave me oven-roasted chicken.",
   "body": "I have no oven either. The AI wasn't the problem. My prompt was.",
   "visual": "Hand-drawn polaroid of the creator in his kitchen, taped at a slight tilt, holding a phone with a puzzled half-smile. The hook is handwritten beside it, with a yellow highlighter on \"oven-roasted chicken\". A small line drawing of a roast chicken on a baking tray sits in the corner with a hand-drawn question mark above it. A sticky note at the bottom reads \"Playbook 1: prompting\"."
  },
  {
   "n": 2,
   "kind": "video",
   "headline": "Same AI. Two prompts. Two dinners.",
   "body": "Same model, each prompt run twice. Only the prompt changed. One dinner built for a stranger. One built for my kitchen.",
   "visual": "Frame 0 shows the headline and one hand-drawn robot chef in the centre. Over 6 seconds, two arrows calmly draw out from it. The left arrow comes from a tiny scrap of paper and ends at a plate with a chicken leg. The right arrow comes from a full recipe card and ends at a bowl of dal with paneer cubes. A yellow highlight then draws under \"Only the prompt changed\"."
  },
  {
   "n": 3,
   "kind": "still",
   "headline": "The vague prompt got this",
   "body": "Prompt: \"Give me a healthy dinner recipe\". AI: \"Lemon-Garlic Chicken with Roasted Vegetables and Quinoa … Heat the oven to 220°C (425°F).\"",
   "visual": "On the left, a torn chit of paper carries the six-word prompt in handwriting. An arrow leads to a hand-drawn output card with the two quoted lines, with a yellow highlighter on \"Chicken\" and \"oven\". Below is a line drawing of an oven with a red hand-drawn cross and the label \"I don't have one\". A sticky note reads \"Both runs: chicken, oven at 220°C, cups and tbsp\"."
  },
  {
   "n": 4,
   "kind": "video",
   "headline": "My prompt was a family recipe",
   "body": "\"A pinch of this, cook till done\" works only if you grew up in that kitchen. The AI didn't. It wasn't wrong. It guessed.",
   "visual": "Frame 0 shows the headline and a hand-drawn, slightly stained recipe card that reads \"a pinch of this, cook till done\". Over 7 seconds, a robot chef draws on beside it. Three thought bubbles appear one at a time: \"Who is eating?\", \"What is in the kitchen?\", \"Oven?\". A sticky note draws on last: \"It even hedged: '…or 300 g paneer or firm tofu for a vegetarian version'\". Yellow highlight on \"It guessed\"."
  },
  {
   "n": 5,
   "kind": "still",
   "headline": "Same AI. Recipe-card prompt. My dinner.",
   "body": "\"Palak paneer moong dal (serves 2, about 25 minutes)\". No oven. Grams and minutes on every step. \"about 34 g per serving\" (AI's estimate).",
   "visual": "A full hand-drawn recipe card with six short labelled lines, shown small as a teaser, sits on the left. An arrow leads to an output card on the right with the quoted title on top. A line drawing shows a pot of dal on a gas stove with paneer cubes and steam. Yellow highlighter on \"about 25 minutes\" and on \"(AI's estimate)\". A sticky note reads \"Both runs: same dish, no oven\"."
  },
  {
   "n": 6,
   "kind": "video",
   "headline": "1-2. Who's eating, what's in the kitchen",
   "body": "Serves = who it is for. Ingredients = what you already have. Mine: \"2 people, vegetarian … 200 g paneer, moong dal … No oven.\"",
   "visual": "Frame 0 shows the headline and a blank recipe card. Over 6 seconds, the lines \"Serves:\" and \"Ingredients:\" write themselves in. Two stick figures at a table draw on beside Serves. An open kitchen shelf with paneer, a dal jar, spinach and a crossed-out oven draws on beside Ingredients. An arrow then draws to a small output snippet: \"Paneer: 200 g, in 1.5 cm cubes\". Yellow highlight on \"who\" and \"what you already have\"."
  },
  {
   "n": 7,
   "kind": "still",
   "headline": "3-4. The shape, and an example",
   "body": "Method = the shape of the answer. Tastes like = one example to aim at. Mine: \"numbered steps with grams … dal tadka, but lighter.\"",
   "visual": "The recipe card now shows lines 3 and 4, \"Method:\" and \"Tastes like:\". Beside Method is a hand-drawn numbered list skeleton (1, 2, 3) with tiny \"g\" and \"min\" tags. Beside Tastes like is a small bowl of dal tadka with an arrow labelled \"like this, but lighter\". The output snippet in the corner reads \"Sear the paneer (3 minutes, during step 1).\" Yellow highlighter on \"shape\" and \"example\"."
  },
  {
   "n": 8,
   "kind": "video",
   "headline": "5-6. The limits, and a self-check",
   "body": "Don't = your limits. Taste and adjust = the AI checks its own work, then asks you one question.",
   "visual": "Frame 0 shows the headline and the recipe card with lines 5 and 6, \"Don't:\" and \"Taste and adjust:\". Over 8 seconds, a hand-drawn fence draws on beside Don't with three small signs: \"no deep frying\", \"no cream\", \"nothing that takes more than 30 minutes\". A tasting spoon then draws on beside Taste and adjust, with two output snippets: \"…so it clears the 30 g goal.\" (tagged \"AI's estimate\") and a speech bubble from the robot chef: \"Will you eat this on its own, or with rice or roti?\". Yellow highlight on \"checks its own work\"."
  },
  {
   "n": 9,
   "kind": "still",
   "headline": "Save this: the recipe-card prompt",
   "body": "Serves: who it's for. Ingredients: what you have. Method: answer shape. Tastes like: an example. Don't: limits. Taste and adjust: self-check, one question.",
   "visual": "One large, clean hand-drawn recipe card fills the slide, with the six labels stacked as six lines. Each has a tiny icon: two people, a shelf, a numbered list, a bowl, a fence, a spoon. Yellow highlighter on the six labels. A sticky note in the top corner reads \"Works for any ask, not just dinner\". A small hand-drawn bookmark arrow points to the save icon area."
  },
  {
   "n": 10,
   "kind": "cta",
   "headline": "Comment RECIPE for the template",
   "body": "I'll DM you the copyable recipe card plus one filled example. Follow for the Playbook. Wednesday: Lakshman Rekha, the lines your AI must not cross.",
   "visual": "A hand-drawn comment bubble has \"RECIPE\" in block letters with a yellow highlighter. An arrow leads to a DM envelope with a small recipe card peeking out. At the bottom, three stepping stones form a road labelled \"Prompting (today)\", \"Guardrails (Wed)\" and \"Evals\", with a small tick on the first stone. A small creator polaroid in the corner ties back to the cover."
  }
 ],
 "caption": "I'm vegetarian and I don't have an oven. I asked AI for a healthy dinner and got lemon-garlic chicken, roasted at 220°C.\n\nThe AI wasn't wrong. It had no way to know who it was cooking for. It even hedged with a vegetarian swap and a no-oven swap, because it had to guess.\n\nMy prompt was a family recipe: \"a pinch of this, cook till done.\" That only works if you grew up in that kitchen.\n\nSo I wrote the prompt like a proper recipe card. Six lines:\nServes: who it is for\nIngredients: what you already have\nMethod: the shape of the answer you want\nTastes like: one example to aim at\nDon't: your limits\nTaste and adjust: make it check its own work and ask you one question\n\nSame model, same day, each prompt run twice. The recipe card gave me palak paneer moong dal both times: no oven, grams for every ingredient, minutes for every step, and one question back to me at the end.\n\nOne honest note: the \"about 34 g per serving\" protein figure is the AI's own estimate, not verified nutrition.\n\nThis is not a magic prompt. It is one principle: the AI can only cook for the person you describe.\n\nComment RECIPE and I'll DM you the copyable template with one filled example.\n\nThis is part 1 of the Playbook. Wednesday: Lakshman Rekha, the lines your AI must not cross. Then evals.\n\n#promptengineering #aiforbeginners #aiagents #learnai #indiantech",
 "pinned_comment": "Comment RECIPE and I'll DM you the copyable recipe-card prompt plus one filled example. Which of the six lines do you usually skip? Mine was \"Don't\". Part 2 lands Wednesday: Lakshman Rekha, the lines your AI must not cross."
}

## DRAFT R
{
 "slides": [
  {
   "n": 1,
   "kind": "cover",
   "headline": "You prompt AI like Maa writes recipes",
   "body": "“A pinch of this, cook till done.” Works for family. Not for AI.",
   "visual": "Hand-drawn polaroid of the creator, taped at a slight tilt. Beside it, a drawn page from an old recipe diary with a turmeric-stain doodle and the handwritten line “a pinch of this, cook till done”. Yellow highlighter on “a pinch of this”. Handwritten hook above; a small arrow points from the diary page to a chat-box doodle."
  },
  {
   "n": 2,
   "kind": "video",
   "headline": "AI is a stranger in your kitchen",
   "body": "Family already knows the dish. AI has never eaten at your table. Same model, two prompts, two very different dinners.",
   "visual": "Frame 0 shows the headline. Calm draw-on, about 6 s: a kitchen doorway in line art, then a small friendly robot standing at the door holding an empty plate with a question mark above it. Two arrows then draw out from the robot to two covered plates labelled “prompt 1” and “prompt 2”. Yellow highlighter sweeps over “stranger” last."
  },
  {
   "n": 3,
   "kind": "still",
   "headline": "A pinch of prompt. A stranger's dinner.",
   "body": "Asked: “Give me a healthy dinner recipe”. Got: “Lemon-Garlic Chicken … Heat the oven to 220°C …” Not wrong. Nobody told it: vegetarian, no oven.",
   "visual": "Left: a sticky note with the prompt in handwriting. An arrow leads to a paper card holding the trimmed output quote in typewriter text, with a small oven doodle and a chicken-leg doodle. Yellow highlighter on “Chicken” and “oven”. A margin note in pencil: “same result both times I ran it”."
  },
  {
   "n": 4,
   "kind": "video",
   "headline": "So I wrote it a recipe card",
   "body": "Same model. Same dinner question. This time, six labelled lines: Serves, Ingredients, Method, Tastes like, Don't, Taste and adjust.",
   "visual": "Frame 0 shows the headline and an empty ruled index card. Calm draw-on, about 8 s: the six labels write themselves one by one down the card, each followed by a trimmed line of the real prompt: “Serves: 2 people, vegetarian, about 30 g protein each.” / “Ingredients … 200 g paneer, moong dal, onion, tomato, spinach, curd … No oven.” / “Method … numbered steps with grams for every ingredient and minutes for every step …” / “Tastes like: dal tadka, but lighter.” / “Don't: no deep frying, no cream …” / “Taste and adjust: check your protein maths against the 30 g goal …”. Yellow highlighter lands on the six labels at the end."
  },
  {
   "n": 5,
   "kind": "still",
   "headline": "Same AI. Now it's my kitchen.",
   "body": "“Palak paneer moong dal (serves 2, about 25 minutes)” … “Paneer: 200 g” … “about 34 g per serving” (AI's estimate, not verified nutrition).",
   "visual": "A paper card with the trimmed output quotes in typewriter text beside a hand-drawn bowl of dal with paneer cubes and a spinach leaf. A crossed-out oven doodle in the corner. A sticky note pointing at the protein figure reads “AI's estimate”. Yellow highlighter on “Palak paneer moong dal” and “200 g”. A pencil margin note: “second run: same dish”."
  },
  {
   "n": 6,
   "kind": "still",
   "headline": "First, tell the stranger who's eating",
   "body": "Serves = who it's for. Ingredients = what you have. Mine: “2 people, vegetarian, about 30 g protein each” … “No oven.”",
   "visual": "Two sticky notes side by side. Left note “Serves” with two stick figures at a small table. Right note “Ingredients” with an open kitchen shelf in line art: paneer block, dal jar, onion, tomato, spinach, curd bowl. Arrows from both notes point to the robot from slide 2, now holding a notepad. Yellow highlighter on “who it's for” and “what you have”."
  },
  {
   "n": 7,
   "kind": "video",
   "headline": "Show it what “done” looks like",
   "body": "Method = the shape of the answer. Tastes like = one example. Mine: “Tastes like: dal tadka, but lighter.”",
   "visual": "Frame 0 shows the headline. Calm draw-on, about 6 s: on the left, an empty numbered list (1, 2, 3) draws in with small “g” and “min” tags on each line, labelled “Method”. On the right, a steaming bowl draws in with a tadka ladle above it, labelled “Tastes like”. A dotted arrow connects the bowl to the list. Yellow highlighter on “shape” and “one example”."
  },
  {
   "n": 8,
   "kind": "still",
   "headline": "Maa tastes before serving. So should AI.",
   "body": "Don't = limits. Taste and adjust = self-check, plus one question. It asked: “Will you eat this on its own, or with rice or roti?”",
   "visual": "Left: a sticky note “Don't” with three small crossed-out doodles: a frying kadhai, a cream carton, a clock past 30. Right: a hand holding a tasting spoon over a pot, labelled “Taste and adjust”. Below, a speech bubble from the robot with the verbatim question. Yellow highlighter on “self-check” and “one question”."
  },
  {
   "n": 9,
   "kind": "still",
   "headline": "Save this: the recipe-card prompt",
   "body": "Serves: who it's for. Ingredients: what you have. Method: answer shape. Tastes like: an example. Don't: limits. Taste and adjust: self-check + one question.",
   "visual": "One large ruled recipe card filling the slide, with a punched hole and string at the top like a card from a recipe box. Six handwritten rows, each label in yellow highlighter with its meaning beside it and a tiny icon (people, shelf, numbered list, bowl, cross, tasting spoon). A small bookmark doodle in the corner with “save”."
  },
  {
   "n": 10,
   "kind": "cta",
   "headline": "Comment RECIPE for the template",
   "body": "I'll DM you the copyable recipe card with one filled example. Follow for the Playbook. Wednesday: Lakshman Rekha, guardrails for AI.",
   "visual": "The robot from slide 2 now sits at the kitchen table with a plate in front of it, no longer at the door. A sticky note with “RECIPE” in yellow highlighter and an arrow pointing down towards the comments. A small three-step line across the bottom: “prompting → guardrails → evals”, with “prompting” ticked."
  }
 ],
 "caption": "Maa's recipe says “a pinch of this, cook till done”. It works, because everyone reading it has eaten that dish a hundred times.\n\nAI has never eaten at your table. It is a stranger in your kitchen.\n\nSo I tested it. Same model, same day, each prompt run twice.\n\nPrompt 1: “Give me a healthy dinner recipe”. Both times it gave me lemon chicken with quinoa, roasted in an oven at 220°C. That is a fair answer. It had no way to know the dinner was vegetarian, or that there is no oven.\n\nPrompt 2: a recipe card with six labelled lines. Both times it gave me a palak paneer moong dal from what was already in the kitchen, with grams for every ingredient and minutes for every step. It put the protein at about 34 g per serving. That number is the AI's own estimate, not verified nutrition. Then it ended with one question to make the dish better.\n\nThe six lines:\nServes: who it is for\nIngredients: what you have\nMethod: the shape of the answer you want\nTastes like: one example\nDon't: your limits\nTaste and adjust: ask it to check its own work and ask you one question\n\nThis is not a magic prompt. It is just what you would tell any stranger cooking in your kitchen. It works the same for an email, a study plan or a piece of code.\n\nComment RECIPE and I will DM you the copyable card with one filled example.\n\nThis is part 1 of the Playbook. Wednesday: Lakshman Rekha, the lines your AI should not cross.\n\nWhat is the vaguest line in your family's recipe?",
 "pinned_comment": "Comment RECIPE and I'll DM you the six-line recipe card with one filled example. And tell me the vaguest instruction in your family's recipe. Ours is “cook till done”."
}

Reply with JSON only:
{"drafts": {"<label>": {"scores": {"hook": int, "swipe": int, "clarity": int, "save": int, "share": int, "merge": int, "proof": int, "accuracy": int}, "stop": [int], "swipe_to_end": [int],
"save": [int], "strengths": [str], "fixes": [str]}}, "best": "<label>", "why": str}
`fixes` = the concrete changes (slide number + what to change) that would raise the score most.