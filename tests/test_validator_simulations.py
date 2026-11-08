"""The named validator simulations must remain deterministic and runnable."""

from content_os.tools.reel_preflight import validate_asset_briefs
from content_os.tools.validator_simulations import build_simulation_cases


def test_baseline_simulation_preflight_expectations_are_exact():
    cases = build_simulation_cases()
    assert [case.name for case in cases] == [
        "earned_mechanism",
        "repeated_comparison",
        "implication_before_mechanism",
        "missing_thumbnail_and_visual",
    ]
    for case in cases:
        assert set(validate_asset_briefs(case.package)) == set(
            case.expected_preflight_failures
        )
