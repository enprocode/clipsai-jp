# 変更履歴

このプロジェクトの重要な変更はすべてこのファイルに記録されます。

## [1.0.0] - 2024-12-XX

### 初回リリース（日本語専用版）

このバージョンは、[ClipsAI](https://github.com/ClipsAI/clipsai)の日本語専用フォーク版として初回リリースされました。

### 主な変更点

#### 文字起こしエンジンの変更
- **`whisperx`から`faster-whisper`への移行**
  - `whisperx`の依存関係の問題（PyTorch 2.8.0との互換性問題）を解決
  - `faster-whisper`は`torch`に依存せず、依存関係の競合を大幅に削減
  - 文字起こしのパフォーマンスと安定性を向上

#### 依存関係の最適化
- **`facenet-pytorch`の削除**
  - MediaPipe Face Detectionに置き換え（既に実装済み）
  - `numpy`と`torch`のバージョン制約を緩和
- **オプショナル依存関係の整理**
  - `pynvml`を`extras_require["gpu"]`に移動
  - `pytest`、`pandas`、`matplotlib`を`extras_require["dev"]`に移動
- **依存関係のバージョン制約の改善**
  - `numpy`: `>=1.24.0,<2.1.0`（`faster-whisper`の柔軟な要件に対応）
  - `torch`: `>=2.0.0,<3.0.0`（`pyannote.audio`の要件に合わせて設定）

#### パッケージ名の変更
- **`clipsai` → `clipsai-jp`**
  - PyPIでの公開名を`clipsai-jp`に変更
  - 日本語専用版であることを明確化

### 互換性に関する注意事項
- 元の`clipsai`パッケージとは別のパッケージとして公開されます
- `faster-whisper`を使用するため、`whisperx`のインストールは不要です
- 既存のコードとの互換性は維持されています（APIは変更なし）

### ドキュメント
- `README.md`を日本語専用版向けに更新
- `doc/SAMPLE_CODE.md`にインストール手順とトラブルシューティングを追加
- PyPIバッジを追加
- GitHub Actionsワークフローを追加（CircleCIから移行）