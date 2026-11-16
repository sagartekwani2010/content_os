"""Stage 3, segment: spoken "beat N" cues -> beat regions -> repeated attempts (takes).

Rules (all deterministic):
- A cue is a cue word (beat / bit / beet / B ...) + optional "number" + a number word, digit or ASR
  homophone (for->4, to->2, won->1, tree->3), accepted only when it stands apart from speech:
  a pause before it (or start of file / sentence end) and a pause or sentence end after it.
- A beat region runs from the end of its cue to the next cue (or the end of the file). Speech
  before the first cue, or in a file without cues, is assigned to beats by text similarity.
- Inside a region, speech is cut into pieces at pauses >= ``attempt_gap_s``. A piece opens a new
  attempt when the pause is >= ``hard_gap_s`` or when it goes back in the script (its first
  matched script word is not after the words already said). A restart without a pause is found
  where the opening words of the line are said again mid-attempt; the attempt is split there.
- Completeness = fuzzy, order-constrained word coverage of the beat line (LCS); complete when
  coverage >= ``complete_threshold`` and both the start and the end of the line are covered.
"""

from __future__ import annotations

import re

from . import textmatch as tm
from .reel import Reel, load_beats, schema, write_json

_SENT_END = re.compile(r"[.?!,:;]$")


def _flat_tokens(words: list[dict]) -> list[tuple[str, int]]:
    out = []
    for wi, w in enumerate(words):
        for t in tm.tokens(w["text"]):
            out.append((t, wi))
    return out


def find_cues(words: list[dict], max_beat: int, scfg: dict) -> list[dict]:
    toks = _flat_tokens(words)
    names = [t for t, _ in toks]
    cues = []
    i = 0
    while i < len(toks):
        parsed = tm.parse_cue(names, i, max_beat)
        if not parsed:
            i += 1
            continue
        beat, used = parsed
        w0 = toks[i][1]
        w1 = toks[i + used - 1][1]
        pre_ok = (w0 == 0 or words[w0]["start"] - words[w0 - 1]["end"] >= scfg["cue_min_pre_gap_s"]
                  or bool(_SENT_END.search(words[w0 - 1]["text"])))
        post_ok = (w1 == len(words) - 1 or words[w1 + 1]["start"] - words[w1]["end"] >= scfg["cue_min_post_gap_s"]
                   or bool(_SENT_END.search(words[w1]["text"])))
        if pre_ok and post_ok:
            cues.append({"beat": beat, "word_start": w0, "word_end": w1, "start": words[w0]["start"],
                         "end": words[w1]["end"], "heard": " ".join(w["text"] for w in words[w0: w1 + 1])})
            i += used
        else:
            i += 1
    return cues


def _pieces(idx: list[int], words: list[dict], gap: float) -> list[list[int]]:
    pieces: list[list[int]] = []
    for wi in idx:
        if pieces and words[wi]["start"] - words[pieces[-1][-1]]["end"] < gap:
            pieces[-1].append(wi)
        else:
            pieces.append([wi])
    return pieces


def _toks(words: list[dict], idx: list[int]) -> list[str]:
    return [t for wi in idx for t in tm.tokens(words[wi]["text"])]


def _best_beat(tokens: list[str], beats: list[dict], thr: float) -> tuple[int | None, float]:
    best, score = None, 0.0
    for b in beats:
        s = tm.similarity(tokens, b["tokens"], thr)
        if s > score:
            best, score = b["id"], s
    return best, score


def _group_attempts(pieces: list[list[int]], words: list[dict], ref: list[str], scfg: dict) -> list[list[int]]:
    thr = scfg["token_similarity"]
    attempts: list[list[int]] = []
    last_ref = -1
    for piece in pieces:
        cov = tm.coverage(_toks(words, piece), ref, thr)
        new = not attempts
        if attempts:
            gap = words[piece[0]]["start"] - words[attempts[-1][-1]]["end"]
            if gap >= scfg["hard_gap_s"]:
                new = True
            elif cov["first_ref"] is not None and last_ref >= 0 and cov["first_ref"] <= max(0, last_ref - 1):
                new = True
        if new:
            attempts.append(list(piece))
            last_ref = cov["last_ref"] if cov["last_ref"] is not None else -1
        else:
            attempts[-1].extend(piece)
            if cov["last_ref"] is not None:
                # continue in script coordinates after what was already said
                cov2 = tm.coverage(_toks(words, attempts[-1]), ref, thr)
                last_ref = cov2["last_ref"] if cov2["last_ref"] is not None else last_ref
    return attempts


