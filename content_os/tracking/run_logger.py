"""Codex SDK orchestration and local invocation tracking.

Each content stage remains an independent agent with a versioned prompt and a
Pydantic output contract. The adapter runs that stage in a read-only Codex SDK
thread using the user's saved ChatGPT authentication, then validates and
persists the result before the next stage receives it.
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
from content_os.storage.repositories import Repositories

T = TypeVar("T", bound=BaseModel)
PROJECT_ROOT = Path(__file__).resolve().parents[2]


@dataclass(frozen=True)
class CodexModelSettings:
    model: str
    reasoning_effort: str | None
    verbosity: str | None


@dataclass(frozen=True)
class CodexAgent:
    """The stable, typed description of one coordination stage."""

    name: str
    instructions: str
    output_type: type[BaseModel] | None
    model_settings: CodexModelSettings


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
    raw: Any = field(default=None, repr=False)

    @property
    def cache_hit_rate(self) -> float:
        return self.cached_input_tokens / self.input_tokens if self.input_tokens else 0.0


class AgentRunError(RuntimeError):
    def __init__(self, agent_name: str, attempts: int, cause: Exception) -> None:
        super().__init__(
            f"Codex stage '{agent_name}' failed after {attempts} attempt(s): "
            f"{type(cause).__name__}: {cause}"
        )
        self.agent_name = agent_name
        self.attempts = attempts
        self.cause = cause


def extract_usage(usage: Any) -> dict[str, int]:
    """Normalise legacy and Codex SDK token-usage shapes."""
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
    model: str, reasoning_effort: str | None, verbosity: str | None
) -> CodexModelSettings:
    return CodexModelSettings(model, reasoning_effort, verbosity)


def build_agent(
    agent_key: str,
    *,
    instructions: str,
    output_type: type[BaseModel] | None = None,
    tools: list[Any] | None = None,
    models: ModelsConfig | None = None,
    name: str | None = None,
) -> tuple[CodexAgent, str, str]:
    """Create one Codex-backed stage; `tools` is retained for API compatibility."""
    del tools
    models = models or load_models_config()
    cfg = models.resolved(agent_key)
    settings = build_model_settings(cfg.model, cfg.reasoning_effort, cfg.verbosity)
    return (
        CodexAgent(name or agent_key, instructions, output_type, settings),
        cfg.model,
        cfg.prompt_version,
    )


def codex_output_schema(output_type: type[BaseModel]) -> dict[str, Any]:
    """Make Pydantic's schema compatible with Codex strict structured output."""
    schema = output_type.model_json_schema()

    def make_strict(value: Any) -> None:
        if isinstance(value, dict):
            if value.get("type") == "object" or "properties" in value:
                value["additionalProperties"] = False
                # Codex strict structured output requires every declared key to
                # appear in `required`. Pydantic represents defaulted fields as
                # optional; the model can still emit []/null/default values, but
                # the transport schema must require the key itself.
                properties = value.get("properties")
                if isinstance(properties, dict):
                    value["required"] = list(properties)
            for child in value.values():
                make_strict(child)
        elif isinstance(value, list):
            for child in value:
                make_strict(child)

    make_strict(schema)
    return schema


def agent_instructions(agent_key: str, models: ModelsConfig | None = None) -> str:
    models = models or load_models_config()
    return load_prompt(models.resolved(agent_key).prompt_version)


class TrackedRunner:
    """Runs each stage in a Codex SDK thread and records it locally."""

    def __init__(
        self,
        repos: Repositories,
        run_id: str | None,
        models: ModelsConfig | None = None,
    ) -> None:
        self.repos = repos
        self.run_id = run_id
        self.models = models or load_models_config()

    async def run(
        self,
        agent: CodexAgent,
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
        """Run a typed stage, retrying one malformed structured response.

        The Codex SDK inherits the local `codex login` session. It therefore
        consumes the user's Codex plan entitlement and never reads an API key.
        """
        del max_turns, extra_metadata
        from openai_codex import AsyncCodex, Sandbox

        workflow_name = self.models.workflow_name(workflow_key)
        retries = self.models.defaults.structured_output_retries
        effort = agent.model_settings.reasoning_effort
        current_prompt = prompt
        last_error: Exception | None = None

        for attempt in range(1, retries + 2):
            started = datetime.now(timezone.utc)
            try:
                async with AsyncCodex() as codex:
                    thread = await codex.thread_start(
                        model=model,
                        cwd=str(PROJECT_ROOT),
                        sandbox=Sandbox.read_only,
                        developer_instructions=agent.instructions,
                        ephemeral=True,
                    )
                    turn = await thread.run(
                        current_prompt,
                        effort=effort,
                        output_schema=(codex_output_schema(agent.output_type)
                                       if agent.output_type is not None else None),
                    )

                raw_output = turn.final_response
                if not raw_output:
                    raise ValueError("Codex returned no final response")
                output: Any = (
                    agent.output_type.model_validate_json(raw_output)
                    if agent.output_type is not None
                    else raw_output
                )
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
            usage = getattr(turn, "usage", None)
            # Codex reports cumulative and per-turn usage; `last` is this stage.
            tokens = extract_usage(getattr(usage, "last", usage))
            tokens["requests"] = max(1, tokens["requests"])
            trace_id = f"codex:{thread.id}"
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
                trace_id=trace_id,
                topic_id=topic_id,
                content_id=content_id,
                requests=tokens["requests"],
                input_tokens=tokens["input_tokens"],
                cached_input_tokens=tokens["cached_input_tokens"],
                cache_write_tokens=tokens["cache_write_tokens"],
                output_tokens=tokens["output_tokens"],
                reasoning_tokens=tokens["reasoning_tokens"],
                total_tokens=tokens["total_tokens"],
                estimated_cost=0.0,
                pricing_known=False,
                attempt=attempt,
            )
            return TrackedResult(
                output=output,
                agent_name=agent_key,
                model=model,
                prompt_version=prompt_version,
                trace_id=trace_id,
                agent_run_id=agent_run_id,
                attempts=attempt,
                reasoning_effort=effort,
                input_tokens=tokens["input_tokens"],
                cached_input_tokens=tokens["cached_input_tokens"],
                cache_write_tokens=tokens["cache_write_tokens"],
                output_tokens=tokens["output_tokens"],
                reasoning_tokens=tokens["reasoning_tokens"],
                total_tokens=tokens["total_tokens"],
                duration_ms=int((completed - started).total_seconds() * 1000),
                raw=turn,
            )

        raise AgentRunError(agent_key, retries + 1, last_error or RuntimeError("unknown"))

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
        # ChatGPT-plan usage is not API-priced; only the token count is local.
        "total_cost": 0.0,
    }


def json_preview(obj: Any, limit: int = 400) -> str:
    try:
        text = json.dumps(obj, default=str)
    except (TypeError, ValueError):
        text = str(obj)
    return text[:limit] + ("..." if len(text) > limit else "")
