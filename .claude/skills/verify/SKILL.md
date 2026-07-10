---
name: verify
description: コード変更が実際に動くことをエンドツーエンドで検証する。コミット前の動作確認、実動画でのパイプライン検証を頼まれたときに使用。
---

# 変更の検証

## 1. ユニットテスト（必須）

```bash
MECABRC=.venv/etc/mecabrc .venv/bin/python -m pytest tests/
```

全件パスすること。詳細は `test` スキル参照。

## 2. エンドツーエンド検証（transcribe / clip 系の変更時）

文字起こし→文分割→クリップ検出の実パイプラインを実際の日本語動画で通す。
CPU では動画実時間の 1/3〜1/2 程度かかるため、長い動画はバックグラウンド実行を推奨。

```python
# PYTHONPATH=<repo> MECABRC=.venv/etc/mecabrc .venv/bin/python で実行
from clipsai_jp import ClipFinder, Transcriber

transcriber = Transcriber()  # CPU: smallモデル/int8 が自動選択される
transcription = transcriber.transcribe(audio_file_path="<動画パス>", iso6391_lang_code="ja")
clips = ClipFinder(min_clip_duration=15, max_clip_duration=300).find_clips(transcription)
```

### 検証すべき不変条件

- `char_info` の時間区間がソート済み・非重複（`end_time < start_time` や前要素との重なりがない）
- `get_sentence_info()` の各 `sentence` が `transcription.text` の部分文字列である
- 各クリップで `0 <= start_time < end_time <= transcription.end_time` かつ `0 <= start_char < end_char <= len(text)`
- クリップが1件以上検出される

## 3. リサイズ系の変更時

`Resizer` は pyannote の学習済みモデル（HuggingFace トークンが必要）に依存するため、
ローカル検証が難しければユニットテスト（tests/test_resize.py）までで可。その旨を報告すること。
