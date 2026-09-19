"""Portfolio composition. The strategist must not return ten identical posts."""

from __future__ import annotations

from content_os.models.content import ContentPlanItem
from content_os.tools.scoring import analyse_portfolio, portfolio_gap_brief


def item(pillar: str, fmt: str = "reel", topic_id: str | None = None) -> ContentPlanItem:
    return ContentPlanItem(
        topic_id=topic_id or f"top_{pillar}_{fmt}_{id(object())}",
        proposed_title=f"{pillar} post",
        format=fmt,
        pillar=pillar,
        strategic_role="authority",
        recommended_publish_window=None,
        urgency="evergreen",
        reasoning="because",
        primary_hook="hook",
        alternate_hooks=[],
        score=8.0,
    )


class TestPortfolioBalance:
    def test_empty_plan_is_flagged(self, cfg):
        report = analyse_portfolio([], cfg)
        assert report["balanced"] is False
        assert "EMPTY_PLAN" in report["violations"]

    def test_ten_identical_agent_posts_are_rejected(self, cfg):
        """The exact failure the strategist exists to prevent."""
        plan = [item("ai_builder") for _ in range(10)]
        report = analyse_portfolio(plan, cfg)

        assert report["balanced"] is False
        assert any(v.startswith("PILLAR_OVER_CAP") for v in report["violations"])
        assert any(v.startswith("TOO_FEW_PILLARS") for v in report["violations"])
        assert any(v.startswith("FORMAT_STREAK") for v in report["violations"])

    def test_a_spread_plan_passes(self, cfg):
        plan = [
            item("ai_builder", "reel"),
            item("ai_builder", "carousel"),
            item("ai_pov", "reel"),
            item("ai_pov", "carousel"),
            item("ai_experiments", "reel"),
            item("ai_real_life", "carousel"),
            item("ai_future", "reel"),
        ]
        report = analyse_portfolio(plan, cfg)
        assert report["violations"] == []
        assert report["balanced"] is True
        assert report["distinct_pillars"] == 5

    def test_pillar_cap_is_enforced(self, cfg):
        """Five of seven posts in one pillar exceeds the cap at that size."""
        plan = [item("ai_builder", "reel" if i % 2 else "carousel") for i in range(5)]
        plan += [item("ai_pov"), item("ai_future")]
        report = analyse_portfolio(plan, cfg)
        assert any("PILLAR_OVER_CAP:ai_builder" in v for v in report["violations"])


class TestPillarCapScaling:
    """A fixed cap is a weekly-scale rule that breaks on longer plans."""

    def test_cap_scales_with_plan_size(self, cfg):
        portfolio = cfg.portfolio
        caps = [portfolio.pillar_cap(n) for n in (5, 7, 10, 15, 20)]
        assert caps == sorted(caps), "cap must not shrink as plans grow"
        assert portfolio.pillar_cap(15) > portfolio.pillar_cap(7)

    def test_cap_never_contradicts_the_largest_target(self, cfg):
        """At 15 posts a fixed cap of 3 would forbid the 30% target, which
        wants 4.5. The cap must never make the targets unsatisfiable."""
        portfolio = cfg.portfolio
        for total in (5, 7, 10, 15, 20, 30):
            cap = portfolio.pillar_cap(total)
            for share in portfolio.targets.values():
                assert cap >= share * total, (
                    f"cap {cap} forbids target {share:.0%} at {total} posts"
                )

    def test_small_plans_keep_the_configured_floor(self, cfg):
        assert cfg.portfolio.pillar_cap(1) >= cfg.portfolio.max_per_pillar
        assert cfg.portfolio.pillar_cap(4) >= cfg.portfolio.max_per_pillar

    def test_fifteen_post_plan_at_target_distribution_passes(self, cfg):
        """The launch-sized plan the targets actually describe must validate."""
        plan = (
            [item("ai_builder") for _ in range(5)]
            + [item("ai_pov", "carousel") for _ in range(4)]
            + [item("ai_experiments") for _ in range(3)]
            + [item("ai_real_life", "carousel") for _ in range(2)]
            + [item("ai_future")]
        )
        # Interleave formats so the streak guardrail is not the thing under test.
        plan = [
            p if i % 2 else item(p.pillar, "carousel" if p.format == "reel" else "reel")
            for i, p in enumerate(plan)
        ]
        report = analyse_portfolio(plan, cfg)
        over_cap = [v for v in report["violations"] if v.startswith("PILLAR_OVER_CAP")]
        assert over_cap == [], f"target distribution rejected: {over_cap}"

    def test_format_streak_is_detected(self, cfg):
        plan = [item(p, "reel") for p in
                ("ai_builder", "ai_pov", "ai_future", "ai_real_life")]
        report = analyse_portfolio(plan, cfg)
        assert report["max_same_format_streak"] == 4
        assert any(v.startswith("FORMAT_STREAK") for v in report["violations"])

    def test_duplicate_topics_are_detected(self, cfg):
        plan = [
            item("ai_builder", "reel", topic_id="top_same"),
            item("ai_pov", "carousel", topic_id="top_same"),
            item("ai_future", "reel", topic_id="top_other"),
        ]
        report = analyse_portfolio(plan, cfg)
        assert any(v.startswith("DUPLICATE_TOPICS") for v in report["violations"])

    def test_unknown_pillar_is_flagged(self, cfg):
        report = analyse_portfolio([item("crypto_news")], cfg)
        assert any("UNKNOWN_PILLAR:crypto_news" in v for v in report["violations"])

    def test_distribution_sums_to_one(self, cfg):
        plan = [item("ai_builder"), item("ai_pov"), item("ai_future"), item("ai_pov")]
        report = analyse_portfolio(plan, cfg)
        assert sum(report["distribution"].values()) == 1.0

    def test_gap_brief_names_the_missing_pillars(self, cfg):
        brief = portfolio_gap_brief([item("ai_builder") for _ in range(5)], cfg, 7)
        assert "ai_pov" in brief
        assert "Guardrail violations" in brief
