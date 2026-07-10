# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## プロジェクト概要

ClipsAI-JP は長い動画を自動的にクリップに変換する Python ライブラリの**日本語専用フォーク版**。オリジナルの [ClipsAI/clipsai](https://github.com/ClipsAI/clipsai) は2024年1月で更新停止しており、**upstream への追従（sync/merge）はしない**。whisperx を faster-whisper に置き換え、MeCab による日本語文分割を独自実装している。

- パッケージ名は `clipsai_jp`（`clipsai` ではない）。テストのモックパスも `clipsai_jp.` で始めること
- 回答・コミュニケーションは日本語

## コマンド

```bash
# テスト実行（.venv と MECABRC が必要 — 下記「環境」参照）
MECABRC=.venv/etc/mecabrc .venv/bin/python -m pytest tests/

# 単一テスト
MECABRC=.venv/etc/mecabrc .venv/bin/python -m pytest tests/test_clip.py::test_texttiler_config_manager_valid_config

# フォーマット / リント（Black line-length=88、flake8 は E203,E502,W503,W504 を無視 — setup.cfg 参照）
.venv/bin/black clipsai_jp tests
.venv/bin/flake8 clipsai_jp tests
```

### 環境セットアップ

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/pip install "mecab>=0.996.0" unidic-lite
# pip版mecabはmecabrcを同梱しないため作成が必要:
printf 'dicdir = %s\n' "$(.venv/bin/python -c 'import unidic_lite; print(unidic_lite.DICDIR)')" > .venv/etc/mecabrc
# macOSでは brew install libmagic ffmpeg も必要（CIではapt-getで導入）
```

## アーキテクチャ

処理パイプライン: **Transcriber → Transcription → ClipFinder →（オプションで）Resizer / MediaEditor**

1. **`transcribe/transcriber.py`** — faster-whisper で文字起こしし、単語タイムスタンプから**文字単位のタイムスタンプ（char_info）を合成**する。char_info がこのライブラリ全体の一次データ
2. **`transcribe/transcription.py`** — char_info から word_info / sentence_info を派生構築。言語が `ja` なら `JapaneseSentenceSplitter`（MeCab）で文分割、失敗時は NLTK にフォールバック。時間→インデックス変換（`find_char_index` 等）は二分探索
3. **`clip/clipfinder.py`** — 文の埋め込み（sentence-transformers）に対して TextTiling を複数の窓幅 k で繰り返し、クリップ境界を検出。`use_gemini=True` なら `gemini_clipfinder.py` の提案と重み付きマージ
4. **`resize/resizer.py`** — pyannote（話者分離）+ mediapipe（顔検出）+ scenedetect で 9:16 等へのリサイズ用クロップを決定
5. **`media/editor.py`** — ffmpeg ベースの切り出し・変換

### 全体に効く不変条件

- **文分割は元テキストの完全な部分文字列を返すこと**。sentence_info の start_char/end_char は char_info のインデックスであり、これが崩れるとタイムスタンプ⇔テキストのマッピング全体が壊れる（`JapaneseSentenceSplitter` が strip 等で文字列を加工しないのはこのため）
- **char_info の時間区間はソート済み・非重複であること**。`Transcription._find_index` の二分探索がこの前提に依存
- クリップの start_time/end_time を変更したら、対応する start_char/end_char も `find_char_index` で再計算すること

### 依存関係の制約（緩めると壊れる）

| パッケージ | 制約 | 理由 |
|---|---|---|
| torch / torchaudio | `<2.9.0` | torchaudio 2.9 で AudioMetaData が削除 |
| pyannote.audio | `>=3.3.0,<4.0.0` | 4.x は torchcodec>=0.7 を要求し torch<2.9 と ABI 衝突（import 不能） |
| mediapipe | `>=0.10.20,<0.10.30` | 0.10.30 でレガシー solutions API（顔検出で使用）が削除 |

依存を追加・変更する場合は `setup.py` と `requirements.txt` の**両方**を更新する。

## コーディング規約（.cursorrules より要点）

- docstring は NumPy スタイル（Parameters / Returns セクション）
- `print` ではなく `logging` を使用
- 例外は各モジュールの `exceptions.py` にあるカスタム例外を使用
- NLTK リソースは `punkt` と `punkt_tab` の両方をダウンロードする処理を含める

## リリース（PyPI）

- `setup.py` のバージョンは一意（同一バージョンの再アップロード不可）
- `python -m build` でビルド、公開前に TestPyPI で動作確認
- 再ビルド前に `dist/` を削除
- ブランチ運用: バージョンブランチ（例 `v1.0.4`）→ PR → main マージの実績あり
