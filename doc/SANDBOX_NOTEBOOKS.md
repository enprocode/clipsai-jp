# Sandbox ノートブック 実行ガイド

このドキュメントでは、`sandbox/`ディレクトリ内のJupyterノートブックファイルの使用方法について説明します。

## 概要

`sandbox/`ディレクトリには、ClipsAI-JPの機能をテスト・実験するためのノートブックファイルが含まれています。これらのノートブックは、ライブラリの内部動作を理解したり、カスタマイズしたりする際に役立ちます。

## 前提条件

### 1. 必要なソフトウェア

- **Python 3.9以上**
- **Jupyter Notebook** または **JupyterLab**
- **開発モードでインストールされたclipsai-jp**

### 2. インストール手順

```bash
# 仮想環境の作成（推奨）
python -m venv venv

# 仮想環境の有効化
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# 開発モードでインストール
pip install -e .[dev]

# Jupyter Notebookのインストール（未インストールの場合）
pip install jupyter notebook

# Jupyter Notebookの起動
jupyter notebook
```

### 3. 環境変数の設定

リサイズ機能を使用する場合は、Hugging FaceのPyannoteアクセストークンが必要です。

```bash
# Windows
set PYANNOTE_AUTH_TOKEN=your_token_here

# Mac/Linux
export PYANNOTE_AUTH_TOKEN="your_token_here"
```

