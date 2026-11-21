# Facts: Gym Jarvis Ep 3, Workout Analyser (measured 19-20 Nov 2026)

Only what has been measured or built. Open items are [SLOTS]. Data files: `demos/workout-hud/data/` (gitignored),
summary in `demos/workout-hud/data/verdicts.json`.

## The tease this reel pays off
- The Fable 5.2 deep-dive (posted 19 Nov) ends: "Let's see how Fable stopped me from doing a wrong set in my Workout
  Analyser", over IMG_2649 (hack squat) with a red circle and a red X "STOP!".
- All footage was filmed before the analyser existed (15 Aug and 28 Aug 2026). Say "found", "flagged", "would have
  stopped me". Never "stopped me mid-set".

## What was analysed
- 23 sets from 2 gym sessions: 15 Aug 2026 legs + core (blue T-shirt, 15 clips) and 28 Aug 2026 back + chest
  (red T-shirt, 8 clips). [N_SETS] = 23.

## The system (architecture, left to right)
1. Pose tool: YOLO11n-pose finds 17 body joints in every frame, 30 frames a second.
2. Rep maths (code): picks the joint that moves in a rhythm (knee, hip or elbow), finds each rep, measures its range
   in degrees, its speed and torso sway.
3. Safety check (code, before any AI is asked): if the moving joint is hidden in over 25% of frames, the system prints
   "CAN'T SEE YOUR KNEE. NOT JUDGING THIS SET." (joint name changes) and gives no verdict. [CAN'T-SEE STRING]. It fired
   on 4 of 23 sets.
4. Baseline = my own best rep in that set (largest range), not a textbook.
5. Judge agent: Claude Fable 5.2 reads the rep table + 4 key frames (best rep and worst rep, both ends) and returns
   CONTINUE / HOLD / STOP with a reason of 4 words max. About USD 0.15 per set.
6. Coach agent: Claude Fable 5.2 as a coach, frames only (2 per second), never sees the numbers. Says good / bad / unclear.
7. Rule: STOP only if the judge says STOP AND the coach says bad. If they disagree: "CHECK FOOTAGE".
8. Output: the Gym Jarvis HUD.

## Results over 23 sets (final verdicts)
- CONTINUE 6 · HOLD 11 · STOP 1 · CHECK FOOTAGE 1 · CAN'T SEE 4.
- Exactly one STOP ("1 FLAGGED" is true).

## The STOP [BAD_SET]
- IMG_2661, 15 Aug 2026, lying leg raise with hip lift (reverse crunch) on a flat bench, blue T-shirt.
- Judge (Fable 5.2, numbers + frames): STOP. Reason [REASON]: "Legs not lowering fully". Detail: "Most reps only swing
  through about 60-80 degrees at the hip against 122 on your best rep."
- Coach (Fable 5.2, frames only): BAD. "Reps 4, 5 and 9 are cut short with bent knees and little pelvic curl, and the
  whole set is swung rather than controlled."
- In plain words both agree on: short, swung reps instead of controlled ones.
- Ghost: best rep = rep 20 (hip range 122 degrees), worst rep = rep 10 (53 degrees), same set, same camera angle. [BEST_SET]
- Caution: the pose tool split this set into 20 reps where the coach counts 12, so no rep count is shown for it.
- [RISK]: creator's own words, 3 words max, or cut. The AI measures range and swing, not injury.

## The false alarm (the failure + fix story)
- IMG_2650, 15 Aug 2026, dumbbell deficit reverse lunge, 17 reps, blue T-shirt.
- Judge said STOP: "Most reps cut short. Only 5 of 17 reps got near your best rep's 80 degrees of knee bend."
- Coach said GOOD: depth consistent, front thigh about parallel every rep.
- Checked by eye on the footage: depth looks the same; I turn towards the camera on some reps, and the knee angle reads
  shallower from the front. The judge was fooled by the camera angle.
- Fix: the two-AI rule above. Final verdict for the lunge: CHECK FOOTAGE.

## Earlier failure (measured on IMG_2649 hack squat; optional, on-screen only)
- Raw pose tool counted 14 reps; there were 11. Dropped by the fix: a half rep at the clip start (0.0-0.7 s), a 0.2 s
  "rep" at 15.4 s with an impossible 115 degree torso lean (tracker jumped joints), and a half rep at the clip end
  (27.9 s). One rep had an impossible 11 degree knee reading behind the machine frame: those frames are thrown out.
  After the fix: 11 reps, matching the coach. 58 of 877 frames (6.6%) rejected.

## The tease clip IMG_2649 (hack squat)
- Coach: GOOD (11 reps, deep on every rep). Judge: HOLD ("depth varies between reps": most reps about 122 degrees of
  knee travel vs 143 on the best rep). Final: HOLD. It was NOT a STOP. Honest twist: "the set I teased wasn't the one".

## The red day (28 Aug, back + chest)
- No STOP. Seated row IMG_2785: CONTINUE, "Torso steady, pulls consistent", torso sway 3 to 7 degrees.
- Lat pulldown IMG_2783: HOLD, "Range shrinking late" (rep 4: 62 degrees of elbow travel vs 86 on the best rep).

## Honest limits (caption, not voice)
- Judge and coach agree on flag vs no flag in 9 of 16 sets both could judge. Same model, different inputs.
- Footage was phone video from one angle; not training advice.

## Series
- Ep 1 Gym Jarvis intro. Ep 2 Meal Analyser: vision agent + matcher agent on Fable 5.2, hidden-chicken failure,
  confidence guardrail. Fable 5.2 deep-dive (19 Nov).
- Creator builds AI agents for a living and tests them on his own training and food.

## Sunday tease (creator decision 20 Nov): layoffs + hiring -> evals and post-training series
- Claim allowed in the tease, no numbers: companies are laying people off and hiring for AI roles at the same time.
  Sources (checked 20 Nov 2026): eWeek 2026 layoffs tracker (companies cutting jobs while hiring aggressively for AI
  roles; IBM replaced about 200 HR roles with AI agents while tripling entry-level AI hiring),
  https://eweek.com/news/tech-layoffs-ai-investment-2026 ; National CIO Review (headcount falls, hiring stays active
  where AI spending is concentrated), https://nationalcioreview.com/?p=79084 ; landing.jobs 2026 European tech data
  (cutting and hiring for the same roles at once), https://landing.jobs/blog/how-hiring-patterns-are-shifting-after-ai-layoffs
