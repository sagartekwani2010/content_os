"""Configuration loading and validation.

Business rules live in YAML, not in prompts. Weights are validated on load, so a
typo that makes a portfolio silently wrong fails at startup instead of quietly
skewing months of scoring.
"""

from __future__ import annotations

import hashlib
import math
import os
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field, ValidationError, model_validator

from content_os.models.brand import BrandMemory

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CONFIG_DIR = PROJECT_ROOT / "config"
PROMPTS_DIR = PROJECT_ROOT / "prompts"

WEIGHT_TOLERANCE = 1e-6


class ConfigError(RuntimeError):
    """Raised when configuration is missing or internally inconsistent."""


# --------------------------------------------------------------------------
# Scoring config
# --------------------------------------------------------------------------


class OpportunityWeights(BaseModel):
    brand_fit: float
    audience_fit: float
    trend_velocity: float
    originality: float
    visual_potential: float
    production_fit: float

    @model_validator(mode="after")
    def _weights_sum_to_one(self) -> "OpportunityWeights":
        total = sum(self.model_dump().values())
        if abs(total - 1.0) > WEIGHT_TOLERANCE:
            raise ValueError(
                f"opportunity_score.weights must sum to 1.0, got {total:.6f}. "
                f"Fix config/scoring.yaml."
            )
        return self

    def as_dict(self) -> dict[str, float]:
        return self.model_dump()


class OpportunityScoreConfig(BaseModel):
    weights: OpportunityWeights
    dimension_min: float = 0.0
    dimension_max: float = 10.0


class BrandFitVetoConfig(BaseModel):
    threshold: float = 5.0
    flag: str = "TRENDING_BUT_OFF_BRAND"
    allow_human_override: bool = True


class SaturationConfig(BaseModel):
    max_penalty: float = Field(ge=0.0, le=1.0, default=0.60)
    curve: float = Field(gt=0.0, default=1.5)
    originality_offset: bool = True
    originality_pivot: float = 7.0
    originality_relief_per_point: float = 0.08


class TrendDecayConfig(BaseModel):
    enabled: bool = True
    half_life_hours: float = Field(gt=0.0, default=72.0)
    floor_fraction: float = Field(ge=0.0, le=1.0, default=0.15)


class PortfolioConfig(BaseModel):
    targets: dict[str, float]
    tolerance: float = 0.15
    max_per_pillar: int = 3
    min_distinct_pillars: int = 3
    max_same_format_streak: int = 3

    def pillar_cap(self, total_posts: int) -> int:
        """Hard ceiling on posts per pillar, scaled to the size of the plan.

        A fixed cap is a weekly-scale rule. At fifteen posts a cap of three
        directly contradicts a 30% target, which wants four and a half, and
        hands the strategist constraints it cannot satisfy.

        Deriving the cap from the largest target plus tolerance means it can
        never fight the distribution it is meant to protect. It stays a backstop
        against genuine concentration rather than a second, competing target.
        """
        if not self.targets:
            return self.max_per_pillar
        ceiling_share = max(self.targets.values()) + self.tolerance
        scaled = math.ceil(total_posts * ceiling_share)
        return max(self.max_per_pillar, scaled)

    @model_validator(mode="after")
    def _targets_sum_to_one(self) -> "PortfolioConfig":
        total = sum(self.targets.values())
        if abs(total - 1.0) > 1e-3:
            raise ValueError(
                f"portfolio.targets must sum to 1.0, got {total:.4f}. "
                f"Fix config/scoring.yaml."
            )
        return self


class NormalisationConfig(BaseModel):
    method: str = "percentile"
    lookback_posts: int = 30
    min_history_for_percentile: int = 5
    fallback_anchors: dict[str, float] = Field(default_factory=dict)


class PerformanceScoreConfig(BaseModel):
    weights: dict[str, float]
    normalisation: NormalisationConfig = Field(default_factory=NormalisationConfig)

    @model_validator(mode="after")
    def _weights_sum_to_one(self) -> "PerformanceScoreConfig":
        total = sum(self.weights.values())
        if abs(total - 1.0) > WEIGHT_TOLERANCE:
            raise ValueError(
                f"performance_score.weights must sum to 1.0, got {total:.6f}. "
                f"Fix config/scoring.yaml."
            )
        return self


