# Content OS

An agentic content intelligence system for an Instagram-first AI personal brand.

It discovers candidate AI topics, scores them, builds a balanced weekly
portfolio, writes Reel and carousel packages, puts every one through QA, and
records enough metadata to eventually learn which of its own decisions were
right.

The long-term value is not that a model writes captions. It is that after
50 to 100 posts, the stored history can answer which topics, hooks, formats,
and delivery modes actually work for this specific account, and which content
has earned paid amplification.

---

## The design rule everything follows

**Agents make contextual judgements. Python does everything deterministic.**

| Agents decide | Python computes |
|---|---|
| Is this topic interesting, and what is the angle | Weighted opportunity score |
| How strong is this topic on six dimensions, 0-10 | Time decay, saturation penalty, brand-fit veto |
| Which seven posts make a balanced week | Portfolio composition measurement and guardrails |
| What the hook, script, and slides should say | Engagement rates, percentiles, performance score |
| Whether the content is good, and why | The approve/reject decision against config thresholds |
| What the performance data means | Every number the analyst is shown |
| | Ad eligibility and budget caps |

No model ever computes a score, writes a database row, decides an approval, or
touches a spending decision.

---

## Pipeline

```
sources -> TrendScout -> Normalizer -> topics -> Scorer -> deterministic scoring
                                                     |
                                              Strategist (portfolio)
                                                /            \
                                       ReelWriter        CarouselWriter
                                                \            /
                                                   QA Editor
                                                       |
                                              deterministic gate
                                                       |
                                          content + creative variants
                                                       |
                                              human approval
                                                       |
                                            performance ingestion
                                                       |
                                           PerformanceAnalyst
                                                       |
                                        brand memory -> next cycle
```

The strategist is the manager. Specialists are invoked by workflows under its
plan rather than conversing with each other, so control and tracing stay intact.

---

## Setup

```bash
cd ~/Desktop/content_os
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt

cp .env.example .env        # then add your OPENAI_API_KEY
.venv/bin/python cli.py doctor
```

`doctor` validates every config file, confirms weights sum to 1.0, checks that
each configured prompt version has a file on disk, and reports which source
connectors are live.

---

## Quickstart

```bash
.venv/bin/python cli.py seed                        # experiments + brand snapshot
.venv/bin/python cli.py discover seeds/sources.json # find candidate topics
.venv/bin/python cli.py score                       # rate and rank them
.venv/bin/python cli.py plan --posts 7 --days 7     # balanced weekly portfolio
.venv/bin/python cli.py create-reel <topic-id>      # generate + QA a Reel
.venv/bin/python cli.py usage                       # token and cost ledger
```

Or the whole cycle in one command:

```bash
.venv/bin/python cli.py weekly
```

### Every command

| Command | Does |
|---|---|
| `doctor` | Validate config, environment, database, connectors, models |
| `seed` | Load the experiment backlog and snapshot brand memory |
| `sources` | List source connectors and which are implemented |
| `discover <file>` | Find candidate topics from source material |
| `score` | Rate unscored topics, `--all` to rescore |
| `topics` | List topics with scores and veto status |
| `plan` | Build a balanced portfolio, `--posts` and `--days` |
| `show-plan` | Print the latest plan and generation status |
| `create-reel <topic>` | Generate and QA a Reel package |
| `create-carousel <topic>` | Generate and QA a carousel package |
| `generate-plan` | Generate every planned item in the latest plan |
| `show <content-id>` | Full package, variants, QA history, cost |
| `ingest-performance <csv>` | Load metrics snapshots |
| `analyze` | Run the performance analyst |
| `leaderboard` | Performance by pillar, format, hook, delivery, duration |
| `ad-candidates` | Deterministic ad eligibility |
| `approve <content-id>` | Record human approval to publish |
| `usage` | Token and cost ledger, including cost per content item |
| `runs` | Recent workflow runs with status and spend |

---

## Scoring

