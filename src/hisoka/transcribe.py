import json
import wave
from pathlib import Path

from hisoka import dictionary

MODEL = "mlx-community/whisper-large-v3-turbo"

# 無音区間で Whisper が出しがちな、動画由来の定型文
# ponytail: 完全一致の固定リスト。取りこぼしが増えたら VAD で無音区間ごと除外する
HALLUCINATIONS = {
    "チャンネル登録をお願いいたします",
    "チャンネル登録お願いします",
    "ご視聴ありがとうございました",
    "最後までご視聴いただきありがとうございました",
}


def drop_hallucinations(segments: list[dict], duration: float) -> list[dict]:
    """音声の長さを超えるセグメントと、定型の誤認識を除く。"""
    return [
        s
        for s in segments
        if s["end"] <= duration + 1.0 and s["text"].rstrip("。！!") not in HALLUCINATIONS
    ]


def format_lines(segments: list[dict]) -> list[str]:
    """セグメントを `[00:12:34] 発言` の行にする。"""
    lines = []
    for seg in segments:
        s = int(seg["start"])
        lines.append(f"[{s // 3600:02d}:{s % 3600 // 60:02d}:{s % 60:02d}] {seg['text']}")
    return lines


def load_lines(meeting_dir: Path) -> list[str]:
    """transcript.json を行にし、辞書で誤認識を直す。辞書を直したら文字起こしをやり直さずに反映される。"""
    entries = dictionary.load()
    return [dictionary.correct(line, entries) for line in format_lines(json.loads((meeting_dir / "transcript.json").read_text()))]


def transcribe(meeting_dir: Path) -> Path:
    """meeting_dir/audio.wav を文字起こしし、meeting_dir/transcript.json に書き出す。"""
    import mlx_whisper  # 重いので、要約やノート作成で load_lines だけ使うときは読み込まない

    audio = meeting_dir / "audio.wav"
    with wave.open(str(audio)) as w:
        duration = w.getnframes() / w.getframerate()

    result = mlx_whisper.transcribe(
        str(audio),
        path_or_hf_repo=MODEL,
        language="ja",
        condition_on_previous_text=False,
    )
    segments = [
        {"start": s["start"], "end": s["end"], "text": s["text"].strip()}
        for s in result["segments"]
    ]
    out = meeting_dir / "transcript.json"
    out.write_text(json.dumps(drop_hallucinations(segments, duration), ensure_ascii=False, indent=2))
    return out
