"""Save the two finished diagrams as stills for the CTA beat (assets/diagram_training.png, assets/diagram_meal.png).

    .venv/bin/python outputs/fable52-deepdive/make_cta_stills.py ~/Movies/ContentOS/fable52-main [main-beat-of-full-picture]

Training pipeline: the last frame of the "full picture" beat (complete diagram, wrapper drawn).
Meal Analyser: the frame just before that beat switches to the plate photo.
"""

from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image

from content_os.visuals.build import load_sheet, resolve_assets
from content_os.visuals.cues import default_duration
from content_os.visuals.render import BeatRenderer


def main(reel_dir: str) -> None:
    reel = Path(reel_dir).expanduser()
    sheet = load_sheet(reel / "visual_cues.json")
    ctx, _ = resolve_assets(sheet.get("params", {}), reel)
    full = next(b for b in sheet["beats"] if b["line"].startswith("Here's the full picture"))
    meal = next(b for b in sheet["beats"] if b["line"].startswith("So where does it earn"))
    out = reel / "assets"
    out.mkdir(exist_ok=True)
    for b, name, pick in ((full, "diagram_training.png", lambda r: r.duration - 0.05),
                          (meal, "diagram_meal.png", lambda r: r.scenes[1].start - 0.1)):
        r = BeatRenderer(b, ctx, [], float(default_duration(b["line"])))
        Image.fromarray(r.frame(pick(r))).convert("RGB").save(out / name)
        print(out / name)


if __name__ == "__main__":
    main(sys.argv[1])