Six dimensions, rated 0-10 by the scorer, weighted in `config/scoring.yaml`:

| Dimension | Weight |
|---|---|
| Brand fit | 30% |
| Audience fit | 20% |
| Trend velocity | 15% |
| Originality | 15% |
| Visual potential | 10% |
| Production fit | 10% |

Then three deterministic adjustments:

**Trend decay.** Velocity is multiplied by `0.5 ** (age_hours / half_life)`,
floored so it never reaches zero. Without this, a topic rated 9 for velocity
three days ago keeps winning the ranking forever.

**Saturation penalty.** `adjusted = base * (1 - max_penalty * saturation ** curve)`.
The exponent means mild saturation is barely punished and heavy saturation
collapses the score. High originality relieves effective saturation first, so an
ownable angle on a crowded theme is not treated like a generic one. A prompt
listicle collapses; a firsthand build does not.

**Brand-fit veto.** Below 5.0 brand fit, a topic is flagged
`TRENDING_BUT_OFF_BRAND` and cannot enter the portfolio no matter how high its
other dimensions are. This is the rule that stops the account becoming an AI-news
aggregator the first time something enormous trends.

Both raw and adjusted scores are stored, along with every component rating, the
model, the prompt version, and a fingerprint of the config that produced them.

---

## Tracking

Every entity carries a prefixed, time-sortable id, and the chain is walkable end
to end:

```
run -> topic -> score -> plan -> content -> creative variant
                                     |
                              post -> performance -> ad test
```

`agent_runs` records one row per agent invocation: model, prompt version, trace
id, token counts, estimated cost, duration, attempt number, and the error when it
failed. That table answers what a Reel costs to produce, which agent burns the
most tokens, and which workflows fail most often.

Traces are grouped by run id and tagged with topic id, content id, format, and
pillar, so a run in the OpenAI traces dashboard lines up with the rows in the
local database.

### History is append-only

The score, performance, QA, and token-ledger repositories expose **no update
method**. Not by convention, by absence. There is nothing to call by accident.

- Rescoring a topic inserts a new row and preserves the earlier verdict.
- A post measured at 24 hours and again at 7 days is two rows.
- Prompt and model metadata are written once and never touched.

Mutation is confined to topic status, content status, and lifecycle fields.

---

## Human-in-the-loop

Nothing publishes and nothing spends money. Both require a row in `approvals`
naming a human. `evaluate_ad_eligibility` can recommend a capped budget but has
no path to act on it, and every eligibility result carries
`requires_human_approval=True` with no code that clears it.

---

## Configuration

Business rules live in `config/`, never in prompts.

| File | Holds |
|---|---|
| `brand.yaml` | Positioning, pillars, audiences, signature opinions, hook patterns, production reality |
| `scoring.yaml` | Every weight, threshold, penalty curve, portfolio target, QA gate, ad gate |
| `models.yaml` | Model and prompt version per agent, reasoning effort, pricing, trace names |
| `experiments.yaml` | The experiment backlog |

Weights are validated on load. A set that does not sum to 1.0 fails at startup
rather than quietly skewing months of scoring.

### Model selection

Every agent names its model and reasoning effort in `config/models.yaml`. No
model name appears anywhere in the code.

| Agent | Model | Reasoning |
|---|---|---|
| trend_scout | gpt-5.6-terra | low |
| scorer | gpt-5.6-terra | medium |
| strategist | gpt-5.6-sol | medium |
| reel_writer | gpt-5.6-sol | medium |
| carousel_writer | gpt-5.6-sol | medium |
| qa | gpt-5.6-sol | high |
| performance_analyst | gpt-5.6-sol | high |
| normalizer | gpt-5.6-luna | low |

Sol handles the work where output quality is the product. Terra handles the
high-volume judgement work, where the scorer alone runs once per topic. Luna
handles dedup, tagging and canonicalization, which is high-volume but shallow.

