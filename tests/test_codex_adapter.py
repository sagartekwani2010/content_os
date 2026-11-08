"""Regression tests for the ChatGPT-authenticated Codex SDK adapter."""

from __future__ import annotations

from pydantic import BaseModel

from content_os.tracking.run_logger import codex_output_schema, extract_usage


class Child(BaseModel):
    value: int


class Parent(BaseModel):
    child: Child


def _objects(schema):
    if isinstance(schema, dict):
        if schema.get("type") == "object" or "properties" in schema:
            yield schema
        for value in schema.values():
            yield from _objects(value)
    elif isinstance(schema, list):
        for value in schema:
            yield from _objects(value)


def test_pydantic_schema_is_strict_for_codex_structured_output():
    schema = codex_output_schema(Parent)
    objects = list(_objects(schema))
    assert objects
    assert all(node.get("additionalProperties") is False for node in objects)


def test_strict_schema_requires_defaulted_nested_fields_too():
    """Codex rejects a strict schema that leaves optional properties out."""
    from content_os.models.content import StoryVerdict

    schema = codex_output_schema(StoryVerdict)
    assessment = schema["$defs"]["StorySceneAssessment"]
    assert set(assessment["required"]) == set(assessment["properties"])


def test_codex_usage_shape_is_normalised():
    class Usage:
        input_tokens = 100
        cached_input_tokens = 40
        cache_write_input_tokens = 20
        output_tokens = 30
        reasoning_output_tokens = 10
        total_tokens = 130

    assert extract_usage(Usage()) == {
        "requests": 0,
        "input_tokens": 100,
        "cached_input_tokens": 40,
        "cache_write_tokens": 20,
        "output_tokens": 30,
        "reasoning_tokens": 10,
        "total_tokens": 130,
    }
