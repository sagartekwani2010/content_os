"""Claude stage orchestration and local invocation tracking.

Each content stage remains an independent agent with a versioned prompt and a
Pydantic output contract. The runner sends that stage to Claude through the
backend chosen in `content_os.llm_runtime` (Anthropic Messages API when API
credentials exist, otherwise the Claude Agent SDK on the local Claude Code
login), then validates and persists the result before the next stage sees it.
"""

from __future__ import annotations

import asyncio
import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Generic, TypeVar

from pydantic import BaseModel, ValidationError

from content_os.config import ModelsConfig, load_models_config, load_prompt
from content_os.llm_runtime import (
    LLMBackend,
    StageRequest,
    StageResponse,
    get_backend,
)
from content_os.storage.repositories import Repositories

T = TypeVar("T", bound=BaseModel)
PROJECT_ROOT = Path(__file__).resolve().parents[2]


@dataclass(frozen=True)
class ModelSettings:
    model: str
    reasoning_effort: str | None
    provider: str = "anthropic"
    max_tokens: int = 16000
    max_turns: int | None = None
    server_fallbacks: bool = False


@dataclass(frozen=True)
class StageAgent:
    """The stable, typed description of one coordination stage."""

    name: str
    instructions: str
    output_type: type[BaseModel] | None
    model_settings: ModelSettings


@dataclass
class TrackedResult(Generic[T]):
    output: T
    agent_name: str
    model: str
    prompt_version: str
    trace_id: str | None
    agent_run_id: str
    attempts: int
    reasoning_effort: str | None = None
    input_tokens: int = 0
    cached_input_tokens: int = 0
    cache_write_tokens: int = 0
    output_tokens: int = 0
    reasoning_tokens: int = 0
    total_tokens: int = 0
    estimated_cost: float = 0.0
    pricing_known: bool = False
    duration_ms: int = 0
    backend: str | None = None
    raw: Any = field(default=None, repr=False)

    @property
    def cache_hit_rate(self) -> float:
        return self.cached_input_tokens / self.input_tokens if self.input_tokens else 0.0


class AgentRunError(RuntimeError):
    def __init__(self, agent_name: str, attempts: int, cause: Exception) -> None:
        super().__init__(
            f"Claude stage '{agent_name}' failed after {attempts} attempt(s): "
            f"{type(cause).__name__}: {cause}"
        )
        self.agent_name = agent_name
        self.attempts = attempts
        self.cause = cause


def extract_usage(usage: Any) -> dict[str, int]:
    """Normalise a generic usage object (attribute names as the ledger uses)."""
    input_details = getattr(usage, "input_tokens_details", None)
    output_details = getattr(usage, "output_tokens_details", None)
    return {
        "requests": int(getattr(usage, "requests", 0) or 0),
        "input_tokens": int(getattr(usage, "input_tokens", 0) or 0),
        "cached_input_tokens": int(
            getattr(input_details, "cached_tokens", None)
            or getattr(usage, "cached_input_tokens", 0)
            or 0
        ),
        "cache_write_tokens": int(
            getattr(input_details, "cache_write_tokens", None)
            or getattr(usage, "cache_write_input_tokens", 0)
            or 0
        ),
        "output_tokens": int(getattr(usage, "output_tokens", 0) or 0),
        "reasoning_tokens": int(
            getattr(output_details, "reasoning_tokens", None)
            or getattr(usage, "reasoning_output_tokens", 0)
            or 0
        ),
        "total_tokens": int(getattr(usage, "total_tokens", 0) or 0),
    }


def build_model_settings(
    model: str,
    reasoning_effort: str | None,
    verbosity: str | None = None,
    **extra: Any,
) -> ModelSettings:
    """`verbosity` is accepted for compatibility; Claude has no such knob."""
    del verbosity
    return ModelSettings(model, reasoning_effort, **extra)