The scorer stays on terra deliberately. Moving it to luna would cut most of the
weekly bill, but that is a change to make after benchmarking terra against luna
on the same scored topic set, comparing rank correlation, score divergence, and
downstream content performance. Same workload, the two are exactly 10x apart in
cost, which is what makes the comparison worth running rather than assuming.

### Pricing and the cost ledger

Rates are USD per million tokens, in the `pricing:` block of `models.yaml`.

| Model | Input | Cached input | Cache write | Output |
|---|---|---|---|---|
| gpt-5.6-sol | $4.00 | $0.40 | $5.00 | $20.00 |
| gpt-5.6-terra | $2.00 | $0.20 | $2.50 | $12.00 |
| gpt-5.6-luna | $0.20 | $0.02 | $0.25 | $1.20 |

Cache writes bill at 1.25x uncached input. A model can state its own
`cache_write_per_mtok`; otherwise the rate is derived from the input price using
`pricing_defaults.cache_write_multiplier`, so adding a model needs only the three
published numbers.

Cached and cache-write tokens are reported by the API as subsets of the total
prompt count, so they are subtracted out before the uncached rate is applied.
Billing them twice would inflate every figure in the ledger.

`agent_runs` records per call: agent, workflow, model, reasoning effort, prompt
version, trace id, topic and content id, requests, input tokens, cached input
tokens, cache-write tokens, output tokens, reasoning tokens, an itemised cost
split across all four billing classes, duration, attempt number, and the error if
it failed.

`cli.py usage` renders that as a per-agent table, a cache hit rate, and a cost
breakdown by billing class, plus cost per content item. When output dominates
the bill, the lever is reasoning effort and script length. When uncached input
dominates, the lever is prompt stability.

A model used by an agent but missing rates records zero cost rather than a
guessed one, and both `doctor` and `usage` warn about it. A ledger reading $0.00
looks exactly like a working ledger, so that has to be loud.

### Prompt and model versioning### Prompt and model versioning

Each agent names a prompt version in `models.yaml`, which maps to a file in
`prompts/`. That version and the model name are stored with every artifact.
Without this you cannot tell whether a better result came from a better topic, a
better prompt, or a better model.

To iterate: copy `prompts/reel_writer_v1.md` to `v2`, edit it, point
`models.yaml` at it. Old content keeps pointing at `v1` and remains comparable.

---

## Testing

```bash
.venv/bin/python -m pytest tests/ -q
```

112 tests, no API key needed, covering the weighted arithmetic against
hand-computed values, saturation monotonicity and bounds, the veto surviving
maximum trend velocity, rejection of ten-identical-posts plans, zero-denominator
metrics, multi-snapshot history, provenance metadata retention, creative-variant
linkage, QA gating independent of the agent's recommendation, and capped ad
budgets.

---

## What is stubbed

Schema and typed interfaces exist so later work is additive rather than a
rewrite. Nothing here is wired to an external service.

- **Source connectors**: X, Reddit, LinkedIn, Instagram, GitHub, arXiv, Hacker
  News, and model-release feeds are registered and raise a clear error. Only the
  manual JSON connector is implemented, and it is enough, since the intelligence
  layer does not care whether a link was pasted or fetched.
- **Ad tests**: table is live and eligibility is fully implemented against real
  percentile math. No API integration, and nothing writes there automatically.
- **Experiments**: table and backlog exist. Enrolling content is manual.
- **Publishing, avatar rendering, scheduling**: interfaces and the approval gate
  exist, implementations do not.

---

## Layout

```
content_os/
  agents/       eight agents, each one prompt + one structured output type
  tools/        scoring, metrics, analytics, ad eligibility, source ingestion
  models/       Pydantic schemas, agent-facing and persisted kept separate
  storage/      schema.sql, connection handling, repositories
  workflows/    discover, score, plan, create, ingest, analyze, weekly
  tracking/     TrackedRunner and the token ledger
config/         brand, scoring, models, experiments
prompts/        versioned prompt files
seeds/          sample source material and a performance CSV template
tests/          112 tests
cli.py
```
