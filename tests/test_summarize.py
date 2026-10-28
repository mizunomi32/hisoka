import json

from hisoka.summarize import chunk_lines, parse_summary


def test_chunk_lines():
    text = "あ" * 4 + "\n" + "い" * 4 + "\n" + "う" * 12 + "\n"
    # 長すぎる行も途中で切らず、1チャンクにする
    assert chunk_lines(text, size=10) == ["ああああ\nいいいい\n", "う" * 12 + "\n"]


def test_parse_summary():
    summary = {"overview": "概要", "decisions": [], "todos": [], "topics": []}
    assert parse_summary(json.dumps(summary)) == summary
    assert parse_summary("```json\n" + json.dumps(summary) + "\n```") == summary
    for bad in ["- **overview**: 概要", json.dumps({"overview": "概要"})]:
        try:
            parse_summary(bad)
        except ValueError:
            continue
        raise AssertionError(f"不正な出力を受け入れた: {bad}")


if __name__ == "__main__":
    test_chunk_lines()
    test_parse_summary()
    print("ok")
