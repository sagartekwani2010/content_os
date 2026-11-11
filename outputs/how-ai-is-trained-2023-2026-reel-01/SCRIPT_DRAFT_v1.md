# How AI Is Trained, Reel 1 — script draft

**Status:** Draft for Sagar's review, 9 November 2026. This follows the approved eight-Reel concept slate; no separate human-authored production brief exists yet. No media generation, spend, scheduling or publishing is authorized by this draft.

## Concept fingerprint and execution plan

- **Topic:** How AI Is Trained: GPT-4 in 2023 to Kimi K3/K3.1 Pro and Claude Opus 5.5 in 2026.
- **Core thesis:** Next-token pretraining still supplies broad model capability; post-training shapes useful behavior; a real agent also needs supplied context, explicit rules and evaluation.
- **Learning objective:** Viewers can separate what a model learned during training from what an application supplied at runtime, then ask what result the system checks.
- **Format:** Face-led Instagram Reel, approximately 80–90 seconds.
- **Brand pillar:** `ai_builder`.
- **Sections:** 2023 GPT-4 baseline; concrete gym check-in; 2026 Kimi and Claude evidence; agent-system implication; future research direction and decision rule.
- **Story spine:** “Next-token prediction sounds too simple” → familiar gym request exposes a gap → two training stages persist in 2026 → runtime context and a safety rule close a different gap → three-question test for any agent claim.
- **Proof boundary:** The gym request is an illustrative *proposed* workflow. Do not show it as a deployed or successful system. Model-training statements are based on public reports, not access to proprietary recipes.

## Hook options

1. **Selected, approved concept wording:** “GPT-4 predicted the next token. Is that still how 2026 models learn?”
2. “If AI only predicts the next word, how can it decide what to do next?”
3. “The biggest mistake in AI explainers: confusing model training with the agent around it.”

Option 1 preserves the locked promise and opens the 2023-to-2026 question directly. Options 2 and 3 are alternates for creator review, not replacements for an approved spoken hook.

## Recording-ready spoken script

> **[Face to camera; first line unhurried]** GPT-4 predicted the next token. Is that still how 2026 models learn?
>
> **[Reveal one request on screen]** Imagine I tell a gym assistant: “I missed two sessions, and my shoulder hurts. What should I do today?”
>
> **[2023 card]** GPT-4's 2023 report described pretraining: repeatedly predicting the next token to learn broad patterns. Then post-training shaped how it answered.
>
> **[Point to the request]** That can give a model general knowledge. It does not give it my log, or permission to make decisions for me.
>
> **[2026 card]** In 2026, the two-stage backbone remains. Kimi K3 reports native vision and a more efficient architecture. K3.1 Pro reports much heavier post-training for agent tasks. Anthropic says Claude Opus 5.5 was pretrained, then substantially post-trained. These are public descriptions, not full recipes.
>
> **[Three layers appear one by one]** Now the missing layer. The app must supply my actual check-in. A proposed agent can ask for missing data; a fixed pain rule blocks automatic progression and routes the case to human review. Those are system decisions, not hidden facts in the model's weights.
>
> **[Face to camera]** So yes, pretraining still matters. But model capabilities, post-training and the systems around them have evolved.
>
> **[Future label: hypothesis]** My bet for what comes next: training judged by whether agents finish real tasks safely, not only by convincing answers.
>
> **[Close; hold each word cluster]** When someone says an agent “learned,” ask: what changed in the *model*, what context did the *app* supply, and what outcome did the *system* verify?

**Delivery note:** Aim for a measured 80–90 seconds. Preserve the entire question → training stages → runtime boundary → decision rule chain when cutting. Do not compress away the distinction between post-training and runtime agent rules.

## Timecoded visual and production plan

Timings are provisional; final keyframes must follow the recorded words.

