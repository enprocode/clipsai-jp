---
name: test
description: このリポジトリのテストスイートを正しい環境変数付きで実行する。テスト実行、pytest、単一テストの実行を頼まれたときに使用。
---

# テスト実行

このプロジェクトのテストは `.venv` と `MECABRC` 環境変数が必要（pip 版 MeCab が設定ファイルを同梱しないため）。

## 全テスト

```bash
MECABRC=.venv/etc/mecabrc .venv/bin/python -m pytest tests/
```

## 単一ファイル / 単一テスト

```bash
MECABRC=.venv/etc/mecabrc .venv/bin/python -m pytest tests/test_transcribe.py
MECABRC=.venv/etc/mecabrc .venv/bin/python -m pytest tests/test_clip.py::test_clip_finder_config_manager_valid_config
```

## トラブルシューティング

- `ModuleNotFoundError: sentence_transformers` など → `.venv` 未構築。CLAUDE.md の「環境セットアップ」を実行
- `RuntimeError: Could not load libtorchcodec` → pyannote.audio 4.x が入っている。`pip install "pyannote.audio>=3.3.0,<4.0.0"` で3.x系に戻す
- `AttributeError: module 'mediapipe' has no attribute 'solutions'` → mediapipe 0.10.30以降が入っている。`pip install "mediapipe>=0.10.20,<0.10.30"`
- `no such file or directory: /usr/local/etc/mecabrc` → MECABRC 環境変数の指定漏れ
- `ImportError: failed to find libmagic` → `brew install libmagic`（macOS）

期待値: 全テストパス（2026-07時点で73件）。
