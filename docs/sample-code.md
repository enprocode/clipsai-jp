# ClipsAI-JP サンプルコード

このドキュメントでは、`clipsai_jp` ライブラリの使用方法を示すサンプルコードについて説明します。LLM クリップ検出の詳細は [llm-clip-finding.md](llm-clip-finding.md) を参照してください。

## 前提条件

### Pythonのインストール

ClipsAI-JPを使用するには、**Python 3.10以上**が必要です。

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
- クリップ動画、字幕ファイル、文字起こしデータを出力

**使用方法:**
```bash
python sample/clip_video.py
```

**出力ファイル:**

このサンプルコードは、元の動画ファイル名を基準とした統一された命名規則で、以下のファイルを出力します。

元の動画ファイルが `test.mp4` の場合の出力例：

**全体の文字起こしデータ:**
- `test_transcription.json` - 全体の文字起こしデータ（JSON形式、タイムスタンプ情報を含む）
- `test_transcription.txt` - 全体の文字起こしテキスト（プレーンテキスト）

**各クリップの出力ファイル（クリップごとに5つのファイル）:**

各クリップ（例：クリップ1）に対して、以下のファイルが生成されます：

1. **クリップ動画**: `test_clip_001.mp4` - トリミングされた動画ファイル
2. **字幕ファイル（SRT形式）**: `test_clip_001.srt` - SubRip字幕形式（動画編集ソフトで使用可能）
3. **字幕ファイル（VTT形式）**: `test_clip_001.vtt` - WebVTT形式（Webプレーヤーで使用可能）
4. **文字起こしデータ（JSON形式）**: `test_clip_001_transcription.json` - クリップの文字起こしデータ（タイムスタンプ、文、文字情報を含む）
5. **文字起こしテキスト**: `test_clip_001_transcription.txt` - クリップの文字起こしテキスト（プレーンテキスト）

**ファイル名の命名規則:**

- 元の動画ファイル名（拡張子を除く）がベース名として使用されます
- クリップファイルは `{元のファイル名}_clip_{番号}` の形式で命名されます
- 例：`my_video.mp4` → `my_video_clip_001.mp4`, `my_video_clip_002.mp4`, ...

**字幕ファイルの特徴:**

- **SRT形式**: 動画編集ソフト（Premiere Pro、Final Cut Pro、DaVinci Resolveなど）で直接使用可能
- **VTT形式**: Webブラウザや動画プレーヤーで使用可能
- 字幕の時間はクリップ開始時刻を0秒にオフセットしているため、クリップ動画と直接組み合わせて使用できます

**出力ディレクトリ:**

すべての出力ファイルは、`sample/output/`ディレクトリに保存されます（デフォルト設定）。

**出力ファイル構造の例:**

3つのクリップが検出された場合の出力例：

```
output/
├── test_transcription.json              # 全体の文字起こし（JSON）
├── test_transcription.txt               # 全体の文字起こし（テキスト）
├── test_clip_001.mp4                    # クリップ1の動画
├── test_clip_001.srt                    # クリップ1の字幕（SRT）
├── test_clip_001.vtt                    # クリップ1の字幕（VTT）
├── test_clip_001_transcription.json     # クリップ1の文字起こし（JSON）
├── test_clip_001_transcription.txt      # クリップ1の文字起こし（テキスト）
├── test_clip_002.mp4                    # クリップ2の動画
├── test_clip_002.srt                    # クリップ2の字幕（SRT）
├── test_clip_002.vtt                    # クリップ2の字幕（VTT）
├── test_clip_002_transcription.json     # クリップ2の文字起こし（JSON）
├── test_clip_002_transcription.txt      # クリップ2の文字起こし（テキスト）
├── test_clip_003.mp4                    # クリップ3の動画
├── test_clip_003.srt                    # クリップ3の字幕（SRT）
├── test_clip_003.vtt                    # クリップ3の字幕（VTT）
├── test_clip_003_transcription.json     # クリップ3の文字起こし（JSON）
└── test_clip_003_transcription.txt      # クリップ3の文字起こし（テキスト）
```

**ファイル名によるデータ管理:**

