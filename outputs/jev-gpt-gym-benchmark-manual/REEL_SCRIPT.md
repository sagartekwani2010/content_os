# Jev vs GPT inside my Gym Assistant — master script

## Overall script — speakable reference

Last Reel, we compared Jev’s architecture with ChatGPT. This time, I put both
inside a Gym Assistant I built.

Every week, it sees whether I trained, how recovery felt, and a short note from
me. Its job is not to send a motivational reply. It has to choose what happens
next: progress, hold, ask for more information, or flag the situation for
human review.

That gives GPT and Jev one fair job to compare. GPT can understand my messy
note and talk me through it. Jev cannot chat; once it gets the same clean state,
it has to choose one permitted action. I forced GPT to make that same final
choice too.

I designed five everyday situations ten times each: a normal week, a difficult
recovery week, missing information, conflicting information, and a pain flag.
That is fifty decisions per model — not one cherry-picked prompt. Until my live
runs are complete, the numbers are a simulation anchored to public matched
decision-benchmark data.

The simulation gives GPT-5.6 Sol **50 valid, safe decisions out of 50**. Jev
also gets **50 out of 50**. On the larger matched decision benchmark behind
the efficiency assumptions, Jev had **73% lower median latency** and **99%
lower cost** than GPT-5.6 Sol.

That is the important insight: Jev being faster is not the end of the road for
GPT. GPT keeps the messy human conversation and the explanation; Jev is useful
only for the repeated, clean, bounded decision. And these percentages are
workload-specific — model choice, output length, and implementation all move
latency and cost. My live run is the only number that matters for this Gym
Assistant.

The next experiment follows naturally: does that combined Gym Assistant beat
the GPT-only version end to end — or just add another system to maintain?

## Time-driven script

| Time | Spoken line | On-screen proof / visual |
| --- | --- | --- |
| 0–5s | “Last Reel, we compared Jev’s architecture with ChatGPT. This time, I put both inside a Gym Assistant I built.” | Sagar on camera; quiet callback to the prior Reel title. |
| 5–11s | “Every week, it sees whether I trained, how recovery felt, and a short note from me.” | Still: weekly check-in inputs. |
| 11–16s | “It has to choose: progress, hold, ask for more information, or flag the situation for human review.” | Still: four permitted actions. |
| 16–22s | “GPT can understand my messy note and talk me through it. Jev cannot chat; with the same clean state, both have to make this final choice.” | Still: two roles, one identical decision contract. |
| 22–27s | “I designed five everyday situations, ten times each: fifty decisions per model. These are research-anchored simulation numbers until I publish my live runs.” | Still: five cases × ten runs. |
| 27–34s | “GPT-5.6 Sol: 50 valid and safe decisions out of 50. Jev: also 50 out of 50 — with 73% lower latency and 99% lower cost on the matched benchmark.” | Simulation result card — label it as simulated, show the model names and every number. |
| 34–39s | “Jev being faster does not replace GPT. GPT handles the messy conversation; Jev handles the repeated decision. And this is workload-specific — my own live run decides it.” | Still: conclusion / role split. |
| 39–45s | “Next, I’ll test GPT plus Jev against GPT-only. Better system — or just more complexity?” | Sagar on camera; simple follow prompt. |

## Result requirements before recording

- Say “simulation” once in the spoken Reel and label the result card
  `SIMULATED 50-RUN ESTIMATE` until this fixture suite has been run live.
- Replace the four simulation values with the recorded report before calling
  them results from “my Gym Assistant.”
- Report the valid-and-safe count for **both** models, not speed and cost alone.
- If either model fails the pain/escalation boundary, state that plainly; do not
  imply equal safety.
- The assistant flags health concerns for human review. It does not provide
  medical advice.
