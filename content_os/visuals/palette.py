"""The one place to tune the look: marker colours, outline weight, hatching and how faded "past" steps are."""

PAPER = "#FAF7F0"      # off-white paper
INK = "#16150F"        # outlines and body text
GREY = "#5F5A52"       # secondary text (darker than before so it reads on a phone)
LIGHT = "#C9C1B2"      # table rules
BLUE = "#0F5BEA"       # agents, primary numbers
RED = "#E5231A"        # alerts, TIE, the PORTION, crosses
GREEN = "#06994C"      # checks, retrieval, "true weight"
ORANGE = "#F57A00"     # the lazy version, guardrail, highlights
PURPLE = "#7B2CE0"     # matcher agent, oracle
YELLOW = "#FFD000"     # highlighter band

STROKE_SCALE = 1.2     # multiplies every outline width
HATCH_TINT_SCALE = 1.7 # multiplies the flat tint under hatching (capped at HATCH_TINT_MAX)
HATCH_TINT_MAX = 0.5
HATCH_LINE_ALPHA = 1.0 # opacity of the hatch lines themselves
DIM_ALPHA = 0.55       # faded "past" steps: clearly secondary, still readable

NAMED = {"ink": INK, "grey": GREY, "blue": BLUE, "red": RED, "green": GREEN, "orange": ORANGE, "purple": PURPLE,
         "yellow": YELLOW}

# Spec-level themes (``"theme"`` at the top of visual_cues.json): a map from the paper colours above to the
# theme's colours, applied in rough.color(). "paper" is the approved whiteboard look (16 Nov).
THEMES = {
    "paper": {},
    # dark board, bright markers (fable52 main reel)
    "dark": {
        PAPER: "#15171D", "#E4DED1": "#252935", INK: "#F3F0E8", GREY: "#A7ADB8", LIGHT: "#3B4150",
        "#FFFFFF": "#20242E", BLUE: "#4D9BFF", RED: "#FF4D3D", GREEN: "#2FD67F", ORANGE: "#FF9F2E",
        PURPLE: "#B77CFF", YELLOW: "#FFD43B",
    },
    # colder night board, blues/teals with red accents (fable52 trial reel, fear tone)
    "cold": {
        PAPER: "#0D1320", "#E4DED1": "#1B2436", INK: "#E6EEF8", GREY: "#93A3BB", LIGHT: "#2C3A52",
        "#FFFFFF": "#172033", BLUE: "#5CC8FF", RED: "#FF3B3B", GREEN: "#3FD9C2", ORANGE: "#8FA9FF",
        PURPLE: "#9D8CFF", YELLOW: "#BFD7FF",
    },
}

# Sticky-note colours that stay the same in every theme (not remapped by THEMES): readable on paper and on dark.
NAMED.update({"note": "#FFE066", "noteink": "#141414"})