すべてのファイルが元の動画ファイル名を基準とした統一された命名規則で保存されるため、以下のメリットがあります：

- **ファイルの関連付けが容易**: 同じベース名を持つファイルでグループ化可能
- **元の動画ファイルを特定しやすい**: ファイル名から元の動画ファイルを特定可能
- **複数の動画を処理しても整理しやすい**: 各動画ごとに独立したファイルセットが生成される

**字幕ファイルの使用例:**

生成された字幕ファイル（SRT/VTT）は、以下のような用途で使用できます：

- **動画編集ソフトでの使用**: Premiere Pro、Final Cut Pro、DaVinci Resolveなどで動画に字幕を追加
- **Webプレーヤーでの使用**: VTT形式はHTML5の`<video>`タグで直接使用可能
- **YouTube動画への字幕追加**: SRTファイルをアップロードして字幕として使用

**ClipFinderのパラメータ調整:**

`ClipFinder`には、クリップ検出を調整するためのパラメータがあります。特にショート動画（最大60秒）を作成する場合は、以下の設定を推奨します：

```python
from clipsai_jp import ClipFinder

# ショート動画（最大60秒）向けの推奨設定
clipfinder = ClipFinder(
    min_clip_duration=10,      # 最小クリップ長（秒）
    max_clip_duration=60,      # 最大クリップ長（秒）- ショート動画は60秒以下
    cutoff_policy="average",   # 境界検出の厳しさ: "low"（緩い）/ "average"（標準）/ "high"（厳しい）
    embedding_model="japanese",  # 日本語最適化モデル（ClipFinderのデフォルト）
    max_clips=8,               # 省略時もショートでは上位8件（全件は max_clips=0）
)
```

**パラメータの説明:**
- `min_clip_duration` (デフォルト: 15): クリップの最小長さ（秒）。より短いクリップを検出したい場合は小さな値を設定
- `max_clip_duration` (デフォルト: 900): クリップの最大長さ（秒）。ショート動画の場合は60程度を推奨
- `cutoff_policy` (デフォルト: "high"): トピック境界の検出の厳しさ
  - `"low"`: 緩い検出（多くのクリップが生成される可能性）
  - `"average"`: 標準的な検出（推奨）
  - `"high"`: 厳しい検出（少ないクリップが生成される可能性）
- `embedding_model` (デフォルト: `"japanese"`): テキスト埋め込みに使用するAIモデル
  - `"japanese"`: 日本語最適化モデル（`paraphrase-multilingual-mpnet-base-v2`、推奨・デフォルト）
  - `"default"`: 英語特化モデル（`all-roberta-large-v1`）
  - `"high_accuracy"`: 高精度モデル（`intfloat/multilingual-e5-base`、多言語対応）
  - `"large"`: 最高精度モデル（`intfloat/multilingual-e5-large`、処理時間が長い）
  - 完全なモデル名を直接指定することも可能（例: `"sentence-transformers/paraphrase-multilingual-mpnet-base-v2"`）
- `clip_style` (デフォルト: `"auto"`): `"auto"` は `max_clip_duration<=90` のときショート向け（文連続候補・フック評価・重複抑制）。`"shorts"` で常にショート向け、`"longform"` で従来の TextTiling のみ
- `max_clips` (デフォルト: None): ショート向け処理で返す最大件数。未指定なら 8 件。`0` で重複抑制後の全件

**LLM APIを使用して精度を向上させる場合:**

TextTiling（埋め込みの類似度で境界を切る）に加えて、任意の LLM にトピック境界を提案させると、日本語の意味の切れ目をより自然に取れます。Gemini 専用ではなく、OpenAI / Anthropic / Gemini / OpenAI互換サーバから選べます。プロバイダ別の例・キーの優先順位・`use_gemini` からの移行は [LLM によるクリップ検出](llm-clip-finding.md) にまとめています。

