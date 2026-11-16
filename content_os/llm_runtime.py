"""Provider-neutral LLM runtime for Content OS stages.

Every stage is one structured call: a versioned system prompt, a user prompt
and a Pydantic output contract. `TrackedRunner` (content_os.tracking.run_logger)
owns validation, retry and the ledger; this module owns *how* the call reaches
Claude. Two backends are chosen automatically:

* ``anthropic_api`` - the official ``anthropic`` SDK and the Messages API, used
  when Anthropic API credentials are available (``ANTHROPIC_API_KEY``,
  ``ANTHROPIC_AUTH_TOKEN``, or an ``ant auth login`` profile). Structured output
  via ``messages.parse(output_format=...)``, adaptive thinking (the ``thinking``
  parameter is omitted), effort via ``output_config``. Billed at API rates, so
  the ledger prices it from config/models.yaml.
* ``claude_agent_sdk`` - the Claude Agent SDK, which drives the local Claude
  Code CLI and therefore reuses the creator's Claude Code login. No API key is
  read. Every built-in tool is disabled, so a stage can neither read nor write
  the repo; it only returns schema-checked JSON. Cost is what the SDK reports.

``CONTENT_OS_LLM_BACKEND`` (``anthropic_api`` | ``claude_agent_sdk``) overrides
the automatic choice. No model name is hardcoded here: models, effort and
fallback opt-in all come from config/models.yaml.
"""

from __future__ import annotations

import os
import shutil
import subprocess
from contextlib import contextmanager
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path
from typing import Any, Iterator, Mapping, Protocol

from pydantic import BaseModel

PROJECT_ROOT = Path(__file__).resolve().parent.parent

BACKEND_ENV = "CONTENT_OS_LLM_BACKEND"
ANTHROPIC_API = "anthropic_api"
CLAUDE_AGENT_SDK = "claude_agent_sdk"
BACKENDS = (ANTHROPIC_API, CLAUDE_AGENT_SDK)

# Opt-in for server-side refusal fallbacks on the Messages API.
SERVER_FALLBACK_BETA = "server-side-fallback-2026-07-01"


@contextmanager
def trace(*_args: object, **_kwargs: object) -> Iterator[None]:
    """Keep workflow trace scopes; provenance lives in the agent-run ledger.

    `TrackedRunner` records the API request id or Agent SDK session id as the
    trace id of every stage, so no external tracer is started.
    """
    yield


# --------------------------------------------------------------------------
# Errors
# --------------------------------------------------------------------------


class LLMBackendError(RuntimeError):
    """A backend failure that a repair prompt cannot fix (auth, refusal, 4xx)."""


class StructuredOutputError(ValueError):
    """The model returned no schema-valid output. Retried with a repair prompt."""


# --------------------------------------------------------------------------
# Request / response
# --------------------------------------------------------------------------


@dataclass(frozen=True)
class StageRequest:
    model: str
    system: str
    prompt: str
    output_type: type[BaseModel] | None = None
    effort: str | None = None
    max_tokens: int = 16000
    max_turns: int | None = None
    server_fallbacks: bool = False
    cwd: Path = PROJECT_ROOT


@dataclass
class StageResponse:
    """Backend-neutral result. `output` is a model instance, dict or text."""

    output: Any
    served_model: str
    trace_id: str | None
    requests: int = 1
    # Normalised so input_tokens INCLUDES cached reads and cache writes; the
    # ledger's compute_cost treats those two as subsets of input_tokens.
    input_tokens: int = 0
    cached_input_tokens: int = 0
    cache_write_tokens: int = 0
    output_tokens: int = 0
    reasoning_tokens: int = 0
    # Set only when the backend itself reports a dollar figure.
    reported_cost_usd: float | None = None
    raw: Any = field(default=None, repr=False)

    @property
    def total_tokens(self) -> int:
        return self.input_tokens + self.output_tokens


class LLMBackend(Protocol):
    name: str

    async def run(self, request: StageRequest) -> StageResponse: ...


