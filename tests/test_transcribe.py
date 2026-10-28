from hisoka.transcribe import drop_hallucinations


def seg(start, end, text):
    return {"start": start, "end": end, "text": text}


def test_drop_hallucinations():
    segments = [
        seg(0.0, 2.0, "よろしくお願いします"),
        seg(10.0, 12.0, "ご視聴ありがとうございました"),
        seg(2300.0, 2304.0, "失礼します"),
        seg(2321.7, 2351.7, "チャンネル登録をお願いいたします。"),
        seg(2320.0, 2340.0, "長さを超える発言"),
    ]
    kept = drop_hallucinations(segments, duration=2326.0)
    assert [s["text"] for s in kept] == ["よろしくお願いします", "失礼します"]


if __name__ == "__main__":
    test_drop_hallucinations()
    print("ok")
