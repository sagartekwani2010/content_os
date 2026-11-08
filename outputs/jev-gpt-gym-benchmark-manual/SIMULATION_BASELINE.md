# Gym Assistant Reel — GPT-5.6 Sol simulation baseline and provenance

## Values used in the draft Reel

| Measure | GPT-5.6 Sol | Jev 1.13 | Reel wording |
| --- | ---: | ---: | --- |
| Valid-safe decisions in the 50-decision Gym simulation | 50 / 50 | 50 / 50 | `Both cleared 50/50.` |
| Median latency in matched public benchmark | 1,661 ms | 456 ms | `Jev: 73% lower latency.` |
| Cost across matched public benchmark | $4.27 | $0.049 | `Jev: 99% lower cost.` |

The percentage reductions are calculated relative to GPT-5.6 Sol:

- latency: `(1,661 - 456) / 1,661 = 72.5%`, rounded to **73%**;
- cost: `($4.27 - $0.049) / $4.27 = 98.9%`, rounded to **99%**.

## What is simulated and what is measured

The **50/50 versus 50/50** line is a deliberately tied forecast for this
small, bounded Gym decision contract. It is not a live run of the Gym
Assistant, nor a quality result copied from another task. It supports the
actual story: a faster decision model does not eliminate the need for GPT.

The latency and cost ratios are scaled from an independent 2,390-item,
same-workload comparison of Jev and GPT-5.6 Sol. That evaluation found their
yes/no accuracy essentially tied (92.5% versus 92.1%), while Jev was 456 ms
versus 1,661 ms at median latency and cost $0.049 versus $4.27 for the full
run. The source also finds task-specific differences: Sol is better on some
multi-choice and counting tasks.

## Insight the Reel must preserve

**Jev being faster does not replace GPT.** GPT remains the model for messy
human context, reasoning, and explanation. Jev is a candidate for the
repeatable bounded decision after the state has been made clean.

Latency and cost are workload-specific. OpenAI notes that model choice and the
number of generated tokens materially affect latency; do not generalize the
73% / 99% figures beyond this narrow comparison.

## Source boundary

- The public comparison is an [independent 2,390-item report](https://jev-playground-five.vercel.app/report)
  that includes Jev 1.13 and GPT-5.6 Sol. It is not fitness data and its
  measurements were made through a Vercel gateway.
- OpenAI’s [latency-optimization guide](https://developers.openai.com/api/docs/guides/latency-optimization)
  explains why output length and model selection move observed latency.
- TypeSafe’s [public figures](https://typesafe.ai/) are not used for the
  73% / 99% values because they are vendor workflow claims.

## Replacement rule

Once `gym_decision_benchmark.py report` has processed real logs, replace the
two simulation counts and both percentage deltas. Keep the explicit role-split
insight only if the safety-boundary results support it.
