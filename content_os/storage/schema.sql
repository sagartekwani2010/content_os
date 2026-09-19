-- Content OS schema.
--
-- Design rule: history is append-only wherever it is evidence.
--   * opportunity_scores, post_performance, agent_runs, qa_results are
--     INSERT-only. A rescore or a re-measurement writes a new row.
--   * Only topics.status and content_items.status/publish dates mutate.
-- This is what makes it possible, after 100 posts, to ask which scoring
-- dimension actually predicted performance.

PRAGMA foreign_keys = ON;

-- ---------------------------------------------------------------- runs

CREATE TABLE IF NOT EXISTS runs (
    id               TEXT PRIMARY KEY,
    workflow         TEXT NOT NULL,
    started_at       TEXT NOT NULL,
    completed_at     TEXT,
    status           TEXT NOT NULL DEFAULT 'RUNNING',
    args_json        TEXT,
    notes            TEXT
);

-- Per-agent-invocation ledger. Mandatory: this is how we answer
-- "what does one Reel cost" and "which agent burns the most tokens".
CREATE TABLE IF NOT EXISTS agent_runs (
    id                TEXT PRIMARY KEY,
    run_id            TEXT REFERENCES runs(id),
    workflow_name     TEXT NOT NULL,
    agent_name        TEXT NOT NULL,
    trace_id          TEXT,

    topic_id          TEXT,
    content_id        TEXT,

    model             TEXT NOT NULL,
    prompt_version    TEXT NOT NULL,

    started_at        TEXT NOT NULL,
    completed_at      TEXT,
    duration_ms       INTEGER,
    status            TEXT NOT NULL,

    -- Reasoning effort is stored per call, not just per config, because it is
    -- changed between runs and is a prime suspect when cost or quality moves.
    reasoning_effort  TEXT,

    requests          INTEGER DEFAULT 0,
    input_tokens      INTEGER DEFAULT 0,
    cached_input_tokens INTEGER DEFAULT 0,
    cache_write_tokens  INTEGER DEFAULT 0,
    output_tokens     INTEGER DEFAULT 0,
    reasoning_tokens  INTEGER DEFAULT 0,
    total_tokens      INTEGER DEFAULT 0,

    -- Itemised so a cost spike can be attributed to cache misses, cache writes,
    -- or runaway reasoning output rather than guessed at.
    uncached_input_cost REAL DEFAULT 0.0,
    cached_input_cost   REAL DEFAULT 0.0,
    cache_write_cost    REAL DEFAULT 0.0,
    output_cost         REAL DEFAULT 0.0,
    estimated_cost    REAL DEFAULT 0.0,
    pricing_known     INTEGER DEFAULT 1,

    attempt           INTEGER DEFAULT 1,
    error_type        TEXT,
    error_message     TEXT
);

CREATE INDEX IF NOT EXISTS idx_agent_runs_run    ON agent_runs(run_id);
CREATE INDEX IF NOT EXISTS idx_agent_runs_agent  ON agent_runs(agent_name);
CREATE INDEX IF NOT EXISTS idx_agent_runs_content ON agent_runs(content_id);

-- ---------------------------------------------------------------- topics

