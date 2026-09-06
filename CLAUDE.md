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
# pip版mecabはmecabrcを同梱しないため作成が必要（.venv/etc はvenv作成時に存在しない）:
mkdir -p .venv/etc
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
| Python | `>=3.10` | セキュリティ修正済みの nltk / av / transformers / pillow 等が 3.10 以上を要求 |
| torch / torchaudio | `<2.9.0` | torchaudio 2.9 で AudioMetaData が削除 |
| pyannote.audio | `>=3.3.0,<4.0.0` | 4.x は torchcodec>=0.7 を要求し torch<2.9 と ABI 衝突（import 不能） |
| pyannote.core | `<6.0.0` | pyannote.audio 3.x が pyannote.core<6.0 を要求 |
| mediapipe | `>=0.10.20,<0.10.30` | 0.10.30 でレガシー solutions API（顔検出で使用）が削除 |
| numpy | `<2.0.0` | mediapipe が numpy<2 を要求 |
| opencv-python | `>=4.5.0,<4.12.0` | 4.12+ / 5.x は numpy>=2 を要求し mediapipe と衝突（#63） |
| av | `>=17.1.0,<18.0.0` | 17.1.0 は CVE-2026-40962 対応の FFmpeg 8.1.1 をバンドル。18.x は Python >=3.11 |
| nltk | `>=3.10.3,<4.0.0` | 3.10.3 未満には pickle RCE / SSRF / path traversal |
| transformers | `>=5.16.1,<6.0.0` | 4.x には RCE 等の未修正 CVE。sentence-transformers 5.x は `<6` |
| protobuf | mediapipe が `<5` | CVE-2026-0994 の修正は protobuf 6.x。mediapipe 0.10.21 が protobuf<5 を要求するため未適用 |

依存を追加・変更する場合は `setup.py` と `requirements.txt` の**両方**を更新する。Dependabot がこれらの上限を超える更新を提案しても解決不能なので、`.github/dependabot.yml` の ignore ルールで抑止済み。

**torch の既知 CVE について（意図的に未対応）**: torch 2.8.x には未修正または 2.9+ でしか直らない CVE がある（CVE-2025-2999 [medium] unpack_sequence / CVE-2025-3001 [low] lstm_cell / CVE-2025-3000 [low] jit.script、ほか CVE-2025-55551 / CVE-2025-55552 / CVE-2025-55554 / CVE-2026-4538 / CVE-2026-24747）。修正版（2.9.1 / 2.10.0）は上記 `torch<2.9` ピンの外側にあり、取り込むには torchaudio 2.9・pyannote.audio 4.x への移行が必要。いずれも「特定の torch 内部関数に攻撃者が細工した入力を渡せる場合」のローカルなメモリ破損で、本ライブラリの用途（ユーザー自身の動画処理）では実効リスクが低いため tolerable risk として受容している。**torch のピンを外して "CVE を直す" と依存全体が壊れるので注意**。将来 pyannote 4.x へ移行する際にまとめて見直すこと。

**その他の残存リスク**:
- **nltk CVE-2026-81726**（high）: 3.10.3 時点で修正版なし。model-artifact API が pathsec を迂回する問題。本ライブラリは `sent_tokenize` と `punkt` ダウンロードのみ使用し、当該 API は呼ばない。
- **protobuf CVE-2026-0994**: 修正は protobuf 6.x。mediapipe が protobuf<5 を要求するため未適用。JSON 再帰の DoS。顔検出パイプラインでは攻撃者が protobuf JSON を直接渡す経路がない。
- **PyAV / FFmpeg PixelSmash (CVE-2026-8461)**: 修正は FFmpeg 8.1.2。av 17.1.0 は 8.1.1 バンドル。av 18.x は Python >=3.11 のため未適用。システム ffmpeg（CI は apt）側の更新も別途必要。

## コーディング規約（.cursorrules より要点）

- docstring は NumPy スタイル（Parameters / Returns セクション）
- `print` ではなく `logging` を使用
- 例外は各モジュールの `exceptions.py` にあるカスタム例外を使用
- NLTK リソースは `punkt` と `punkt_tab` の両方をダウンロードする処理を含める

## リリース（PyPI）

- バージョンはリポジトリ直下の **`VERSION` ファイルで一元管理**（setup.py・CI・`clipsai_jp.__version__` すべてここから読む）。リリース時は `VERSION` と `CHANGELOG.md` のみ更新する
- バージョンは一意（同一バージョンの再アップロード不可）
- ブランチ運用: バージョンブランチ（例 `v1.0.6`）→ PR → main マージ
- **リリースは全自動**: `VERSION` を上げて main にマージ → Tests 成功後に TestPyPI 公開、さらに GitHub Release（`v<VERSION>`）の自動作成 → 本番 PyPI 公開（`python-publish.yml`）。いずれも既存バージョンはスキップ（冪等）。手動の twine upload や Release 作成は不要
- 本番公開を手動承認にしたい場合は `pypi` 環境に Required reviewers を設定する
- 詳細は `release` スキル参照
