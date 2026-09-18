"""Token pricing.

Cost data is only useful if it is right. These tests pin the published rates and
the rules for splitting a prompt into billing classes.
"""

from __future__ import annotations

import pytest

from content_os.config import ModelsConfig, load_models_config


@pytest.fixture
def models() -> ModelsConfig:
    return load_models_config()


class TestPublishedRates:
    @pytest.mark.parametrize(
        "model,inp,cached,out",
        [
            ("gpt-5.6-sol", 4.00, 0.40, 20.00),
            ("gpt-5.6-terra", 2.00, 0.20, 12.00),
            ("gpt-5.6-luna", 0.20, 0.02, 1.20),
        ],
    )
    def test_rates_match_official_pricing(self, models, model, inp, cached, out):
        pricing = models.price(model)
        assert pricing.input_per_mtok == inp
        assert pricing.cached_input_per_mtok == cached
        assert pricing.output_per_mtok == out

    @pytest.mark.parametrize(
        "model,expected",
        [("gpt-5.6-sol", 5.00), ("gpt-5.6-terra", 2.50), ("gpt-5.6-luna", 0.25)],
    )
    def test_cache_write_is_derived_at_1_25x_input(self, models, model, expected):
        multiplier = models.pricing_defaults.cache_write_multiplier
        assert models.price(model).cache_write_rate(multiplier) == pytest.approx(expected)

    def test_explicit_cache_write_rate_overrides_the_multiplier(self):
        from content_os.config import ModelPricing

        pricing = ModelPricing(
            input_per_mtok=4.0, output_per_mtok=20.0, cache_write_per_mtok=9.99
        )
        assert pricing.cache_write_rate(1.25) == 9.99


class TestCostComputation:
    def test_plain_call_with_no_caching(self, models):
        cost = models.compute_cost(
            "gpt-5.6-sol", input_tokens=1_000_000, output_tokens=1_000_000
        )
        assert cost.uncached_input_cost == pytest.approx(4.00)
        assert cost.output_cost == pytest.approx(20.00)
        assert cost.total_cost == pytest.approx(24.00)

    def test_cached_and_written_tokens_are_not_double_billed(self, models):
        """Cached and cache-write tokens are subsets of input_tokens. Charging
        them at the uncached rate as well would inflate every bill."""
        cost = models.compute_cost(
            "gpt-5.6-sol",
            input_tokens=100_000,
            output_tokens=0,
            cached_input_tokens=60_000,
            cache_write_tokens=20_000,
        )
        assert cost.uncached_input_tokens == 20_000
        assert cost.uncached_input_cost == pytest.approx(20_000 * 4.00 / 1e6)
        assert cost.cached_input_cost == pytest.approx(60_000 * 0.40 / 1e6)
        assert cost.cache_write_cost == pytest.approx(20_000 * 5.00 / 1e6)
        assert cost.total_cost == pytest.approx(0.08 + 0.024 + 0.10)

    def test_caching_is_cheaper_than_not_caching(self, models):
        uncached = models.compute_cost(
            "gpt-5.6-sol", input_tokens=100_000, output_tokens=0
        )
        cached = models.compute_cost(
            "gpt-5.6-sol", input_tokens=100_000, output_tokens=0,
            cached_input_tokens=90_000,
        )
        assert cached.total_cost < uncached.total_cost

    def test_components_never_go_negative(self, models):
        """A provider reporting an unexpected split must not produce a refund."""
        cost = models.compute_cost(
            "gpt-5.6-sol",
            input_tokens=1000,
            output_tokens=-50,
            cached_input_tokens=900,
            cache_write_tokens=900,
        )
        assert cost.uncached_input_tokens == 0
        assert cost.output_tokens == 0
        assert cost.total_cost >= 0.0

    def test_variant_costs_are_correctly_ordered_and_separated(self, models):
        """The spread is what makes the terra-versus-luna benchmark worth
        running: same workload, an order of magnitude apart in cost."""
        args = dict(input_tokens=100_000, output_tokens=20_000)
        sol = models.compute_cost("gpt-5.6-sol", **args).total_cost
        terra = models.compute_cost("gpt-5.6-terra", **args).total_cost
        luna = models.compute_cost("gpt-5.6-luna", **args).total_cost

        # 100k in + 20k out: sol 0.40+0.40, terra 0.20+0.24, luna 0.02+0.024
        assert sol == pytest.approx(0.80)
        assert terra == pytest.approx(0.44)
        assert luna == pytest.approx(0.044)
        assert sol > terra > luna
        assert terra / luna == pytest.approx(10.0)

    def test_unknown_model_costs_zero_and_is_flagged(self, models):
        cost = models.compute_cost("no-such-model", input_tokens=1000, output_tokens=1000)
        assert cost.total_cost == 0.0
        assert cost.priced is False


