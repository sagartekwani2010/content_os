# SkillRL — how agents turn trajectories into reusable skills

## Status

`READY_FOR_HUMAN_REVIEW`

The spoken claims are source-backed. Quantitative paper results remain
author-reported and are not presented as Sagar's reproduction.

## Brief fingerprint

- **Topic:** SkillRL — how agents turn trajectories into reusable skills
- **Core thesis:** Storing past agent trajectories is not the same as learning
  from them. SkillRL proposes a pipeline that distils successful and failed
  trajectories into structured general and task-specific skills, retrieves
  relevant skills at runtime and evolves the skill library from validation
  failures while the policy is trained.
- **Learning objective:** After viewing, a person can distinguish a trajectory,
  episodic memory, a reusable skill and a learned policy, and can name the four
  system contracts required for experience to improve future agent behaviour:
  validation, abstraction, retrieval and controlled evolution.
- **Format:** Reel
- **Brand pillar:** ai_builder
- **Mandatory sections:** raw-trajectory problem; success and failure
  distillation; SkillBank organisation and retrieval; recursive evolution;
  author-reported evidence boundary; production/interview rule.

## Learning payoff

The viewer can reject vague claims that an agent “learns from experience” and
ask four concrete design questions: how was the experience validated, what was
abstracted, when is the skill retrieved and what controlled the update?

## Hook options

1. **Selected — mistake:** `Most agents do not learn from experience. They just accumulate longer histories.`
2. **Comparison:** `A trajectory records what happened. A skill compresses what to do next.`
3. **Myth-busting:** `Agent memory is not automatically agent learning.`
4. **Framework:** `Before you say your agent learns, show me four contracts.`

The selected hook creates the strongest unanswered question: if storing history
is not learning, what mechanism is?

## Story spine

Viewer assumption that memory equals learning → raw trajectories are noisy and
task-specific → SkillRL distils them into structured skills and failure lessons
→ relevant skills are retrieved and validation failures evolve the library →
the viewer gets a four-contract test for agent-learning claims.

## Recording-ready script

> **[High energy; direct to camera]** Your AI agent can complete a task
> perfectly—and still learn nothing from it.
>
> **[Keep the pace high; count the steps]** On a complex query, ChatGPT does not
> jump directly to the final answer. First, it interprets your query. Next, it
> chooses an action—like searching the web or running code. Then it reads the
> result and uses that result to decide the next action.
>
> **[Slow slightly]** This ordered chain—**query, action, result, next
> action**—is called a **trajectory**.
>
> **[Punch the contrast]** But that is execution—not learning. Learning begins
> only when that experience changes what the agent does in the next run.
>
> **[Emphasise]** So how do we turn one completed trajectory into better future
> decisions? That is a long-running challenge across agent research, including
> at OpenAI.
>
> **[Introduce the paper]** That brings us to **SkillRL**, from researchers at
> UNC-Chapel Hill, UC Berkeley and other institutions.
>
> SkillRL has two layers.
>
> **[Count one]** First, the skill layer. A teacher model studies successful and
> failed trajectories, extracts what worked and what should change, and stores
> reusable general and task-specific skills.
>
> **[Count two]** Second, the **RL layer—reinforcement learning**. The agent
> attempts tasks, receives rewards and updates its decision policy. Validation
> failures also update the SkillBank.
>
> **[Land the mechanism]** The result? The policy and skills improve together.
>
> **[Lean in]** The agents we build next cannot just store logs. They need a
> controlled learning layer that evaluates each run, turns validated experience
> into reusable skills—and governs how those skills change future behaviour.
>
> **[Warm, direct CTA]** If you are building agents and want to discuss
> architectures like this, reach out through the link in my bio.

Keep this disclosure on screen during the paper mechanism rather than spending
spoken time on it: `AUTHOR-REPORTED BENCHMARK RESULTS · NOT INDEPENDENTLY REPRODUCED`.

Show the full affiliation line on screen during the paper introduction:
`UNC-CHAPEL HILL · UCHICAGO · UC SAN DIEGO · UC BERKELEY · UC SANTA CRUZ · NEC LABS AMERICA`.

### Positioning note

Do not call SkillRL “the most important paper in agentic history.” The paper is
too recent and its results are benchmark-specific. The defensible high-conviction
claim is that it tackles **one of the most important unanswered questions in
agent design: how experience becomes reusable behaviour**.

## Scene plan

