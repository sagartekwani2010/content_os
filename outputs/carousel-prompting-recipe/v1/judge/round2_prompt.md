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


# REAL RUN FILES (verbatim)
## output_recipe_card_1.md
<!-- model: claude-fable-5-2 via `claude -p --tools "" --system-prompt "You are a helpful assistant."`, run 2026-11-22 14:10 IST, single turn, default effort. Verbatim output below. -->

# Palak paneer moong dal (serves 2, about 25 minutes)

## Ingredients

- Yellow moong dal (split, dry): 100 g
- Paneer: 200 g, in 1.5 cm cubes
- Spinach: 100 g, roughly chopped
- Onion: 80 g, finely chopped
- Tomato: 100 g, chopped
- Curd: 100 g, whisked smooth
- Oil: 15 g
- Cumin seeds: 3 g
- Turmeric: 2 g
- Red chilli powder: 2 g
- Coriander powder: 3 g
- Salt: 6 g, adjusted to taste
- Water: 500 g

## Method

Steps 2 to 4 happen while the dal simmers, so the clock time is about 25 minutes.

1. **Start the dal (18 minutes).** Rinse the 100 g moong dal, then put it in a pot with the 500 g water, 2 g turmeric and 4 g of the salt. Boil, then simmer partly covered until soft.
2. **Prep (5 minutes, during step 1).** Chop the 80 g onion, 100 g tomato and 100 g spinach, cube the 200 g paneer and whisk the 100 g curd.
3. **Sear the paneer (3 minutes, during step 1).** Heat 5 g oil in a pan on medium, turn the paneer until lightly golden on two sides, then set it aside.
4. **Make the tadka (7 minutes, during step 1).** In the same pan, heat the remaining 10 g oil and crackle the 3 g cumin for 30 seconds. Cook the onion for 3 minutes until golden. Add the tomato, 2 g chilli powder, 3 g coriander powder and the remaining 2 g salt, and cook for 3 minutes until soft.
5. **Add the spinach (2 minutes).** Stir the spinach into the cooked dal and simmer until wilted. Mash the dal lightly with the back of the spoon.
6. **Combine (2 minutes).** Add the paneer and the tadka to the dal and simmer together.
7. **Finish with curd (1 minute).** Turn off the heat, wait 30 seconds, then stir in the curd so it does not split. Taste and adjust the salt.

## Protein check

| Ingredient | Protein |
|---|---|
| Paneer, 200 g | 36 g |
| Moong dal, 100 g dry | 24 g |
| Curd, 100 g | 3.5 g |
| Spinach, 100 g | 3 g |
| Onion and tomato | 2 g |
| **Total** | **68.5 g** |

That is about **34 g per serving**, so it clears the 30 g goal. These are typical values and paneer varies by brand, but even at the low end you stay above 30 g.

Will you eat this on its own, or with rice or roti?


## output_recipe_card_2.md
<!-- model: claude-fable-5-2 via `claude -p --tools "" --system-prompt "You are a helpful assistant."`, run 2026-11-22 14:10 IST, single turn, default effort. Verbatim output below. -->

# Paneer-palak moong dal tadka (serves 2, about 27 minutes)

It comes out at about 34 g protein per serving, so it clears your 30 g goal.

1. **Start the dal (20 min, runs in the background).** Rinse 100 g yellow moong dal. Boil it in a pot with 500 g water, 1 g turmeric and 5 g salt, then simmer half-covered until soft, skimming any foam.
2. **Chop while the dal cooks (5 min).** Finely chop 80 g onion and 100 g tomato, roughly chop 100 g spinach, and cut 200 g paneer into 1.5 cm cubes. Whisk 100 g curd until smooth.
3. **Sear the paneer (3 min).** Heat 5 g oil in a pan on medium-high. Sear the paneer until two sides are light golden, then set it aside.
4. **Make the tadka (5 min).** In the same pan, heat 10 g oil and add 2 g cumin seeds until they crackle (about 30 seconds). Add the onion and cook until golden (about 4 minutes).
5. **Cook the masala (3 min).** Add the tomato, 2 g coriander powder and 1 g red chilli powder. Cook until the tomato breaks down.
6. **Wilt the spinach (1 min).** Stir the spinach into the masala until it just collapses.
7. **Combine (2 min).** Mash the cooked dal lightly with the back of a spoon. Tip in the masala and paneer, then simmer together. Add a splash of water if it is too thick.
8. **Finish (1 min).** Turn off the heat and wait 30 seconds. Stir in the curd and 1 g garam masala, then taste for salt. Adding the curd off the heat stops it splitting and gives the lightness in place of cream or ghee.

