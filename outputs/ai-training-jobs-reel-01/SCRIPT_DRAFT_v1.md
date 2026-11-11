# Which AI jobs are actually emerging? — career-led training Reel

**Status:** Proposed script from Sagar's 9 November 2026 direction. This is a new career-led concept; it does not replace the previously locked `LLM-04` training explainer or constitute a human-approved production brief. Specific role guidelines are intentionally left open for Sagar to dictate. No media generation, spend, scheduling or publishing is implied.

## Concept and sequence

- **Audience promise:** Name the work behind pretraining, post-training and evaluation, explain why it requires people, and give viewers one credible way to demonstrate readiness.
- **Primary pillar:** `ai_career`, with an `ai_builder` technical lesson. This changes the primary pillar and thesis from the earlier `LLM-04` concept, so it needs its own brief before production.
- **Story spine:** Vague promise that AI will create jobs → three concrete types of work → how the two training stages work → why evaluation is a separate responsibility → 2026 evidence that the work is expanding in scope → choose one lane and build a proof artifact.
- **Evidence boundary:** Current job postings establish that these openings exist, not that AI has caused net job creation or guarantees employment. Job titles and requirements vary by employer. The portfolio recommendation is Sagar's practitioner judgment.

## Spoken script — about 85–95 seconds

> **[Direct to camera]** People say AI will create jobs. Which jobs? Imagine an AI assistant gets my gym check-in: “My shoulder hurts. Should I train today?” Three kinds of work help make that model useful.
>
> **[First card: PRETRAINING]** First, pretraining. The model predicts the next token, compares it with the real one, and updates its weights across huge datasets. Data and training engineers build those datasets and keep distributed runs reliable. That calls for coding, data engineering, and systems skills.
>
> **[Second card: POST-TRAINING]** Second, post-training. General knowledge doesn't tell the model how to handle my question. Post-training engineers use examples and feedback to shape behavior—like asking for context before offering a plan. This calls for machine learning, Python, controlled experiments, and debugging.
>
> **[Third card: EVALUATION]** Third, evaluation. Did the changed model handle new pain cases better—or fail somewhere else? Evaluation engineers create held-out tests, inspect errors, and judge whether the improvement is real. That takes experimental design and statistics.
>
> **[2023 → 2026]** These roles are current. Kimi K3 reports pretraining on text and images; K3.1 Pro reports much larger post-training for agent tasks. Claude Opus 5.5 also discloses both stages.
>
> **[Face-led close]** So if you want in, choose one lane. Build a clean, reproducible data pipeline, or take an open model and show one change against a baseline on unseen cases. Publish the failures and what you learned.
>
> That's what I would look for: evidence you can improve one part of the loop.

**Delivery note:** The role categories are generic by design. Sagar can later supply exact titles, qualification rules and his own hiring viewpoint without changing the training mechanism. Aim for about 85–95 seconds; let the first three role reveals carry the visual pace. The gym check-in is illustrative and gives no exercise or medical advice.

## Shot and engagement plan

| Beat | Viewer question | On-screen evidence/copy | What changes in the story |
| --- | --- | --- | --- |
| 0–10 s | Which jobs and why should I care? | Face + illustrated `ILLUSTRATIVE GYM CHECK-IN`; copy `WHICH AI JOBS, EXACTLY?`. Flash real, dated posting-title crops for the three role families, without pay figures. | Converts a vague career claim into one concrete question and shows the openings exist. |
| 10–29 s | What is pretraining work? | `PREDICT → ERROR → WEIGHT UPDATE`; reveal `DATA + TRAINING SYSTEMS` | Shows the mechanism and the people who make it run. |
| 29–48 s | Why is post-training separate? | `EXAMPLES + FEEDBACK → BEHAVIOR CHANGE`; reveal `EXPERIMENTS + MODEL DEBUGGING` | Shows a second kind of work, tied to the gym question. |
| 48–64 s | Who checks that the change worked? | `UNSEEN CASES → REGRESSIONS → DECISION`; reveal `EVALUATION` | Adds the quality-control role and a concrete test. |
| 64–77 s | Is this still relevant in 2026? | Real source-title captures: Kimi K3, K3.1 Pro, Claude Opus 5.5; `PUBLIC DISCLOSURES` | Grounds the evolution in current reports. |
| 77–95 s | What should I do to qualify? | Split path: `REPRODUCIBLE DATA PIPELINE` or `BASELINE → ONE CHANGE → HELD-OUT TEST → FAILURES` | Leaves a concrete proof-of-work choice. |