def _get(obj: Any, key: str, default: Any = 0) -> Any:
    if obj is None:
        return default
    if isinstance(obj, Mapping):
        value = obj.get(key, default)
    else:
        value = getattr(obj, key, default)
    return default if value is None else value


def normalise_anthropic_usage(usage: Any) -> dict[str, int]:
    """Messages-API usage -> ledger shape.

    The API's `input_tokens` is the uncached remainder only; total prompt size
    is input + cache_creation + cache_read.
    """
    uncached = int(_get(usage, "input_tokens"))
    read = int(_get(usage, "cache_read_input_tokens"))
    written = int(_get(usage, "cache_creation_input_tokens"))
    details = _get(usage, "output_tokens_details", None)
    return {
        "input_tokens": uncached + read + written,
        "cached_input_tokens": read,
        "cache_write_tokens": written,
        "output_tokens": int(_get(usage, "output_tokens")),
        "reasoning_tokens": int(_get(details, "thinking_tokens")),
    }


def normalise_agent_sdk_usage(
    model_usage: Mapping[str, Any] | None, usage: Mapping[str, Any] | None
) -> dict[str, int]:
    """Agent SDK ResultMessage usage -> ledger shape.

    `model_usage` (camelCase, keyed by model) includes internal calls, so it is
    preferred; `usage` (main loop only, Messages-API shape) is the fallback.
    """
    if model_usage:
        totals = dict.fromkeys(
            ("input_tokens", "cached_input_tokens", "cache_write_tokens",
             "output_tokens", "reasoning_tokens"), 0,
        )
        for entry in model_usage.values():
            uncached = int(_get(entry, "inputTokens"))
            read = int(_get(entry, "cacheReadInputTokens"))
            written = int(_get(entry, "cacheCreationInputTokens"))
            totals["input_tokens"] += uncached + read + written
            totals["cached_input_tokens"] += read
            totals["cache_write_tokens"] += written
            totals["output_tokens"] += int(_get(entry, "outputTokens"))
            totals["reasoning_tokens"] += int(_get(entry, "thinkingTokens"))
        return totals
    return normalise_anthropic_usage(usage or {})


# --------------------------------------------------------------------------
# Backend selection
# --------------------------------------------------------------------------


@lru_cache(maxsize=1)
def _ant_profile_available() -> bool:
    """True when an `ant auth login` profile can authenticate the SDK."""
    ant = shutil.which("ant")
    if ant:
        try:
            return subprocess.run(
                [ant, "auth", "status"], stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL, check=False, timeout=10,
            ).returncode == 0
        except (OSError, subprocess.SubprocessError):
            return False
    profile_dir = Path.home() / ".config" / "anthropic"
    return profile_dir.is_dir() and any(profile_dir.iterdir())


def api_credentials_available(env: Mapping[str, str] | None = None) -> bool:
    env = os.environ if env is None else env
    if env.get("ANTHROPIC_API_KEY") or env.get("ANTHROPIC_AUTH_TOKEN"):
        return True
    if env.get("ANTHROPIC_PROFILE"):
        return True
    return _ant_profile_available()


def select_backend_name(env: Mapping[str, str] | None = None) -> str:
    """API backend when API credentials exist, otherwise the Agent SDK."""
    env = os.environ if env is None else env
    forced = (env.get(BACKEND_ENV) or "").strip().lower()
    if forced:
        if forced not in BACKENDS:
            raise LLMBackendError(
                f"{BACKEND_ENV}={forced!r} is not one of {', '.join(BACKENDS)}"
            )
        return forced
    return ANTHROPIC_API if api_credentials_available(env) else CLAUDE_AGENT_SDK


def get_backend(name: str | None = None) -> LLMBackend:
    name = name or select_backend_name()
    if name == ANTHROPIC_API:
        return AnthropicAPIBackend()
    if name == CLAUDE_AGENT_SDK:
        return ClaudeAgentSDKBackend()
    raise LLMBackendError(f"Unknown LLM backend {name!r}")


