from datetime import datetime

from hisoka.note import render_note


def test_render_note():
    summary = {
        "overview": "予算を決めた。",
        "decisions": ["予算は100万円"],
        "todos": [{"task": "見積もりを出す", "owner": "田中", "due": "来週"}],
        "topics": [{"title": "予算", "points": ["100万円で合意"]}],
    }
    transcript = ["[00:00:01] 見積もりを出します", "[00:00:05] 予算は100万円で"]
    meta = {"date": datetime(2026, 10, 28, 14, 0), "audio": "/m/audio.wav"}
    md = render_note(summary, transcript, meta)

    assert md.startswith("---\ndate: 2026-10-28 14:00\naudio: /m/audio.wav\ntags: [meeting]\n---\n# 会議メモ 2026-10-28 14:00\n")
    assert "## 決定事項\n\n- 予算は100万円\n" in md
    assert "- [ ] 見積もりを出す（担当：田中 / 期限：来週）" in md
    assert "### 予算\n\n- 100万円で合意\n" in md
    assert md.endswith("## 文字起こし\n\n[00:00:01] 見積もりを出します\n\n[00:00:05] 予算は100万円で\n")


def test_render_note_empty():
    summary = {"overview": "雑談。", "decisions": [], "todos": [], "topics": []}
    md = render_note(summary, [], {"audio": "a.wav"})
    assert "# 会議メモ\n" in md and "date:" not in md
    assert "## 決定事項\n\nなし\n" in md and "## ToDo\n\nなし\n" in md


if __name__ == "__main__":
    test_render_note()
    test_render_note_empty()
    print("ok")
