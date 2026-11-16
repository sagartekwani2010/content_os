"""Recorded approvals. An approval is tied to the sha256 of the file it approves, so changing the cuts
after approval invalidates it."""

from __future__ import annotations

from datetime import datetime, timezone

from .reel import Reel, StageError, read_json, write_json

GATES = {"cut_review": "cuts_file"}


def approve(reel: Reel, gate: str, by: str, note: str = "") -> dict:
    if gate not in GATES:
        raise StageError(f"unknown gate {gate}; known: {sorted(GATES)}")
    target = reel.need(getattr(reel, GATES[gate]), gate)
    if gate == "cut_review" and not reel.review_html.exists():
        raise StageError("cut_review.html has not been generated; run `cut_review` and look at it first")
    data = read_json(reel.approvals_file) if reel.approvals_file.exists() else {}
    record = {"sha256": target["sha256"], "by": by, "note": note,
              "approved_at": datetime.now(timezone.utc).isoformat(timespec="seconds")}
    judge = reel.work / "judge_cuts.json"
    if judge.exists():
        rej = read_json(judge).get("result", {}).get("reject_cuts", [])
        record["judge_rejections_seen"] = len(rej)
    data[gate] = record
    write_json(reel.approvals_file, data)
    return record


def require_approval(reel: Reel, gate: str, sha256: str) -> None:
    data = read_json(reel.approvals_file) if reel.approvals_file.exists() else {}
    rec = data.get(gate)
    if not rec:
        raise StageError(f"no recorded {gate} approval: open work/cut_review.html, then run "
                         f"`python -m content_os.pipeline approve <reel_dir> {gate} --by <name>`")
    if rec["sha256"] != sha256:
        raise StageError(f"{gate} approval is for an older version (cuts changed after approval); review again")