class AdBudgetConfig(BaseModel):
    base_daily: float = 10.0
    max_daily: float = 50.0
    max_total: float = 250.0
    scale_per_percentile_point: float = 0.5


class AdEligibilityConfig(BaseModel):
    min_performance_percentile: float = 70.0
    min_profile_visit_percentile: float = 60.0
    min_follow_conversion_percentile: float = 60.0
    min_share_percentile: float = 50.0
    min_brand_fit: float = 6.0
    min_days_since_publish: int = 3
    max_days_since_publish: int = 45
    budget: AdBudgetConfig = Field(default_factory=AdBudgetConfig)


class QAGatesConfig(BaseModel):
    """Thresholds the QA verdict is checked against in Python.

    The agent recommends; config decides. This keeps the approval bar stable
    even when the QA prompt is edited.
    """

    min_composite: float = 6.5
    min_hook_strength: float = 6.0
    min_technical_accuracy: float = 7.0
    min_brand_fit: float = 6.0
    min_originality: float = 5.0
    max_ai_hype_penalty: float = 4.0
    max_generic_content_penalty: float = 4.0
    composite_weights: dict[str, float] = Field(
        default_factory=lambda: {
            "hook_strength": 0.25,
            "clarity": 0.10,
            "technical_accuracy": 0.15,
            "brand_fit": 0.15,
            "originality": 0.15,
            "share_potential": 0.10,
            "save_potential": 0.05,
            "visual_potential": 0.05,
        }
    )
    penalty_weight: float = 0.5


class ScoringConfig(BaseModel):
    opportunity_score: OpportunityScoreConfig
    brand_fit_veto: BrandFitVetoConfig = Field(default_factory=BrandFitVetoConfig)
    saturation: SaturationConfig = Field(default_factory=SaturationConfig)
    trend_decay: TrendDecayConfig = Field(default_factory=TrendDecayConfig)
    portfolio: PortfolioConfig
    performance_score: PerformanceScoreConfig
    ad_eligibility: AdEligibilityConfig = Field(default_factory=AdEligibilityConfig)
    qa_gates: QAGatesConfig = Field(default_factory=QAGatesConfig)

    version: str = "unversioned"


# --------------------------------------------------------------------------
# Model config
# --------------------------------------------------------------------------


class AgentModelConfig(BaseModel):
    model: str
    prompt_version: str
    reasoning_effort: str | None = None
    verbosity: str | None = None
    max_turns: int | None = None


class ModelDefaults(BaseModel):
    model: str = "gpt-5"
    reasoning_effort: str | None = "medium"
    verbosity: str | None = "medium"
    max_turns: int = 12
    structured_output_retries: int = 1


class ModelPricing(BaseModel):
    """USD per million tokens, split by how the tokens were billed.

    Cache writes are charged at a premium over normal uncached input. When a
    model omits an explicit cache-write rate it is derived from the input rate
    using the configured multiplier, so adding a model only requires the three
    published numbers.
    """

    input_per_mtok: float = 0.0
    cached_input_per_mtok: float = 0.0
    output_per_mtok: float = 0.0
    cache_write_per_mtok: float | None = None

    def cache_write_rate(self, multiplier: float) -> float:
        if self.cache_write_per_mtok is not None:
            return self.cache_write_per_mtok
        return round(self.input_per_mtok * multiplier, 6)

    @property
    def is_priced(self) -> bool:
        return self.input_per_mtok > 0.0 or self.output_per_mtok > 0.0


class PricingDefaults(BaseModel):
    cache_write_multiplier: float = 1.25


class TracingConfig(BaseModel):
    enabled: bool = True
    workflows: dict[str, str] = Field(default_factory=dict)


class TokenCost(BaseModel):
    """A fully itemised cost for one agent invocation."""

    uncached_input_tokens: int = 0
    cached_input_tokens: int = 0
    cache_write_tokens: int = 0
    output_tokens: int = 0

    uncached_input_cost: float = 0.0
    cached_input_cost: float = 0.0
    cache_write_cost: float = 0.0
    output_cost: float = 0.0
    total_cost: float = 0.0

    priced: bool = True


