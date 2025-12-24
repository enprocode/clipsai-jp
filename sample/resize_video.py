"""
動画をリサイズするサンプルコード

このサンプルでは、動画を指定したアスペクト比（デフォルトは9:16）に
リサイズする方法を示します。

注意: この機能を使用するには、Hugging FaceのPyannoteアクセストークンが必要です。
トークンの取得方法: https://huggingface.co/pyannote/speaker-diarization-3.0

【開発モードで使用する場合】
ローカルでビルドしたclipsaiを使用する場合は、以下のいずれかの方法で
セットアップしてください：

方法1: 開発モードでインストール（推奨）
    pip install -e .

方法2: パスを追加
    import sys
    import os
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
"""

from clipsai import resize

# 動画ファイルのパス（絶対パスを指定してください）
video_file_path = "/abs/path/to/video.mp4"

# Hugging FaceのPyannoteアクセストークン
# トークンの取得方法: https://huggingface.co/pyannote/speaker-diarization-3.0
pyannote_auth_token = "your_pyannote_token_here"

# 動画をリサイズ（デフォルトは9:16の縦型）
print("動画をリサイズしています...")
crops = resize(
    video_file_path=video_file_path,
    pyannote_auth_token=pyannote_auth_token,
    aspect_ratio=(9, 16)  # (幅, 高さ) の形式
)

# リサイズ結果のセグメント情報を表示
print(f"\nリサイズセグメント数: {len(crops.segments)}")
for i, segment in enumerate(crops.segments):
    print(f"\nセグメント {i + 1}:")
    print(f"  開始時間: {segment['start_time']}秒")
    print(f"  終了時間: {segment['end_time']}秒")
    if 'x' in segment and 'y' in segment:
        print(f"  位置: ({segment['x']}, {segment['y']})")
    if 'width' in segment and 'height' in segment:
        print(f"  サイズ: {segment['width']}x{segment['height']}")

