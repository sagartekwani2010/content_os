"""Source connectors.

v1 ingests manually supplied URLs and text. The protocol and registry exist now
so that real connectors are additive: implementing X, Reddit, or arXiv means
writing one class and registering it, with no change to the scout, the workflow,
or the schema.

Unimplemented connectors are registered and raise a clear error rather than
being absent, so `sources list` shows the full roadmap and a typo in a source
name is distinguishable from a connector that has not been built.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Protocol, runtime_checkable


class SourceError(RuntimeError):
    pass


@runtime_checkable
class SourceConnector(Protocol):
    """Anything that can produce raw material for the Trend Scout."""

    name: str
    implemented: bool

    def fetch(self, **kwargs: Any) -> list[dict[str, Any]]:
        """Return a list of source records.

        Each record should carry at minimum: title, text or summary, url,
        source_type, and where available a published date.
        """
        ...


class ManualFileConnector:
    """Reads a JSON or JSONL file of manually collected sources.

    This is the only fully implemented connector in v1, and it is enough: the
    intelligence layer does not care whether a link was pasted by a human or
    pulled from an API.
    """

    name = "manual"
    implemented = True

    def fetch(self, path: str | Path | None = None, **_: Any) -> list[dict[str, Any]]:
        if path is None:
            raise SourceError("ManualFileConnector requires a file path.")
        file_path = Path(path)
        if not file_path.exists():
            raise SourceError(f"Source file not found: {file_path}")

        text = file_path.read_text(encoding="utf-8").strip()
        if not text:
            return []

        if file_path.suffix == ".jsonl":
            records = [json.loads(line) for line in text.splitlines() if line.strip()]
        else:
            data = json.loads(text)
            if isinstance(data, dict):
                records = data.get("sources", [])
            else:
                records = data

        if not isinstance(records, list):
            raise SourceError(
                f"{file_path} must contain a JSON list, or an object with a "
                f"'sources' list."
            )
        return [self._normalise(r, i) for i, r in enumerate(records)]

    @staticmethod
    def _normalise(record: Any, index: int) -> dict[str, Any]:
        if isinstance(record, str):
            # A bare string is treated as raw text with no URL. The scout is
            # instructed never to invent a URL, so this stays empty.
            return {
                "id": f"src_{index}",
                "title": record[:80],
                "text": record,
                "url": None,
                "source_type": "manual_text",
            }
        out = dict(record)
        out.setdefault("id", f"src_{index}")
        out.setdefault("source_type", "manual")
        return out


class _NotImplementedConnector:
    """Registered but unbuilt. Present so the roadmap is visible and a missing
    connector is distinguishable from a misspelled source name."""

    implemented = False

    def __init__(self, name: str, note: str) -> None:
        self.name = name
        self.note = note

    def fetch(self, **_: Any) -> list[dict[str, Any]]:
        raise SourceError(
            f"Source connector '{self.name}' is not implemented yet. {self.note} "
            f"For now, collect items manually into a JSON file and run: "
            f"cli.py discover <file>"
        )


REGISTRY: dict[str, Any] = {
    "manual": ManualFileConnector(),
    "x": _NotImplementedConnector("x", "Needs X/Twitter API credentials."),
    "reddit": _NotImplementedConnector("reddit", "Needs Reddit API credentials."),
    "linkedin": _NotImplementedConnector("linkedin", "No usable public read API."),
    "instagram": _NotImplementedConnector(
        "instagram", "Needs Meta Graph API and a business account."
    ),
    "github": _NotImplementedConnector("github", "Trending repos via the GitHub API."),
    "arxiv": _NotImplementedConnector("arxiv", "arXiv Atom feed for cs.AI and cs.CL."),
    "hackernews": _NotImplementedConnector("hackernews", "Firebase API, no auth needed."),
    "model_releases": _NotImplementedConnector(
        "model_releases", "OpenAI, Anthropic, Google and Meta announcement feeds."
    ),
}


def get_connector(name: str) -> SourceConnector:
    if name not in REGISTRY:
        raise SourceError(
            f"Unknown source '{name}'. Available: {', '.join(sorted(REGISTRY))}"
        )
    return REGISTRY[name]


def load_sources(path: str | Path) -> list[dict[str, Any]]:
    return REGISTRY["manual"].fetch(path=path)


def list_sources() -> list[dict[str, Any]]:
    return [
        {"name": name, "implemented": getattr(c, "implemented", False),
         "note": getattr(c, "note", "Ready.")}
        for name, c in sorted(REGISTRY.items())
    ]
