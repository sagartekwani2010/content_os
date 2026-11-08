# Reel batch for 2 October 2026

## Status

`CREATOR_APPROVED_DIRECTION_AND_ORDER`

The creator selected this three-Reel order:

1. real-life Wardrobe Selector;
2. one paper deep-dive;
3. one interview Reel.

This order replaces the previously proposed all-Gym-Agent batch. It matches the
existing fixed Reel lineup and rotates across the three intended content
surfaces: real-life agent demo, technical authority and AI-native career
judgement.

## Reel 1 — Real-life Wardrobe Selector

- **Pillar:** Agent Demos in Real Life
- **Canonical topic:** `MEM-01 — Context engineering`
- **Evidence state:** prototype until a working selection trace is recorded
- **Outcome:** choose from clothes Sagar already owns instead of browsing or
  buying more items
- **Hook:** `I do not need AI to buy more clothes. I need it to choose from what I already own.`
- **Viewer learning:** A useful selector needs a decision-ready context packet,
  not a photograph plus a vague prompt.
- **Concrete system:** wardrobe inventory + occasion + weather + preferences and
  constraints → three ranked outfit options with concise reasons → human choice.
- **Proof visual:** real wardrobe images, one occasion/weather card and the
  resulting three-option shortlist.
- **Human boundary:** the system proposes; Sagar chooses. It does not purchase,
  discard or alter anything.
- **Closing rule:** `Context should contain what changes the decision—not every fact you can collect.`
- **Target duration:** 35–45 seconds.

Keep this grounded in Sagar's real clothes and a real occasion. Do not use a
fake polished app dashboard as evidence.

## Reel 2 — Paper deep-dive: SkillRL

- **Pillar:** Agents: Build, Evaluate & Operate
- **Paper:** `SkillRL: Evolving Agents via Recursive Skill-Augmented Reinforcement Learning`
- **Canonical topic:** `LRN-03 — Skill abstraction`
- **Evidence state:** source-led paper and code explanation; the authors'
  reported results are not an independent reproduction
- **Why this paper now:** it is directly about agents, has public code and was
  announced as accepted at NeurIPS 2026 on 24 September 2026.
- **Hook:** `Most agents do not learn from experience. They just accumulate longer histories.`
- **Viewer learning:** The viewer can distinguish a raw trajectory, episodic
  memory, a reusable skill and an updated policy.
- **Single concept:** SkillRL distils useful patterns from successful
  trajectories and concise lessons from failures into a hierarchical skill
  library, retrieves relevant skills for a task and evolves the library using
  validation failures during reinforcement learning.
- **Proof visual:** several noisy agent trajectories compress into one
  structured skill card containing `when to apply`, `strategy` and `failure to
  avoid`; a later validation failure updates that card.
- **Production implication:** logging experience is not the same as learning;
  an agent needs validation, abstraction, retrieval and controlled skill
  evolution.
- **Closing rule:** `Do not call stored history learning. Show what was abstracted, when it is retrieved and how it changes after failure.`
- **Target duration:** 50–65 seconds.

Primary sources:

- <https://arxiv.org/abs/2602.08234>
- <https://github.com/aiming-lab/SkillRL>

Avoid presenting the paper's benchmark improvement or token reduction as a
general production guarantee. Attribute any numerical result to the authors.

## Reel 3 — Tech job losses: what is actually changing?

- **Pillar:** Become AI-Native: Career & Leadership
- **Scope:** evidence-led labour-market interpretation and preparation guidance
  for software engineering, data science and product roles
- **Evidence state:** current labour-market reports plus role-specific informed
  recommendations; do not claim that every layoff was caused by AI
- **Hook:** `The tech job slowdown is real. “AI took all the jobs” is still the wrong diagnosis.`
- **Core thesis:** current hiring weakness has multiple macroeconomic and
  restructuring causes. AI is already changing the skills and task mix inside
  roles, tightening some entry paths and raising the evidence bar, while
  credible projections still show growth for software and data occupations.
- **Viewer learning:** The viewer can separate three questions: Is hiring weak?
  Is AI the proven cause? What capability evidence should I build next?
- **Reality checks:**
  - LinkedIn's 2026 labour-market analysis attributes most recent hiring
    weakness to broader economic conditions rather than AI displacement alone.
  - LinkedIn reports tightening entry pathways for software engineers while
    AI-related and adjacent roles expand.
  - The World Economic Forum projects substantial displacement and creation at
    the same time; surveyed employers also expect large-scale reskilling.
  - U.S. BLS projections still show strong 2024–34 growth for software
    developers and data scientists. These are U.S. projections, not universal
    guarantees or short-term hiring forecasts.
- **Role-specific readiness:**
  - **SDE:** move beyond code generation; demonstrate system design, agent/tool
    contracts, testing, security, observability, failure recovery and ownership
    of a shipped outcome.
  - **Data science:** demonstrate problem framing, data quality, experimentation,
    causal judgement, model and agent evaluation, monitoring and a decision
    that changed because of the analysis.
  - **Product:** demonstrate workflow redesign, customer judgement, measurable
    success criteria, rapid AI prototyping, evaluation, guardrails and the
    quality–latency–cost trade-off.
- **Shared preparation rule:** build one proof-of-work case study showing the
  problem, judgement calls, AI leverage, validation, failure trace and measured
  or honestly qualitative outcome.
- **Proof visual:** `Reality / Not proven / Prepare` in three columns, followed
  by one compact SDE–DS–Product readiness matrix.
- **Closing rule:** `Do not prepare for the old job description with one new tool. Build evidence that you can own outcomes in an AI-native workflow.`
- **Target duration:** 55–70 seconds, or split into a trend Reel and a
  role-readiness carousel if the role matrix becomes unreadable.

Primary sources:

- <https://economicgraph.linkedin.com/research/labor-market-report-2026>
- <https://economicgraph.linkedin.com/content/dam/me/economicgraph/en-us/PDF/us-software-engineer-talent-landscape-2026.pdf>
- <https://www.weforum.org/publications/the-future-of-jobs-report-2025/in-full/2-jobs-outlook/>
- <https://www.bls.gov/opub/ted/2026/artificial-intelligence-information-technology-and-employment-2024-34.htm>

## Batch-production plan

Shoot in the approved order, using the same camera, lighting and framing:

1. Wardrobe Selector: record the real-life footage and decision trace first,
   while the wardrobe and occasion setup are available.
2. SkillRL paper: switch to face-led delivery with the paper title and one
   trajectory-to-skill visual.
3. Career Reel: finish with the cleanest talking-head setup, one evidence card
   and one SDE–DS–Product preparation matrix.

The three Reels should feel intentionally different:

- Reel 1 proves an ordinary-life outcome;
- Reel 2 interprets current technical research;
- Reel 3 converts leadership experience into practical career guidance.

Do not add Gym Assistant material to this batch. The Agent Loop carousel remains
the separate Gym-themed asset.
