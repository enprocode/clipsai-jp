# ClipsAI-JP

[![PyPI version](https://badge.fury.io/py/clipsai-jp.svg)](https://badge.fury.io/py/clipsai-jp)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> **注意:** このパッケージは[ClipsAI](https://github.com/ClipsAI/clipsai)の日本語専用フォーク版です。
> - 元の`whisperx`を`faster-whisper`に置き換え、依存関係の問題を解決
> - 日本語環境での使用に最適化
> - 元のプロジェクト: https://github.com/ClipsAI/clipsai

## クイックスタート

Clips AIは、長い動画を自動的にクリップに変換するオープンソースのPythonライブラリです。数行のコードで、動画を複数のクリップに分割し、アスペクト比を16:9から9:16にリサイズできます。

> **注意:** Clips AIは、ポッドキャスト、インタビュー、スピーチ、説教などの音声中心のナラティブ動画向けに設計されています。動画のトランスクリプトを積極的に活用してクリップを識別・作成します。リサイズアルゴリズムは、現在話している話者に動的にフォーカスし、動画を様々なアスペクト比に変換します。

完全なドキュメントについては、[Clips AI Documentation](https://clipsai.com)をご覧ください。
このライブラリで生成されたクリップの[UIデモ](https://demo.clipsai.com)もご確認いただけます。

### インストール

1. Pythonの依存関係をインストールします。 <br></br> *依存関係の競合を避けるため、仮想環境（[venv](https://packaging.python.org/en/latest/guides/installing-using-pip-and-virtual-environments/#create-and-use-virtual-environments)など）の使用を強く推奨します*
    ```bash
    pip install clipsai-jp
    ```

    **注意:** このパッケージは元の[ClipsAI](https://github.com/ClipsAI/clipsai)の日本語専用フォーク版です。`faster-whisper`を使用しており、依存関係の問題を解決しています。

    **オプショナル依存関係:**
    
    - **GPUメモリ監視機能を使用する場合:**
      ```bash
      pip install clipsai-jp[gpu]
      ```
    
    - **開発・テスト用パッケージをインストールする場合:**
      ```bash
      pip install clipsai-jp[dev]
      ```

2. [libmagic](https://github.com/ahupp/python-magic?tab=readme-ov-file#debianubuntu)をインストールします
   - **Windows**: [python-magic-binaries](https://github.com/pidydx/libmagicwin64)からダウンロードするか、`pip install python-magic-bin`を使用
   - **Mac**: Homebrewでインストール: `brew install libmagic`

3. [ffmpeg](https://github.com/kkroening/ffmpeg-python/tree/master?tab=readme-ov-file#installing-ffmpeg)をインストールします
   - **Windows**: [ffmpeg.org](https://ffmpeg.org/download.html)からダウンロードするか、`choco install ffmpeg`を使用
   - **Mac**: Homebrewでインストール: `brew install ffmpeg`

### 要件

- Python >= 3.9
- すべての依存関係はバージョン制約付きで自動インストールされます
- 開発用の依存関係については`requirements.txt`を参照してください

### クリップの作成

クリップは動画のトランスクリプトを使用して見つけられるため、まず動画を文字起こしする必要があります。文字起こしは[faster-whisper](https://github.com/guillaumekln/faster-whisper)を使用して行われます。これは[Whisper](https://github.com/openai/whisper)の高速実装版で、CTranslate2を使用して高速化されています。各単語の開始時刻と終了時刻を検出する機能を備えています。元の動画を選択したクリップにトリミングするには、クリッピングリファレンスを参照してください。

```python
from clipsai import ClipFinder, Transcriber

transcriber = Transcriber()
transcription = transcriber.transcribe(audio_file_path="/abs/path/to/video.mp4")

clipfinder = ClipFinder()
clips = clipfinder.find_clips(transcription=transcription)

print("StartTime: ", clips[0].start_time)
print("EndTime: ", clips[0].end_time)
```

### 動画のリサイズ

動画をリサイズするには、話者分離に[Pyannote](https://github.com/pyannote/pyannote-audio)が使用されるため、Hugging Faceのアクセストークンが必要です。Pyannoteの使用に料金はかかりません。手順については[Pyannote HuggingFace](https://huggingface.co/pyannote/speaker-diarization-3.0#requirements)ページを参照してください。元の動画を希望のアスペクト比にリサイズするには、リサイズリファレンスを参照してください。

```python
from clipsai import resize

crops = resize(
    video_file_path="/abs/path/to/video.mp4",
    pyannote_auth_token="pyannote_token",
    aspect_ratio=(9, 16)
)

print("Crops: ", crops.segments)
```
