"""Anchored cues: every animation event names a spoken word; times are resolved against the
selected take's word timestamps at render time.

Cue (one entry of ``beats[i].cues`` in visual_cues.json)::

    {"on_word": "seventy-seven" | "77" | "thirteen thousand" | 5,   # phrase in the beat line, or word index
     "occurrence": 1,           # nth occurrence of the phrase in the line (default 1)
     "anchor": "start|end",     # word start (default) or the phrase's last word end
     "offset": -0.25,           # seconds relative to the anchor (default -0.25: land early, the picture leads the word)
     "action": "draw|pop|countup|write|highlight|cross|fade|shake",
     "target": "element_id",
     "dur": 0.5,                # 0.3-0.8 s (default 0.45, emphasis 0.7)
     "emphasis": false}         # strongest motion: overshoot, burst lines, marker highlight

Resolution order per cue: ``exact`` (the scripted word was aligned to a transcribed word),
``interpolated`` (the word was not recognised; time interpolated between the nearest aligned
neighbours), ``proportional`` (no usable transcript: the word's position in the line times the beat's
speech span). Fallbacks are listed in the report so they can be checked by eye. A motion that would
still be running when the beat's clip ends (cues on the last words of a line) is moved earlier so it
completes two frames before the cut; those moves are reported as ``fit_shifts``.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from content_os.pipeline.textmatch import align, norm

ACTIONS = {"draw", "pop", "countup", "write", "highlight", "cross", "fade", "shake"}
DEFAULT_OFFSET = -0.25  # policy (16 Nov): every element lands on or ~0.2-0.3 s before the word naming it
DEFAULT_DUR = 0.45
EMPHASIS_DUR = 0.7
MIN_DUR, MAX_DUR = 0.3, 0.8
FIT_MARGIN = 2 / 30  # every motion completes at least two frames before the beat's clip ends
COUNTUP_HOLD = 0.6   # a counted number shows its final value for at least this long before the cut
INSTANT = 1e-3       # "duration" of a countup that has no room: the final value appears at once

_ONES = ["zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten", "eleven",
         "twelve", "thirteen", "fourteen", "fifteen", "sixteen", "seventeen", "eighteen", "nineteen"]
_TENS = ["", "", "twenty", "thirty", "forty", "fifty", "sixty", "seventy", "eighty", "ninety"]


def int_words(n: int) -> list[str]:
    if n < 20:
        return [_ONES[n]]
    if n < 100:
        return [_TENS[n // 10]] + ([_ONES[n % 10]] if n % 10 else [])
    if n < 1000:
        return [_ONES[n // 100], "hundred"] + (int_words(n % 100) if n % 100 else [])
    for div, name in ((10 ** 9, "billion"), (10 ** 6, "million"), (1000, "thousand")):
        if n >= div:
            return int_words(n // div) + [name] + (int_words(n % div) if n % div else [])
    return [str(n)]


def expand(word: str) -> list[str]:
    """Spoken-form tokens of one written word: '84' -> eighty four, '13,224' -> thirteen thousand two
    hundred twenty four, '0.3' -> zero point three, '5.2' -> five point two, 'seventy-seven' -> seventy seven."""
    w = word.lower().replace("’", "'").strip()
    w = w.rstrip(".,;:!?\"')]}").lstrip("\"'([{")
    m = re.fullmatch(r"(\d{1,3}(?:,\d{3})+|\d+)?(?:\.(\d+))?(%?)", w)
    if m and (m.group(1) or m.group(2)):
        out = int_words(int(m.group(1).replace(",", ""))) if m.group(1) else []
        if m.group(2):
            out += ["point"] + [_ONES[int(d)] for d in m.group(2)]
        if m.group(3):
            out.append("percent")
        return out
    out = []
    for part in re.split(r"[\s—–/-]+", w):
        t = norm(part)
        if t:
            out.append(t)
    return out


def spoken_tokens(words: list[str]) -> tuple[list[str], list[int]]:
    """Expanded tokens and, per token, the index of the word it came from."""
    toks, src = [], []
    for i, w in enumerate(words):
        for t in expand(w):
            toks.append(t)
            src.append(i)
    return toks, src


def line_words(line: str) -> list[str]:
    return [w for w in re.split(r"\s+", line.strip()) if w]


@dataclass
class Resolved:
    target: str
    action: str
    t: float
    dur: float
    emphasis: bool
    method: str
    on_word: object
    matched: str | None = None
    params: dict | None = None

    def as_dict(self) -> dict:
        return {"target": self.target, "action": self.action, "t": round(self.t, 3), "dur": round(self.dur, 3),
                "emphasis": self.emphasis, "method": self.method, "on_word": self.on_word, "matched": self.matched}


def find_phrase(script_toks: list[str], phrase_toks: list[str], occurrence: int = 1) -> int | None:
    n = len(phrase_toks)
    seen = 0
    for i in range(len(script_toks) - n + 1):
        if script_toks[i:i + n] == phrase_toks:
            seen += 1
            if seen == occurrence:
                return i
    return None


def speech_span(words: list[dict], duration: float) -> tuple[float, float]:
    if words:
        return float(words[0]["start"]), float(words[-1].get("end", words[-1]["start"]))
    lead = min(0.3, duration * 0.1)
    return lead, max(lead + 0.1, duration - lead)


def resolve_beat(line: str, cues: list[dict], words: list[dict], duration: float) -> tuple[list[Resolved], dict]:
    """Resolve every cue of one beat. ``words``: [{"text", "start", "end"}] in seconds from the clip start."""
    sw = line_words(line)
    s_toks, s_src = spoken_tokens(sw)
    h_toks, h_src = spoken_tokens([w["text"] for w in words])
    pairs = align(h_toks, s_toks, 0.8) if words else []
    s2h = {j: i for i, j in pairs}
    span0, span1 = speech_span(words, duration)
    out: list[Resolved] = []
    problems, shifts = [], []

    def tok_time(j: int, end: bool) -> tuple[float, str]:
        if j in s2h:
            w = words[h_src[s2h[j]]]
            return float(w["end"] if end else w["start"]), "exact"
        if pairs:
            before = [(jj, ii) for ii, jj in pairs if jj < j]
            after = [(jj, ii) for ii, jj in pairs if jj > j]
            if before and after:
                (jb, ib), (ja, ia) = before[-1], after[0]
                tb = float(words[h_src[ib]]["end"])
                ta = float(words[h_src[ia]]["start"])
                return tb + (ta - tb) * (j - jb) / (ja - jb), "interpolated"
            if before:
                jb, ib = before[-1]
                tb = float(words[h_src[ib]]["end"])
                rate = (span1 - span0) / max(1, len(s_toks))
                return min(duration, tb + rate * (j - jb - 1)), "interpolated"
            ja, ia = after[0]
            ta = float(words[h_src[ia]]["start"])
            rate = (span1 - span0) / max(1, len(s_toks))
            return max(0.0, ta - rate * (ja - j)), "interpolated"
        frac = (j + (1 if end else 0)) / max(1, len(s_toks))
        return span0 + (span1 - span0) * frac, "proportional"

    for k, c in enumerate(cues):
        action = c.get("action", "pop")
        if action not in ACTIONS:
            raise ValueError(f"cue {k}: unknown action {action!r}")
        ow = c["on_word"]
        if isinstance(ow, int):
            if not 0 <= ow < len(sw):
                raise ValueError(f"cue {k}: word index {ow} outside line ({len(sw)} words)")
            idx = [j for j, s in enumerate(s_src) if s == ow]
            j0, j1 = idx[0], idx[-1]
            matched = sw[ow]
        else:
            ptoks = [t for w in line_words(str(ow)) for t in expand(w)]
            j0 = find_phrase(s_toks, ptoks, int(c.get("occurrence", 1)))
            if j0 is None:
                raise ValueError(f"cue {k}: phrase {ow!r} not in line {line!r}")
            j1 = j0 + len(ptoks) - 1
            matched = " ".join(sw[s_src[j0]: s_src[j1] + 1])
        end = c.get("anchor", "start") == "end"
        span = list(range(j1, j0 - 1, -1)) if end else list(range(j0, j1 + 1))
        hit = next((j for j in span if j in s2h), None)
        t, method = tok_time(hit if hit is not None else (j1 if end else j0), end)
        emph = bool(c.get("emphasis", False))
        dur = float(c.get("dur", EMPHASIS_DUR if emph else DEFAULT_DUR))
        dur = min(MAX_DUR, max(MIN_DUR, dur))
        t = max(0.0, min(duration - 0.05, t + float(c.get("offset", DEFAULT_OFFSET))))
        shift = 0.0
        margin = COUNTUP_HOLD if action == "countup" else FIT_MARGIN
        if action == "countup" and t + dur > duration - margin:
            # a number must land on its final value and hold it: shorten, then start earlier,
            # and if the beat is too short show the final value without counting
            dur = max(MIN_DUR, duration - margin - t)
            if t + dur > duration - margin:
                if duration - margin - MIN_DUR >= 0:
                    new_t = duration - margin - MIN_DUR
                    shift, t, dur = round(new_t - t, 3), new_t, MIN_DUR
                else:
                    shift, t, dur = round(-t, 3), 0.0, INSTANT
        elif t + dur > duration - margin:  # finish before the beat cuts away (last words of a line)
            new_t = max(0.0, duration - margin - dur)
            shift, t = round(new_t - t, 3), new_t
        r = Resolved(c["target"], action, t, dur, emph, method, ow, matched,
                     {k2: v for k2, v in c.items() if k2 not in {"on_word", "occurrence", "anchor", "offset", "action",
                                                                 "target", "dur", "emphasis"}})
        out.append(r)
        if shift:
            shifts.append({"cue": k, "on_word": ow, "shift_s": shift})
        if method != "exact":
            problems.append({"cue": k, "on_word": ow, "method": method, "t": round(r.t, 3)})
    report = {"aligned_tokens": len(pairs), "script_tokens": len(s_toks),
              "coverage": round(len(pairs) / max(1, len(s_toks)), 3), "fallbacks": problems, "fit_shifts": shifts,
              "methods": {m: sum(1 for r in out if r.method == m) for m in ("exact", "interpolated", "proportional")}}
    return out, report


def default_duration(line: str, wpm: float = 160.0) -> float:
    """Preview length when no transcript exists: speaking time at ``wpm`` plus lead and tail."""
    n = len(spoken_tokens(line_words(line))[0])
    return round(0.3 + n * 60.0 / wpm + 0.6, 2)


def proportional_words(line: str, duration: float) -> list[dict]:
    """Fake word timings spread evenly (used only to test layouts without audio)."""
    ws = line_words(line)
    a, b = speech_span([], duration)
    step = (b - a) / max(1, len(ws))
    return [{"text": w, "start": a + i * step, "end": a + (i + 0.85) * step} for i, w in enumerate(ws)]


def validate(sheet: dict) -> list[str]:
    """Static checks of a cue sheet (phrases exist in their lines, actions known, targets named)."""
    errs = []
    for b in sheet.get("beats", []):
        try:
            resolve_beat(b["line"], b.get("cues", []), [], float(b.get("default_duration") or default_duration(b["line"])))
        except (ValueError, KeyError) as e:
            errs.append(f"beat {b.get('beat')}: {e}")
    return errs
