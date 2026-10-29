import argparse
import time
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(prog="hisoka")
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("record", help="録音し、停止後に run と同じ処理を行う")
    p.add_argument("--device", help="入力デバイス名（一部でよい）。省略時はシステムの既定の入力")
    p.add_argument("--list-devices", action="store_true", help="入力デバイスの一覧を表示して終わる")
    p.add_argument("--no-run", action="store_true", help="録音だけして、文字起こし以降を行わない")
    p = sub.add_parser("run", help="文字起こし → 要約 → 書き出しを順に実行する")
    p.add_argument("meeting_dir", type=Path)
    p = sub.add_parser("transcribe", help="会議フォルダの audio.wav を文字起こしする")
    p.add_argument("meeting_dir", type=Path)
    p = sub.add_parser("summarize", help="文字起こしを要約する")
    p.add_argument("meeting_dir", type=Path)
    p = sub.add_parser("note", help="要約と文字起こしを ~/Documents/mtg に Markdown で書き出す")
    p.add_argument("meeting_dir", type=Path)
    args = parser.parse_args()

    if args.command == "record":
        if args.list_devices:
            import sounddevice as sd

            for i, d in enumerate(sd.query_devices()):
                if d["max_input_channels"] > 0:
                    print(f"{i}: {d['name']}（{d['max_input_channels']}ch）")
            return
        from hisoka.record import record

        args.meeting_dir = record(args.device)
        if args.no_run:
            return

    steps = ["transcribe", "summarize", "note"] if args.command in ("record", "run") else [args.command]
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
