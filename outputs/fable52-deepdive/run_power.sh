set -u
cd "$(dirname "$0")"
retry() { local out=$1; shift; for i in 1 2 3; do "$@" > "$out"; [ "$(wc -w < "$out")" -gt 300 ] && return 0; sleep 30; done; }
PANEL="Panel (Indian viewers at 10 pm, English only): 1 TCS support engineer Pune 24; 2 CA Ahmedabad 31; 3 HR exec Bengaluru 28; 4 bank RM Lucknow 35; 5 school teacher Jaipur 38; 6 BTech final-year Hyderabad 21; 7 FP&A analyst Gurgaon 25; 8 IB/equity research associate Mumbai 33; 9 Big 4 consulting analyst Bengaluru 24; 10 strategy consulting manager Mumbai 32; 11 performance marketing exec Delhi 26; 12 FMCG brand manager Mumbai 34; 13 startup backend dev Bengaluru 27; 14 ML engineer Hyderabad 30; 15 gym trainer Delhi 29 (non-tech); 16 BCom student Kolkata 20."
retry POWER_IDEAS.md bash -c "{ cat facts.md creator_inputs.md; echo; echo 'CURRENT MAIN SCRIPT:'; sed -n '/^## 1/,/^## 2/p' SCREENPLAY_MAIN.md; echo; echo 'CURRENT TRIAL SCRIPT:'; sed -n '/^## 1/,/^## 2/p' SCREENPLAY_TRIAL.md; echo; echo 'LATEST SURVEY:'; sed -n '/Group averages/,\$p' SURVEY_LOCKED.md; cat <<'P'

You own this script. TASK (think hard, be ambitious, stay honest):
1. HOW TO MAKE IT MORE POWERFUL: diagnose the 5 biggest weaknesses of the current scripts for an Indian Instagram audience, and propose 8 concrete upgrades (structure, open loops, emotional turns, a signature moment people screenshot or quote, payoff of the hook, ending that loops back, how to make the 'how I use Fable' beat the emotional core, how to make numbers land as percentages).
2. HOOKS: write 10 hooks for the MAIN reel (positive tone, money/value family; include sharper rewrites of 'Forty times the price, for the same scores.') and 10 for the TRIAL reel (fear tone; include the creator's exact line and 4 sharper variants that keep his meaning). Each: spoken (<= 14 words), on-screen text (<= 6 words), first frame, emotion. Rank each set with reasons.
English only.
P
} | claude -p --model claude-fable-5-2 --tools '' 2>/dev/null"
echo ideas
retry HOOK_PANEL.md bash -c "{ echo \"Independent reviewer; another model wrote these hooks. $PANEL For the MAIN set and the TRIAL set separately: a stop/swipe grid (16 personas x 10 hooks), stops per hook /16, and your top 3 per set with why. Note any hook that misquotes or overclaims vs FACTS. Under 900 words.\"; sed -n '/HOOK/,\$p' POWER_IDEAS.md; echo FACTS:; cat facts.md creator_inputs.md; } | claude -p --model claude-opus-5-5 --tools '' 2>/dev/null"
echo hookpanel
retry SCRIPTS_v6.md bash -c "{ cat facts.md results_tonight.md creator_inputs.md; echo; echo 'YOUR IDEAS AND HOOKS:'; cat POWER_IDEAS.md; echo; echo 'INDEPENDENT HOOK PANEL:'; cat HOOK_PANEL.md; cat <<'P'

TASK: Write the two FINAL scripts, applying your upgrades and the creator's locked changes. Use the panel's best MAIN hook (positive) and, for TRIAL, the creator's exact line unless a panel-preferred variant keeps his exact meaning (then give both, creator decides). Body the same in both except tone-driven lines. 75-88 s at 1.1x incl. cards.
Output:
# MAIN REEL (positive) - beat table: Beat | Section | Spoken (exact) | Top-half visual (diagram/table/screen recording, what draws on which word) | On-screen text | Viewer feels | Music/SFX ; then runtime
# TRIAL REEL (fear) - same columns; runtime
# WHAT MAKES THIS VERSION MORE POWERFUL (5 bullets)
# PLACEHOLDERS (all [DUMMY] values to measure tomorrow, exact definitions)
English only. Never present a [DUMMY] value as real in on-screen text without the [DUMMY] tag in this draft.
P
} | claude -p --model claude-fable-5-2 --tools '' 2>/dev/null"
echo final
retry SURVEY_v6.md bash -c "{ echo \"Independent engagement survey of two reel versions (another model wrote them). $PANEL Per version: per-persona row (3 s hold Y/N, watch %, emotion felt, relatability, learned, send, save 0-10, comment FABLE Y/N); group averages (mass 2-5,12,15,16 / fin-consult-mktg 7-12 / builders 1,6,13,14) and overall; does each evoke its intended emotion; inaccuracies vs FACTS; top 5 fixes. Under 1000 words.\"; cat SCRIPTS_v6.md; echo FACTS:; cat facts.md creator_inputs.md; } | claude -p --model claude-opus-5-5 --tools '' 2>/dev/null"
echo POWER_DONE
