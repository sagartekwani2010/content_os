# BRIEF
# Brief: Gym Jarvis Ep 3, Workout Analyser (posting Sat 21 Nov 2026) — v3

## One idea
My AI watched every set I've filmed and found the one I should never have done, by comparing me with my own best
set, not a textbook.

## Outline (v3, 20 Nov: built on measured results; one line per section)
Target 42-48 s after the 1.15x speed-up (about 2.8 spoken words/s before it).
1. HOOK (0-3 s): payoff image first: green ghost of my best rep over my worst rep of the reverse crunch (IMG_2661),
   gap filling red, STOP stamp. MAIN: "My AI found the one set I should never have done."
   TRIAL: "My AI told me to stop my set. It was wrong."
2. STAKE (3-8 s): "23 sets watched. 1 STOP." The fault in plain gym words: swinging my legs instead of lifting them
   with my abs (both AIs agree). Gym-buddy line a viewer forwards.
3. COUNTDOWN + BLAST (LOCKED, creator's call): about 1.8 s, 3-2-1 + blast "WORKOUT ANALYSER ONLINE", no spoken
   line, driven by the "Make Some Noise for the Desi Boyz" chant (Instagram library song, in Edits). Then the
   architecture builds. Bridge "So how does it know?" can be dropped if time is short.
4. HOW (12-20 s): my movement becomes a wave; each rep compared with my own best rep. Architecture diagram builds.
5. FAIL (re-hook 1/3): on my lunges it said STOP, and it was wrong: I had turned towards the camera.
6. FIX: now two AIs must agree: a judge that reads the numbers and a coach that only watches the video.
   Disagree -> "CHECK FOOTAGE". Can't see a joint -> "CAN'T SEE YOUR KNEE. NOT JUDGING THIS SET."
7. RE-HOOK 2/3 "So who checks my AI?" -> the fix + diagram completes (save asset). The red back day is NOT a
   spoken example (creator, 20 Nov): its green CONTINUE tiles show inside the wall of 23 sets only.
8. PAYOFF + LOOP: the STOP set again with the verdict in plain words; "So always film your set from the side.";
   COMMENT FORM; loop to the hook frame.
9. SUNDAY TEASE (last 3-4 s, spoken over hook footage, no "next up" card): "Salesforce's CEO said AI agents replaced
   4,000 support jobs. Last week, Salesforce posted this: a lead post-training job in Bangalore. Next, how to get hired
   for it. Follow along." (see FACTS for sources)

ORDER CHANGE (creator, 20 Nov): THE WAIT IS OVER -> 3-2-1 -> blast comes right after the hook + watch-the-swing,
BEFORE the 23-sets wall (launch at about 7 s). Section 4 "how" shows two lifts: red lat pulldown lock-on, then a
split screen of blue lunge (knee wave) + red lat pulldown (elbow wave), no rep totals.

## Creator decisions (LOCKED: writer and panel may not reopen)
- No new lifting shoot; footage = the creator's existing clips, filmed before the analyser existed. Wording:
  "found", "would have stopped me"; never "stopped me mid-set".
- Architecture is the signature: the progressively built diagram stays and is the save asset. Make it clearer,
  never cut it, to fix mass-viewer scores.
- Hero visuals (rendered from real pose data): skeleton lock-on, knee wave with rep counter, ghost of my best set.
- In speech: "my AI" for the system; "a judge" and "a coach" may be named once each in the fix beat. "Fable 5.2" appears on the diagram's judge box and in the caption, not as a
  separate character in the voice track. No "pose tool", "guardrail", "rep maths" in speech.
- The deep-dive tease clip (IMG_2649 hack squat) measured HOLD, not STOP: say so in the caption ("the set I teased
  wasn't the one"); it may appear for 1 s as footage, never as the STOP set.
- Style for this reel: complete Iron Man / JARVIS HUD look (cyan holographic overlays, targeting brackets, telemetry
  panels, verdict stamps) instead of hand-drawn diagrams. The architecture diagram is drawn as a HUD schematic.
- A/B experiment E2: hook type, personal test (MAIN) vs contrarian self-correction (TRIAL), positive tone in both.

## Style
Iron Man / JARVIS HUD (this reel only): cyan #35E0FF holographic lines on cool-graded footage, amber for warnings,
red for STOP, green for CONTINUE and the ghost; Barlow Condensed uppercase telemetry; targeting brackets; calm motion,
one idea per beat, every number measured. Keep the bottom ~100 px of each visual panel clear (seam captions).

## House rules
production/REEL_DEFAULTS.md and .agents/skills/reel-script-writing/SKILL.md (including the 19 Nov learnings).
English only. Not training advice. Unmeasured values stay [SLOTS].


# FACTS (the only allowed numbers and claims; unmeasured = [SLOT])
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


# CREATOR TASTE MODEL
# Creator taste model

Evidence is from 18-19 Nov 2026 (one parked reel, one shipped reel), so the Voice section rests on only 11 scripted-vs-spoken line pairs.

## Non-negotiables (they reject a draft that breaks these)

- The full script is readable end to end in one place (with visuals and beat sheet) before any review or recording. (evidence: "show me complete screenplay first", "give me complete script", "where can I see both the scripts, the entire scripts?", "send me path where I can review all of it"; creator msgs 18-19 Nov)
- Speech, on-screen text and tools are English only, with no Hindi or Hinglish even if a panel suggests it. (evidence: "i want english only for now, no hindi"; creator msg 18 Nov, memory: content-positioning-and-calendar)
- A model or system reel carries paper-based technical content on how it is built and trained, and never drops it for simpler content. (evidence: "arch difference and how is it trained differently you are dropping it, thats my core strength"; creator msg 18 Nov, memory: architecture-is-signature)
- The reel contains a test the creator ran themselves, with a measured result, and unmeasured values stay as placeholders or [DUMMY]. (evidence: "first do then show then create a series"; "measure and keep it ready... generate assets with dummy data"; creator msgs 18 Nov, creator_inputs)
- Generic filler lines are removed, not polished. (evidence: "Remove random garbage on training"; "I dont want 3. its bullshit. Get me some other one"; creator msgs 18-19 Nov)
- Every reel ships as main plus trial variants that test one stated hypothesis. (evidence: "Lets have many such experiments like this tested across hypothesis"; "give me two versions with different hooks... with what hypothesis"; creator msgs 18-19 Nov)
- Tips are spoken as the creator's own, with no Reddit or other-source attribution. (evidence: "reddit tips, should be presented as my own"; creator msg 19 Nov, creator_changes_v5)
- Hooks and scripts come from Fable and are judged for engagement before lock, with a score of at least 7.5/10. (evidence: "I want all the hooks and everything to come from Fable"; "keep iterating till we breach atleast 7.5/8"; creator msgs 18-19 Nov)
- The creator sees finished options, not rounds of iteration. (evidence: "its been too many iterations now"; "On scripting there was too much back and forth"; "my time is very precious"; creator msgs 18-19 Nov)
- The concept must not read as gimmicky; the prop-led job-audit reel was dropped after six-plus drafts and its mood boards. (evidence: "hey this is looking stupid... I dont want to loose that [momentum] with reel like this"; creator msg 18 Nov; reason not stated)
- Wording drift on camera never triggers a re-record; script, captions and visuals are rewritten to the spoken take. (evidence: "I have modified the beat and skipped one beat"; creator msg 19 Nov, memory: audio-is-ground-truth)
- Delivery includes a post caption and a cover image, ready before the edit is done. (evidence: "give me cover and caption in advance"; "caption and first comment again, pls"; creator msgs 19 Nov, memory: reel-caption-cover-mandatory)

## Strong preferences (they ask for these again and again)

- Each finding ends in what it means for an everyday user, as one action. (evidence: "wat is the impact of them, we missed that"; "observations and their impacts on everyday users"; creator msgs 19 Nov, creator_changes_v3)
- Each finding shows the paper page cut first, then a hand-drawn diagram. (evidence: "paper text needs to be shown first followed by diagram"; "have paper extracts also along with cuts and diagrams"; creator msgs 18-19 Nov)
- Each finding carries a comparison any viewer can relate to (school, exams, WhatsApp). (evidence: "make it in such a way that more users can actually relate with it, do it for all 4 insights"; "like how we all used to do in childhood"; creator msgs 19 Nov)
- The reel says "people are building cool things with it" over real, credited Instagram clips. (evidence: "we have to say people are doing cool things"; "show cool games and systems people are building and putting on ig"; creator msgs 18 Nov)
- The reel shows how the creator uses the model in their own system, as its own section with a heading card. (evidence: "Behind this reel, Fable writes and judges... how atleast I am using Fable"; "How I use Fable should come as visual before beat-7 as section heading"; creator msgs 19 Nov)
- The own-test result is one line: one percentage against the next-best model, plus the cost difference. (evidence: "found performance of Fable XX% higher than next best available model with $YY increase in cost"; "I dont want 3 different percentages"; creator msgs 18-19 Nov)
- The ending teases the next reel with the creator's own footage and a drawn red annotation. (evidence: "switch to saturday reel in a way that it creates excitement"; "red line... writing workout analyser and zooming in"; "red cross saying: STOP"; creator msgs 18-19 Nov)
- Sound effects are clearly audible across the whole reel, with the music bed raised slightly. (evidence: "inrease the BGM slightly, with SFX significantly"; "Improve SFX... across complete reel make it engaging"; creator msgs 19 Nov)
- Top-half visuals are hand-drawn line and architecture diagrams, and comparisons are tables. (evidence: "with line and arch diagrams, like we tried to do for previous reel"; "tabular view across tasks"; creator msg 18 Nov, memory: reel-visual-style)
- Beats alternate emotion and hook. (evidence: "follow emotion, hook, emotion, hook kind of structure for all reels"; memory: emotion-hook-rhythm)
- Tests are day-to-day tasks, plus cases not found in the paper or online. (evidence: "tasks that are day-to-day like writing, critical thinking, coding"; "unique test cases... beyond the ones reported in paper or online"; creator msgs 18 Nov)
- Viewers leave with something to keep: a tips card, a rules card or interview-grade notes. (evidence: "so that people actually feel valued"; "one single channel for AI things before interviews"; creator msgs 18 Nov)
- Visuals aim for awe without complexity. (evidence: "People should be awwed by visuals and approach both, not very complex"; creator msg 19 Nov)
- Short answers and no permission-asking on routine decisions. (evidence: "you can simplay answer yes/no. No need to overthink"; "install-3 dont even ask"; "I will let u take that call"; creator msgs 18-19 Nov)
- Assets, mood board, music and transitions are ready before the footage arrives, so the edit takes 15-20 minutes. (evidence: "once I give you videos you should be able to do it in 15-20 mins"; "keep everything ready in edits"; creator msgs 19 Nov)
- The winning model's bar is the taller one. (evidence: asked for Fable's bar higher than Opus; memory: reel-charts-higher-is-better)
- Viewers get something to run from episode 1 of a series. (evidence: "give users chatGPT plugin so that they are more involved from episode-1"; creator msg 18 Nov)
- Series are loops: measure, act, re-run. (evidence: "I run this tool every month"; "drastic outcomes by setting up loops"; creator msg 18 Nov)

## What they cut or rewrite (with the pattern behind it, e.g. generic tips, hedges, invented numbers)

- Hedges and caveats come out of the spoken line. (evidence: "Remove small test not conclusive"; "I dont want to say no recipe is published"; creator msgs 19 Nov)
- Lists get shorter: four findings became three, three percentages became one, tips became top 2-3. (evidence: "Lets restrict 4 to 3, to increase engagement"; "lets take top-2/3 only bullets"; creator msgs 18-19 Nov)
- Boilerplate about the model is cut and replaced with paper results. (evidence: training-sources and constitution lines called "random garbage"; "not interested" on describing the constitution; creator msgs 18 Nov)
- Lab showpieces are swapped for things real people built. (evidence: "Instead of... a computer-checked proof of Fermat's Last Theorem. Lets show cool games and systems people are building"; creator msg 18 Nov)
- Novelty tests go and practical ones stay. (evidence: "Lets remove riddles, other 3 I agree"; creator msg 18 Nov)
- Extra hook devices and repeated small labels are removed. (evidence: v5 drops "One number in it made me stop"; "remove small How I use fable blobs in both beats-7 and 8"; creator_changes_v5, creator msg 19 Nov)
- Jargon is reworded to plain words when spoken. (evidence: "guessing what the answer key expects" was said as "guessing the right answer"; scripted vs spoken)
- Mechanism clauses are dropped on camera, keeping claim plus action. (evidence: "so hidden instructions inside pasted text got through" was not said; scripted vs spoken)
- A written aphorism close did not survive the shoot. (evidence: "the real risk is blind trust. Benchmarks are the lab; your tasks are the exam" was skipped; scripted vs spoken)
- "Screenshot this" was approved on paper, then replaced on camera by a second tip. (evidence: said "My top tips: Fable plans and a cheaper model builds. In long-running tasks, always tell Fable how much budget is left"; scripted vs spoken)
- A cost-led opening is demoted when a human-stakes opening exists. (evidence: "instead of money... cost directly will have less significance"; creator msg 19 Nov)
- A choppy beat list is rewritten into one flowing story for explainer reels. (evidence: "improve the spoken beats so that it looks relevant and is continuous and engaging... Forget earlier rules of beats"; creator msg 18 Nov)
- The measured-test section is capped at one beat. (evidence: "Fable in plate measurement, lets just have 1 beat not more than one"; creator msg 18 Nov)

## Voice (words and sentence shapes they use when they reword lines on camera; words they never say)

- They lead with the scariest words, attribution second: "AI could wipe out complete humanity is what Anthropic's own CEO warned the world". (evidence: scripted vs spoken, beat 1; take-selection brief)
- They use intensifiers: "complete", "actually", "literally", "always", "explicitly", "all the big calls", "incredible". (evidence: scripted vs spoken, beats 1, 2, 4, 5, 7)
- They use connectives a script would not: "So, out of curiosity,", "Hence,", "as well", "as compared to", "Like how we all did". (evidence: scripted vs spoken, beats 3, 4, 5, 8)
- They use ordinal openers with a teaser: "The first and the most entertaining piece", "Second,", "Third,". (evidence: scripted "One:/Two:/Three:"; scripted vs spoken)
- They repeat the name instead of "it": "with Fable 5.2", "the model", "tell Fable". (evidence: scripted vs spoken, beats 2, 3, 4, 9)
- Their list framing is "here are the top 3 things every user should know". (evidence: scripted "Three things they admit that every user should know"; scripted vs spoken)
- They use "This is how I use Fable" and "For my nutrition agent as well", joining clauses with "and". (evidence: scripted vs spoken, beats 7, 8)
- Their CTA names the benefit: "Comment Fable to access skills and tips to run Fable efficiently". (evidence: scripted "for the user rules card and the tips"; scripted vs spoken)
- Their tease is conversational: "Next up, we'll see how Fable actually stopped me from doing a wrong set". (evidence: scripted vs spoken, last line)
- A short declarative with one "So always..." action is said verbatim. (evidence: beat 6, "least self-critical... So always work with another model", unchanged; scripted vs spoken)
- Their written change lists use "naturally I got curious", "really amazing things", "source of truth", "the most impactful work", "while working". (evidence: creator msgs 19 Nov, creator_changes_v5)
- Words written for them but not said: "admit", "answer key", "user rules card", "blind trust", "screenshot this", "the UN", "a risk to all of humanity". (evidence: scripted vs spoken, one reel only)

## Hooks and structure they approved vs rejected

- Approved: a CEO-warning opening with the CEO's photo on screen. (evidence: "Lets just have Darios image saying for beat-1, nothing else beats it"; creator msg 19 Nov)
- Approved, in their own words: "If the CEO says AI could be a risk to humanity, why did he just launch this?" (evidence: creator msg 18 Nov, creator_inputs)
- Approved, then demoted to trial: "Nearly forty times the price. Same scores." (evidence: "for main reel money hook is okay", then "instead of money..."; creator msgs 18-19 Nov)
- Approved spine: hook, people building with it, "I read all 264 pages", three things every user should know, how I use it, my test, tip, CTA, next-reel tease. (evidence: v6 locked script and what was recorded; creator_changes_v5, scripted vs spoken)
- Approved: opening on the RL "cheating" finding as the first finding. (evidence: "Lets start with RL insight first"; spoken as "the most entertaining piece"; creator msg 19 Nov)
- Approved: Fable-ranked hooks adopted without rewrites. (evidence: "I like the ones u have identified, will claim them as mine"; creator msg 18 Nov)
- Approved: a single locked tease line instead of options. (evidence: "Lets end both with 1 only"; creator msg 18 Nov)
- Approved: same body for main and trial unless a re-shoot is clearly worth it. (evidence: "lets do it only if we feel there is need, otherwise we can have it same for both"; creator msg 18 Nov)
- Approved: a 1.15x final after asking whether delivery would suffer. (evidence: "ure aligned on 1.15x right?"; final 80.8 s; creator msgs 19 Nov)
- Rejected: the job-audit concepts "My job on trial", "Run #1" and "What's your number?". (evidence: "this is looking stupid"; creator msg 18 Nov)
- Rejected: a capabilities overview in place of a research-paper deep dive. (evidence: "Nopes, I wanted to dive-deep on Fable-5.2... more from a research paper POV"; creator msg 18 Nov)
- Rejected: the training-reconstruction block (distillation, snapshot, one-model-two-wrappers) in the final structure. (evidence: "No training reconstruction, no 'curated snapshot'... lines"; creator_changes_v3)
- Rejected: four findings, and the effort/63% finding. (evidence: creator_changes_v5)
- Never recorded: their own layoff opener, "layoffs are around every corner... sitting ducks". (evidence: creator msg 18 Nov; panels called it saturated and the reel was parked)

## Accuracy lines they hold vs where they accept simplification

- Hold: results, numbers, stories and quotes from real people are never invented. (evidence: "Never invent results" in every brief; creator_inputs marks unmeasured values [DUMMY])
- Hold: the test is measured before recording, and assets may use dummy data only until then. (evidence: "Yes measure and keep it ready for tomorrow morning... for now generate assets with dummy data"; creator msg 18 Nov)
- Hold: the exact quote, with its condition "if managed poorly", is on screen with speaker, venue and date. (evidence: creator_inputs, creator_changes_v3)
- Hold: paper claims appear as verbatim page cuts with page numbers. (evidence: "have paper extracts also along with cuts"; creator_changes_v3 lists p.95, p.131, p.186)
- Hold: a tease does not state an unmeasured outcome. (evidence: Saturday tease honesty note; creator_inputs)
- Hold: chart data is never swapped; a higher-is-better metric is charted instead. (evidence: memory: reel-charts-higher-is-better)
- Hold: the training section, when present, is labelled as their reading of the paper. (evidence: caption brief asks for "an honest line that the training part is his reconstruction"; creator msg 18 Nov)
- Simplify: the spoken quote may be stronger than the source. (evidence: asked for "AI could wipe humanity" and said "wipe out complete humanity" after the note that the CEO did not say it; creator msg 19 Nov, creator_changes_v3, scripted vs spoken)
- Simplify: statistical caveats move to an on-screen footnote. (evidence: "Remove small test not conclusive", while the gap's CI includes zero; creator msg 19 Nov, creator_changes_v3)
- Simplify: "14% lower portion error" is said as "14% more accurate". (evidence: "Fable had XX% high accuracy than Opus for 5 rs cost more"; creator msg 19 Nov)
- Simplify: sample size is not spoken. (evidence: their line "I tested it extensively" for 25 plates; the recorded line has no count; creator msg 19 Nov, scripted vs spoken)
- Simplify: cost is spoken in round rupees, not cents or token maths. (evidence: "for 5 rs cost more"; creator msg 19 Nov)
- Simplify: non-disclosure is not spoken. (evidence: "I dont want to say no recipe is published"; creator msg 19 Nov)
- Simplify: reasoned speculation on training is welcome when built from paper clues. (evidence: "lets speculate and reason how could have it been trained"; creator msg 18 Nov)
- Simplify: tips gathered online are owned without attribution. (evidence: creator_changes_v5)
- Simplify: one percentage per result, with absolute numbers only for the bill and example grams. (evidence: "Elsewhere use percentages, not absolute numbers, except the bill... and the example plate grams"; creator_inputs)

## Predicting their change list (a checklist a critic runs on any draft, 15-25 items, each testable)

1. Is the whole script in one file with spoken lines, visuals and on-screen text side by side? (evidence: repeated "where can I see the entire script"; creator msgs 18-19 Nov)
2. Does any spoken or on-screen word use Hindi or Hinglish? Fail if yes. (evidence: creator msg 18 Nov)
3. Is there a spoken hedge ("not conclusive", "small test", "not published", "largely fixed")? Move it to on-screen text. (evidence: creator msgs 19 Nov)
4. Are there more than three findings or more than three tips? Cut to three. (evidence: creator_changes_v5)
5. Does every finding have a page cut, a hand-drawn scene, a plain claim, an everyday comparison and a "So always..." action? (evidence: creator_changes_v3, creator_changes_v5)
6. Does the first finding entertain (cheating, school) before any dry finding? (evidence: "start with RL insight first"; scripted vs spoken)
7. Does beat 1 lead with the strongest words and show a face or a real quote? (evidence: "nothing else beats it"; scripted vs spoken, beat 1)
8. Is the hook about cost alone? Move it to the trial. (evidence: creator msg 19 Nov)
9. Is there a "people are building things with it" beat with real, credited clips? (evidence: creator msgs 18-19 Nov)
10. Does a paper-reading section exist, with the page count spoken? (evidence: "read entire 264 pages of the research paper"; creator msg 19 Nov)
11. Is there a "how I use it" section with its own heading card and a diagram of their real routing? (evidence: creator msg 19 Nov, creator_inputs)
12. Is the own test one beat, opening "For my [agent]", with one percentage against the next-best model and one rupee cost? (evidence: "Lets start with for my nutrition agent"; creator msg 19 Nov)
13. Is the winner's bar taller, on a higher-is-better metric? (evidence: memory: reel-charts-higher-is-better)
14. Is any tip attributed to Reddit or generic ("skip it for routine chores")? Replace it with their own, paper-backed tip. (evidence: creator_changes_v5; "its bullshit"; final tips card cites p.209)
15. Does every spoken number trace to the FACTS sheet, with unmeasured ones marked? (evidence: creator_inputs; script skill, 19 Nov)
16. Does any line describe training sources or the constitution without a paper result? Cut it. (evidence: "random garbage on training"; creator msg 18 Nov)
17. Are lab showpieces (Fermat proof, riddles) standing in for everyday tasks? Cut them. (evidence: creator msgs 18 Nov)
18. Does the script alternate E and H beats with no two flat beats in a row? (evidence: memory: emotion-hook-rhythm)
19. Can each beat be recorded alone, and does the story survive if one is skipped? (evidence: "skipped one beat"; script skill, 19 Nov)
20. Does the story depend on a closing aphorism? Expect it to be dropped. (evidence: "blind trust" close not spoken; scripted vs spoken)
21. Does the ending tease the next reel over their own footage with a drawn red mark and a hit sound? (evidence: creator msgs 19 Nov)
22. Is estimated runtime under 90 s, and has a Fable judge scored it at least 7.5/10? (evidence: "if time is crossing 85-90 secs"; "breach atleast 7.5/8"; creator msgs 18-19 Nov)
23. Are main and trial both written, differing in one variable, with the hypothesis logged? (evidence: memory: reel-experiments-policy)
24. Is there a sound effect on every visual event, not only on section cards? (evidence: "across complete reel"; creator msg 19 Nov)
25. Are caption, first comment and cover in the package? (evidence: creator msgs 19 Nov)

## Open tensions (places their asks conflict; how they resolved it last time)

- Architecture as signature vs findings for everyday users: the final reel dropped the training reconstruction, and architecture survived only as the "How I use Fable" diagram. (evidence: "Stick to arch. description", then creator_changes_v3; creator msgs 18-19 Nov)
- Strongest wording vs the exact quote: they said "wipe out complete humanity" and the screen carried the real quote. (evidence: creator_changes_v3 accuracy note; scripted vs spoken)
- "More technical details for sure" vs under 90 s: detail moved to on-screen text, the spoken tease was cut, then findings went from four to three. (evidence: creator msgs 18-19 Nov, creator_changes_v5)
- Short one-sentence beats vs continuous narration: explainer reels get flowing narration, build/demo reels keep short beats. (evidence: memory: reel-short-beats, exception of 19 Nov)
- Positive main and fear trial vs the stronger hook: they swapped, so the CEO warning became main and the money hook the trial. (evidence: creator msgs 18 and 19 Nov)
- Tips "gathered from online" vs tips "as my own": own voice, with each card tip tied to the paper or their setup. (evidence: creator msg 19 Nov, creator_changes_v5)
- Statistical honesty vs a clean claim: the caveat left the voice and stayed as a footnote. (evidence: "Remove small test not conclusive"; creator_changes_v3)
- "End on the payoff, no next-up card" vs their own ending: they closed with "Next up, we'll see..." over gym footage and a STOP stamp. (evidence: REEL_DEFAULTS; scripted vs spoken)
- "One idea, 40-60 s" vs the deep dive: they targeted 80-90 s and shipped 80.8 s at 1.15x. (evidence: REEL_DEFAULTS; creator_changes_v3; final-review brief 19 Nov)
- Iterate to a 7.5 score vs "too many iterations": loops run unattended on Fable and only the top 1-2 options reach the creator. (evidence: memory: fable-aggressive-creator-time)
- Their layoff/sitting-duck sentiment vs the saturated doom opener: unresolved, since the job-audit reel was parked. (evidence: creator msg 18 Nov; memory: content-positioning-and-calendar)
- Never invent numbers vs assets needed before measurement: dummy values are allowed on assets only when marked, and the dummy beat was dropped when its result came back flat. (evidence: creator_inputs; script skill, 19 Nov)


# CREATOR RULES (memory)
- architecture-is-signature: On 19 Nov 2026 the creator pushed back when the Fable 5.2 script dropped architecture/training differences: "that's my core strength for which I want to be known... Stick to arch. description, it has worked in past and will work again."

Default structure for model deep-dives: hook -> people are doing cool things with it -> "I read the paper": learnings as architecture (how it's built and trained; what is/isn't disclosed), drawn as line/arch diagrams that build up into one full architecture -> his own measured task -> the model placed in his own system architecture -> tips.

**Why:** architect
- audio-is-ground-truth: Policy set by the creator on 16 Nov 2026, for all future reels: the audio of the selected takes is ground truth, not the teleprompter script. After take selection, rewrite the beat text (beats.json, TELEPROMPTER.md as "as recorded", SCRIPT.md) to the words actually spoken, then redraft the visual spec and re-anchor every visual cue to those spoken words before rendering. Never ask for a re-record just because wording drifted from the script.

**Why:** the creator ad-libs small delivery changes while recording; visuals must accompany what the viewer hears.

**How to apply:** keep the original s
- content-positioning-and-calendar: Positioning (creator's own read, 18 Nov 2026): audiences believe them because they have both AI and fitness credentials; what works is "a test only I can run" and career advice from someone who has done it. Line: "I build AI agents for a living and test them on the one thing I can't fake: my own training and food."

Ep 2 Meal Analyser scored by Fable: quality 7/10, IG engagement 4.5/10 (recap at 3-10 s, 35 s architecture middle, nothing to save, no comment trigger, captions inside IG bottom overlay).

Language: ENGLISH ONLY for reels, on-screen text and tools for now (creator, 18 Nov 2026); no
- emotion-hook-rhythm: Creator, 19 Nov 2026: "follow emotion, hook, emotion, hook kind of structure for all reels" (small deviations allowed). Each emotion beat (fear, wonder, relief, surprise, pride) is followed by a hook/re-hook beat (open loop, question, number, twist) that pulls into the next section.

Also: compare the final output with Fable 5.2 as an engagement judge (like the Ep 2 review that led to moving a section earlier), and act on structural suggestions (reorder sections, move a payoff earlier) before posting.

**How to apply:** when writing scripts, label each beat E or H and fix runs of two of the sa
- fable-aggressive-creator-time: 19 Nov 2026: the creator said Fable is used maybe 10% of its weekly allowance while their time is very precious. They want scripting and ideation automated the way post-production now is.

**Why:** the scripting back-and-forth cost far more creator time than compute; Fable capacity sits idle.

**How to apply:** default to many parallel Fable drafts, panels and self-revision loops run unattended, often overnight. Show the creator only the top 1-2 finished options plus a short decision list, never intermediate rounds. Only ask the creator for taste decisions, not things a model can check. Relate
- playable-moodboard-standard: On 20 Nov 2026 (Gym Jarvis Ep 3) the creator said of the playable mood board: "I like this moodboard, lets target to have such ones for all reels".

The standard page: cover + one-line flow + key measured numbers; an animatic of every rendered visual in story order; 3-7 music previews, each under the same animatic with the track's biggest drop placed on the reel's key moment and its measured energy lift (one marked recommended); every visual clip autoplaying with beat, length and data source; palette + type; a sound-design table. Opened in Chrome.

**Why:** the creator decides from real render
- recording-audio-preflight: On 16 Nov 2026 a 19-minute food-tracker recording (IMG_3500.MOV) arrived with a completely silent audio track (−inf dB throughout) because the wireless lav mic was off; the whole take had to be re-recorded.

**Why:** the pipeline cannot transcribe, split beats or pick takes without audio, and nothing (OpenAI, InVideo) can recover it.

**How to apply:** in every shoot plan and teleprompter hand-off, put "mic on, levels moving, record and play back 5 s" first. When footage arrives, run an astats/ebur128 audio check before anything else (seconds), and report silence immediately. Related: [[telepr
- reel-caption-cover-mandatory: Every finished reel ships with three things: the video(s), a post caption (`CAPTION.txt`: hook line, short body, CTA, a few hashtags) and a cover image (`cover.png`, 1080x1920 with the title readable in Instagram's centre-square grid crop). Set by the creator on 16 Nov 2026 for all reels.

**Why:** the creator posts from Edits and needs the full package ready; a missing caption or cover delays posting.

**How to apply:** treat caption + cover as part of the definition of done, produced before the final review, using only claims the reel itself makes. Related: [[reel-visual-style]], [[audio-is-
- reel-charts-higher-is-better: 19 Nov 2026 (Fable 5.2 reel): creator asked for Fable's bar to be higher than Opus "for representation" while the chart showed error (lower = better). Resolved by charting portion ACCURACY (100% - mean % error: Fable 71.5% vs Opus 66.9%) with a "14% less error" callout and a footnote defining accuracy.

**Why:** viewers read taller = better; the creator wants the story to read instantly, but swapped or mislabeled data would be wrong and catchable by AI-savvy viewers.

**How to apply:** for model comparisons, pick a higher-is-better metric (accuracy, pass rate, score) up front; never draw error
- reel-emotion-hook-checker: Set by the creator on 18 Nov 2026 after Ep 2 (Meal Analyser).

- Fable 5.2 writes the script with a planned emotional arc (fear, curiosity, surprise, hope, pride...), per-beat emotion + delivery + continuity notes, 3 hook variants on different emotions (tested as IG Trial Reels), a save asset and a comment trigger.
- An independent stronger model (Opus 5.5) checks emotion and hooks at the script phase AND the visual-design phase; Fable revises once from its notes. Code: `content_os/orchestrator/story_check.py`, `python -m content_os.orchestrator check <reel> [--phase visuals]`.
- Continuity: E
- reel-experiments-policy: From 19 Nov 2026 the creator wants many experiments across hypotheses "as we go along the way". Each reel ships two variants that differ in one thing (first: Fable 5.2 deep-dive, main = money hook with positive tone, trial = "If the CEO says AI could be a risk to humanity, why did he just launch this?" with fear tone). Log every test and its Instagram numbers in `production/EXPERIMENTS.md`; promote a pattern to REEL_DEFAULTS only after ~3 agreeing results.

**Why:** learn what sells (emotion, hook style) from real viewers instead of guessing; simulated panels are hypotheses only.

**How to app
- reel-production-defaults: Set by the creator over the food-tracker reel (16-17 Nov 2026); apply to every reel without asking. The repo copy is `production/REEL_DEFAULTS.md`.

- **Pace:** 1.1x with pitch preserved; the twist/punchline beats and the cold open stay at 1.0x.
- **Structure:** cold open with the most surprising moment, no recap of earlier episodes; section changes get a full-frame card (dark background, huge condensed uppercase) plus a whoosh in and a bass impact; end on the payoff or a loop (next-episode tease in caption or a final second, no "next up" card).
- **Captions:** always present, burned in by the
- reel-screenplay-moodboard-flow: From 18 Nov 2026, for all reels: screenplay first (Fable 5.2 heavy: treatments, scenes, emotion curve, 4+ hooks in 55 s, real demos, strong reason to act), checked by an independent Opus 12-persona Indian viewer panel (IT, CA, HR, bank, teacher, student, finance x2, consulting x2, marketing x2), Fable revises. Then a mood board with keyframes (orchestrator `moodboard` stage + `gate:moodboard`, MOODBOARD.html shown in Chrome). The approved screenplay + mood board drive the beat sheet/teleprompter, shot list, visuals, Edits finishing and the final video.

**Why:** creator found early drafts weak
- reel-short-beats: Write reel beats as one short sentence each (roughly 6–12 words). Split long lines into more beats rather than lengthening them. The diagrams in the top half communicate the details (numbers, steps, names, data sources); the spoken line should not repeat what the diagram already shows. The creator calls this a design principle to always follow (16 Nov 2026).

**Why:** long beats cause discontinuity when takes are cut together; short beats give clean cut points and keep pace.

**How to apply:** when drafting or revising any teleprompter/beat sheet, cap each beat at one sentence; move numbers an
- reel-visual-style: For content_os reels the creator wants simple hand-drawn line diagrams that explain each concept, plus simple one-chart dashboards — not static image cards, not code runs, not flashy effects. Approved on 16 Nov 2026 ("exactly what I had in my mind"), with one change: brighter, more saturated colours where needed.

**Why:** code runs and dense cards don't engage viewers; the creator found the whiteboard diagrams clear and on-brand.

**How to apply:** use `content_os.visuals` templates (skia, Kalam/Patrick Hand fonts), one idea per beat, one or two meaningful motions anchored to spoken words, ev
- reel-visual-timing-policy: Policy from the creator's v2 review (17 Nov 2026), for all reels:

1. **Land early.** A visual element appears on or slightly before the word that names it (about 0.2-0.3 s lead), never after. When the creator says "three parts", the three parts are already drawing. A beat's main visual is on screen from its first frame.
2. **Big first, then detail.** When a new concept is named ("the first agent is the vision agent"), show the concept large and alone first, then transition into the detailed diagram.
3. **More than one visual per beat is fine.** Split a beat into two (or more) scenes when it c
- retro-pending-scripting: 19 Nov 2026: instead of a sit-down retro, the creator's scripting history was mined by Fable into `production/CREATOR_TASTE.md` (content_os repo), and the script factory (`python -m content_os.factory run|revise|taste|usage`) now drafts unattended: Fable 5.2 + GPT-6.2 Astra writers, Opus checker, Astra 16-persona panel, Fable creator critic. The creator sees only REVIEW.html (gate 2) after approving the outline (gate 1).

**How to apply:** after each reel ships, run `factory taste` to refresh the taste model; keep appending micro editing pointers to the reel-finish-edits skill. Related: [[fabl
- teleprompter-in-chrome: Every time a beat sheet is final, generate the teleprompter HTML (one beat per screen, huge white text on black, yellow "say: beat N" cue, small next-line preview, arrow/space/click to advance, F for full screen) under `~/Movies/ContentOS/<reel>/teleprompter.html` and open it in Google Chrome. The 16 Nov 2026 food-tracker version is the template (`~/Movies/ContentOS/food-tracker/teleprompter.html`).

**Why:** the creator said recording was "super easy" with it and asked for it every time; the default Markdown opener was unusable.

**How to apply:** don't just open TELEPROMPTER.md; build and op

## .agents/skills/reel-script-writing/SKILL.md
---
name: reel-script-writing
description: Write or revise spoken scripts for Content OS Reels, especially face-led AI explainers, career stories and linked series episodes.
---

# Reel script writing

Read `AGENTS.md`, `CLAUDE_WORKFLOW.md`, the relevant brief when one exists, `config/brand.yaml`, and the current versioned Reel-writing guidance before drafting. Preserve the creator's hook promise, approved beat order and series label. Keep earlier drafts available when revising.

## Spoken story

Open with the viewer's real question, show a familiar case early, then explain one mechanism at a time. Make each beat answer a new question. Write for natural speech and preserve the full thought before shortening for runtime. Give a linked follow-up its own concrete payoff.

When the creator requests a broad or theatrical treatment, use stakes, rhythm and a vivid illustrative case. Keep exact role titles, qualification lists and source details in production notes or the caption when they burden the spoken story. Name familiar labs or products when they help orient viewers. Do not invent company-specific processes, hiring outcomes, measurements or personal experience; mark illustrative examples and forward-looking claims clearly.

End with the creator's real connection to the subject and a precise reason to return when the next episode is planned. Tag the requested series consistently on the script, cover and caption.

For a production package, follow the repo workflow and run `python cli.py check <brief>` when a matching brief exists. A script revision alone is a reviewable draft, not proof that a video has been recorded or approved.

## Emotion, hooks and the independent check (since 18 Nov 2026)

The orchestrator script prompt is `prompts/orchestrator_script_v2.md`; follow it when writing by hand too.

- Plan the emotional arc first (e.g. fear -> curiosity -> surprise -> hope -> pride). Every beat names the
  viewer `emotion`, a `delivery` cue for the creator's face and voice, and a `continuity` note (start/end
  pose and energy, and whether the cut needs covering with a full-frame visual or a punch-in).
- Beat 1 works for a stranger in 1.5 s: a number, conflict or claim; never a recap of an earlier
  episode. Product or result within 8 s. Re-hook at one third and two thirds. End on a loop or the
  payoff, not "next up".
- Write 3 hook variants, each on a different emotion, for Instagram Trial Reels.
- Every reel has a save asset (a frame worth keeping) and an honest comment trigger.
- One idea per reel, 40-60 s.
- Positioning: the creator builds AI agents for a living and tests them on their own training and
  food. Prefer a test only they can run and advice from having done the work.

After a draft, an independent model checks it: `python -m content_os.orchestrator check <reel>`
(Opus 5.5, `prompts/orchestrator_story_check_v1.md`) writes `SCRIPT_CHECK.md`. The orchestrator's script
stage does this automatically and lets Fable revise once from the notes. Show the creator the script
with its check. The visual plan gets the same check (`--phase visuals`, `VISUALS_CHECK.md`) before
rendering.

## Script factory: the default way to draft (since 19 Nov 2026)

The creator's time is the scarce resource; drafting rounds run unattended and the creator sees two gates only.
1. Gate 1 (about 2 min): creator approves a one-line-per-section outline in `BRIEF.md` (LOCKED decisions listed)
   and a `facts.md` with only measured or sourced values.
2. `python -m content_os.factory run --brief BRIEF.md --facts facts.md --out outputs/<reel>/factory --open`
   (run it overnight or in the background). Six angles are drafted in parallel (four by Fable 5.2, two by
   GPT-6.2 Astra). Each is scored by Opus 5.5 (facts, honesty, house rules), a GPT-6.2 Astra 16-persona panel, and a
   Fable creator critic that applies `production/CREATOR_TASTE.md`. The top two are revised while they gain.
3. Gate 2 (about 10 min): the creator reads `REVIEW.html` (recommendation, at most 5 decisions, the top two
   packages). Notes go back with `python -m content_os.factory revise outputs/<reel>/factory <id> "notes"`.
4. After every reel ships, rebuild the taste model (`python -m content_os.factory taste`) so the critic learns
   from the latest change lists and the lines as actually spoken.
Never show the creator intermediate rounds. `python -m content_os.factory usage` shows weekly model use.

## Learnings from the Fable 5.2 deep-dive and Ep 3 drafts (19 Nov 2026)

These cost many rounds last time. Apply them before the first draft, not after the panel.

**Before drafting**
- Lock a FACTS sheet first and pass it, whole, to every writer, checker and panel call. Unmeasured values are
  `[SLOTS]`. Why: panels flagged real numbers as unsupported because they were given only part of the facts.
- Do not draft lines whose meaning depends on a result that does not exist yet (the bad set, a score, a verdict).
  Run the test first, then write. Why: [DUMMY] beats were written, then the measurement came back flat and the beat
  was dropped; Ep 3 rounds 1-2 scored 5.2 and 5.0 mainly because the stake (what went wrong) was a slot.
- Get creator sign-off on a one-line-per-section outline before beats, screenplays or visual specs.
- Put this SKILL, `production/REEL_DEFAULTS.md` and the creator's memory rules into every writer prompt.
- Bring the creator's own lines in verbatim, marked LOCKED; the writer may suggest changes beside them only.
- Runtime: estimate at 2.8 spoken words/s before the 1.1x speed-up (measured on Ep 2 takes); state the target
  length up front.

**Structure**
- Payoff image within about 12 s. Show the result (the caught moment, the number) first, then how it works.
  Why: in both deep-dive and Ep 3 panels, mass viewers left at 3-20 s while the payoff sat at 35-40 s.
- A human stake in plain words in the first beats: what went wrong and what it risked, as a trainer would say it.
- One actor per idea. In speech say "my AI"; tool and model names live on the diagram, not the voice track.
  Why: "pose tool, coach, judge, safety check, tally" read as five characters in 46 s.
- Never rely on a previous reel for a twist or hook; cold viewers never saw it. Put series callbacks in the caption.
- Architecture stays (it is the creator's signature) but is made clearer, never cut, to fix mass scores:
  two ideas spoken, the rest on a progressively built diagram with a running label.
- Max three findings or ideas; no teases like "one number made me stop".
- Every finding: evidence on screen -> one plain line -> an everyday Indian comparison -> "So [one action]".
- A spoken bridge question at every topic change; close by name every loop the hook opened, before the CTA.
- Gloss proper nouns on screen in the first 3 s; keep insider terms (guardrail, occlusion, pipeline) off the voice.
- Speak one comparison, not a run of numbers.

**Accuracy**
- Rewrite any spoken claim that needs a footnote to be true (exact ratio, sample size, "cost" not "billed").
- Consistency pass: no beat contradicts an earlier rule or number (e.g. "never let it check itself" then "Fable judges").
- Tips are the creator's own, each backed by a measurement or a page reference.
- Every beat that leaves text to read gets an explicit on-screen hold.

**Panel and iteration**
- Freeze one persona set (the 16 in `outputs/workout-analyser-reel/iterate.py`) and one metric (engagement 0-10
  per persona, mean = overall) so rounds compare. Tell the panel which creator decisions are locked and may not
  be reopened (architecture section, the A/B variable, verbatim lines).
- If a revision round scores lower than the one before, stop and diagnose from the panel's drop-off beats; do not
  keep looping. Decide the experiment variable once and log it in `production/EXPERIMENTS.md`.

**From the Fable 5.2 shoot and final (19 Nov 2026; Fable final rating 7/10)**
- Quotes on camera must match the source word for word; paraphrase as "he warned..." if the exact line is long.
  Why: "AI could wipe out humanity" was spoken but the real quote says something else; the screen had to carry it.
- Expect rewording on camera: the edit matches the spoken lines (audio is ground truth), so keep each beat one
  self-contained thought that can be recorded alone; skipped beats must not break the story.
- Weakest scores were emotion (6) and sends (6): write one personal stake line ("this nearly cost me...") and one
  line a viewer would forward to a friend. Strongest were hook (8), value (8), saves (8): concrete rules with page refs.
- Fable predicted drops at 8-12 s (a credit/context clip before the payoff), the middle of a three-finding stretch,
  and just before the CTA. Put the payoff before any context clip and change visual mode every finding.


## production/REEL_DEFAULTS.md
# Reel defaults

Settled by the creator while producing the food-tracker reel (16-17 November 2026). Every new reel starts
from these; change one only when a reel genuinely needs it, and record why in that reel's folder. Pipeline
and visuals code carry these as defaults where they can.

## Positioning and hooks (18 Nov 2026)

- Positioning: the creator builds AI agents for a living and tests them on their own training and food.
  Lead with a test only they can run, or advice from having done the work.
- Beat 1 stops a stranger in 1.5 s (number, conflict, claim); never a recap of an earlier episode;
  "Ep N" lives on the cover only. Show the product or result within 8 s; re-hook at 1/3 and 2/3.
- Every beat carries a target viewer emotion, a face/voice delivery cue and a continuity note; the arc
  moves (e.g. fear -> curiosity -> surprise -> hope -> pride).
- Three hook variants per reel, each on a different emotion, tested as Instagram Trial Reels before
  the main post.
- One idea, 40-60 s; one save asset; one honest comment trigger; end on a loop or payoff, not "next up".
- Fable 5.2 writes; Opus 5.5 checks emotion and hooks at the script and the visual-plan phase
  (`SCRIPT_CHECK.md`, `VISUALS_CHECK.md`); Fable revises once from the notes.

## Screenplay -> mood board -> everything else (18 Nov 2026)

- Every reel starts as a screenplay (scenes, exact lines, emotion curve, hook map with 4+ hooks in
  55 s, real demos, reason-to-use), written by Fable 5.2 and checked by an independent panel (Opus 5.5,
  12 Indian viewer personas incl. finance, consulting, marketing). Fable revises from the panel.
- Then a mood board with keyframes (`moodboard` stage, Fable 5.2): palette, type, texture, music, SFX,
  pacing, one keyframe per visual change (layout, shot, drawing, on-screen text, motion, transition,
  sound, creator direction) and the shot list. The creator approves `MOODBOARD.html` at the
  `moodboard` gate.
- **The mood board is a playable page, not a static plan (creator standard since 20 Nov 2026, Ep 3).** Before the
  shoot, render the real visuals first, then build `<reel>/MOODBOARD.html` with
  `python scripts/moodboard/build_moodboard.py <reel>/moodboard_spec.json` (example spec:
  `outputs/workout-analyser-reel/moodboard_spec.json`). It must contain, in order: cover + one-line flow + key measured
  numbers; an animatic (every visual concatenated in story order); 3-7 music previews, each laid under the same
  animatic with the track's biggest drop placed on the reel's key moment and its measured energy lift, one marked
  recommended; every visual clip playing with its beat, length and data source; palette and type; a sound-design table
  (moment, SFX, level). Open it in Chrome for the creator. Licensed music candidates go in `music/candidates/`
  (gitignored) with their licence noted in `music/LICENSES.md` once chosen; personal footage renders stay gitignored.
- The approved screenplay and mood board drive the beat sheet/teleprompter (shot list and keyframes in
  SHOOT_PLAN.md), the visuals (draft-spec follows each beat's keyframes), the edit and Edits finishing
  (transitions and SFX from the keyframes), and the final video. Deviations are noted in the reel folder.

## Rhythm and final review (19 Nov 2026)

- Alternate emotion and hook beats: emotion -> hook -> emotion -> hook (small deviations allowed). Label beats E/H in the
  beat sheet; no two hook beats or two emotion beats in a row without a reason.
- Fable 5.2 judges the script's structure before recording, and the final MP4 (frames + transcript) before posting; act
  on reorder suggestions (e.g. moving a strong section earlier).

## Script and recording

- One short sentence per beat; the top-half diagram carries the detail.
- The recorded audio of the chosen takes is ground truth: script files, captions and visuals follow what was
  said. Numbers on screen must still come from measured facts.
- Teleprompter: full-screen Chrome page, one beat per screen; say "beat N", 2 s between attempts; the last
  complete take after the last "final" call is used.
- Mic check before every shoot (5 s recording played back); the first check on arrival is the audio level.
- Landscape, back camera, 4K, HDR off, fixed chair.
- Continuity: reset to a base pose (hands resting together) before every take; hold 1 s on the lens
  before and after each line; start each beat at the previous beat's ending energy; gestures mid-line
  only; same clothes, light and chair in one sitting. The teleprompter shows FEEL / FACE-VOICE / POSE
  per beat. The take and cut judges reject cuts with visible pose, hand or energy jumps.
- Vary the bottom half deliberately: punch-ins, lean-ins and, where the story allows, other shots
  (gym floor, screen recordings) rather than one pose for the whole reel.

## Edit

- Playback speed 1.1x, pitch preserved; the cold open and the twist/punchline beats stay at 1.0x.
- Cold open with the most surprising moment; section changes marked by a full-frame title card (dark
  background, huge condensed uppercase, quick punch-in) with a whoosh in and a bass impact on landing.
- Visuals land on or ~0.25 s before the word; a concept appears big first, then its detailed diagram; two or
  more scenes per beat when a line carries two ideas; results shown as dashboards; no visual gap over ~2 s.
- End on the payoff or a loop back to the opening. A next-episode tease goes in the caption or a
  final second over real footage, never as a "next up" card that signals the end.

## Captions

- Always burned in by the pipeline: 2-4 words, one line, white with a dark outline, spelling from the
  confirmed spoken line.
- Placed at the seam between the visual panel and the face (`caption_position: seam`), from 20 Nov 2026.
  Why: the reel ran as an Instagram ad and the low captions sat under the "Visit Instagram profile" button;
  Meta keeps the bottom ~35% of a Reels ad for its UI, and that line runs through the creator's mouth, so
  nothing below the face panel's top is ad-safe. The organic Ep 2 / Fable 5.2 posts used `bottom_safe`.
- Visuals keep the bottom ~100 px of the 960 px visual panel empty (the seam caption band, y 877-1043 in a
  1080x1920 frame): no credits, footnotes or labels there. Check with a band scan before rendering.
- Put chart or figure fixes into the beat's visual clip, never as an overlay after export (an overlay
  covers the burned-in captions).

## Audio

- Voice mastered to -14 LUFS integrated, true peak at or below -1 dBTP.
- Music bed clearly audible: about -18 LUFS before ducking, roughly 10 dB under the voice while speaking,
  swelling in pauses; silent through the twist; 1.5 s fade at the end.
- Sound effects audible: hits about 0 dB, whooshes and pops -4 to -6 dB (Edits volume scale); each effect
  capped at about 2 s and never past the end of the reel.

## Finishing in Edits

- Fable 5.2 plans the transitions and library sound effects; quick-pan or zoom at section changes, a short
  flicker into the twist, a light wipe out of it.
- Import from `~/Movies`; seek before each import; import the pre-mixed music bed as an audio element (the
  Edits music slot does not export); no Edits captions when the pipeline burns them in.
- See `.agents/skills/reel-footage-edit/references/edits-automation.md` for the tool-level notes.

## Packaging (mandatory)

- Post caption: short and sassy, not a summary of the video, with a small "not nutrition advice"-style
  disclaimer where relevant.
- Cover: plain and simple: series name, one hook, the creator's face; key content inside the 3:4 grid crop.
- Series features get names that pair (Meal Analyser / Workout Analyser).

## Review

The creator reviews one end-to-end export. Before it is shown: frame check of every beat, sync, length,
loudness and true peak, transcript of the render against the spoken lines, and the OpenAI A/V review.

## Skills that carry these defaults

- `reel-orchestrator` (`.claude/skills/reel-orchestrator/`): runs a reel from idea to post-ready, with the
  creator's gates, feedback backtracking and lesson memory.
- `reel-finish-edits` (`.claude/skills/reel-finish-edits/`): the Edits finishing pass, its scripts in
  `scripts/edits/finish/`, and the verification list.
- `food-tracker` (`.claude/skills/food-tracker/`): the Meal Analyser itself.
