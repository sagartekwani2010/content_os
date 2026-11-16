"""Claude runtime: backend selection, both transports and the tracked runner.

Every backend is mocked; nothing here touches the network or the Claude CLI.
"""

from __future__ import annotations

import asyncio
from types import SimpleNamespace

import pytest
from pydantic import BaseModel

from content_os import llm_runtime
from content_os.llm_runtime import (
    ANTHROPIC_API,
    CLAUDE_AGENT_SDK,
    AnthropicAPIBackend,
    ClaudeAgentSDKBackend,
    LLMBackendError,
    StageRequest,
    StageResponse,
    StructuredOutputError,
    normalise_agent_sdk_usage,
    normalise_anthropic_usage,
    select_backend_name,
)
from content_os.tracking.run_logger import (
    AgentRunError,
    TrackedRunner,
    build_agent,
    summarise_usage,
)


class Child(BaseModel):
    value: int


class Parent(BaseModel):
    child: Child
    note: str = ""


# --------------------------------------------------------------------- selection


class TestBackendSelection:
    @pytest.fixture(autouse=True)
    def no_ant_profile(self, monkeypatch):
        monkeypatch.setattr(llm_runtime, "_ant_profile_available", lambda: False)

    def test_api_key_selects_messages_api(self):
        assert select_backend_name({"ANTHROPIC_API_KEY": "x"}) == ANTHROPIC_API

    def test_auth_token_selects_messages_api(self):
        assert select_backend_name({"ANTHROPIC_AUTH_TOKEN": "x"}) == ANTHROPIC_API

    def test_ant_profile_selects_messages_api(self, monkeypatch):
        monkeypatch.setattr(llm_runtime, "_ant_profile_available", lambda: True)
        assert select_backend_name({}) == ANTHROPIC_API

    def test_no_credentials_falls_back_to_agent_sdk(self):
        assert select_backend_name({}) == CLAUDE_AGENT_SDK

    def test_empty_key_does_not_count(self):
        assert select_backend_name({"ANTHROPIC_API_KEY": ""}) == CLAUDE_AGENT_SDK

    def test_explicit_override_wins(self):
        env = {"ANTHROPIC_API_KEY": "x", "CONTENT_OS_LLM_BACKEND": "claude_agent_sdk"}
        assert select_backend_name(env) == CLAUDE_AGENT_SDK

    def test_unknown_override_is_rejected(self):
        with pytest.raises(LLMBackendError):
            select_backend_name({"CONTENT_OS_LLM_BACKEND": "codex"})


# --------------------------------------------------------------------- usage


class TestUsageNormalisation:
    def test_messages_api_input_includes_cache_reads_and_writes(self):
        usage = SimpleNamespace(
            input_tokens=100, cache_read_input_tokens=600,
            cache_creation_input_tokens=200, output_tokens=50,
        )
        assert normalise_anthropic_usage(usage) == {
            "input_tokens": 900, "cached_input_tokens": 600,
            "cache_write_tokens": 200, "output_tokens": 50, "reasoning_tokens": 0,
        }

    def test_agent_sdk_model_usage_is_summed_across_models(self):
        model_usage = {
            "a": {"inputTokens": 10, "cacheReadInputTokens": 5,
                  "cacheCreationInputTokens": 100, "outputTokens": 7,
                  "thinkingTokens": 3},
            "b": {"inputTokens": 1, "outputTokens": 2},
        }
        assert normalise_agent_sdk_usage(model_usage, None) == {
            "input_tokens": 116, "cached_input_tokens": 5,
            "cache_write_tokens": 100, "output_tokens": 9, "reasoning_tokens": 3,
        }

    def test_agent_sdk_falls_back_to_main_loop_usage(self):
        usage = {"input_tokens": 2, "cache_creation_input_tokens": 1105,
                 "cache_read_input_tokens": 0, "output_tokens": 52}
        tokens = normalise_agent_sdk_usage(None, usage)
        assert tokens["input_tokens"] == 1107
        assert tokens["cache_write_tokens"] == 1105


# --------------------------------------------------------------------- API backend


class FakeMessages:
    def __init__(self, response=None, exc=None):
        self.response, self.exc, self.calls = response, exc, []

    async def parse(self, **kwargs):
        self.calls.append(kwargs)
        if self.exc:
            raise self.exc
        return self.response

    create = parse


def fake_client(messages):
    return SimpleNamespace(beta=SimpleNamespace(messages=messages))


