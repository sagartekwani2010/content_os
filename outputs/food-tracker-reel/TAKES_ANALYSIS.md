# Take analysis: IMG_3507.MOV (16 November 2026)

Source: 19:41 landscape 1080p SDR, lav mic, -13.1 LUFS integrated. Transcript: whisper.cpp small.en.
Rule: last complete take after the last "final" call for the beat; if no "final" call, last complete
take. Policy: the spoken words of the chosen take are ground truth for the script and visuals.

| Beat | "final" calls (s) | Takes seen | Chosen take (s) | Spoken (ground truth) |
|---|---|---|---|---|
| 1 | none (no cue) | 3 | 19.50-21.98 | In last video, you met my Gym Jarvis. |
| 2 | none (no cue) | 3 | 47.88-52.57 | Today, let's see how it scans my plate for protein and calories. |
| 3 | 91.8, 110.8, 114.2 | 9 | 127.53-132.55 | For building a system like this, I had Claude dig through a lot of research papers online. |
| 4 | 201.9, 213.2, 219.5, 227.4 | 9 | 248.56-256.20 | And I realized, naming items in your plate is super easy. But identifying the quantity of items is the hard part. |
| 5 | 278-333 (6 calls) | 11 | 346.14-351.05 | So, I split the problem into three parts: find, size, and look up. |
| 6 | none | 3 | 365.74-368.00 | Then I built two agents. |
| 7 | 420.3 | 6 | 437.30-444.62 | The first agent is the vision agent on Fable 5.2, which lists the items and its grams. |
| 8 | 458.5, 467.4 | 5 | 478.74-482.34 | It's not allowed to say calories or proteins in those items. |
| 9 | 517-570 (6 calls) | 12 | 594.97-602.29 | The second agent is the matcher agent, which finds all the items identified by the vision agent in a database. |
| 10 | none (no cue heard) | 3 | 622.77-625.71 | So every number traces back to a real source. |
| 11 | 678.4 | 8 | 690.49-694.36 | I packaged all of it as a Claude skill with a single guardrail. |
| 12 | 734.7, 745.5 | 9 | 756.24-759.28 | Which was: if unsure, flag the meal for my review. |
| 13 | 772.9-831.5 (6 calls) | 10 | 844.32-848.57 | Then I tested it on many meals that I had across days. |
| 14 | 865.3 | 4 | 877.88-882.30 | And it performed with reasonable accuracy across all kinds of food. |
| 15 | 904.7 | 7 | 923.17-926.37 | Except this one. Chicken hidden under carrots. |
| 16 | none | 6 | 973.37-977.40 | And 500 calories just became 94. |
| 17 | 1010.6 | 9 | 1036.02-1040.31 | To explicitly handle cases like this, I added a confidence score. |
| 18 | none | 5 | 1090.24-1094.73 | Now every meal is logged, and the less confident ones come to me for review. |
| 19 | 1137.3 | 7 | 1145.62-1150.07 | Next up, we'll see how my Workout Analyser tracks every set. |

Estimated length of the chosen takes: about 84 s.

## Differences from the planned script that change visuals

- Beat 8 adds "or proteins": cross out both calories and protein.
- Beat 9 "finds all the items identified by the vision agent in a database": show the vision agent's
  items flowing into the matcher and the USDA table.
- Beat 12 "flag the meal for my review": label "my review".
- Beat 17 is new: "To explicitly handle cases like this, I added a confidence score." (was "But its
  confidence was 0.3. It knew."). Visual: confidence score added to the flow; the chicken plate's
  measured 0.3 can still be shown.
- Beat 18 "less confident ones come to me for review".
- Beat 16 "500 calories became 94": measured 499 to 94; on screen 499 to 94 is consistent.

## Takes to double-check by ear

- Beat 11: whisper heard "guard drill" in several takes; expected "guardrail".
- Beat 17: some takes heard "confidence code"; the chosen take reads "score".
- Beat 9: the chosen take ends "in our database" in the transcript; probably "in a database".
