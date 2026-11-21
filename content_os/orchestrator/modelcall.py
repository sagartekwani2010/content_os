"""One structured Claude call per model stage, through content_os.llm_runtime.

Model, effort and prompt version come from config/models.yaml (agent keys in
config/orchestrator.yaml); the returned provenance records all three plus prompt and config hashes.
Tests replace ``CALLER`` with a fake; nothing here hardcodes a model.
"""

from __future__ import annotations

import asyncio
import time
from typing import Any, Callable

from pydantic import BaseModel, Field

from content_os.config import load_models_config, load_prompt

from . import settings
from .state import sha256_bytes, sha256_json


# --------------------------------------------------------------------------- output contracts
class BriefOut(BaseModel):
    topic: str
    core_thesis: str
    learning_objective: str
    format: str
    brand_pillar: str
    sections: list[str]
    audience: str
    promise: str
    takeaway: str
    target_duration_s: int = 75
    open_questions: list[str] = Field(default_factory=list)


class BeatOut(BaseModel):
    id: int
    text: str
    section: str
    visual: str
    emotion: str = Field(default="", description="what the viewer should feel at this beat")
    delivery: str = Field(default="", description="face/voice cue for the creator that produces the emotion")
    continuity: str = Field(default="", description="start/end pose and energy; how the cut into this beat is hidden")


class HookVariant(BaseModel):
    text: str
    emotion: str
    on_screen_text: str
    first_frame: str


class ScriptOut(BaseModel):
    title: str
    promise: str
    hook: str
    target_duration_s: int
    beats: list[BeatOut]
    emotional_arc: str = ""
    hook_variants: list[HookVariant] = Field(default_factory=list)
    save_asset: str = ""
    comment_trigger: str = ""
    caption_notes: list[str] = Field(default_factory=list)
    open_questions: list[str] = Field(default_factory=list)


class Keyframe(BaseModel):
    id: str = Field(description="KF01, KF02, ...")
    time_s: float
    beats: list[int] = Field(default_factory=list, description="script beat ids this frame belongs to")
    emotion: str
    layout: str = Field(description="split (visual top, creator bottom) | full_visual | full_creator | screen_recording | broll | card")
    shot: str = Field(description="what the camera or screen recording shows; framing, angle, punch-in")
    top_visual: str = Field(default="", description="hand-drawn diagram / demo screen: what is drawn and how it moves")
    template: str = Field(default="", description="content_os.visuals template to use, when one fits")
    on_screen_text: str = ""
    motion: str = ""
    transition_in: str = ""
    sfx: str = ""
    music: str = ""
    creator_direction: str = Field(default="", description="expression, gesture, pose for the creator in this frame")


class MoodboardOut(BaseModel):
    concept: str = Field(description="one-line visual concept of the reel")
    palette: list[str] = Field(description="hex colours with roles, e.g. '#FFD23F accent: numbers'")
    typography: str
    texture: str = Field(description="line style, paper, glow, grain")
    music: str
    sfx_palette: list[str]
    pacing: str
    references: list[str] = Field(default_factory=list, description="described visual references (no copyrighted assets)")
    keyframes: list[Keyframe]
    shot_list: list[str] = Field(description="everything to film or screen-record besides the talking beats, in shooting order")
    risks: list[str] = Field(default_factory=list)


class BeatCheck(BaseModel):
    beat: int
    intended: str
    likely_felt: str
    issue: str = ""
    fix: str = ""
    blocking: bool = False


class CheckScores(BaseModel):
    hook: int
    emotional_arc: int
    clarity: int
    retention: int
    sends: int
    saves: int
    comments: int
    continuity: int


class StoryCheckOut(BaseModel):
    phase: str = Field(description="script | visuals")
    verdict: str = Field(description="pass | revise")
    scores: CheckScores
    beats: list[BeatCheck]
    hook_ranking: list[str] = Field(default_factory=list, description="hook variants best first, each with why")
    likely_drop_offs: list[str] = Field(default_factory=list)
    top_fixes: list[str] = Field(default_factory=list)


class PostOut(BaseModel):
    caption: str
    hashtags: list[str]
    cover_text: str
    cover_beat: int


class LessonOut(BaseModel):
    category: str = Field(description="content | visual | edit | audio | process")
    rule: str
    applies_to: list[str]


class FeedbackOut(BaseModel):
    stage: str
    timestamp_s: float | None = None
    beat: int | None = None
    reason: str
    confidence: str = Field(description="high | medium | low")
    generalizable: bool
    lesson: LessonOut


class HeartbeatOut(BaseModel):
    ok: bool
    nonce: str


def agent_key(role: str) -> str:
    return settings.load()["agents"][role]


def resolved(role: str) -> dict[str, Any]:
    key = agent_key(role)
    cfg = load_models_config().resolved(key)
    prompt = load_prompt(cfg.prompt_version)
    return {"agent": key, "model": cfg.model, "prompt_version": cfg.prompt_version,
            "effort": cfg.reasoning_effort, "max_turns": cfg.max_turns, "max_tokens": cfg.max_tokens,
            "server_fallbacks": cfg.server_fallbacks, "system": prompt,
            "prompt_sha": sha256_bytes(prompt.encode())[:12],
            "config_hash": sha256_json(cfg.model_dump())}


def _default_caller(role: str, prompt: str, output_type: type[BaseModel]) -> tuple[Any, dict[str, Any]]:
    from content_os.llm_runtime import StageRequest, get_backend, select_backend_name

    r = resolved(role)
    req = StageRequest(model=r["model"], system=r["system"], prompt=prompt, output_type=output_type,
                       effort=r["effort"], max_tokens=r["max_tokens"], max_turns=r["max_turns"],
                       server_fallbacks=r["server_fallbacks"])
    backend = get_backend()
    t0 = time.time()
    resp = asyncio.run(backend.run(req))
    out = resp.output
    if isinstance(out, BaseModel):
        out = out.model_dump()
    meta = {"backend": select_backend_name(), "served_model": resp.served_model,
            "trace_id": resp.trace_id, "input_tokens": resp.input_tokens,
            "output_tokens": resp.output_tokens, "cost_usd": resp.reported_cost_usd,
            "seconds": round(time.time() - t0, 1)}
    return out, meta


# Replaced in tests: (role, prompt, output_type) -> (dict, meta)
CALLER: Callable[[str, str, type[BaseModel]], tuple[Any, dict[str, Any]]] = _default_caller


def call(role: str, prompt: str, output_type: type[BaseModel]) -> tuple[BaseModel, dict[str, Any]]:
    r = resolved(role)
    raw, meta = CALLER(role, prompt, output_type)
    out = output_type.model_validate(raw)
    provenance = {"agent": r["agent"], "model": r["model"], "prompt_version": r["prompt_version"],
                  "prompt_sha": r["prompt_sha"], "effort": r["effort"],
                  "config_hash": r["config_hash"], "prompt_input_sha": sha256_bytes(prompt.encode())[:12],
                  **meta}
    return out, provenance