class ModelsConfig(BaseModel):
    defaults: ModelDefaults = Field(default_factory=ModelDefaults)
    pricing_defaults: PricingDefaults = Field(default_factory=PricingDefaults)
    agents: dict[str, AgentModelConfig] = Field(default_factory=dict)
    pricing: dict[str, ModelPricing] = Field(default_factory=dict)
    tracing: TracingConfig = Field(default_factory=TracingConfig)

    def for_agent(self, name: str) -> AgentModelConfig:
        cfg = self.agents.get(name)
        if cfg is None:
            raise ConfigError(
                f"No model configuration for agent '{name}'. "
                f"Add it under 'agents:' in config/models.yaml."
            )
        return cfg

    def resolved(self, name: str) -> AgentModelConfig:
        """Agent config with defaults filled in."""
        cfg = self.for_agent(name)
        return AgentModelConfig(
            model=cfg.model or self.defaults.model,
            prompt_version=cfg.prompt_version,
            reasoning_effort=cfg.reasoning_effort or self.defaults.reasoning_effort,
            verbosity=cfg.verbosity or self.defaults.verbosity,
            max_turns=cfg.max_turns or self.defaults.max_turns,
        )

    def workflow_name(self, key: str) -> str:
        return self.tracing.workflows.get(key, key)

    def price(self, model: str) -> ModelPricing:
        if model in self.pricing:
            return self.pricing[model]
        # Unknown model: record zero cost rather than guessing wrong numbers.
        return ModelPricing()

    def compute_cost(
        self,
        model: str,
        *,
        input_tokens: int,
        output_tokens: int,
        cached_input_tokens: int = 0,
        cache_write_tokens: int = 0,
    ) -> TokenCost:
        """Itemise the cost of one call.

        input_tokens from the API is the full prompt count, with cached and
        cache-write tokens reported as subsets of it. Billing them at the
        uncached rate as well would double-count, so they are subtracted out and
        charged at their own rates. Every component is clamped at zero, because
        a provider reporting an unexpected split must not produce negative spend.
        """
        pricing = self.price(model)
        multiplier = self.pricing_defaults.cache_write_multiplier

        cached = max(0, cached_input_tokens)
        written = max(0, cache_write_tokens)
        uncached = max(0, input_tokens - cached - written)
        out = max(0, output_tokens)

        per_token = 1_000_000.0
        uncached_cost = uncached * pricing.input_per_mtok / per_token
        cached_cost = cached * pricing.cached_input_per_mtok / per_token
        write_cost = written * pricing.cache_write_rate(multiplier) / per_token
        output_cost = out * pricing.output_per_mtok / per_token

        return TokenCost(
            uncached_input_tokens=uncached,
            cached_input_tokens=cached,
            cache_write_tokens=written,
            output_tokens=out,
            uncached_input_cost=round(uncached_cost, 8),
            cached_input_cost=round(cached_cost, 8),
            cache_write_cost=round(write_cost, 8),
            output_cost=round(output_cost, 8),
            total_cost=round(
                uncached_cost + cached_cost + write_cost + output_cost, 8
            ),
            priced=pricing.is_priced,
        )


# --------------------------------------------------------------------------
# Loading
# --------------------------------------------------------------------------


def _read_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise ConfigError(f"Missing configuration file: {path}")
    with path.open("r", encoding="utf-8") as fh:
        data = yaml.safe_load(fh)
    if not isinstance(data, dict):
        raise ConfigError(f"{path} must contain a YAML mapping at the top level.")
    return data


def _fingerprint(path: Path) -> str:
    """Short content hash, stored with every score so we can tell which config
    produced a historical number."""
    return hashlib.sha256(path.read_bytes()).hexdigest()[:12]


@lru_cache(maxsize=1)
def load_scoring_config(config_dir: str | None = None) -> ScoringConfig:
    path = Path(config_dir or CONFIG_DIR) / "scoring.yaml"
    raw = _read_yaml(path)
    try:
        cfg = ScoringConfig(**raw)
    except ValidationError as exc:
        raise ConfigError(f"Invalid config/scoring.yaml:\n{exc}") from exc
    cfg.version = _fingerprint(path)
    return cfg