def _split_restarts(attempt: list[int], words: list[dict], ref: list[str], thr: float) -> list[list[int]]:
    """Split where the line's opening words are said again inside one attempt (no pause)."""
    if len(ref) < 2:
        return [attempt]
    flat = [(t, wi) for wi in attempt for t in tm.tokens(words[wi]["text"])]
    k = min(3, len(ref))
    cuts = []
    for p in range(1, len(flat) - 1):
        if all(p + q < len(flat) and tm.tok_sim(flat[p + q][0], ref[q]) >= thr for q in range(min(k, 2))):
            before = [t for t, _ in flat[:p]]
            cov = tm.coverage(before, ref, thr)
            if cov["first_ref"] is not None and cov["first_ref"] <= 1:
                wi = flat[p][1]
                if wi != attempt[0] and wi not in cuts:
                    cuts.append(wi)
    if not cuts:
        return [attempt]
    parts, cur = [], []
    for wi in attempt:
        if wi in cuts and cur:
            parts.append(cur)
            cur = []
        cur.append(wi)
    parts.append(cur)
    return parts


def _take_record(words: list[dict], idx: list[int], beat: dict, beats: list[dict], scfg: dict, source: str,
                 restarted_after: bool) -> dict:
    thr = scfg["token_similarity"]
    toks = _toks(words, idx)
    ref = beat["tokens"]
    cov = tm.coverage(toks, ref, thr)
    fillers = [t for t in toks if t in tm.FILLERS and t not in ref]
    stutters = [toks[i] for i in range(1, len(toks)) if toks[i] == toks[i - 1] and
                not any(ref[j] == ref[j - 1] == toks[i] for j in range(1, len(ref)))]
    repeats = tm.repeated_ngrams(toks, ref, 2)
    pauses = []
    for a, b in zip(idx, idx[1:]):
        g = words[b]["start"] - words[a]["end"]
        if g >= 0.35:
            pauses.append({"after_word": words[a]["text"], "gap_s": round(g, 2)})
    best, best_s = _best_beat(toks, beats, thr)
    cue_s = tm.similarity(toks, ref, thr)
    flags = []
    complete = (cov["completeness"] >= scfg["complete_threshold"] and cov["covers_start"] and cov["covers_end"])
    if not complete:
        flags.append("incomplete")
    if restarted_after:
        flags.append("abandoned_restart")
    if repeats:
        flags.append("internal_repeat")
    if stutters:
        flags.append("stutter")
    if fillers:
        flags.append("fillers")
    if best is not None and best != beat["id"] and best_s - cue_s >= scfg["beat_mismatch_margin"]:
        flags.append(f"beat_mismatch:{best}")
    return {
        "beat": beat["id"], "source": source,
        "start": words[idx[0]]["start"], "end": words[idx[-1]]["end"],
        "duration": round(words[idx[-1]]["end"] - words[idx[0]]["start"], 3),
        "word_range": [idx[0], idx[-1]],
        "words": [{"text": words[i]["text"], "start": words[i]["start"], "end": words[i]["end"]} for i in idx],
        "text": " ".join(words[i]["text"] for i in idx),
        "completeness": cov["completeness"], "precision": cov["precision"],
        "covers_start": cov["covers_start"], "covers_end": cov["covers_end"],
        "text_similarity": cov["text_similarity"], "complete": complete,
        "restart": bool(restarted_after or repeats), "repeated_ngrams": repeats,
        "fillers": len(fillers) + len(stutters), "filler_words": fillers + stutters,
        "internal_pauses": pauses, "best_beat": best, "best_beat_similarity": best_s,
        "flags": flags,
    }


