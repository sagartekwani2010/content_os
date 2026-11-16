"""The reel stage graph: idea -> ... -> performance.

Kinds:
  auto      deterministic step run by the orchestrator (no model)
  model     one structured Claude call through content_os.llm_runtime (model from config)
  pipeline  delegated to ``python -m content_os.pipeline`` on the reel's media dir
  external  optional external service (OpenAI av_review); never blocks the creator gate
  creator   something only the creator can do (record, report performance); recorded with ``approve``
  gate      a creator approval of the exact current version of the stage it approves

The graph is a chain (each node depends on its predecessor), plus extra data dependencies listed in
``inputs`` that are hashed into provenance. Downstream of X = every node after X.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Node:
    name: str
    kind: str
    title: str
    inputs: tuple[str, ...] = ()       # extra data deps beyond the predecessor
    gate: str | None = None            # for gate/creator nodes: the name used in `approve <reel> <gate>`
    approves: str | None = None        # for gate nodes: the stage whose version is approved
    pipeline: tuple[str, ...] = field(default=())  # pipeline stages run for this node
    lessons: bool = False              # loads relevant lessons from memory


NODES: tuple[Node, ...] = (
    Node("idea", "auto", "Idea captured"),
    Node("brief", "model", "Brief", lessons=True),
    Node("gate:brief", "gate", "Creator approves brief", gate="brief", approves="brief"),
    Node("script", "model", "Script + beat sheet", inputs=("brief",), lessons=True),
    Node("gate:script", "gate", "Creator approves script", gate="script", approves="script"),
    Node("shoot_plan", "auto", "Shoot plan + teleprompter", inputs=("script",)),
    Node("record", "creator", "Creator records the beats", gate="recorded", inputs=("shoot_plan",)),
    Node("ingest", "pipeline", "Ingest footage", inputs=("script", "record"), pipeline=("ingest",)),
    Node("transcribe", "pipeline", "Transcribe", pipeline=("transcribe",)),
    Node("segment", "pipeline", "Match takes to beats", inputs=("script",), pipeline=("segment",)),
    Node("score", "pipeline", "Score + select takes", pipeline=("score", "judge_takes"), lessons=True),
    Node("cutpoints", "pipeline", "Cut points", pipeline=("cutpoints",), lessons=True),
    Node("cut_review", "pipeline", "Cut review page", pipeline=("cut_review", "judge_cuts")),
    Node("gate:cut_review", "gate", "Creator approves cuts", gate="cut_review", approves="cut_review"),
    Node("draft_render", "pipeline", "Draft render + draft QA", pipeline=("render:draft", "qa:draft")),
    Node("visuals", "auto", "Visuals (content_os.visuals)", inputs=("script",), lessons=True),
    Node("render", "pipeline", "Final render + master", inputs=("visuals",), pipeline=("render",), lessons=True),
    Node("qa", "pipeline", "Measured QA", pipeline=("qa",)),
    Node("av_review", "external", "Audio/video review (OpenAI)", inputs=("render",)),
    Node("gate:final_listen", "gate", "Creator listens to the final file", gate="final_listen",
         approves="render"),
    Node("post_package", "model", "Caption + cover", inputs=("script", "render"), lessons=True),
    Node("gate:posting", "gate", "Creator posts (Content OS never posts)", gate="posting",
         approves="post_package"),
    Node("performance", "creator", "Performance + feedback record", gate="performance"),
)

ORDER: tuple[str, ...] = tuple(n.name for n in NODES)
BY_NAME: dict[str, Node] = {n.name: n for n in NODES}
GATE_NODES: dict[str, str] = {n.gate: n.name for n in NODES if n.gate}
CREATOR_GATES = ("brief", "script", "cut_review", "final_listen", "posting")

# Stages feedback may be routed to (the classifier's label set), earliest first.
FEEDBACK_TARGETS = ("brief", "script", "shoot_plan", "record", "score", "cutpoints", "visuals",
                    "render", "post_package")


def node(name: str) -> Node:
    if name not in BY_NAME:
        raise KeyError(f"unknown stage {name!r}; known: {', '.join(ORDER)}")
    return BY_NAME[name]


def index(name: str) -> int:
    return ORDER.index(name)


def deps(name: str) -> tuple[str, ...]:
    """Predecessor plus declared data inputs (deduplicated, in graph order)."""
    i = index(name)
    out = ([ORDER[i - 1]] if i else []) + list(node(name).inputs)
    return tuple(sorted(set(out), key=index))


def downstream(name: str, include_self: bool = True) -> tuple[str, ...]:
    i = index(name)
    return ORDER[i if include_self else i + 1:]


def lesson_scope(name: str) -> str:
    """Which lesson bucket a stage reads."""
    if name in ("brief", "script", "shoot_plan", "post_package"):
        return name
    if name in ("score", "cutpoints", "cut_review", "record"):
        return "edit"
    if name in ("visuals",):
        return "visuals"
    if name in ("render", "qa", "draft_render", "av_review"):
        return "render"
    return name
