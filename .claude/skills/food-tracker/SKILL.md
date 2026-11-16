---
name: food-tracker
description: Estimate protein and calories from a meal photo with the Gym Jarvis food tracker (vision agent + USDA retrieval + matcher agent + confidence guardrail), ask the user before saving an uncertain estimate, and log corrections. Use when the user shares a meal photo or asks to log a meal, check its protein/calories, or review the tracker's monitoring.
---

# Food tracker skill

The tracker lives in `demos/food-tracker/`. Read `demos/food-tracker/RESULTS.md` once per session so
you know how accurate it is (Nutrition5k, n = 50: about 84 kcal average miss per plate; portion size is
the main error; stated ranges cover the truth only about 68% of the time).

## Log a meal

1. Run, from the repository root:
   `.venv/bin/python demos/food-tracker/estimate.py <photo> --mode table --model claude-fable-5-2 --source real`
   The pipeline: a vision agent lists items and grams (never calories) → BM25 retrieval over 13,224
   USDA FoodData Central rows → a matcher agent picks the row or rejects all → grams × table values →
   the estimate is logged with confidence and alerts.
2. Show the user the items, grams, protein and kcal, with the range.
3. **Guardrail.** If the logged record has `needs_confirmation: true` (low confidence, weak table match,
   wide range or implausible total), ask **one** question before treating the number as final. Pick the
   question that targets the biggest uncertainty: hidden food under other food, the portion of the
   heaviest item, or how it was cooked.
4. If the user's answer changes the estimate, record it:
   `cd demos/food-tracker && ../../.venv/bin/python -m monitor.correct <log_id> --kcal <n> --protein <n> --note "<answer>"`

## Review monitoring

`cd demos/food-tracker && ../../.venv/bin/python -m monitor.dashboard` renders the dashboard from the log.
Real runs and simulated history are kept apart and labelled.

## Rules

- Never present an estimate as measured. It is an estimate with a range.
- Never give nutrition or medical advice; report numbers, not recommendations.
- Photos are personal: never copy them into the repository. The log stores a SHA-256 hash, not the image.
