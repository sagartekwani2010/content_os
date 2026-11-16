from content_os.pipeline import segment, textmatch as tm

from .conftest import words_from

BEATS = [{"id": 1, "text": "Most agents are workflows wearing a costume."},
         {"id": 2, "text": "Here is the test I use before I build one."},
         {"id": 3, "text": "If the steps never change, write a script instead."}]
for b in BEATS:
    b["tokens"] = tm.tokens(b["text"])


def run(spec, cfg):
    return segment.segment_source("s1", words_from(spec), BEATS, cfg["segment"])


def test_cues_and_attempts(cfg):
    takes, cues, unassigned = run([
        ("Beat 1.", 0.0), (BEATS[0]["text"], 0.8), (BEATS[0]["text"], 1.0),
        ("beat two", 1.0),
        ("Here is the", 0.8), (BEATS[1]["text"], 1.0), (BEATS[1]["text"], 1.0),
    ], cfg)
    assert [c["beat"] for c in cues] == [1, 2]
    assert [t["beat"] for t in takes] == [1, 1, 2, 2, 2]
    assert [t["complete"] for t in takes] == [True, True, False, True, True]
    assert not unassigned


def test_asr_variant_cues(cfg):
    takes, cues, _ = run([("bit 3", 0.0), (BEATS[2]["text"], 0.8), ("beat number one", 1.0), (BEATS[0]["text"], 0.8)], cfg)
    assert [c["beat"] for c in cues] == [3, 1]
    assert [t["beat"] for t in takes] == [3, 1]


def test_word_beat_inside_speech_is_not_a_cue(cfg):
    spec = [("Beat 2.", 0.0), ("Here is the test I use to beat two rivals before I build one", 0.8)]
    takes, cues, _ = run(spec, cfg)
    assert [c["beat"] for c in cues] == [2]
    assert len(takes) == 1


def test_restart_without_pause_is_split(cfg):
    takes, _, _ = run([("Beat 1.", 0.0), ("Most agents are most agents are workflows wearing a costume.", 0.8)], cfg)
    assert len(takes) == 2
    assert takes[0]["complete"] is False and "abandoned_restart" in takes[0]["flags"]
    assert takes[1]["complete"] is True and takes[1]["text"].startswith("most agents are workflows")


def test_restart_after_short_pause_goes_back_in_script(cfg):
    # pause 0.5 s (>= attempt_gap) and the speaker goes back to the start of the line
    takes, _, _ = run([("Beat 1.", 0.0), ("Most agents are workflows", 0.8), (BEATS[0]["text"], 0.5)], cfg)
    assert len(takes) == 2 and takes[1]["complete"]


def test_mid_line_pause_continues_attempt(cfg):
    takes, _, _ = run([("Beat 3.", 0.0), ("If the steps never change,", 0.8), ("write a script instead.", 0.5)], cfg)
    assert len(takes) == 1 and takes[0]["complete"]
    assert takes[0]["internal_pauses"]


def test_no_cue_falls_back_to_similarity(cfg):
    takes, cues, _ = run([(BEATS[1]["text"], 0.0), (BEATS[2]["text"], 1.6)], cfg)
    assert cues == []
    assert [t["beat"] for t in takes] == [2, 3]
    assert all(t["assigned_by"] == "similarity" for t in takes)


def test_beat_mismatch_flag(cfg):
    takes, _, _ = run([("Beat 1.", 0.0), (BEATS[2]["text"], 0.8)], cfg)
    assert any(f.startswith("beat_mismatch:3") for f in takes[0]["flags"])


def test_fillers_counted(cfg):
    takes, _, _ = run([("Beat 1.", 0.0), ("Most agents um are workflows wearing a costume.", 0.8)], cfg)
    assert takes[0]["fillers"] == 1 and takes[0]["filler_words"] == ["um"]
