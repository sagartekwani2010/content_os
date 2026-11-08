"""Adversarial simulations for the story and package validators.

These are deliberately small, named counterexamples. They are not a claim of
real-world engagement prediction; they tell us whether the validators enforce
the editorial rules we explicitly care about before a Reel is produced.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Literal

from content_os.agents import story_validator
from content_os.config import load_brand, load_models_config
from content_os.models.content import AssetBrief, ReelPackage, Scene
from content_os.storage.repositories import Repositories
from content_os.tools.reel_preflight import validate_asset_briefs
from content_os.tracking.run_logger import TrackedRunner


@dataclass(frozen=True)
class SimulationCase:
    name: str
    expected_story: Literal["PASS", "REWRITE", "BLOCK"]
    expected_preflight_failures: tuple[str, ...]
    package: ReelPackage


def _thumbnail() -> AssetBrief:
    return AssetBrief(
        scene_index=0, content_unit="cover", asset_id="thumbnail",
        source_type="generated_image", rendering_tool="gpt_2_5", purpose="State the precise viewer promise.",
        prompt=(
            "Create a finished 9:16 Reel cover showing a person comparing a clear "
            "system decision trace. Use one readable headline in the central square "
            "safe area, natural editorial lighting and no decorative fake interface."
        ),
        composition="Headline and subject remain inside the central 1:1 crop-safe area.",
        negative_constraints=["no robots", "no fake dashboard", "no tiny text"],
        output_filename="thumbnail.png",
        alt_text="A creator explaining a visible decision trace.",
    )


def _proof_asset(scene_index: int) -> AssetBrief:
    beats = {
        1: (
            "Show one customer message beside a clear order-status fact: the courier "
            "has not scanned the parcel. Make the unanswered question visible.",
            "Customer message and status result appear side by side before any action.",
            "Show the customer request and the raw tool fact, not an action.",
        ),
        2: (
            "Show the raw no-scan result entering one agent decision: call scan-history "
            "next because the current fact is inconclusive. Make the unanswered "
            "question and selected next tool visible.",
            "The raw result is central; one decision arrow selects the scan-history tool.",
            "Show the agent choosing a new observation rather than acting too early.",
        ),
        3: (
            "Show a late-scan tool result flowing into one explicit decision: courier "
            "investigation, not refund. Then show the next tool call being selected.",
            "The late scan is central; one arrow leads only to courier investigation.",
            "Show the tool result causing the next choice.",
        ),
        4: (
            "Show a deterministic refund-limit check blocking an automatic refund and "
            "sending an exception to a human queue. Make the stop condition obvious.",
            "A policy gate divides auto-approved cases from the human exception queue.",
            "Show the guardrail stopping the agent from overreaching.",
        ),
    }
    prompt_beat, composition, alt_text = beats[scene_index]
    return AssetBrief(
        scene_index=scene_index, content_unit="scene", asset_id=f"scene-{scene_index}-proof",
        source_type="generated_image", rendering_tool="gpt_2_5", purpose="Prove that a tool result changes the next decision.",
        prompt=(
            "Create a simple vertical editorial visual for an AI agent explanation. "
            f"{prompt_beat} Clean white background, dark navy labels, one lime accent, "
            "large legible elements, phone-safe composition, no fictional software dashboard."
        ),
        composition=composition,
        negative_constraints=["no robot", "no unreadable UI", "no neon cyberpunk"],
        output_filename=f"{scene_index:02d}-proof.png",
        alt_text=alt_text,
    )


def _package(
    *,
    title: str,
    hook: str,
    scenes: list[Scene],
    include_thumbnail: bool = True,
    include_proof_asset: bool = True,
) -> ReelPackage:
    return ReelPackage(
        brief_id="simulation", title=title, hook=hook, hook_variants=[],
        script=" ".join(scene.voiceover for scene in scenes),
        estimated_duration_seconds=20,
        learning_payoff="Viewer can distinguish a system decision from a tool result.",
        save_reason="Use this check before calling every AI step an agent.",
        share_reason="It gives a concrete way to critique agent architecture.",
        scene_plan=scenes, avatar_segments=[], screen_demo_segments=[],
        b_roll_requirements=[], avatar_requirements=[], on_screen_text=[],
        visual_hook="A visible state-to-decision trace.",
        asset_briefs=[_proof_asset(scene.index) for scene in scenes] if include_proof_asset else [],
        thumbnail_asset=_thumbnail() if include_thumbnail else None,
        caption="A short caption that adds a useful architecture detail.",
        cta="Next: which part of this loop should stay deterministic?",
        hashtags_or_keywords=[], sections_covered=[], factual_claims_to_verify=[],
        references=[],
    )


def _scene(index: int, start: float, end: float, *, voice: str, visual: str,
           new: str, question: str, shift: str, proof: str) -> Scene:
    return Scene(
        index=index, start_second=start, end_second=end, voiceover=voice,
        visual=visual, on_screen_text="", production_mode="generated_image",
        viewer_question=question, new_information=new, belief_shift=shift,
        visual_proof=proof, cut_rationale="This introduces the next story layer.",
    )


def build_simulation_cases() -> list[SimulationCase]:
    """The baseline suite: one good Reel and targeted known failure patterns."""
    good = _package(
        title="Good trace", hook="Why does an agent sometimes stop instead of acting?",
        scenes=[
            _scene(1, 0, 4, voice="A customer says their order never arrived. The order-status tool only says: no courier scan yet.",
                   visual="Customer request beside an order-status result.", new="Tools return facts, not the next action.",
                   question="Is this a refund or a courier problem?", shift="A result needs interpretation.",
                   proof="The status payload is visible with no action attached."),
            _scene(2, 4, 8, voice="No scan is inconclusive. So the agent does not refund—it calls scan history to answer one question: was this parcel ever moving?",
                   visual="Raw result routes to one scan-history tool call.", new="The agent chooses a new observation before acting.",
                   question="Was the parcel ever moving?", shift="Uncertainty should trigger investigation, not a guess.",
                   proof="The no-scan result visibly selects scan-history as the next tool."),
            _scene(3, 8, 13, voice="Scan history finds a hub scan four hours ago. Now the next action is clear: courier investigation—not refund.",
                   visual="Hub-scan result highlights courier investigation, then courier tool call.", new="New evidence resolves the action.",
                   question="Can it refund without a limit?", shift="The agent loop is visible.",
                   proof="The hub-scan result visibly causes the courier-tool route."),
            _scene(4, 13, 20, voice="A deterministic refund-limit workflow blocks exceptions and sends them to a human. That is where the agent stops.",
                   visual="Policy gate separates auto-approved cases from human exceptions.", new="Deterministic policy bounds autonomy.",
                   question="Which part of your system should stay deterministic?", shift="Agent and workflow have different jobs.",
                   proof="The exception route is visibly separated from auto-action."),
        ],
    )
    repeat = _package(
        title="Repeat contrast", hook="ChatGPT writes. Jev decides.",
        scenes=[
            _scene(1, 0, 5, voice="ChatGPT writes and Jev decides.", visual="Two model labels.",
                   new="The models have different jobs.", question="What does that difference mean?",
                   shift="Generation and decision are not identical.", proof="Two labels are compared."),
            _scene(2, 5, 10, voice="Jev decides while ChatGPT writes language.", visual="The same two labels again.",
                   new="The models have different jobs.", question="What does that difference mean?",
                   shift="Generation and decision are not identical.", proof="The same labels repeat."),
            _scene(3, 10, 20, voice="So one writes and one decides.", visual="The same labels a third time.",
                   new="The models have different jobs.", question="What does that difference mean?",
                   shift="Generation and decision are not identical.", proof="No new proof."),
        ],
    )
    implication_first = _package(
        title="Implication first", hook="This will change every shopping agent.",
        scenes=[
            _scene(1, 0, 5, voice="This will change every shopping agent.", visual="A grand claim.",
                   new="A broad implication is asserted.", question="How does it work?",
                   shift="None yet.", proof="No mechanism."),
            _scene(2, 5, 10, voice="It means better purchases and fewer mistakes.", visual="Generic shopping montage.",
                   new="Another broad implication.", question="Why would that happen?",
                   shift="Still no mechanism.", proof="No evidence."),
            _scene(3, 10, 20, voice="There is a typed decision output somewhere underneath.", visual="A vague diagram.",
                   new="A late mechanism reference.", question="What is the actual contract?",
                   shift="The explanation arrives too late.", proof="No concrete input/output."),
        ],
    )
    missing_assets = _package(
        title="Missing assets", hook="Can you see a tool result change a decision?",
        scenes=good.scene_plan, include_thumbnail=False, include_proof_asset=False,
    )
    return [
        SimulationCase("earned_mechanism", "PASS", (), good),
        SimulationCase("repeated_comparison", "REWRITE", (), repeat),
        SimulationCase("implication_before_mechanism", "REWRITE", (), implication_first),
        SimulationCase(
            "missing_thumbnail_and_visual", "PASS",
            (
                "THUMBNAIL_MISSING", "ASSET_BRIEF_MISSING:scene_1",
                "ASSET_BRIEF_MISSING:scene_2", "ASSET_BRIEF_MISSING:scene_3",
                "ASSET_BRIEF_MISSING:scene_4",
            ),
            missing_assets,
        ),
    ]


async def run_validator_simulations(repos: Repositories) -> dict[str, Any]:
    """Run the live story judge plus deterministic preflight and score the suite."""
    brand = load_brand()
    models = load_models_config()
    run_id = repos.runs.create("validator_simulations", {"suite": "baseline_v1"})
    runner = TrackedRunner(repos, run_id, models)
    rows: list[dict[str, Any]] = []
    try:
        for case in build_simulation_cases():
            result, _ = await story_validator.review(
                runner, brand, case.package, topic_title=case.package.title, models=models,
            )
            preflight = validate_asset_briefs(case.package)
            story_pass = result.output.verdict == case.expected_story
            preflight_pass = set(preflight) == set(case.expected_preflight_failures)
            rows.append({
                "name": case.name,
                "expected_story": case.expected_story,
                "observed_story": result.output.verdict,
                "story_pass": story_pass,
                "expected_preflight_failures": list(case.expected_preflight_failures),
                "observed_preflight_failures": preflight,
                "preflight_pass": preflight_pass,
                "judge_rationale": result.output.rationale,
                "passed": story_pass and preflight_pass,
            })
        report = {
            "run_id": run_id,
            "cases": rows,
            "passed": sum(row["passed"] for row in rows),
            "total": len(rows),
        }
        report["pass_rate"] = round(report["passed"] / report["total"], 3)
        repos.runs.complete(run_id, "COMPLETED", json.dumps(report, ensure_ascii=False))
    except Exception:
        repos.runs.complete(run_id, "FAILED")
        raise

    return report
