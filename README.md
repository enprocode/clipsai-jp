# ClipsAI-JP

[![PyPI version](https://badge.fury.io/py/clipsai-jp.svg)](https://badge.fury.io/py/clipsai-jp)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> **注意:** このパッケージは[ClipsAI](https://github.com/ClipsAI/clipsai)の日本語専用フォーク版です。`whisperx`を`faster-whisper`に置き換え、依存関係の問題を解決しています。

## クイックスタート

Clips AIは、長い動画を自動的にクリップに変換するオープンソースのPythonライブラリです。数行のコードで、動画を複数のクリップに分割し、アスペクト比を16:9から9:16にリサイズできます。

> **注意:** Clips AIは、ポッドキャスト、インタビュー、スピーチ、説教などの音声中心のナラティブ動画向けに設計されています。

完全なドキュメントについては、[Clips AI Documentation](https://clipsai.com)をご覧ください。
このライブラリで生成されたクリップの[UIデモ](https://demo.clipsai.com)もご確認いただけます。

### インストール

**前提条件:**
- Python >= 3.9
- [libmagic](https://github.com/ahupp/python-magic?tab=readme-ov-file#debianubuntu)（Windows: `pip install python-magic-bin`、Mac: `brew install libmagic`）
- [ffmpeg](https://github.com/kkroening/ffmpeg-python/tree/master?tab=readme-ov-file#installing-ffmpeg)（Windows: [ffmpeg.org](https://ffmpeg.org/download.html)からダウンロード、Mac: `brew install ffmpeg`）

**推奨:** 依存関係の競合を避けるため、仮想環境（[venv](https://packaging.python.org/en/latest/guides/installing-using-pip-and-virtual-environments/#create-and-use-virtual-environments)など）の使用を強く推奨します。

```bash
pip install clipsai-jp
```

**オプショナル依存関係:**
- GPUメモリ監視: `pip install clipsai-jp[gpu]`
- 開発・テスト用: `pip install clipsai-jp[dev]`

### クリップの作成

```python
from clipsai_jp import ClipFinder, Transcriber

transcriber = Transcriber()
transcription = transcriber.transcribe(audio_file_path="/abs/path/to/video.mp4")

clipfinder = ClipFinder()
clips = clipfinder.find_clips(transcription=transcription)

print("StartTime: ", clips[0].start_time)
print("EndTime: ", clips[0].end_time)
```

**ショート動画（最大60秒）向けの設定:**

```python
# ショート動画用の推奨設定（日本語最適化モデル使用）
clipfinder = ClipFinder(
    min_clip_duration=10,
    max_clip_duration=60,
    cutoff_policy="average",
    embedding_model="japanese",  # 日本語最適化モデル（精度向上）
)
clips = clipfinder.find_clips(transcription=transcription)
```

**Gemini APIを使用して精度を向上させる場合:**

```python
import os

# 環境変数 GEMINI_API_KEY を設定
# export GEMINI_API_KEY="your_api_key_here"  # Linux/Mac
# $env:GEMINI_API_KEY="your_api_key_here"     # Windows PowerShell

# Gemini APIを使用した高精度なクリップ検出
clipfinder = ClipFinder(
    min_clip_duration=10,
    max_clip_duration=60,
    cutoff_policy="average",
    embedding_model="japanese",
    use_gemini=True,  # Gemini APIを使用
    gemini_api_key=os.getenv("GEMINI_API_KEY"),  # 環境変数から取得（推奨）
    gemini_model="gemini-2.5-flash",  # または "gemini-2.5-pro"（高精度）
    gemini_priority=0.7,  # Geminiの提案を70%重視（0.0=TextTilingのみ, 1.0=Geminiのみ）
)
clips = clipfinder.find_clips(transcription=transcription)
```

> **注意:** Gemini APIキーは[Google AI Studio](https://aistudio.google.com/app/apikey)で無料で取得できます。

文字起こしは[faster-whisper](https://github.com/guillaumekln/faster-whisper)を使用して行われます。

### 動画のリサイズ

```python
from clipsai_jp import resize

crops = resize(
    video_file_path="/abs/path/to/video.mp4",
    pyannote_auth_token="pyannote_token",
    aspect_ratio=(9, 16)
)

print("Crops: ", crops.segments)
```

話者分離に[Pyannote](https://github.com/pyannote/pyannote-audio)が使用されるため、Hugging Faceのアクセストークンが必要です（無料）。手順については[Pyannote HuggingFace](https://huggingface.co/pyannote/speaker-diarization-3.0#requirements)ページを参照してください。
