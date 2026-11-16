"""Deprecated alias kept so older imports keep working.

The runtime moved to `content_os.llm_runtime` when the system switched from
the Codex SDK to Claude. Import `trace` from there in new code.
"""

from content_os.llm_runtime import trace

__all__ = ["trace"]