class TestUsageExtraction:
    def test_missing_detail_objects_do_not_crash(self):
        from content_os.tracking.run_logger import extract_usage

        class Bare:
            requests = 1
            input_tokens = 100
            output_tokens = 50
            total_tokens = 150

        tokens = extract_usage(Bare())
        assert tokens["input_tokens"] == 100
        assert tokens["cached_input_tokens"] == 0
        assert tokens["cache_write_tokens"] == 0
        assert tokens["reasoning_tokens"] == 0

    def test_full_usage_object_is_read_completely(self):
        from agents.usage import Usage
        from openai.types.responses.response_usage import (
            InputTokensDetails,
            OutputTokensDetails,
        )
        from content_os.tracking.run_logger import extract_usage

        usage = Usage(
            requests=2, input_tokens=1000, output_tokens=400, total_tokens=1400,
            input_tokens_details=InputTokensDetails(
                cached_tokens=600, cache_write_tokens=200
            ),
            output_tokens_details=OutputTokensDetails(reasoning_tokens=250),
        )
        tokens = extract_usage(usage)
        assert tokens == {
            "requests": 2, "input_tokens": 1000, "cached_input_tokens": 600,
            "cache_write_tokens": 200, "output_tokens": 400,
            "reasoning_tokens": 250, "total_tokens": 1400,
        }


class TestLedgerCompleteness:
    def test_every_required_field_is_a_column(self, repos):
        required = {
            "model", "reasoning_effort", "input_tokens", "cached_input_tokens",
            "cache_write_tokens", "output_tokens", "reasoning_tokens",
            "estimated_cost", "prompt_version", "trace_id", "agent_name",
            "workflow_name", "topic_id", "content_id",
        }
        columns = {
            row["name"] for row in repos.conn.execute("PRAGMA table_info(agent_runs)")
        }
        assert required <= columns, f"missing: {sorted(required - columns)}"

    def test_migration_adds_columns_to_an_existing_database(self, tmp_path):
        """An old database must gain the new columns, not be recreated."""
        import sqlite3
        from content_os.storage.db import migrate

        path = tmp_path / "old.db"
        conn = sqlite3.connect(str(path))
        conn.row_factory = sqlite3.Row
        conn.execute(
            "CREATE TABLE agent_runs (id TEXT PRIMARY KEY, model TEXT, "
            "input_tokens INTEGER, output_tokens INTEGER)"
        )
        conn.execute("INSERT INTO agent_runs VALUES ('a1','gpt-5',100,50)")

        applied = migrate(conn)
        assert "agent_runs.cached_input_tokens" in applied
        assert "agent_runs.reasoning_effort" in applied

        row = conn.execute("SELECT * FROM agent_runs WHERE id='a1'").fetchone()
        assert row["input_tokens"] == 100, "existing data survives"
        assert row["cached_input_tokens"] == 0, "new column gets its default"

    def test_migration_is_idempotent(self, tmp_path):
        from content_os.storage.db import get_db, migrate

        conn = get_db(tmp_path / "x.db")
        assert migrate(conn) == [], "a current schema needs no changes"