| Time | Viewer question / new information | Visual proof and on-screen copy | Production mode / cut rationale |
| --- | --- | --- | --- |
| 0–6 s | Does 2026 training still use prediction? | Sagar on camera. Large copy: `2023 → 2026: WHAT CHANGED?` | Face-led hook; creates the unanswered question. |
| 6–16 s | What real request tests the explanation? | One simple illustrated check-in card, labelled `ILLUSTRATIVE`: missed sessions + shoulder pain. No fake product UI. | Presenter + clean still; introduces the running case. |
| 16–32 s | What did GPT-4's report actually say? | Real report title briefly, then two large cards revealed in speech order: `PRETRAINING: PATTERNS` → `POST-TRAINING: BEHAVIOR`. | Real paper capture + simple typography; establishes the 2023 mechanism. |
| 32–40 s | Why is training insufficient for this request? | The example request stays on screen; a separate `MY ACTUAL LOG?` card is blank. | Still/card; shows the missing runtime input. |
| 40–61 s | What is disclosed in 2026? | Source-title captures for Kimi K3, K3.1 Pro, Claude Opus 5.5, each with only the spoken fact: `TEXT + VISION`, `MORE POST-TRAINING`, `PRE + POST`. Footer: `PUBLIC DISCLOSURES`. | Real source captures + type; current evidence, no invented training diagram. |
| 61–77 s | What belongs to the application? | Reveal three steps only when spoken: `LOG SUPPLIED` → `MISSING DATA?` → `PAIN FLAG → HUMAN REVIEW`. Label `PROPOSED WORKFLOW`. | Face + simple flow; makes the agent/runtime boundary concrete. |
| 77–90 s | What should the viewer ask next? | Return to Sagar. Three words appear in spoken order: `MODEL` / `CONTEXT` / `VERIFIED OUTCOME`. `FUTURE: HYPOTHESIS` briefly appears with the future line. | Face close; leaves a reusable decision rule. |

**Thumbnail direction:** 9:16 cover, Sagar's face in center-safe zone. Exact headline: `HOW AI LEARNS IN 2026`; small secondary line: `GPT-4 → KIMI → CLAUDE`. Neutral background, high contrast, no invented interfaces or model logos. This is a design direction, not an image-generation request.

## Paste-ready caption

AI training did not stop at “predict the next token.” The useful question is what that stage teaches, what post-training changes, and what the application must still do at runtime.

GPT-4's 2023 report described next-token pretraining plus alignment. Public 2026 descriptions of Kimi K3/K3.1 Pro and Claude Opus 5.5 still show pretraining and post-training, with newer models handling richer inputs and more demanding tasks. The complete proprietary recipes are not public.

If you are building an agent, ask: what is in the model, what context is supplied now, and what outcome is checked? The gym example in the video is an illustrative system design, not fitness advice or a deployed result.

## Source and factual checks

- [GPT-4 Technical Report](https://arxiv.org/abs/2303.08774): explicitly describes next-token pretraining and post-training alignment. The spoken line simplifies “token” as “piece of text.”
- [Kimi K3 technical report](https://arxiv.org/abs/2607.24653): reports native vision and pre/post-training methods. Avoid calling K3 merely a base model; the paper also describes its post-training.
- [Kimi K3.1 Pro technical blog](https://www.kimi.com/en/blog/kimi-k3-1-pro): calls K3.1 Pro a post-trained version of K3 with substantially larger post-training compute. This is a vendor report, not independent verification.
- [Anthropic transparency hub](https://www.anthropic.com/transparency): Claude Opus 5.5 entry says pretraining followed by substantial post-training; it does not disclose a full recipe.
- **Future line:** explicitly Sagar's hypothesis. “Better tests of real tasks” is a direction, not an established industry consensus or promised feature.
- **Gym line:** illustrative design only. Do not use a real person’s check-in, personal health detail or claimed outcome without a recorded case and consent.

## Draft QA

- **Story check:** Question by second 5; concrete request by second 15; 2023 mechanism, 2026 evidence and the runtime reveal each add new information. The close resolves the training question and gives a three-part decision rule.
- **Evidence check:** Public-source claims above verified on 9 November 2026. Vendor-reported details and future hypothesis are labelled. No result or benchmark comparison is asserted.
- **Visual check:** One idea per card; labels revealed on the corresponding spoken cue. Keyframe timing remains provisional until recording.
- **Concept coverage:** 2023 GPT-4 baseline (spoken beat 3); gym check-in (beat 2); 2026 Kimi and Claude evidence (beat 5); agent-system implication (beats 6–7); future direction and decision rule (beats 8–9). No concept section is omitted. This is not a formal brief coverage check.
- **Provisional scores, 0–10:** hook 7.5; clarity 8; technical accuracy 8; brand fit 8.5; originality 7.5; share potential 7; save potential 7; visual potential 8; learning value 8.5; execution against an approved brief **0 because none exists**; AI hype penalty 0.5; generic content penalty 0.5. Under the repo's configured QA weights, provisional composite **7.215**. This is a self-review, not a model-run QA result.
- **Failed hard gate:** `POOR_BRIEF_EXECUTION`, because a separate human-authored production brief has not been supplied. Deterministic `python cli.py check <brief>` cannot run against a nonexistent brief. The other numeric hard gates pass provisionally; the final package gates have not been evaluated.
- **Verdict:** `REVISE` before asset generation: obtain the human brief or explicit confirmation of these six fingerprint fields, then run deterministic brief validation and final QA.
