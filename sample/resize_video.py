"""
動画をリサイズするサンプルコード

このサンプルでは、動画を指定したアスペクト比（デフォルトは9:16）に
リサイズする方法を示します。

注意: この機能を使用するには、Hugging FaceのPyannoteアクセストークンが必要です。
トークンの取得方法: https://huggingface.co/pyannote/speaker-diarization-3.0

【開発モードで使用する場合】
ローカルでビルドしたclipsai-jpを使用する場合は、以下のいずれかの方法で
セットアップしてください：

方法1: 開発モードでインストール（推奨）
    pip install -e .

方法2: パスを追加
    import sys
    import os
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
"""

from clipsai_jp import resize, MediaEditor, AudioVideoFile
import os

# 動画ファイルのパス（絶対パスを指定してください）
video_file_path = "/abs/path/to/video.mp4"

# Hugging FaceのPyannoteアクセストークン
# トークンの取得方法: https://huggingface.co/pyannote/speaker-diarization-3.0
pyannote_auth_token = "your_pyannote_token_here"

# 出力ディレクトリ（必要に応じて変更してください）
output_dir = os.path.join(os.path.dirname(video_file_path), "output")
os.makedirs(output_dir, exist_ok=True)

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

# リサイズ動画を実際のファイルとして保存（オプション）
print("\nリサイズ動画をファイルとして保存しています...")
media_editor = MediaEditor()
media_file = AudioVideoFile(video_file_path)
resized_output_path = os.path.join(output_dir, "resized_video.mp4")

resized_video = media_editor.resize_video(
    original_video_file=media_file,
    resized_video_file_path=resized_output_path,
    width=crops.crop_width,
    height=crops.crop_height,
    segments=crops.to_dict()["segments"],
)

if resized_video:
    print(f"リサイズ動画を {resized_output_path} に保存しました")
else:
    print("リサイズ動画の保存に失敗しました")

print(f"\nすべての出力ファイルは {output_dir} に保存されました。")

