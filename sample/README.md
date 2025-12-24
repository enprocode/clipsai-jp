# ClipsAI サンプルコード

このディレクトリには、ClipsAIライブラリの使用方法を示すサンプルコードが含まれています。

## セットアップ方法

### 方法1: PyPIからインストール（本番環境）

```bash
pip install clipsai
pip install whisperx@git+https://github.com/m-bain/whisperx.git
```

### 方法2: 開発モードでインストール（ローカル開発）

プロジェクトルートで以下のコマンドを実行：

```bash
pip install -e .
```

これにより、ローカルでビルドしたclipsaiパッケージが開発モードでインストールされ、
コードの変更が即座に反映されます。

## ファイル一覧

### 1. `clip_video.py`
動画からクリップを見つける基本的なサンプルです。
- 動画を文字起こし
- トランスクリプトからクリップを検出
- クリップの開始時間と終了時間を表示

**使用方法:**
```bash
python sample/clip_video.py
```

### 2. `resize_video.py`
動画を指定したアスペクト比にリサイズするサンプルです。
- 動画を9:16（縦型）などのアスペクト比にリサイズ
- 話者分離と顔検出を使用して最適なクロップ位置を計算

**注意:** この機能を使用するには、Hugging FaceのPyannoteアクセストークンが必要です。
トークンの取得方法: https://huggingface.co/pyannote/speaker-diarization-3.0

**使用方法:**
```bash
python sample/resize_video.py
```

### 3. `complete_example.py`
ClipsAIの全機能を使用する完全なサンプルです。
- 文字起こし
- クリップ検出
- 動画リサイズ（オプション）

**使用方法:**
```bash
python sample/complete_example.py
```

## その他の依存関係

1. **libmagic**
   - Windows: `pip install python-magic-bin`
   - Mac: `brew install libmagic`

2. **ffmpeg**
   - Windows: [ffmpeg.org](https://ffmpeg.org/download.html)からダウンロードするか、`choco install ffmpeg`
   - Mac: `brew install ffmpeg`

3. **Pyannoteアクセストークン（リサイズ機能を使用する場合）**
   - https://huggingface.co/pyannote/speaker-diarization-3.0 でトークンを取得

## 注意事項

- すべてのサンプルコードで、`video_file_path` を実際の動画ファイルの絶対パスに変更してください
- リサイズ機能を使用する場合は、`pyannote_auth_token` を実際のトークンに変更してください
- 処理には時間がかかる場合があります（特に長い動画の場合）

## 詳細情報

完全なドキュメントについては、[Clips AI Documentation](https://clipsai.com)をご覧ください。

