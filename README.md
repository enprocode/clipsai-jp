# ClipsAI-JP

[![PyPI version](https://badge.fury.io/py/clipsai-jp.svg)](https://badge.fury.io/py/clipsai-jp)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> **注意:** このパッケージは[ClipsAI](https://github.com/ClipsAI/clipsai)の日本語専用フォーク版です。`whisperx`を`faster-whisper`に置き換え、依存関係の問題を解決しています。

## クイックスタート

Clips AIは、長い動画を自動的にクリップに変換するオープンソースのPythonライブラリです。数行のコードで、動画を複数のクリップに分割し、アスペクト比を16:9から9:16にリサイズできます。

> **注意:** Clips AIは、ポッドキャスト、インタビュー、スピーチ、説教などの音声中心のナラティブ動画向けに設計されています。

完全なドキュメントについては、[Clips AI Documentation](https://clipsai.com)をご覧ください。

### インストール

**前提条件:**
- Python >= 3.10
- [libmagic](https://github.com/ahupp/python-magic?tab=readme-ov-file#debianubuntu)（Windows: `pip install python-magic-bin`、Mac: `brew install libmagic`）
- [ffmpeg](https://github.com/kkroening/ffmpeg-python/tree/master?tab=readme-ov-file#installing-ffmpeg)（Windows: [ffmpeg.org](https://ffmpeg.org/download.html)からダウンロード、Mac: `brew install ffmpeg`）

**推奨:** 依存関係の競合を避けるため、仮想環境（[venv](https://packaging.python.org/en/latest/guides/installing-using-pip-and-virtual-environments/#create-and-use-virtual-environments)など）の使用を強く推奨します。

```bash
pip install clipsai-jp
```

**オプショナル依存関係:**
- MeCab（日本語の文分割精度向上のため推奨）: `pip install clipsai-jp[mecab]`
  - MeCabがインストールされていない場合、自動的にNLTKにフォールバックします
  - MeCab本体も含まれており、Windows、Mac、Linuxすべてで`pip install`のみで使用可能
  - 公式サイト: https://pypi.org/project/mecab/
- GPUメモリ監視: `pip install clipsai-jp[gpu]`
- 開発・テスト用: `pip install clipsai-jp[dev]`

### LLM によるクリップ検出（任意）

デフォルトはローカルの TextTiling のみです。OpenAI / Anthropic / Gemini / OpenAI互換 API（Ollama、Groq など）を併用すると、意味の切れ目での分割精度が上がります。キーはコードに書かず、環境変数で渡してください。ライブラリ本体は `.env` を読み込みません。

| プロバイダ | 環境変数 | デフォルトモデル |
|---|---|---|
| OpenAI | `OPENAI_API_KEY` | `gpt-4o-mini` |
| Anthropic | `ANTHROPIC_API_KEY` | `claude-sonnet-4-5` |
| Gemini | `GEMINI_API_KEY` | `gemini-2.5-flash` |
| OpenAI互換 | `LLM_API_KEY`（ローカルなら不要） | `llm_model` 必須 |

```python
from clipsai_jp import ClipFinder

clipfinder = ClipFinder(
    use_llm=True,
    llm_provider="openai",  # openai / anthropic / gemini / openai_compatible
    llm_model="gpt-4o-mini",
    llm_priority=0.7,
)
```

キーの優先順位は **引数 `llm_api_key` → プロバイダ専用の環境変数 → `LLM_API_KEY`** です。キーが無い、または API 呼び出しに失敗した場合は警告を出して TextTiling のみで動作します。詳細は [`docs/sample-code.md`](docs/sample-code.md) を参照してください。

## ドキュメント

使用方法、サンプルコード、パラメータ設定などの詳細については、[`docs/sample-code.md`](docs/sample-code.md)を参照してください。
