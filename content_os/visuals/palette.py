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
