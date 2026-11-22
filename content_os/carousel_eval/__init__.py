"""Claude-owned evaluation of carousels that Codex produces.

Ownership (see AGENTS.md, "Carousel ownership"):
  Codex  owns  content_os/carousel/, tests/carousel/, and everything it writes for a carousel.
  Claude owns  content_os/carousel_eval/, tests/carousel_eval/, outputs/<id>/eval/,
               .agents/skills/carousel-production/SKILL.md.

Isolation: this package never imports content_os.carousel (or any other content_os module), so a Codex
change to the production code cannot change how a carousel is judged. The only interface is the file
contract SUBMISSION.json (see contract.py) plus the files it points to.

CLI:  python -m content_os.carousel_eval {check|eval|monitor|seal} ...
"""