```python
# OpenAI（例）
clipfinder = ClipFinder(
    min_clip_duration=10,
    max_clip_duration=60,
    cutoff_policy="average",
    embedding_model="japanese",
    use_llm=True,
    llm_provider="openai",  # openai / anthropic / gemini / openai_compatible
    llm_model="gpt-5.6-terra",  # 高精度なら "gpt-5.6-sol"
    llm_priority=0.7,  # 0.0=TextTilingのみ, 1.0=LLMのみ
)

# Anthropic
# clipfinder = ClipFinder(
#     ...,
#     use_llm=True,
#     llm_provider="anthropic",
#     llm_model="claude-sonnet-5",
# )

# ローカル LLM（Ollama など OpenAI 互換）
# clipfinder = ClipFinder(
#     ...,
#     use_llm=True,
#     llm_provider="openai_compatible",
#     llm_model="llama3",
#     llm_base_url="http://localhost:11434/v1",
# )
```

**LLM パラメータ:**
- `use_llm` (デフォルト: False): LLM でクリップ境界を補助するかどうか
- `llm_provider`: `"openai"` / `"anthropic"` / `"gemini"` / `"openai_compatible"`
- `llm_api_key` (デフォルト: None): APIキー。未指定時は環境変数から取得（後述）
- `llm_model`: モデル名。未指定時のデフォルトは
  - openai: `gpt-5.6-terra`
  - anthropic: `claude-sonnet-5`
  - gemini: `gemini-3.8-flash`
- `llm_base_url`: API のベースURL。`openai_compatible` では必須
- `llm_priority` (デフォルト: 0.5): LLM提案の重み（0.0-1.0）
  - `0.0`: TextTilingのみ
  - `0.7`: LLMをやや重視（推奨の出発点）
  - `1.0`: LLMのみ

`use_gemini=True` と `gemini_*` は非推奨の互換エイリアスです。内部では `use_llm=True, llm_provider="gemini"` に変換されます。

**精度を上げる順番（効果の大きい順）:**

1. **LLM 補助を使う**（上記）。意味の切れ目・フック・自己完結を LLM が見る
2. **強いモデルを選ぶ**（`gpt-5.6-sol` / `claude-opus-5`）。デフォルトの terra / sonnet / flash より境界の自然さが上がる一方、遅い・高い
3. **埋め込みを上げる**: `embedding_model="high_accuracy"` または `"large"`（TextTiling 側の境界精度）
4. **MeCab を入れる**: 日本語の文境界が正しくなる（クリップが文の途中で切れない）
5. **`llm_priority` を 0.6〜0.8 にする**: TextTiling の安定性と LLM の意味理解を混ぜる
6. **ショートなら `clip_style="shorts"`**（または `max_clip_duration<=90`）: フック評価と重複抑制が乗る

**APIキーの扱い:**

ライブラリはキーをハードコードしません。取得順は次のとおりです。

1. 引数 `llm_api_key=...`（または旧APIの `gemini_api_key`）
2. プロバイダ専用の環境変数
3. 共通フォールバック `LLM_API_KEY`
4. それでも無い場合: `ClipFinder` は警告を出して LLM をオフにし、TextTiling のみで動作する

| プロバイダ | 環境変数 | HTTP への載せ方 |
|---|---|---|
| OpenAI | `OPENAI_API_KEY` | `Authorization: Bearer ...` |
| Anthropic | `ANTHROPIC_API_KEY` | `x-api-key` |
| Gemini | `GEMINI_API_KEY` | `x-goog-api-key` |
| OpenAI互換（Ollama 等） | `LLM_API_KEY`（任意） | キーがあれば Bearer。ローカルならキーなしで可 |

`clipsai_jp` 本体は `.env` を読み込みません。環境変数をセットするか、サンプルのように `python-dotenv` で読み込んでください。ログにはプロバイダ名とモデル名だけ出し、キーは出しません。API 呼び出しに失敗した場合も TextTiling にフォールバックします。

【方法1】.envファイルを使用（サンプル向け・推奨）

`.env`ファイルを使用することで、APIキーをコードから分離して管理できます。

1. サンプルの雛形 `sample/.env.example` をコピーして `sample/.env` を作成:

```bash
cp sample/.env.example sample/.env
```

2. `sample/.env` を開き、**使うプロバイダのキーだけ**書き換える:

