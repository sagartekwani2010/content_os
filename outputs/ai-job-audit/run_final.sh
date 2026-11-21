set -u
cd "$(dirname "$0")"
F() { claude -p --model claude-fable-5-2 --tools "" 2>/dev/null; }
O() { claude -p --model claude-opus-5-5 --tools "" 2>/dev/null; }
retry() { local out=$1; shift; for i in 1 2 3; do "$@" > "$out"; [ "$(wc -w < "$out")" -gt 200 ] && return 0; sleep 20; done; }
PANEL="Panel of 12 real Indian viewers scrolling at 10 pm (English only): 1 TCS support engineer Pune 24; 2 CA Ahmedabad 31; 3 HR exec Bengaluru 28; 4 bank RM Lucknow 35; 5 school teacher Jaipur 38; 6 BTech final-year Hyderabad 21; 7 FP&A analyst Gurgaon 25; 8 IB/equity research associate Mumbai 33; 9 Big 4 consulting analyst Bengaluru 24; 10 strategy consulting manager Mumbai 32; 11 performance marketing exec Delhi 26; 12 FMCG brand manager Mumbai 34."
GPT="NEW REQUIREMENT FROM THE CREATOR: viewers get a free ChatGPT custom GPT from Episode 1 so they are involved immediately: 'Run #1' GPT where they list 3-5 weekly tasks, ChatGPT actually attempts each on a sanitised or dummy input, they grade pass / pass with edits / fail, and get a dated Run card with the task to hand over (and its prompt), the task that stayed human, and a Run #2 date to come back and compare. It improves every episode. The CTA must drive people to it (one action: e.g. 'Comment RUN and I'll DM you the GPT' with link in bio as backup) and make running it feel like joining the series (post your card / number in comments)."
FORMAT="Deliver in markdown, English only:
1. Title, logline, emotion arc, why this version works.
2. SCREENPLAY: for every scene: scene number + name, time range, SET/LOCATION (what is in frame, props, wardrobe), CAMERA (framing, angle, lens feel, movement, layout: split top/bottom or full frame), LIGHTING, ACTION (what physically happens), SPOKEN (exact words), ON-SCREEN TEXT, TOP-HALF / FULL VISUAL (hand-drawn diagram, screen recording or real demo: what exactly is shown and how it animates), VIEWER EMOTION, DELIVERY (face, voice, body), CONTINUITY (pose and energy in/out), SOUND (music, SFX), TRANSITION OUT.
3. BEAT SHEET for the teleprompter: numbered beats, each one short spoken line, with FEEL / FACE-VOICE / POSE cues and the alternate line where a result may differ.
4. Hook map (every hook/re-hook with time and emotion).
5. Result-dependent lines and alternates.
6. Shot list in shooting order (camera + screen recordings + props).
7. Pre-shoot measurement checklist.
8. Spoken word count and runtime (2.6 words/s, max ~58 s)."

retry RUN1_PANEL_tuesday.md bash -c "{ echo \"You are an independent reviewer; another model wrote this reel script. $PANEL Give: per-persona one line (where they swipe or what holds them, would they comment, send to whom); score table (stop, relate, emotion, comment/run, send, return-for-Run-2) with averages; count spoken words and check runtime; lines that overclaim, blame laid-off people, sound smug, or state unmeasured results; top 6 fixes by beat. Verdict pass/revise. Under 800 words.\"; cat RUN1_SCRIPT_v2.md; } | claude -p --model claude-opus-5-5 --tools '' 2>/dev/null"
echo panel_tuesday

retry SCRIPT_TUESDAY_v3.md bash -c "{ cat hooks_brief.md; echo; echo 'YOUR TUESDAY SCRIPT v2:'; cat RUN1_SCRIPT_v2.md; echo; echo 'INDEPENDENT PANEL REVIEW:'; cat RUN1_PANEL_tuesday.md; echo; echo \"$GPT\"; echo; echo 'TASK: Write the FINAL version of the TUESDAY script (main hook: AI took my [DAY] morning / planner peel). Apply every honest fix from the panel, add the GPT CTA, keep what works. Make it dramatic and emotional but honest.'; echo \"$FORMAT\"; } | claude -p --model claude-fable-5-2 --tools '' 2>/dev/null"
echo tuesday_v3

retry SCRIPT_YOURNUMBER_v1.md bash -c "{ cat hooks_brief.md; echo; echo 'REFERENCE: the Tuesday script (same series, same facts):'; cat SCRIPT_TUESDAY_v3.md; echo; echo 'PANEL NOTES ON THE TUESDAY v2 SCRIPT:'; cat RUN1_PANEL_tuesday.md; echo; echo \"$GPT\"; echo; echo 'TASK: Write a COMPLETE, standalone script built around the hook \"How many of your weekly tasks can AI do? Mine: [N].\" (card flip ? -> [N] of [TOTAL]). The creator prefers this one. Do not just swap the opening: build the whole reel around the VIEWER'\''s number. The viewer is the subject; his number is the example; the open question (what is YOUR number) pays off with the GPT, where they get their own number in 5 minutes. Keep: method in one breath, dated count, back-test (last year vs today), one handover with real before/after, the taped failed task as open loop and reveal, the monthly loop and higher-order work, the sitting-duck/layoff sentiment as one honest line (never blaming laid-off people), non-IT doorway by 6 s. Dramatic, emotional, honest.'; echo \"$FORMAT\"; } | claude -p --model claude-fable-5-2 --tools '' 2>/dev/null"
echo yournumber_v1

for S in TUESDAY_v3 YOURNUMBER_v1; do
retry PANEL_$S.md bash -c "{ echo \"You are an independent reviewer; another model wrote this reel script. $PANEL Give: score table per persona (stop, relate, emotion, run-the-GPT, send, return-for-Run-2, avg) with column averages and overall; spoken word count and runtime check; hooks that work; does the GPT CTA make people act (friction?); lines that overclaim, sound smug, blame laid-off people or state unmeasured results; top 5 fixes by scene. Verdict pass/revise. Under 700 words.\"; cat SCRIPT_$S.md; } | claude -p --model claude-opus-5-5 --tools '' 2>/dev/null"
echo panel_$S
done

retry SCRIPT_TUESDAY_FINAL.md bash -c "{ cat hooks_brief.md; echo; echo \"$GPT\"; echo; echo 'YOUR SCRIPT:'; cat SCRIPT_TUESDAY_v3.md; echo; echo 'INDEPENDENT PANEL REVIEW:'; cat PANEL_TUESDAY_v3.md; echo; echo 'TASK: Final pass. Apply every honest fix; keep what works; same sections and format; English only.'; } | claude -p --model claude-fable-5-2 --tools '' 2>/dev/null"
echo tuesday_final
retry SCRIPT_YOURNUMBER_FINAL.md bash -c "{ cat hooks_brief.md; echo; echo \"$GPT\"; echo; echo 'YOUR SCRIPT:'; cat SCRIPT_YOURNUMBER_v1.md; echo; echo 'INDEPENDENT PANEL REVIEW:'; cat PANEL_YOURNUMBER_v1.md; echo; echo 'TASK: Final pass. Apply every honest fix; keep what works; same sections and format; English only.'; } | claude -p --model claude-fable-5-2 --tools '' 2>/dev/null"
echo yournumber_final
echo ALL_DONE
