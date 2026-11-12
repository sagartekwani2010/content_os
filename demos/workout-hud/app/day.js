// Data for the Workout HUD. Replace values here to load real days.
// placeholder:true means every value below is a stand-in and must not be filmed.
window.HUD = {
  placeholder: true,
  analysedBy: null, // set to "Claude Fable 5.2" once real photos and footage are analysed
  targets: { protein_g: 140, kcal: 2300, weight_kg: 78.0 },

  // Weekly score per body part, computed in the page:
  // 50 x sets done / planned + 30 x progress (0 to 1 vs last week) + 20 x (1 - form flags / 3).
  // history = the same score for the three previous weeks, oldest first.
  week: {
    label: "Week 46",
    parts: [
      { key: "shoulders", name: "Shoulders", done: 9,  planned: 10, progress: 0.6, flags: 0, history: [74, 78, 80] },
      { key: "chest",     name: "Chest",     done: 12, planned: 12, progress: 0.8, flags: 0, history: [85, 88, 90] },
      { key: "back",      name: "Back",      done: 10, planned: 14, progress: 0.5, flags: 1, history: [70, 66, 68] },
      { key: "arms",      name: "Arms",      done: 12, planned: 12, progress: 1.0, flags: 0, history: [90, 94, 96] },
      { key: "core",      name: "Core",      done: 4,  planned: 8,  progress: 0.3, flags: 0, history: [58, 60, 62] },
      { key: "legs",      name: "Legs",      done: 11, planned: 12, progress: 0.4, flags: 2, history: [72, 70, 69] }
    ]
  },

  days: {
    /* ------------------------------------------------ YESTERDAY */
    yesterday: {
      label: "Yesterday", date: "Wed 11 Nov", weight_kg: 78.2,
      meals: [
        { key: "bf", name: "Breakfast", time: "08:10", img: null, items: [
          { label: "Oats bowl",  box: [10, 27, 44, 31], grams: [220, 260], protein: [10, 12], kcal: [300, 350], tint: "#C9B48A" },
          { label: "Milk",       box: [60, 25, 26, 21], grams: [200, 240], protein: [8, 9],   kcal: [120, 150], tint: "#F1F3EE" },
          { label: "Whey shake", box: [52, 53, 34, 24], grams: [280, 320], protein: [22, 25], kcal: [120, 140], tint: "#B98B6A" } ] },
        { key: "lu", name: "Lunch", time: "13:20", img: null, items: [
          { label: "Rice",          box: [10, 52, 34, 24], grams: [180, 220], protein: [4, 6],   kcal: [250, 310], tint: "#E3E9EC" },
          { label: "Rajma",         box: [54, 25, 30, 21], grams: [160, 200], protein: [12, 16], kcal: [220, 280], tint: "#8C3B2A" },
          { label: "Chicken tikka", box: [12, 25, 34, 21], grams: [140, 170], protein: [34, 40], kcal: [260, 320], tint: "#C4672F" },
          { label: "Salad",         box: [52, 53, 34, 22], grams: [80, 120],  protein: [1, 2],   kcal: [30, 50],   tint: "#6FA65B" } ] },
        { key: "di", name: "Dinner", time: "20:40", img: null, items: [
          { label: "Paneer bhurji", box: [12, 25, 34, 22], grams: [150, 190], protein: [26, 32], kcal: [320, 400], tint: "#D8A23C" },
          { label: "Roti x2",       box: [52, 52, 36, 25], grams: [60, 80],   protein: [5, 7],   kcal: [170, 200], tint: "#C99A62" },
          { label: "Dal",           box: [56, 25, 28, 20], grams: [150, 200], protein: [8, 12],  kcal: [170, 230], tint: "#D9A93F" },
          { label: "Curd",          box: [14, 55, 26, 18], grams: [80, 120],  protein: [3, 4],   kcal: [70, 90],   tint: "#F4F6F2" } ] }
      ],
      nudge: { ok: true, title: "On target", text: "Protein and calories both landed inside my targets. No fix needed.", basis: "day totals vs targets" },
      set: {
        lift: "Back squat", load_kg: 65, prev_load_kg: 62.5, video: null, pose: null, baseline: 39,
        reps: [ { knee_min: 84, lean_max: 38 }, { knee_min: 83, lean_max: 39 }, { knee_min: 84, lean_max: 39 },
                { knee_min: 84, lean_max: 40 }, { knee_min: 85, lean_max: 39 }, { knee_min: 85, lean_max: 40 } ],
        observation: null,
        posture: { ok: true, label: "Correct", basis: "Torso lean stayed within 2° across all 6 reps" },
        next: { kind: "up", label: "Increase to 70 kg", basis: "65 kg moved cleanly for 3 x 6" }
      },
      decisions: {
        set: { label: "Set", routes: ["PROGRESS", "HOLD", "ASK_FOR_DATA", "ESCALATE"], pick: "PROGRESS",
          observe: [ { short: "Load: 65 kg, 3 x 6 done", ref: "set.load_kg" }, { short: "Lean steady at 38° to 40°", ref: "set.reps" }, { short: "Depth held on every rep", ref: "set.reps" } ],
          propose: "Increase squat to 70 kg next session.", gate: "No change is applied until Sagar approves.",
          reason: "R1 every rep matched the baseline, so the load can move up one step." },
        meal: { label: "Meals", routes: ["ADD", "SWAP", "REDUCE", "KEEP"], pick: "KEEP",
          observe: [ { short: "Protein: about 149 g of 140 g", ref: "meals" }, { short: "Calories: about 2,275 of 2,300", ref: "meals" }, { short: "All planned items seen", ref: "plan check" } ],
          propose: "Keep the same meal plan.", gate: "No change is applied until Sagar approves.",
          reason: "R2 both totals are inside the 5% band around target." }
      },
      plan: {
        title: "Today's plan, approved yesterday", status: "approved", approved_at: "21:40",
        workout: { name: "Legs", rows: [
          { ex: "Back squat", last: "65 kg · 3 x 6",   next: "70 kg · 3 x 6",   tag: "PROGRESS", reason: "R1" },
          { ex: "Leg press",  last: "140 kg · 3 x 10", next: "140 kg · 3 x 10", tag: "HOLD" },
          { ex: "Leg curl",   last: "40 kg · 3 x 12",  next: "42.5 kg · 3 x 12", tag: "PROGRESS" } ] },
        meals: [ { slot: "Breakfast", before: "Eggs, toast, banana", after: "Eggs, toast, banana" },
                 { slot: "Lunch",     before: "Dal, rice, paneer, 2 roti", after: "Dal, rice, paneer, 2 roti" },
                 { slot: "Dinner",    before: "Chicken curry, 3 roti, salad", after: "Chicken curry, 3 roti, salad" } ],
        kcal: { from: 2300, to: 2300, reason: "Weight within range. No change." }
      }
    },

    /* ------------------------------------------------ TODAY */
    today: {
      label: "Today", date: "Thu 12 Nov", weight_kg: 78.3,
      meals: [
        { key: "bf", name: "Breakfast", time: "08:05", img: null, items: [
          { label: "Eggs x3",  box: [12, 27, 40, 27], grams: [150, 170], protein: [18, 20], kcal: [230, 260], tint: "#F0D879" },
          { label: "Toast x2", box: [54, 31, 34, 24], grams: [60, 70],   protein: [5, 6],   kcal: [180, 210], tint: "#C89A5C" },
          { label: "Banana",   box: [28, 58, 44, 18], grams: [110, 130], protein: [1, 2],   kcal: [110, 130], tint: "#E9D15A" } ] },
        { key: "lu", name: "Lunch", time: "13:10", img: null, items: [
          { label: "Rice",         box: [10, 51, 34, 24], grams: [180, 220], protein: [4, 6],   kcal: [250, 310], tint: "#E3E9EC" },
          { label: "Dal",          box: [56, 25, 28, 20], grams: [150, 200], protein: [8, 12],  kcal: [170, 230], tint: "#D9A93F" },
          { label: "Paneer sabzi", box: [14, 25, 30, 20], grams: [100, 140], protein: [12, 18], kcal: [240, 320], tint: "#A44E2C" },
          { label: "Roti x2",      box: [52, 54, 36, 24], grams: [60, 80],   protein: [5, 7],   kcal: [170, 200], tint: "#C99A62" },
          { label: "Curd",         box: [41, 38, 16, 11], grams: [80, 120],  protein: [3, 4],   kcal: [70, 90],   tint: "#F4F6F2" } ] },
        { key: "di", name: "Dinner", time: "20:30", img: null, items: [
          { label: "Chicken curry", box: [10, 27, 40, 25], grams: [170, 210], protein: [30, 38], kcal: [400, 480], tint: "#B5542B" },
          { label: "Roti x3",       box: [50, 49, 40, 28], grams: [90, 120],  protein: [8, 10],  kcal: [340, 420], tint: "#C99A62" },
          { label: "Salad",         box: [58, 25, 28, 18], grams: [80, 120],  protein: [1, 2],   kcal: [40, 60],   tint: "#6FA65B" } ] }
      ],
      nudge: { ok: false, title: "Small fix", text: "Swap 1 roti at dinner for a protein bar. About +20 g protein, calories stay about level.", basis: "protein about 30 g short while calories are already over target" },
      set: {
        lift: "Back squat", load_kg: 70, prev_load_kg: 65, video: null, pose: null, baseline: 39,
        reps: [ { knee_min: 84, lean_max: 39 }, { knee_min: 83, lean_max: 38 }, { knee_min: 84, lean_max: 40 },
                { knee_min: 85, lean_max: 39 }, { knee_min: 86, lean_max: 48 }, { knee_min: 88, lean_max: 49 } ],
        observation: { rep: 5, baseline: 39 },
        posture: { ok: false, label: "Needs improvement", basis: "Torso lean rose from 39° to 48° from rep 5" },
        next: { kind: "hold", label: "Hold at 70 kg", basis: "Up from 65 kg yesterday. Form slipped late in the set." }
      },
      decisions: {
        set: { label: "Set", routes: ["PROGRESS", "HOLD", "ASK_FOR_DATA", "ESCALATE"], pick: "HOLD",
          observe: [ { short: "Load: 70 kg, up from 65 kg", ref: "set.load_kg" }, { short: "Lean 39° to 48° on rep 5", ref: "set.reps[4]" }, { short: "Depth held on all 6 reps", ref: "set.reps" } ],
          propose: "Hold squat at 70 kg next leg day. Posture: needs improvement.", gate: "No change is applied until Sagar approves.",
          reason: "R1 form changed late in the set at the new load, so the load does not move up." },
        meal: { label: "Meals", routes: ["ADD", "SWAP", "REDUCE", "KEEP"], pick: "SWAP",
          observe: [ { short: "Protein: about 110 g of 140 g", ref: "meals" }, { short: "Calories: about 2,455 of 2,300", ref: "meals" }, { short: "Dinner: 3 roti seen", ref: "meals[2].items" } ],
          propose: "Swap 1 roti at dinner for a protein bar: about +20 g protein, calories about level.", gate: "No change is applied until Sagar approves.",
          reason: "R2 protein is short while calories are already over, so adding food alone would overshoot." },
        part: { label: "Body part", routes: ["ADD_VOLUME", "KEEP", "REDUCE", "ASK_FOR_DATA"], pick: "ADD_VOLUME",
          observe: [ { short: "Core: 4 of 8 sets done", ref: "week.parts.core" }, { short: "Core score 54, down 8", ref: "week.parts.core" }, { short: "No form flags on core", ref: "week.parts.core" } ],
          propose: "Add 2 plank sets to tomorrow's session.", gate: "No change is applied until Sagar approves.",
          reason: "R3 lowest score this week, caused by missed sets, not by form." },
        weight: { label: "Weight", routes: ["REDUCE", "KEEP", "INCREASE", "ASK_FOR_DATA"], pick: "REDUCE",
          observe: [ { short: "Weight 78.3 kg, target 78.0", ref: "weight_kg" }, { short: "7-day average: 300 g over", ref: "weight log" }, { short: "Calories over target today", ref: "meals" } ],
          propose: "Lower tomorrow's calories from 2,300 to 2,150 by cutting carbs: less rice, one roti fewer.", gate: "No change is applied until Sagar approves.",
          reason: "R4 a small, steady overage, so a small carb cut and no change to protein." }
      },
      plan: {
        title: "Tomorrow, proposed", status: "pending",
        workout: { name: "Pull + core", rows: [
          { ex: "Barbell row",  last: "60 kg · 3 x 8",  next: "62.5 kg · 3 x 8", tag: "PROGRESS" },
          { ex: "Lat pulldown", last: "55 kg · 3 x 10", next: "55 kg · 3 x 10",  tag: "HOLD" },
          { ex: "Plank",        last: "2 sets",          next: "4 sets",           tag: "ADD", reason: "R3" },
          { ex: "Squat, next leg day", last: "70 kg · 3 x 6", next: "70 kg · 3 x 6", tag: "HOLD", reason: "R1" } ] },
        meals: [ { slot: "Breakfast", before: "Eggs, toast, banana", after: "Eggs, toast, banana" },
                 { slot: "Lunch",     before: "Dal, rice 1 cup, paneer, 2 roti", after: "Dal, rice 3/4 cup, paneer, 2 roti", reason: "R4" },
                 { slot: "Dinner",    before: "Chicken curry, 3 roti, salad", after: "Chicken curry, 2 roti, salad + protein bar", reason: "R2 R4" } ],
        kcal: { from: 2300, to: 2150, reason: "Weight 300 g over target on the 7-day average. Fewer carbs, same protein." }
      }
    }
  },

  ledger: { checked: 0, errors: [] }
};
