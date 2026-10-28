import argparse
import time
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(prog="hisoka")
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("transcribe", help="会議フォルダの audio.wav を文字起こしする")
    p.add_argument("meeting_dir", type=Path)
    p = sub.add_parser("diarize", help="会議フォルダの audio.wav を話者分離する")
    p.add_argument("meeting_dir", type=Path)
    p.add_argument("--speakers", type=int, help="話者数（分かっている場合）")
    p = sub.add_parser("merge", help="文字起こしと話者分離を突き合わせる")
    p.add_argument("meeting_dir", type=Path)
    p = sub.add_parser("summarize", help="話者付き文字起こしを要約する")
    p.add_argument("meeting_dir", type=Path)
    args = parser.parse_args()

    started = time.perf_counter()
    if args.command == "transcribe":
        from hisoka.transcribe import transcribe

        out = transcribe(args.meeting_dir)
    elif args.command == "diarize":
        from hisoka.diarize import diarize

        out = diarize(args.meeting_dir, args.speakers)
    elif args.command == "merge":
        from hisoka.merge import merge

        out = merge(args.meeting_dir)
    else:
        from hisoka.summarize import summarize

        out = summarize(args.meeting_dir)
    print(f"{out} ({time.perf_counter() - started:.1f}s)")
