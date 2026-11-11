# How AI Is Trained, Reel 1 — script draft

**Status:** Revised draft for Sagar's review, 9 November 2026. This follows the approved eight-Reel concept slate; no separate human-authored production brief exists yet. The previous draft and its QA are preserved in `SCRIPT_DRAFT_v1.md`. No media generation, spend, scheduling or publishing is authorized by this draft.

## Concept fingerprint and execution plan

- **Topic:** How AI Is Trained: GPT-4 in 2023 to Kimi K3/K3.1 Pro and Claude Opus 5.5 in 2026.
- **Core thesis:** Next-token pretraining builds broad model capability through prediction-error updates; post-training further updates weights using examples and feedback; an agent application still needs live context, explicit rules and outcome checks.
- **Learning objective:** Viewers can explain the basic update in pretraining and post-training, identify their distinct jobs, and separate both from an application's runtime responsibilities.
- **Format:** Face-led Instagram Reel, approximately 100–110 seconds at a measured pace.
- **Brand pillar:** `ai_builder`.
- **Sections:** 2023 GPT-4 baseline; concrete gym check-in; 2026 Kimi and Claude evidence; agent-system implication; future research direction and decision rule.
- **Story spine:** A gym question demands a trustworthy response → pretraining explains knowledge but exposes the missing personal context → post-training explains assistant behavior but cannot supply live facts → 2026 evidence shows both stages have evolved → the app must supply facts and enforce the boundary → three-layer takeaway.
- **Proof boundary:** The gym request is an illustrative *proposed* workflow. Do not show it as a deployed or successful system. Model-training statements are based on public reports, not access to proprietary recipes.

## Hook options

1. **Selected, stronger spoken opening:** “In 2023, GPT-4 learned to predict the next token. I wouldn't trust that alone with this gym decision.”
2. **Original locked concept wording:** “GPT-4 predicted the next token. Is that still how 2026 models learn?”
3. “A model can know every exercise and still mishandle your workout. Here's why.”

Option 1 turns the locked 2023-to-2026 question into a concrete decision tension; the answer comes from the two training stages and the app boundary. Option 2 preserves the concept wording for creator review. The hook is planned wording until Sagar approves and records it.

## Recording-ready spoken script

> **[Face to camera; open on the decision tension]** In 2023, GPT-4 learned to predict the next token. I wouldn't trust that alone with this gym decision.
>
> **[One gym check-in appears]** Here's the test: “I missed two gym sessions, and my shoulder hurts. What should I do today?”
>
> **[Reveal guess → error → update]** Pretraining first. The model sees the start of a passage and predicts the next token. Training compares that prediction with the actual token, adjusts the model's weights, and repeats across enormous amounts of data. It learns broad patterns, including exercise language. That is capability, not a decision about me.
>
> **[Show two illustrative responses]** Next, post-training. Give the model examples of user questions and useful answers; update its weights again. Early ChatGPT also used human rankings of alternative answers to guide further training. For this gym question, you'd prefer a response that asks about the pain over one that blindly prescribes a workout. This shapes assistant behavior. It still doesn't supply my current facts.
>
> **[2023 timeline moves to 2026]** In 2026, that structure remains. Kimi K3 reports next-token pretraining across text and images. K3.1 Pro reports substantially more post-training for agent tasks. Anthropic says Claude Opus 5.5 also has pretraining followed by substantial post-training. The full recipes aren't public.
>
> **[Return to check-in; reveal boundary]** Then comes the app. It provides my log and enforces a hard rule: pain stops automatic progression and goes to human review.
>
> **[Small on-screen label: HYPOTHESIS]** My bet for what's next: models learn more from complete tasks, while independent checks tell us whether those tasks were finished safely.
>
> **[Face-led close; reveal three layers in order]** So remember three layers: pretraining builds broad capability, post-training shapes responses, and the app supplies current context and checks the outcome. If someone says an agent “learned,” ask which layer actually changed.

**Delivery note:** About 260 spoken words; plan for 100–110 seconds at a measured pace. Keep the example, prediction update, post-training update, 2026 evidence and runtime boundary in this order. The sample response ranking is illustrative, not a claim about a real training dataset.

## Timecoded visual and production plan

Timings are provisional; final keyframes must follow the recorded words.

