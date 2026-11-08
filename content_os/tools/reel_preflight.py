"""Deterministic preflight checks for publishable content packages.

These do not try to judge taste. They prevent an LLM from approving an asset
plan that cannot be produced cleanly in the creator's ChatGPT UI.
"""

from __future__ import annotations

from typing import Any

from content_os.models.content import AssetBrief

GENERATED = {"generated_image", "generated_video"}


def validate_asset_briefs(package: Any) -> list[str]:
    """Return blocking asset-brief errors, never silently repair them."""
    errors: list[str] = []
    seen: set[tuple[str, int]] = set()

    thumbnail = getattr(package, "thumbnail_asset", None)
    if thumbnail is None:
        errors.append("THUMBNAIL_MISSING")
    else:
        _validate_asset(thumbnail, errors)
        if thumbnail.source_type not in GENERATED | {"reference_edit"}:
            errors.append("THUMBNAIL_NOT_RENDERABLE")

    for asset in getattr(package, "asset_briefs", []):
        seen.add((asset.content_unit, asset.scene_index))
        _validate_asset(asset, errors)

    if hasattr(package, "scene_plan"):
        for scene in package.scene_plan:
            mode = scene.production_mode.lower()
            if any(token in mode for token in ("generated", "b_roll", "video", "image")):
                if ("scene", scene.index) not in seen:
                    errors.append(f"ASSET_BRIEF_MISSING:scene_{scene.index}")
    elif hasattr(package, "slides"):
        for slide in package.slides:
            if ("slide", slide.index) not in seen:
                errors.append(f"ASSET_BRIEF_MISSING:slide_{slide.index}")

    if not getattr(package, "caption", "").strip():
        errors.append("CAPTION_MISSING")

    return errors


def _validate_asset(asset: AssetBrief, errors: list[str]) -> None:
    prefix = f"scene_{asset.scene_index}"
    if not asset.purpose.strip():
        errors.append(f"ASSET_PURPOSE_MISSING:{prefix}")
    if not asset.output_filename.strip():
        errors.append(f"ASSET_FILENAME_MISSING:{prefix}")
    if asset.source_type in GENERATED:
        expected_tool = "gpt_2_5" if asset.source_type == "generated_image" else "h3"
        if asset.rendering_tool != expected_tool:
            errors.append(f"RENDERING_TOOL_INVALID:{prefix}:expected_{expected_tool}")
        if len(asset.prompt.strip()) < 120:
            errors.append(f"GENERATED_PROMPT_TOO_THIN:{prefix}")
        if not asset.composition.strip():
            errors.append(f"COMPOSITION_MISSING:{prefix}")
        if not asset.negative_constraints:
            errors.append(f"NEGATIVE_CONSTRAINTS_MISSING:{prefix}")
        if asset.source_type == "generated_video":
            if not asset.motion_beats or asset.duration_seconds is None:
                errors.append(f"VIDEO_MOTION_OR_DURATION_MISSING:{prefix}")
    if asset.source_type in {"real_capture", "screen_recording", "reference_edit"}:
        if not asset.source_materials:
            errors.append(f"SOURCE_MATERIALS_MISSING:{prefix}")
