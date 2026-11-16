"""Curated lesson memory.

Flow (mirrors feedback/VIDEO_LEARNING_LOOP.md and content_learning_memory in config/brand.yaml):
  creator feedback -> dated record feedback/orchestrator/<date>-<reel>.md (append-only)
                   -> candidate in lesson_candidates.yaml (deduplicated by token similarity)
  candidate seen in 2 independent feedback events, or approved by the creator
                   -> promoted into reel_memory.yaml (compact, capped, with source links)
  over the cap      -> lowest-ranked repeat-promoted lesson moves to lesson_archive.yaml (never lost)

Stages read only the lessons whose ``applies_to`` matches their scope, at most
``max_lessons_per_stage``. config/brand.yaml stays human-curated: ``memory brand-snippet`` prints a
promoted lesson in brand.yaml form for the creator to paste.
"""

from __future__ import annotations

import re
from datetime import date
from pathlib import Path
from typing import Any

import yaml

from . import graph, settings
from .state import now

STOP = set("""a an the and or but if then so to of in on at for with from by is are was were be been it its
this that these those i me my we our you your too very just not no do does did there here as into than
more less can should would could will""".split())


def _cfg() -> dict[str, Any]:
    return settings.load()["memory"]


def _files() -> dict[str, Path]:
    d = settings.paths().memory_dir
    c = _cfg()
    return {"memory": d / Path(c["file"]).name, "candidates": d / Path(c["candidates_file"]).name,
            "archive": d / Path(c["archive_file"]).name, "dir": d}


def _read(path: Path, default: dict[str, Any]) -> dict[str, Any]:
    if path.exists():
        return yaml.safe_load(path.read_text(encoding="utf-8")) or default
    return default


