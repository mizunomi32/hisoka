from hisoka.merge import assign_speakers, format_line


def test_assign_speakers():
    segments = [
        {"start": 0.0, "end": 2.0, "text": "こんにちは"},
        {"start": 2.0, "end": 4.0, "text": "よろしく"},
        {"start": 4.0, "end": 6.0, "text": "どうも"},
        {"start": 6.0, "end": 7.0, "text": "はい"},  # 話者区間なし → 直前を引き継ぐ
        {"start": 7.0, "end": 9.0, "text": "では"},
    ]
    turns = [
        {"start": 0.0, "end": 3.5, "speaker": 5},
        {"start": 3.5, "end": 6.0, "speaker": 2},
        {"start": 7.0, "end": 9.0, "speaker": 5},
    ]
    got = [(u["speaker"], u["text"]) for u in assign_speakers(segments, turns)]
    assert got == [(1, "こんにちは よろしく"), (2, "どうも はい"), (1, "では")]


def test_format_line():
    assert format_line({"start": 754.9, "speaker": 1, "text": "〜"}) == "[00:12:34] 話者1：〜"


if __name__ == "__main__":
    test_assign_speakers()
    test_format_line()
    print("ok")
