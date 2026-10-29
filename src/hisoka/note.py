import json
from datetime import datetime
from pathlib import Path

from hisoka.transcribe import load_lines

OUT_DIR = Path.home() / "Documents" / "mtg"
RAW_DIR = "raw"  # 文字起こしの保存先（OUT_DIR からの相対）


def render_summary(summary: dict, meta: dict) -> str:
    """要約の Markdown ノートを作る。文字起こしは別ファイルへのリンクにする。"""
    front = ["---", f"date: {meta['date']:%Y-%m-%d %H:%M}", f"audio: {meta['audio']}", "tags: [meeting]", "---"]
    body = [f"# 会議メモ {meta['date']:%Y-%m-%d %H:%M}", "", f"文字起こし：[{meta['raw']}]({meta['raw']})", ""]
    body += ["## 概要", "", summary["overview"], "", "## 決定事項", ""]
    body += [f"- {d}" for d in summary["decisions"]] or ["なし"]
    body += ["", "## ToDo", ""]
    body += [f"- [ ] {t['task']}（担当：{t['owner']} / 期限：{t['due']}）" for t in summary["todos"]] or ["なし"]
    body += ["", "## 議題ごとの要点", ""]
    for topic in summary["topics"]:
        body += [f"### {topic['title']}", ""] + [f"- {p}" for p in topic["points"]] + [""]
    return "\n".join(front + body).rstrip("\n") + "\n"


def render_transcript(lines: list[str], meta: dict) -> str:
    # 1発言ずつ段落にする（空行なしだと Markdown ビューアによって1段落に繋がる）
    return f"# 文字起こし {meta['date']:%Y-%m-%d %H:%M}\n\n" + "\n\n".join(lines) + "\n"


def pick_name(out_dir: Path, date: datetime) -> str:
    """`YYYY-MM-DD_HHMM` を返す。要約か文字起こしに同名があれば `-2`, `-3` … を付け、上書きしない。"""
    base = f"{date:%Y-%m-%d_%H%M}"
    name, n = base, 1
    while (out_dir / f"{name}.md").exists() or (out_dir / RAW_DIR / f"{name}.md").exists():
        n += 1
        name = f"{base}-{n}"
    return name


def meeting_date(meeting_dir: Path) -> datetime:
    """会議フォルダ名 `YYYY-MM-DD_HHMM` の日時。違う名前なら audio.wav の更新日時。"""
    try:
        return datetime.strptime(meeting_dir.resolve().name, "%Y-%m-%d_%H%M")
    except ValueError:
        return datetime.fromtimestamp((meeting_dir / "audio.wav").stat().st_mtime)


def note(meeting_dir: Path, out_dir: Path = OUT_DIR) -> Path:
    """summary.json と transcript.json から、out_dir に要約、out_dir/raw に文字起こしを書き出す。"""
    summary = json.loads((meeting_dir / "summary.json").read_text())
    date = meeting_date(meeting_dir)
    (out_dir / RAW_DIR).mkdir(parents=True, exist_ok=True)
    name = pick_name(out_dir, date)
    meta = {"date": date, "audio": (meeting_dir / "audio.wav").resolve(), "raw": f"{RAW_DIR}/{name}.md"}

    (out_dir / RAW_DIR / f"{name}.md").write_text(render_transcript(load_lines(meeting_dir), meta))
    out = out_dir / f"{name}.md"
    out.write_text(render_summary(summary, meta))
    return out
