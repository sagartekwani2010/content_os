# Post-review capture template

Use this after a human edits or publishes a piece. The goal is to turn a review
into evidence, not silently rewrite brand guidance.

```yaml
post:
  title: ""
  stage: "generated_candidate | final_export | published_review"
  published_at: "YYYY-MM-DD or null"
  output_artifact: "outputs/<file>.md"
  media_artifact: "local path or durable project URL"
  source_map: "local path or null"
  approved_hook: ""
generation:
  tool: "ChatGPT | Edits | invideo | Magnific | fal.ai | none"
  model: ""
  prompt_version: ""
  keyframes: []
  generation_id: ""
  estimated_credits: null
  charged_credits: null
review:
  source: "human review | performance data | both"
  summary: ""
changes:
  - category: "hook | story | visual | factual | edit | delivery | brand"
    before: "Draft version or concise description"
    after: "Final version or concise description"
    why: "What improved or what failed"
    evidence: "Human rationale, measured result, or both"
candidate_learning:
  rule: "Generalized rule, stated narrowly"
  confidence: "low | medium | high"
  promotion_status: "candidate | explicitly approved | repeated evidence"
verification:
  brief_and_spoken_cues: "pass | fail | not_applicable"
  captions_and_mix: "pass | fail | not_applicable"
  full_decode_and_codec: "pass | fail | not_applicable"
  next_generation_checked_against_failure: "pass | fail | pending"
```

Only add a candidate learning to `config/brand.yaml` after repeated evidence or
explicit human approval. Include the source and confidence when it is promoted.