CREATE TABLE IF NOT EXISTS topics (
    id                  TEXT PRIMARY KEY,
    canonical_topic     TEXT NOT NULL,
    title               TEXT NOT NULL,
    description         TEXT,

    discovered_at       TEXT NOT NULL,
    event_date          TEXT,

    source_count        INTEGER DEFAULT 0,
    source_urls_json    TEXT,
    source_types_json   TEXT,

    trend_signals_json  TEXT,
    target_audience_json TEXT,
    potential_angles_json TEXT,
    content_pillars_json TEXT,

    trend_velocity      REAL,
    saturation          REAL DEFAULT 0.0,

    why_it_matters      TEXT,
    discussion_angle    TEXT,

    status              TEXT NOT NULL DEFAULT 'CANDIDATE',
    run_id              TEXT REFERENCES runs(id),

    created_at          TEXT NOT NULL,
    updated_at          TEXT NOT NULL
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_topics_canonical ON topics(canonical_topic);
CREATE INDEX IF NOT EXISTS idx_topics_status ON topics(status);

-- Append-only. Never UPDATE. A rescore inserts a new row.
CREATE TABLE IF NOT EXISTS opportunity_scores (
    id                     TEXT PRIMARY KEY,
    topic_id               TEXT NOT NULL REFERENCES topics(id),
    run_id                 TEXT REFERENCES runs(id),

    brand_fit              REAL NOT NULL,
    audience_fit           REAL NOT NULL,
    trend_velocity         REAL NOT NULL,
    originality            REAL NOT NULL,
    visual_potential       REAL NOT NULL,
    production_fit         REAL NOT NULL,

    decayed_trend_velocity REAL NOT NULL,
    base_score             REAL NOT NULL,
    saturation             REAL NOT NULL,
    effective_saturation   REAL NOT NULL,
    saturation_penalty     REAL NOT NULL,
    adjusted_score         REAL NOT NULL,

    vetoed                 INTEGER NOT NULL DEFAULT 0,
    veto_flag              TEXT,

    scoring_model          TEXT NOT NULL,
    scoring_prompt_version TEXT NOT NULL,
    scoring_config_version TEXT NOT NULL,

    rationale              TEXT,
    recommended_pillar     TEXT,
    recommended_format     TEXT,

    created_at             TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_scores_topic ON opportunity_scores(topic_id, created_at DESC);

-- ---------------------------------------------------------------- content

CREATE TABLE IF NOT EXISTS content_plans (
    id                 TEXT PRIMARY KEY,
    run_id             TEXT REFERENCES runs(id),
    created_at         TEXT NOT NULL,
    horizon_days       INTEGER,
    target_posts       INTEGER,
    portfolio_rationale TEXT,
    composition_json   TEXT,
    balance_report_json TEXT
);

CREATE TABLE IF NOT EXISTS content_items (
    id                       TEXT PRIMARY KEY,
    topic_id                 TEXT NOT NULL REFERENCES topics(id),
    plan_id                  TEXT REFERENCES content_plans(id),
    run_id                   TEXT REFERENCES runs(id),

    format                   TEXT NOT NULL,
    pillar                   TEXT NOT NULL,
    strategic_role           TEXT,

    title                    TEXT NOT NULL,
    hook                     TEXT,
    body_json                TEXT,
    caption                  TEXT,
    cta                      TEXT,

    avatar_used              INTEGER DEFAULT 0,
    human_used               INTEGER DEFAULT 0,
    screen_demo_used         INTEGER DEFAULT 0,

    status                   TEXT NOT NULL DEFAULT 'IDEA',

    planned_publish_date     TEXT,
    actual_publish_date      TEXT,
    platform_post_id         TEXT,

    urgency                  TEXT,
    strategist_reasoning     TEXT,
    strategist_score         REAL,

    -- Provenance, never overwritten.
    generator_agent          TEXT,
    generator_model          TEXT,
    generator_prompt_version TEXT,

    -- Human strategy from the brief, preserved through to publication.
    brief_id                 TEXT,
    core_thesis              TEXT,
    learning_objective       TEXT,
    hook_direction           TEXT,
    approved_hook_points_json TEXT,
    high_level_sections_json TEXT,
    preferred_pov            TEXT,
    visual_direction         TEXT,

    hook_strategy            TEXT,
    hook_source              TEXT,
    hook_variant_id          TEXT,

    learning_payoff          TEXT,
    save_reason              TEXT,
    share_reason             TEXT,
    sections_covered_json    TEXT,

    qa_approved              INTEGER,
    qa_composite             REAL,
    qa_json                  TEXT,

    approved_by              TEXT,
    approved_at              TEXT,

    created_at               TEXT NOT NULL,
    updated_at               TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_content_topic  ON content_items(topic_id);
CREATE INDEX IF NOT EXISTS idx_content_status ON content_items(status);
CREATE INDEX IF NOT EXISTS idx_content_pillar ON content_items(pillar);

CREATE TABLE IF NOT EXISTS creative_variants (
    id               TEXT PRIMARY KEY,
    content_id       TEXT NOT NULL REFERENCES content_items(id),

    variant_type     TEXT NOT NULL,
    label            TEXT,

    hook             TEXT,
    script           TEXT,
    visual_style     TEXT,
    duration_seconds INTEGER,

    is_control       INTEGER DEFAULT 0,
    experiment_id    TEXT REFERENCES experiments(id),

    created_at       TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_variants_content ON creative_variants(content_id);

-- Append-only QA history. A revision writes a new row.
CREATE TABLE IF NOT EXISTS qa_results (
    id                 TEXT PRIMARY KEY,
    content_id         TEXT NOT NULL REFERENCES content_items(id),
    run_id             TEXT REFERENCES runs(id),

    revision_number    INTEGER NOT NULL DEFAULT 0,
    approved           INTEGER NOT NULL,
    composite          REAL NOT NULL,
    scores_json        TEXT NOT NULL,
    issues_json        TEXT,
    required_changes_json TEXT,
    failed_gates_json  TEXT,
    agent_recommends_approval INTEGER,
    verdict_rationale  TEXT,

    qa_model           TEXT,
    qa_prompt_version  TEXT,

    created_at         TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_qa_content ON qa_results(content_id, revision_number);


-- ---------------------------------------------------------------- briefs

-- Human strategy. The authoritative input to production.
--
-- Backlog fields live on this table rather than in a separate content_backlog,
-- because every backlog column would otherwise be a copy of a brief column and
-- copies drift. Query it through the backlog view instead.
CREATE TABLE IF NOT EXISTS content_briefs (
    brief_id                 TEXT PRIMARY KEY,

    topic                    TEXT NOT NULL,
    core_thesis              TEXT NOT NULL,
    why_this_matters         TEXT,
    audience_takeaway        TEXT,
    learning_objective       TEXT NOT NULL,

    target_audience_json     TEXT,
    brand_pillar             TEXT NOT NULL,
    content_format           TEXT NOT NULL,

    hook_direction           TEXT,
    approved_hook_points_json TEXT,

    high_level_sections_json TEXT,
    core_examples_json       TEXT,

    preferred_pov            TEXT,
    desired_tone             TEXT,
    visual_direction         TEXT,

    desired_duration_seconds INTEGER,
    desired_slide_count      INTEGER,

    references_json          TEXT,
    factual_claims_json      TEXT,
    must_include_json        TEXT,
    must_avoid_json          TEXT,

    cta_direction            TEXT,
    urgency                  TEXT NOT NULL DEFAULT 'evergreen',
    notes                    TEXT,

    -- Backlog / workflow state.
    status                   TEXT NOT NULL DEFAULT 'DRAFT',
    priority                 INTEGER DEFAULT 3,
    scheduled_date           TEXT,
    created_at               TEXT NOT NULL,
    approved_at              TEXT,
    approved_by              TEXT,
    published_at             TEXT,

    -- Full object, so a brief can be reconstructed exactly as approved.
    brief_json               TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_briefs_status ON content_briefs(status, priority);

-- Execution plans. Append-only: replanning a brief writes a new row so the
-- plan that actually produced a piece of content stays recoverable.
CREATE TABLE IF NOT EXISTS execution_plans (
    id                 TEXT PRIMARY KEY,
    brief_id           TEXT NOT NULL REFERENCES content_briefs(brief_id),
    run_id             TEXT REFERENCES runs(id),

    format             TEXT NOT NULL,
    plan_json          TEXT NOT NULL,

    alternate_format_recommendation TEXT,
    alternate_format_reason         TEXT,
    risks_json         TEXT,

    model              TEXT,
    prompt_version     TEXT,
    created_at         TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_plans_brief ON execution_plans(brief_id);

-- Every hook considered, not just the one used. Hook approach is a variable we
-- intend to correlate with performance, which requires keeping the losers.
CREATE TABLE IF NOT EXISTS hook_variants (
    id                 TEXT PRIMARY KEY,
    brief_id           TEXT REFERENCES content_briefs(brief_id),
    content_id         TEXT REFERENCES content_items(id),

    variant_id         TEXT NOT NULL,
    text               TEXT NOT NULL,
    hook_strategy      TEXT,
    hook_source        TEXT NOT NULL,
    derived_from_point TEXT,
    rationale          TEXT,
    is_selected        INTEGER DEFAULT 0,

    model              TEXT,
    prompt_version     TEXT,
    created_at         TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_hooks_brief ON hook_variants(brief_id);
CREATE INDEX IF NOT EXISTS idx_hooks_content ON hook_variants(content_id);

-- ---------------------------------------------------------------- performance

-- Append-only. A post measured at 24h and again at 7d is two rows.
CREATE TABLE IF NOT EXISTS post_performance (
    id                       TEXT PRIMARY KEY,
    content_id               TEXT NOT NULL REFERENCES content_items(id),
    creative_id              TEXT REFERENCES creative_variants(id),
    platform_post_id         TEXT,

    snapshot_time            TEXT NOT NULL,
    followers_at_post_time   INTEGER,

    impressions              INTEGER DEFAULT 0,
    reach                    INTEGER DEFAULT 0,
    follower_reach           INTEGER DEFAULT 0,
    non_follower_reach       INTEGER DEFAULT 0,

    plays                    INTEGER DEFAULT 0,
    avg_watch_time_seconds   REAL DEFAULT 0,
    total_watch_time_seconds REAL DEFAULT 0,
    video_duration_seconds   REAL DEFAULT 0,

    likes                    INTEGER DEFAULT 0,
    comments                 INTEGER DEFAULT 0,
    shares                   INTEGER DEFAULT 0,
    sends                    INTEGER DEFAULT 0,
    saves                    INTEGER DEFAULT 0,

    profile_visits           INTEGER DEFAULT 0,
    new_followers            INTEGER DEFAULT 0,
    website_clicks           INTEGER DEFAULT 0,

    organic_impressions      INTEGER DEFAULT 0,
    paid_impressions         INTEGER DEFAULT 0,

    created_at               TEXT NOT NULL
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_perf_snapshot
    ON post_performance(content_id, snapshot_time, COALESCE(creative_id, ''));
CREATE INDEX IF NOT EXISTS idx_perf_content ON post_performance(content_id);

-- ---------------------------------------------------------------- experiments

CREATE TABLE IF NOT EXISTS experiments (
    id                 TEXT PRIMARY KEY,
    name               TEXT NOT NULL UNIQUE,
    hypothesis         TEXT NOT NULL,

    variable           TEXT NOT NULL,
    control            TEXT NOT NULL,
    variant            TEXT NOT NULL,

    start_date         TEXT,
    end_date           TEXT,

    primary_metric     TEXT NOT NULL,
    secondary_metrics_json TEXT,

    status             TEXT NOT NULL DEFAULT 'DESIGNED',

    result             TEXT,
    confidence_notes   TEXT,

    created_at         TEXT NOT NULL
);

-- ---------------------------------------------------------------- paid media

-- Schema only for v1. Nothing writes here automatically and no code path can
-- spend money without an explicit human approval record.
CREATE TABLE IF NOT EXISTS ad_tests (
    id                        TEXT PRIMARY KEY,
    content_id                TEXT NOT NULL REFERENCES content_items(id),
    creative_id               TEXT REFERENCES creative_variants(id),

    audience_name             TEXT NOT NULL,

    start_date                TEXT,
    end_date                  TEXT,

    daily_budget              REAL DEFAULT 0,
    total_spend               REAL DEFAULT 0,

    objective                 TEXT,
    status                    TEXT NOT NULL DEFAULT 'PROPOSED',

    paid_reach                INTEGER DEFAULT 0,
    paid_impressions          INTEGER DEFAULT 0,
    paid_profile_visits       INTEGER DEFAULT 0,
    paid_followers            INTEGER DEFAULT 0,

    cost_per_profile_visit    REAL,
    cost_per_follower         REAL,
    quality_adjusted_followers REAL,
    quality_adjusted_cpf      REAL,

    approved_by               TEXT,
    approved_at               TEXT,

    created_at                TEXT NOT NULL
);

-- Audit trail for every human gate: publishing, spending, positioning changes.
CREATE TABLE IF NOT EXISTS approvals (
    id             TEXT PRIMARY KEY,
    subject_type   TEXT NOT NULL,
    subject_id     TEXT NOT NULL,
    action         TEXT NOT NULL,
    decision       TEXT NOT NULL,
    approved_by    TEXT NOT NULL,
    notes          TEXT,
    created_at     TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_approvals_subject ON approvals(subject_type, subject_id);

-- ---------------------------------------------------------------- brand memory

-- Append-only snapshots so a positioning change is always reversible and the
-- brand memory in force at generation time can be reconstructed.
CREATE TABLE IF NOT EXISTS brand_memory_snapshots (
    id            TEXT PRIMARY KEY,
    version       INTEGER NOT NULL,
    memory_json   TEXT NOT NULL,
    source        TEXT NOT NULL,
    change_note   TEXT,
    created_at    TEXT NOT NULL
);

-- Findings emitted by the performance analyst, typed so a hypothesis is never
-- mistaken for an observation when it feeds back into scoring.
CREATE TABLE IF NOT EXISTS analyst_findings (
    id                TEXT PRIMARY KEY,
    run_id            TEXT REFERENCES runs(id),
    claim_type        TEXT NOT NULL,
    statement         TEXT NOT NULL,
    supporting_metric TEXT,
    sample_size       INTEGER,
    confidence        TEXT,
    caveats_json      TEXT,
    created_at        TEXT NOT NULL
);
