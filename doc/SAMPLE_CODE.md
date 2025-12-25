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
pip install clipsai-jp
```

**注意:** このパッケージは元の`clipsai`の日本語専用フォーク版です。`faster-whisper`を使用しており、依存関係の問題を解決しています。

### 方法2: 開発モードでインストール（ローカル開発）

プロジェクトルートで以下のコマンドを実行：

```bash
# 基本的な開発モードインストール
pip install -e .

# 開発ツール（pytest、black、flake8など）も含めてインストールする場合
pip install -e .[dev]
```

これにより、ローカルでビルドしたclipsai-jpパッケージが開発モードでインストールされ、
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

## オプショナル依存関係

ClipsAIには、オプショナルな依存関係がいくつかあります。これらは通常の使用には必要ありませんが、特定の機能を使用する場合や開発を行う場合に必要になります。

### GPUメモリ監視機能（`clipsai-jp[gpu]`）

GPUメモリの詳細な統計情報を取得する場合にインストールします：

**PyPIからインストールする場合:**
```bash
pip install clipsai-jp[gpu]
```

**ローカル開発の場合:**
```bash
pip install -e .[gpu]
```

このオプションには以下のパッケージが含まれます：
- `pynvml`: NVIDIA GPUメモリ監視

**注意**: `pynvml`がインストールされていない場合でも、基本的なGPUメモリ情報は`torch.cuda`を使用して取得されます。

### 開発・テスト用パッケージ（`clipsai-jp[dev]`）

開発やテストを行う場合にインストールします：

**PyPIからインストールする場合:**
```bash
pip install clipsai-jp[dev]
```

**ローカル開発の場合:**
```bash
pip install -e .[dev]
```

このオプションには以下のパッケージが含まれます：
- `pytest`: テストフレームワーク
- `pandas`: テスト用データ処理
- `matplotlib`: 開発用可視化
- `black`, `flake8`: コードフォーマッターとリンター
- `ipykernel`, `build`, `twine`: その他の開発ツール

### 複数のオプションを同時にインストール

複数のオプションを同時にインストールする場合：

**PyPIからインストールする場合:**
```bash
pip install clipsai-jp[gpu,dev]
```

**ローカル開発の場合:**
```bash
pip install -e .[gpu,dev]
```

## 依存関係のトラブルシューティング

### 依存関係の競合エラーが発生した場合

インストール時に依存関係の競合エラーが表示される場合、以下の手順で解決できます：

#### 1. 仮想環境を再作成（推奨）

```bash
# 仮想環境を削除
deactivate
rm -rf venv  # Mac/Linux
rmdir /s venv  # Windows

# 新しい仮想環境を作成
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux

# 依存関係を再インストール
pip install --upgrade pip
pip install -e .
```

#### 2. 互換性のあるバージョンを明示的にインストール

```bash
# faster-whisper は numpy>=1.24.0 を要求（より柔軟なバージョン制約）
# torch は pyannote.audio の要件に合わせて設定（pyannote.audio 3.3.0+ は torch>=2.0.0 を要求）
pip install "numpy>=1.24.0,<2.1.0" "torch>=2.0.0,<3.0.0"

# その後、clipsai-jpを再インストール
pip install -e .
```

#### 3. 既存のパッケージをアンインストールして再インストール

```bash
# 競合しているパッケージをアンインストール
pip uninstall numpy torch torchaudio torchvision facenet-pytorch -y

# faster-whisper と pyannote.audio の要件を満たすバージョンをインストール
pip install "numpy>=1.24.0,<2.1.0" "torch>=2.0.0,<3.0.0"

# clipsai-jpを再インストール
pip install -e .
```

### よくあるエラー

- **`numpy` のバージョン競合**: `faster-whisper`は`numpy>=1.24.0`を要求します（`numpy 2.x`もサポート）。以前は`whisperx`が`numpy>=2.0.2,<2.1.0`を要求していましたが、`faster-whisper`はより柔軟なバージョン制約を持っています。
- **`torch` のバージョン競合**: `pyannote.audio`は`torch>=2.0.0`を要求します。`faster-whisper`は`torch`に依存していないため、依存関係の競合が少なくなっています。
- **`torchvision` のバージョン競合**: `torchvision`は`facenet-pytorch`の依存関係としてインストールされていましたが、`facenet-pytorch`を削除したため、`torchvision`も不要になりました。他のパッケージが`torchvision`を要求する場合は、`torch`と互換性のあるバージョンをインストールしてください。

## 注意事項

- すべてのサンプルコードで、`video_file_path` を実際の動画ファイルのパスに変更してください
- リサイズ機能を使用する場合は、`pyannote_auth_token` を実際のトークンに変更してください
- 処理には時間がかかる場合があります（特に長い動画の場合）

## 詳細情報

完全なドキュメントについては、[Clips AI Documentation](https://clipsai.com)をご覧ください。