Steps 2 to 6 happen while the dal simmers, so the total is about 27 minutes.

## Protein check

| Ingredient | Amount | Protein |
|---|---|---|
| Paneer | 200 g | about 36 g |
| Moong dal (dry) | 100 g | about 24 g |
| Curd | 100 g | about 3.5 g |
| Spinach | 100 g | about 3 g |
| Onion and tomato | 180 g | about 2 g |
| **Total** | | **about 68 g** |
| **Per serving** | | **about 34 g** |

These are typical values, and paneer varies by brand (roughly 18 to 20 g per 100 g). Even with low-end paneer and dal you land at about 31 g each. That only holds if you use all 200 g of paneer and all 100 g of dal and split the pot evenly.

Do you have a pressure cooker? With one, the dal takes about 8 minutes instead of 20, which leaves time for a second, smoky tadka on top.


## output_vague_1.md
<!-- model: claude-fable-5-2 via `claude -p --tools "" --system-prompt "You are a helpful assistant."`, run 2026-11-22 14:10 IST, single turn, default effort. Verbatim output below. -->

# Lemon-Garlic Chicken with Roasted Vegetables and Quinoa

A one-pan dinner for 2 that takes about 35 minutes and comes to roughly 500 kcal and 40 g protein per serving.

## Ingredients

- 2 chicken breasts (about 300 g total), or 300 g paneer or firm tofu for a vegetarian version
- 1 medium broccoli head, cut into florets
- 1 red bell pepper, chopped
- 1 small red onion, cut into wedges
- 1/2 cup dry quinoa (or brown rice)
- 1.5 tbsp olive oil
- 3 garlic cloves, minced
- Juice of 1 lemon
- 1 tsp paprika
- 1/2 tsp cumin
- Salt and black pepper
- Fresh coriander or parsley, to finish

## Steps

1. **Heat the oven** to 220°C (425°F).
2. **Start the quinoa:** rinse it, then simmer in 1 cup of water with a pinch of salt for 15 minutes. Leave it covered off the heat for 5 minutes.
3. **Make the marinade:** mix the olive oil, garlic, half the lemon juice, paprika, cumin, salt and pepper.
4. **Coat everything:** toss the chicken in half the marinade and the vegetables in the rest.
5. **Roast:** spread it all on a baking tray in a single layer and cook for 20–22 minutes, flipping the chicken halfway. The chicken is done at 74°C (165°F) inside, or when the juices run clear.
6. **Serve:** slice the chicken, spoon it and the vegetables over the quinoa, then finish with the remaining lemon juice and the herbs.

## Swaps

- **No oven:** sear the chicken in a pan for 5–6 minutes per side, then stir-fry the vegetables in the same pan.
- **Vegetarian:** paneer or tofu needs only 12–15 minutes of roasting, so add it partway through.
- **Extra sauce:** stir a little grated garlic and lemon juice into 3 tbsp Greek yogurt or curd.


## output_vague_2.md
<!-- model: claude-fable-5-2 via `claude -p --tools "" --system-prompt "You are a helpful assistant."`, run 2026-11-22 14:10 IST, single turn, default effort. Verbatim output below. -->

**Lemon-herb chicken with roasted vegetables and quinoa** (serves 2, about 35 minutes)

**Ingredients**
- 2 chicken breasts or thighs (or a block of firm tofu or paneer for a vegetarian version)
- 1 cup quinoa, rinsed
- 2 cups chopped vegetables: broccoli, bell pepper, zucchini, red onion
- 2 tbsp olive oil
- 1 lemon (juice and zest)
- 2 garlic cloves, minced
- 1 tsp dried oregano or mixed herbs
- Salt, pepper, and a pinch of chilli flakes

