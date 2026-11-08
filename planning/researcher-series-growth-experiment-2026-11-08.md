# Researcher-led Reel series: follower-growth experiment

**Refined by creator direction:** [fitness-training-research-series-2026-11-08.md](fitness-training-research-series-2026-11-08.md) adds mass-entry ChatGPT training explainers and makes Sagar's fitness work the flagship test environment. The funnel diagnosis and experiment principles below remain applicable.

**Prepared:** 8 November 2026 (Asia/Kolkata)<br>
**Status:** proposed strategy and six-post pilot for creator approval; no production brief, generation, paid spend, scheduling or publication is authorised by this document.<br>
**Question:** What repeatable content makes the *right* new viewer want to follow Sagar for the next investigation?

## Diagnosis: what is known and what is not

- The creator reports stagnant follower count despite paid campaigns. Treat that as the observed business outcome.
- All three local Content OS databases currently contain **zero `post_performance` rows and zero `ad_tests` rows**. The repo has hypothesis and scoring files, but it cannot tell us whether the loss is at non-follower reach, attention, profile visits, visit-to-follow conversion or unfollows. The existing `config/experiments.yaml` hypotheses are not measured findings.
- One plausible creative bottleneck is *time to proof*: the prepared SkillRL package spends its opening explaining a trajectory and its mechanism extends to a roughly 74-second Reel. That is a useful deep lesson, but it has not been shown here to attract new followers. This is a hypothesis from the script, not a verdict on its published performance.
- A second plausible bottleneck is *follow promise*: a viewer can appreciate an isolated Wardrobe, career, paper or model Reel without knowing what the next post will reliably give them. A recurring investigation with a visible next test can answer that. This is a strategy hypothesis, not an Instagram algorithm fact.
- A third plausible bottleneck is paid distribution/creative mismatch. We need the objective, targeting, spend, placements and actual post-level follow data before claiming that paid promotion helped or harmed growth. Organic and paid cohorts must be analysed separately; net follower count also includes unfollows.

