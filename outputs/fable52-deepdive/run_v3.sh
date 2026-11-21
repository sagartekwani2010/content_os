set -u
cd "$(dirname "$0")"
retry() { local out=$1; shift; for i in 1 2 3; do "$@" > "$out"; [ "$(wc -w < "$out")" -gt 300 ] && return 0; sleep 30; done; }
FORMAT="Output exactly:
# MAIN REEL beat table: Beat (numbered 1..N, one row per spoken beat) | Section | Spoken (exact) | Top-half visual (PAPER CUT first, then the hand-drawn diagram: describe the drawing precisely) | Paper extract / on-screen text | Viewer feels | Music/SFX ; then runtime at 1.1x
# TRIAL REEL: only beats that differ from MAIN (full rows, using the SAME beat numbers where the line is shared; give trial-only beats new numbers after the last main beat) + runtime
# FABLE USER RULES CARD (4 rules from the observations)
# TIPS CARD (3 tips, text only, with attribution line)
# THE SPOKEN TRACK ONLY (main as numbered beats, then trial differences)
English only."
retry V3_DRAFT.md bash -c "{ cat facts.md arch_facts.md impact_findings.md creator_changes_v3.md; echo; echo 'PREVIOUS SCRIPT FOR REFERENCE:'; cat SCRIPT_IMPACT_FINAL.md; echo; echo 'TASK: Write the new script applying ALL the creator changes exactly. Make the four observations vivid and relatable for everyday users (analogies Indians instantly get), each with clear impact, flowing narration with connective lines.'; echo \"\$1\"; } | claude -p --model claude-fable-5-2 --tools '' 2>/dev/null" _ "$FORMAT"
echo draft
retry V3_PANEL.md bash -c "{ echo 'Independent review (another model wrote this reel script). Panel of 16 Indian viewers at 10 pm, English only: TCS support engineer Pune 24; CA Ahmedabad 31; HR exec Bengaluru 28; bank RM Lucknow 35; school teacher Jaipur 38; BTech final-year Hyderabad 21; FP&A analyst Gurgaon 25; IB associate Mumbai 33; Big 4 analyst Bengaluru 24; strategy manager Mumbai 32; performance marketer Delhi 26; FMCG brand manager Mumbai 34; startup backend dev Bengaluru 27; ML engineer Hyderabad 30; gym trainer Delhi 29; BCom student Kolkata 20. Give: group averages (stop at 3 s, watch %, relatability, learned, send, save); which of the four observations land and which confuse; are the analogies apt; any claim not supported by FACTS/CHANGES (flag especially the CEO quote and the 14% / 6 cents line); top 6 fixes by beat. Under 800 words.'; cat V3_DRAFT.md; echo FACTS:; cat facts.md impact_findings.md creator_changes_v3.md; } | claude -p --model claude-opus-5-5 --tools '' 2>/dev/null"
echo panel
retry V3_FINAL.md bash -c "{ cat facts.md arch_facts.md impact_findings.md creator_changes_v3.md; echo; echo 'YOUR DRAFT:'; cat V3_DRAFT.md; echo; echo 'INDEPENDENT PANEL:'; cat V3_PANEL.md; echo; echo 'TASK: Final pass: apply every fix that keeps accuracy and the creator structure.'; echo \"\$1\"; } | claude -p --model claude-fable-5-2 --tools '' 2>/dev/null" _ "$FORMAT"
echo V3_DONE
