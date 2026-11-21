from content_os.orchestrator import moodboard

MB = {"concept": "c", "palette": ["#FF3B6B accent: alarm", "#6EE7F9 lines"], "typography": "Barlow", "texture": "chalk",
      "music": "m", "sfx_palette": ["hit"], "pacing": "p",
      "keyframes": [{"id": "KF01", "time_s": 0, "beats": [1], "emotion": "fear", "layout": "split", "shot": "s",
                     "on_screen_text": "<b>4 OF 11</b>"},
                    {"id": "KF02", "time_s": 6, "beats": [2, 3], "emotion": "hope", "layout": "card", "shot": "card",
                     "on_screen_text": "TASKS"}],
      "shot_list": ["screen-record"]}


def test_board_escapes_uses_images_and_maps_beats(tmp_path):
    (tmp_path / "moodboard").mkdir()
    (tmp_path / "moodboard" / "KF02.png").write_bytes(b"png")
    files = moodboard.write_board(tmp_path, MB, "t")
    page = files["MOODBOARD.html"].read_text()
    assert "&lt;b&gt;4 OF 11&lt;/b&gt;" in page and "<b>4 OF 11" not in page
    assert 'src="moodboard/KF02.png"' in page and "#FF3B6B" in page
    assert [k["id"] for k in moodboard.keyframes_for_beat(moodboard.load(tmp_path), 3)] == ["KF02"]
