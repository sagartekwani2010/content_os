"""Agent invocation tracking.

Every agent call in the system goes through TrackedRunner. It stamps the trace,
times the call, reads token usage off the run context, prices it, and writes one
row to agent_runs whether the call succeeded or failed.

That ledger is what eventually answers the questions the system was built for:
what does it cost to produce one Reel, which agent burns the most tokens, and
which workflows fail most often.
"""

from __future__ import annotations

import asyncio
import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Generic, TypeVar

from agents import Agent, ModelSettings, RunConfig, Runner
from agents.tracing import get_current_trace
from openai.types.shared import Reasoning
from pydantic import BaseModel, ValidationError

from content_os.config import ModelsConfig, load_models_config, load_prompt
from content_os.storage.repositories import Repositories

T = TypeVar("T", bound=BaseModel)

# Models that do not accept reasoning parameters. Sending `reasoning` to these
# is an API error rather than a no-op, so the setting is dropped instead.
_NON_REASONING_PREFIXES = ("gpt-4", "gpt-3", "chatgpt")


@dataclass
class TrackedResult(Generic[T]):
    """An agent result plus everything we recorded about producing it."""

    output: T
    agent_name: str
    model: str
    prompt_version: str
    trace_id: str | None
    agent_run_id: str
    attempts: int
    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0
    estimated_cost: float = 0.0
    duration_ms: int = 0
    raw: Any = field(default=None, repr=False)


class AgentRunError(RuntimeError):
    """Raised when an agent could not produce a valid result after retries."""

    def __init__(self, agent_name: str, attempts: int, cause: Exception) -> None:
        super().__init__(
            f"Agent '{agent_name}' failed after {attempts} attempt(s): "
            f"{type(cause).__name__}: {cause}"
        )
        self.agent_name = agent_name
        self.attempts = attempts
        self.cause = cause


def _supports_reasoning(model: str) -> bool:
    lowered = model.lower()
    return not any(lowered.startswith(p) for p in _NON_REASONING_PREFIXES)


def build_model_settings(
    model: str, reasoning_effort: str | None, verbosity: str | None
) -> ModelSettings:
    kwargs: dict[str, Any] = {"include_usage": True}
    if reasoning_effort and _supports_reasoning(model):
        kwargs["reasoning"] = Reasoning(effort=reasoning_effort)  # type: ignore[arg-type]
    if verbosity:
        kwargs["verbosity"] = verbosity  # type: ignore[assignment]
    return ModelSettings(**kwargs)


def build_agent(
    agent_key: str,
    *,
    instructions: str,
    output_type: type[BaseModel] | None = None,
    tools: list[Any] | None = None,
    models: ModelsConfig | None = None,
    name: str | None = None,
) -> tuple[Agent, str, str]:
    """Construct an agent from config. Returns (agent, model, prompt_version).

    No model name is ever passed in from calling code; it always comes from
    config/models.yaml so the choice is recorded and changeable in one place.
    """
    models = models or load_models_config()
    cfg = models.resolved(agent_key)

    agent = Agent(
        name=name or agent_key,
        instructions=instructions,
        model=cfg.model,
        model_settings=build_model_settings(
            cfg.model, cfg.reasoning_effort, cfg.verbosity
        ),
        output_type=output_type,
        tools=tools or [],
    )
    return agent, cfg.model, cfg.prompt_version


def agent_instructions(agent_key: str, models: ModelsConfig | None = None) -> str:
    """Load the versioned prompt file configured for an agent."""
    models = models or load_models_config()
    return load_prompt(models.resolved(agent_key).prompt_version)


