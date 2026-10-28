import json
from pathlib import Path


def assign_speakers(segments: list[dict], turns: list[dict]) -> list[dict]:
    """各セグメントに時間が最も重なる話者を割り当て、同じ話者の連続を1発言にまとめる。

    話者番号は登場順に 1 から振り直す。重なる話者がいなければ直前の話者を引き継ぐ。
    """
    # ponytail: セグメント×話者区間の総当たり O(n*m)。数時間の会議で遅ければ二分探索にする
    labels: dict[int, int] = {}
    utterances: list[dict] = []
    for seg in segments:
        overlap: dict[int, float] = {}
        for t in turns:
            d = min(seg["end"], t["end"]) - max(seg["start"], t["start"])
            if d > 0:
                overlap[t["speaker"]] = overlap.get(t["speaker"], 0.0) + d
        if overlap:
            raw = max(overlap, key=overlap.get)
            speaker = labels.setdefault(raw, len(labels) + 1)
        elif utterances:
            speaker = utterances[-1]["speaker"]
        else:
            speaker = 0  # 話者不明

        if utterances and utterances[-1]["speaker"] == speaker:
            utterances[-1]["end"] = seg["end"]
            utterances[-1]["text"] += " " + seg["text"]
        else:
            utterances.append({**seg, "speaker": speaker})
    return utterances


def format_line(u: dict) -> str:
    s = int(u["start"])
    name = f"話者{u['speaker']}" if u["speaker"] else "話者不明"
    return f"[{s // 3600:02d}:{s % 3600 // 60:02d}:{s % 60:02d}] {name}：{u['text']}"


def merge(meeting_dir: Path) -> Path:
    """transcript.json と diarization.json を突き合わせ、meeting_dir/merged.txt に書き出す。"""
    segments = json.loads((meeting_dir / "transcript.json").read_text())
    turns = json.loads((meeting_dir / "diarization.json").read_text())
    out = meeting_dir / "merged.txt"
    out.write_text("\n".join(format_line(u) for u in assign_speakers(segments, turns)) + "\n")
    return out