**External evidence:** Meta says Instagram recommendations have placed more weight on original posts, with [75% of US recommendations from original posts in Q4 2025](https://about.fb.com/news/2026/01/2026-ai-drives-performance/). This is a platform-wide US figure, not an expected result for this India-based account. Meta's [Trial Reels](https://about.fb.com/news/2024/12/trial-reels-try-content-non-followers-first-see-what-perfoms-best/) are designed to show a Reel to non-followers first and expose early engagement metrics. We can use that surface if the account has it, but a trial's early reach is not proof of follower conversion. Meta's creator [Best Practices](https://about.fb.com/news/2024/10/best-practices-education-hub-creators-instagram/) explicitly covers attention, engagement, reach and the relationship between Reels and follower growth; account-specific guidance should be checked in the creator dashboard.

## New external promise

> **I test AI agents on real decisions, show what broke, and explain the design choice that changed the result.**

Each Reel must pay off independently and also make the next investigation intelligible. Sagar's authority comes from the experiment contract: a real input, baseline, changed condition, actual trace, result, limitation and a reusable design rule. Papers provide the hypothesis or comparison; Sagar's own test is the visible story. If the test produces a null or negative result, that becomes a stronger research Reel than a polished but unverified success claim.

The format is **result or failure first → familiar stakes → one changed variable → evidence → decision rule → truthful next test**. Avoid opening with a paper title, model launch, architecture chart or the words “AI is changing everything.” Keep Sagar visible or recognisable as the investigator; an AI avatar is a deliberate variant for Agent Astra, not the default trust cue until measured.

## Three recurring categories and the first six pilots

| Category / acquisition role | Pilot Reel | First-screen tension and real proof | Reason to follow |
| --- | --- | --- | --- |
| **1. Agent on Trial** — broad, shareable real-life stakes | **A1 · `MEM-01`: Wardrobe Agent, first decision.** Give it owned clothes and one real event; show its first shortlist and Sagar's choice. | Begin with the actual outfit result or obvious mismatch, then reveal the inventory/occasion constraints. If there is no failure, make the real success and its limits the story. | Next test changes one constraint and reruns the same agent. |
| **2. Researcher’s Lab** — original test and calibrated authority | **B1 · `REL-01`: Astra changes Qwen's support-routing behaviour.** Run the local LoRA experiment on a bounded missing-order decision. | Base output → adapter training → held-out output, plus the prompt-only and rule baselines. Lead with the measured result after it exists. AI-avatar delivery can be tested here. | Next lab result tests whether a paper's memory claim holds in a small local fixture. |
| **3. Design After Failure** — technical followers and saves | **C1 · `ACT-06`: AI system design after a duplicate send.** Use a contained agent with mock messaging tools and a simulated retry failure. | Show two sends or a blocked second send first; teach the single design decision that makes a retry safe. Permission and approval appear only as context. Position as a practical system-design interview answer. | Next review tests an untrusted-page attack on a tool-using agent. |
| **1. Agent on Trial** | **A2 · `MEM-02`: Wardrobe Agent after rejection.** Sagar says “too warm” or another real reason; rerun on the same wardrobe. | Show the rejected outfit and the reranked option side by side. Distinguish one-run state from a lasting preference. | Viewers see whether the agent responds to feedback rather than merely sounding agreeable. |
| **2. Researcher’s Lab** | **B2 · `REL-02`: memory under irrelevant-history growth.** Keep one travel preference and question fixed, add irrelevant prior sessions in steps. | Reveal the same question receiving a different answer or a stable answer under a fixed retrieval budget; report the actual local counts. The [29 October paper revision](https://arxiv.org/abs/2605.07313) motivates the test pattern, not a borrowed result. | A reproducible test series for claims people normally take on faith. |
| **3. Design After Failure** | **C2 · `REL-09`: a web page tries to become the agent's boss.** Put a malicious instruction in a controlled page/tool result. | Show the attempted deviation and the observed result after separating external text from instructions and scoping actions. [OpenAI guidance](https://developers.openai.com/api/docs/guides/tools-computer-use-integration) treats third-party content as untrusted. | The series can return to one agent failure mode each week and show the engineering fix. |

This batch keeps three `ai_builder`, two `ai_real_life` and one `ai_career` pieces: within the repository's portfolio guardrails and close to its directional mix. C1 is explicitly the career/interview treatment of system design. The approved broader career initiative remains available for later experiments; this pilot concentrates on the creator's research authority and the agent-learning promise.

**Potential first-screen language, to lock only after evidence:** “I gave an agent my actual wardrobe. Here is the decision I had to reject”; “I changed Qwen's weights to fix one decision—here is the held-out result”; “This agent wrote the right message and still failed when the send retried”; “I buried one useful fact under old chats and measured what happened.” Never imply a failure or gain that the recording does not show.

## What we are testing

This first batch tests **series demand and funnel location**, not a statistical winner. Two posts per category are too few to isolate a format effect, and each topic differs. Freeze the common production contract as much as practical: one visible proof in the opening seconds, one changed condition, one main lesson, Sagar's recognisable voice/presence, a truthful sequel line and consistent cover naming. Do not change hook, duration, delivery mode, CTA and paid support all at once.

| Funnel stage | Measure at 24 h, 72 h and 7 d | Interpretation if weak |
| --- | --- | --- |
| Discovery | Non-follower reach, separately organic and paid | Test audience/problem framing and opening visual. |
| Attention and sharing | Average watch time or retention, sends/shares per reach, saves per reach | Test time to result and proof clarity. Shares indicate a viewer saw value for someone else; saves indicate repeat utility. Neither is a follow. |
| Profile intent | Profile visits per non-follower reach, or per total reach when attribution is unavailable | If high reach but few visits, the Reel may be complete as a one-off or the investigator identity is unclear. |
| Follow conversion | Follows per profile visit and follows per 1,000 non-follower accounts reached | If visits are high but follows low, audit bio, pinned Reels and whether the profile promises this same recurring series. |
| Retention of new followers | Net follower change, unfollows, and returning-viewer indicators if available | A flat count can hide simultaneous follows and unfollows; do not infer zero acquisition from net alone. |

Use the same seven-day organic window for all six. If paid campaigns continue, report them in a separate column with objective, spend, audience, profile visits and attributable follows; do not pool paid views into the organic series comparison. Do not boost a Reel in the measurement window unless all compared pilots receive equivalent treatment. The first six establish an account baseline; then repeat the strongest two categories with new episodes and a preregistered single-variable creative test (for example proof-first versus story-first opening). Choose a direction after **two batches**, not one lucky post.

### Within-category experiments after the pilot

| Category | First controlled question in the next batch | Keep stable | Winning signal to look for |
| --- | --- | --- | --- |
| Agent on Trial | Does the first screen showing the **real-world consequence** (worn outfit/actual choice) outperform a first screen showing the **agent's decision card**? | Same wardrobe task type, Sagar delivery, length band, proof quality, posting support and profile promise. | More qualified non-follower reach and profile visits without a collapse in follow conversion. |
| Researcher’s Lab | Does a **measured result first** opening outperform a **specific claim being tested first** opening? | Same research question or closely matched experiments, result disclosure, Sagar/approved-avatar treatment, length band and visual density. | Higher watch-through and follows per reached non-follower; report whether the result is positive, null or negative. |
| Design After Failure | Does the **failure trace first** outperform the **human consequence first** for a system-design lesson? | Same failure class, one architecture decision, diagram complexity, delivery, length band and release support. | Higher shares/saves among technical viewers and qualified follows, rather than views alone. |

These are *future* controlled tests. The first six cannot identify these effects because their subjects and evidence differ. If Instagram Trial Reels is available, use it for a small non-follower pretest of genuinely distinct edits; compare the same elapsed window and avoid treating its view count as a follow result. Replicate any apparent winner on another topic before changing the default production format.

**Signal rules:** high non-follower reach plus high follows per reach earns another episode; high reach with low visits calls for a sharper personal/series bridge; high visits with low follows calls for a profile-promise audit; high saves with low reach calls for a more accessible first screen; high paid reach with weak organic and follow conversion calls for campaign-objective and audience review. These are diagnostic patterns, not proof of causation.

## Production and profile dependencies

1. Obtain the last 10–15 Reel Insights and paid campaign screenshots/export before claiming a precise cause. The needed fields are reach (including non-followers and paid/organic split where possible), watch time/retention, sends/shares, saves, profile visits, new follows, unfollows, spend, objective and targeting.
2. Review the current bio and three pinned posts as a **conversion surface**. Proposed wording to test, not a profile edit: “I test AI agents on real tasks. See the failures, results and system designs behind each build.” Pin one Agent on Trial result, one Researcher’s Lab result and one Design After Failure result when they actually exist.
3. Collect actual wardrobe items and occasion, preserve raw runs, complete the Qwen feasibility/eval, and build contained mock tools for C1/C2. A1/A2 need genuine Sagar inputs; B1/B2 need raw result tables; C1/C2 need auditable failure traces. Scripts and claims follow the results.
4. Batch production over 2–3 days after the creator approves the topics; target a first reviewable release on 12–13 November, with the remaining Reels staged across subsequent days. No new media credits are needed for this planning pass. For production, check connected service balances before any justified InVideo or Magnific run; fal.ai generations remain creator-run.
5. After every generation and final edit, record creator feedback, actual before/after evidence and whether the Reel fulfilled its hook. Promote only approved or repeated lessons into brand memory and versioned prompts.

## Decision requested from Sagar

Approve or revise the **three-category research-led series** and six pilots. The most consequential creative choice is whether the public promise should be “I test AI agents on real decisions” as written here. The performance diagnosis remains provisional until Instagram Insights and campaign data are supplied.

This proposal supersedes the narrower [demo-topic slate](regular-demo-series-backlog-2026-11-08.md), while retaining the creator-requested two Wardrobe Agent videos, Agent Astra and AI system design.
