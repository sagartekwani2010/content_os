"""Hand-drawn, word-anchored animated visuals for the top panel of a split-screen reel.

``python -m content_os.visuals render <reel_dir> [--preview]`` renders one MP4 per beat from
``<reel_dir>/visual_cues.json``; ``preview`` builds a synthetic-voice split-screen preview.
Cue format: ``content_os/visuals/cues.py``; scenes and sourced numbers: ``scenes.py``.
"""

SCHEMA = "content_os.visuals/spec@2"
