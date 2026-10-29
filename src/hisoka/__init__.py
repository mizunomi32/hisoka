import argparse
import time
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(prog="hisoka")
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("run", help="文字起こし → 要約 → 書き出しを順に実行する")
    p.add_argument("meeting_dir", type=Path)
    p = sub.add_parser("transcribe", help="会議フォルダの audio.wav を文字起こしする")
    p.add_argument("meeting_dir", type=Path)
    p = sub.add_parser("summarize", help="文字起こしを要約する")
    p.add_argument("meeting_dir", type=Path)
    p = sub.add_parser("note", help="要約と文字起こしを ~/Documents/mtg に Markdown で書き出す")
    p.add_argument("meeting_dir", type=Path)
    args = parser.parse_args()

    steps = ["transcribe", "summarize", "note"] if args.command == "run" else [args.command]
    for step in steps:
        started = time.perf_counter()
        if step == "transcribe":
            from hisoka.transcribe import transcribe

            out = transcribe(args.meeting_dir)
        elif step == "summarize":
            from hisoka.summarize import summarize

            out = summarize(args.meeting_dir)
        else:
            from hisoka.note import note

            out = note(args.meeting_dir)
        print(f"{out} ({time.perf_counter() - started:.1f}s)")