def _write(path: Path, data: dict[str, Any], header: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    tmp.write_text(header + yaml.safe_dump(data, sort_keys=False, allow_unicode=True, width=100),
                   encoding="utf-8")
    tmp.replace(path)


MEMORY_HEADER = ("# Compact reel lesson memory (written by content_os.orchestrator).\n"
                 "# Promoted from creator feedback: repeated in 2 independent feedback events or approved\n"
                 "# by the creator. Capped and de-duplicated; evicted lessons go to lesson_archive.yaml.\n"
                 "# Same fields as content_learning_memory in config/brand.yaml.\n")
CAND_HEADER = "# Candidate lessons from creator feedback (content_os.orchestrator). Not yet applied.\n"
ARCH_HEADER = "# Lessons retired from reel_memory.yaml (cap or creator). Kept for history.\n"


def tokens(text: str) -> set[str]:
    words = re.findall(r"[a-z0-9]+", text.lower())
    return {w[:-1] if w.endswith("s") and len(w) > 3 else w for w in words if w not in STOP and len(w) > 1}


def similarity(a: str, b: str) -> float:
    ta, tb = tokens(a), tokens(b)
    if not ta or not tb:
        return 0.0
    return len(ta & tb) / len(ta | tb)


def load_memory() -> dict[str, Any]:
    return _read(_files()["memory"], {"version": 0, "updated_at": None, "lessons": []})


def load_candidates() -> dict[str, Any]:
    return _read(_files()["candidates"], {"next_id": 1, "candidates": []})


def _clip(rule: str) -> str:
    rule = " ".join(rule.split())
    cap = _cfg()["max_rule_chars"]
    return rule if len(rule) <= cap else rule[: cap - 1].rstrip() + "…"


# --------------------------------------------------------------------------- dated records
def write_record(reel_id: str, feedback_id: str, text: str, classification: dict[str, Any],
                 plan: list[str], invalidated: list[str]) -> Path:
    d = _files()["dir"]
    d.mkdir(parents=True, exist_ok=True)
    path = d / f"{date.today().isoformat()}-{reel_id}.md"
    new = not path.exists()
    lesson = classification.get("lesson") or {}
    with open(path, "a", encoding="utf-8") as fh:
        if new:
            fh.write(f"# Creator feedback: {reel_id} ({date.today().isoformat()})\n\n"
                     "Written by `content_os.orchestrator feedback`; append-only. Format follows "
                     "`feedback/POST_REVIEW_TEMPLATE.md` (before -> after -> why -> evidence).\n")
        fh.write(f"\n## {feedback_id} ({now()})\n\n"
                 f"- **Feedback (verbatim):** {text}\n"
                 f"- **Routed to stage:** `{classification.get('stage')}` "
                 f"(confidence {classification.get('confidence')}, by {classification.get('classified_by')})\n"
                 f"- **Why:** {classification.get('reason')}\n"
                 + (f"- **Timestamp:** {classification['timestamp_s']} s\n" if classification.get("timestamp_s") is not None else "")
                 + (f"- **Beat:** {classification['beat']}\n" if classification.get("beat") is not None else "")
                 + f"- **Invalidated:** {', '.join(invalidated) or 'nothing'}\n"
                 f"- **Re-run plan:** {' -> '.join(plan) or 'none'}\n"
                 f"- **Candidate lesson:** "
                 + (f"[{lesson.get('category')}; applies to {', '.join(lesson.get('applies_to', []))}] {lesson.get('rule')}"
                    if classification.get("generalizable") and lesson.get("rule") else "none (one-off)")
                 + "\n- **After / evidence:** _fill in after the re-run_\n")
    return path


# --------------------------------------------------------------------------- candidates
def add_candidate(lesson: dict[str, Any], *, reel_id: str, feedback_id: str, record: Path) -> dict[str, Any]:
    """Merge into a similar candidate or memory lesson, or add a new one. Returns an outcome dict."""
    rule = _clip(lesson.get("rule", ""))
    if not rule:
        return {"action": "none"}
    thr = _cfg()["dedupe_similarity"]
    src = {"reel": reel_id, "feedback": feedback_id, "record": _rel(record), "at": now()}
    mem = load_memory()
    for les in mem["lessons"]:
        if similarity(les["rule"], rule) >= thr:
            if not any(s.get("feedback") == feedback_id for s in les["sources"]):
                les["sources"].append(src)
                les["sources"] = les["sources"][-6:]
                les["seen"] = les.get("seen", 1) + 1
                _save_memory(mem, f"reinforced {les['id']}")
            return {"action": "reinforced_memory", "id": les["id"]}
    cands = load_candidates()
    for c in cands["candidates"]:
        if c["status"] == "candidate" and similarity(c["rule"], rule) >= thr:
            if not any(s["feedback"] == feedback_id for s in c["sources"]):
                c["sources"].append(src)
                c["count"] = len({(s["reel"], s["feedback"]) for s in c["sources"]})
                c["applies_to"] = sorted(set(c["applies_to"]) | set(lesson.get("applies_to", [])))
            _write(_files()["candidates"], cands, CAND_HEADER)
            if c["count"] >= _cfg()["promote_after_repeats"]:
                promote(c["id"], by="repeat")
                return {"action": "promoted_on_repeat", "id": c["id"]}
            return {"action": "merged", "id": c["id"], "count": c["count"]}
    cid = f"L{cands['next_id']:04d}"
    cands["next_id"] += 1
    cands["candidates"].append({"id": cid, "status": "candidate", "category": lesson.get("category", "content"),
                                "rule": rule, "applies_to": sorted(set(lesson.get("applies_to") or [])),
                                "count": 1, "sources": [src]})
    _write(_files()["candidates"], cands, CAND_HEADER)
    return {"action": "new_candidate", "id": cid}


def promote(cid: str, by: str = "creator") -> dict[str, Any]:
    cands = load_candidates()
    c = next((c for c in cands["candidates"] if c["id"] == cid), None)
    if c is None:
        raise KeyError(f"no candidate {cid}")
    if c["status"] == "promoted":
        return c
    c["status"] = "promoted"
    c["promoted_by"] = by
    _write(_files()["candidates"], cands, CAND_HEADER)
    mem = load_memory()
    lesson = {"id": cid, "category": c["category"], "rule": c["rule"], "applies_to": c["applies_to"],
              "confidence": "high" if by == "creator" else "medium", "promoted_by": by,
              "promoted_at": now(), "seen": c["count"],
              "source": "; ".join(sorted({s["record"] for s in c["sources"]})),
              "sources": c["sources"][-6:]}
    mem["lessons"].append(lesson)
    _save_memory(mem, f"promoted {cid} ({by})")
    return lesson


def reject(cid: str, reason: str = "") -> None:
    cands = load_candidates()
    for c in cands["candidates"]:
        if c["id"] == cid:
            c["status"] = "rejected"
            c["rejected_reason"] = reason
    _write(_files()["candidates"], cands, CAND_HEADER)
    mem = load_memory()
    keep = [l for l in mem["lessons"] if l["id"] != cid]
    if len(keep) != len(mem["lessons"]):
        _archive([l for l in mem["lessons"] if l["id"] == cid], f"retired by creator: {reason}")
        mem["lessons"] = keep
        _save_memory(mem, f"retired {cid}")


def _rank(l: dict[str, Any]) -> tuple:
    return (l.get("promoted_by") == "creator", l.get("seen", 1), l.get("promoted_at") or "")


def _save_memory(mem: dict[str, Any], why: str) -> None:
    cap = _cfg()["max_lessons"]
    if len(mem["lessons"]) > cap:
        ranked = sorted(mem["lessons"], key=_rank, reverse=True)
        keep, drop = ranked[:cap], ranked[cap:]
        _archive(drop, "evicted: memory cap")
        ids = {l["id"] for l in keep}
        mem["lessons"] = [l for l in mem["lessons"] if l["id"] in ids]
    mem["version"] = int(mem.get("version", 0)) + 1
    mem["updated_at"] = now()
    mem["last_change"] = why
    _write(_files()["memory"], mem, MEMORY_HEADER)


def _archive(lessons: list[dict[str, Any]], reason: str) -> None:
    if not lessons:
        return
    arch = _read(_files()["archive"], {"lessons": []})
    for l in lessons:
        arch["lessons"].append({**l, "archived_at": now(), "archived_reason": reason})
    _write(_files()["archive"], arch, ARCH_HEADER)


# --------------------------------------------------------------------------- reading
def lessons_for(stage: str, context: str = "", limit: int | None = None) -> list[dict[str, Any]]:
    scope = graph.lesson_scope(stage)
    limit = limit or _cfg()["max_lessons_per_stage"]
    rel = [l for l in load_memory()["lessons"] if scope in l.get("applies_to", []) or stage in l.get("applies_to", [])]
    ctx = tokens(context)
    rel.sort(key=lambda l: (_rank(l), len(tokens(l["rule"]) & ctx)), reverse=True)
    return rel[:limit]


BRAND_CATEGORIES = {"brief": {"content", "brand"}, "script": {"content", "brand"},
                    "post_package": {"content", "brand"}, "visuals": {"visual"},
                    "edit": {"technical", "process"}, "render": {"technical"}}


def brand_lessons_for(stage: str, context: str, limit: int = 6) -> list[dict[str, Any]]:
    """The most relevant human-approved lessons from config/brand.yaml for this stage."""
    from content_os.config import load_brand

    cats = BRAND_CATEGORIES.get(graph.lesson_scope(stage), set())
    ctx = tokens(context)
    items = [l.model_dump() for l in load_brand().content_learning_memory if l.category in cats]
    items.sort(key=lambda l: len(tokens(l["rule"]) & ctx), reverse=True)
    return items[:limit]


def prompt_block(stage: str, context: str = "") -> tuple[str, list[str]]:
    """Compact text block for a stage prompt + the lesson ids used (for provenance)."""
    lines, ids = [], []
    for l in lessons_for(stage, context):
        lines.append(f"- [{l['category']}; {l['confidence']}] {l['rule']} (lesson {l['id']})")
        ids.append(l["id"])
    for l in brand_lessons_for(stage, context):
        lines.append(f"- [{l['category']}; {l['confidence']}] {' '.join(l['rule'].split())} (brand.yaml)")
    if not lines:
        return "", ids
    return "APPROVED LESSONS FOR THIS STAGE (apply them):\n" + "\n".join(lines), ids


def _rel(p: Path) -> str:
    try:
        return str(p.resolve().relative_to(settings.PROJECT_ROOT))
    except ValueError:
        return settings.tilde(p)
