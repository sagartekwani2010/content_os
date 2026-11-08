# Reel story golden set

This is the regression suite for the Reel Story Judge. Add a real script or
edited final Reel whenever human feedback exposes a storytelling failure. A
prompt/model change must be reviewed against these cases before it becomes the
new default.

## Case 1 — repeat the comparison (reject)

**Failure pattern:** The script says “ChatGPT writes, Jev decides” in the hook,
then repeats the same contrast as its central explanation without adding
training, runtime, evidence, or a change in the viewer's understanding.

**Expected verdict:** `REWRITE`

**Required diagnosis:** Flag the repeated comparison, name the redundant scene,
and require a new story layer or removal.

## Case 2 — implication before mechanism (reject)

**Failure pattern:** A technical Reel opens with broad claims about what a new
model will change before explaining its input, output contract, or runtime role.

**Expected verdict:** `REWRITE`

**Required diagnosis:** Require a concrete mechanism/proof before implications.

## Case 3 — decorative visual (reject)

**Failure pattern:** The visual direction says “futuristic AI animation” or
“cinematic dashboard” but does not show evidence, state, a decision, a tool
result, or a real outcome.

**Expected verdict:** `REWRITE`

**Required diagnosis:** Require a visual proof, not an aesthetic replacement.

## Case 4 — earned technical deep-dive (approve)

**Required shape:** Specific hook → architecture contract → training objective
→ runtime flow → limitation → one unresolved future benchmark.

**Expected verdict:** `PASS`

## Case 5 — asset prompt is not production-ready (reject)

**Failure pattern:** “Generate a stylish shopping agent UI” with no source
material, composition, proof, motion, duration, final copy, or exclusions.

**Expected verdict:** deterministic asset-preflight failure.

## How to add a case

Include: the brief, the generated script, the human edit or rejection, and one
sentence explaining what the validator should have caught. Do not add generic
preferences; add observed failures.

## Case 6 — Diwali final edit missed approved spoken cues (reject)

**Evidence:** `feedback/diwali-reel-edit-retrospective-2026-11-08.md` and the
final source cut map named there. The early cut lost the exact salary hook,
omitted or reordered the case and level beats, and timed graphics away from
their spoken cues. A budget card introduced an unspoken fact.

**Expected verdict:** `REWRITE` for the content or visual plan; final export
must fail handoff until the rendered captions, mix and codec are verified.

**Required diagnosis:** Identify the missing source line and timecode, restore
the complete argument order before shortening, align each graphic to the
spoken line, remove the unsupported card, and inspect the final file.
