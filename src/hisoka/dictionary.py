import re
from pathlib import Path

DICT_DIR = Path.home() / "Documents" / "mtg" / "_dictionary"
TEMPLATE = """# {title}

文字起こしと要約で、{kind}をこの表記に揃える。「読み・誤認識」には、音声認識が間違えやすい表記をカンマ区切りで書く。

| 表記 | 読み・誤認識 | 補足 |
| --- | --- | --- |
"""
FILES = {
    "people.md": TEMPLATE.format(title="人名辞書", kind="人名"),
    "terms.md": TEMPLATE.format(title="用語辞書", kind="用語"),
}


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
    """辞書ファイルを読む。ファイルがなければ空の表のテンプレートを作る。"""
    dict_dir.mkdir(parents=True, exist_ok=True)
    entries = []
    for name, template in FILES.items():
        path = dict_dir / name
        if not path.exists():
            path.write_text(template)
        entries += parse_table(path.read_text())
    return entries


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
