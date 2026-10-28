import json
from datetime import datetime
from pathlib import Path

from hisoka.transcribe import load_lines


def render_note(summary: dict, transcript: list[str], meta: dict) -> str:
    """要約と文字起こしから、Obsidian 用の Markdown ノートを作る。"""
    front = ["---"]
    if "date" in meta:
        front.append(f"date: {meta['date']:%Y-%m-%d %H:%M}")
    front += [f"audio: {meta['audio']}", "tags: [meeting]", "---"]
    title = f"# 会議メモ {meta['date']:%Y-%m-%d %H:%M}" if "date" in meta else "# 会議メモ"

    body = [title, "", "## 概要", "", summary["overview"], "", "## 決定事項", ""]
    body += [f"- {d}" for d in summary["decisions"]] or ["なし"]
    body += ["", "## ToDo", ""]
    body += [f"- [ ] {t['task']}（担当：{t['owner']} / 期限：{t['due']}）" for t in summary["todos"]] or ["なし"]
    body += ["", "## 議題ごとの要点", ""]
    for topic in summary["topics"]:
        body += [f"### {topic['title']}", ""] + [f"- {p}" for p in topic["points"]] + [""]
    # 1発言ずつ段落にする（空行なしだと Obsidian の設定によって1段落に繋がる）
    body += ["## 文字起こし", "", "\n\n".join(transcript)]
    return "\n".join(front + body) + "\n"


def note(meeting_dir: Path) -> Path:
    """summary.json と transcript.json から meeting_dir/note.md を作る。"""
    summary = json.loads((meeting_dir / "summary.json").read_text())
    meta = {"audio": (meeting_dir / "audio.wav").resolve()}
    try:  # 会議フォルダ名 YYYY-MM-DD_HHMM から日時を取る
        meta["date"] = datetime.strptime(meeting_dir.resolve().name, "%Y-%m-%d_%H%M")
    except ValueError:
        pass

    out = meeting_dir / "note.md"
    out.write_text(render_note(summary, load_lines(meeting_dir), meta))
    return out
