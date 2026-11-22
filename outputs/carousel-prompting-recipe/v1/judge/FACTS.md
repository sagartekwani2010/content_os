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
