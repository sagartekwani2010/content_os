# Generic AI · 01 — Who works behind ChatGPT and Claude?

**Status:** Part 1 script for creator review, 9 November 2026. The earlier career-led draft is preserved in `SCRIPT_DRAFT_v1.md`. Part 2 will cover how to demonstrate readiness through a real, bounded project. This script reflects Sagar's direction in chat; a separate production brief has not yet been created.

## Story promise

People hear that AI will create jobs but cannot name the work. Use a gym question to explain three kinds of work visible at frontier labs: building the base model, shaping its behavior, and checking whether it improved. Sagar's post-training and evals experience makes the next episode a practical continuation.

## Spoken script — approximately 75–90 seconds

> **[Face to camera]** People say AI will create jobs. Which jobs? Look at OpenAI's ChatGPT and Anthropic's Claude.
>
> Imagine I ask an AI: “My shoulder hurts. Should I train today?” It could sound fluent and still give me a bad answer. Who makes it better?
>
> **First: pretraining.** The model learns patterns by repeatedly predicting what comes next in huge amounts of data, then adjusting its weights. People build the data and training systems that make this possible. Think data engineers and training engineers.
>
> **Then: post-training.** Knowing language is different from knowing how to respond. Post-training researchers use examples, feedback and experiments to shape the model's behavior—so it can handle uncertainty, ask for context and avoid sounding certain when it shouldn't.
>
> **And then: evals.** Evaluation researchers give the model questions it hasn't seen and check what changed. Did it become more useful? Did it start failing somewhere else? Their job is designing tests you can actually trust.
>
> At frontier labs, these are real areas of work: training, post-training and evaluation. The roles go well beyond writing prompts.
>
> I work extensively on post-training models and evals. In the next Generic AI video, I'll show the small experiment I'd build to demonstrate those skills. And in this series, I'll share what I've learned about making models better—and catching the failures.

**Delivery:** Keep “what jobs?” sharp, pause after each role reveal, and make the final first-person line direct. The gym question is an illustrative case, not medical or exercise advice. Do not imply Sagar works at OpenAI or Anthropic.

## On-screen beats

| Spoken cue | Visual/copy | Purpose |
| --- | --- | --- |
| “What jobs?” | Face-led cover: `GENERIC AI · 01` / `WHO BUILDS CHATGPT & CLAUDE?` | Series identity and question. |
| “My shoulder hurts” | Simple chat bubble labelled `ILLUSTRATIVE QUESTION`; no generated answer | Familiar case without a medical claim. |
| “First: pretraining” | `DATA → PREDICT → ADJUST WEIGHTS`; then `DATA + TRAINING ENGINEERS` | One mechanism and the people behind it. |
| “Then: post-training” | `EXAMPLES + FEEDBACK → BEHAVIOR`; then `POST-TRAINING RESEARCHERS` | Shows what changes after the base model. |
| “And then: evals” | `UNSEEN QUESTIONS → CHECK FAILURES`; then `EVAL RESEARCHERS` | Makes measurement a visible job. |
| “I work extensively” | Return to Sagar; `NEXT: A REAL SMALL EXPERIMENT` | Establishes creator authority and the next episode's payoff. |

Use real Sagar footage for the opening and close. Any lab imagery or job-page crop must be genuine and legible; avoid decorative logos implying affiliation. Reveal each label when that line is spoken.

## Caption draft

**Generic AI · 01 | Who works behind models like ChatGPT and Claude?**

The broad answer is three kinds of work: building the data and training systems, improving model behavior after pretraining, and measuring whether those changes actually help. Current frontier-lab roles cover these areas, though titles and requirements vary.

I spend much of my time on post-training and evals. In the next episode, I'll walk through a small project that shows what credible evidence of those skills could look like.

The gym question is illustrative; it is not training or medical advice. #GenericAI #AIResearch #MachineLearning

## Factual basis and boundaries

- [OpenAI post-training role](https://openai.com/careers/research-engineerresearch-scientist-post-training-model-experience-san-francisco/) describes shaping ChatGPT behavior with human data, evaluations, reward models and post-training.
- [Anthropic pretraining scaling role](https://job-boards.greenhouse.io/anthropic/jobs/4938432008) describes production pretraining systems, data and reliability; [production post-training role](https://job-boards.greenhouse.io/anthropic/jobs/4613592008) describes training Claude base models into production models; [post-training evals role](https://job-boards.greenhouse.io/anthropic/jobs/5198255008-126) describes measurement, regressions and training decisions.
- These examples show current job families. They do not establish net job creation or a guarantee that any particular credential leads to a role. The spoken script keeps titles generic, per creator direction.
- Sagar's own post-training and evals work is a creator-supplied first-person claim; use his preferred exact wording in the recording.

## Script QA

- **Hook answer:** Three work areas and the people behind them are named.
- **Learning payoff:** The viewer can distinguish pretraining, post-training and evals with one everyday example.
- **Series bridge:** Part 2 promises a specific experiment, not an unspecified list of tips.
- **Performance intent:** The closing gives non-followers a reason to expect firsthand methods in a recurring series. Measure organic follows per 1,000 non-follower accounts reached after seven days; keep paid reach separate.
- **Production status:** Script ready for creator wording review. Keyframes, recording and final video have not been produced. `python cli.py check <brief>` is pending a matching human-authored brief.