def segment_source(source: str, words: list[dict], beats: list[dict], scfg: dict) -> tuple[list[dict], list[dict], list[dict]]:
    by_id = {b["id"]: b for b in beats}
    thr = scfg["token_similarity"]
    cues = find_cues(words, max(by_id), scfg)
    cue_words = {wi for c in cues for wi in range(c["word_start"], c["word_end"] + 1)}
    regions: list[tuple[int | None, list[int]]] = []
    bounds = [(None, 0)] + [(c["beat"], c["word_end"] + 1) for c in cues]
    for k, (beat, begin) in enumerate(bounds):
        end = cues[k]["word_start"] if k < len(cues) else len(words)
        idx = [i for i in range(begin, end) if i not in cue_words]
        if idx:
            regions.append((beat, idx))
    takes, unassigned = [], []
    for beat_id, idx in regions:
        pieces = _pieces(idx, words, scfg["attempt_gap_s"])
        if beat_id is None:
            # no cue: assign each piece by similarity, then group consecutive same-beat pieces
            labelled = []
            for pc in pieces:
                b, s = _best_beat(_toks(words, pc), beats, thr)
                if b is None or s < scfg["fallback_min_similarity"] * 0.5:
                    unassigned.append({"source": source, "start": words[pc[0]]["start"], "end": words[pc[-1]]["end"],
                                       "text": " ".join(words[i]["text"] for i in pc)})
                    continue
                labelled.append((b, pc))
            groups: list[tuple[int, list[list[int]]]] = []
            for b, pc in labelled:
                if groups and groups[-1][0] == b:
                    groups[-1][1].append(pc)
                else:
                    groups.append((b, [pc]))
            work = [(b, pcs, "similarity") for b, pcs in groups]
        else:
            work = [(beat_id, pieces, "cue")]
        for b, pcs, how in work:
            beat = by_id[b]
            for att in _group_attempts(pcs, words, beat["tokens"], scfg):
                parts = _split_restarts(att, words, beat["tokens"], thr)
                for pi, part in enumerate(parts):
                    rec = _take_record(words, part, beat, beats, scfg, source, restarted_after=pi < len(parts) - 1)
                    rec["assigned_by"] = how
                    if how == "similarity" and rec["best_beat_similarity"] < scfg["fallback_min_similarity"]:
                        rec["flags"].append("weak_beat_match")
                    takes.append(rec)
    return takes, [dict(c, source=source) for c in cues], unassigned


def run(reel: Reel, cfg: dict) -> dict:
    transcript = reel.need(reel.transcript_file, "transcribe")
    sources = reel.need(reel.sources_file, "ingest")["sources"]
    beats = load_beats(reel)
    for b in beats:
        b["tokens"] = tm.tokens(b["text"])
    scfg = cfg["segment"]
    all_takes, all_cues, unassigned = [], [], []
    for s in sources:
        words = transcript["sources"][s["id"]]["words"]
        t, c, u = segment_source(s["id"], words, beats, scfg)
        all_takes += t
        all_cues += c
        unassigned += u
    order = {s["id"]: i for i, s in enumerate(sources)}
    all_takes.sort(key=lambda t: (t["beat"], order[t["source"]], t["start"]))
    counters: dict[int, int] = {}
    for t in all_takes:
        counters[t["beat"]] = counters.get(t["beat"], 0) + 1
        t["id"] = f"b{t['beat']}_t{counters[t['beat']]}"
        t["attempt"] = counters[t["beat"]]
    takes = [{"id": t.pop("id"), **t} for t in all_takes]
    summary = []
    for b in beats:
        bt = [t for t in takes if t["beat"] == b["id"]]
        summary.append({"beat": b["id"], "takes": len(bt), "complete": sum(t["complete"] for t in bt),
                        "cues_heard": sum(1 for c in all_cues if c["beat"] == b["id"])})
    data = {"schema": schema("takes"), "beats": [{"id": b["id"], "text": b["text"]} for b in beats],
            "cues": all_cues, "takes": takes, "unassigned": unassigned, "summary": summary,
            "missing_beats": [s["beat"] for s in summary if s["complete"] == 0]}
    write_json(reel.takes_file, data)
    return data
