# SkillRL Reel — final B-roll production pack

## Final recommendation

Use **one opening proof image plus five core H3 assets**:

1. one GPT-2.5 proof image showing a task completed without learning;
2. one H3 clip defining a trajectory and exposing the no-transfer problem;
3. one H3 image-to-video source reveal built from the real SkillRL paper
   capture;
4. one H3 clip for SkillRL's skill layer;
5. one H3 clip for the RL layer and SkillBank evolution;
6. one H3 clip translating the paper into a future-agent architecture rule.

This is the minimum set that explains every causal step in the final script.
The fourth H3 clip is intentionally distinct from the paper-mechanism clips:
it visualises Sagar's forward-looking design implication. Reusing or freezing
the RL clip here would not clearly show evaluation, abstraction and controlled
behaviour change.

The GPT-2.5 two-layer map is a **fallback still**, not mandatory B-roll. Use it
only if either the skill-layer or RL-layer H3 generation fails visual QA.

## Master edit map

| Spoken beat | Core asset | Source length | Use in edit | H3-baked text |
|---|---|---:|---:|---|
| “Your AI agent can complete a task perfectly…” | `00-task-complete-nothing-learned.png` | still | 1.5–2.5s | Text is baked into the GPT-2.5 still |
| “On a complex query…” through “trajectory” | `01-trajectory-memory-gap.mp4` | 12s | First 6.5s | `QUERY → ACTION → RESULT → NEXT ACTION` + `TRAJECTORY` |
| “But that is execution—not learning…” | Same clip | 12s | Last 5.5s | `PAST RUN ≠ FUTURE LEARNING` |
| “That brings us to SkillRL…” | `02-skillrl-paper-intro.mp4` | 5s | 3–5s | Text is baked into H3; genuine paper remains visible |
| “First, the skill layer…” | `04-skill-layer.mp4` | 12s | 10–12s | `SUCCESS → STRATEGY`; `FAILURE → LESSON`; then distil/retrieve labels |
| “Second, the RL layer…” through “improve together” | `05-rl-coevolution.mp4` | 15s | 13–15s | Policy update, SkillBank update and evidence disclosure |
| “The agents we build next…” | `06-future-learning-layer.mp4` | 12s | 10–12s | `EVALUATE`; `EXTRACT`; `CONTROL BEHAVIOUR CHANGES` |
| Link-in-bio CTA | No generated B-roll | — | 5–7s | Full-screen talking head; verbal CTA is sufficient for this H3-only pass |

Do not cover every spoken second with B-roll. Let Sagar remain full screen for
the hook, the research question and the CTA. B-roll should enter when it proves
a mechanism, then leave.

## Shared generation settings for every H3 clip

- Model/workflow: MiniMax H3 text-to-video; use image-to-video only for the
  real-paper source reveal.
- Aspect ratio: 16:9 landscape.
- Frame rate: 24 fps.
- Audio: silent.
- Visual language: flat 2D instructional animation on warm white.
- Camera: fixed, straight-on, no cuts or camera movement.
- Crop rule: keep every meaningful object inside the central 55% because the
  clip will be centre-cropped into the top half of a 9:16 Reel.
- Text rule: every technical label is baked into H3. Render only the exact copy
  specified in each prompt. Misspelled, morphing or invented text is an
  automatic rejection.
- Palette: charcoal outlines, electric-blue information flow, muted lime only
  for validated/selected states, amber for failure or uncertainty, restrained
  red only for blocked or invalid transitions.
- Generate at low resolution first. Upscale only the accepted motion.

## Asset 1 — trajectory and missing transfer

Before this clip, show the opening proof image generated from
[`asset-prompts/01-history-not-learning.md`](asset-prompts/01-history-not-learning.md)
for 1.5–2.5 seconds. It establishes the contradiction; this first H3 clip then
explains the trajectory mechanism behind it.

- **File:** `01-trajectory-memory-gap.mp4`
- **Length:** 12 seconds
- **Purpose:** make `query → action → result → next action` understandable,
  then show why one completed run does not automatically improve the next.
- **Prompt:**
  [`asset-prompts/h3-combined-01-trajectory-memory-gap.md`](asset-prompts/h3-combined-01-trajectory-memory-gap.md)
- **Acceptance test:** a first-time viewer can describe both the within-run
  dependency and the between-run learning gap without hearing the narration.

## Asset 2 — H3 SkillRL paper source reveal