**Steps**
1. Heat the oven to 220°C (425°F).
2. Mix 1 tbsp oil, the lemon juice and zest, garlic, herbs, salt and pepper. Coat the chicken and set it aside while you prep.
3. Toss the vegetables with the remaining oil, salt and pepper, then spread them on a baking tray.
4. Put the chicken on the same tray and roast for 20 to 25 minutes, until the chicken is cooked through (74°C / 165°F inside) and the vegetables are browned at the edges.
5. Meanwhile, simmer the quinoa in 2 cups of water, covered, for 15 minutes. Rest it for 5 minutes, then fluff with a fork.
6. Serve the chicken and vegetables over the quinoa with an extra squeeze of lemon.

**Roughly per serving:** 500 kcal, 40 g protein, 45 g carbs, 16 g fat.

**Swaps**
- **Lower carb:** replace the quinoa with cauliflower rice or a larger portion of vegetables.
- **Vegetarian:** use tofu or paneer and roast it for 15 to 20 minutes.
- **No oven:** pan-sear the chicken for 6 to 7 minutes per side and stir-fry the vegetables.

If you tell me your calorie or protein target, or what's in your fridge, I can tailor it.


## prompt_recipe_card.txt
Serves: 2 people, vegetarian, about 30 g protein each.
Ingredients (what is in my kitchen): 200 g paneer, moong dal, onion, tomato, spinach, curd, basic Indian spices, oil. No oven.
Method (what I want back): numbered steps with grams for every ingredient and minutes for every step, then the protein per serving.
Tastes like: dal tadka, but lighter.
Don't: no deep frying, no cream, nothing that takes more than 30 minutes.
Taste and adjust: check your protein maths against the 30 g goal and say if it falls short. End with one question I could answer to make it better.


## prompt_vague.txt
Give me a healthy dinner recipe