```bash
# .env
OPENAI_API_KEY=your_actual_api_key_here
# リサイズ機能を使う場合は Hugging Face トークンも設定
HF_TOKEN=your_actual_huggingface_token_here
```

3. `python-dotenv`パッケージをインストール（オプション、推奨）:

```bash
pip install python-dotenv
```

4. `sample/clip_video.py` などは `.env` を自動読み込みします:

```python
# .envファイルから環境変数を読み込む（オプション）
try:
    from dotenv import load_dotenv
    env_path = os.path.join(os.path.dirname(__file__), ".env")
    load_dotenv(env_path)
except ImportError:
    # python-dotenvがインストールされていない場合は環境変数のみを使用
    pass
```

**注意:** `.env`ファイルは`.gitignore`に含まれているため、リポジトリにコミットされません。実際のAPIキーをコードに直接記述しないでください。

【方法2】環境変数として直接設定

**Linux/Mac:**
```bash
export OPENAI_API_KEY="your_api_key_here"
# または: ANTHROPIC_API_KEY / GEMINI_API_KEY
```

**Windows PowerShell:**
```powershell
$env:OPENAI_API_KEY="your_api_key_here"
```

**Windows コマンドプロンプト:**
```cmd
set OPENAI_API_KEY=your_api_key_here
```

【方法3】引数で渡す（非推奨。ソースやログに残りやすい）

```python
clipfinder = ClipFinder(
    use_llm=True,
    llm_provider="openai",
    llm_api_key=os.environ["OPENAI_API_KEY"],
)
```

**注意:**
- LLM 補助はオプショナルです（`use_llm` のデフォルトは False）。キーが無い、または API 呼び出しに失敗した場合でも TextTiling のみで動作します。
- `sample/clip_video.py` はデモとして `use_llm=True, llm_provider="openai"` になっているため、動かすには `OPENAI_API_KEY` が必要です（未設定なら TextTiling のみ）。
- MeCabもオプショナル機能です。MeCabがインストールされていない場合、自動的にNLTKにフォールバックします。ただし、MeCabをインストールすることで、日本語の文分割精度が向上し、より自然な動画分割が可能になります。

**MeCabによる日本語文分割（自動使用）:**

ClipsAI-JPは、日本語の文字起こしに対して自動的にMeCabを使用して文分割を行います。これにより、より自然で正確な文分割が可能になり、クリップ検出の精度が向上します。