**Cover direction:** Face-led 9:16, exact headline `WHICH AI JOBS?`, subline `PRETRAINING · POST-TRAINING · EVALS`. Keep the headline readable in the profile-grid crop. Use a real creator photo, not generic AI imagery.

## Paste-ready caption

“AI will create jobs” is only useful if we can name the work.

Current openings show three role families around model training: preparing data and reliable training runs, improving behavior after pretraining, and testing whether the improvement holds on unseen cases. The qualifications differ, but each demands evidence you can build, measure and debug.

Start with one lane. Build a small reproducible project, record the baseline, test one change and publish the failures. The gym question in the Reel is an illustrative evaluation case, not exercise advice or a claim that a model handled it safely.

## Sources and factual checks

- [GPT-4 technical report](https://arxiv.org/abs/2303.08774) describes next-token pretraining and separate post-training alignment. [Original ChatGPT training method](https://openai.com/index/chatgpt/) documents examples, human rankings and further training for that historical release.
- [Kimi K3 report](https://arxiv.org/html/2607.24653v2) explicitly describes a joint text-and-vision next-token objective; [Kimi K3.1 Pro](https://www.kimi.com/en/blog/kimi-k3-1-pro) reports substantially more post-training compute. These are author/vendor descriptions.
- [Claude Opus 5.5 transparency entry](https://www.anthropic.com/transparency) describes pretraining followed by substantial post-training without a full public recipe.
- Current employer postings show the corresponding work: [pretraining scaling](https://job-boards.greenhouse.io/anthropic/jobs/4938432008) seeks large-scale ML and distributed-systems experience; [production post-training](https://job-boards.greenhouse.io/anthropic/jobs/4613592008) seeks Python, ML frameworks and model-training experience; [post-training evaluations](https://job-boards.greenhouse.io/anthropic/jobs/5198255008-126) seeks Python, evaluation design and statistical judgment. These postings are examples of current hiring, not proof of net job creation or universal qualifications.

## Draft QA and decision

- **Engagement:** The hook poses the actual viewer question; each training stage reveals a job category and qualification signal; the final beat provides a concrete action. No generic “learn AI” CTA.
- **Learning payoff:** Viewers can distinguish pretraining, post-training and evaluation work, then choose a portfolio artifact that shows one relevant skill.
- **Technical boundary:** The script describes representative mechanisms and current postings. It does not claim every model uses the same post-training recipe or that an open-model project qualifies someone for a frontier role by itself.
- **Provisional scores, 0–10:** hook 8; clarity 8; technical accuracy 8; brand fit 8; originality 7.5; share potential 8; save potential 7; visual potential 7.5; learning value 8.5; execution against an approved brief **0 because none exists**; AI hype penalty 0.5; generic content penalty 0.5. Weighted composite under the repo's QA formula: **7.315**. This is a self-review, not a model-run QA result.
- **Failed hard gate:** `POOR_BRIEF_EXECUTION`, because this career-led concept lacks its own approved brief. The other numeric hard gates pass provisionally. All concept beats are covered: job question, pretraining, post-training, evaluation, current evidence and career action.
- **Concept status:** `REVISE` before production. This changes the earlier concept's thesis, learning objective and primary brand pillar. A separate human-authored brief and Sagar's role guidelines are needed before keyframes or production assets. `python cli.py check <brief>` is not applicable until that brief exists.
