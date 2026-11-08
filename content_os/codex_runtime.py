"""Small runtime helpers for Codex SDK orchestration."""

from __future__ import annotations

from contextlib import contextmanager
from typing import Iterator


@contextmanager
def trace(*_args: object, **_kwargs: object) -> Iterator[None]:
    """Keep workflow trace scopes while Codex thread IDs provide provenance.

    The old API tracer is intentionally not started. `TrackedRunner` records the
    Codex SDK thread ID in the existing agent-run ledger instead.
    """
    yield
