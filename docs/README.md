# ClipsAI-JP ドキュメント

このフォーク版の使い方は、オリジナルの [clipsai.com](https://clipsai.com) ではなく、このディレクトリのガイドを参照してください。パッケージ名は `clipsai_jp`（`clipsai` ではない）です。

| ガイド | 内容 |
|---|---|
| [README](../README.md) | インストールと最短の使い方 |
| [サンプルコードとパラメータ](sample-code.md) | 文字起こし・クリップ検出・リサイズの手順と `ClipFinder` の設定 |
| [LLM によるクリップ検出](llm-clip-finding.md) | OpenAI / Anthropic / Gemini / OpenAI互換 API の使い方と `use_gemini` からの移行 |
| [Sandbox ノートブック](sandbox-notebooks.md) | `sandbox/` の Jupyter ノートの実行方法 |
| [変更履歴](../CHANGELOG.md) | バージョンごとの差分 |

現在の安定版は **1.1.0** です。

```bash
pip install clipsai-jp==1.1.0
```
