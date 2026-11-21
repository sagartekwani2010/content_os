"""pipeline_steps jobs: only the project's own pipeline/visuals commands, never a creator gate."""

import pytest

from content_os.orchestrator import jobs


def test_allowed_steps_validate():
    steps = [["content_os.visuals", "render", "/x/reel"], ["content_os.pipeline", "render", "/x/reel"]]
    assert jobs.validate_steps(steps) == steps


@pytest.mark.parametrize("steps", [
    [],
    None,
    [["bash", "-c", "rm -rf /"]],
    [["content_os.pipeline"]],
    [["content_os.orchestrator", "run", "reel"]],
    [["content_os.pipeline", "approve", "/x/reel", "cut_review", "--by", "me"]],
    [["content_os.pipeline", 3]],
])
def test_rejected_steps(steps):
    with pytest.raises(ValueError):
        jobs.validate_steps(steps)


def test_enqueue_rejects_bad_steps(tmp_path, monkeypatch):
    from content_os.orchestrator import settings

    real = settings.paths()
    monkeypatch.setattr(settings, "paths", lambda: real.__class__(**{**real.__dict__, "queue_db": tmp_path / "q.sqlite"})
                        if hasattr(real, "__dict__") else real)
    with pytest.raises(ValueError):
        jobs.enqueue("pipeline_steps", "reel", {"steps": [["sh", "-c", "echo"]]})