- Contested: CBS News reports economists see AI's effect more as weaker hiring than mass layoffs. So: no "because of
  AI", no numbers in the tease.
- SALESFORCE EXAMPLE (creator decision 20 Nov, replaces the generic line):
  - Cuts: CEO Marc Benioff said Salesforce went from about 9,000 to about 5,000 support heads because AI agents
    handle about half of the conversations ("I need less heads", The Logan Bartlett Show, 2025; widely reported, e.g.
    https://www.outlookbusiness.com/artificial-intelligence/ai-agents-replaced-4000-customer-support-jobs-at-salesforce-says-ceo-marc-benioff ).
    Further cuts of nearly 1,000 jobs were REPORTED in Feb 2026 (not confirmed by Salesforce; do not use).
  - Hiring: Salesforce posted "LMTS - Lead AI/ML Engineer (LLM Post-Training)", JR368314, Bangalore + Hyderabad,
    posted 13 Nov 2026, on its own careers site (saved verbatim: outputs/hiring-posttraining-reel/SALESFORCE_LMTS_POSTTRAINING_JD.md).
    Quote: "This is a model-training role, not a wrapper around a hosted LLM and not a prompt-engineering-only role."
- Tease line (spoken, last beat, over hook footage): "Salesforce's CEO said AI agents replaced 4,000 support jobs.
  Last week, Salesforce posted this: a lead post-training job in Bangalore. Next, how to get hired for it. Follow along."
  On screen for 1 s: the real job title + "Posted 13 Nov 2026 · Bangalore" (screenshot of the public posting, cropped
  to the title block). Then the series: how to get hired -> evals -> post-training.

- UPDATE 20 Nov 02:00 (creator): tease uses India. Reported 19-20 Nov 2026 by Free Press Journal, People Matters, DNA,
  SME Futures: Salesforce layoffs reached India; affected staff reportedly on garden leave until 1 Feb 2027, severance
  about 21 weeks; based on employee posts, NOT confirmed by Salesforce -> the line must say "reportedly".
  https://www.peoplematters.in/news/strategic-hr/salesforce-layoffs-2026-india-employees-report-cuts-some-put-on-garden-leave-53440
  https://www.dnaindia.com/business/report-salesforce-layoffs-hit-india-employees-staff-put-on-garden-leave-till-february-1-3224284
  Tease line now: "Salesforce reportedly just put staff in India on garden leave. And it's hiring this, in Bangalore.
  Next: how to get it."

## Settled items (so checkers do not re-flag them)
- The FORM giveaway EXISTS and was verified on 20 Nov: `outputs/workout-analyser-reel/share/` holds the form-coach
  skill (SKILL.md), its script (label_sets.py), architecture.png and a README; no footage inside. Viewers who comment
  FORM get that bundle. In plain words: "my AI coach prompt + the diagram".
- Runtime target for this reel: 55-62 s after 1.15x (creator accepted the longer cut for the five-step architecture).
- "Judge" and "coach" may be named in steps 4 and 5 of the five-step explanation and in the fix beat.
- [RISK] is cut: no injury or risk wording anywhere.
- The footage was filmed on the creator's phone on 15 and 28 Aug 2026 and first analysed on 19-20 Nov 2026 (about
  three months later). Do not claim the clips sat "unwatched".
