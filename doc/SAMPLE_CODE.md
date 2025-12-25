# ClipsAI サンプルコード

このドキュメントでは、ClipsAIライブラリの使用方法を示すサンプルコードについて説明します。

## 前提条件

### Pythonのインストール

ClipsAIを使用するには、**Python 3.9以上**が必要です。

#### Pythonのバージョン確認

```bash
python --version
```

または

```bash
python3 --version
```

#### Pythonのインストール

Pythonがインストールされていない場合、またはバージョンが古い場合は、以下のサイトから最新版をダウンロードしてインストールしてください：

- **Windows/Mac**: [python.org](https://www.python.org/downloads/)
- **Linux**: パッケージマネージャーを使用
  ```bash
  # Ubuntu/Debian
  sudo apt update
  sudo apt install python3 python3-pip python3-venv
  ```

### 仮想環境の設定（推奨）

依存関係の競合を避けるため、**仮想環境の使用を強く推奨します**。

#### Windows

```bash
# 仮想環境の作成
python -m venv venv

# 仮想環境の有効化
venv\Scripts\activate

# 仮想環境の無効化（作業終了時）
deactivate
```

#### Mac/Linux

```bash
# 仮想環境の作成
python3 -m venv venv

# 仮想環境の有効化
source venv/bin/activate

# 仮想環境の無効化（作業終了時）
deactivate
```

#### 仮想環境の確認

仮想環境が有効になっている場合、プロンプトの前に `(venv)` が表示されます：

```bash
(venv) C:\Users\YourName\clipsai>
```

## セットアップ方法

> **重要**: 以下の手順を実行する前に、仮想環境を有効化してください。

### pipのアップグレード（推奨）

最新のpipを使用することを推奨します：

```bash
python -m pip install --upgrade pip
```

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

## サンプルファイル一覧

### 1. `sample/clip_video.py`
動画からクリップを見つける基本的なサンプルです。
- 動画を文字起こし
- トランスクリプトからクリップを検出
- クリップの開始時間と終了時間を表示

**使用方法:**
```bash
python sample/clip_video.py
```

### 2. `sample/resize_video.py`
動画を指定したアスペクト比にリサイズするサンプルです。
- 動画を9:16（縦型）などのアスペクト比にリサイズ
- 話者分離と顔検出を使用して最適なクロップ位置を計算

**注意:** この機能を使用するには、Hugging FaceのPyannoteアクセストークンが必要です。
トークンの取得方法: https://huggingface.co/pyannote/speaker-diarization-3.0

**使用方法:**
```bash
python sample/resize_video.py
```

### 3. `sample/complete_example.py`
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

- すべてのサンプルコードで、`video_file_path` を実際の動画ファイルのパスに変更してください
- リサイズ機能を使用する場合は、`pyannote_auth_token` を実際のトークンに変更してください
- 処理には時間がかかる場合があります（特に長い動画の場合）

## 詳細情報

完全なドキュメントについては、[Clips AI Documentation](https://clipsai.com)をご覧ください。