def claude_code_cli_available() -> bool:
    """The Agent SDK ships its own CLI; a system `claude` also works."""
    try:
        import claude_agent_sdk  # noqa: F401
    except ImportError:
        return False
    return True


def describe_backend() -> tuple[bool, str]:
    """(ready, message) for `cli.py doctor`. Never makes a model call."""
    try:
        name = select_backend_name()
    except LLMBackendError as exc:
        return False, str(exc)
    if name == ANTHROPIC_API:
        try:
            import anthropic  # noqa: F401
        except ImportError:
            return False, "anthropic SDK not installed (pip install -r requirements.txt)"
        return True, "Anthropic API (Messages API, API-key or ant profile auth)"
    if not claude_code_cli_available():
        return False, "claude-agent-sdk not installed (pip install -r requirements.txt)"
    return True, (
        "Claude Agent SDK using the local Claude Code login "
        "(run `claude` and /login if a stage reports an auth error)"
    )


# --------------------------------------------------------------------------
# Backend (a): Anthropic Messages API
# --------------------------------------------------------------------------


class AnthropicAPIBackend:
    name = ANTHROPIC_API

    def __init__(self, client: Any | None = None) -> None:
        self._client = client

    def _client_or_default(self) -> Any:
        if self._client is None:
            import anthropic

            # Resolves ANTHROPIC_API_KEY / AUTH_TOKEN / ant profile itself.
            self._client = anthropic.AsyncAnthropic()
        return self._client

    async def run(self, request: StageRequest) -> StageResponse:
        import anthropic

        client = self._client_or_default()
        kwargs: dict[str, Any] = {
            "model": request.model,
            "max_tokens": request.max_tokens,
            "system": request.system,
            "messages": [{"role": "user", "content": request.prompt}],
            # The stage system prompt is stable across calls; cache it.
            "cache_control": {"type": "ephemeral"},
        }
        # Thinking is omitted on purpose: current models run adaptive thinking
        # by default, and depth is controlled through effort.
        if request.effort:
            kwargs["output_config"] = {"effort": request.effort}
        if request.output_type is not None:
            kwargs["output_format"] = request.output_type
        if request.server_fallbacks:
            kwargs["betas"] = [SERVER_FALLBACK_BETA]
            kwargs["fallbacks"] = "default"

        try:
            if request.output_type is not None:
                response = await client.beta.messages.parse(**kwargs)
            else:
                response = await client.beta.messages.create(**kwargs)
        except anthropic.BadRequestError as exc:
            raise LLMBackendError(f"Bad request: {exc.message}") from exc
        except anthropic.AuthenticationError as exc:
            raise LLMBackendError("Anthropic API authentication failed") from exc
        except anthropic.PermissionDeniedError as exc:
            raise LLMBackendError(f"Permission denied: {exc.message}") from exc
        except anthropic.NotFoundError as exc:
            raise LLMBackendError(f"Model or endpoint not found: {exc.message}") from exc
        except anthropic.RateLimitError as exc:
            # The SDK already retried with backoff (max_retries=2).
            raise LLMBackendError(f"Rate limited after SDK retries: {exc.message}") from exc
        except anthropic.APIStatusError as exc:
            raise LLMBackendError(
                f"API error {exc.status_code} after SDK retries: {exc.message}"
            ) from exc
        except anthropic.APIConnectionError as exc:
            raise LLMBackendError(f"Network error reaching the API: {exc}") from exc

        stop = getattr(response, "stop_reason", None)
        if stop == "refusal":
            details = getattr(response, "stop_details", None)
            category = getattr(details, "category", None) if details else None
            raise LLMBackendError(f"Model refused the request (category={category})")
        if stop == "max_tokens":
            raise LLMBackendError(
                f"Output hit max_tokens={request.max_tokens}; raise max_tokens "
                "for this agent in config/models.yaml"
            )

        if request.output_type is not None:
            output = getattr(response, "parsed_output", None)
            if output is None:
                raise StructuredOutputError("API response carried no parsed output")
        else:
            output = "".join(
                b.text for b in response.content if getattr(b, "type", "") == "text"
            )
            if not output:
                raise StructuredOutputError("API response carried no text")

        tokens = normalise_anthropic_usage(response.usage)
        iterations = _get(response.usage, "iterations", None) or []
        return StageResponse(
            output=output,
            served_model=getattr(response, "model", request.model) or request.model,
            trace_id=f"anthropic:{getattr(response, 'id', '')}",
            requests=max(1, len(iterations)),
            raw=response,
            **tokens,
        )


