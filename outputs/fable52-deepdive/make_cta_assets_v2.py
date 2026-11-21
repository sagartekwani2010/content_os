"""CTA assets for the v2 reels, written to <reel>/assets/:

- diagram_training.png: last frame of beat 4 (the condensed training pipeline, complete)
- diagram_system.png: last frame of beat 11 (this reel's model routing)
- fable_user_rules.png: the FABLE USER RULES card (1080x960, the screenshot people get for "Comment FABLE")

    PYTHONPATH=. .venv/bin/python outputs/fable52-deepdive/make_cta_assets_v2.py ~/Movies/ContentOS/fable52-main
"""

from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
from content_os.visuals.build import load_sheet, resolve_assets  # noqa: E402
from content_os.visuals.cues import default_duration  # noqa: E402
from content_os.visuals.render import BeatRenderer  # noqa: E402
from content_os.visuals.scenes import validate_spec  # noqa: E402
from make_visual_specs_v2 import RULES_CARD  # noqa: E402


def main(reel_dir: str) -> None:
    reel = Path(reel_dir).expanduser()
    sheet = load_sheet(reel / "visual_cues.json")  # also sets the reel's theme
    ctx, _ = resolve_assets(sheet.get("params", {}), reel)
    out = reel / "assets"
    out.mkdir(exist_ok=True)
    by = {int(b["beat"]): b for b in sheet["beats"]}
    for n, name in ((4, "diagram_training.png"), (11, "diagram_system.png")):
        r = BeatRenderer(by[n], ctx, [], float(default_duration(by[n]["line"])))
        Image.fromarray(r.frame(r.duration - 0.05)).convert("RGB").save(out / name)
        print(out / name)
    card = {"beat": 99, "template": "rules_card", "params": RULES_CARD, "cues": [], "line": "card"}
    errs = validate_spec({"beats": [card]}, ctx)
    if errs:
        raise SystemExit("rules card: " + "; ".join(errs))
    r = BeatRenderer(card, ctx, [], 1.0)
    Image.fromarray(r.frame(0.9)).convert("RGB").save(out / "fable_user_rules.png")
    print(out / "fable_user_rules.png")


if __name__ == "__main__":
    main(sys.argv[1])
