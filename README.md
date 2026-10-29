# hisoka

会議の録音・文字起こし・要約・Markdownでの保存までを、MacBook Pro（Apple Silicon）上ですべてローカルで完結させる個人用アプリ。音声も文字起こしも外部サービスに送らない。

## 状態

試作段階。録音済みの音声ファイルから、文字起こし → 要約 → Markdown ノートまでを CLI で実行できる。録音とメニューバー UI はまだない。

## 必要なもの

- Apple Silicon の Mac
- [uv](https://docs.astral.sh/uv/)
- ffmpeg（`brew install ffmpeg`）
- [Ollama](https://ollama.com/) と要約モデル（`ollama pull gemma4:e4b`）

```sh
uv sync
```

文字起こしモデル（whisper-large-v3-turbo、約1.6GB）は初回実行時に自動でダウンロードされる。

## 使い方

会議ごとにフォルダを作り、音声を 16kHz・モノラルの WAV で `audio.wav` として置く。フォルダ名を `YYYY-MM-DD_HHMM` にすると、ノートに日時が入る。

```sh
mkdir -p meetings/2026-10-28_1400
ffmpeg -i 録音.m4a -vn -ac 1 -ar 16000 -c:a pcm_s16le meetings/2026-10-28_1400/audio.wav
```

3つのコマンドを順に実行する。`transcribe` と `summarize` の出力は会議フォルダに残り、どの段からでもやり直せる。

```sh
uv run hisoka transcribe meetings/2026-10-28_1400   # → transcript.json
uv run hisoka summarize  meetings/2026-10-28_1400   # → summary.json（Ollama を起動しておく）
uv run hisoka note       meetings/2026-10-28_1400   # → ~/Documents/mtg/ に書き出す
```

`note` は要約を `~/Documents/mtg/YYYY-MM-DD_HHMM.md`、文字起こしを `~/Documents/mtg/raw/YYYY-MM-DD_HHMM.md` に書き出す。同じ名前があれば `-2` などを付け、上書きしない。

要約の観点や書き方は `prompts/` の Markdown を編集して変えられる。

人名・用語の表記は `~/Documents/mtg/_dictionary/` の `people.md` と `terms.md` に表で登録する（初回の `summarize` / `note` 実行時に空のテンプレートが作られる）。音声認識が間違えやすい表記を書いておくと、文字起こしで正しい表記に置き換わり、要約の表記も揃う。

`meetings/` と音声ファイルは `.gitignore` で除外している。

## テスト

```sh
for t in tests/test_*.py; do uv run python "$t"; done
```

## 構成（予定）

録音 → 文字起こし → 要約 → Markdown 出力 の順に、録音停止後にバックグラウンドで実行する。

- 言語: Python
- 録音: sounddevice + soundfile（オンライン会議は BlackHole 2ch 経由）
- 文字起こし: mlx-whisper（whisper-large-v3-turbo）
- 要約: Ollama + gemma4 E4B
- UI: rumps（メニューバー常駐）

## ドキュメント

- [設計](docs/design.md)