# --------------------------------------------------------------------------
# Backend (b): Claude Agent SDK (local Claude Code login)
# --------------------------------------------------------------------------


class ClaudeAgentSDKBackend:
    name = CLAUDE_AGENT_SDK

    def __init__(self, query_fn: Any | None = None) -> None:
        self._query = query_fn

    def options(self, request: StageRequest) -> Any:
        from claude_agent_sdk import ClaudeAgentOptions

        kwargs: dict[str, Any] = {
            "model": request.model,
            # A plain string replaces Claude Code's own system prompt.
            "system_prompt": request.system,
            # No built-in tools: the stage cannot read, write or run anything.
            # The SDK still injects its StructuredOutput tool when
            # output_format is set.
            "tools": [],
            # Ignore user/project/local settings, hooks and CLAUDE.md so a stage
            # sees only its own prompt.
            "setting_sources": [],
            # Deny anything not pre-approved rather than prompting.
            "permission_mode": "dontAsk",
            "cwd": str(request.cwd),
        }
        if request.max_turns:
            kwargs["max_turns"] = request.max_turns
        if request.effort:
            kwargs["effort"] = request.effort
        if request.output_type is not None:
            kwargs["output_format"] = {
                "type": "json_schema",
                "schema": request.output_type.model_json_schema(),
            }
        return ClaudeAgentOptions(**kwargs)

    async def run(self, request: StageRequest) -> StageResponse:
        from claude_agent_sdk import AssistantMessage, ResultMessage
        from claude_agent_sdk import ClaudeSDKError

        query = self._query
        if query is None:
            from claude_agent_sdk import query

        result: Any = None
        served_model = request.model
        try:
            async for message in query(prompt=request.prompt, options=self.options(request)):
                if isinstance(message, AssistantMessage):
                    served_model = message.model or served_model
                    if message.error in ("authentication_failed", "billing_error"):
                        raise LLMBackendError(
                            f"Claude Code login problem ({message.error}); run "
                            "`claude` and /login"
                        )
                elif isinstance(message, ResultMessage):
                    result = message
        except ClaudeSDKError as exc:
            # A failed run yields its error ResultMessage and then raises; the
            # result (if captured) is the more precise signal.
            if result is None:
                raise LLMBackendError(f"Claude Agent SDK failed: {exc}") from exc

        if result is None:
            raise LLMBackendError("Claude Agent SDK returned no result message")
        if result.subtype == "error_max_structured_output_retries":
            raise StructuredOutputError(
                "Agent SDK could not produce schema-valid output: "
                + "; ".join(result.errors or [])
            )
        if result.is_error or result.subtype != "success":
            if result.stop_reason == "refusal":
                raise LLMBackendError("Model refused the request")
            raise LLMBackendError(
                f"Claude Agent SDK run ended with {result.subtype}: "
                + ("; ".join(result.errors or []) or (result.result or ""))[:500]
            )

        if request.output_type is not None:
            output = result.structured_output
            if output is None:
                raise StructuredOutputError("Agent SDK result carried no structured_output")
        else:
            output = result.result
            if not output:
                raise StructuredOutputError("Agent SDK result carried no text")

        tokens = normalise_agent_sdk_usage(result.model_usage, result.usage)
        return StageResponse(
            output=output,
            served_model=served_model,
            trace_id=f"claude-agent-sdk:{result.session_id}",
            requests=max(1, int(result.num_turns or 1)),
            reported_cost_usd=result.total_cost_usd,
            raw=result,
            **tokens,
        )