| Time | Viewer question | Voiceover | On-screen copy | Visual proof | Production mode | Why it stays |
|---:|---|---|---|---|---|---|
| 0–10s | How can a successful agent still learn nothing? | Contradiction hook followed by the familiar trajectory sequence | `TASK COMPLETE. NOTHING LEARNED.` then `QUERY → ACTION → RESULT → NEXT ACTION` | A completed task and stored log fail to alter the next run; the following animation defines the within-run trajectory. | Face + opening proof image + H3 animation | Makes the learning problem visible before introducing the technical term. |
| 10–20s | What happens to the experience after the run? | Research-problem transition | `PAST EXPERIENCE → BETTER FUTURE DECISIONS?` | A completed trajectory stops before an unchanged future run. | Face + generated diagram | Creates the precise question before naming the paper. |
| 20–28s | What is SkillRL? | One-line paper introduction and two-layer mental model | `SKILLRL` / `SKILL LAYER + RL LAYER` | Real paper title appears, then separates into two labelled lanes. | Real paper capture + face | Gives a general audience a simple map before the mechanism. |
| 28–41s | What is its skill layer? | Teacher distillation and retrieval | `TRAJECTORIES → GENERAL + TASK SKILLS → RETRIEVE` | Successful and failed traces compress into general and task-specific skills; the relevant skill enters a future task. | Generated architecture diagram | Explains the `Skill` in SkillRL first. |
| 41–55s | What is its RL layer? | Reward, policy update and SkillBank evolution | `TASK → REWARD → POLICY UPDATE` / `VALIDATION FAILURE → SKILLBANK UPDATE` | The policy and SkillBank update on parallel tracks. Show `SFT → RL` as a small technical annotation and keep the evidence disclosure visible. | Generated architecture diagram + face | Explains RL only inside the introduced SkillRL architecture. |
| 55–66s | What changes for agent builders? | Concise production-design implication | `LOGS ≠ LEARNING PIPELINE` | Three governed steps lock together: evaluate experience, extract skill, control update. | Architecture diagram + face | Converts the paper into a concrete system-design decision. |
| 66–74s | What should an interested builder do next? | Direct relationship CTA | `BUILDING AGENTS?` / `LINK IN BIO` | Face-led close with the site/link cue below the safe-zone headline. | Talking head | Gives interested builders a clear, non-pushy channel to continue the conversation. |

## Illustrative skill card used in visuals

Label this example `ILLUSTRATIVE`, not a paper benchmark output:

- **Name:** Verify preconditions before action
- **Principle:** Confirm that the required state and permission are present
  before invoking the tool.
- **When to apply:** An action depends on a previous step or an external state.
- **Failure to avoid:** Repeating the same invalid action after the environment
  has already rejected its precondition.

## Visual system

- Final canvas is vertical 9:16. Generate all H3 B-roll in 16:9 landscape,
  centre-safe within the middle 55%, then crop it into the top half while Sagar
  remains visible in the bottom half.
- Use warm off-white backgrounds, charcoal objects, electric-blue system lines
  and muted lime only for selected or validated states.
- Keep Sagar present throughout scenes 1–6 in the lower half. Use a full
  talking-head frame for the CTA in scene 7.
- Use the real arXiv title page or HTML title as evidence in scene 3.
- For the current production pass, bake the exact technical labels directly
  into H3 alongside the causal animation. Treat any misspelled, morphing or
  invented text as a failed generation. Keep the GPT-2.5 two-layer still only
  as an optional fallback if repeated H3 generations fail.
- Use the four explanation-first H3 clips in `BROLL_H3_PROMPTS.md`: trajectory
  plus memory gap, skill layer, RL plus SkillBank co-evolution, and the
  future-agent controlled learning layer. The final clip is necessary because
  the design implication introduces a new architecture contract rather than
  merely summarising the paper mechanism.
- No fake code console, chain-of-thought, robots, neural-network imagery or
  fabricated benchmark bars.

## Caption

See `caption.txt`.

## Factual boundaries

- arXiv v1 is dated 9 February 2026.
- The repository announces NeurIPS 2026 acceptance on 24 September 2026.
- The paper describes successful-trajectory pattern extraction, failed-run
  lessons, general and task-specific SkillBank entries, runtime retrieval and
  recursive updates using validation failures during RL.
- Learning from past experience and transferring reusable strategies to new
  tasks is a long-running research problem; OpenAI described this objective and
  limitation in its 2016 Universe research release.
- Benchmark and compression claims belong to the authors and the evaluated
  settings. Sagar has not independently reproduced them.
- `name`, `principle` and `when_to_apply` are paper-described skill fields. The
  precondition skill card above is an illustrative application.

## Source links

- Paper: <https://arxiv.org/abs/2602.08234>
- Code and project updates: <https://github.com/aiming-lab/SkillRL>
- OpenAI background on transferring past experience to new tasks:
  <https://openai.com/index/universe/>

## QA report

- **Learning payoff:** 9/10 — gives a reusable four-contract test.
- **Technical accuracy:** 9/10 — distinguishes memory, skill retrieval and RL
  policy training.
- **Story progression:** 9/10 — familiar trajectory → research question →
  SkillRL's two-layer mental model → production implication → relationship CTA.
- **Visual proof:** 8/10 until the real paper capture is attached.
- **Evidence integrity:** 9/10 — results are attributed and reproduction status
  is explicit.
- **Phone readability:** 9/10 — one mechanism per proof visual.
- **Hard gates:** pass, conditional on retaining the source boundary.

**Verdict:** `READY_FOR_HUMAN_REVIEW`

## Files

- `caption.txt` — paste-ready caption.
- `ASSET_PROMPTS.md` — current asset index.
- `BROLL_H3_PROMPTS.md` — horizontal H3 production settings, edit map and QA.
- `EDITOR_OVERLAY_GUIDE.md` — H3-baked text acceptance and assembly guidance.
- `asset-prompts/` — one prompt per visual asset.
- `asset-manifest.json` — filenames and source requirements.