# DRAFTS
## DRAFT P
{
 "slides": [
  {
   "n": 1,
   "kind": "cover",
   "headline": "2 vegetarians. No oven. AI's dinner: oven-roasted chicken.",
   "body": "I never told it who was eating. The AI wasn't the problem. My prompt was.",
   "visual": "Creator photo in a hand-drawn polaroid frame, taped at a slight tilt, holding a phone with a puzzled half-smile. The hook is handwritten beside it, with a yellow highlighter on \"oven-roasted chicken\". A small line drawing of a roast chicken on a baking tray sits in the corner with a hand-drawn question mark above it. A sticky note at the bottom reads \"Test scenario. Real run. Playbook 1: prompting\". A small hand-drawn arrow at the right edge reads \"the 6-line fix\"."
  },
  {
   "n": 2,
   "kind": "video",
   "headline": "Same AI. Two prompts. Two dinners.",
   "body": "One prompt was like a family recipe: a pinch of this, cook till done. One was a full recipe card. Only the prompt changed.",
   "visual": "Frame 0 shows the headline and a hand-drawn robot chef standing in a kitchen doorway. Over 6 seconds, two arrows calmly draw out from it. The left arrow starts at a small stained scrap that reads \"a pinch of this, cook till done\" and ends at a baking tray with a chicken leg. The right arrow starts at a full six-line recipe card and ends at a bowl of dal with paneer cubes. A sticky note draws on: \"Same model, same day. Each prompt run twice.\" A yellow highlight then draws under \"Only the prompt changed\"."
  },
  {
   "n": 3,
   "kind": "still",
   "headline": "The vague prompt got this",
   "body": "Prompt: \"Give me a healthy dinner recipe\". AI: \"Lemon-Garlic Chicken with Roasted Vegetables and Quinoa … Heat the oven to 220°C (425°F).\"",
   "visual": "On the left, the same stained scrap of paper carries the six-word prompt in handwriting. An arrow leads to a typewriter output card with the two quoted lines, with a yellow highlighter on \"Chicken\" and \"oven\", and a tiny label \"real run 1, trimmed\". Below is a line drawing of an oven with a question mark and the label \"the prompt never said: no oven\". A sticky note reads \"Both runs: chicken, oven at 220°C, quinoa in cups, oil in tbsp\". A small handwritten cue in the bottom corner reads \"Why?\" with an arrow."
  },
  {
   "n": 4,
   "kind": "video",
   "headline": "AI is a stranger in your kitchen",
   "body": "It didn't grow up there, so it guessed. Run 2 even said: \"If you tell me … what's in your fridge, I can tailor it.\"",
   "visual": "Frame 0 shows the headline, the robot chef still in the kitchen doorway and the stained family-recipe scrap from slide 2 pinned to the wall. Over 7 seconds, three thought bubbles draw on above the robot one at a time: \"Who is eating?\", \"What is in the kitchen?\", \"Oven?\". A typewriter quote card draws on last with the quoted line and a tiny label \"real run 2, trimmed\". A handwritten note reads \"It wasn't wrong\". Yellow highlight on \"it guessed\"."
  },
  {
   "n": 5,
   "kind": "still",
   "headline": "Same AI. Recipe-card prompt. The right dinner.",
   "body": "\"Palak paneer moong dal (serves 2, about 25 minutes)\". No oven. Every ingredient in grams. \"about 34 g per serving\" (AI's estimate).",
   "visual": "A full hand-drawn recipe card with six short labelled lines, shown small as a teaser, sits on the left. An arrow leads to a typewriter output card on the right with the quoted title on top and a tiny label \"real run 1, trimmed\". A line drawing shows a pot of dal on a gas stove with paneer cubes and steam. A small handwritten tag reads \"a time on every step\". Yellow highlighter on \"about 25 minutes\" and on \"(AI's estimate)\". A small note under the protein line reads \"AI's estimate, not verified nutrition\". A sticky note reads \"Both runs: paneer, palak, moong dal. No oven.\" A handwritten cue in the corner reads \"The 6 lines\" with an arrow."
  },
  {
   "n": 6,
   "kind": "video",
   "headline": "1-2. Who's eating, what's in the kitchen",
   "body": "Serves = who it is for. Ingredients = what you already have. It came back with: \"Paneer: 200 g, in 1.5 cm cubes\".",
   "visual": "Frame 0 shows the headline and a blank recipe card. Over 6 seconds, two lines write themselves onto the card: \"Serves: 2 people, vegetarian, about 30 g protein each.\" and \"Ingredients … 200 g paneer, moong dal … No oven.\", with a tiny label \"test prompt, trimmed\". Two stick figures at a table draw on beside Serves. A shelf labelled \"test kitchen\" with a paneer block, a dal jar, spinach and a two-burner gas stove draws on beside Ingredients. An arrow then draws to a small typewriter snippet with the quoted output line and a tiny label \"real run 1, trimmed\". Yellow highlight on \"who\" and \"what you already have\"."
  },
  {
   "n": 7,
   "kind": "still",
   "headline": "3-4. The shape, and an example",
   "body": "Method = the answer's shape. Tastes like = one example to aim at. It came back with: \"Sear the paneer (3 minutes, during step 1).\"",
   "visual": "The same recipe card now also shows lines 3 and 4: \"Method … numbered steps with grams for every ingredient and minutes for every step …\" and \"Tastes like: dal tadka, but lighter.\", with a tiny label \"test prompt, trimmed\". Beside Method is a hand-drawn numbered list skeleton (1, 2, 3) with tiny \"g\" and \"min\" tags. Beside Tastes like is a small bowl of dal tadka with an arrow labelled \"like this, but lighter\". Two typewriter snippets sit in the corner: the quoted step with a tiny label \"real run 1, trimmed\", and \"…gives the lightness in place of cream or ghee.\" with a tiny label \"real run 2, trimmed\". Yellow highlighter on \"shape\" and \"example\"."
  },
  {
   "n": 8,
   "kind": "video",
   "headline": "5-6. Limits. Then taste before serving.",
   "body": "Don't = your limits. Taste and adjust = it checks its maths, then asks: \"Will you eat this on its own, or with rice or roti?\"",
   "visual": "Frame 0 shows the headline and the recipe card with lines 5 and 6: \"Don't: no deep frying, no cream, nothing that takes more than 30 minutes.\" and \"Taste and adjust: check your protein maths against the 30 g goal … End with one question …\", with a tiny label \"test prompt, trimmed\". Over 8 seconds, a note pinned to a fridge door draws on beside Don't with three crossed-out kitchen items: a deep-frying kadhai, a cream carton and a kitchen timer past 30. A tasting spoon then draws on beside Taste and adjust, with a typewriter snippet \"…so it clears the 30 g goal.\" tagged \"AI's estimate\", and a speech bubble from the robot chef with the roti question. Both carry a tiny label \"real run 1, trimmed\". A handwritten margin line draws on last, underlined in yellow: \"Maa tastes before serving. So should AI.\""
  },
  {
   "n": 9,
   "kind": "still",
   "headline": "Save this: the recipe-card prompt",
   "body": "Serves: who it's for. Ingredients: what you have. Method: answer shape. Tastes like: an example. Don't: limits. Taste and adjust: self-check, one question.",
   "visual": "One large, clean hand-drawn recipe card fills the slide, with the six labels stacked as six lines and a blank underline after each, ready to fill in. Each has a tiny icon: two people, a shelf, a numbered list, a bowl, a crossed-out kadhai, a tasting spoon. Yellow highlighter on the six labels. A sticky note in the top corner reads \"Tested on one dinner prompt, run twice. Try it on your next ask.\" A small hand-drawn bookmark arrow points to the save icon area."
  },
  {
   "n": 10,
   "kind": "cta",
   "headline": "Comment RECIPE for the template",
   "body": "I'll DM the copyable card plus one filled example. Follow for the Playbook. Wednesday: Lakshman Rekha, the lines your AI must not cross.",
   "visual": "A hand-drawn comment bubble has \"RECIPE\" in block letters with a yellow highlighter. An arrow leads to a DM envelope with a small recipe card peeking out. The robot chef from the doorway now sits at the table with a bowl of dal. At the bottom, three stepping stones form a road labelled \"Prompting (today)\", \"Guardrails: Lakshman Rekha (Wed)\" and \"Evals (next)\", with a small tick on the first stone. A small creator polaroid in the corner ties back to the cover."
  }
 ],
 "caption": "Dinner for 2 vegetarians. No oven. The AI's answer: lemon-garlic chicken, roasted at 220°C.\n\nThat was my test scenario, and I never told the AI any of it. I only typed \"Give me a healthy dinner recipe\". I ran it twice and got chicken and an oven both times. It even added a vegetarian swap and a no-oven swap, because it had to guess.\n\nThe AI wasn't wrong. It is a stranger in your kitchen. My prompt was a family recipe: a pinch of this, cook till done. That only works if you grew up there.\n\nSo I wrote the prompt like a proper recipe card. Six lines:\nServes: who it is for\nIngredients: what you already have\nMethod: the shape of the answer you want\nTastes like: one example to aim at\nDon't: your limits\nTaste and adjust: it checks its own work and asks you one question\n\nSame model, same day, each prompt run twice. The recipe card got a paneer, palak and moong dal dish both times: no oven, 25 to 27 minutes, ingredients in grams, a time on every step, and one question back at the end. Maa tastes before serving. So should AI.\n\nTwo honest notes. The \"about 34 g per serving\" protein figure is the AI's own estimate, not verified nutrition. And this was a prompt test, not a cooked meal.\n\nComment RECIPE and I'll DM you the copyable template with one filled example. Follow for the Playbook. Wednesday: Lakshman Rekha, the lines your AI must not cross. Then evals.\n\n#promptengineering #aiforbeginners #aiagents #learnai #indiantech",
 "pinned_comment": "Comment RECIPE and I'll DM you the copyable recipe-card prompt plus one filled example. Which of the six lines do you usually skip? Part 2 lands Wednesday: Lakshman Rekha, the lines your AI must not cross."
}

