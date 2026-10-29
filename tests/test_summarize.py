import json

from hisoka import summarize
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


def test_parse_summary_drops_empty_todos():
    content = json.dumps({
        "overview": "概要", "decisions": [], "topics": [],
        "todos": [{"task": "不明", "owner": "不明", "due": "不明"}, {"task": "見積もり", "owner": "田中", "due": "不明"}],
    })
    assert [t["task"] for t in parse_summary(content)["todos"]] == ["見積もり"]


class FakeResponse:
    def __init__(self, content):
        self.body = json.dumps({"message": {"content": content}}).encode()

    def read(self):
        return self.body

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


def test_chat_retries():
    good = json.dumps({"overview": "概要", "decisions": [], "todos": [], "topics": []})
    replies = [ConnectionResetError("Ollama 再起動"), FakeResponse('{"overview": "閉じ忘れ"'), FakeResponse(good)]
    temperatures = []

    def fake_urlopen(req, timeout):
        temperatures.append(json.loads(req.data)["options"]["temperature"])
        reply = replies.pop(0)
        if isinstance(reply, Exception):
            raise reply
        return reply

    original, summarize.urllib.request.urlopen = summarize.urllib.request.urlopen, fake_urlopen
    summarize.RETRY_WAIT = 0
    try:
        assert summarize._chat("system", "user")["overview"] == "概要"
        assert temperatures == [0.2, 0.5, 0.8]  # 接続エラー、壊れた JSON のあと、3回目で成功

        replies[:] = [FakeResponse("壊れた")] * 3
        try:
            summarize._chat("system", "user")
        except ValueError:
            pass
        else:
            raise AssertionError("3回失敗したら例外にする")
    finally:
        summarize.urllib.request.urlopen = original


if __name__ == "__main__":
    test_chunk_lines()
    test_parse_summary()
    test_parse_summary_drops_empty_todos()
    test_chat_retries()
    print("ok")