- **File:** `02-skillrl-paper-intro.mp4`
- **Length:** 5 seconds.
- **Type:** H3 image-to-video using the genuine paper capture.
- **Source:** <https://arxiv.org/abs/2602.08234>
- **Capture instructions:** open the real arXiv paper page or PDF title page at
  high resolution. Retain the full paper title, author names and visible arXiv
  identity. Crop browser tabs, bookmarks, notifications and irrelevant page
  margins. Do not upload a scrolling screenshot. Place the cropped title and
  author block in the centre of a plain warm-white **1920 × 1080 landscape
  canvas**, then export it as PNG. Do not alter the paper title, author list or
  date. H3 requires input width ÷ height to remain between `0.4` and `2.5`;
  1920 × 1080 equals `1.78`.
- **Prompt:**
  [`asset-prompts/h3-combined-paper-intro.md`](asset-prompts/h3-combined-paper-intro.md)
- **Acceptance test:** the actual paper title and authors remain legible enough
  to establish provenance; H3 does not alter the source or garble the baked-in
  institution labels.

## Asset 3 — skill layer: distil, organise, retrieve

- **File:** `04-skill-layer.mp4`
- **Length:** 12 seconds
- **Purpose:** show successful patterns and failure lessons becoming general
  and task-specific skills, followed by runtime retrieval of only the relevant
  skill.
- **Prompt:**
  [`asset-prompts/h3-combined-02-skill-layer.md`](asset-prompts/h3-combined-02-skill-layer.md)
- **Acceptance test:** the animation looks like abstraction and retrieval, not
  an archive receiving more logs.

## Asset 4 — RL and SkillBank co-evolution

- **File:** `05-rl-coevolution.mp4`
- **Length:** 15 seconds
- **Purpose:** distinguish reward-driven policy learning from controlled
  SkillBank refinement following validation failure, then show both improving
  within the overall training system.
- **Prompt:**
  [`asset-prompts/h3-combined-03-rl-coevolution.md`](asset-prompts/h3-combined-03-rl-coevolution.md)
- **Acceptance test:** reward changes the policy first; a separate validation
  and review sequence changes exactly one skill. The clip must not imply that
  one failure freely rewrites the complete system.

## Asset 5 — future-agent controlled learning layer

- **File:** `06-future-learning-layer.mp4`
- **Length:** 12 seconds
- **Purpose:** make the final design implication explicitly forward-looking:
  future agents need a governed layer between raw experience and behaviour
  change.
- **Prompt:**
  [`asset-prompts/h3-combined-04-future-learning-layer.md`](asset-prompts/h3-combined-04-future-learning-layer.md)
- **Acceptance test:** logs cannot directly modify behaviour; a run is
  evaluated, a skill is extracted, and a control gate approves the change
  before that skill influences a future decision.

## Optional fallback still — exact two-layer map

When a horizontal crop is the problem rather than a failed mechanism, use the
finished vertical image `07-separate-learning-layer-vertical.png`. Its reusable
prompt is
[`asset-prompts/image-08-separate-learning-layer-vertical.md`](asset-prompts/image-08-separate-learning-layer-vertical.md).

- **File:** `03-skillrl-two-layer-map.png`
- **Tool:** GPT-2.5 image.
- **Purpose:** exact technical labels when H3 motion is unreliable. It may
  replace a failed mechanism clip for 3–5 seconds, but should not be inserted in
  addition to both successful mechanism clips.
- **Prompt:**
  [`asset-prompts/image-07-skillrl-two-layer-map.md`](asset-prompts/image-07-skillrl-two-layer-map.md)

## Split-screen assembly

- Final canvas: 1080 × 1920, 9:16.
- B-roll panel: top 1080 × 960.
- Talking head: bottom 1080 × 960.
- Divider: 2 px light grey.
- All labels are already baked into the H3 sources; do not add or replace text
  during assembly.
- Keep Sagar on screen during the technical mechanism. Use full-screen Sagar
  for the hook, research question and CTA.
- Disable auto-generated decorative transitions, captions and music until the
  technical edit is approved.

## Final rejection checklist

Reject and regenerate a clip if any answer is “no”:

1. Can a silent first-time viewer identify the cause-and-effect order?
2. Does only one meaningful state change at a time?
3. Do object identities remain stable across the shot?
4. Is every critical object still visible after the central crop?
5. Is every specified label spelled correctly, stable and readable?
6. Is the visual teaching rather than merely creating motion?
7. Does validation occur before any persistent skill update?
8. Is the future behaviour change governed rather than automatic?

## H3 references

- MiniMax H3 model and supported outputs:
  <https://huggingface.co/MiniMaxAI/MiniMax-H3>
- Official H3 prompt-writing guide:
  <https://huggingface.co/MiniMaxAI/MiniMax-H3/blob/main/docs/VIDEO_PROMPT_WRITING_GUIDE_base_en.md>