- The ending clip `tease_jd.mp4` shows the real posting screenshot: title "LMTS - Lead AI/ML Engineer (LLM
  Post-Training)", "India - Bangalore / India - Hyderabad", "Posted 6 Days Ago" (captured 20 Nov 2026), JR368314, and
  the verbatim line "This is a model-training role, not a wrapper around a hosted LLM".
- Garden-leave source tag for the screen: "People Matters, DNA · 19-20 Nov 2026 · not confirmed by Salesforce".

## v5 additions (creator, 20 Nov morning)
- Creator's build statement: Gym Jarvis has been built over months of weekends (series planning from Sept 2026: biceps
  progression agent 30 Sept; Ep 1 launch 12 Nov; Ep 2 meal analyser 16 Nov; Workout Analyser judge + coach built 19-20
  Nov). Allowed: "I spent months of weekends building Gym Jarvis/this system." Not allowed: "the analyser took months".
- Tease (sourced): Salesforce staff in India reportedly put on garden leave (19-20 Nov 2026 reports, not confirmed by
  Salesforce) while Salesforce is hiring "LMTS - Lead AI/ML Engineer (LLM Post-Training)" in Bangalore/Hyderabad.
  General pattern, sourced (eWeek 2026 tracker, National CIO Review, landing.jobs): companies cutting jobs while still
  hiring for AI roles. Allowed: "Many companies are doing the same: cutting jobs and hiring for AI." Say "AI engineers
  with post-training experience", not "AI scientists". "Firing" must be "reportedly letting people go" or similar.
- The architecture is now presented as 3 parts: SEE (pose + rep maths + can't-see refusal), JUDGE (Fable 5.2 vs my best
  rep), CHECK (coach, video only; both must agree). Same measured facts as above.

## Research pass (done 20 Nov 2026 evening, so the "I had Claude dig through research" line is true)
- Markerless pose estimation for resistance-training technique (arXiv 2608.24384): joint-angle estimates were most
  sensitive to CAMERA ORIENTATION; non-side (non-sagittal) views distort 2D angles. https://arxiv.org/pdf/2608.24384
- Smartphone camera positioning study (PMC12978916): squats and push-ups across 12 phone positions (3 angles x 4
  distances); camera angle and distance change detection and rep-count error. https://pmc.ncbi.nlm.nih.gov/articles/PMC12978916/
- Viewpoint-invariant rep counting (arXiv 2107.13760): counting reps from skeletons works well (MAE 0.06 reps).
  https://arxiv.org/abs/2107.13760
- ALEX-GYM-1 (2025) and FormCoach (arXiv 2508.07501): pose-based models are precise on joint relationships; vision
  models are better at context (equipment, the whole movement) -> supports using numbers (JUDGE) + video (CHECK).
- Allowed spoken summaries: "I had Claude dig through the research first." / "Counting reps is easy. Judging a rep is
  the hard part." / "One warning stood out: the camera angle can fool it." (then the lunge proves it)
- Which sets: the can't-see refusal fired on IMG_2652 (lying leg curl, knee), IMG_2655 (leg extension, knee),
  IMG_2657 (seated leg extension, knee), IMG_2658 (hip adduction, hip) -> "CAN'T SEE YOUR KNEE" on the leg extension is
  measured (verdicts.json). The 23 include IMG_2780, incline cable chest fly (28 Aug, red T-shirt): CONTINUE, "Fly
  range stays consistent". Exercises across the 23: chest (cable flies), back (lat pulldowns, seated rows, back
  extensions / side bends), legs (hack squat, lunge, leg press, curls, extensions, adduction/abduction, calf raise),
  core (reverse crunch, Russian twist).

## Research sweep (20 Nov 2026 evening; RESEARCH_SWEEP.md): 225 distinct sources (119 papers, 90 tools/repos/apps, 16 reviews)
- Allowed: "Claude went through over 200 papers and tools." (about 60 entries are thin; >160 without them)
- Supported: counting reps is mostly solved in controlled setups; judging form is hard (Fitness-AQA ECCV 2022: pose
  features cannot reliably detect subtle errors; FormCoach: best VLM caught 58% of real form issues); camera angle
  fools pose systems (MediaPipe accuracy highly dependent on viewing angle; JMIR mHealth 2026: squats 95.5% counted
  diagonal at 2 m vs 0% side at 90 cm).
- Spoken: "Counting reps is easy. Judging them is hard. And the camera angle can fool the agent."