@lru_cache(maxsize=1)
def load_models_config(config_dir: str | None = None) -> ModelsConfig:
    path = Path(config_dir or CONFIG_DIR) / "models.yaml"
    raw = _read_yaml(path)
    try:
        return ModelsConfig(**raw)
    except ValidationError as exc:
        raise ConfigError(f"Invalid config/models.yaml:\n{exc}") from exc


@lru_cache(maxsize=1)
def load_brand(config_dir: str | None = None) -> BrandMemory:
    path = Path(config_dir or CONFIG_DIR) / "brand.yaml"
    raw = _read_yaml(path)
    try:
        return BrandMemory(**raw)
    except ValidationError as exc:
        raise ConfigError(f"Invalid config/brand.yaml:\n{exc}") from exc


@lru_cache(maxsize=1)
def load_experiments_config(config_dir: str | None = None) -> list[dict[str, Any]]:
    path = Path(config_dir or CONFIG_DIR) / "experiments.yaml"
    raw = _read_yaml(path)
    return list(raw.get("experiments", []))


@lru_cache(maxsize=32)
def load_prompt(version: str, prompts_dir: str | None = None) -> str:
    """Load a versioned prompt by its version string.

    The version is the filename stem, so 'reel_writer_v1' maps to
    prompts/reel_writer_v1.md. Prompt text is never inlined in Python, and the
    version is stored with every artifact it produced.
    """
    path = Path(prompts_dir or PROMPTS_DIR) / f"{version}.md"
    if not path.exists():
        raise ConfigError(
            f"Missing prompt file {path}. "
            f"Every prompt_version in config/models.yaml needs a matching .md file."
        )
    return path.read_text(encoding="utf-8")


def config_warnings() -> list[str]:
    """Non-fatal problems worth surfacing before a run.

    A model with no pricing entry still works; it just records zero cost, which
    would quietly make the token ledger useless. That has to be visible rather
    than silent, since the ledger is the whole point of tracking spend.
    """
    warnings: list[str] = []
    try:
        models = load_models_config()
    except Exception:
        return warnings

    for agent_name in models.agents:
        model = models.resolved(agent_name).model
        pricing = models.pricing.get(model)
        if pricing is None:
            warnings.append(
                f"agent '{agent_name}' uses model '{model}', which has no entry "
                f"under 'pricing:' in config/models.yaml. Cost will record as $0."
            )
        elif not pricing.is_priced:
            warnings.append(
                f"model '{model}' is configured at zero cost. Fill in real rates "
                f"under 'pricing:' or the cost ledger will read $0 for every call."
            )

    return sorted(set(warnings))


def validate_all() -> list[str]:
    """Load every config file and report problems. Used by `cli.py doctor`."""
    problems: list[str] = []
    for loader, label in (
        (load_scoring_config, "scoring.yaml"),
        (load_models_config, "models.yaml"),
        (load_brand, "brand.yaml"),
        (load_experiments_config, "experiments.yaml"),
    ):
        try:
            loader()
        except Exception as exc:  # noqa: BLE001 - surfaced to the operator
            problems.append(f"{label}: {exc}")

    # Every configured prompt version must exist on disk.
    try:
        models = load_models_config()
        for agent_name, cfg in models.agents.items():
            try:
                load_prompt(cfg.prompt_version)
            except ConfigError as exc:
                problems.append(f"agent '{agent_name}': {exc}")
    except Exception:
        pass

    # Portfolio pillar keys must exist in brand.yaml.
    try:
        scoring = load_scoring_config()
        brand = load_brand()
        unknown = set(scoring.portfolio.targets) - set(brand.pillar_keys)
        if unknown:
            problems.append(
                f"portfolio.targets references pillars not defined in brand.yaml: "
                f"{sorted(unknown)}"
            )
    except Exception:
        pass

    return problems


def db_path() -> Path:
    return Path(os.environ.get("CONTENT_OS_DB", PROJECT_ROOT / "content_os.db"))


def reset_caches() -> None:
    """Clear cached config. Used by tests that write temporary config files."""
    for fn in (
        load_scoring_config,
        load_models_config,
        load_brand,
        load_experiments_config,
        load_prompt,
    ):
        fn.cache_clear()
