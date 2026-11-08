# SkillRL Reel — H3-baked text workflow

## Current decision

For this production pass, every technical label is generated directly inside
H3. Do not create separate text overlays in Morphic, Magnific, CapCut or the
Codex render.

H3 must produce a finished B-roll source containing both the causal animation
and its exact technical labels. Final assembly only trims the clips and places
them above the talking head.

## Generate these five finished H3 assets

1. `01-trajectory-memory-gap.mp4`
2. `02-skillrl-paper-intro.mp4` — image-to-video using a 1920 × 1080 prepared
   source image containing the real paper title and author block; do not upload
   a long scrolling screenshot
3. `04-skill-layer.mp4`
4. `05-rl-coevolution.mp4`
5. `06-future-learning-layer.mp4`

The exact H3 prompts live under `asset-prompts/`. Do not separately paste the
old overlay directions; the current prompts already include the text, timing,
placement, spelling and negative constraints.

## Assembly

- Final canvas: 1080 × 1920, 9:16.
- H3 B-roll: top 1080 × 960 half.
- Talking head: bottom 1080 × 960 half.
- Centre-crop the H3 source; all important text and motion are constrained to
  the central 55%.
- Mute H3 audio and retain the talking-head voice.
- Do not add automatic captions over the B-roll panel.
- Use full-screen talking head for the hook, research question and CTA.

## H3 text acceptance gate

Reject and regenerate any clip when:

- one word is misspelled;
- letters morph, flicker or change between frames;
- H3 invents additional text;
- a label is clipped after the centre crop;
- a title overlaps the mechanism;
- the evidence disclosure is unreadable;
- the real paper title, authors or affiliations are altered;
- the animation is correct but the terminology is not.

Do not publish a technically incorrect label because the animation looks good.
For this Reel, text correctness is part of factual correctness.

## Retry method

When a clip fails, regenerate only that clip and change one variable:

1. shorten the failed line while preserving the concept;
2. split a long line into two lines;
3. reduce the number of simultaneously visible labels;
4. extend the stable hold;
5. simplify the underlying motion.

Do not add visual detail on a retry. Text stability improves when the scene is
simpler.
