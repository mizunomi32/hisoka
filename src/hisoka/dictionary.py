import re
from pathlib import Path

DICT_DIR = Path.home() / "Documents" / "mtg" / "_dictionary"
FILES = ["people.md", "terms.md"]


def parse_table(markdown: str) -> list[dict]:
    """`| 表記 | 読み・誤認識 | 補足 |` の表を読む。誤認識はカンマ（、も可）区切り。"""
    entries = []
    for line in markdown.splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if not line.lstrip().startswith("|") or len(cells) < 3 or cells[0] in ("表記", "") or set(cells[0]) <= set("-: "):
            continue
        variants = [v.strip() for v in cells[1].replace("、", ",").split(",") if v.strip()]
        entries.append({"term": cells[0], "variants": variants, "note": cells[2]})
    return entries


def load(dict_dir: Path = DICT_DIR) -> list[dict]:
    """辞書ファイルを読む。ファイルがなければ空。"""
    return [e for f in FILES if (dict_dir / f).exists() for e in parse_table((dict_dir / f).read_text())]


def correct(text: str, entries: list[dict]) -> str:
    """誤認識されやすい表記を、辞書の表記に置き換える。"""
    # 1回の走査で置き換える。順に replace すると置き換え後の表記（ABC社）の一部（ABC）をまた置き換えてしまう。
    # 正しい表記もそのまま残す対象として入れ、長い順に照合する
    mapping = {v: e["term"] for e in entries for v in e["variants"]} | {e["term"]: e["term"] for e in entries}
    if not mapping:
        return text
    pattern = re.compile("|".join(re.escape(k) for k in sorted(mapping, key=len, reverse=True)))
    return pattern.sub(lambda m: mapping[m.group(0)], text)


def prompt_block(entries: list[dict]) -> str:
    """要約プロンプトに足す、表記の一覧。辞書が空なら空文字。"""
    if not entries:
        return ""
    lines = [f"- {e['term']}（{e['note']}）" if e["note"] else f"- {e['term']}" for e in entries]
    return "\n\n人名・用語は次の表記に揃えてください。\n" + "\n".join(lines) + "\n"
