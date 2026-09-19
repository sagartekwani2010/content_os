"""Loading and scaffolding ContentBriefs from YAML.

YAML rather than JSON because briefs are written by a human, and block scalars
make long prose fields readable. The loader is deliberately forgiving about
field naming and strict about substance: a brief missing its thesis or learning
objective is rejected at load, not discovered halfway through production.
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml
from pydantic import ValidationError

from content_os.config import load_brand
from content_os.ids import new_id
from content_os.models.brief import BriefStatus, ContentBrief

# Tolerated spellings for fields people naturally write differently.
ALIASES = {
    "CTA_direction": "cta_direction",
    "cta": "cta_direction",
    "format": "content_format",
    "pillar": "brand_pillar",
    "duration": "desired_duration_seconds",
    "desired_duration": "desired_duration_seconds",
    "slides": "desired_slide_count",
    "slide_count": "desired_slide_count",
    "tone": "desired_tone",
    "claims_to_verify": "factual_claims_to_verify",
    "sections": "high_level_sections",
    "hook_points": "approved_hook_points",
}

REQUIRED = (
    "topic",
    "core_thesis",
    "learning_objective",
    "content_format",
    "brand_pillar",
    "hook_direction",
)

LIST_FIELDS = (
    "target_audience",
    "approved_hook_points",
    "high_level_sections",
    "core_examples",
    "references",
    "factual_claims_to_verify",
    "must_include",
    "must_avoid",
)

PROSE_FIELDS = (
    "topic",
    "core_thesis",
    "why_this_matters",
    "audience_takeaway",
    "learning_objective",
    "hook_direction",
    "desired_tone",
    "preferred_pov",
    "visual_direction",
    "cta_direction",
    "notes",
)


class BriefError(ValueError):
    pass


def _normalise(raw: dict[str, Any]) -> dict[str, Any]:
    data: dict[str, Any] = {}
    for key, value in raw.items():
        if key.startswith("_"):
            continue
        data[ALIASES.get(key, key)] = value

    # A single string where a list is expected is a natural thing to write.
    for field in LIST_FIELDS:
        value = data.get(field)
        if isinstance(value, str):
            data[field] = [value]

    # YAML block scalars carry newlines that would otherwise reach the prompt.
    for field in PROSE_FIELDS:
        if isinstance(data.get(field), str):
            data[field] = " ".join(data[field].split())

    return data


def parse_brief(raw: dict[str, Any], *, brief_id: str | None = None) -> ContentBrief:
    data = _normalise(raw)

    missing = [f for f in REQUIRED if not data.get(f)]
    if missing:
        raise BriefError(
            f"Brief is missing required fields: {', '.join(missing)}. "
            f"The human owns strategy, so these cannot be inferred."
        )

    pillars = load_brand().pillar_keys
    if data["brand_pillar"] not in pillars:
        raise BriefError(
            f"Unknown brand_pillar '{data['brand_pillar']}'. "
            f"Valid pillars: {', '.join(pillars)}"
        )

    data.setdefault("brief_id", brief_id or new_id("brief"))
    data.setdefault("created_at", datetime.now(timezone.utc))
    data.setdefault("why_this_matters", "")
    data.setdefault("audience_takeaway", data["learning_objective"])

    status = data.get("status")
    if isinstance(status, str):
        data["status"] = BriefStatus(status.upper())

    try:
        return ContentBrief(**data)
    except ValidationError as exc:
        raise BriefError(f"Invalid brief:\n{exc}") from exc


def load_brief_file(path: str | Path) -> list[ContentBrief]:
    """Load one brief, or many from a list or a multi-document YAML file."""
    file_path = Path(path)
    if not file_path.exists():
        raise BriefError(f"Brief file not found: {file_path}")

    documents = [
        d for d in yaml.safe_load_all(file_path.read_text(encoding="utf-8")) if d
    ]

    briefs: list[ContentBrief] = []
    for document in documents:
        if isinstance(document, list):
            briefs += [parse_brief(d) for d in document if isinstance(d, dict)]
        elif isinstance(document, dict) and "briefs" in document:
            briefs += [parse_brief(d) for d in document["briefs"]]
        elif isinstance(document, dict):
            briefs.append(parse_brief(document))

    if not briefs:
        raise BriefError(f"No briefs found in {file_path}")
    return briefs


def scaffold(topic: str, content_format: str = "carousel") -> str:
    """Emit a commented YAML template for a human to fill in."""
    brand = load_brand()
    audiences = "\n".join(f"  - {a}" for a in brand.target_audiences[:3])
    sizing = (
        "desired_slide_count: 8"
        if content_format == "carousel"
        else "desired_duration_seconds: 30"
    )
    return f"""# Content brief. You own strategy; the agents own execution.
# Required: topic, core_thesis, learning_objective, content_format,
# brand_pillar, hook_direction.

topic: "{topic}"

core_thesis: >
  The single argument this content makes. Agents may not change this.

why_this_matters: >
  Why this deserves attention now.

learning_objective: >
  What the viewer can do, decide, or recognise afterwards.
  Be concrete; QA checks this as a hard gate.

audience_takeaway: >
  The one line they should remember.

target_audience:
{audiences}

brand_pillar: {brand.pillar_keys[0]}   # one of: {', '.join(brand.pillar_keys)}
content_format: {content_format}        # reel | carousel | trial_reel

hook_direction: >
  The angle the hook should take, for example a contrarian practitioner opinion.

approved_hook_points:
  - "A specific claim the hook may develop."
  - "Another. Two to five; the agent stays inside this territory."

high_level_sections:
  # Mandatory. Every one must be covered. Agents may reorder and reword.
  - first concept
  - second concept
  - final takeaway

core_examples:
  - "A concrete example the content should use."

preferred_pov: >
  Optional. The stance to argue from.

desired_tone: >
  Clear, confident, practitioner-led, useful, non-hype.

visual_direction: >
  Optional. What this should look like.

{sizing}

must_include: []
must_avoid:
  - generic motivational language
  - unsupported statistics
  - unnecessary jargon

references: []
factual_claims_to_verify: []

cta_direction: null
urgency: evergreen     # evergreen | this_week | 24_48h
priority: 3            # 1 is highest
notes: null
"""
