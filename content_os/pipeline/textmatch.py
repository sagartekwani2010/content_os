"""Word normalisation, spoken "beat N" cue parsing, fuzzy order-constrained alignment and WER."""

from __future__ import annotations

import re
from difflib import SequenceMatcher

_NUM_WORDS = {
    "zero": 0, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8,
    "nine": 9, "ten": 10, "eleven": 11, "twelve": 12, "thirteen": 13, "fourteen": 14, "fifteen": 15,
    "sixteen": 16, "seventeen": 17, "eighteen": 18, "nineteen": 19, "twenty": 20,
    "first": 1, "second": 2, "third": 3, "fourth": 4, "fifth": 5, "sixth": 6, "seventh": 7, "eighth": 8,
    "ninth": 9, "tenth": 10,
}
# ASR homophones that only count as numbers right after a cue word
_CUE_HOMOPHONES = {"won": 1, "to": 2, "too": 2, "tu": 2, "tree": 3, "free": 3, "for": 4, "fore": 4, "fo": 4,
                   "ate": 8, "sics": 6, "sex": 6, "nein": 9, "tin": 10, "then": 10}
CUE_WORDS = {"beat", "beats", "beet", "beets", "bit", "bits", "beep", "bead", "b", "bee", "be", "beat's", "pete",
             "meet", "peat"}
CUE_FILLERS = {"number", "no", "num", "nr", "#"}
FILLERS = {"um", "umm", "uh", "uhh", "uhm", "er", "erm", "ah", "ahh", "hmm", "mm", "mhm", "eh"}

_PUNCT = re.compile(r"[^\w'%#]+")


def norm(word: str) -> str:
    w = word.lower().replace("’", "'").strip()
    w = _PUNCT.sub("", w)
    return w.strip("'")


def tokens(text: str) -> list[str]:
    out = []
    for raw in re.split(r"[\s—–/-]+", text):
        t = norm(raw)
        if t:
            out.append(t)
    return out


def number_value(tok: str, allow_homophones: bool = False) -> int | None:
    if tok.isdigit():
        return int(tok)
    m = re.fullmatch(r"(\d+)(st|nd|rd|th)", tok)
    if m:
        return int(m.group(1))
    if tok in _NUM_WORDS:
        return _NUM_WORDS[tok]
    if allow_homophones and tok in _CUE_HOMOPHONES:
        return _CUE_HOMOPHONES[tok]
    return None


def parse_cue(toks: list[str], i: int, max_beat: int) -> tuple[int, int] | None:
    """If a cue starts at toks[i], return (beat number, number of tokens consumed)."""
    t = toks[i]
    m = re.fullmatch(r"(?:beat|bit|b|beet)#?(\d+)", t)
    if m:
        n = int(m.group(1))
        return (n, 1) if 1 <= n <= max_beat else None
    if t not in CUE_WORDS:
        return None
    j = i + 1
    while j < len(toks) and toks[j] in CUE_FILLERS and j - i <= 2:
        j += 1
    if j >= len(toks):
        return None
    n = number_value(toks[j], allow_homophones=True)
    used = j - i + 1
    # "twenty one"
    if n == 20 and j + 1 < len(toks):
        extra = number_value(toks[j + 1])
        if extra is not None and 1 <= extra <= 9:
            n, used = 20 + extra, used + 1
    if n is None or not (1 <= n <= max_beat):
        return None
    if t in ("b", "be", "bee", "meet", "pete", "peat") and toks[j] not in _NUM_WORDS and not toks[j].isdigit():
        return None  # weak cue word + homophone number is too ambiguous
    return n, used


def canon(tok: str) -> str:
    v = number_value(tok)
    return str(v) if v is not None else tok


def tok_sim(a: str, b: str) -> float:
    a, b = canon(a), canon(b)
    if a == b:
        return 1.0
    return SequenceMatcher(None, a, b).ratio()


def align(hyp: list[str], ref: list[str], min_sim: float = 0.8) -> list[tuple[int, int]]:
    """Order-constrained fuzzy alignment (LCS where tokens match if similarity >= min_sim).

    Returns matched (hyp_index, ref_index) pairs in order.
    """
    n, m = len(hyp), len(ref)
    if n == 0 or m == 0:
        return []
    match = [[tok_sim(hyp[i], ref[j]) >= min_sim for j in range(m)] for i in range(n)]
    dp = [[0] * (m + 1) for _ in range(n + 1)]
    for i in range(n - 1, -1, -1):
        for j in range(m - 1, -1, -1):
            if match[i][j]:
                dp[i][j] = 1 + dp[i + 1][j + 1]
            else:
                dp[i][j] = max(dp[i + 1][j], dp[i][j + 1])
    pairs, i, j = [], 0, 0
    while i < n and j < m:
        if match[i][j] and dp[i][j] == 1 + dp[i + 1][j + 1]:
            pairs.append((i, j))
            i += 1
            j += 1
        elif dp[i + 1][j] >= dp[i][j + 1]:
            i += 1
        else:
            j += 1
    return pairs


def coverage(hyp: list[str], ref: list[str], min_sim: float = 0.8) -> dict:
    pairs = align(hyp, ref, min_sim)
    matched_ref = {j for _, j in pairs}
    m = len(ref)
    head = set(range(min(2, m)))
    tail = set(range(max(0, m - 2), m))
    return {
        "completeness": round(len(pairs) / m, 3) if m else 0.0,
        "precision": round(len(pairs) / len(hyp), 3) if hyp else 0.0,
        "covers_start": bool(matched_ref & head),
        "covers_end": bool(matched_ref & tail),
        "first_ref": pairs[0][1] if pairs else None,
        "last_ref": pairs[-1][1] if pairs else None,
        "pairs": pairs,
        "text_similarity": round(SequenceMatcher(None, " ".join(map(canon, hyp)), " ".join(map(canon, ref))).ratio(), 3),
    }


def similarity(hyp: list[str], ref: list[str], min_sim: float = 0.8) -> float:
    """Symmetric score in [0,1] used for beat assignment (F1 of fuzzy alignment)."""
    if not hyp or not ref:
        return 0.0
    k = len(align(hyp, ref, min_sim))
    p, r = k / len(hyp), k / len(ref)
    return 0.0 if k == 0 else round(2 * p * r / (p + r), 3)


def wer(hyp: list[str], ref: list[str]) -> float:
    hyp = [canon(t) for t in hyp]
    ref = [canon(t) for t in ref]
    n, m = len(hyp), len(ref)
    if m == 0:
        return 0.0 if n == 0 else 1.0
    prev = list(range(m + 1))
    for i in range(1, n + 1):
        cur = [i] + [0] * m
        for j in range(1, m + 1):
            cur[j] = min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (hyp[i - 1] != ref[j - 1]))
        prev = cur
    return round(prev[m] / m, 3)


def repeated_ngrams(hyp: list[str], ref: list[str], n: int = 2) -> list[str]:
    """n-grams said more often than the script contains them (restart / stutter evidence)."""
    def grams(seq):
        out: dict[tuple, int] = {}
        for i in range(len(seq) - n + 1):
            g = tuple(canon(t) for t in seq[i: i + n])
            out[g] = out.get(g, 0) + 1
        return out
    h, r = grams(hyp), grams(ref)
    return [" ".join(g) for g, c in h.items() if c > r.get(g, 0) and c > 1]
