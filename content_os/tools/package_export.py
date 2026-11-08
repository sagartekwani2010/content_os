"""Export a complete, handoff-ready content package to the workspace.

The generative model produces copy and asset instructions. ChatGPT UI remains
the preferred renderer, so this module makes the handoff tangible: a caption
file, package JSON, asset manifest, and one ready-to-paste prompt per asset.
Rendered files can later be attached into the same package directory.
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Any

from content_os.ids import slugify


def export_content_package(
    *,
    content_id: str,
    package: Any,
    qa: Any,
    root: str | Path = "outputs",
) -> Path:
    """Create a deterministic package directory and return its path."""
    short_id = content_id.rsplit("_", 1)[-1]
    directory = Path(root) / f"{slugify(package.title)}-{short_id}"
    assets_dir = directory / "assets"
    prompts_dir = directory / "asset-prompts"
    assets_dir.mkdir(parents=True, exist_ok=True)
    prompts_dir.mkdir(parents=True, exist_ok=True)

    planned_assets = list(getattr(package, "asset_briefs", []))
    thumbnail = getattr(package, "thumbnail_asset", None)
    if thumbnail is not None:
        planned_assets.insert(0, thumbnail)

    asset_manifest: list[dict[str, Any]] = []
    prompt_pages: list[str] = ["# Asset prompts", ""]
    for number, asset in enumerate(planned_assets, start=1):
        filename = asset.output_filename or f"{number:02d}-asset"
        relative_path = f"assets/{filename}"
        prompt_file = prompts_dir / f"{number:02d}-{slugify(asset.asset_id or filename)}.md"
        entry = asset.model_dump()
        entry.update({
            "package_path": relative_path,
            "status": "attached" if (assets_dir / filename).exists() else "prompt_ready",
            "prompt_file": str(prompt_file.relative_to(directory)),
        })
        asset_manifest.append(entry)
        prompt_text = _asset_prompt(asset, relative_path)
        prompt_file.write_text(prompt_text, encoding="utf-8")
        prompt_pages += [f"## {number}. {asset.asset_id or filename}", "", prompt_text, ""]

    payload = {
        "content_id": content_id,
        "package": package.model_dump(),
        "qa": qa.model_dump() if hasattr(qa, "model_dump") else qa,
        "assets": asset_manifest,
        "caption_file": "caption.txt",
    }
    (directory / "package.json").write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    (directory / "asset-manifest.json").write_text(
        json.dumps(asset_manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    (directory / "caption.txt").write_text(package.caption.strip() + "\n", encoding="utf-8")
    (directory / "ASSET_PROMPTS.md").write_text(
        "\n".join(prompt_pages).rstrip() + "\n", encoding="utf-8"
    )
    return directory


def attach_rendered_assets(package_dir: str | Path, source_dir: str | Path) -> list[str]:
    """Copy matching rendered files into a package's assets folder.

    The renderer (normally ChatGPT UI) stays outside the content pipeline. This
    lets the creator download its output anywhere, then attach only files whose
    names were assigned by the asset manifest. Existing files are replaced only
    when the creator explicitly runs this command again.
    """
    directory = Path(package_dir)
    source = Path(source_dir)
    manifest_path = directory / "asset-manifest.json"
    if not manifest_path.exists():
        raise FileNotFoundError(f"No asset manifest at {manifest_path}")
    if not source.is_dir():
        raise NotADirectoryError(f"Asset source directory not found: {source}")

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assets_dir = directory / "assets"
    assets_dir.mkdir(exist_ok=True)
    attached: list[str] = []
    for entry in manifest:
        filename = Path(entry["package_path"]).name
        candidate = source / filename
        if not candidate.is_file():
            continue
        shutil.copy2(candidate, assets_dir / filename)
        entry["status"] = "attached"
        entry["asset_path"] = entry["package_path"]
        attached.append(filename)

    manifest_path.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    package_path = directory / "package.json"
    if package_path.exists():
        payload = json.loads(package_path.read_text(encoding="utf-8"))
        payload["assets"] = manifest
        package_path.write_text(
            json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
        )
    return attached


def _asset_prompt(asset: Any, relative_path: str) -> str:
    """Format the exact handoff prompt rather than hiding it inside JSON."""
    lines = [
        f"# {asset.asset_id or relative_path}",
        "",
        f"Save the finished asset as: `{relative_path}`",
        f"Content unit: {asset.content_unit} {asset.scene_index}",
        f"Source type: {asset.source_type}",
        f"Purpose: {asset.purpose}",
        f"Source materials to upload: {', '.join(asset.source_materials) or 'none'}",
        "",
        "## Final prompt",
        asset.prompt or "Use the specified real capture/source material.",
        "",
        "## Composition",
        asset.composition or "Use the native layout of the supplied source.",
    ]
    if asset.motion_beats:
        lines += ["", "## Motion", *[f"- {beat}" for beat in asset.motion_beats]]
    if asset.duration_seconds is not None:
        lines += ["", f"Duration: {asset.duration_seconds:g} seconds"]
    if asset.on_screen_copy:
        lines += ["", "## Exact on-screen copy", *[f"- {copy}" for copy in asset.on_screen_copy]]
    if asset.negative_constraints:
        lines += ["", "## Do not include", *[f"- {item}" for item in asset.negative_constraints]]
    if asset.alt_text:
        lines += ["", f"Alt text: {asset.alt_text}"]
    return "\n".join(lines)
