import tempfile
from pathlib import Path

from hisoka.dictionary import correct, load, parse_table, prompt_block

TABLE = """# 人名辞書

説明文。

| 表記 | 読み・誤認識 | 補足 |
| --- | --- | --- |
| 本田圭佑 | 本田圭介, 本田啓介 | サッカー選手 |
| Redash | リダッシュ、レダッシュ | |
| 未登録 | | |
"""


def test_parse_table():
    assert parse_table(TABLE) == [
        {"term": "本田圭佑", "variants": ["本田圭介", "本田啓介"], "note": "サッカー選手"},
        {"term": "Redash", "variants": ["リダッシュ", "レダッシュ"], "note": ""},
        {"term": "未登録", "variants": [], "note": ""},
    ]


def test_correct():
    entries = parse_table(TABLE) + [{"term": "ABC社", "variants": ["ABC", "ABCシャ"], "note": ""}]
    assert correct("本田啓介さんがリダッシュを使う", entries) == "本田圭佑さんがRedashを使う"
    # 置き換えた結果や、もともと正しい表記を二重に置き換えない（「ABC社社」にしない）
    assert correct("ABCシャの件とABC社の件とABCの件", entries) == "ABC社の件とABC社の件とABC社の件"
    assert correct("そのまま", []) == "そのまま"


def test_prompt_block():
    assert prompt_block([]) == ""
    assert prompt_block(parse_table(TABLE)[:2]) == "\n\n人名・用語は次の表記に揃えてください。\n- 本田圭佑（サッカー選手）\n- Redash\n"


def test_load_creates_templates():
    with tempfile.TemporaryDirectory() as d:
        dict_dir = Path(d) / "_dictionary"
        assert load(dict_dir) == []  # テンプレートは空の表
        assert sorted(p.name for p in dict_dir.iterdir()) == ["people.md", "terms.md"]
        assert (dict_dir / "people.md").read_text().startswith("# 人名辞書\n")

        # 既存のファイルは上書きしない
        (dict_dir / "terms.md").write_text(TABLE)
        assert [e["term"] for e in load(dict_dir)] == ["本田圭佑", "Redash", "未登録"]


if __name__ == "__main__":
    test_parse_table()
    test_correct()
    test_prompt_block()
    test_load_creates_templates()
    print("ok")
