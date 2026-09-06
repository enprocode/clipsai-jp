# LLM によるクリップ検出

`ClipFinder` の既定動作はローカルの TextTiling（文埋め込みの類似度で境界を切る）だけです。任意で LLM を併用すると、日本語の意味の切れ目・フック・自己完結をより自然に取れます。

1.1.0 から Gemini 専用ではなく、**OpenAI / Anthropic / Gemini / OpenAI互換** から選べます。プロバイダ専用 SDK は不要です（HTTP は既存の `requests`）。

## 最短の使い方

キーはコードに書かず、環境変数で渡してください。ライブラリ本体は `.env` を読み込みません。

```python
from clipsai_jp import ClipFinder

clipfinder = ClipFinder(
    use_llm=True,
    llm_provider="openai",  # openai / anthropic / gemini / openai_compatible
    llm_priority=0.7,       # 0.0=TextTilingのみ, 1.0=LLMのみ
)
clips = clipfinder.find_clips(transcription)
```

`llm_model` を省略すると、プロバイダごとのデフォルトモデルを使います。

## プロバイダとデフォルトモデル

| `llm_provider` | 環境変数 | デフォルトモデル | 高精度の例 |
|---|---|---|---|
| `openai` | `OPENAI_API_KEY` | `gpt-5.6-terra` | `gpt-5.6-sol` |
| `anthropic` | `ANTHROPIC_API_KEY` | `claude-sonnet-5` | `claude-opus-5` |
| `gemini` | `GEMINI_API_KEY` | `gemini-3.8-flash` | （Flash が既定の作業用） |
| `openai_compatible` | `LLM_API_KEY`（ローカルなら不要） | なし（`llm_model` 必須） | サーバ側のモデル名 |

`llm_provider` はハイフンでも書けます（`openai-compatible` → `openai_compatible`）。

### OpenAI

```python
clipfinder = ClipFinder(
    use_llm=True,
    llm_provider="openai",
    llm_model="gpt-5.6-terra",  # 高精度なら "gpt-5.6-sol"
    llm_priority=0.7,
)
```

```bash
export OPENAI_API_KEY="sk-..."
```

### Anthropic

```python
clipfinder = ClipFinder(
    use_llm=True,
    llm_provider="anthropic",
    llm_model="claude-sonnet-5",  # 高精度なら "claude-opus-5"
)
```

```bash
export ANTHROPIC_API_KEY="..."
```

### Gemini

```python
clipfinder = ClipFinder(
    use_llm=True,
    llm_provider="gemini",
    llm_model="gemini-3.8-flash",
)
```

```bash
export GEMINI_API_KEY="..."
```

### OpenAI互換（Ollama / Groq / vLLM など）

`llm_base_url` と `llm_model` が必須です。キーはローカルなら不要、クラウド互換 API なら `LLM_API_KEY` または `llm_api_key` を使います。

```python
# ローカル Ollama
clipfinder = ClipFinder(
    use_llm=True,
    llm_provider="openai_compatible",
    llm_model="llama3",
    llm_base_url="http://localhost:11434/v1",
)

# Groq などクラウドの互換 API
clipfinder = ClipFinder(
    use_llm=True,
    llm_provider="openai_compatible",
    llm_model="llama-3.3-70b-versatile",
    llm_base_url="https://api.groq.com/openai/v1",
    llm_api_key=os.environ["LLM_API_KEY"],
)
```

## パラメータ

`use_llm` と `llm_*` はキーワード専用です。位置引数で渡さないでください。

| 引数 | 既定 | 説明 |
|---|---|---|
| `use_llm` | `False` | LLM で境界提案を補助する |
| `llm_provider` | `"openai"` | 上記4種 |
| `llm_api_key` | `None` | 未指定時は環境変数 |
| `llm_model` | プロバイダ既定 | モデル ID |
| `llm_base_url` | プロバイダ既定 | `openai_compatible` では必須 |
| `llm_priority` | `0.5` | TextTiling と LLM 提案の重み。`0` 以下なら API を呼ばない |

推奨の出発点は `llm_priority=0.6`〜`0.8` です。ショート動画なら `clip_style="shorts"` または `max_clip_duration<=90` と組み合わせると、フック評価と重複抑制も乗ります。

## APIキーの優先順位

1. 引数 `llm_api_key`（旧 API では `gemini_api_key`）
2. プロバイダ専用の環境変数（上表）
3. 共通フォールバック `LLM_API_KEY`
4. それでも無い場合: 警告を出して LLM をオフにし、TextTiling のみで動作

キーが無い、または API 呼び出しに失敗した場合も処理は止まりません。ログにはプロバイダ名とモデル名だけ出し、キーは出しません。

`clipsai_jp` 本体は `.env` を読み込みません。サンプル（`sample/clip_video.py`）は `python-dotenv` で `sample/.env` を読むだけです。雛形は `sample/.env.example` です。

## `use_gemini` からの移行（1.0.x → 1.1.0）

旧引数は動きますが非推奨です。内部では `use_llm=True, llm_provider="gemini"` に変換されます。

```python
# 1.0.x（非推奨・まだ動く）
ClipFinder(
    use_gemini=True,
    gemini_api_key=os.environ["GEMINI_API_KEY"],
    gemini_model="gemini-3.8-flash",
    gemini_priority=0.5,
)

# 1.1.0（推奨）
ClipFinder(
    use_llm=True,
    llm_provider="gemini",
    llm_model="gemini-3.8-flash",
    llm_priority=0.5,
)
```

`GeminiClipFinder` も残していますが非推奨です。直接使う必要はなく、`ClipFinder(use_llm=True, ...)` を使ってください。

位置引数 `ClipFinder(..., "japanese", True, "gemini-key")` は従来どおり `use_gemini` に当たります。新しい `use_llm` / `llm_*` を位置で渡すと別の引数として解釈されるため、必ずキーワードで指定してください。

## 精度を上げる順番

効果が大きい順です。全部を一度に変える必要はありません。

1. **`use_llm=True`** で意味の切れ目を LLM に見させる
2. **強いモデル**（`gpt-5.6-sol` / `claude-opus-5`）。遅い・高い
3. **埋め込みを上げる**（`embedding_model="high_accuracy"` または `"large"`）
4. **MeCab**（`pip install clipsai-jp[mecab]`）。文の途中で切れにくくなる
5. **`llm_priority` を 0.6〜0.8**
6. **ショートなら `clip_style="shorts"`**（または `max_clip_duration<=90`）

## 長尺動画について

文字起こしが長い場合、文をオーバーラップ付きチャンクに分けて複数回問い合わせ、提案を統合します。キー課金と待ち時間は動画の長さに比例します。`llm_priority=0` または `use_llm=False` なら API は呼びません。

## 関連

- パラメータ全体とサンプル実行: [sample-code.md](sample-code.md)
- 環境変数の雛形: [`sample/.env.example`](../sample/.env.example)
- 実装: `clipsai_jp/clip/llm_clipfinder.py` / `clipsai_jp/clip/clipfinder.py`
