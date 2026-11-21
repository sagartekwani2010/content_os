set -e
cd "$(dirname "$0")"
F() { claude -p --model claude-fable-5-2 --tools "" 2>/dev/null; }
O() { claude -p --model claude-opus-5-5 --tools "" 2>/dev/null; }
PANEL="Panel of 12 real Indian viewers at 10 pm: 1 TCS support engineer Pune 24; 2 CA Ahmedabad 31; 3 HR exec Bengaluru 28; 4 bank RM Lucknow 35; 5 school teacher Jaipur 38; 6 BTech final-year Hyderabad 21; 7 FP&A analyst Gurgaon 25; 8 IB/equity research associate Mumbai 33; 9 Big 4 consulting analyst Bengaluru 24; 10 strategy consulting manager Mumbai 32; 11 performance marketing exec Delhi 26; 12 FMCG brand manager Mumbai 34."

{ cat context.md; cat <<'P'

TASK: Write THREE radically different dramatic treatments for this 55 s reel. The current version is weak: too explanatory, too calm. Push emotion and drama (honest, no fear-mongering lies): stakes, tension, a personal confession, a reveal, a turn to hope and power. Each treatment must: show ACTUAL demos of the tool on screen (not described), contain a hook at 0 s plus re-hooks roughly every 10-12 s (at least 4 hooks in 55 s, each with a different emotion), and give a strong, specific reason to use the tool today (what the viewer gets in 2 minutes that they cannot get elsewhere).
Possible directions (use or beat them): A) "Confession/trial": he puts his own job on trial on camera, the verdict stings, then he fights back by handing tasks to AI live. B) "Friend's 2 minutes": real-time audit of a finance friend on a call, reactions on camera, the dignity reveal. C) "Race": AI does his Monday task in 40 seconds while he watches; what he does with the freed hours; then the viewer's turn.
For each: title, one-line concept, emotion curve (per 10 s), the 4-5 hooks with timestamps, the demo moments, the reason-to-use line, and the single riskiest element. About 300 words each.
P
} | F > TREATMENTS_v3.md
echo treatments done

{ echo "You are an independent reviewer; another model wrote these. $PANEL"; cat <<'P'
For EACH of the three treatments: per-persona one line (stop? relate? run the tool? send to whom?) and a score table per treatment (avg stop, relate, run, send, drama/emotion 0-10). Then: pick the winner, list the best elements to steal from the other two, and the 5 changes that would make the winner stronger for ALL 12. Under 900 words.
P
cat context.md; cat TREATMENTS_v3.md; } | O > TREATMENTS_PANEL_v3.md
echo panel1 done

{ cat context.md; echo; echo "THREE TREATMENTS YOU WROTE:"; cat TREATMENTS_v3.md; echo; echo "INDEPENDENT PANEL REVIEW:"; cat TREATMENTS_PANEL_v3.md; cat <<'P'

TASK: Write the full SCREENPLAY v3 (55 s) from the winning treatment, stealing the named elements and applying the panel's changes. Requirements:
- Dramatic and emotional; a clear emotion curve; at least 4 hooks/re-hooks in 55 s, each a different emotion, placed where people would otherwise swipe.
- ACTUAL demos on screen: screen recordings of the tool (task ticks, ratings landing, the card), and at least one live "hand it to AI" moment with a real before/after.
- A strong, specific reason to use the tool now, said and shown.
- Hinglish speech; English on-screen text and task names; the 8-role grid; consistency proof; friend dignity row; low-bar CTA.
Format, in markdown:
1. Logline + promise.
2. Emotion curve table (time, emotion, what triggers it).
3. Hook map: every hook/re-hook with timestamp, emotion, exact words, on-screen text.
4. SCREENPLAY: scenes with timestamps, each with SHOT (what is filmed or recorded, full-frame or split), SPOKEN (exact Hinglish lines, short), ON-SCREEN TEXT, DEMO (what the tool shows), EMOTION, DELIVERY (face/voice/body), CONTINUITY (pose/energy in and out), SFX/MUSIC.
5. Alternative opening hooks (5, different emotions, ranked) for Trial Reels.
6. Why people will run it (the reason-to-use stack) and why they will send it.
7. Shot list: everything to record or screen-record, in shooting order.
8. Honesty check: every placeholder and what must be true before posting.
Under 1500 words.
P
} | F > SCREENPLAY_v3.md
echo v3 done

{ echo "You are an independent reviewer; another model wrote this screenplay. $PANEL"; cat <<'P'
Per persona: at what second they stop or swipe, the moment they feel most, whether they run the tool and send it (to whom). Score table per persona (stop, relate, emotion, run, send 0-10) and averages per group (original six, finance, consulting, marketing) and overall. Check: are there >=4 working hooks; are demos real and visible; is the reason-to-use strong; any moment that feels fake, preachy, fear-mongering or insulting to a profession; is 55 s realistic for the spoken words (count them at ~2.7 words/s Hinglish). Top 6 fixes, specific. Verdict pass/revise. Under 900 words.
P
cat SCREENPLAY_v3.md; } | O > PANEL_CHECK_v3b.md
echo panel2 done

{ cat context.md; echo; echo "YOUR SCREENPLAY v3:"; cat SCREENPLAY_v3.md; echo; echo "INDEPENDENT 12-PERSONA PANEL REVIEW:"; cat PANEL_CHECK_v3b.md; echo; echo "TASK: Write the FINAL screenplay v4 applying every fix that keeps it honest; keep what works. Same format and sections as v3. Under 1500 words."; } | F > SCREENPLAY_v4.md
echo v4 done

{ echo "Independent re-score of this final screenplay. $PANEL Output ONLY: score table per persona (stop, relate, emotion, run, send), group averages, overall average, the hook count that works, top 3 remaining weaknesses, verdict pass/revise. Under 350 words."; cat SCREENPLAY_v4.md; } | O > PANEL_CHECK_v4.md
echo all done
