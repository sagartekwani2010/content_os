"""Brand memory: explicit, structured, versioned.

Deliberately not conversational memory. Everything the agents need to know about
positioning lives here as data, loaded from config/brand.yaml, so that a change
in brand strategy is a reviewable diff rather than a prompt edit.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class BrandPillar(BaseModel):
    key: str
    name: str
    description: str


class SignatureSeries(BaseModel):
    """A recurring format the audience learns to recognise.

    Series matter more than one-off topics because they compound: the second
    episode borrows the recognition the first one built.
    """

    name: str
    description: str


class ProductionProfile(BaseModel):
    """Physical production reality. Drives the production_fit scoring dimension."""

    avatar_share_target: float = 0.75
    default_reel_seconds: tuple[int, int] = (15, 35)
    carousel_slides: tuple[int, int] = (6, 9)
    available_modes: list[str] = Field(default_factory=list)
    constraints: list[str] = Field(default_factory=list)


class ContentLearning(BaseModel):
    """A human-approved rule distilled from a published-content review.

    Keeping the rule, evidence source, and confidence together prevents a
    one-off aesthetic preference from quietly becoming permanent brand policy.
    """

    category: Literal["content", "visual", "technical", "brand", "process"]
    rule: str
    confidence: Literal["low", "medium", "high"]
    source: str


class BrandMemory(BaseModel):
    version: int = 1
    positioning: str

    brand_pillars: list[BrandPillar] = Field(default_factory=list)
    target_audiences: list[str] = Field(default_factory=list)

    preferred_topics: list[str] = Field(default_factory=list)
    avoided_topics: list[str] = Field(default_factory=list)

    signature_opinions: list[str] = Field(default_factory=list)
    signature_series: list[SignatureSeries] = Field(default_factory=list)
    identity_themes: list[str] = Field(default_factory=list)

    winning_hook_patterns: list[str] = Field(default_factory=list)
    losing_hook_patterns: list[str] = Field(default_factory=list)
    communication_principles: list[str] = Field(default_factory=list)
    content_learning_memory: list[ContentLearning] = Field(default_factory=list)

    winning_formats: list[str] = Field(default_factory=list)
    historical_insights: list[str] = Field(default_factory=list)

    production: ProductionProfile = Field(default_factory=ProductionProfile)

    @property
    def pillar_keys(self) -> list[str]:
        return [p.key for p in self.brand_pillars]

    def pillar(self, key: str) -> BrandPillar | None:
        return next((p for p in self.brand_pillars if p.key == key), None)

    def as_prompt_context(self) -> str:
        """Render brand memory as a compact block for agent instructions.

        Kept as a method rather than a template file so that brand.yaml remains
        the single source of truth.
        """
        lines: list[str] = [f"POSITIONING: {self.positioning}", ""]

        lines.append("CONTENT PILLARS:")
        for p in self.brand_pillars:
            lines.append(f"  - {p.key} ({p.name}): {p.description}")

        lines.append("")
        lines.append(f"TARGET AUDIENCES: {', '.join(self.target_audiences)}")

        if self.signature_opinions:
            lines.append("")
            lines.append("SIGNATURE OPINIONS (these are the brand's actual positions):")
            lines += [f"  - {o}" for o in self.signature_opinions]

        if self.signature_series:
            lines.append("")
            lines.append(
                "SIGNATURE SERIES (recurring formats the audience recognises; a new "
                "episode of an established series is worth more than a one-off):"
            )
            lines += [f"  - {s.name}: {s.description}" for s in self.signature_series]

        if self.identity_themes:
            lines.append("")
            lines.append(
                "IDENTITY THEMES (content about this brand and its work, not about "
                "AI in general; this is what builds a recognisable persona):"
            )
            lines += [f"  - {t}" for t in self.identity_themes]

        if self.preferred_topics:
            lines.append("")
            lines.append(f"PREFERRED TOPICS: {', '.join(self.preferred_topics)}")
        if self.avoided_topics:
            lines.append("")
            lines.append("AVOID (do not propose these):")
            lines += [f"  - {t}" for t in self.avoided_topics]

        if self.winning_hook_patterns:
            lines.append("")
            lines.append("HOOK PATTERNS THAT WORK:")
            lines += [f"  - {h}" for h in self.winning_hook_patterns]
        if self.losing_hook_patterns:
            lines.append("")
            lines.append("HOOK PATTERNS THAT FAIL (never use):")
            lines += [f"  - {h}" for h in self.losing_hook_patterns]

        if self.communication_principles:
            lines.append("")
            lines.append("COMMUNICATION PRINCIPLES (apply these before using jargon):")
            lines += [f"  - {principle}" for principle in self.communication_principles]

        if self.content_learning_memory:
            lines.append("")
            lines.append(
                "APPROVED CONTENT LEARNINGS (apply these; do not treat them as "
                "optional stylistic suggestions):"
            )
            for learning in self.content_learning_memory:
                lines.append(
                    f"  - [{learning.category}; {learning.confidence} confidence] "
                    f"{learning.rule} (source: {learning.source})"
                )

        lines.append("")
        lines.append("PRODUCTION REALITY:")
        lines.append(
            f"  - About {int(self.production.avatar_share_target * 100)}% of Reels "
            "use an AI avatar."
        )
        lines.append(f"  - Available modes: {', '.join(self.production.available_modes)}")
        lines += [f"  - {c}" for c in self.production.constraints]

        if self.historical_insights:
            lines.append("")
            lines.append("LEARNED FROM PAST PERFORMANCE:")
            lines += [f"  - {i}" for i in self.historical_insights]

        return "\n".join(lines)
