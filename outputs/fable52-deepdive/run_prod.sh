set -u
cd "$(dirname "$0")"
retry() { local out=$1; shift; for i in 1 2 3; do "$@" > "$out"; [ "$(wc -w < "$out")" -gt 300 ] && return 0; sleep 30; done; }
PANEL="Panel (Indian viewers at 10 pm, English only): 1 TCS support engineer Pune 24; 2 CA Ahmedabad 31; 3 HR exec Bengaluru 28; 4 bank RM Lucknow 35; 5 school teacher Jaipur 38; 6 BTech final-year Hyderabad 21; 7 FP&A analyst Gurgaon 25; 8 IB/equity research associate Mumbai 33; 9 Big 4 consulting analyst Bengaluru 24; 10 strategy consulting manager Mumbai 32; 11 performance marketing exec Delhi 26; 12 FMCG brand manager Mumbai 34; 13 startup backend dev Bengaluru 27; 14 ML engineer Hyderabad 30; 15 gym trainer Delhi 29 (non-tech); 16 BCom student Kolkata 20."

retry SCRIPTS_LOCKED.md bash -c "{ cat facts.md results_tonight.md; echo; echo 'PREVIOUS DRAFTS:'; cat SCRIPTS_FINAL_v5.md; echo; echo 'SURVEY:'; sed -n '/Group averages/,\$p' SURVEY_v5.md; cat <<'P'

CREATOR DECISIONS (locked):
- MAIN REEL: money hook (\"Thirty-two times the price, for the same scores.\") with a POSITIVE emotional tone throughout: curiosity, wonder (Fermat), empowerment, savings, \"you can use the best AI smartly\". Bookend positive: check its work = you stay in control.
- TRIAL REEL: hook exactly: \"If the CEO says AI could be a risk to humanity, why did he just launch this?\" with a FEAR / stakes tone throughout, honest: CEO's UN warning (exact quote + 'if managed poorly' on screen, dates), the report's uncomfortable findings (it suspects it's being tested in up to 43% of audit transcripts; reward hacks mostly 'guessing what the answer key expects'; least self-critical; quit open-ended research without running an experiment 63% of sessions at medium effort; all measured on Mythos 5.2 = same model), the bill that burns, then the calm answer (my tests, router, check its work). No misquotes, no claim he said it after launch, no fear-mongering beyond the facts.
- Same core body (tests, quantity table, router, Fable on Pro card, CTA FABLE, Saturday Workout Analyser tease) so the hook + emotional tone are the experiment.
- Apply survey fixes: 'everyone around me is building with it' (his observation); 'four current Claude models'; 264 pages is verified.
OUTPUT exactly:
# MAIN REEL (money hook, positive)
full beat table (Beat | Section | Spoken (exact) | Top-half visual | On-screen text | Viewer feels | Music/SFX mood) + runtime (75-88 s at 1.1x incl. cards)
# TRIAL REEL (CEO question hook, fear)
full beat table, same columns + runtime
# TONE GUIDE
2 short paragraphs: how delivery, music, colour and visuals differ between the two (so the emotion, not just words, is tested)
English only.
P
} | claude -p --model claude-fable-5-2 --tools '' 2>/dev/null"
echo locked

retry SURVEY_LOCKED.md bash -c "{ echo \"Independent survey of two reel versions (another model wrote them). $PANEL For each version: per-persona row (3 s hold Y/N, watch %, dominant emotion felt, relatability 0-10, learned 0-10, send 0-10, save 0-10, comment FABLE Y/N); group averages (mass non-tech 2-5,12,15,16 / fin-consult-mktg 7-12 / builders 1,6,13,14) and overall; does each version actually evoke its intended emotion (positive vs fear)? where each loses people; any inaccuracy or fear-mongering vs FACTS; top 5 fixes. Under 1100 words.\"; cat SCRIPTS_LOCKED.md; echo FACTS:; cat facts.md results_tonight.md; } | claude -p --model claude-opus-5-5 --tools '' 2>/dev/null"
echo survey

for V in MAIN TRIAL; do
retry SCREENPLAY_$V.md bash -c "{ cat SCRIPTS_LOCKED.md; echo; echo 'INDEPENDENT SURVEY:'; cat SURVEY_LOCKED.md; cat <<P

TASK: For the $V REEL only, apply the survey's fixes that keep it accurate, then write its production package:
1. FINAL SCRIPT beat table (as above, updated).
2. SCREENPLAY: per scene: time, SET (props, wardrobe), CAMERA (framing, layout split/full), LIGHTING, ACTION, SPOKEN, ON-SCREEN TEXT, TOP-HALF VISUAL (exact hand-drawn line/architecture diagram or table, what draws on which word), EMOTION, DELIVERY (face/voice/body), CONTINUITY (pose/energy in/out), SOUND (music, SFX), TRANSITION.
3. BEAT SHEET for the teleprompter: numbered beats, one short line each, with FEEL / FACE-VOICE / POSE cues; record-order notes.
4. VISUAL LIST: every diagram/table/card to build (id, type, contents, animation, duration).
5. Shot list (camera + screen recordings) in shooting order.
English only.
P
} | claude -p --model claude-fable-5-2 --tools '' 2>/dev/null"
echo screenplay_$V
done
echo PROD_DONE
