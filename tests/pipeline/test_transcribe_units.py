import pytest

from content_os.pipeline import transcribe
from content_os.pipeline.reel import StageError


def test_chunks_split_at_pauses_and_cap_length():
    regions = [[0.5, 1.0], [1.2, 3.0], [4.0, 6.0], [6.1, 40.0]]
    chunks = transcribe.make_chunks(regions, 41.0, 28.0, split_gap=0.5)
    assert len(chunks) == 3
    assert chunks[0][0] == 0.25 and chunks[0][1] <= 3.5
    # chunks never overlap
    assert all(a[1] <= b[0] for a, b in zip(chunks, chunks[1:]))


def test_dtw_preset_from_model_name():
    assert transcribe.dtw_preset("/x/ggml-small.en.bin", "auto") == "small.en"
    assert transcribe.dtw_preset("/x/ggml-medium.en.bin", "auto") == "medium.en"
    assert transcribe.dtw_preset("/x/ggml-large-v3.bin", "auto") == "large.v3"
    assert transcribe.dtw_preset("/x/custom.bin", "auto") is None
    assert transcribe.dtw_preset("/x/ggml-small.en.bin", "off") is None


def test_whisper_tokens_merge_into_words():
    js = {"transcription": [{"tokens": [
        {"text": "[_BEG_]", "offsets": {"from": 0, "to": 0}, "p": 0.9, "t_dtw": -1},
        {"text": " Beat", "offsets": {"from": 50, "to": 460}, "p": 0.5, "t_dtw": 12},
        {"text": " 1", "offsets": {"from": 460, "to": 580}, "p": 0.5, "t_dtw": 40},
        {"text": ".", "offsets": {"from": 580, "to": 600}, "p": 0.9, "t_dtw": 45},
        {"text": " work", "offsets": {"from": 900, "to": 1000}, "p": 1.0, "t_dtw": 95},
        {"text": "flows", "offsets": {"from": 1000, "to": 1200}, "p": 1.0, "t_dtw": 100},
        {"text": "[_TT_50]", "offsets": {"from": 1200, "to": 1200}, "p": 0.2, "t_dtw": -1}]}]}
    words = transcribe.whisper_words(js)
    assert [w["text"] for w in words] == ["Beat", "1.", "workflows"]
    assert words[0]["anchor"] == 0.12 and words[2]["anchor"] == 0.95


def test_snap_words_uses_pause_edges():
    words = [{"text": "a", "anchor": 1.1}, {"text": "b", "anchor": 1.4}, {"text": "c", "anchor": 3.15}]
    out = transcribe.snap_words(words, [[1.0, 1.8], [3.0, 3.5]], lead=0.08)
    assert out[0]["start"] == 1.0 and out[1]["end"] == 1.8
    assert out[2]["start"] == 3.0 and out[2]["end"] == 3.5
    assert out[0]["end"] == out[1]["start"]


def test_openai_requires_env_key(monkeypatch, tmp_path):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    f = tmp_path / "c.wav"
    f.write_bytes(b"RIFF")
    with pytest.raises(StageError, match="OPENAI_API_KEY"):
        transcribe.run_openai([f], {"openai_model": "whisper-1", "language": "en"})


def test_openai_engine_request_shape(monkeypatch, tmp_path):
    calls = []

    class FakeTranscriptions:
        def create(self, **kw):
            calls.append(kw)
            return {"words": [{"word": "Beat", "start": 0.1, "end": 0.4}, {"word": "one", "start": 0.4, "end": 0.7}]}

    class FakeClient:
        def __init__(self, api_key):
            assert api_key == "sk-test"
            self.audio = type("A", (), {"transcriptions": FakeTranscriptions()})()

    import openai

    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    monkeypatch.setattr(openai, "OpenAI", FakeClient)
    f = tmp_path / "c.wav"
    f.write_bytes(b"RIFF0000")
    res = transcribe.run_openai([f], {"openai_model": "whisper-1", "language": "en"})
    assert calls[0]["model"] == "whisper-1"
    assert calls[0]["response_format"] == "verbose_json"
    assert calls[0]["timestamp_granularities"] == ["word"]
    assert [w["text"] for w in res[0]] == ["Beat", "one"]