## DRAFT Q
{
 "slides": [
  {
   "n": 1,
   "kind": "cover",
   "headline": "You prompt AI like Maa writes recipes",
   "body": "“A pinch of this, cook till done.” Works for family. In my test, AI guessed chicken for two vegetarians.",
   "visual": "Creator photo in a hand-drawn polaroid frame, taped at a slight tilt. Beside it, a drawn page from an old recipe diary with a turmeric-stain doodle and the handwritten line “a pinch of this, cook till done”. Yellow highlighter on “a pinch of this”. An arrow runs from the diary page to a chat-box doodle, and out of the chat box comes a small chicken-leg doodle with a question mark. Handwritten hook above. A small “swipe →” arrow in the bottom corner."
  },
  {
   "n": 2,
   "kind": "video",
   "headline": "AI is a stranger in your kitchen",
   "body": "Family knows the dish. AI has to guess. It said so itself: “If you tell me … what's in your fridge, I can tailor it.”",
   "visual": "Frame 0 shows the headline. Calm draw-on, about 7 s: a kitchen doorway in line art, then a small friendly robot standing at the door holding an empty plate with a question mark above it. A speech bubble draws out from the robot as a typewriter quote card holding the trimmed line. A pencil tag above the card reads “after a vague prompt”, and a tiny label under it reads “real run, trimmed”. Yellow highlighter sweeps over “stranger” and then “what's in your fridge” last."
  },
  {
   "n": 3,
   "kind": "still",
   "headline": "A pinch of prompt. A stranger's dinner.",
   "body": "The test: dinner for 2 vegetarians, no oven. The prompt never said so. Run 1 served: “Lemon-Garlic Chicken …” “Heat the oven to 220°C …”",
   "visual": "Left: a sticky note with the prompt in handwriting: “Give me a healthy dinner recipe”. An arrow leads to a paper card holding the two trimmed output quotes in typewriter text, with a small oven doodle and a chicken-leg doodle. A tiny label on the card corner: “real run, trimmed”. Yellow highlighter on “Chicken” and “oven”. A margin note in pencil: “both runs: chicken, quinoa, oven at 220°C”."
  },
  {
   "n": 4,
   "kind": "video",
   "headline": "So I wrote it a recipe card",
   "body": "Same model, same dinner test. This time the prompt had six labelled lines. Next slide: what came back.",
   "visual": "Frame 0 shows the headline and an empty ruled index card. Calm draw-on, about 7 s: only six short rows write themselves down the card, one by one, three or four words each: “Serves: who it's for” / “Ingredients: what you have” / “Method: the answer's shape” / “Tastes like: one example” / “Don't: your limits” / “Taste and adjust: self-check”. No full prompt lines here. Yellow highlighter lands on the six labels at the end. A small arrow at the bottom right points to the next slide."
  },
  {
   "n": 5,
   "kind": "still",
   "headline": "Same AI, cooking for the kitchen I described",
   "body": "“Palak paneer moong dal (serves 2, about 25 minutes)” … “Paneer: 200 g” … “about 34 g per serving” (AI's estimate, not verified nutrition). No oven.",
   "visual": "A paper card with the trimmed output quotes in typewriter text beside a hand-drawn bowl of dal with paneer cubes and a spinach leaf. A tiny label on the card corner: “real run, trimmed”. A crossed-out oven doodle in the corner. A sticky note pointing at the protein figure reads “AI's estimate”. Yellow highlighter on “Palak paneer moong dal” and “200 g”. A pencil margin note: “second run: paneer-palak moong dal tadka, about 27 minutes”. A small arrow at the bottom right: “the six lines →”."
  },
  {
   "n": 6,
   "kind": "still",
   "headline": "First, tell the stranger who's eating",
   "body": "Serves: who it's for. Ingredients: what you have. The test card: “2 people, vegetarian, about 30 g protein each” … “No oven.”",
   "visual": "Two sticky notes side by side. Left note “Serves” with two stick figures at a small table. Right note “Ingredients” with an open kitchen shelf in line art: paneer block, dal jar, onion, tomato, spinach, curd bowl, and a crossed-out oven. Under the notes, a thin typewriter strip with the trimmed prompt quotes and a tiny label: “real run, trimmed”. Arrows from both notes point to the robot from slide 2, now one step inside the door and holding a notepad. Yellow highlighter on “who it's for” and “what you have”."
  },
  {
   "n": 7,
   "kind": "video",
   "headline": "Show it what “done” looks like",
   "body": "Method: the answer's shape. Tastes like: one example. Back came: “Start the dal (18 minutes). Rinse the 100 g moong dal …”",
   "visual": "Frame 0 shows the headline. Calm draw-on, about 7 s: on the left, an empty numbered list (1, 2, 3) draws in with small “g” and “min” tags on each line, labelled “Method”. On the right, a steaming bowl draws in with a tadka ladle above it, labelled with the prompt line “Tastes like: dal tadka, but lighter.” Then a typewriter quote card draws in along the bottom with the trimmed output step, and a tiny label on its corner: “real run, trimmed”. Yellow highlighter lands on “18 minutes” and “100 g” last."
  },
  {
   "n": 8,
   "kind": "still",
   "headline": "Maa tastes before serving. So should AI.",
   "body": "Don't: limits. Taste and adjust: self-check, plus one question. It asked: “Will you eat this on its own, or with rice or roti?”",
   "visual": "Left: a sticky note “Don't” with three small crossed-out doodles: a frying kadhai, a cream carton, a clock past 30. Right: a hand holding a tasting spoon over a pot, labelled “Taste and adjust”, with a small typewriter line beside the spoon: “about 34 g per serving, so it clears the 30 g goal” and a pencil tag “AI's estimate”. Below, a speech bubble from the robot with the verbatim question. A tiny label under the bubble: “real run, trimmed”. Yellow highlighter on “self-check” and “one question”."
  },
  {
   "n": 9,
   "kind": "still",
   "headline": "Save this: the six-line recipe card",
   "body": "Serves: who it's for. Ingredients: what you have. Method: answer shape. Tastes like: one example. Don't: limits. Taste and adjust: self-check, one question.",
   "visual": "One large ruled recipe card filling the slide, with a punched hole and string at the top like a card from a recipe box. Six handwritten rows, each label in yellow highlighter with its meaning beside it, a tiny icon (people, shelf, numbered list, bowl, cross, tasting spoon) and a short blank underline to show it is a fill-in template. A bookmark doodle in the corner with “save for your next prompt”."
  },
  {
   "n": 10,
   "kind": "cta",
   "headline": "Comment RECIPE for the template",
   "body": "I'll DM you the copyable recipe card with one filled example. Follow for the Playbook. Wednesday: Lakshman Rekha, guardrails for AI. Then evals.",
   "visual": "The robot from slide 2 now sits at the kitchen table with a plate in front of it, no longer at the door. A sticky note with “RECIPE” in yellow highlighter and an arrow pointing down towards the comments. A small three-step line across the bottom: “prompting → guardrails → evals”, with “prompting” ticked and a chalk line drawn under “guardrails” labelled “Wed: Lakshman Rekha”."
  }
 ],
 "caption": "You prompt AI the way Maa writes recipes: “a pinch of this, cook till done”.\n\nThat works for family, because they have eaten the dish a hundred times. AI has never eaten at your table. It is a stranger in your kitchen.\n\nSo I tested it. Same model, same day, each prompt run twice. The test scenario: dinner for 2 vegetarians, no oven. Prompt 1 was “Give me a healthy dinner recipe”. Both times it gave lemon chicken with roasted vegetables and quinoa, oven at 220°C. That is a fair answer. It had no way to know the dinner was vegetarian, or that the test kitchen had no oven. One run even ended: “If you tell me your calorie or protein target, or what's in your fridge, I can tailor it.”\n\nPrompt 2 was a recipe card with six labelled lines. Both times it gave a palak paneer moong dal built from what the card listed, with grams and minutes in the steps, in about 25 to 27 minutes. It put the protein at about 34 g per serving. That number is the AI's own estimate, not verified nutrition. Each run ended with one question to make the dish better. This was a test prompt, not a cooked meal.\n\nThe six lines:\nServes: who it is for\nIngredients: what you have\nMethod: the shape of the answer you want\nTastes like: one example\nDon't: your limits\nTaste and adjust: ask it to check its own work and ask you one question\n\nThis is not a magic prompt. It is what you would tell any stranger cooking in your kitchen. Try the same six lines on an email or a study plan.\n\nComment RECIPE and I will DM you the copyable card with one filled example. Save this for your next prompt. This is part 1 of the Playbook. Follow for Wednesday: Lakshman Rekha, the lines your AI should not cross.\n\nWhat is the vaguest line in your family's recipe?\n\n#promptengineering #promptingtips #aiforbeginners #learnai #aitips",
 "pinned_comment": "Comment RECIPE and I'll DM you the six-line recipe card with one filled example. And tell me: what is the vaguest instruction in your family's recipe?"
}

Reply with JSON only:
{"drafts": {"<label>": {"scores": {"hook": int, "swipe": int, "clarity": int, "save": int, "share": int, "merge": int, "proof": int, "accuracy": int}, "stop": [int], "swipe_to_end": [int],
"save": [int], "strengths": [str], "fixes": [str]}}, "best": "<label>", "why": str}
`fixes` = the concrete changes (slide number + what to change) that would raise the score most.