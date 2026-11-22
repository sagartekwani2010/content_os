import ast
import json
from pathlib import Path

from content_os.carousel_eval import checks
from content_os.carousel_eval.contract import CONTRACT, load

PKG = Path(__file__).resolve().parents[2] / "content_os" / "carousel_eval"


def test_isolated_from_production_code():
    """The evaluator must not import any other content_os module (Codex owns content_os.carousel)."""
    for f in PKG.glob("*.py"):
        for node in ast.walk(ast.parse(f.read_text())):
            if isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
                assert not node.module.startswith("content_os"), f"{f.name} imports {node.module}"
            if isinstance(node, ast.Import):
                for n in node.names:
                    assert not n.name.startswith("content_os"), f"{f.name} imports {n.name}"


def test_fragments_and_norm():
    assert checks.fragments('"Paneer, 100 g: 265 kcal… Total: 1,803 kcal"') == ["paneer, 100 g: 265 kcal",
                                                                             "total: 1,803 kcal"]
    assert checks.norm("**Don’t**   guess") == "don't guess"


def _make(tmp: Path, quote: str, body: str = "short body") -> Path:
    out = tmp / "outputs" / "carousel-x"
    (out / "runs").mkdir(parents=True)
    (out / "runs" / "r1.md").write_text("The model said: **Stand mid-foot under the bar**, feet hip-width apart.")
    (out / "CAPTION.txt").write_text("caption TRAINER")
    sub = {"contract": CONTRACT, "id": "carousel-x", "version": "v1", "media_dir": str(tmp / "media"),
           "post_files": [], "contact_sheet": "cs.jpg", "caption_file": "CAPTION.txt", "runs_dir": "runs",
           "slides": [{"n": 1, "kind": "still", "headline": "H", "body": body,
                       "quotes": [{"text": quote, "run": "runs/r1.md"}]}]}
    (out / "SUBMISSION.json").write_text(json.dumps(sub))
    return out


def test_quote_check(tmp_path):
    out = _make(tmp_path, "Stand mid-foot under the bar… feet hip-width apart")
    sub, problems = load(out)
    assert not problems
    assert not [i for i in checks.check_text(sub) if "verbatim" in i["msg"]]
    out2 = _make(tmp_path / "b", "Stand with feet wide under the bar")
    sub2, _ = load(out2)
    assert [i for i in checks.check_text(sub2) if "verbatim" in i["msg"]]


def test_body_word_limit(tmp_path):
    sub, _ = load(_make(tmp_path, "Stand mid-foot under the bar", body=" ".join(["word"] * 30)))
    assert any("body 30 words" in i["msg"] for i in checks.check_text(sub))


def test_missing_submission(tmp_path):
    sub, problems = load(tmp_path / "outputs" / "nothing")
    assert sub is None and problems
