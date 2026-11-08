"""Deterministic checks for the Reel story and asset-production gates."""

from __future__ import annotations

from content_os.agents.story_validator import failed_gates
from content_os.models.content import AssetBrief, ReelPackage, Scene, StorySceneAssessment, StoryVerdict
from content_os.tools.package_export import attach_rendered_assets, export_content_package
from content_os.tools.reel_preflight import validate_asset_briefs


def _thumbnail() -> AssetBrief:
    return AssetBrief(
        scene_index=0, content_unit="cover", asset_id="thumbnail",
        source_type="generated_image", rendering_tool="gpt_2_5", purpose="Make the viewer promise clear.",
        prompt=(
            "Create a finished vertical cover with one clear visual subject, large "
            "readable headline in the central safe area, natural lighting, and no "
            "decorative interface elements or unreadable tiny type."
        ),
        composition="Subject and headline stay in the central 1:1 safe area.",
        negative_constraints=["no fake dashboard"], output_filename="thumbnail.png",
        alt_text="A clear content thumbnail.",
    )


def _package(*, assets: list[AssetBrief] | None = None) -> ReelPackage:
    return ReelPackage(
        brief_id="brief_test",
        title="A useful Reel",
        hook="Here is the question this Reel answers.",
        hook_variants=[],
        script="A concise, useful script.",
        estimated_duration_seconds=20,
        learning_payoff="Viewer can tell whether a visual demonstrates a claim.",
        save_reason="Use the checklist before commissioning an asset.",
        share_reason="It prevents wasted time and vague image prompts.",
        scene_plan=[
            Scene(
                index=1, start_second=0, end_second=5,
                visual="A generated visual proves the hook.",
                voiceover="A precise idea.", on_screen_text="A precise idea.",
                production_mode="generated_image",
            )
        ],
        avatar_segments=[], screen_demo_segments=[], b_roll_requirements=[],
        avatar_requirements=[], on_screen_text=[], visual_hook="A real proof.",
        asset_briefs=assets or [], thumbnail_asset=_thumbnail(), caption="caption", cta=None,
        hashtags_or_keywords=[], sections_covered=[],
        factual_claims_to_verify=[], references=[],
    )


def test_generated_reel_scene_requires_an_asset_brief():
    assert validate_asset_briefs(_package()) == ["ASSET_BRIEF_MISSING:scene_1"]


def test_generated_asset_needs_a_production_ready_prompt():
    package = _package(assets=[
        AssetBrief(
            scene_index=1, source_type="generated_video", rendering_tool="h3", purpose="Show the proof.",
            prompt="too short", composition="", negative_constraints=[],
            output_filename="proof.mp4",
        )
    ])

    failures = validate_asset_briefs(package)
    assert "GENERATED_PROMPT_TOO_THIN:scene_1" in failures
    assert "COMPOSITION_MISSING:scene_1" in failures
    assert "NEGATIVE_CONSTRAINTS_MISSING:scene_1" in failures
    assert "VIDEO_MOTION_OR_DURATION_MISSING:scene_1" in failures


def test_thumbnail_is_a_required_publish_asset():
    package = _package()
    package.thumbnail_asset = None

    assert "THUMBNAIL_MISSING" in validate_asset_briefs(package)


def test_exported_package_contains_caption_thumbnail_and_attachable_assets(tmp_path):
    package = _package(assets=[
        AssetBrief(
            scene_index=1, content_unit="scene", asset_id="proof",
            source_type="generated_image", rendering_tool="gpt_2_5", purpose="Show the visual proof.",
            prompt=(
                "Create a focused vertical visual that clearly proves the scene's "
                "claim using one real-world subject, simple composition, natural "
                "lighting and absolutely no decorative dashboard or tiny text."
            ),
            composition="The proof is centred with safe space above it.",
            negative_constraints=["no fake UI"], output_filename="01-proof.png",
            alt_text="The proof visual.",
        )
    ])

    package_dir = export_content_package(
        content_id="content_test123", package=package, qa={"approved": False}, root=tmp_path,
    )
    assert (package_dir / "caption.txt").read_text(encoding="utf-8") == "caption\n"
    assert (package_dir / "asset-prompts" / "01-thumbnail.md").exists()
    assert (package_dir / "assets").is_dir()

    source = tmp_path / "rendered"
    source.mkdir()
    (source / "thumbnail.png").write_bytes(b"thumbnail")
    attached = attach_rendered_assets(package_dir, source)
    assert attached == ["thumbnail.png"]
    assert (package_dir / "assets" / "thumbnail.png").read_bytes() == b"thumbnail"


def test_story_gate_rejects_a_repeated_story_without_a_turn():
    verdict = StoryVerdict(
        verdict="REWRITE", narrative_spine="The same point twice.",
        viewer_question_by_second_five="What changes?",
        story_turn_scene_index=None, reveal_or_proof_by_second_fifteen=None,
        scene_assessments=[
            StorySceneAssessment(scene_index=1, advances_story=True),
            StorySceneAssessment(scene_index=2, advances_story=False, issue="Repeats scene 1."),
        ],
        repeated_claims=["The same point twice."], issues=[], required_changes=[],
        rationale="It stalls.",
    )

    failures = failed_gates(verdict)
    assert "STORY_REWRITE" in failures
    assert "STORY_NO_TURN" in failures
    assert "STORY_NO_EARLY_PROOF" in failures
    assert "STORY_STALLED_SCENES:2" in failures
