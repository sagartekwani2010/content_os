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
   "headline": "You prompt AI like Maa writes recipes",
   "body": "“A pinch of this, cook till done.” Works for family. AI isn't family. Swipe for the 6-line fix →",
   "visual": "Creator photo in a taped hand-drawn polaroid. Beside it an old recipe-diary page: “a pinch of this, cook till done”, yellow highlighter on “a pinch of this”. Arrow from the page to a chat box with a chicken-leg and a question mark."
  },
  {
   "n": 2,
   "kind": "video",
   "headline": "The vague prompt got chicken and an oven",
   "body": "My test: dinner for 2 vegetarians, no oven. The prompt never said so. Both runs: chicken, quinoa, oven at 220°C.",
   "visual": "Frame 0: headline + sticky note “Give me a healthy dinner recipe”. 6 s calm draw-on: arrow to a typewriter output card (“Lemon-Garlic Chicken with Roasted Vegetables and Quinoa” / “Heat the oven to 220°C (425°F).”, tag “real run 1, trimmed”), then chicken and oven doodles with red circles."
  },
  {
   "n": 3,
   "kind": "still",
   "headline": "AI is a stranger in your kitchen",
   "body": "Family already knows the dish. AI has to guess. Run 2 even offered:",
   "visual": "A doorway with a small robot holding an empty plate and a question mark. Speech-bubble quote card: “If you tell me … what's in your fridge, I can tailor it.” tag “real run 2, trimmed”."
  },
  {
   "n": 4,
   "kind": "video",
   "headline": "So I wrote it a recipe card",
   "body": "Same model, same test. Six labelled lines. Each prompt run twice.",
   "visual": "Frame 0: headline + empty ruled index card. 7 s: six rows write on, label then trimmed test-prompt line (Serves / Ingredients / Method / Tastes like / Don't / Taste and adjust). Tag “test prompt, trimmed”."
  },
  {
   "n": 5,
   "kind": "still",
   "headline": "Same AI. A dinner that fits the brief.",
   "body": "No oven. Grams and minutes in the steps. One question back. The protein number is the AI's estimate.",
   "visual": "Typewriter output card: “Palak paneer moong dal (serves 2, about 25 minutes)” / “Paneer: 200 g, in 1.5 cm cubes” / “That is about 34 g per serving”, tag “real run 1, trimmed”; sticky “AI's estimate, not verified”; bowl of dal with paneer cubes; margin note “run 2: paneer-palak moong dal tadka, about 27 minutes”."
  },
  {
   "n": 6,
   "kind": "still",
   "headline": "Tell the stranger who's eating",
   "body": "Serves = who it's for. Ingredients = what you already have. Without them, it guessed chicken and an oven.",
   "visual": "Two sticky notes: “Serves” with two stick figures at a table and the line “2 people, vegetarian, about 30 g protein each”; “Ingredients” with a shelf (paneer, dal jar, spinach) and a crossed-out oven, line “… No oven.”"
  },
  {
   "n": 7,
   "kind": "video",
   "headline": "Show it what “done” looks like",
   "body": "Method = the shape of the answer. Tastes like = one example to aim at.",
   "visual": "Frame 0: headline. 6 s: numbered list 1-2-3 with “g” and “min” tags draws on (Method), a bowl with a tadka ladle labelled “dal tadka, but lighter” (Tastes like), then a quote card “Start the dal (18 minutes). Rinse the 100 g moong dal …” tag “real run 1, trimmed”."
  },
  {
   "n": 8,
   "kind": "still",
   "headline": "Maa tastes before serving. So should AI.",
   "body": "Don't = your limits. Taste and adjust = check your own work, then ask me one question.",
   "visual": "Left: “Don't” sticky with crossed-out kadhai (deep frying), cream and a clock past 30, plus “asked: under 30 min → got: about 25 minutes”. Right: tasting spoon over a pot; speech bubble “Will you eat this on its own, or with rice or roti?” tag “real run 1”."
  },
  {
   "n": 9,
   "kind": "still",
   "headline": "Save this: the six-line recipe card",
   "body": "Serves: who it's for. Ingredients: what you have. Method: answer shape. Tastes like: one example. Don't: limits. Taste and adjust: self-check, one question.",
   "visual": "One big ruled recipe card with a punched hole; six rows, label highlighted, meaning beside it, tiny icon; one filled example under Serves in grey: “e.g. 2 people, vegetarian, ~30 g protein each”. Bookmark doodle “save for your next prompt”."
  },
  {
   "n": 10,
   "kind": "cta",
   "headline": "Comment RECIPE for the template",
   "body": "I'll DM you the copyable card with one filled example. Follow the Playbook: Wednesday, Lakshman Rekha = AI guardrails.",
   "visual": "Comment bubble “RECIPE” highlighted, arrow to an envelope with a card peeking out. Path of three sticky notes: Prompting (today, ticked) → Guardrails (Wed: Lakshman Rekha) → Evals. 5 s video: the arrow and the path draw on."
  }
 ],
 "caption": "You prompt AI the way Maa writes recipes: “a pinch of this, cook till done”.\n\nThat works for family, because they have eaten the dish a hundred times. AI has never eaten at your table. It is a stranger in your kitchen.\n\nSo I tested it. Same model, same day, each prompt run twice. The test scenario: dinner for 2 vegetarians, no oven. Prompt 1 was “Give me a healthy dinner recipe”. Both times it gave lemon chicken with roasted vegetables and quinoa, oven at 220°C. That is a fair answer. It had no way to know the dinner was vegetarian, or that the test kitchen had no oven. One run even ended: “If you tell me your calorie or protein target, or what's in your fridge, I can tailor it.”\n\nPrompt 2 was a recipe card with six labelled lines. Both times it gave a palak paneer moong dal built from what the card listed, with grams and minutes in the steps, in about 25 to 27 minutes. It put the protein at about 34 g per serving. That number is the AI's own estimate, not verified nutrition. Each run ended with one question to make the dish better. This was a test prompt, not a cooked meal.\n\nThe six lines:\nServes: who it is for\nIngredients: what you have\nMethod: the shape of the answer you want\nTastes like: one example\nDon't: your limits\nTaste and adjust: ask it to check its own work and ask you one question\n\nThis is not a magic prompt. It is what you would tell any stranger cooking in your kitchen. Try the same six lines on an email or a study plan.\n\nComment RECIPE and I will DM you the copyable card with one filled example. Save this for your next prompt. This is part 1 of the Playbook. Follow for Wednesday: Lakshman Rekha, the lines your AI should not cross.\n\nWhat is the vaguest line in your family's recipe?\n\n#promptengineering #promptingtips #aiforbeginners #learnai #aitips",
 "pinned_comment": "Comment RECIPE and I'll DM you the six-line recipe card with one filled example. And tell me: what is the vaguest instruction in your family's recipe?"
}

Reply with JSON only:
{"drafts": {"<label>": {"scores": {"hook": int, "swipe": int, "clarity": int, "save": int, "share": int, "merge": int, "proof": int, "accuracy": int}, "stop": [int], "swipe_to_end": [int],
"save": [int], "strengths": [str], "fixes": [str]}}, "best": "<label>", "why": str}
`fixes` = the concrete changes (slide number + what to change) that would raise the score most.