- MeCabがインストールされている場合: 自動的にMeCabを使用して日本語の文構造を考慮した文分割を実行
- MeCabがインストールされていない場合: 自動的にNLTKにフォールバック（既存の動作を維持）
- 元の文字列の空白・改行を保持: MeCabによる文分割では、元の文字列の空白や改行を保持するため、タイムスタンプのマッピングが正確に機能します（改行が句点代わりに使われる字幕でも対応可能）
- MeCabのインストール方法:
  - **全プラットフォーム（推奨）:** `pip install mecab`
    - [PyPIのmecabパッケージ](https://pypi.org/project/mecab/)を使用します
    - MeCab本体も含まれており、システムレベルのインストールは不要です
    - Windows、Mac、Linuxすべてで`pip install`のみで使用可能
  - **Mac/Linux（代替方法）:** システムパッケージマネージャーを使用する場合
    - Mac: `brew install mecab mecab-ipadic`
    - Linux: `sudo apt-get install mecab libmecab-dev mecab-ipadic-utf8`
    - その後、`pip install mecab-python3`でPythonバインディングをインストール

**トラブルシューティング:**
- クリップが1つも見つからない場合: `cutoff_policy="low"`に変更してみてください
- 動画全体が1つのクリップとして返される場合: `cutoff_policy="average"`または`"low"`に変更してください
- より短いクリップが必要な場合: `min_clip_duration`を5-10秒程度に設定してください
- 日本語動画の精度を向上させたい場合: `embedding_model="japanese"`を指定してください
- より高精度な検出が必要な場合: `embedding_model="high_accuracy"`または`"large"`を指定してください（処理時間が長くなります）
- クリップ検出精度を最大限に向上させたい場合: `use_llm=True` で LLM を併用してください
- 日本語の文分割が不自然な場合: MeCabをインストールすることで、より自然な文分割が可能になります（自動的に使用されます）

### 2. `sample/resize_video.py`
動画を指定したアスペクト比にリサイズするサンプルです。
- 動画を9:16（縦型）などのアスペクト比にリサイズ
- 話者分離と顔検出を使用して最適なクロップ位置を計算

**注意:** この機能を使用するには、Hugging Faceのアクセストークンが必要です（取得手順は下記「Hugging Faceトークンの取得方法」を参照）。

**使用方法:**
```bash
python sample/resize_video.py
```

**Hugging Faceトークンの取得方法:**

pyannoteの話者分離モデルは **gated（利用規約への同意が必要）** です。トークンの発行とモデルへの同意は**別の作業**なので、両方行ってください。

1. [Hugging Face](https://huggingface.co/join) でアカウントを作成し、ログインする
2. **アクセストークンを発行する**: [Settings → Access Tokens](https://huggingface.co/settings/tokens) を開いてトークンを作成し、コピーする。トークンタイプは2通り:
   - **Read タイプ（簡単・推奨）**: 上部タブで `Read` を選ぶだけ。同意済みの gated モデルを含め、閲覧可能なリポジトリを一括で読めるトークンになる
   - **Fine-grained タイプ**: `Repositories` の権限で **「Read access to contents of all public gated repos you can access」** に必ずチェックを入れる（pyannote は personal namespace 外の公開 gated モデルのため、「... under your personal namespace」だけでは**アクセスできない**）。Write・Org・Inference 系は不要
3. **モデルの利用規約に同意する**（これを忘れると `401` / gated エラーになります）:
   - [pyannote/speaker-diarization-3.0](https://huggingface.co/pyannote/speaker-diarization-3.0) を開き、ページ上部のフォームで利用条件に同意
   - 依存モデル [pyannote/segmentation-3.0](https://huggingface.co/pyannote/segmentation-3.0) でも同様に同意
4. 取得したトークンを環境変数 `HF_TOKEN` に設定する（`sample/.env.example` を参照。または `sample/resize_video.py` の `pyannote_auth_token` を直接書き換え）

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

3. **Hugging Faceアクセストークン（リサイズ機能を使用する場合）**
   - [Settings → Access Tokens](https://huggingface.co/settings/tokens) で `Read` トークンを発行（Fine-grained の場合は「Read access to contents of all public gated repos you can access」にチェック）
   - pyannoteモデルは gated のため、[speaker-diarization-3.0](https://huggingface.co/pyannote/speaker-diarization-3.0) と [segmentation-3.0](https://huggingface.co/pyannote/segmentation-3.0) で利用規約に同意（詳細は上記「Hugging Faceトークンの取得方法」を参照）

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
# torchaudio 2.9.0以降ではAudioMetaDataが削除されているため、torchも2.9.0未満に制限
pip install "numpy>=1.24.0,<2.1.0" "torch>=2.0.0,<2.9.0" "torchaudio>=2.0.0,<2.9.0"

# その後、clipsai-jpを再インストール
pip install -e .
```

#### 3. 既存のパッケージをアンインストールして再インストール

```bash
# 競合しているパッケージをアンインストール
pip uninstall numpy torch torchaudio torchvision facenet-pytorch -y

# faster-whisper と pyannote.audio の要件を満たすバージョンをインストール
# torchaudio 2.9.0以降ではAudioMetaDataが削除されているため、torchも2.9.0未満に制限
pip install "numpy>=1.24.0,<2.1.0" "torch>=2.0.0,<2.9.0" "torchaudio>=2.0.0,<2.9.0"

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

- [ドキュメント一覧](README.md)
- [LLM によるクリップ検出](llm-clip-finding.md)
- [Sandbox ノートブック](sandbox-notebooks.md)
- [変更履歴](../CHANGELOG.md)

オリジナル（英語・更新停止）の解説は [Clips AI Documentation](https://clipsai.com) にあります。このフォーク版のパッケージ名は `clipsai_jp` です。