class TrackedRunner:
    """Runs agents and records every invocation.

    One instance per workflow run, carrying the run_id so that every agent call,
    topic, score, and artifact produced tonight traces back to a single row in
    `runs`.
    """

    def __init__(
        self,
        repos: Repositories,
        run_id: str | None,
        models: ModelsConfig | None = None,
    ) -> None:
        self.repos = repos
        self.run_id = run_id
        self.models = models or load_models_config()

    def _price(self, model: str, input_tokens: int, output_tokens: int) -> float:
        pricing = self.models.price(model)
        return round(
            (input_tokens / 1_000_000) * pricing.input_per_mtok
            + (output_tokens / 1_000_000) * pricing.output_per_mtok,
            6,
        )

    async def run(
        self,
        agent: Agent,
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
        """Run an agent, retrying once on a malformed structured output.

        The retry feeds the validation error back to the model rather than
        repeating the same prompt, because a schema violation is almost always
        a specific fixable mistake.
        """
        workflow_name = self.models.workflow_name(workflow_key)
        retries = self.models.defaults.structured_output_retries
        turns = max_turns or self.models.defaults.max_turns

        metadata: dict[str, str] = {
            "agent": agent_key,
            "prompt_version": prompt_version,
        }
        if self.run_id:
            metadata["run_id"] = self.run_id
        if topic_id:
            metadata["topic_id"] = topic_id
        if content_id:
            metadata["content_id"] = content_id
        metadata.update(extra_metadata or {})

        current_prompt = prompt
        last_error: Exception | None = None

        for attempt in range(1, retries + 2):
            started = datetime.now(timezone.utc)
            run_config = RunConfig(
                workflow_name=workflow_name,
                group_id=self.run_id,
                trace_metadata=metadata,
                tracing_disabled=not self.models.tracing.enabled,
            )

            try:
                result = await Runner.run(
                    agent,
                    current_prompt,
                    run_config=run_config,
                    max_turns=turns,
                )
            except Exception as exc:  # noqa: BLE001 - recorded, then rethrown
                completed = datetime.now(timezone.utc)
                self._record_failure(
                    agent_key=agent_key,
                    workflow_name=workflow_name,
                    model=model,
                    prompt_version=prompt_version,
                    started=started,
                    completed=completed,
                    topic_id=topic_id,
                    content_id=content_id,
                    attempt=attempt,
                    exc=exc,
                )
                last_error = exc
                if attempt <= retries and isinstance(exc, (ValidationError, ValueError)):
                    current_prompt = self._repair_prompt(prompt, exc)
                    continue
                raise AgentRunError(agent_key, attempt, exc) from exc

            completed = datetime.now(timezone.utc)
            usage = result.context_wrapper.usage
            trace = get_current_trace()
            trace_id = getattr(trace, "trace_id", None)

            cost = self._price(model, usage.input_tokens, usage.output_tokens)
            agent_run_id = self.repos.agent_runs.record(
                run_id=self.run_id,
                workflow_name=workflow_name,
                agent_name=agent_key,
                model=model,
                prompt_version=prompt_version,
                started_at=started,
                completed_at=completed,
                status="OK",
                trace_id=trace_id,
                topic_id=topic_id,
                content_id=content_id,
                requests=usage.requests,
                input_tokens=usage.input_tokens,
                output_tokens=usage.output_tokens,
                total_tokens=usage.total_tokens,
                estimated_cost=cost,
                attempt=attempt,
            )

            return TrackedResult(
                output=result.final_output,
                agent_name=agent_key,
                model=model,
                prompt_version=prompt_version,
                trace_id=trace_id,
                agent_run_id=agent_run_id,
                attempts=attempt,
                input_tokens=usage.input_tokens,
                output_tokens=usage.output_tokens,
                total_tokens=usage.total_tokens,
                estimated_cost=cost,
                duration_ms=int((completed - started).total_seconds() * 1000),
                raw=result,
            )

        raise AgentRunError(agent_key, retries + 1, last_error or RuntimeError("unknown"))

    def _record_failure(
        self,
        *,
        agent_key: str,
        workflow_name: str,
        model: str,
        prompt_version: str,
        started: datetime,
        completed: datetime,
        topic_id: str | None,
        content_id: str | None,
        attempt: int,
        exc: Exception,
    ) -> None:
        """Failures are logged too.

        A ledger that only records successes cannot answer which workflows fail
        most, which is one of the questions this table exists for.
        """
        self.repos.agent_runs.record(
            run_id=self.run_id,
            workflow_name=workflow_name,
            agent_name=agent_key,
            model=model,
            prompt_version=prompt_version,
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
            f"{original}\n\n"
            f"---\n"
            f"Your previous response could not be parsed into the required schema.\n"
            f"Error: {type(exc).__name__}: {exc}\n"
            f"Return a response that matches the schema exactly. "
            f"Every required field must be present and correctly typed."
        )


def run_sync(coro: Any) -> Any:
    """Run an async workflow from the synchronous CLI."""
    return asyncio.run(coro)


def summarise_usage(repos: Repositories, run_id: str | None = None) -> dict[str, Any]:
    rows = repos.agent_runs.usage_summary(run_id)
    total_cost = sum(r["estimated_cost"] or 0.0 for r in rows)
    total_tokens = sum(r["total_tokens"] or 0 for r in rows)
    return {
        "run_id": run_id,
        "by_agent": [dict(r) for r in rows],
        "total_tokens": total_tokens,
        "total_cost": round(total_cost, 4),
    }


def json_preview(obj: Any, limit: int = 400) -> str:
    try:
        text = json.dumps(obj, default=str)
    except (TypeError, ValueError):
        text = str(obj)
    return text[:limit] + ("..." if len(text) > limit else "")