def api_response(**overrides):
    base = dict(
        id="msg_1", model="claude-opus-5-5", stop_reason="end_turn", stop_details=None,
        parsed_output=Parent(child=Child(value=3)), content=[],
        usage=SimpleNamespace(input_tokens=10, cache_read_input_tokens=0,
                              cache_creation_input_tokens=0, output_tokens=5,
                              iterations=None),
    )
    base.update(overrides)
    return SimpleNamespace(**base)


def request(**overrides):
    base = dict(model="claude-opus-5-5", system="sys", prompt="hi",
                output_type=Parent, effort="high")
    base.update(overrides)
    return StageRequest(**base)


class TestAnthropicAPIBackend:
    def test_request_shape_follows_the_current_api(self):
        messages = FakeMessages(api_response())
        backend = AnthropicAPIBackend(client=fake_client(messages))
        out = asyncio.run(backend.run(request(server_fallbacks=True)))

        kwargs = messages.calls[0]
        assert kwargs["output_format"] is Parent
        assert kwargs["output_config"] == {"effort": "high"}
        assert kwargs["system"] == "sys"
        assert kwargs["fallbacks"] == "default"
        assert kwargs["betas"] == [llm_runtime.SERVER_FALLBACK_BETA]
        # Adaptive thinking is the default; sampling params and budgets are gone.
        for banned in ("thinking", "temperature", "top_p", "top_k", "budget_tokens"):
            assert banned not in kwargs
        assert out.output == Parent(child=Child(value=3))
        assert out.trace_id == "anthropic:msg_1"
        assert out.reported_cost_usd is None

    def test_fallbacks_are_omitted_when_disabled(self):
        messages = FakeMessages(api_response())
        asyncio.run(AnthropicAPIBackend(fake_client(messages)).run(request()))
        assert "fallbacks" not in messages.calls[0]
        assert "betas" not in messages.calls[0]

    def test_refusal_is_a_non_retryable_error(self):
        messages = FakeMessages(api_response(
            stop_reason="refusal", stop_details=SimpleNamespace(category="cyber"),
            parsed_output=None,
        ))
        with pytest.raises(LLMBackendError, match="cyber"):
            asyncio.run(AnthropicAPIBackend(fake_client(messages)).run(request()))

    def test_missing_parsed_output_is_retryable(self):
        messages = FakeMessages(api_response(parsed_output=None))
        with pytest.raises(StructuredOutputError):
            asyncio.run(AnthropicAPIBackend(fake_client(messages)).run(request()))

    def test_sdk_connection_error_is_wrapped(self):
        import anthropic

        exc = anthropic.APIConnectionError(request=SimpleNamespace())
        messages = FakeMessages(exc=exc)
        with pytest.raises(LLMBackendError, match="Network"):
            asyncio.run(AnthropicAPIBackend(fake_client(messages)).run(request()))


# --------------------------------------------------------------------- Agent SDK backend


def sdk_result(**overrides):
    from claude_agent_sdk import ResultMessage

    base = dict(
        subtype="success", duration_ms=10, duration_api_ms=8, is_error=False,
        num_turns=2, session_id="sess-1", total_cost_usd=0.0012,
        usage={"input_tokens": 2, "output_tokens": 5},
        structured_output={"child": {"value": 7}},
        model_usage={"claude-haiku-5-5": {"inputTokens": 20, "outputTokens": 5,
                                          "cacheReadInputTokens": 0,
                                          "cacheCreationInputTokens": 100}},
    )
    base.update(overrides)
    return ResultMessage(**base)


def fake_query(*messages, raise_after=None):
    seen = {}

    async def query(*, prompt, options):
        seen["prompt"], seen["options"] = prompt, options
        for m in messages:
            yield m
        if raise_after:
            raise raise_after

    return query, seen