def build_agent(
    agent_key: str,
    *,
    instructions: str,
    output_type: type[BaseModel] | None = None,
    tools: list[Any] | None = None,
    models: ModelsConfig | None = None,
    name: str | None = None,
) -> tuple[StageAgent, str, str]:
    """Create one Claude-backed stage; `tools` is retained for API compatibility."""
    del tools
    models = models or load_models_config()
    cfg = models.resolved(agent_key)
    settings = ModelSettings(
        model=cfg.model,
        reasoning_effort=cfg.reasoning_effort,
        provider=cfg.provider,
        max_tokens=cfg.max_tokens,
        max_turns=cfg.max_turns,
        server_fallbacks=cfg.server_fallbacks,
    )
    return (
        StageAgent(name or agent_key, instructions, output_type, settings),
        cfg.model,
        cfg.prompt_version,
    )


def agent_instructions(agent_key: str, models: ModelsConfig | None = None) -> str:
    models = models or load_models_config()
    return load_prompt(models.resolved(agent_key).prompt_version)


class TrackedRunner:
    """Runs each stage through a Claude backend and records it locally."""

    def __init__(
        self,
        repos: Repositories,
        run_id: str | None,
        models: ModelsConfig | None = None,
        backend: LLMBackend | None = None,
    ) -> None:
        self.repos = repos
        self.run_id = run_id
        self.models = models or load_models_config()
        self._backend = backend

    @property
    def backend(self) -> LLMBackend:
        if self._backend is None:
            self._backend = get_backend()
        return self._backend

    async def run(
        self,
        agent: StageAgent,
        prompt: str,
        *,
        agent_key: str,
        workflow_key: str,
        model: str,
        prompt_version: str,
        topic_id: str | None = None,
        content_id: str | None = None,
        max_turns: int | None = None,
        extra_metadata: dict[str, str] | None = None,
    ) -> TrackedResult[Any]:
        """Run a typed stage, retrying one malformed structured response."""
        del extra_metadata
        settings = agent.model_settings
        if settings.provider != "anthropic":
            raise AgentRunError(
                agent_key, 0,
                ValueError(f"unsupported provider {settings.provider!r} in models.yaml"),
            )
        backend = self.backend
        workflow_name = self.models.workflow_name(workflow_key)
        retries = self.models.defaults.structured_output_retries
        effort = settings.reasoning_effort
        current_prompt = prompt
        last_error: Exception | None = None

        for attempt in range(1, retries + 2):
            started = datetime.now(timezone.utc)
            try:
                response = await backend.run(StageRequest(
                    model=model,
                    system=agent.instructions,
                    prompt=current_prompt,
                    output_type=agent.output_type,
                    effort=effort,
                    max_tokens=settings.max_tokens,
                    max_turns=max_turns or settings.max_turns,
                    server_fallbacks=settings.server_fallbacks,
                    cwd=PROJECT_ROOT,
                ))
                output = self._validate(agent, response)
            except Exception as exc:  # noqa: BLE001 - the failure is persisted
                completed = datetime.now(timezone.utc)
                self._record_failure(
                    agent_key, workflow_name, model, prompt_version, effort,
                    started, completed, topic_id, content_id, attempt, exc,
                )
                last_error = exc
                if attempt <= retries and isinstance(exc, (ValidationError, ValueError)):
                    current_prompt = self._repair_prompt(prompt, exc)
                    continue
                raise AgentRunError(agent_key, attempt, exc) from exc

            completed = datetime.now(timezone.utc)
            return self._record_success(
                response, output, backend.name, agent_key, workflow_name, model,
                prompt_version, effort, started, completed, topic_id, content_id,
                attempt,
            )

        raise AgentRunError(agent_key, retries + 1, last_error or RuntimeError("unknown"))

    @staticmethod
    def _validate(agent: StageAgent, response: StageResponse) -> Any:
        output_type = agent.output_type
        raw = response.output
        if output_type is None:
            return raw
        if isinstance(raw, output_type):
            return raw
        if isinstance(raw, BaseModel):
            raw = raw.model_dump()
        if isinstance(raw, (str, bytes)):
            return output_type.model_validate_json(raw)
        return output_type.model_validate(raw)

    def _record_success(
        self,
        response: StageResponse,
        output: Any,
        backend_name: str,
        agent_key: str,
        workflow_name: str,
        model: str,
        prompt_version: str,
        effort: str | None,
        started: datetime,
        completed: datetime,
        topic_id: str | None,
        content_id: str | None,
        attempt: int,
    ) -> TrackedResult[Any]:
        # Price by the model that actually served the request (a server-side
        # refusal fallback can change it).
        cost = self.models.compute_cost(
            response.served_model or model,
            input_tokens=response.input_tokens,
            output_tokens=response.output_tokens,
            cached_input_tokens=response.cached_input_tokens,
            cache_write_tokens=response.cache_write_tokens,
        )
        if response.reported_cost_usd is not None:
            # The Agent SDK reports its own figure; record it as the total and
            # keep the config-priced split for the billing-class breakdown.
            estimated_cost = float(response.reported_cost_usd)
            pricing_known = True
        else:
            estimated_cost = cost.total_cost
            pricing_known = cost.priced
        agent_run_id = self.repos.agent_runs.record(
            run_id=self.run_id,
            workflow_name=workflow_name,
            agent_name=agent_key,
            model=model,
            prompt_version=prompt_version,
            reasoning_effort=effort,
            started_at=started,
            completed_at=completed,
            status="OK",
            trace_id=response.trace_id,
            topic_id=topic_id,
            content_id=content_id,
            requests=response.requests,
            input_tokens=response.input_tokens,
            cached_input_tokens=response.cached_input_tokens,
            cache_write_tokens=response.cache_write_tokens,
            output_tokens=response.output_tokens,
            reasoning_tokens=response.reasoning_tokens,
            total_tokens=response.total_tokens,
            uncached_input_cost=cost.uncached_input_cost,
            cached_input_cost=cost.cached_input_cost,
            cache_write_cost=cost.cache_write_cost,
            output_cost=cost.output_cost,
            estimated_cost=estimated_cost,
            pricing_known=pricing_known,
            attempt=attempt,
        )
        return TrackedResult(
            output=output,
            agent_name=agent_key,
            model=model,
            prompt_version=prompt_version,
            trace_id=response.trace_id,
            agent_run_id=agent_run_id,
            attempts=attempt,
            reasoning_effort=effort,
            input_tokens=response.input_tokens,
            cached_input_tokens=response.cached_input_tokens,
            cache_write_tokens=response.cache_write_tokens,
            output_tokens=response.output_tokens,
            reasoning_tokens=response.reasoning_tokens,
            total_tokens=response.total_tokens,
            estimated_cost=estimated_cost,
            pricing_known=pricing_known,
            duration_ms=int((completed - started).total_seconds() * 1000),
            backend=backend_name,
            raw=response.raw,
        )

    def _record_failure(
        self,
        agent_key: str,
        workflow_name: str,
        model: str,
        prompt_version: str,
        effort: str | None,
        started: datetime,
        completed: datetime,
        topic_id: str | None,
        content_id: str | None,
        attempt: int,
        exc: Exception,
    ) -> None:
        self.repos.agent_runs.record(
            run_id=self.run_id,
            workflow_name=workflow_name,
            agent_name=agent_key,
            model=model,
            prompt_version=prompt_version,
            reasoning_effort=effort,
            started_at=started,
            completed_at=completed,
            status="ERROR",
            topic_id=topic_id,
            content_id=content_id,
            attempt=attempt,
            error_type=type(exc).__name__,
            error_message=str(exc)[:2000],
        )

    @staticmethod
    def _repair_prompt(original: str, exc: Exception) -> str:
        return (
            f"{original}\n\n---\n"
            f"The prior response did not satisfy the required JSON schema: "
            f"{type(exc).__name__}: {exc}. Return only schema-valid JSON."
        )


def run_sync(coro: Any) -> Any:
    return asyncio.run(coro)


def summarise_usage(repos: Repositories, run_id: str | None = None) -> dict[str, Any]:
    rows = repos.agent_runs.usage_summary(run_id)
    return {
        "run_id": run_id,
        "by_agent": [dict(row) for row in rows],
        "total_tokens": sum(row["total_tokens"] or 0 for row in rows),
        # API runs are priced from config/models.yaml; Agent SDK runs record the
        # cost the SDK reports (list-price equivalent on a Claude Code login).
        "total_cost": round(sum(row["estimated_cost"] or 0.0 for row in rows), 8),
    }


def json_preview(obj: Any, limit: int = 400) -> str:
    try:
        text = json.dumps(obj, default=str)
    except (TypeError, ValueError):
        text = str(obj)
    return text[:limit] + ("..." if len(text) > limit else "")
