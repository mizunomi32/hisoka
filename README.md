# hisoka

会議の録音・文字起こし・話者分離・要約・Obsidianへの保存までを、MacBook Pro（Apple Silicon）上ですべてローカルで完結させる個人用アプリ。音声も文字起こしも外部サービスに送らない。

## 状態

設計段階。実装はまだない。

## 構成（予定）

録音 → 文字起こし → 話者分離 → マージ → 要約 → Obsidian 出力 の順に、録音停止後にバックグラウンドで実行する。

- 言語: Python
- 録音: sounddevice + soundfile（オンライン会議は BlackHole 2ch 経由）
- 文字起こし: mlx-whisper（whisper-large-v3-turbo）
- 話者分離: pyannote.audio
- 要約: Ollama + qwen3.5 9B
- UI: rumps（メニューバー常駐）

## ドキュメント

- [設計](docs/design.md)