トークンの取得方法: [Pyannote HuggingFace](https://huggingface.co/pyannote/speaker-diarization-3.0#requirements)

## ノートブックファイル一覧

### 1. `clipsai.ipynb`

**目的**: ClipsAI-JPの主要機能（リサイズ、文字起こし、クリップ検出）を統合的に使用する完全なワークフローを実行するノートブック。

**主な内容**:
- 動画のリサイズ（9:16アスペクト比への変換）
- 動画の文字起こし
- 文字起こし結果からのクリップ検出
- リサイズ動画とクリップ動画の保存

**使用方法**:
1. ノートブックを開く
2. 「Data」セクションで動画ファイルパスを指定
3. 環境変数`PYANNOTE_AUTH_TOKEN`を設定（リサイズ機能を使用する場合）
4. セルを順番に実行

**主要なセクション**:
- **Setup**: パス設定とautoreloadの有効化
- **Data**: 動画ファイルパスと認証トークンの設定
- **Resize**: 動画のリサイズ処理
- **Transcribe**: 動画の文字起こし処理
- **Clip**: 文字起こし結果からのクリップ検出

### 2. `resizer.ipynb`

**目的**: リサイズ機能の詳細なテストと実験を行うノートブック。内部処理を理解するために使用します。

**主な内容**:
- `Resizer`クラスの使用方法
- シーン検出（`detect_scenes`）
- 話者分離（`PyannoteDiarizer`）
- 顔検出とMediaPipe Face Meshの使用
- リサイズセグメントの可視化
- k-meansクラスタリングによる顔分類

**使用方法**:
1. ノートブックを開く
2. 環境変数`PYANNOTE_AUTH_TOKEN`を設定
3. セルを順番に実行

**主要なセクション**:
- **Setup**: パス設定、ロギング設定、インポート
- **Data**: 認証トークンとテストファイルの設定
- **detect_scenes**: シーン検出の実行
- **diarize**: 話者分離の実行
- **resize**: リサイズ処理の実行
- **Sandbox**: フレーム抽出、顔検出、MediaPipeランドマーク検出の実験

**注意事項**:
- このノートブックは内部APIを使用しており、将来的に変更される可能性があります
- `tests.test_files`モジュールを使用しているため、テスト環境が必要です

### 3. `transcribe.ipynb`

**目的**: 文字起こし機能の詳細なテストと実験を行うノートブック。

**主な内容**:
- `Transcriber`クラスの使用方法
- `transcribe()`メソッドの実行
- 文字レベル、単語レベル、文レベルの情報取得
- 文字起こし結果の保存（JSON形式）
- 言語検出（`detect_language()`）

**使用方法**:
1. ノートブックを開く
2. セルを順番に実行

**主要なセクション**:
- **Setup**: パス設定、ロギング設定、インポート
- **transcribe()**: 文字起こしの実行
- **transcription getter functions**: 文字起こし結果の各種情報取得
- **detect_language()**: 言語検出の実行

**注意事項**:
- このノートブックは内部APIを使用しており、将来的に変更される可能性があります
- `tests.test_files`モジュールを使用しているため、テスト環境が必要です

## 共通の設定

### パスの設定

すべてのノートブックでは、プロジェクトのルートディレクトリをPythonのパスに追加します：

```python
import sys, os

ROOT_PATH = os.path.abspath(os.path.join(".."))
sys.path.insert(0, ROOT_PATH)
```

これにより、開発モードでインストールされていない場合でも、ローカルの`clipsai_jp`パッケージをインポートできます。

### Autoreloadの設定

開発中にコードの変更を自動的に反映させるため、`autoreload`拡張機能を使用します：

```python
%load_ext autoreload
%autoreload 2
```

### インポートパス

すべてのノートブックでは、`clipsai_jp`パッケージを使用します：

```python
# パッケージから直接インポート（推奨）
from clipsai_jp import ClipFinder, Transcriber, resize

# または、モジュールから直接インポート
from clipsai_jp.transcribe.transcriber import Transcriber
from clipsai_jp.resize.resizer import Resizer
```

## トラブルシューティング

### インポートエラーが発生する場合

1. **開発モードでインストールされているか確認**:
   ```bash
   pip install -e .
   ```

2. **仮想環境が有効化されているか確認**:
   ```bash
   # Windows
   venv\Scripts\activate
   
   # Mac/Linux
   source venv/bin/activate
   ```

3. **Jupyter Notebookのカーネルが正しい環境を使用しているか確認**:
   - Jupyter Notebook起動時に、仮想環境が有効化されていることを確認
   - または、カーネルを明示的に選択

### 認証トークンエラーが発生する場合

リサイズ機能を使用する場合、環境変数`PYANNOTE_AUTH_TOKEN`が設定されている必要があります：

```bash
# Windows
set PYANNOTE_AUTH_TOKEN=your_token_here

# Mac/Linux
export PYANNOTE_AUTH_TOKEN="your_token_here"
```

環境変数が設定されていない場合、ノートブックではプレースホルダー値`"your_pyannote_token_here"`が使用されますが、これは実行時にエラーになります。

### 依存関係エラーが発生する場合

必要なパッケージがインストールされていない場合、エラーメッセージにインストール方法が表示されます。例：

```
ImportError: opencv-python is required. Install it with: pip install opencv-python
```

すべての依存関係をインストールするには：

```bash
pip install -e .[dev]
```

### テストファイルが見つからない場合

`resizer.ipynb`や`transcribe.ipynb`では、`tests.test_files`モジュールを使用しています。テストファイルが必要な場合は、リポジトリの`tests/`ディレクトリが存在することを確認してください。

## サンプルコードとの違い

`sandbox/`ディレクトリのノートブックは、`sample/`ディレクトリのサンプルコード（`.py`ファイル）とは以下の点で異なります：

1. **目的**: 
   - `sample/`: 本番環境で使用できる実用的なサンプル
   - `sandbox/`: 開発・テスト・実験用のノートブック

2. **内部APIの使用**:
   - `sample/`: 公開APIのみを使用
   - `sandbox/`: 内部APIも使用（将来的に変更される可能性あり）

3. **可視化とデバッグ**:
   - `sample/`: シンプルな出力
   - `sandbox/`: 詳細な可視化、デバッグ情報、中間結果の表示

4. **テストデータ**:
   - `sample/`: ユーザーが指定したファイルを使用
   - `sandbox/`: テスト用のファイルセットを使用（`tests.test_files`）

## 注意事項

- **開発環境専用**: これらのノートブックは開発・テスト環境での使用を想定しています
- **APIの変更**: 内部APIを使用しているため、将来のバージョンで動作しなくなる可能性があります
- **認証情報**: 認証トークンは環境変数から読み込むようにしており、ハードコードされていません
- **パフォーマンス**: 実験用のため、最適化されていないコードが含まれている可能性があります

## 関連ドキュメント

- [サンプルコード](./SAMPLE_CODE.md): 実用的なサンプルコードの使用方法
- [README](../README.md): プロジェクトの概要とインストール方法
- [CHANGELOG](./CHANGELOG.md): 変更履歴

