# Video learning loop

Run this after every generated video candidate and every final export. The
review is part of production, not a claim that a video is approved or
published. Save each record as a new dated file in `feedback/`; preserve older
reviews and rejected variants.

## Capture the result

Record the brief/output ID, source footage or generation ID, approved hook,
tool, model, prompt version, keyframe paths, credit estimate, actual charge,
and artifact path or URL. Compare the artifact with its brief, actual spoken
lines and intended visual cue. At final export record the take map, captions,
mix, full-decode result and codec/container check. Keep credentials, signed
upload URLs and private booking details out of the repo.

## Turn feedback into a change

For every creator correction, record **before → after → why → evidence** using
`POST_REVIEW_TEMPLATE.md`. Tag the affected hook, story beat, visual, factual
claim, edit or delivery gate. Write one narrow candidate rule. A one-off
generation artifact or taste choice does not become global policy.

An explicitly approved rule or one supported by repeated independent reviews
may enter `content_learning_memory` in `config/brand.yaml` with source and
confidence; increment its version. Change agent behavior in a **new** version
of the relevant prompt under `prompts/`, then point `config/models.yaml` to it.
Add an observed failure to `feedback/REEL_STORY_GOLDEN_SET.md` or a focused
deterministic test where possible. Run QA and brief checks, then compare the
next generation against the saved failure. If later evidence contradicts a
rule, revise or retire it in a new version while retaining the prior record.

## Media and credit guard

- ChatGPT built-in image generation makes keyframe stills. Save selected images
  in the package and inspect them before motion generation.
- Edits MCP handles source footage, narration cut, timing, captions and export.
- invideo or Magnific may animate a selected keyframe when the shot has a
  specific job. Check balance and model pricing first; use invideo `dry_run`,
  `max_credits` and an idempotency key. For Magnific, read the live catalog and
  quoted cost before a run. Record the actual charge and stop after a useful
  result instead of generating redundant variants.
- The creator owns fal.ai generations. Provide a prompt and asset handoff when
  needed, but leave the fal.ai run to the creator.
- A posted or already finalized video is learning evidence. Do not spend
  credits regenerating it simply to exercise a tool.
