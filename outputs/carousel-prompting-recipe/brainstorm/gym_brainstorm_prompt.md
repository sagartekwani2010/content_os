# THE JOB
An Instagram carousel (~12 slides, hand-drawn light paper style) for an Indian AI practitioner who builds AI agents and
tests them on his own gym training and food ("Gym Jarvis"). Posts Mon 23 Nov 2026, 13:00 IST. Series: the Playbook
(prompting today -> guardrails Wed -> evals). It teaches 8 DIFFERENT PROMPTING TECHNIQUES, one per slide, each with a
copy-ready line and a REAL before -> after AI run (same model, verbatim, trimmed). Ends with a one-page cheat sheet
(the save) and a comment-keyword CTA that DMs the full cheat sheet plus a combined prompt template.

# CREATOR RULE (new, binding)
Analogies come ONLY from the gym / fitness world (the creator's own world and his audience's), with AI building and
careers allowed as secondary. No kitchens, tailors, cricket, weddings, exams. Every concept must be explained through a
real gym / real-life example a non-technical Indian viewer gets in one read. No jargon. English only on screen.

# TECHNIQUES (chosen by a blind judge in an earlier round)
1 context (who it is for, what they care about) 2 constraints (must / must not) 3 few-shot examples ("here are 2
examples of what I want") 4 output format (table / bullets / length) 5 prompt chaining (split a big ask into steps,
check between steps) 6 clarifying questions ("ask me up to 3 questions before you start") 7 say "I don't know" /
don't guess ("use only what I told you; write [ASK ME] instead of inventing") 8 show your working + self-check
(honest: on a modern model this makes the answer checkable, not more correct).

# LESSONS FROM THE EARLIER ROUND (blind judge)
- A gym-trainer framing scored low (5.6/10) because ROLES FLIPPED: the client briefed the trainer for some techniques and
  the trainer instructed the client for others. Pick ONE fixed casting for the whole carousel (who is "you", who is
  "the AI") and keep it on every slide. Say it in one line on slide 2.
- Mappings must be literal, not forced: "a logbook" is a record, not reasoning; an end-of-week review is not checking
  before delivery; output format must not blur into constraints.
- The before -> after must visibly differ on a modern model. Pilot runs (claude-fable-5-2, each twice): context, constraints,
  output format (a table), clarifying questions ("weekly workout plan" -> 3 questions) showed clear differences; simple
  maths and "exactly 40 words" showed no difference with or without step-by-step / self-check.

# AUDIENCE
Panel (Indian Instagram viewers scrolling at 10 pm, English only): 1 TCS support engineer Pune 24; 2 CA Ahmedabad 31; 3 HR exec Bengaluru 28; 4 bank RM Lucknow 35; 5 school teacher Jaipur 38; 6 BTech final-year Hyderabad 21; 7 FP&A analyst Gurgaon 25; 8 IB/equity research associate Mumbai 33; 9 Big 4 consulting analyst Bengaluru 24; 10 strategy consulting manager Mumbai 32; 11 performance marketing exec Delhi 26; 12 FMCG brand manager Mumbai 34; 13 startup backend dev Bengaluru 27; 14 ML engineer Hyderabad 30; 15 gym trainer Delhi 29 (non-tech); 16 BCom student Kolkata 20. Groups: mass 2-5,12,15,16; fin-consult-mktg 7-12; builders 1,6,13,14.

# YOUR TASK
1. At least 4 DIFFERENT gym framings for the whole carousel (different castings or structures inside the gym world,
   e.g. who plays the AI: a new personal trainer, a new gym buddy, a coach writing your program, a spotter...). For each:
   name, casting (you = ?, AI = ?), 3 cover hooks, technique -> gym move (one line each, literal), save/share reason,
   and a gym-fitting comment keyword for the CTA.
2. For EACH technique, 3 gym / real-life examples: the everyday gym moment (one line) + a real AI task for the run:
   the exact BEFORE prompt and the one line ADDED in AFTER (everything else identical), chosen so the difference will
   be visible in the output. Fitness tasks preferred (workout plan, form cue, diet for a goal, progress check, gym bag,
   supplement question); 1-2 everyday/career tasks only where they show the technique better. Keep prompts short.
Reply with JSON only:
{"framings": [{"id": str, "name": str, "casting": str, "hooks": [str,str,str], "mapping": {"<technique>": str},
  "save_share": str, "keyword": str}],
 "examples": {"<technique>": [{"gym_moment": str, "task": str, "before_prompt": str, "added_line": str,
  "expected_visible_difference": str}]}}