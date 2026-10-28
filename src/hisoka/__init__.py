import argparse
import time
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(prog="hisoka")
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("transcribe", help="会議フォルダの audio.wav を文字起こしする")
    p.add_argument("meeting_dir", type=Path)
    args = parser.parse_args()

    if args.command == "transcribe":
        from hisoka.transcribe import transcribe

        started = time.perf_counter()
        out = transcribe(args.meeting_dir)
        print(f"{out} ({time.perf_counter() - started:.1f}s)")