| Time | Viewer question / new information | Visual proof and on-screen copy | Production mode / cut rationale |
| --- | --- | --- | --- |
| 0–7 s | Why is next-token training insufficient for this decision? | Sagar on camera. Small date `2023 GPT-4`; large copy: `NEXT TOKEN ≠ TRUSTED DECISION`. | Face-led hook; creates the unanswered question. |
| 7–14 s | What real request tests the explanation? | One clean check-in card, labelled `ILLUSTRATIVE`: missed sessions + shoulder pain. No fake product UI. | Presenter + still; the same request carries the whole story. |
| 14–38 s | What does pretraining actually change? | Real GPT-4 report title, then progressive `START OF TEXT → NEXT TOKEN GUESS → ERROR → WEIGHT UPDATE`. Hold `WEIGHT UPDATE` while repeated examples are described. | Real source capture + simple motion; shows a training mechanism rather than a definition. |
| 38–62 s | How does post-training change the base model? | `USER QUESTION → EXAMPLE ANSWERS → RANKED ALTERNATIVES → FURTHER UPDATE`. Two response cards are explicitly `ILLUSTRATIVE`: `PRESCRIBE IMMEDIATELY` vs `ASK ABOUT PAIN`. | Face + two readable cards; reveals why a general predictor can act more like an assistant. |
| 62–84 s | What survives into 2026? | Source-title captures and three brief evidence labels revealed with the narration: `K3: TEXT + IMAGE TOKENS`, `K3.1 PRO: MORE POST-TRAINING`, `CLAUDE OPUS 5.5: PRE + POST`. Footer: `PUBLIC DISCLOSURES`. | Real source captures + type; answers the hook with current evidence. |
| 84–97 s | What belongs to the app, not model training? | Return to the request. Reveal `CURRENT LOG` → `PAIN FLAG` → `HUMAN REVIEW`, labelled `PROPOSED WORKFLOW`. | Simple flow; locates the runtime boundary. |
| 97–110 s | What can the viewer now remember and test? | Brief `FUTURE: HYPOTHESIS` label, then Sagar on camera. Reveal `PRETRAINING / POST-TRAINING / APP` in spoken order. | Face-led close; converts the story into a three-layer mental model and ends on the decision rule. |

**Thumbnail direction:** 9:16 cover, Sagar's face in center-safe zone. Exact headline: `HOW AI LEARNS IN 2026`; small secondary line: `GPT-4 → KIMI → CLAUDE`. Neutral background, high contrast, no invented interfaces or model logos. This is a design direction, not an image-generation request.

## Paste-ready caption

The next-token story is true—and incomplete. Pretraining repeatedly compares a model's prediction with what actually came next and updates its weights. Post-training updates it again with examples and feedback so it behaves more like a useful assistant.

GPT-4's 2023 report described next-token pretraining plus alignment; the original ChatGPT method also described human-ranked answers. Public 2026 descriptions of Kimi K3/K3.1 Pro and Claude Opus 5.5 still show pretraining and post-training, with richer inputs and more demanding tasks. The complete proprietary recipes are not public.

If you are building an agent, ask what came from its base model, what was shaped later, and what the app supplies and checks at runtime. The gym example is an illustrative design, not fitness advice or a deployed result.

## Source and factual checks

- [GPT-4 Technical Report](https://arxiv.org/abs/2303.08774): explicitly describes next-token pretraining and post-training alignment. The spoken prediction-error loop is a high-level description of the training objective, not a disclosure of every optimizer detail.
- [Original ChatGPT method](https://openai.com/index/chatgpt/): describes supervised fine-tuning with human-written dialogues, ranked alternative answers, a reward model and further reinforcement learning. This is an early ChatGPT example, not a disclosed GPT-4 recipe.
- [Kimi K3 technical report](https://arxiv.org/html/2607.24653v2): explicitly describes a joint text-and-vision next-token objective and separate post-training. Avoid calling K3 merely a base model; the paper also describes its post-training.
- [Kimi K3.1 Pro technical blog](https://www.kimi.com/en/blog/kimi-k3-1-pro): calls K3.1 Pro a post-trained version of K3 with substantially larger post-training compute. This is a vendor report, not independent verification.
- [Anthropic transparency hub](https://www.anthropic.com/transparency): Claude Opus 5.5 entry says pretraining followed by substantial post-training; it does not disclose a full recipe.
- **Future line:** explicitly Sagar's hypothesis. More learning from complete tasks with independent safety checks is a direction, not an established industry consensus or promised feature.
- **Gym line:** illustrative design only. Do not use a real person’s check-in, personal health detail or claimed outcome without a recorded case and consent.

## Draft QA

- **Story check:** Question by second 5; concrete request by second 15; prediction-error update and example/feedback update are distinct mechanisms; 2026 evidence answers the opening question; runtime reveal resolves the gym case. The close gives a three-layer decision rule.
- **Evidence check:** Public-source claims above verified on 9 November 2026. Vendor-reported details and future hypothesis are labelled. No result or benchmark comparison is asserted.
- **Visual check:** One idea per card; labels revealed on the corresponding spoken cue. Keyframe timing remains provisional until recording.
- **Concept coverage:** 2023 GPT-4 baseline (pretraining beat); gym check-in (opening and runtime); 2026 Kimi and Claude evidence (current beat); agent-system implication (runtime and close); future direction (last line). No concept section is omitted. This is not a formal brief coverage check.
- **Provisional scores, 0–10:** hook 7.5; clarity 8.5; technical accuracy 8.5; brand fit 8.5; originality 8; share potential 7.5; save potential 7.5; visual potential 8.5; learning value 9; execution against an approved brief **0 because none exists**; AI hype penalty 0.5; generic content penalty 0.5. Under the repo's configured QA weights, provisional composite **7.550**. This is a self-review, not a model-run QA result.
- **Failed hard gate:** `POOR_BRIEF_EXECUTION`, because a separate human-authored production brief has not been supplied. Deterministic `python cli.py check <brief>` cannot run against a nonexistent brief. The other numeric hard gates pass provisionally; the final package gates have not been evaluated.
- **Verdict:** `REVISE` before asset generation: obtain the human brief or explicit confirmation of these six fingerprint fields, then run deterministic brief validation and final QA.
