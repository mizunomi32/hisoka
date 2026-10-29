import json
import time
import urllib.request
from pathlib import Path

from hisoka import dictionary
from hisoka.transcribe import load_lines

OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL = "gemma4:e4b"
# ponytail: リポジトリ直下の prompts/ を読む。アプリ化するときは config.toml でパスを指定する
PROMPTS_DIR = Path(__file__).resolve().parents[2] / "prompts"
CHUNK_CHARS = 6000
RETRY_WAIT = 5  # 接続が切れたときに再試行するまでの秒数

# Ollama 0.20 + qwen3.5 では format にスキーマを渡しても出力が制約されないため、
# 形はプロンプトで指示し、受け取った側で検証する。プロンプトファイルを編集しても壊れないようコード側に置く
JSON_INSTRUCTION = """

出力は次の形の JSON オブジェクトだけにしてください。前後に説明文やコードフェンスを付けないでください。
{"overview": "文字列", "decisions": ["文字列"], "todos": [{"task": "文字列", "owner": "文字列", "due": "文字列"}], "topics": [{"title": "文字列", "points": ["文字列"]}]}
"""
KEYS = {"overview", "decisions", "todos", "topics"}


def parse_summary(content: str) -> dict:
    """モデルの出力から要約 JSON を取り出す。コードフェンスで囲まれていても読む。"""
    content = content.strip().removeprefix("```json").removeprefix("```").removesuffix("```")
    summary = json.loads(content)
    missing = KEYS - summary.keys()
    if missing:
        raise ValueError(f"要約に {sorted(missing)} がない")
    # ToDo がないとき、作業内容が「不明」の項目を入れてくることがある
    summary["todos"] = [t for t in summary["todos"] if t.get("task", "").strip() not in ("", "不明", "なし")]
    return summary


def chunk_lines(text: str, size: int = CHUNK_CHARS) -> list[str]:
    """行の途中で切らずに、size 文字前後のチャンクに分ける。"""
    chunks: list[str] = []
    current = ""
    for line in text.splitlines(keepends=True):
        if current and len(current) + len(line) > size:
            chunks.append(current)
            current = ""
        current += line
    if current:
        chunks.append(current)
    return chunks


def _chat(system: str, user: str) -> dict:
    # 閉じ括弧の書き忘れなどで壊れた JSON が返ることがある。同じ温度だと同じ誤りを繰り返すため、再試行ごとに上げる。
    # Ollama の再起動などで接続が切れたときも、少し待って再試行する
    error: Exception | None = None
    for temperature in [0.2, 0.5, 0.8]:
        body = {
            "model": MODEL,
            "messages": [{"role": "system", "content": system + JSON_INSTRUCTION}, {"role": "user", "content": user}],
            "format": "json",
            "think": False,
            "stream": False,
            # num_predict: 出力が止まらなくなったときの上限。通常の出力は 400〜900 トークン
            "options": {"num_ctx": 16384, "num_predict": 1500, "temperature": temperature},
        }
        req = urllib.request.Request(OLLAMA_URL, data=json.dumps(body).encode(), headers={"Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=600) as res:
                content = json.loads(res.read())["message"]["content"]
            return parse_summary(content)
        except OSError as e:  # 接続エラー・タイムアウト
            error = e
            time.sleep(RETRY_WAIT)
        except ValueError as e:  # 壊れた JSON（JSONDecodeError も ValueError）
            error = e
    raise error


def summarize(meeting_dir: Path) -> Path:
    """transcript.json を map-reduce で要約し、meeting_dir/summary.json に書き出す。"""
    terms = dictionary.prompt_block(dictionary.load())
    chunk_prompt = (PROMPTS_DIR / "summarize_chunk.md").read_text() + terms
    merge_prompt = (PROMPTS_DIR / "summarize_merge.md").read_text() + terms

    text = "\n".join(load_lines(meeting_dir)) + "\n"
    partials = [_chat(chunk_prompt, c) for c in chunk_lines(text)]
    summary = partials[0] if len(partials) == 1 else _chat(merge_prompt, json.dumps(partials, ensure_ascii=False))

    out = meeting_dir / "summary.json"
    out.write_text(json.dumps(summary, ensure_ascii=False, indent=2))
    return out
