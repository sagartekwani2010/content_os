# SkillRL Reel — current asset prompts

## Current production format

The finished Reel is 9:16. Every generated B-roll clip is 16:9 landscape and
is centre-cropped into the top half; Sagar remains visible in the bottom half.
All important H3 motion stays inside the central 55% of the source frame.

The complete B-roll plan, generation settings, edit map and acceptance checks
are in [`BROLL_H3_PROMPTS.md`](BROLL_H3_PROMPTS.md).

## Core B-roll assets

0. [`01-history-not-learning.md`](asset-prompts/01-history-not-learning.md)
   — GPT-2.5 opening proof image: the task completes, the log is stored and the
   next run begins with unchanged behaviour.

1. [`h3-combined-01-trajectory-memory-gap.md`](asset-prompts/h3-combined-01-trajectory-memory-gap.md)
   — one trajectory plus the missing transfer to the next run.
2. [`h3-combined-02-skill-layer.md`](asset-prompts/h3-combined-02-skill-layer.md)
   — successful and failed experience becomes retrievable skills.
3. [`h3-combined-03-rl-coevolution.md`](asset-prompts/h3-combined-03-rl-coevolution.md)
   — reward updates the policy and validation evolves the SkillBank.
4. [`h3-combined-04-future-learning-layer.md`](asset-prompts/h3-combined-04-future-learning-layer.md)
   — a controlled learning layer turns validated experience into governed
   future behaviour changes.

Capture the **real SkillRL arXiv title page** and use it as the source image for
[`h3-combined-paper-intro.md`](asset-prompts/h3-combined-paper-intro.md). H3
bakes the title and affiliation labels into `02-skillrl-paper-intro.mp4`.

## Still assets

- **Generated vertical learning-layer image:**
  [`image-08-separate-learning-layer-vertical.md`](asset-prompts/image-08-separate-learning-layer-vertical.md).
  This is the preferred 9:16 still when horizontal B-roll creates framing or
  crop problems.
- **Optional GPT-2.5 fallback still:**
  [`image-07-skillrl-two-layer-map.md`](asset-prompts/image-07-skillrl-two-layer-map.md).
- **GPT-2.5 thumbnail:** the existing
  [`thumbnail.md`](asset-prompts/thumbnail.md). Its current portrait-led format
  remains suitable for the profile grid.

## Superseded prompts

The six shorter H3 prompts and older vertical GPT-2.5 scene prompts remain
under `asset-prompts/` as preserved alternatives. They are not part of the
current explanation-first horizontal split-screen production plan.
