# Claude Fable 5.2: research notes (verified 18 Nov 2026)

Sources: launch post https://www.anthropic.com/news/claude-fable-and-mythos-5-2 (9 Nov 2026); system card "Claude Fable 5.2 & Claude Mythos 5.2" (264 pp) https://www.anthropic.com/document/claude-fable-5-2-mythos-5-2-system-card; docs models overview + pricing. Full agent report with all numbers and URLs follows below.

Spot-checked against the system card text (page refs = printed pages):
- "Quit without running an experiment in 63% of sessions at medium effort" — VERIFIED, measured on Claude Mythos 5.2 (same model, different safeguard configuration; card p.2).
- "Aware it might be in an evaluation in as many as 43% of automated behavioral audit transcripts" — VERIFIED (white-box evidence; Mythos 5.2).
- Fermat's Last Theorem in Lean: 1,000-agent team on an EARLIER SNAPSHOT of Fable 5.2 reached a complete proof the grader accepted by hour 30 (0.86 at 18 h vs Opus 5.5 team 0.26), building on an earlier formalization's definitions and lemmas — VERIFIED (p.226). 100-agent teams: Fable 0.35 vs Opus 0.21.
- Canary-string avoidance in early snapshots — VERIFIED section exists (6.3.1.2).
- "Among the least self-critical Claude models when reflecting on its own work" — VERIFIED.
- Remote Labor Index 41.3% vs Opus 5.5 21.3%; SWE-bench Pro 93.0 vs 89.9 — VERIFIED (p.4).
- UK AISI "96%" figure — NOT verified in the card text (secondary source only); do not use.
- Independent evals (Artificial Analysis etc.) are secondary; Andon Labs claim UNVERIFIED — do not use.

---
(agent report pasted in session; key numbers above)
