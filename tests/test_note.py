import tempfile
from datetime import datetime
from pathlib import Path

from hisoka.note import pick_name, render_summary, render_transcript

DATE = datetime(2026, 10, 28, 14, 0)


def test_render_summary():
    summary = {
        "overview": "予算を決めた。",
        "decisions": ["予算は100万円"],
        "todos": [{"task": "見積もりを出す", "owner": "田中", "due": "来週"}],
        "topics": [{"title": "予算", "points": ["100万円で合意"]}],
    }
    md = render_summary(summary, {"date": DATE, "audio": "/m/audio.wav", "raw": "raw/2026-10-28_1400.md"})

    assert md.startswith("---\ndate: 2026-10-28 14:00\naudio: /m/audio.wav\ntags: [meeting]\n---\n# 会議メモ 2026-10-28 14:00\n")
    assert "文字起こし：[raw/2026-10-28_1400.md](raw/2026-10-28_1400.md)" in md
    assert "## 決定事項\n\n- 予算は100万円\n" in md
    assert "- [ ] 見積もりを出す（担当：田中 / 期限：来週）" in md
    assert md.endswith("### 予算\n\n- 100万円で合意\n")


def test_render_summary_empty():
    summary = {"overview": "雑談。", "decisions": [], "todos": [], "topics": []}
    md = render_summary(summary, {"date": DATE, "audio": "a.wav", "raw": "raw/x.md"})
    assert "## 決定事項\n\nなし\n" in md and "## ToDo\n\nなし\n" in md


def test_render_transcript():
    md = render_transcript(["[00:00:01] 見積もりを出します", "[00:00:05] 予算は100万円で"], {"date": DATE})
    assert md == "# 文字起こし 2026-10-28 14:00\n\n[00:00:01] 見積もりを出します\n\n[00:00:05] 予算は100万円で\n"


def test_pick_name():
    with tempfile.TemporaryDirectory() as d:
        out = Path(d)
        (out / "raw").mkdir()
        assert pick_name(out, DATE) == "2026-10-28_1400"
        (out / "2026-10-28_1400.md").touch()
        assert pick_name(out, DATE) == "2026-10-28_1400-2"
        (out / "raw" / "2026-10-28_1400-2.md").touch()  # 文字起こしだけ残っていても避ける
        assert pick_name(out, DATE) == "2026-10-28_1400-3"


if __name__ == "__main__":
    test_render_summary()
    test_render_summary_empty()
    test_render_transcript()
    test_pick_name()
    print("ok")