class TestClaudeAgentSDKBackend:
    def test_options_disable_tools_and_settings(self):
        options = ClaudeAgentSDKBackend().options(request(max_turns=4))
        assert options.tools == []
        assert options.setting_sources == []
        assert options.permission_mode == "dontAsk"
        assert options.system_prompt == "sys"
        assert options.model == "claude-opus-5-5"
        assert options.effort == "high"
        assert options.max_turns == 4
        assert options.output_format["type"] == "json_schema"
        assert options.output_format["schema"]["properties"]["child"]

    def test_success_records_sdk_usage_and_cost(self):
        from claude_agent_sdk import AssistantMessage

        query, seen = fake_query(
            AssistantMessage(content=[], model="claude-haiku-5-5"), sdk_result()
        )
        out = asyncio.run(ClaudeAgentSDKBackend(query).run(request()))
        assert seen["prompt"] == "hi"
        assert out.output == {"child": {"value": 7}}
        assert out.served_model == "claude-haiku-5-5"
        assert out.trace_id == "claude-agent-sdk:sess-1"
        assert out.reported_cost_usd == pytest.approx(0.0012)
        assert out.input_tokens == 120 and out.cache_write_tokens == 100
        assert out.requests == 2

    def test_structured_output_exhaustion_is_retryable(self):
        from claude_agent_sdk import ClaudeSDKError

        query, _ = fake_query(
            sdk_result(subtype="error_max_structured_output_retries", is_error=True,
                       structured_output=None, errors=["bad"]),
            raise_after=ClaudeSDKError("exit 1"),
        )
        with pytest.raises(StructuredOutputError):
            asyncio.run(ClaudeAgentSDKBackend(query).run(request()))

    def test_auth_failure_is_reported_plainly(self):
        from claude_agent_sdk import AssistantMessage

        query, _ = fake_query(
            AssistantMessage(content=[], model="x", error="authentication_failed")
        )
        with pytest.raises(LLMBackendError, match="login"):
            asyncio.run(ClaudeAgentSDKBackend(query).run(request()))

    def test_crash_without_result_is_wrapped(self):
        from claude_agent_sdk import ClaudeSDKError

        query, _ = fake_query(raise_after=ClaudeSDKError("cli missing"))
        with pytest.raises(LLMBackendError, match="cli missing"):
            asyncio.run(ClaudeAgentSDKBackend(query).run(request()))


# --------------------------------------------------------------------- runner


class ScriptedBackend:
    name = "scripted"

    def __init__(self, *outcomes):
        self.outcomes, self.requests = list(outcomes), []

    async def run(self, req: StageRequest) -> StageResponse:
        self.requests.append(req)
        outcome = self.outcomes.pop(0)
        if isinstance(outcome, Exception):
            raise outcome
        return outcome


def response(output, **kw):
    base = dict(output=output, served_model="claude-opus-5-5", trace_id="t-1",
                input_tokens=1_000_000, output_tokens=1_000_000)
    base.update(kw)
    return StageResponse(**base)


def run_stage(repos, backend, agent_key="carousel_writer"):
    agent, model, version = build_agent(
        agent_key, instructions="be useful", output_type=Parent
    )
    runner = TrackedRunner(repos, None, backend=backend)
    return asyncio.run(runner.run(
        agent, "prompt", agent_key=agent_key, workflow_key="reel",
        model=model, prompt_version=version,
    ))


class TestTrackedRunner:
    def test_config_drives_the_request(self, repos):
        from content_os.config import load_models_config

        cfg = load_models_config().resolved("carousel_writer")
        backend = ScriptedBackend(response({"child": {"value": 1}}))
        result = run_stage(repos, backend)
        req = backend.requests[0]
        assert req.model == cfg.model
        assert req.effort == cfg.reasoning_effort
        assert req.max_tokens == cfg.max_tokens
        assert req.system == "be useful"
        assert result.output == Parent(child=Child(value=1))

    def test_api_runs_are_priced_from_config(self, repos):
        result = run_stage(repos, ScriptedBackend(response({"child": {"value": 1}})))
        # 1M in + 1M out on claude-opus-5-5 at $4 / $20.
        assert result.estimated_cost == pytest.approx(24.0)
        assert result.pricing_known is True
        assert summarise_usage(repos)["total_cost"] == pytest.approx(24.0)

    def test_sdk_reported_cost_is_recorded_as_is(self, repos):
        backend = ScriptedBackend(
            response({"child": {"value": 1}}, reported_cost_usd=0.5)
        )
        result = run_stage(repos, backend)
        assert result.estimated_cost == pytest.approx(0.5)
        row = repos.conn.execute("SELECT * FROM agent_runs").fetchone()
        assert row["estimated_cost"] == pytest.approx(0.5)
        assert row["trace_id"] == "t-1"

    def test_one_repair_retry_on_invalid_output(self, repos):
        backend = ScriptedBackend(
            response({"child": {"value": "not-an-int"}}),
            response({"child": {"value": 2}}),
        )
        result = run_stage(repos, backend)
        assert result.attempts == 2
        assert "did not satisfy the required JSON schema" in backend.requests[1].prompt
        statuses = [r["status"] for r in repos.conn.execute(
            "SELECT status FROM agent_runs ORDER BY attempt")]
        assert statuses == ["ERROR", "OK"]

    def test_backend_errors_are_not_retried(self, repos):
        backend = ScriptedBackend(LLMBackendError("auth"))
        with pytest.raises(AgentRunError):
            run_stage(repos, backend)
        assert len(backend.requests) == 1

    def test_json_text_output_is_validated(self, repos):
        result = run_stage(repos, ScriptedBackend(response('{"child": {"value": 5}}')))
        assert result.output.child.value == 5
