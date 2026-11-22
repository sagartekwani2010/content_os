# Brief · carousel-prompting-recipe · "Prompt like a family recipe"

- **Slot:** Mon 23 Nov 2026, 13:00 IST (calendar item 2, `planning/content-calendar-2026-11-22.md`). Format tested: static Playbook carousel (with short video slides).
- **Domains:** AI prompting × home cooking (a family recipe: "a pinch of this, cook till done").
- **Takeaway a viewer saves for:** the recipe-card prompt — six labelled lines (Serves, Ingredients, Method, Tastes like, Don't, Taste and adjust) that turn a vague ask into a specific answer.
- **Theme:** creator. **Points:** proposed by the orchestrator, refined here; the creator can correct them at the final gate.

## Points → slides (proposal; final order set by the judged script)
1. Hook: a family recipe says "a pinch of this, cook till done" — that is how most people prompt AI. (creator photo cover)
2. Stake: same model, two prompts, two very different dinners.
3. Real run, vague: "Give me a healthy dinner recipe" → what came back (verbatim, trimmed).
4. Real run, recipe card: the six-line prompt → what came back (verbatim, trimmed).
5-7. Mapping, one idea per slide where it earns it: Serves = who it is for; Ingredients = what you have (context); Method = the shape of the answer; Tastes like = an example; Don't = limits; Taste and adjust = make it check itself and ask one question.
8. Recap: the recipe-card prompt template (the save).
9. CTA: comment RECIPE → DM with the copyable template; follow for the Playbook series (prompting → guardrails on Wed 25 → evals).

## Real run (done 22 Nov, `runs/`)
Same model (claude-fable-5-2), same plain system prompt, single turn, each prompt run twice.
- Vague prompt → both runs: lemon chicken + quinoa, roasted in an oven at 220 °C, cups/tbsp, "roughly 500 kcal, 40 g protein".
- Recipe-card prompt → both runs: palak paneer moong dal, ~25-27 min, no oven, grams for every ingredient, minutes per step, protein table "about 34 g per serving" (the model's estimate, not verified nutrition), ends with one question.
- Honest framing: the vague prompt was not "wrong" for the model — it had no way to know the viewer is vegetarian with no oven. That is the point.

## Keyword
RECIPE → DM: the copyable recipe-card prompt template (text) + one filled example. `dm_kit/` built before posting.

## Calendar rules check
Two domains: yes (cooking × prompting). Real run: yes, verbatim in `runs/`. No "me too": the recipe-card mapping with a self-check line is our own framing, proven on a real side-by-side. English only. No screenshots of other people.
